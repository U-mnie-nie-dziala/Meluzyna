# 📈 Indeks Branż – Model Oceny Koniunktury Gospodarczej

## 📖 O projekcie

Projekt powstał w odpowiedzi na wyzwanie opracowania **„Indeksu Branż”** – narzędzia analitycznego prezentującego aktualną sytuację oraz perspektywy rozwoju sektorów polskiej gospodarki.

Rozwiązanie ma na celu wsparcie procesów decyzyjnych największego polskiego banku w zakresie strategii finansowania przedsiębiorstw. Model identyfikuje branże o zdrowych fundamentach oraz te narażone na podwyższone ryzyko, umożliwiając budowę bezpiecznego portfela kredytowego.

---

## 🧠 Metodologia i Uzasadnienie (Kluczowe Założenia)

Zgodnie z wymogami konkursowymi, poniżej przedstawiono szczegółowe uzasadnienie przyjętego podejścia badawczego.

### 1. Definicja Branży i Klasyfikacja
Do analizy przyjęto klasyfikację opartą na kodach **PKD (Polska Klasyfikacja Działalności)** / NACE.

* **Uzasadnienie wyboru:** PKD jest obligatoryjnym standardem dla każdego podmiotu gospodarczego w Polsce. Użycie tego standardu zapewnia kompletność danych oraz spójność z raportowaniem europejskim.
* **Obsługa zmian klasyfikacji (2007 vs 2025):** Ze względu na zmianę klasyfikacji w 2025 roku, model uwzględnia mapowanie danych historycznych (dostępnych w układzie 2007) na nowe standardy, co pozwala zachować ciągłość analizy trendów.

### 2. Poziom Agregacji Danych
Analizę przeprowadzono na poziomie **Działu** (np. 46 – handel hurtowy) lub **Grupy** (np. 46.1).

* **Uzasadnienie:** Przyjęcie tego poziomu stanowi optymalny kompromis między dostępnością danych a precyzją wnioskowania. Wyższy poziom agregacji zapewnia większą próbę statystyczną, minimalizując błędy wynikające z jednostkowych zdarzeń w małych firmach.

### 3. Horyzont Czasowy
Model ocenia nie tylko stan obecny, ale prognozuje perspektywy w horyzoncie **12-36 miesięcy**.

* **Uzasadnienie:** Taki okres jest kluczowy dla strategii kredytowych (krótko- i średnioterminowych), pozwalając bankowi reagować na nadchodzące zmiany cyklu koniunkturalnego.

---

## 📊 Składowe Indeksu (Dobór Wskaźników)

Ocena kondycji branży opiera się na wielowymiarowym modelu scoringowym. Wybrano wskaźniki, które najlepiej obrazują zarówno stabilność, jak i potencjał wzrostu.

### A. Fundamenty Finansowe (Ocena Historyczna)
Wykorzystano twarde dane finansowe przedsiębiorstw:

1.  **Dynamika Rozwoju:** Zmiana przychodów i aktywów r/r. Pozwala zidentyfikować sektory w fazie ekspansji.
2.  **Rentowność:** Marża zysku (zysk/przychody). Kluczowa miara odporności branży na wzrost kosztów.
3.  **Ryzyko i Zadłużenie:** Poziom długu oraz jego dynamika. Wskazuje na potencjalne problemy z płynnością.
4.  **Szkodowość:** Procent upadłości w danym sektorze. Bezpośredni sygnał ryzyka kredytowego.

### B. Dane Alternatywne (Perspektywy)
W celu zwiększenia wartości predykcyjnej modelu, analizę uzupełniono o zmienne niefinansowe:

* **Sentyment rynkowy:** Analiza trendów w mediach i internecie (nastroje konsumenckie).
* **Uzasadnienie:** Dane finansowe są danymi opóźnionymi (lagging indicators). Dane alternatywne pełnią funkcję wyprzedzającą (leading indicators), sygnalizując zmiany popytu zanim pojawią się w raportach kwartalnych.

---

## 💻 Aspekty Techniczne

Rozwiązanie zostało zaimplementowane w języku **Python**, z wykorzystaniem bibliotek do analizy danych i wizualizacji.

### Możliwości Wdrożeniowe
Zgodnie z kontekstem biznesowym, rozwiązanie zaprojektowano tak, aby mogło działać jako **aplikacja cykliczna**. System automatycznie zaciąga nowe dane po ich publikacji, odświeża ocenę branży i generuje zaktualizowane rekomendacje dla analityków.

---

## 🚀 Instrukcja Uruchomienia

1.  Zainstaluj wymagane zależności:
    ```bash
    pip install -r requirements.txt
    ```
2.  Uruchom skrypt generujący indeks:
    ```bash
    python src/main.py
    ```