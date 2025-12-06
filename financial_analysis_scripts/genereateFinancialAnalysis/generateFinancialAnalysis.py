import os
import json
import time
import datetime
import concurrent.futures
import pandas as pd
import yfinance as yf
import logging
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "host": "212.132.76.195",
    "port": "5433",
    "database": "hacknation_db",
    "user": "hack",
    "password": "HackNation!"
}

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

PKD_DESCRIPTIONS = {
    "A": "Rolnictwo",
    "B": "Górnictwo",
    "C": "Przemysł",
    "D": "Energetyka",
    "E": "Woda i Odpady",
    "F": "Budownictwo",
    "G": "Handel",
    "H": "Transport",
    "I": "Gastronomia i Hotele",
    "J": "IT i Media",
    "K": "Finanse",
    "L": "Nieruchomości",
    "M": "Nauka i Biznes",
    "Q": "Opieka Zdrowotna",
    "R": "Rozrywka i Sport",
    "OT": "Pozostałe"
}

# 2. MAPOWANIE BRANŻ (INDUSTRY) -> PKD
YFINANCE_INDUSTRY_TO_PKD = {
    # --- F: BUDOWNICTWO ---
    "Engineering & Construction": "F",
    "Residential Construction": "F",
    "Building Materials": "F",

    # --- G: HANDEL ---
    "Apparel Retail": "G",
    "Specialty Retail": "G",
    "Grocery Stores": "G",
    "Internet Retail": "G",
    "Auto Parts": "G",
    "Auto & Truck Dealerships": "G",
    "Luxury Goods": "G",

    # --- H: TRANSPORT  ---
    "Railroads": "H",
    "Airlines": "H",
    "Airports & Air Services": "H",
    "Marine Shipping": "H",
    "Integrated Freight & Logistics": "H",
    "Trucking": "H",

    # --- I: GASTRONOMIA I HOTELE ---
    "Restaurants": "I",
    "Lodging": "I",
    "Food Services": "I",
    "Resorts & Casinos": "I",

    # --- J: IT I MEDIA ---
    "Software - Infrastructure": "J",
    "Software - Application": "J",
    "Electronic Gaming & Multimedia": "J",
    "Entertainment": "J",
    "Telecom Services": "J",
    "Internet Content & Information": "J",
    "Broadcasting": "J",

    # --- K: FINANSE ---
    "Banks - Regional": "K",
    "Insurance - Diversified": "K",
    "Insurance - Life": "K",
    "Capital Markets": "K",
    "Asset Management": "K",
    "Credit Services": "K",

    # --- L: NIERUCHOMOŚCI ---
    "Real Estate - Development": "L",
    "Real Estate Services": "L",
    "REIT - Diversified": "L",
    "REIT - Retail": "L",

    # --- M: NAUKA I BIZNES ---
    "Consulting Services": "M",
    "Staffing & Employment Services": "M",
    "Research & Consulting": "M",

    # --- B: GÓRNICTWO ---
    "Other Industrial Metals & Mining": "B",
    "Copper": "B",
    "Coal": "B",
    "Oil & Gas E&P": "B",
    "Gold": "B",

    # --- C: PRZEMYSŁ ---
    "Oil & Gas Integrated": "C",
    "Chemicals": "C",
    "Specialty Chemicals": "C",
    "Aerospace & Defense": "C",
    "Packaging & Containers": "C",
    "Food Distribution": "C",
    "Farm Products": "C",
    "Paper & Paper Products": "C",

    # --- D: ENERGETYKA ---
    "Utilities - Regulated Electric": "D",
    "Utilities - Renewable": "D",
    "Utilities - Independent Power Producers": "D",

    # --- Q: ZDROWIE ---
    "Medical Instruments & Supplies": "Q",
    "Medical Care Facilities": "Q",
    "Health Information Services": "Q",

    # --- R: ROZRYWKA (NOWE) ---
    "Leisure": "R",  #
    "Travel Services": "R"
}

# 3. MAPOWANIE SEKTORÓW (FALLBACK)
YFINANCE_SECTOR_FALLBACK = {
    "Financial Services": "K",
    "Technology": "J",
    "Communication Services": "J",
    "Energy": "D",
    "Consumer Cyclical": "G",
    "Consumer Defensive": "G",
    "Industrials": "C",
    "Basic Materials": "C",
    "Real Estate": "L",
    "Healthcare": "Q",
    "Utilities": "D"
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
                                              YFINANCE_SECTOR_FALLBACK.get(info.get('sector', ''), ""))

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
    logger.info("--- KROK 3: OBLICZANIE WSKAŹNIKÓW ---")
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

    # WAŻNE: Tu musi być LISTA, nie słownik
    report_list = []

    for pkd, row in agg.iterrows():
        if row['MarketCap_get_count'] < 3: continue

        margin = row.get('ProfitMargin_get_median', 0)
        roe = row.get('ROE_get_median', 0)
        div = row.get('DividendYield_get_median', 0)
        pe = row.get('PE_Trailing_get_median', 0)

        # Scoring
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

        final_score = min(100, s_margin + s_roe + s_scale + s_div + s_pe)

        if final_score >= 80:
            rating = "A (Strong)"
        elif final_score >= 60:
            rating = "B (Stable)"
        elif final_score >= 40:
            rating = "C (Weak)"
        else:
            rating = "D (Speculative)"

        def clean_decimal(v):
            if pd.isna(v) or v is None: return 0.0
            return float(v)

        def clean_int(v):
            if pd.isna(v) or v is None: return 0
            return int(v)

        # Tworzymy obiekt sekcji
        section_data = {
            "section_code": pkd,  # To pole jest kluczowe dla bazy danych
            "section_name": PKD_DESCRIPTIONS.get(pkd, pkd)[:20],
            "safety_score": int(final_score),
            "rating": rating[:20],
            "median_margin": clean_decimal(margin),
            "median_roe": clean_decimal(roe),
            "median_pe": clean_decimal(pe),
            "median_dividend_yield": clean_decimal(div),
            "companies_count": clean_int(row['MarketCap_get_count']),
            "total_cap_pln": clean_int(row['MarketCap_get_sum'])
        }

        # Dodajemy do LISTY
        report_list.append(section_data)

    return report_list


def save_to_database(report_data):
    logger.info("--- KROK 4: ZAPIS DO BAZY DANYCH ---")

    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT MAX(Id) FROM Report;")
        max_id = cur.fetchone()[0]
        new_report_id = 1 if max_id is None else max_id + 1

        today = datetime.datetime.now().date()

        insert_report_query = "INSERT INTO Report (Id, date) VALUES (%s, %s);"
        cur.execute(insert_report_query, (new_report_id, today))
        logger.info(f"Utworzono Raport ID: {new_report_id}")

        insert_section_query = """
                               INSERT INTO Section (Id, Report_Id, Section_code, Section_name, Safety_score, Rating, \
                                                    Median_margin, Median_roe, Median_pe, Median_divident_yield, \
                                                    Companies_count, total_cap_pln) \
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); \
                               """

        cur.execute("SELECT MAX(Id) FROM Section;")
        max_sec_id = cur.fetchone()[0]
        current_sec_id = 1 if max_sec_id is None else max_sec_id + 1

        for section in report_data:
            cur.execute(insert_section_query, (
                current_sec_id,
                new_report_id,
                section['section_code'],
                section['section_name'],
                section['safety_score'],
                section['rating'],
                section['median_margin'],
                section['median_roe'],
                section['median_pe'],
                section['median_dividend_yield'],
                section['companies_count'],
                section['total_cap_pln']
            ))
            current_sec_id += 1

        conn.commit()
        logger.info(f"Zapisano {len(report_data)} sekcji do bazy.")

    except Exception as e:
        logger.error(f"Błąd bazy danych: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

def main():
    logger.info("=== START ===")
    start_time = time.time()

    tickers = update_tickers()
    if not tickers: return

    df = process_market_data(tickers)
    report = generate_report(df)

    save_to_database(report)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    path = f"{OUTPUT_DIR}/financial_report_{today}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    logger.info(f"Zapisano raport: {path}")
    logger.info(f"Czas wykonania: {round(time.time() - start_time, 2)}s")


if __name__ == "__main__":
    main()