Ekstrakcja (Extract):

    Źródło Tickerów: Plik lokalny tickers_cache.json (jako baza) + skanowanie strony Bankier.pl w poszukiwaniu nowych debiutów giełdowych.

    Źródło Danych Finansowych: API yfinance. Pobierane są surowe metryki dla każdej spółki osobno.

Transformacja (Transform):

    Mapowanie: Przypisanie każdej spółki do sekcji PKD (np. "KGHM" -> "B - Górnictwo") na podstawie branży z Yahoo Finance.

    Czyszczenie: Konwersja danych tekstowych na liczbowe, usuwanie błędów (NaN, Infinity).

    Agregacja: Obliczenie mediany dla każdego wskaźnika wewnątrz sektora. Użycie mediany zamiast średniej jest kluczowe, aby pojedyncze gigantyczne spółki (jak Orlen czy PKO BP) nie zafałszowały obrazu całego sektora.

Wycena (Scoring):

    Zastosowanie algorytmu punktowego do zagregowanych danych sektorowych.

    Generowanie raportu końcowego w formacie JSON. I przesłanie danych do bazy danych

Algorytm Liczenia Ratingu

System oblicza wynik punktowy w skali 0-100 dla każdego sektora. Wynik ten jest sumą ważoną pięciu statystyk  
1: Rentowność Operacyjna (Waga: 25 pkt)

Określa, jak duży margines bezpieczeństwa posiada sektor w przypadku wzrostu kosztów.

    Metryka: Mediana Marży Zysku Netto (Profit Margin).

    Logika: Im wyższa marża, tym lepiej.

    Wzór: min((max(0, margin) / 0.15), 1.0) * 25

    Próg nasycenia: 15% marży netto daje maksymalną liczbę punktów.

2: Efektywność Kapitałowa (Waga: 15 pkt)

Określa, jak sprawnie zarządy spółek w danym sektorze pomnażają kapitał akcjonariuszy.

    Metryka: Mediana ROE (Return on Equity).

    Logika: Preferowane są sektory, które generują wysoki zwrot z kapitału własnego.

    Wzór: min((max(0, roe) / 0.12), 1.0) * 15

    Próg nasycenia: 12% ROE daje maksymalną liczbę punktów.

3: Skala i Płynność Rynku (Waga: 10 pkt)

Nagradza sektory duże i zdywersyfikowane, karze sektory niszowe (np. składające się z 1-2 spółek), gdzie ryzyko idiosynkratyczne jest wysokie.

    Metryka: Liczba spółek w sektorze.

    Wzór: min(row['MarketCap_get_count'] / 10, 1.0) * 10

    Próg nasycenia: 10 spółek w sektorze.

4: Przepływy Pieniężne / Dywidenda (Waga: 20 pkt)

Wypłacane dywidendy są ciężkie do zmanipulowania, im większe tym lepiej

    Metryka: Mediana Stopy Dywidendy (Dividend Yield).

    Wzór: min((div / 0.04), 1.0) * 20

    Próg nasycenia: Stopa dywidendy 4% lub wyższa.

5: Wycena Rynkowa (Waga: 30 pkt)

Najważniejszy filar w analizie bezpieczeństwa – ochrona przed kupowaniem "bańki spekulacyjnej".

    Metryka: Mediana Ceny do Zysku (P/E Ratio).

    Logika:

        Bezpieczna strefa (5 ≤ P/E ≤ 25): 30 pkt (Maksimum). Sektor jest wyceniany racjonalnie.

        Strefa ostrzegawcza (25 < P/E ≤ 40): 10 pkt. Sektor jest drogi.

        Strefa ryzyka (P/E > 40 lub P/E < 5): 0 pkt. Oznacza bańkę spekulacyjną lub sektor w głębokim kryzysie/stracie.