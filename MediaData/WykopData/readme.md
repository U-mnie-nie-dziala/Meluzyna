Głównym celem projektu jest Badanie Sentymentu Użytkowników (Sentiment Analysis) na platformie Wykop.pl. Podobnie jak w przypadku innych mediów społecznościowych, interesują nas przede wszystkim ludzkie emocje i reakcje ukryte w treściach publikowanych przez użytkowników.

## Metodologia

Dane są pozyskiwane za pomocą skryptu `wykop.py`, który wykorzystuje oficjalne API v3 serwisu Wykop.pl. Proces przebiega następująco:

1.  **Pobranie tagów**: Skrypt łączy się z bazą danych PostgreSQL i pobiera listę predefiniowanych tagów, które będą monitorowane (np. #gielda, #cpk, #polityka).
2.  **Pobieranie wpisów**: Dla każdego tagu, skrypt pobiera strumień wpisów z API.
3.  **Zapis do bazy**: Treść każdego wpisu jest zapisywana w dedykowanej tabeli w bazie danych, z powiązaniem do tagu, w ramach którego został opublikowany.

## Pytania Badawcze

Chcemy odpowiedzieć na podobne pytania jak w przypadku danych z YouTube, ale w kontekście specyfiki Wykopu:

- Jaki jest odbiór społeczny kluczowych inwestycji (np. CPK, Elektrownie jądrowe) i tematów politycznych?
- Jak zmieniają się nastroje użytkowników w tagach o tematyce finansowej (np. #gielda, #kryptowaluty) w zależności od sytuacji na rynkach?
- Jak wydarzenia ze świata rzeczywistego wpływają na ton dyskusji na Wykopie?

## Zastosowanie

Zebrane dane tekstowe posłużą jako zbiór treningowy dla modeli uczenia maszynowego (ML). Celem jest stworzenie narzędzi zdolnych do automatycznej klasyfikacji opinii jako pozytywne, negatywne lub neutralne, co pozwoli na analizę sentymentu na dużą skalę.
