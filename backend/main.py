from numbers import Number
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, selectinload
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, select, desc, BigInteger, func, TIMESTAMP, Float
from pydantic import BaseModel, ConfigDict # Changed here
from typing import List, Optional
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
    total_cap_pln = Column(Integer)
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

class CeidgDB(Base):
    __tablename__ = "ceidg"
    id = Column(Integer, primary_key=True, index=True)
    pkd_id = Column(String(2))
    wskaznik = Column(BigInteger)
    utworzono = Column(TIMESTAMP)

class TagDB(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(50))
    pkd_id = Column(String(2))

class YoutubeCommentDB(Base):
    __tablename__ = "komentarz_youtube"

    id = Column(Integer, primary_key=True, index=True)
    komentarz = Column(String)
    tag_id = Column(Integer, ForeignKey("tags.id"))
    timestamp = Column(TIMESTAMP)
    emocje = Column(Integer)

class WykopPostDB(Base):
    __tablename__ = "post_wykop"

    id = Column(Integer, primary_key=True, index=True)
    post = Column(String)
    tag_id = Column(Integer, ForeignKey("tags.id"))
    emocje = Column(Integer)
    timestamp = Column(TIMESTAMP)

class SectionSchema(BaseModel):
    section_code: str
    section_name: str
    safety_score: int
    rating: str
    median_margin: float
    median_pe: float
    median_roe: float
    median_divident_yield: float
    total_cap_pln: int
    companies_count: int

    model_config = ConfigDict(from_attributes=True)

class ReportSchema(BaseModel):
    id: int
    date: date
    sections: List[SectionSchema] = []

    model_config = ConfigDict(from_attributes=True)

class SimpleScoreSchema(BaseModel):
    section_code: str
    section_name: str
    safety_score: int
    rating: str

    model_config = ConfigDict(from_attributes=True)

class PkdSchema(BaseModel):
    pkd: str
    nazwa: str

    model_config = ConfigDict(from_attributes=True)

class GusSchema(BaseModel):
    id: int
    wskaznik: float
    pkd: str

class CombinedScoreSchema(BaseModel):
    section_code: str
    section_name: str
    market_score: Optional[int] = None       # Wynik z giełdy
    gus_score: Optional[float] = None        # Wynik z GUS
    ceidg_score: Optional[float] = None      # Wynik z ceidg
    social_score: Optional[float] = None     # Wynik z social mediów
    final_score: float    # Średnia z obu

    model_config = ConfigDict(from_attributes=True)

class CeidgSimpleSchema(BaseModel):
    pkd_id: str
    wskaznik: int

    class Config:
        from_attributes = True

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/markets/reports/latest", response_model=ReportSchema)
async def get_latest_report(db: AsyncSession = Depends(get_db)):
    stmt = select(ReportDB).order_by(desc(ReportDB.date)).limit(1)
    result = await db.execute(stmt)
    latest_report = result.scalars().first()

    if not latest_report:
        raise HTTPException(status_code=404, detail="Brak raportów w bazie")

    stmt_full = select(ReportDB).options(selectinload(ReportDB.sections)).where(ReportDB.id == latest_report.id)
    result_full = await db.execute(stmt_full)
    return result_full.scalars().first()

@app.get("/markets/reports/history", response_model=List[ReportSchema])
async def get_reports_history(limit: int = 5, db: AsyncSession = Depends(get_db)):
    stmt = select(ReportDB).order_by(desc(ReportDB.date)).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

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


@app.get("/markets/scores/latest", response_model=List[SimpleScoreSchema])
async def get_latest_scores_only(db: AsyncSession = Depends(get_db)):
    subquery = select(ReportDB.id).order_by(desc(ReportDB.date)).limit(1).scalar_subquery()
    stmt = (
        select(SectionDB)
        .where(SectionDB.report_id == subquery)
        .order_by(desc(SectionDB.safety_score))
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/markets/scores/{section_code}", response_model=SectionSchema)
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

@app.get("/categories", response_model=List[PkdSchema])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(PKD).order_by(PKD.pkd)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    if not categories:
        raise HTTPException(status_code=404, detail=f"Nie znaleziono kategorii")
    return categories

@app.get("/ceidg/scores", response_model=List[CeidgSimpleSchema])
async def get_all_ceidg_scores(db: AsyncSession = Depends(get_db)):

    stmt = select(CeidgDB)
    result = await db.execute(stmt)
    return result.scalars().all()

@app.get("/ceidg/scores/{section_code}", response_model=CeidgSimpleSchema)
async def get_ceidg_score_by_code(section_code: str, db: AsyncSession = Depends(get_db)):

    stmt = (
        select(CeidgDB)
        .where(CeidgDB.pkd_id == section_code.upper())
        .limit(1)
    )

    result = await db.execute(stmt)
    score = result.scalars().first()

    if not score:
        raise HTTPException(status_code=404, detail=f"Nie znaleziono danych CEIDG dla sekcji {section_code}")

    return score


@app.get("/scores", response_model=List[CombinedScoreSchema])
async def get_combined_scores(db: AsyncSession = Depends(get_db)):

    latest_report_subquery = select(ReportDB.id).order_by(desc(ReportDB.date)).limit(1).scalar_subquery()
    res_market = await db.execute(select(SectionDB).where(SectionDB.report_id == latest_report_subquery))
    market_map = {row.section_code: row for row in res_market.scalars().all()}

    res_gus = await db.execute(select(GusScores, PKD).join(PKD))
    gus_map = {row[0].pkd: row for row in res_gus.all()}

    res_ceidg = await db.execute(select(CeidgDB))
    ceidg_map = {row.pkd_id: float(row.wskaznik) for row in res_ceidg.scalars().all()}


    stmt_yt = (
        select(TagDB.pkd_id, func.avg(YoutubeCommentDB.emocje))
        .join(TagDB, YoutubeCommentDB.tag_id == TagDB.id)
        .group_by(TagDB.pkd_id)
    )
    res_yt = await db.execute(stmt_yt)
    yt_rows = res_yt.all()

    stmt_wyk = (
        select(TagDB.pkd_id, func.avg(WykopPostDB.emocje))
        .join(TagDB, WykopPostDB.tag_id == TagDB.id)
        .group_by(TagDB.pkd_id)
    )
    res_wyk = await db.execute(stmt_wyk)
    wyk_rows = res_wyk.all()

    social_temp = {}

    for pkd, score in yt_rows:
        if pkd and score is not None:
            if pkd not in social_temp: social_temp[pkd] = []
            social_temp[pkd].append(float(score))

    for pkd, score in wyk_rows:
        if pkd and score is not None:
            if pkd not in social_temp: social_temp[pkd] = []
            social_temp[pkd].append(float(score))

    social_map = {}
    for pkd, values in social_temp.items():
        if values:
            social_map[pkd] = sum(values) / len(values)

    all_codes = set(market_map.keys()) | set(gus_map.keys()) | set(ceidg_map.keys()) | set(social_map.keys())

    final_results = []

    for code in all_codes:
        valid_values = []

        m_score, g_score, c_score, s_score = None, None, None, None
        section_name = "Nieznana sekcja"

        if code in market_map:
            item = market_map[code]
            val = float(item.safety_score)
            m_score = int(val)
            valid_values.append(val)
            section_name = item.section_name

        if code in gus_map:
            item, pkd_info = gus_map[code]
            val = float(item.wskaznik)
            g_score = val
            valid_values.append(val)
            if section_name == "Nieznana sekcja":
                section_name = pkd_info.nazwa

        if code in ceidg_map:
            val = ceidg_map[code]
            c_score = val
            valid_values.append(val)

        if code in social_map:
            val = social_map[code]
            s_score = round(val, 2)
            valid_values.append(val)

        if valid_values:
            final_val = sum(valid_values) / len(valid_values)
        else:
            final_val = 0.0

        final_results.append({
            "section_code": code,
            "section_name": section_name,
            "market_score": m_score,
            "gus_score": g_score,
            "ceidg_score": c_score,
            "social_score": s_score,
            "final_score": round(final_val, 2)
        })

    final_results.sort(key=lambda x: x["final_score"], reverse=True)
    return final_results


@app.get("/scores/{section_code}", response_model=CombinedScoreSchema)
async def get_combined_score_by_code(section_code: str, db: AsyncSession = Depends(get_db)):
    code = section_code.upper()

    latest_sub = select(ReportDB.id).order_by(desc(ReportDB.date)).limit(1).scalar_subquery()
    res_m = await db.execute(select(SectionDB).where(SectionDB.report_id == latest_sub, SectionDB.section_code == code))
    market_entry = res_m.scalars().first()

    res_g = await db.execute(select(GusScores, PKD).join(PKD).where(GusScores.pkd == code))
    gus_entry = res_g.first()

    res_c = await db.execute(select(CeidgDB).where(CeidgDB.pkd_id == code))
    ceidg_entry = res_c.scalars().first()

    tags_subquery = select(TagDB.id).where(TagDB.pkd_id == code)

    res_yt = await db.execute(
        select(func.avg(YoutubeCommentDB.emocje)).where(YoutubeCommentDB.tag_id.in_(tags_subquery)))
    yt_avg = res_yt.scalar()

    res_wyk = await db.execute(select(func.avg(WykopPostDB.emocje)).where(WykopPostDB.tag_id.in_(tags_subquery)))
    wyk_avg = res_wyk.scalar()

    social_vals = []
    if yt_avg is not None: social_vals.append(yt_avg)
    if wyk_avg is not None: social_vals.append(wyk_avg)

    social_score = sum(social_vals) / len(social_vals) if social_vals else None

    if not any([market_entry, gus_entry, ceidg_entry, social_score is not None]):
        raise HTTPException(status_code=404, detail="Brak danych dla tego sektora")

    valid_values = []

    m_val = None
    if market_entry:
        val = float(market_entry.safety_score)
        m_val = int(val)
        valid_values.append(val)

    g_val = None
    if gus_entry:
        val = float(gus_entry[0].wskaznik)
        g_val = val
        valid_values.append(val)

    c_val = None
    if ceidg_entry:
        val = float(ceidg_entry.wskaznik)
        c_val = val
        valid_values.append(val)

    s_val = None
    if social_score is not None:
        s_val = float(social_score)
        valid_values.append(s_val)

    name = "Nieznana"
    if market_entry:
        name = market_entry.section_name
    elif gus_entry:
        name = gus_entry[1].nazwa

    final = sum(valid_values) / len(valid_values) if valid_values else 0.0

    return {
        "section_code": code,
        "section_name": name,
        "market_score": m_val,
        "gus_score": g_val,
        "ceidg_score": c_val,
        "social_score": round(s_val, 2) if s_val else None,
        "final_score": round(final, 2)
    }

@app.get("/komentarz_youtube")
async def get_all_youtube_comments(db: AsyncSession = Depends(get_db)):
    """
    Returns all rows from komentarz_youtube (YoutubeCommentDB)
    """
    result = await db.execute(select(YoutubeCommentDB))
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(status_code=404, detail="Brak danych w komentarz_youtube")

    return [
        {
            "id": r.id,
            "komentarz": r.komentarz,
            "tag_id": r.tag_id,
            "timestamp": r.timestamp,
            "emocje": r.emocje
        }
        for r in rows
    ]

@app.get("/post_wykop")
async def get_all_youtube_comments(db: AsyncSession = Depends(get_db)):
    """
    Returns all rows from komentarz_youtube (YoutubeCommentDB)
    """
    result = await db.execute(select(YoutubeCommentDB))
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(status_code=404, detail="Brak danych w komentarz_youtube")

    return [
        {
            "id": r.id,
            "tag_id": r.tag_id,
            "post": r.komentarz,
            "timestamp": r.timestamp,
            "emocje": r.emocje
        }
        for r in rows
    ]
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)