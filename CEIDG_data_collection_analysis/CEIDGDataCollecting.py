import requests
import time
import csv
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()
JWT_TOKEN = os.getenv("CEIDG_API_KEY")

if not JWT_TOKEN:
    print("ERROR: JWT_TOKEN not found!")
    print("Please set the CEIDG_API_KEY variable in your .env file or environment.")
    exit()

HEADERS = {"Authorization": f"Bearer {JWT_TOKEN}", "Accept": "application/json"}
BASE_URL = "https://dane.biznes.gov.pl/api/ceidg/v3/"
CSV_FILENAME = f"firmy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


PAGE_SAMPLE_SIZE = 20


FIVE_YEARS_AGO = datetime.now() - timedelta(days=5 * 365 + 1)
START_DATE_FILTER = FIVE_YEARS_AGO.strftime('%Y-%m-%d')
DATE_QUERY = f"&dataod={START_DATE_FILTER}"

all_firm_ids = []
csv_data = []

# ----------------------------------------------------------------------
# --- Phase 1: Determine Total Pages and Select Random Pages (FILTERED) ---
# ----------------------------------------------------------------------

print("Starting Phase 1: Determining total pages and selecting random sample...")
print(f"Filtering firms started on or after: {START_DATE_FILTER}")


initial_search_url = f"{BASE_URL}firmy?limit=25&page=0{DATE_QUERY}"

try:
    response = requests.get(initial_search_url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    search_data = response.json()

    count = search_data.get('count', 0)
    total_pages = (count + 24) // 25

    print(f"Total RECENT firms found: {count}. Total available pages: {total_pages}.")

    if total_pages == 0:
        print("Error: No recent firms found matching criteria.")
        exit()

    all_page_indices = list(range(total_pages))


    if total_pages >= PAGE_SAMPLE_SIZE:
        random_page_indices = random.sample(all_page_indices, PAGE_SAMPLE_SIZE)
    else:
        print(f"Warning: Only {total_pages} pages available. Processing all of them.")
        random_page_indices = all_page_indices

    print(f"Selected {len(random_page_indices)} random pages for processing.")


    for page_index in random_page_indices:

        page_search_url = f"{BASE_URL}firmy?limit=25&page={page_index}{DATE_QUERY}"
        print(f"  > Collecting IDs from Page {page_index + 1}...")

        time.sleep(5)

        page_response = requests.get(page_search_url, headers=HEADERS, timeout=15)
        page_response.raise_for_status()
        page_data = page_response.json()

        for firm in page_data.get('firmy', []):
            all_firm_ids.append(firm.get('id'))

except requests.exceptions.RequestException as e:
    print(f"Error during initial search: {e}")
    exit()

print(f"\nPhase 1 Complete. Collected {len(all_firm_ids)} firm IDs from the selected random pages.")

# ----------------------------------------------------------------------
# --- Phase 2: Detail Extraction for All Collected IDs ---
# ----------------------------------------------------------------------

total_firms_to_process = len(all_firm_ids)
print(f"\nStarting Phase 2: Retrieving detailed data for {total_firms_to_process} collected firms...")


for i, firm_id in enumerate(all_firm_ids):

    current_firm_index = i + 1
    detail_url = f"{BASE_URL}firma/{firm_id}"

    if current_firm_index % 5 == 0 or current_firm_index == 1 or current_firm_index == total_firms_to_process:
        print(f"  > Processing firm {current_firm_index} of {total_firms_to_process} (ID: {firm_id})...")

    try:
        detail_response = requests.get(detail_url, headers=HEADERS, timeout=15)
        detail_response.raise_for_status()
        detail_data = detail_response.json()

        firm_details = detail_data.get('firma', [{}])[0]

        if not firm_details:
            print(f"Could not find firm details for ID: {firm_id}. Skipping.")
            time.sleep(1)
            continue

        # --- Data Flattening and row creation ---
        row = {
            'id': firm_details.get('id', ''),
            'nazwa': firm_details.get('nazwa', ''),
            'dataRozpoczecia': str(firm_details.get('dataRozpoczecia', '')),
            'dataZakonczenia': str(firm_details.get('dataZakonczenia', '')),
            'status': firm_details.get('status', ''),

            # WLASCIEL
            'imie_wlasciciel': firm_details.get('wlasciciel', {}).get('imie', ''),
            'nazwisko_wlasciciel': firm_details.get('wlasciciel', {}).get('nazwisko', ''),
            'nip': firm_details.get('wlasciciel', {}).get('nip', ''),
            'regon': firm_details.get('wlasciciel', {}).get('regon', ''),

            # ADRES GLOWNEJ DZIALALNOSCI
            'ulica_dzialalnosc': firm_details.get('adresDzialalnosci', {}).get('ulica', ''),
            'miasto_dzialalnosc': firm_details.get('adresDzialalnosci', {}).get('miasto', ''),
            'powiat_dzialalnosc': firm_details.get('adresDzialalnosci', {}).get('powiat', ''),
            'wojewodztwo_dzialalnosc': firm_details.get('adresDzialalnosci', {}).get('wojewodztwo', ''),
            'kod_dzialalnosc': firm_details.get('adresDzialalnosci', {}).get('kod', ''),

            # GLOWNY PKD
            'kod_pkd_glowny': firm_details.get('pkdGlowny', {}).get('kod', '')[:2],
            'nazwa_pkd_glowny': firm_details.get('pkdGlowny', {}).get('nazwa', ''),
        }

        csv_data.append(row)
        time.sleep(5)

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving details for ID {firm_id}: {e}")
        time.sleep(1)
        continue
    except Exception as e:
        print(f"Unexpected error for ID {firm_id}: {e}")
        time.sleep(1)
        continue

print(f"\nPhase 2 Complete. Prepared {len(csv_data)} records for export.")

# ----------------------------------------------------------------------
# --- Phase 3: CSV Export ---
# ----------------------------------------------------------------------
if csv_data:
    fieldnames = list(csv_data[0].keys())
    try:
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"\nData successfully written to **{CSV_FILENAME}**")
    except IOError as e:
        print(f"I/O Error during CSV writing: {e}")
else:
    print("\nNo data to write to CSV.")