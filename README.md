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
### 0. Baza Danych
```
create database hacknation_db
    with owner hack;

create table public.report
(
    id   integer not null
        constraint report_pk
            primary key,
    date date    not null
);

alter table public.report
    owner to hack;

create table public.section
(
    id                    integer         not null
        constraint section_pk
            primary key,
    report_id             integer         not null
        constraint section_report
            references public.report,
    section_code          varchar(2)      not null,
    section_name          varchar(20)     not null,
    safety_score          integer         not null,
    rating                varchar(20)     not null,
    median_margin         numeric(20, 18) not null,
    median_roe            numeric(20, 18) not null,
    median_pe             numeric(20, 18) not null,
    median_divident_yield numeric(20, 18) not null,
    companies_count       integer         not null,
    total_cap_pln         bigint          not null
);

alter table public.section
    owner to hack;

create table public.pkd
(
    pkd   varchar(1)   not null
        constraint pkd_pk
            primary key,
    nazwa varchar(255) not null
);

alter table public.pkd
    owner to hack;

create table public.ceidg
(
    id        integer generated always as identity
        constraint ceidg_pk
            primary key,
    pkd_id    varchar(2) not null
        constraint ceidg_pkd
            references public.pkd,
    wskaznik  bigint,
    utworzono timestamp
);

alter table public.ceidg
    owner to hack;

create table public.gus
(
    id        integer    not null
        constraint gus_pk
            primary key,
    pkd       varchar(2) not null
        constraint gus_pkd
            references public.pkd,
    wskaznik  numeric(6, 2),
    timestamp timestamp,
    year_0    numeric(1000, 5),
    year_1    numeric(1000, 5),
    year_2    numeric(1000, 5),
    year_3    numeric(1000, 5),
    year_4    numeric(1000, 5)
);

alter table public.gus
    owner to hack;

create table public.tag
(
    id       integer     not null
        constraint tag_pk
            primary key,
    tag_name varchar(50) not null,
    pkd_id   varchar(2)  not null
        constraint tagi_pkd
            references public.pkd
);

alter table public.tag
    owner to hack;

create table public.komentarz_youtube
(
    id        integer not null
        constraint komentarz_youtube_pk
            primary key,
    komentarz text    not null,
    tag_id    integer not null
        constraint komentarze_youtube_tag
            references public.tag,
    timestamp timestamp,
    emocje    integer
);

alter table public.komentarz_youtube
    owner to hack;

create table public.post_wykop
(
    id        integer not null
        constraint post_wykop_pk
            primary key,
    tag_id    integer not null
        constraint post_wykop_tag
            references public.tag,
    post      text    not null,
    emocje    integer,
    timestamp timestamp
);

alter table public.post_wykop
    owner to hack;

create table public.slownik_szegolowy_pkd
(
    id              integer      not null
        constraint slownik_szegolowy_pkd_pk
            primary key,
    nazwa_szegolowa varchar(255) not null,
    pkd_pkd         varchar(1)   not null
        constraint slownik_sekcji_pkd_pkd
            references public.pkd,
    pkd_2           integer
);

alter table public.slownik_szegolowy_pkd
    owner to hack;

create function public.clean_bare_links() returns trigger
    language plpgsql
as
$$
BEGIN
    -- REGEX wyjaśnienie:
    -- \S+        -> łapie ciąg znaków (bez spacji) np. "youtube"
    -- \.         -> łapie dosłownie kropkę
    -- (pl|com)   -> łapie konkretne rozszerzenia (możesz dopisać |eu|net itp.)
    -- [[:>:]]    -> (Opcjonalnie) koniec słowa, aby nie ucinać w środku dziwnych zzlepków

    -- Wersja prosta i skuteczna dla Twoich przykładów:
    -- Flaga 'gi' oznacza: Global (wszystkie wystąpienia) + Case Insensitive (ignoruj wielkość liter, np. WP.PL)

    NEW.post := REGEXP_REPLACE(NEW.post, '\S+\.(pl|com|eu|net|org|ai)', '', 'gi');

    -- Usuwanie ewentualnych podwójnych spacji po wycięciu linku
    NEW.post := REGEXP_REPLACE(NEW.post, '\s+', ' ', 'g');

    -- (Opcjonalnie) Usunięcie spacji na początku/końcu wpisu
    NEW.post := TRIM(NEW.post);

    RETURN NEW;
END;
$$;

alter function public.clean_bare_links() owner to hack;

create trigger trigger_remove_bare_links
    before insert or update
    on public.post_wykop
    for each row
execute procedure public.clean_bare_links();

```


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
