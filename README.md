# Meluzyna - Market Analysis Platform

Meluzyna to kompleksowa platforma analityczna zaprojektowana do monitorowania i analizy sektorów gospodarczych (PKD). Aplikacja integruje dane giełdowe, wskaźniki ekonomiczne (GUS), dane o firmach (CEIDG) oraz nastroje społeczne z mediów (Youtube, Wykop).

## Struktura Projektu

Projekt składa się z dwóch głównych komponentów oraz skryptów pomocniczych:

- **`frontend/`**: Aplikacja webowa napisana w React (Vite + TypeScript + Tailwind CSS).
- **`backend/`**: Serwer API oparty na FastAPI i SQLAlchemy.
- **Skrypty analityczne**:
  - `financial_analysis_scripts/`: Skrypty do zbierania i analizy danych finansowych.
  - `CEIDG_data_collection_analysis/`: Narzędzia do pobierania i przetwarzania danych z CEIDG.
  - `GUSData/`: Obsługa danych z Głównego Urzędu Statystycznego.
  - `youtubeData/`: Skrypty do pobierania i analizy komentarzy z Youtube.

## Technologie

### Frontend
- **React 18**: Biblioteka UI.
- **Vite**: Narzędzie budowania i serwer deweloperski.
- **TypeScript**: Typowanie statyczne.
- **Tailwind CSS**: Stylowanie.
- **Recharts / Chart.js**: Wizualizacja danych i wykresy.
- **Lucide React**: Ikony.

### Backend
- **FastAPI**
- **SQLAlchemy (AsyncIO)**
- **Pydantic**
- **Uvicorn**

## Uruchomienie

### Wymagania wstępne
- Node.js (wersja 16+)
- Python (wersja 3.8+)
- Baza danych PostgreSQL (dostępna pod adresem skonfigurowanym w `backend/main.py`).

### 1. Backend

Przejdź do katalogu backendu, aktywuj środowisko wirtualne i uruchom serwer:

```bash
cd backend
# Aktywacja venv (Windows)
.\venv\Scripts\activate
# Instalacja zależności (jeśli wymagane)
pip install -r requirements.txt 
# Uruchomienie serwera (domyślnie port 8001)
python main.py
```

API będzie dostępne pod adresem: `http://127.0.0.1:8000`. Dokumentacja Swagger UI: `http://127.0.0.1:8000/docs`.

### 2. Frontend

Przejdź do katalogu frontendu, zainstaluj zależności i uruchom serwer deweloperski:

```bash
cd frontend
npm install
npm run dev
```

Aplikacja będzie dostępna pod adresem wskazanym przez Vite (zazwyczaj `http://localhost:5173`).

## Kluczowe Funkcjonalności

1.  **Analiza Sektorowa**: Wybór sektora PKD i wyświetlanie skonsolidowanych statystyk.
2.  **Rankingi**: Porównanie wyników sektorów pod względem bezpieczeństwa inwestycyjnego i potencjału.
3.  **Wskaźnik Syntetyczny**: Unikalny algorytm łączący dane twarde (giełda, GUS) z miękkimi (sentyment w social media).
4.  **Wykresy Historyczne**: Wizualizacja trendów w czasie dla wskaźników nastrojów i danych ekonomicznych.
5.  **Analiza Ryzyka**: Prezentacja poziomu ryzyka inwestycyjnego ("Low", "Medium", "High") na podstawie wskaźników finansowych.

## Autor

U mnie (nie) działa
