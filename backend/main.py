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