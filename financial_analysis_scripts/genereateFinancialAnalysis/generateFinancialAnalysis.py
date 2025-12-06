import time
import yfinance as yf
import pandas as pd
import concurrent.futures
import json
import re
import os

# --- CONFIGURATION ---
CACHE_FILE = "tickers_cache.json"  # The file storing the list ["ABC.WA", "DEF.WA"]

# --- MAPPINGS (PKD/Industry) ---
YFINANCE_INDUSTRY_TO_PKD = {
    "Engineering & Construction": "F", "Residential Construction": "F", "Building Materials": "F",
    "Apparel Retail": "G", "Specialty Retail": "G", "Grocery Stores": "G", "Internet Retail": "G",
    "Auto Parts": "G", "Auto & Truck Dealerships": "G", "Luxury Goods": "G",
    "Software - Infrastructure": "J", "Software - Application": "J", "Electronic Gaming & Multimedia": "J",
    "Entertainment": "J", "Telecom Services": "J", "Internet Content & Information": "J",
    "Banks - Regional": "K", "Insurance - Diversified": "K", "Insurance - Life": "K",
    "Capital Markets": "K", "Asset Management": "K", "Credit Services": "K",
    "Other Industrial Metals & Mining": "B", "Copper": "B", "Coal": "B", "Oil & Gas E&P": "B",
    "Oil & Gas Integrated": "C", "Chemicals": "C", "Specialty Chemicals": "C", "Aerospace & Defense": "C",
    "Packaging & Containers": "C", "Food Distribution": "C", "Farm Products": "C",
    "Utilities - Regulated Electric": "D", "Utilities - Renewable": "D", "Utilities - Independent Power Producers": "D",
    "Real Estate - Development": "L", "Real Estate Services": "L", "REIT - Diversified": "L",
    "Medical Instruments & Supplies": "C", "Diagnostics & Research": "M", "Biotechnology": "M", "Hospitals": "Q"
}

YFINANCE_SECTOR_FALLBACK = {
    "Financial Services": "K", "Technology": "J", "Communication Services": "J", "Energy": "D",
    "Consumer Cyclical": "G", "Consumer Defensive": "G", "Industrials": "C", "Basic Materials": "C",
    "Real Estate": "L", "Healthcare": "Q", "Utilities": "D"
}

PKD_DESCRIPTIONS = {
    "B": "Górnictwo i wydobywanie", "C": "Przetwórstwo przemysłowe", "D": "Wytwarzanie i zaopatrywanie w energię",
    "F": "Budownictwo", "G": "Handel hurtowy i detaliczny", "J": "Informacja i komunikacja",
    "K": "Działalność finansowa i ubezpieczeniowa", "L": "Obsługa rynku nieruchomości",
    "M": "Działalność profesjonalna, naukowa i techniczna", "Q": "Opieka zdrowotna", "Inne": "Pozostała działalność"
}


# --- TICKER ACQUISITION LOGIC ---

def fetch_ticker_gpw(stock_slug: str) -> str:
    """Scrapes ticker for a single company from Bankier.pl"""
    details_url = f"https://www.bankier.pl/gielda/notowania/akcje/{stock_slug}/podstawowe-dane"
    try:
        detail_tables = pd.read_html(details_url, match="Ticker GPW")
        if detail_tables:
            return detail_tables[0].iloc[3, 1]
    except Exception:
        pass
    return None


def scrape_all_tickers():
    """Scrapes ALL tickers from scratch (Slow)"""
    print("Cache not found. Starting full scrape from Bankier.pl...")
    LIST_URL = "https://www.bankier.pl/gielda/notowania/akcje"
    try:
        stock_table = pd.read_html(LIST_URL)[0]
        slugs = stock_table.iloc[:, 0].astype(str).str.strip().dropna().tolist()
    except Exception as e:
        print(f"Error fetching master list: {e}")
        return []

    tickers = []
    print(f"Found {len(slugs)} companies. Scraping details...")

    for i, slug in enumerate(slugs):
        t = fetch_ticker_gpw(slug)
        if t:
            t_wa = f"{t}.WA"
            tickers.append(t_wa)
            print(f"[{i + 1}/{len(slugs)}] Got: {t_wa}")
        time.sleep(0.5)  # Be polite to the server

    return sorted(list(set(tickers)))


def get_tickers_cached():
    """
    1. Checks if 'tickers_cache.json' exists.
    2. IF YES: Loads it, cleans 'nan.WA', returns list.
    3. IF NO: Runs scraper, saves file, returns list.
    """
    if os.path.exists(CACHE_FILE):
        print(f"Found cache file: {CACHE_FILE}")
        try:
            with open(CACHE_FILE, 'r') as f:
                tickers = json.load(f)

            # --- CLEANING DATA ---
            # Remove duplicates and garbage like 'nan.WA'
            cleaned_tickers = [t for t in tickers if t and "nan.WA" not in t]

            print(f"Loaded {len(cleaned_tickers)} tickers from cache.")
            return cleaned_tickers
        except Exception as e:
            print(f"Error reading cache: {e}. Re-scraping...")

    # If we are here, we need to scrape
    tickers = scrape_all_tickers()

    if tickers:
        with open(CACHE_FILE, 'w') as f:
            json.dump(tickers, f)
        print(f"Saved {len(tickers)} tickers to {CACHE_FILE}")

    return tickers


# --- FINANCIAL ANALYSIS LOGIC ---

def get_raw_data(ticker):
    try:
        # Ticker format check
        if not ticker.endswith('.WA'): ticker += '.WA'

        info = yf.Ticker(ticker).info

        # Filter out dead tickers
        if 'shortName' not in info and 'symbol' not in info:
            return None

        yf_industry = info.get('industry', '')
        yf_sector = info.get('sector', '')

        pkd_id = YFINANCE_INDUSTRY_TO_PKD.get(yf_industry)
        if not pkd_id:
            pkd_id = YFINANCE_SECTOR_FALLBACK.get(yf_sector, "Inne")

        return {
            'PKD_ID': pkd_id,
            'YF_Industry': yf_industry,
            'MarketCap': info.get('marketCap'),
            'Revenue': info.get('totalRevenue'),
            'PE_Trailing': info.get('trailingPE'),
            'PB_Ratio': info.get('priceToBook'),
            'ROE': info.get('returnOnEquity'),
            'ProfitMargin': info.get('profitMargins'),
            'DividendYield': info.get('dividendYield')
        }
    except Exception:
        return None


def main():
    # 1. GET TICKERS (CACHE OR SCRAPE)
    tickers = get_tickers_cached()

    if not tickers:
        print("No tickers found. Exiting.")
        return

    # 2. GET FINANCIAL DATA
    raw_data_list = []
    print(f"\nAnalyzing {len(tickers)} companies...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(get_raw_data, t): t for t in tickers}
        completed = 0
        total = len(tickers)
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            completed += 1
            if completed % 20 == 0:
                print(f"Progress: {completed}/{total}")
            if res:
                raw_data_list.append(res)

    if not raw_data_list:
        print("No financial data found.")
        return

    # 3. AGGREGATE
    df = pd.DataFrame(raw_data_list)
    numeric_cols = ['MarketCap', 'Revenue', 'PE_Trailing', 'PB_Ratio', 'ROE', 'ProfitMargin', 'DividendYield']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    def get_median(x):
        return x.median()

    def get_sum(x):
        return x.sum()

    def get_count(x):
        return x.count()

    aggregated = df.groupby('PKD_ID').agg({
        'MarketCap': [get_sum, get_count],
        'Revenue': get_sum,
        'PE_Trailing': get_median,
        'PB_Ratio': get_median,
        'ROE': get_median,
        'ProfitMargin': get_median,
        'DividendYield': get_median
    })

    aggregated.columns = ['_'.join(col).strip() for col in aggregated.columns.values]

    output_json = {}
    aggregated = aggregated.sort_values(by='Revenue_get_sum', ascending=False)

    for pkd_id, row in aggregated.iterrows():
        if row['MarketCap_get_count'] < 2: continue

        def clean(val):
            return None if pd.isna(val) else val

        nazwa_pelna = PKD_DESCRIPTIONS.get(pkd_id, f"Inne / Nieznana ({pkd_id})")

        output_json[pkd_id] = {
            "nazwa_sekcji": nazwa_pelna,
            "statystyki": {
                "liczba_firm": int(row['MarketCap_get_count']),
                "kapitalizacja_suma": clean(row['MarketCap_get_sum']),
                "przychody_suma": clean(row['Revenue_get_sum'])
            },
            "wskazniki_mediana": {
                "pe": clean(row['PE_Trailing_get_median']),
                "pb": clean(row['PB_Ratio_get_median']),
                "roe": clean(row['ROE_get_median']),
                "marza_netto": clean(row['ProfitMargin_get_median']),
                "dywidenda_yield": clean(row['DividendYield_get_median'])
            }
        }

    filename = 'analiza_pkd_full.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, indent=4, ensure_ascii=False)

    print(f"\nDone! Analysis saved to: {filename}")

    # Preview
    if output_json:
        k = next(iter(output_json))
        print(f"Example ({k}):")
        print(json.dumps(output_json[k], indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()