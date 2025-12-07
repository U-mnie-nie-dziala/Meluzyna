import psycopg2
import pandas as pd
import numpy as np
import datetime
from dotenv import load_dotenv
import os
import glob

# Load environment variables
load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    database=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    port=os.getenv("PGPORT")
)
cur = conn.cursor()

# Fetch PKD mapping from the database
cur.execute("SELECT pkd_2, pkd_pkd FROM slownik_szegolowy_pkd ORDER BY pkd_pkd")
rows = cur.fetchall()
mapping = {row[0]: row[1] for row in rows}



csv_folder = "."
csv_files = glob(os.path.join(csv_folder, "firmy_*.csv"))
filename = max(csv_files, key=os.path.getctime)
print("Processing newest CSV:", filename)
df = pd.read_csv(filename, sep=None, engine="python")


df["kod_pkd_glowny_norm"] = df["kod_pkd_glowny"].astype(int)
df["pkd_letter"] = df["kod_pkd_glowny_norm"].map(mapping)


df["dataRozpoczecia"] = pd.to_datetime(df["dataRozpoczecia"], errors="coerce")
df["dataZakonczenia"] = pd.to_datetime(df["dataZakonczenia"], errors="coerce")


today = pd.Timestamp.today()
df["dataZakonczenia_filled"] = df.apply(
    lambda row: row["dataZakonczenia"] if str(row["status"]).upper() == "WYKRESLONY" else today,
    axis=1
)


df["dni_otwarte"] = (df["dataZakonczenia_filled"] - df["dataRozpoczecia"]).dt.days


df["status_value"] = df["status"].map({
    "AKTYWNY": 1,
    "WYKRESLONY": -1
})


df["points"] = np.log1p(df["dni_otwarte"])


pkd_summary = df.groupby("pkd_letter").agg(
    active_count=("status_value", "sum"),
    total_points=("points", "sum")
)


min_points = pkd_summary["total_points"].min()
max_points = pkd_summary["total_points"].max()
pkd_summary["points_normalized"] = (pkd_summary["total_points"] - min_points) / (max_points - min_points) * 100


date_str = filename.split("_")[1]
time_str = filename.split("_")[2].split(".")[0]
dt = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")


df_to_insert = pkd_summary.reset_index()


insert_query = """
INSERT INTO ceidg (pkd_id, wskaznik, utworzono)
VALUES (%s, %s, %s)
"""

for _, row in df_to_insert.iterrows():
    cur.execute(insert_query, (row["pkd_letter"], row["points_normalized"], dt))

conn.commit()


print("Data inserted successfully with timestamp:", dt)
print(pkd_summary.sort_values("points_normalized", ascending=False))


cur.close()
conn.close()
