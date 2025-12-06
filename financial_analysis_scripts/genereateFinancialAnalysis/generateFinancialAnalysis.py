import os
import json
import time
import datetime
import concurrent.futures
import pandas as pd
import yfinance as yf
import logging

#log config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("execution.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GPW_Fin_Only")

CACHE_FILE = "tickers_cache.json"
OUTPUT_DIR = "reports_financial"

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

YFINANCE_INDUSTRY_TO_PKD = {
    "Engineering & Construction": "F", "Residential Construction": "F", "Building Materials": "F",
    "Apparel Retail": "G", "Specialty Retail": "G", "Grocery Stores": "G", "Internet Retail": "G",
    "Auto Parts": "G", "Auto & Truck Dealerships": "G", "Luxury Goods": "G",
    "Software - Infrastructure": "J", "Software - Application": "J", "Electronic Gaming & Multimedia": "J",
    "Entertainment": "J", "Telecom Services": "J", "Internet Content & Information": "J",
    "Banks - Regional": "K", "Insurance - Diversified": "K", "Insurance - Life": "K", "Capital Markets": "K",
    "Other Industrial Metals & Mining": "B", "Copper": "B", "Coal": "B", "Oil & Gas E&P": "B",
    "Chemicals": "C", "Specialty Chemicals": "C", "Aerospace & Defense": "C", "Packaging & Containers": "C",
    "Utilities - Regulated Electric": "D", "Utilities - Renewable": "D", "Real Estate - Development": "L",
    "Medical Instruments & Supplies": "C", "Diagnostics & Research": "M", "Biotechnology": "M", "Hospitals": "Q"
}
YFINANCE_SECTOR_FALLBACK = {
    "Financial Services": "K", "Technology": "J", "Communication Services": "J", "Energy": "D",
    "Consumer Cyclical": "G", "Consumer Defensive": "G", "Industrials": "C", "Basic Materials": "C",
    "Real Estate": "L", "Healthcare": "Q", "Utilities": "D"
}
PKD_DESCRIPTIONS = {
    "B": "Górnictwo", "C": "Przetwórstwo", "D": "Energetyka", "F": "Budownictwo",
    "G": "Handel", "J": "IT i Media", "K": "Finanse", "L": "Nieruchomości",
    "M": "Nauka", "Q": "Opieka Zdrowotna", "Inne": "Pozostałe"
}



def fetch_ticker_from_slug(slug):
    """Pobiera ticker ze strony szczegółów spółki"""
    try:
        url = f"https://www.bankier.pl/gielda/notowania/akcje/{slug}/podstawowe-dane"
        tables = pd.read_html(url, match="Ticker GPW")
        if tables:
            ticker = tables[0].iloc[3, 1]
            return ticker
    except:
        pass
    return None


def resolve_company_ticker(row):
    """Przetwarza wiersz z głównej tabeli, aby znaleźć ticker"""
    try:
        raw_name = str(row.iloc[0])
        # Pobieramy 'slug' z nazwy (pierwsze słowo), aby znaleźć stronę z tickerem
        slug = raw_name.split(" ")[0].strip()

        ticker = fetch_ticker_from_slug(slug)

        if ticker:
            return f"{ticker}.WA"
    except Exception:
        pass
    return None


def update_tickers():
    logger.info("--- KROK 1: AKTUALIZACJA LISTY TICKERÓW ---")

    cached_tickers = set()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                clean_list = [t for t in data if t and "nan" not in str(t)]
                cached_tickers = set(clean_list)
            logger.info(f"Wczytano {len(cached_tickers)} tickerów z cache.")
        except Exception as e:
            logger.warning(f"Błąd cache: {e}. Tworzę nowy.")

    url = "https://www.bankier.pl/gielda/notowania/akcje"
    try:
        df_market = pd.read_html(url)[0]
    except Exception as e:
        logger.error(f"Błąd pobierania strony głównej: {e}")
        return list(cached_tickers)

    logger.info(f"Skanowanie {len(df_market)} spółek w poszukiwaniu nowych tickerów...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(resolve_company_ticker, row) for _, row in df_market.iterrows()]

        completed = 0
        new_found = 0
        for future in concurrent.futures.as_completed(futures):
            ticker = future.result()
            completed += 1

            if ticker and ticker not in cached_tickers:
                cached_tickers.add(ticker)
                new_found += 1

            if completed % 100 == 0:
                logger.info(f"Postęp: {completed}/{len(df_market)}")

    if new_found > 0:
        logger.info(f"Znaleziono {new_found} nowych spółek.")
        sorted_tickers = sorted(list(cached_tickers))
        with open(CACHE_FILE, 'w') as f:
            json.dump(sorted_tickers, f)
    else:
        logger.info("Brak nowych spółek. Używam istniejącej listy.")

    return sorted(list(cached_tickers))

def fetch_financial_data(ticker):
    try:
        info = yf.Ticker(ticker).info

        if 'shortName' not in info and 'symbol' not in info:
            return None

        pkd_id = YFINANCE_INDUSTRY_TO_PKD.get(info.get('industry', ''),
                                              YFINANCE_SECTOR_FALLBACK.get(info.get('sector', ''), "Inne"))

        return {
            'PKD_ID': pkd_id,
            'Ticker': ticker,
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


def process_market_data(tickers):
    logger.info("--- KROK 2: ANALIZA FINANSOWA ---")
    financial_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(fetch_financial_data, t): t for t in tickers}

        completed = 0
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            completed += 1
            if completed % 50 == 0:
                logger.info(f"Pobrano dane: {completed}/{len(tickers)}")
            if res:
                financial_data.append(res)

    return pd.DataFrame(financial_data)


def generate_report(df):
    logger.info("--- KROK 3: SCORING I RAPORT ---")

    cols = ['MarketCap', 'Revenue', 'PE_Trailing', 'PB_Ratio', 'ROE', 'ProfitMargin', 'DividendYield']
    for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce')

    def get_median(x):
        return x.median()

    def get_sum(x):
        return x.sum()

    def get_count(x):
        return x.count()

    agg = df.groupby('PKD_ID').agg({
        'MarketCap': [get_sum, get_count],
        'Revenue': get_sum,
        'PE_Trailing': get_median,
        'ROE': get_median,
        'ProfitMargin': get_median,
        'DividendYield': get_median
    })

    agg.columns = ['_'.join(c).strip() for c in agg.columns.values]
    agg = agg.sort_values(by='Revenue_get_sum', ascending=False)

    report = {}

    for pkd, row in agg.iterrows():
        if row['MarketCap_get_count'] < 3: continue

        margin = row.get('ProfitMargin_get_median', 0)
        roe = row.get('ROE_get_median', 0)
        div = row.get('DividendYield_get_median', 0)
        pe = row.get('PE_Trailing_get_median', 0)

        s_margin = min((max(0, margin) / 0.15), 1.0) * 25
        s_roe = min((max(0, roe) / 0.12), 1.0) * 15
        s_scale = min(row['MarketCap_get_count'] / 10, 1.0) * 10
        s_div = min((div / 0.04), 1.0) * 20
        if 5 <= pe <= 25:
            s_pe = 30
        elif 25 < pe <= 40:
            s_pe = 10
        else:
            s_pe = 0

        final_score = s_margin + s_roe + s_scale + s_div + s_pe
        final_score = min(100, final_score)

        if final_score >= 80:
            rating = "A"
        elif final_score >= 60:
            rating = "B"
        elif final_score >= 40:
            rating = "C"
        else:
            rating = "D"

        def clean(v):
            return None if pd.isna(v) else v

        report[pkd] = {
            "section_name": PKD_DESCRIPTIONS.get(pkd, pkd),
            "safety_score": int(final_score),
            "rating": rating,
            "financial_health": {
                "median_margin": clean(margin),
                "median_roe": clean(roe),
                "median_pe": clean(pe),
                "median_dividend_yield": clean(div)
            },
            "market_data": {
                "companies_count": int(row['MarketCap_get_count']),
                "total_cap_pln": clean(row['MarketCap_get_sum'])
            }
        }

    return report


def main():
    logger.info("=== START ===")
    start_time = time.time()

    # 1. Update Tickers
    tickers = update_tickers()
    if not tickers: return

    # 2. Fetch Data
    df = process_market_data(tickers)

    # 3. Report
    report = generate_report(df)

    # 4. Save
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    path = f"{OUTPUT_DIR}/financial_report_{today}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    logger.info(f"Zapisano raport: {path}")
    logger.info(f"Czas wykonania: {round(time.time() - start_time, 2)}s")


if __name__ == "__main__":
    main()