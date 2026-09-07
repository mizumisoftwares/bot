from fastapi import FastAPI
import duckdb
import pandas as pd
import numpy as np
import traceback

app = FastAPI()

PARQUETS = [
    "hf://datasets/warmifans/HiTeckGroup@main/part1.parquet",
    "hf://datasets/warmifans/HiTeckGroup@main/part2a.parquet",
    "hf://datasets/warmifans/HiTeckGroup@main/part2b_new.parquet"
]

con = duckdb.connect()

con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")

@app.get("/")
def home():
    return {"status": "API running"}

@app.get("/search")
def search(search: str):
    try:

        query = """
        SELECT DISTINCT *
        FROM read_parquet(?)
        WHERE phoneNumber = ?
           OR LOWER(name) LIKE LOWER(?)
        """

        df = con.execute(
            query,
            [PARQUETS, search, f"%{search}%"]
        ).fetchdf()

        if df is None or df.empty:
            return {
                "found": 0,
                "data": []
            }

        # Remove duplicate rows (same data)
        df = df.drop_duplicates()

        # JSON-safe
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)

        return {
            "found": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception:
        traceback.print_exc()
        return {
            "error": traceback.format_exc()
        }