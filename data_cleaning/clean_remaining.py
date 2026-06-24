"""
clean_remaining.py
==================
Day 2 -- Data Cleaning for the remaining 7 CSVs:
  - 01_fund_master.csv
  - 03_aum_by_fund_house.csv
  - 04_monthly_sip_inflows.csv
  - 05_category_inflows.csv
  - 06_industry_folio_count.csv
  - 09_portfolio_holdings.csv
  - 10_benchmark_indices.csv

This completes the deliverable of "10 cleaned CSVs in data/processed/".
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def strip_string_cols(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
    return df

def clean_remaining_files():
    print("=" * 60)
    print("Cleaning remaining raw CSVs...")
    print("=" * 60)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 01_fund_master.csv
    f1_raw = RAW_DIR / "01_fund_master.csv"
    if f1_raw.exists():
        df = pd.read_csv(f1_raw)
        df = strip_string_cols(df)
        df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df.to_csv(PROCESSED_DIR / "01_fund_master.csv", index=False)
        print("  [OK] Processed 01_fund_master.csv")

    # 3. 03_aum_by_fund_house.csv
    f3_raw = RAW_DIR / "03_aum_by_fund_house.csv"
    if f3_raw.exists():
        df = pd.read_csv(f3_raw)
        df = strip_string_cols(df)
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df.to_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv", index=False)
        print("  [OK] Processed 03_aum_by_fund_house.csv")

    # 4. 04_monthly_sip_inflows.csv
    f4_raw = RAW_DIR / "04_monthly_sip_inflows.csv"
    if f4_raw.exists():
        df = pd.read_csv(f4_raw)
        df = strip_string_cols(df)
        # month is YYYY-MM
        df.to_csv(PROCESSED_DIR / "04_monthly_sip_inflows.csv", index=False)
        print("  [OK] Processed 04_monthly_sip_inflows.csv")

    # 5. 05_category_inflows.csv
    f5_raw = RAW_DIR / "05_category_inflows.csv"
    if f5_raw.exists():
        df = pd.read_csv(f5_raw)
        df = strip_string_cols(df)
        df.to_csv(PROCESSED_DIR / "05_category_inflows.csv", index=False)
        print("  [OK] Processed 05_category_inflows.csv")

    # 6. 06_industry_folio_count.csv
    f6_raw = RAW_DIR / "06_industry_folio_count.csv"
    if f6_raw.exists():
        df = pd.read_csv(f6_raw)
        df = strip_string_cols(df)
        df.to_csv(PROCESSED_DIR / "06_industry_folio_count.csv", index=False)
        print("  [OK] Processed 06_industry_folio_count.csv")

    # 9. 09_portfolio_holdings.csv
    f9_raw = RAW_DIR / "09_portfolio_holdings.csv"
    if f9_raw.exists():
        df = pd.read_csv(f9_raw)
        df = strip_string_cols(df)
        df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df.to_csv(PROCESSED_DIR / "09_portfolio_holdings.csv", index=False)
        print("  [OK] Processed 09_portfolio_holdings.csv")

    # 10. 10_benchmark_indices.csv
    f10_raw = RAW_DIR / "10_benchmark_indices.csv"
    if f10_raw.exists():
        df = pd.read_csv(f10_raw)
        df = strip_string_cols(df)
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df.to_csv(PROCESSED_DIR / "10_benchmark_indices.csv", index=False)
        print("  [OK] Processed 10_benchmark_indices.csv")

if __name__ == "__main__":
    clean_remaining_files()
