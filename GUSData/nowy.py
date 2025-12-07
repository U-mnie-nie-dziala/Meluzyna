import requests
import pandas as pd
import sys
import re
import os
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GUS_API_KEY")
HEADERS = {"X-ClientId": API_KEY}
BASE_URL = "https://bdl.stat.gov.pl/api/v1"
ILE_LAT_WSTECZ = 5

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

if not all([API_KEY, DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT]):
    print("Blad: Brak zmiennych srodowiskowych w pliku .env")
    sys.exit(1)

db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


def tlumacz_i_skroc(nazwa_z_gus):
    n = nazwa_z_gus.lower()
    if "rolnictwo" in n or "łowiectwo" in n or "leśnictwo" in n or "rybołówstwo" in n: return "[A] Rolnictwo, leśnictwo, łowiectwo i rybactwo"
    if "górnictwo" in n or "wydobywanie" in n: return "[B] Górnictwo i wydobywanie"
    if "przetwórstwo" in n and "przemysłowe" in n: return "[C] Przetwórstwo przemysłowe"
    if "wytwarzanie" in n and "energię" in n or "dostawa pary" in n or "klimatyzacja" in n: return "[D] Wytwarzanie i zaopatrywanie w energię elektryczną, gaz, parę wodną i gorącą wodę"
    if "dostawa wody" in n or "gospodarowanie odpadami" in n or "rekultywacja" in n: return "[E] Dostawa wody; gospodarowanie ściekami i odpadami; rekultywacja"
    if "budownictwo" in n: return "[F] Budownictwo"
    if "handel" in n or "naprawa pojazdów" in n: return "[G] Handel hurtowy i detaliczny; naprawa pojazdów samochodowych, włączając motocykle"
    if "transport" in n or "gospodarka magazynowa" in n: return "[H] Transport i gospodarka magazynowa"
    if "zakwaterowanie" in n or "gastronomia" in n or "usługi gastronomiczne" in n or "hotele i restauracje" in n: return "[I] Działalność związana z zakwaterowaniem i usługami gastronomicznymi"
    if "informacja" in n and "komunikacja" in n or "telekomunikacja" in n or "wydawnictwa" in n: return "[J] Informacja i komunikacja"
    if "finansowa" in n or "ubezpieczeniowa" in n: return "[K] Działalność finansowa i ubezpieczeniowa"
    if "nieruchomości" in n: return "[L] Działalność związana z obsługą rynku nieruchomości"
    if "profesjonalna" in n or "naukowa" in n or "techniczna" in n: return "[M] Działalność profesjonalna, naukowa i techniczna"
    if "administrowanie" in n or "obsługa" in n and "biurowa" in n or "działalność w zakresie usług administrowania i działalność wspierająca" in n: return "[N] Działalność w zakresie usług administrowania i działalność wspierająca"
    if "administracja publiczna" in n or "obrona" in n or "zabezpieczenia społeczne" in n or "obowiązkowe ubezpieczenia" in n: return "[O] Administracja publiczna i obrona narodowa; obowiązkowe zabezpieczenia społeczne"
    if "edukacja" in n or "oświata" in n: return "[P] Edukacja"
    if "opieka zdrowotna" in n or "pomoc społeczna" in n: return "[Q] Opieka zdrowotna i pomoc społeczna"
    if "kultura" in n or "rozrywka" in n or "sztuka" in n or "sport" in n or "działalność związana z kulturą, rozrywką i rekreacją" in n: return "[R] Działalność związana z kulturą, rozrywką i rekreacją"
    if "pozostała działalność usługowa" in n or "usługowa komunalna" in n or "indywidualna" in n: return "[S] Pozostała działalność usługowa"
    if "gospodarstwa domowe" in n: return "[T] Gospodarstwa domowe zatrudniające pracowników"
    if "organizacje i zespoły" in n or "eksterytorialne" in n: return "[U] Organizacje i zespoły eksterytorialne"
    if "sektor publiczny" in n or "sektor prywatny" in n or "ogółem" in n or "ogółem (wiersz)" in n: return "FILTR"
    return "[?] Nieznana"


print(f"Pobieranie danych finansowych (Ostatnie {ILE_LAT_WSTECZ} lat)...")

url_search = f"{BASE_URL}/variables/search"
params_search = {"name": "przychody z całokształtu działalności", "page-size": 100}

baza_danych = []
znalezione_sekcje = set()
ranking_series = pd.Series(dtype='float64')

try:
    response = requests.get(url_search, headers=HEADERS, params=params_search)
    wyniki = response.json().get('results', [])
    print(f"Znaleziono {len(wyniki)} zmiennych. Przetwarzanie...")

    for z in wyniki:
        pelna_nazwa = f"{z.get('n1')} {z.get('n2')} {z.get('n3')}".lower()
        if "wskaźnik" in pelna_nazwa or "dynamika" in pelna_nazwa or "na 1 podmiot" in pelna_nazwa: continue

        nazwa_branze = z.get('n2')
        if not nazwa_branze or "przychody" in nazwa_branze.lower(): nazwa_branze = z.get('n3')

        if nazwa_branze and "ogółem" not in nazwa_branze.lower():
            krotka_nazwa = tlumacz_i_skroc(nazwa_branze)

            if krotka_nazwa != "[?] Nieznana" and krotka_nazwa != "FILTR" and krotka_nazwa not in znalezione_sekcje:
                url_dane = f"{BASE_URL}/data/by-variable/{z['id']}"
                r_dane = requests.get(url_dane, headers=HEADERS, params={"unit-level": 0, "page-size": 100})

                if r_dane.status_code == 200:
                    dane = r_dane.json().get('results', [])
                    if dane:
                        vals = dane[0]['values']
                        vals.sort(key=lambda x: int(x['year']))

                        if vals and int(vals[-1]['year']) >= 2022:
                            znalezione_sekcje.add(krotka_nazwa)
                            zakres_danych = vals[-ILE_LAT_WSTECZ:]
                            for v in zakres_danych:
                                baza_danych.append({
                                    "Branża": krotka_nazwa,
                                    "Rok": v['year'],
                                    "Przychód (Mld zł)": v['val'] / 1000000
                                })
                            print(f"Pobrano: {krotka_nazwa}")

except Exception as e:
    print(f"Blad API: {e}")

if baza_danych:
    df = pd.DataFrame(baza_danych)
    df = df[df['Branża'].str.startswith('[')]

    tabela_numeryczna = df.pivot_table(
        index="Rok", columns="Branża", values="Przychód (Mld zł)", aggfunc='sum'
    )

    tabela_numeryczna.replace(0, np.nan, inplace=True)
    zmiany_roczne = tabela_numeryczna.pct_change()
    raw_median = zmiany_roczne.median()

    BENCHMARK_WZROSTU = 0.25
    score_inwestycyjny = (raw_median / BENCHMARK_WZROSTU) * 100
    score_inwestycyjny = score_inwestycyjny.clip(upper=100)
    score_inwestycyjny = score_inwestycyjny.fillna(0)

    ranking_series = score_inwestycyjny.sort_values(ascending=False)
    print("\nOBLICZONY WSKAZNIK (Score 0-100):")
    print(ranking_series)

else:
    print("Brak danych API.")
    sys.exit(1)

print("\nPRZYGOTOWANIE DO ZAPISU SQL...")
print(f"Laczenie z baza PostgreSQL ({DB_HOST})...")

try:
    engine = create_engine(db_url)
    conn = engine.connect()
    print("Polaczono z baza danych.")

    print("Czyszczenie starej tabeli gus...")
    conn.execute(text("TRUNCATE TABLE gus RESTART IDENTITY;"))
    conn.commit()
    print("Tabela wyczyszczona.")

except Exception as e:
    print(f"Blad polaczenia/czyszczenia: {e}")
    sys.exit(1)

last_id = 0
print(f"Startujemy od ID: {last_id + 1}")

lista_do_zapisu = []
current_id = last_id + 1

for nazwa_branzy, wskaznik in ranking_series.items():
    match = re.search(r'\[([A-Z])\]', nazwa_branzy)

    if match:
        pkd_code = match.group(1)
    else:
        continue

    row = {
        'id': current_id,
        'pkd': pkd_code,
        'wskaznik': round(float(wskaznik), 2)
    }
    lista_do_zapisu.append(row)
    current_id += 1

df_to_save = pd.DataFrame(lista_do_zapisu)
print("Dane do wysylki:")
print(df_to_save.to_string(index=False))

if not lista_do_zapisu:
    print("Brak danych do zapisu.")
    conn.close()
    sys.exit(0)

try:
    trans = conn.begin()
    stmt = text("INSERT INTO gus (id, pkd, wskaznik) VALUES (:id, :pkd, :wskaznik)")
    for row in lista_do_zapisu:
        conn.execute(stmt, row)
    trans.commit()
    print("SUKCES: Dane zapisane w tabeli gus.")

except Exception as e:
    if 'trans' in locals():
        trans.rollback()
    print(f"BLAD ZAPISU: {e}")
finally:
    conn.close()