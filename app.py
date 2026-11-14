from fastapi import FastAPI
import duckdb
import pandas as pd
import numpy as np
import traceback

app = FastAPI()

# 1. Fixed URL: Use /resolve/main/ instead of /tree/ for direct file downloading
PARQUETS = [
    "https://huggingface.co/datasets/sarveshmgkvp/HiTeckNuMinfo-bucket/resolve/main/users_data.parquet"
]

# Initialize global DuckDB connection
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")

@app.get("/")
def home():
    return {"status": "API running"}

@app.get("/search")
def search(search: str):
    try:
        # Convert the Python list of paths to a SQL-compatible list representation.
        # File paths cannot be passed as '?' parameters in DuckDB.
        paths_literal = repr(PARQUETS)

        query = f"""
        SELECT DISTINCT *
        FROM read_parquet({paths_literal})
        WHERE phoneNumber = ?
           OR LOWER(name) LIKE LOWER(?)
        """

        # Only user search inputs are bound using parameters to prevent SQL injection
        df = con.execute(
            query,
            [search, f"%{search}%"]
        ).fetchdf()

        if df is None or df.empty:
            return {
                "found": 0,
                "data": []
            }

        # Remove duplicate rows
        df = df.drop_duplicates()

        # Handle NaN/Inf values for JSON compliance
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
