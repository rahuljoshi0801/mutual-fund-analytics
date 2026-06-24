"""
clean_nav_history.py
====================
Day 2 — Data Cleaning: 02_nav_history.csv

Steps:
  1. Parse 'date' column to datetime
  2. Sort by amfi_code + date
  3. Forward-fill missing NAV for holidays/weekends (within each fund)
  4. Remove exact duplicates on (amfi_code, date)
  5. Validate nav > 0; drop rows that fail
  6. Output to data/processed/nav_history_clean.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "02_nav_history.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "nav_history_clean.csv"

def clean_nav_history() -> pd.DataFrame:
    print("=" * 60)
    print("Cleaning: nav_history.csv")
    print("=" * 60)

    # ── 1. Load ────────────────────────────────────────────────────────────────
    df = pd.read_csv(RAW_PATH)
    print(f"  Loaded   : {len(df):,} rows | columns: {list(df.columns)}")

    # ── 2. Parse dates ─────────────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = df["date"].isna().sum()
    if bad_dates:
        print(f"  [!] Unparseable dates: {bad_dates} -- dropping")
        df = df.dropna(subset=["date"])

    # ── 3. Sort by amfi_code + date ────────────────────────────────────────────
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # ── 4. Build full calendar per fund and forward-fill NAV ───────────────────
    funds = df["amfi_code"].unique()
    date_min, date_max = df["date"].min(), df["date"].max()
    full_cal = pd.date_range(start=date_min, end=date_max, freq="D")

    filled_frames = []
    for fund in funds:
        fund_df = df[df["amfi_code"] == fund].set_index("date")
        fund_df = fund_df.reindex(full_cal)           # insert missing calendar days
        fund_df["amfi_code"] = fund
        fund_df["nav"] = fund_df["nav"].ffill()       # forward-fill
        fund_df = fund_df.reset_index().rename(columns={"index": "date"})
        filled_frames.append(fund_df)

    df = pd.concat(filled_frames, ignore_index=True)
    print(f"  After ffill (all calendar days): {len(df):,} rows")

    # ── 5. Remove duplicates on (amfi_code, date) ─────────────────────────────
    dupes = df.duplicated(subset=["amfi_code", "date"]).sum()
    if dupes:
        print(f"  [!] Duplicate (amfi_code, date) pairs: {dupes} -- dropping")
        df = df.drop_duplicates(subset=["amfi_code", "date"])

    # ── 6. Validate nav > 0 ───────────────────────────────────────────────────
    invalid_nav = df["nav"] <= 0
    n_invalid = invalid_nav.sum()
    if n_invalid:
        print(f"  [!] Rows with nav <= 0: {n_invalid} -- dropping")
        df = df[~invalid_nav]

    also_null = df["nav"].isna().sum()
    if also_null:
        print(f"  [!] Rows with null nav (unfillable start): {also_null} -- dropping")
        df = df.dropna(subset=["nav"])

    # ── 7. Final sort & dtype tidy ─────────────────────────────────────────────
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["nav"] = df["nav"].round(4)

    # ── 8. Save ───────────────────────────────────────────────────────────────
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    df.to_csv(OUT_PATH.parent / "02_nav_history.csv", index=False)
    print(f"  [OK] Saved  : {len(df):,} rows -> {OUT_PATH} and 02_nav_history.csv")
    print()
    return df


if __name__ == "__main__":
    clean_nav_history()
