# 📈 GUS Financial Trend Analyzer (PKD Scorer)

**Narzędzie analityczne w Pythonie, automatyzujące ocenę kondycji finansowej sektorów gospodarki w Polsce.**

System pobiera dane z Głównego Urzędu Statystycznego (BDL), przetwarza je i generuje **Score Inwestycyjny (0-100)** dla każdej sekcji PKD. Wyniki są zapisywane w bazie PostgreSQL i służą do identyfikacji trendów makroekonomicznych oraz wspierania decyzji inwestycyjnych.

---

## 📋 Spis treści
1. [Cel Biznesowy](#-cel-biznesowy)
2. [Metodologia Wskaźnika](#-metodologia-wskaźnika-algorytm)
3. [Instalacja i Konfiguracja](#-instalacja-i-konfiguracja)
4. [Uruchomienie](#-uruchomienie)
5. [Raport Analityczny: Logika Biznesowa](#-raport-analityczny-uzasadnienie-modelu)

---

## 🎯 Cel Biznesowy
Głównym zadaniem skryptu jest identyfikacja najszybciej rozwijających się branż w Polsce przy jednoczesnym odfiltrowaniu szumu informacyjnego (np. anomalii wywołanych pandemią lub jednorazowymi zdarzeniami księgowymi).

**Zastosowanie danych:**
* **Wskazywanie trendów makroekonomicznych:** Szybka ocena kondycji polskiej gospodarki.
* **Wspieranie decyzji inwestycyjnych:** Selekcja sektorów z potencjałem wzrostu.
* **Analiza ryzyka:** Identyfikacja sektorów kurczących się.

---

## 📊 Metodologia Wskaźnika (Algorytm)
Zastosowano zaawansowany model oceny, aby przekształcić surowe dane finansowe w czytelny ranking.

**Dane Źródłowe:** Przychody z całokształtu działalności (szereg czasowy: ostatnie 5 lat).

1.  **Normalizacja:** Zamiana wartości `0` na `NaN` (brak danych), aby uniknąć fałszywych spadków o 100%.
2.  **Dynamika R/R:** Obliczenie procentowej zmiany rok do roku dla każdego okresu.
3.  **Mediana (Odporność na Błędy):** Wyciągnięcie mediany wzrostów, a nie średniej. Dzięki temu jeden rok kryzysowy (np. COVID) lub jeden rok anomalnego wzrostu nie zafałszowuje oceny stabilności branży.
4.  **Skalowanie do Benchmarku (Score 0-100):**
    * Przyjęto **Benchmark Wzrostu = 25% rocznie**.
    * Wzrost ≥ 25% = **100 pkt**.
    * Wzrost 12.5% = **50 pkt**.
    * Wzrost ujemny/zerowy = niskie punkty.
    * *Wynik jest przycinany (capped) do 100, aby zachować czytelność wykresów.*

---

## ⚙️ Instalacja i Konfiguracja

### 1. Wymagania
* Python 3.8+
* PostgreSQL

### 2. Instalacja bibliotek
Zaleca się użycie wirtualnego środowiska (`venv`).

```bash
pip install pandas sqlalchemy psycopg2-binary requests python-dotenv numpy