from numbers import Number

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, select, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from fastapi.middleware.cors import CORSMiddleware


DB_USER = "hack"
DB_PASS = "HackNation!"
DB_HOST = "212.132.76.195"
DB_NAME = "hacknation_db"
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:5433/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class ReportDB(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)

    # Relacja do sekcji (Jeden Raport -> Wiele Sekcji)
    sections = relationship("SectionDB", back_populates="report")


class SectionDB(Base):
    __tablename__ = "section"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("report.id"), nullable=False)
    section_code = Column(String(2))
    section_name = Column(String(20))
    safety_score = Column(Integer)
    rating = Column(String(20))

    median_margin = Column(Numeric(20, 18))
    median_roe = Column(Numeric(20, 18))
    median_pe = Column(Numeric(20, 18))
    median_divident_yield = Column(Numeric(20, 18))

    companies_count = Column(Integer)
    total_cap_pln = Column(Integer)  # BigInt mapuje się na Integer/Long

    report = relationship("ReportDB", back_populates="sections")


class PKD(Base):
    __tablename__ = "pkd"
    pkd = Column(String(1), primary_key=True, index=True)
    nazwa = Column(String(255))
    pkds = relationship("GusScores", back_populates="pkd_rel")


class GusScores(Base):
    __tablename__ = "gus"
    id = Column(Integer, primary_key=True, index=True)
    wskaznik = Column(Numeric(4, 2))
    pkd = Column(String(2), ForeignKey("pkd.pkd"), nullable=False)
    pkd_rel = relationship("PKD", back_populates="pkds")

class SectionSchema(BaseModel):
    section_code: str
    section_name: str
    safety_score: int
    rating: str
    median_margin: float
    median_pe: float
    companies_count: int

    class Config:
        from_attributes = True

class ReportSchema(BaseModel):
    id: int
    date: date
    sections: List[SectionSchema] = []

    class Config:
        from_attributes = True

class SimpleScoreSchema(BaseModel):
    section_code: str
    section_name: str
    safety_score: int
    rating: str

    class Config:
        from_attributes = True

class PkdSchema(BaseModel):
    pkd: str
    nazwa: str

    class Config:
        from_attributes = True

class GusSchema(BaseModel):
    id: int
    wskaznik: float
    pkd: str

class CombinedScoreSchema(BaseModel):
    section_code: str
    section_name: str
    market_score: Optional[int] = None       # Wynik z giełdy (0-100)
    gus_score: Optional[float] = None        # Wynik z GUS
    final_score: float    # Średnia z obu

    class Config:
        from_attributes = True

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/")
def read_root():
    return {"Hello": "World"}


"""
    ------ 
    Część api do raportów z giełdy
    TO NIE JEST FINALNE API, TO TYLKO CZĘŚĆ Z GIEŁDY FINALNE WYNIKI TRZEBA JESZCZE PRZELICZYĆ!!!!!!!!
    ------
"""

#najnowszy raport
@app.get("/markets/reports/latest", response_model=ReportSchema)
async def get_latest_report(db: AsyncSession = Depends(get_db)):
    stmt = select(ReportDB).order_by(desc(ReportDB.date)).limit(1)
    result = await db.execute(stmt)
    latest_report = result.scalars().first()

    if not latest_report:
        raise HTTPException(status_code=404, detail="Brak raportów w bazie")

    from sqlalchemy.orm import selectinload
    stmt_full = select(ReportDB).options(selectinload(ReportDB.sections)).where(ReportDB.id == latest_report.id)
    result_full = await db.execute(stmt_full)
    report_with_sections = result_full.scalars().first()

    return report_with_sections

#lista ostatnich raportów
@app.get("/markets/reports/history", response_model=List[ReportSchema])
async def get_reports_history(limit: int = 5, db: AsyncSession = Depends(get_db)):
    stmt = select(ReportDB).order_by(desc(ReportDB.date)).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


#najlepsze kategorie z najnowszego raportu
@app.get("/markets/sectors/top", response_model=List[SectionSchema])
async def get_top_sectors(limit: int = 5, db: AsyncSession = Depends(get_db)):
    subquery = select(ReportDB.id).order_by(desc(ReportDB.date)).limit(1).scalar_subquery()

    stmt = (
        select(SectionDB)
        .where(SectionDB.report_id == subquery)
        .order_by(desc(SectionDB.safety_score))
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


#historia dla danej kategorii
@app.get("/markets/sectors/{section_code}", response_model=List[SectionSchema])
async def get_sector_history(section_code: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SectionDB)
        .join(ReportDB)
        .where(SectionDB.section_code == section_code.upper())
        .order_by(desc(ReportDB.date))
    )
    result = await db.execute(stmt)
    return result.scalars().all()

#lista wyników w zależności od kategorii
@app.get("markets/scores/latest", response_model=List[SimpleScoreSchema])
async def get_latest_scores_only(db: AsyncSession = Depends(get_db)):

    subquery = select(ReportDB.id).order_by(desc(ReportDB.date)).limit(1).scalar_subquery()

    stmt = (
        select(SectionDB)
        .where(SectionDB.report_id == subquery)
        .order_by(desc(SectionDB.safety_score))
    )

    result = await db.execute(stmt)
    return result.scalars().all()


# sam wynik dla danej kategorii
@app.get("markets/scores/{section_code}", response_model=SimpleScoreSchema)
async def get_single_sector_score(section_code: str, db: AsyncSession = Depends(get_db)):

    stmt = (
        select(SectionDB)
        .join(ReportDB)
        .where(SectionDB.section_code == section_code.upper())
        .order_by(desc(ReportDB.date))
        .limit(1)
    )

    result = await db.execute(stmt)
    section = result.scalars().first()

    if not section:
        raise HTTPException(status_code=404, detail=f"Nie znaleziono danych dla sektora {section_code}")

    return section

"""
---------------------------------------------------------------------------
"""

#wyniki od kuby
@app.get("/gus/scores", response_model=List[GusSchema])
async def get_gus_scores(db: AsyncSession = Depends(get_db)):

    stmt = (
        select(GusScores)
        .join(PKD)
        .where(GusScores.pkd == PKD.pkd)
    )

    result = await db.execute(stmt)
    scores = result.scalars().all()

    if not scores:
        raise HTTPException(status_code=404, detail=f"Scores not found")

    return scores

@app.get("/gus/scores/{section_code}", response_model=GusSchema)
async def get_gus_score_by_section_code(section_code: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(GusScores, PKD)
        .join(PKD)
        .where(GusScores.pkd == PKD.pkd)
        .where(PKD.pkd == section_code.upper())
        .limit(1)
    )

    result = await db.execute(stmt)
    scores = result.scalars().first()

    if not scores:
        raise HTTPException(status_code=404, detail=f"Score {section_code} not found")

    return scores

#lista kategorii, opis i kod
@app.get("/categories", response_model=List[PkdSchema])
async def get_all_categories(db: AsyncSession = Depends(get_db)):

    stmt = (
        select(PKD).order_by(PKD.pkd)
    )

    result = await db.execute(stmt)
    categories = result.scalars().all()

    if not categories:
        raise HTTPException(status_code=404, detail=f"Nie znaleziono kategorii")

    return categories


@app.get("/scores", response_model=List[CombinedScoreSchema])
async def get_combined_scores(db: AsyncSession = Depends(get_db)):
    """
    Zwraca zestawienie dla WSZYSTKICH sektorów.
    - Jeśli dane są w obu źródłach -> Średnia.
    - Jeśli tylko w jednym -> Wynik z tego jednego źródła.
    """

    # --- 1. POBIERZ DANE RYNKOWE (Market) ---
    latest_report_subquery = (
        select(ReportDB.id)
        .order_by(desc(ReportDB.date))
        .limit(1)
        .scalar_subquery()
    )

    stmt_market = select(SectionDB).where(SectionDB.report_id == latest_report_subquery)
    result_market = await db.execute(stmt_market)
    market_rows = result_market.scalars().all()

    # Zamień listę na słownik dla szybkiego dostępu: { "F": obiekt_db, "K": obiekt_db }
    market_dict = {row.section_code: row for row in market_rows}

    # --- 2. POBIERZ DANE GUS ---
    # Dołączamy tabelę PKD, żeby mieć nazwę sektora, jeśli brakuje go w danych rynkowych
    stmt_gus = select(GusScores, PKD).join(PKD, GusScores.pkd == PKD.pkd)
    result_gus = await db.execute(stmt_gus)
    gus_rows = result_gus.all()  # Zwraca listę krotek (GusScores, PKD)

    # Słownik: { "F": (wynik_gus, nazwa_z_pkd) }
    gus_dict = {row[0].pkd: (row[0], row[1]) for row in gus_rows}

    # --- 3. POŁĄCZ DANE (FULL OUTER JOIN LOGIC) ---

    # Zbiór wszystkich unikalnych kodów z obu źródeł
    all_codes = set(market_dict.keys()) | set(gus_dict.keys())

    final_results = []

    for code in all_codes:
        market_entry = market_dict.get(code)
        gus_entry_tuple = gus_dict.get(code)  # To jest krotka (GusScores, PKD)

        # Wartości domyślne
        m_score = None
        g_score = None
        final_val = 0.0

        # Ustalamy nazwę sektora (priorytet ma nazwa z Rynku, jeśli brak - to z tabeli PKD)
        sec_name = "Nieznany Sektor"
        if market_entry:
            sec_name = market_entry.section_name
        elif gus_entry_tuple:
            sec_name = gus_entry_tuple[1].nazwa  # Pobieramy nazwę z tabeli PKD

        # --- LOGIKA LICZENIA ---

        if market_entry:
            m_score = int(market_entry.safety_score)

        if gus_entry_tuple:
            g_score = float(gus_entry_tuple[0].wskaznik)

        # Scenariusz A: Są oba wyniki -> Liczymy średnią
        if m_score is not None and g_score is not None:
            final_val = (m_score + g_score) / 2.0

        # Scenariusz B: Tylko Rynek -> Wynik to wynik rynkowy
        elif m_score is not None:
            final_val = float(m_score)

        # Scenariusz C: Tylko GUS -> Wynik to wynik GUS
        elif g_score is not None:
            final_val = float(g_score)

        # Dodaj do listy wynikowej
        final_results.append({
            "section_code": code,
            "section_name": sec_name,
            "market_score": m_score,
            "gus_score": g_score,
            "final_score": round(final_val, 2)
        })

    # Opcjonalnie: sortowanie po wyniku końcowym malejąco
    final_results.sort(key=lambda x: x["final_score"], reverse=True)

    return final_results

# --- ENDPOINT 2: Konkretny sektor ---
app.get("/scores/{section_code}", response_model=CombinedScoreSchema)


async def get_combined_score_by_code(section_code: str, db: AsyncSession = Depends(get_db)):
    code = section_code.upper()

    # 1. Pobierz dane rynkowe
    latest_report_subquery = (
        select(ReportDB.id)
        .order_by(desc(ReportDB.date))
        .limit(1)
        .scalar_subquery()
    )
    stmt_market = select(SectionDB).where(SectionDB.report_id == latest_report_subquery, SectionDB.section_code == code)
    res_market = await db.execute(stmt_market)
    market_entry = res_market.scalars().first()

    # 2. Pobierz dane GUS
    stmt_gus = select(GusScores, PKD).join(PKD).where(GusScores.pkd == code)
    res_gus = await db.execute(stmt_gus)
    gus_entry_row = res_gus.first()  # (GusScores, PKD)

    if not market_entry and not gus_entry_row:
        raise HTTPException(status_code=404, detail="Brak danych dla tego sektora w obu źródłach")

    # 3. Logika łączenia
    m_score = int(market_entry.safety_score) if market_entry else None
    g_score = float(gus_entry_row[0].wskaznik) if gus_entry_row else None

    # Nazwa
    sec_name = market_entry.section_name if market_entry else gus_entry_row[1].nazwa

    # Liczenie
    if m_score is not None and g_score is not None:
        final = (m_score + g_score) / 2.0
    elif m_score is not None:
        final = float(m_score)
    else:
        final = float(g_score)

    return {
        "section_code": code,
        "section_name": sec_name,
        "market_score": m_score,
        "gus_score": g_score,
        "final_score": round(final, 2)
    }