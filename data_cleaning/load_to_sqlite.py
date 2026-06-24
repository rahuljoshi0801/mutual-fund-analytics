"""
load_to_sqlite.py
=================
Day 2 -- Load cleaned CSVs into bluestock_mf.db (SQLite star schema)

Steps:
  1. Run schema.sql to create tables (idempotent -- IF NOT EXISTS)
  2. Build dim_date from the full date range across datasets
  3. Load dim_fund from fund_master
  4. Load fact_nav, fact_transactions, fact_performance, fact_aum
  5. Verify row counts match source cleaned CSVs
  6. Print a summary report
"""

import pandas as pd
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
PROCESSED   = BASE_DIR / "data" / "processed"
RAW         = BASE_DIR / "data" / "raw"
DB_PATH     = BASE_DIR / "bluestock_mf.db"
SCHEMA_SQL  = BASE_DIR / "sql" / "schema.sql"

DB_URL = f"sqlite:///{DB_PATH}"


# ── Helpers ────────────────────────────────────────────────────────────────────
def build_dim_date(date_min: str, date_max: str) -> pd.DataFrame:
    """Generate a complete calendar dimension table."""
    dates = pd.date_range(start=date_min, end=date_max, freq="D")
    df = pd.DataFrame({"full_date": dates})
    df["date_id"]      = df["full_date"].dt.strftime("%Y-%m-%d")
    df["full_date"]    = df["date_id"]
    df["year"]         = dates.year
    df["quarter"]      = dates.quarter
    df["month"]        = dates.month
    df["month_name"]   = dates.month_name()
    df["week_of_year"] = dates.isocalendar().week.astype(int)
    df["day_of_week"]  = dates.dayofweek        # 0=Mon … 6=Sun
    df["day_name"]     = dates.day_name()
    df["is_weekend"]   = (dates.dayofweek >= 5).astype(int)
    return df


def verify(engine, table: str, expected: int):
    """Assert DB row count matches expected; print result."""
    with engine.connect() as conn:
        actual = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    status = "[OK]" if actual == expected else "✗"
    print(f"  {status}  {table:<25} expected={expected:>8,}  actual={actual:>8,}")
    if actual != expected:
        print(f"      [!]  MISMATCH -- difference: {actual - expected:+,}")


# ── Main ──────────────────────────────────────────────────────────────────────
def load_to_sqlite():
    print("=" * 60)
    print("Loading cleaned data -> bluestock_mf.db")
    print("=" * 60)

    # ── 1. Create / reset database and apply schema ────────────────────────────
    engine = create_engine(DB_URL, echo=False)
    schema_sql = SCHEMA_SQL.read_text(encoding="utf-8")
    with engine.connect() as conn:
        for stmt in schema_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("  Schema applied (schema.sql)")

    # ── 2. Load source cleaned CSVs ───────────────────────────────────────────
    nav_df   = pd.read_csv(PROCESSED / "nav_history_clean.csv",           parse_dates=["date"])
    txn_df   = pd.read_csv(PROCESSED / "investor_transactions_clean.csv", parse_dates=["transaction_date"])
    perf_df  = pd.read_csv(PROCESSED / "scheme_performance_clean.csv")
    fund_df  = pd.read_csv(PROCESSED / "01_fund_master.csv",              parse_dates=["launch_date"])
    aum_df   = pd.read_csv(PROCESSED / "03_aum_by_fund_house.csv",        parse_dates=["date"])

    # ── 3. dim_date ───────────────────────────────────────────────────────────
    all_dates = pd.concat([
        nav_df["date"],
        txn_df["transaction_date"],
        aum_df["date"],
    ]).dropna()
    date_min = all_dates.min().strftime("%Y-%m-%d")
    date_max = all_dates.max().strftime("%Y-%m-%d")
    dim_date = build_dim_date(date_min, date_max)
    dim_date.to_sql("dim_date", engine, if_exists="replace", index=False)
    print(f"  dim_date : {len(dim_date):,} rows loaded ({date_min} -> {date_max})")

    # ── 4. dim_fund ───────────────────────────────────────────────────────────
    fund_df["launch_date"] = fund_df["launch_date"].dt.strftime("%Y-%m-%d")
    fund_df.to_sql("dim_fund", engine, if_exists="replace", index=False)
    print(f"  dim_fund : {len(fund_df):,} rows loaded")

    # ── 5. fact_nav ───────────────────────────────────────────────────────────
    nav_df["date_id"] = nav_df["date"].dt.strftime("%Y-%m-%d")
    fact_nav = nav_df[["amfi_code", "date_id", "nav"]].copy()
    fact_nav.to_sql("fact_nav", engine, if_exists="replace", index=False)
    print(f"  fact_nav : {len(fact_nav):,} rows loaded")

    # ── 6. fact_transactions ──────────────────────────────────────────────────
    txn_df["date_id"] = txn_df["transaction_date"].dt.strftime("%Y-%m-%d")
    fact_txn = txn_df.drop(columns=["transaction_date"]).copy()
    fact_txn.to_sql("fact_transactions", engine, if_exists="replace", index=False)
    print(f"  fact_transactions : {len(fact_txn):,} rows loaded")

    # ── 7. fact_performance ───────────────────────────────────────────────────
    perf_df.to_sql("fact_performance", engine, if_exists="replace", index=False)
    print(f"  fact_performance : {len(perf_df):,} rows loaded")

    # ── 8. fact_aum ───────────────────────────────────────────────────────────
    aum_df = aum_df.dropna(subset=["date"])
    aum_df["date_id"] = aum_df["date"].dt.strftime("%Y-%m-%d")
    fact_aum = aum_df.drop(columns=["date"]).copy()
    fact_aum.to_sql("fact_aum", engine, if_exists="replace", index=False)
    print(f"  fact_aum : {len(fact_aum):,} rows loaded")

    # ── 9. Verify row counts ──────────────────────────────────────────────────
    print()
    print("Row Count Verification")
    print("-" * 60)
    verify(engine, "dim_date",         len(dim_date))
    verify(engine, "dim_fund",         len(fund_df))
    verify(engine, "fact_nav",         len(fact_nav))
    verify(engine, "fact_transactions",len(fact_txn))
    verify(engine, "fact_performance", len(perf_df))
    verify(engine, "fact_aum",         len(fact_aum))
    print()
    print(f"  [OK]  Database saved -> {DB_PATH}")
    print()


if __name__ == "__main__":
    load_to_sqlite()
