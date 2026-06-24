"""
clean_scheme_performance.py
===========================
Day 2 -- Data Cleaning: 07_scheme_performance.csv

Steps:
  1. Cast all return/metric columns to float, coerce errors -> NaN + flag
  2. Validate expense_ratio_pct in range 0.1% – 2.5%; flag anomalies
  3. Validate morningstar_rating in 1–5
  4. Validate risk_grade in known enum set
  5. Flag (but retain) rows with anomalies in a new 'anomaly_flags' column
  6. Output to data/processed/scheme_performance_clean.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "07_scheme_performance.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "scheme_performance_clean.csv"

# ── Constants ─────────────────────────────────────────────────────────────────
NUMERIC_COLS = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
    "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
    "aum_crore", "expense_ratio_pct",
]
VALID_RISK_GRADES = {
    "Low", "Low to Moderate", "Moderate", "Moderately High", "High", "Very High"
}
EXPENSE_RATIO_MIN = 0.1
EXPENSE_RATIO_MAX = 2.5


def clean_scheme_performance() -> pd.DataFrame:
    print("=" * 60)
    print("Cleaning: scheme_performance.csv")
    print("=" * 60)

    # ── 1. Load ────────────────────────────────────────────────────────────────
    df = pd.read_csv(RAW_PATH)
    print(f"  Loaded   : {len(df):,} rows | columns: {list(df.columns)}")

    # ── 2. Coerce all numeric columns ─────────────────────────────────────────
    coerce_flags = {}
    for col in NUMERIC_COLS:
        if col in df.columns:
            original = df[col].copy()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            n_coerced = original.notna().sum() - df[col].notna().sum()
            if n_coerced > 0:
                coerce_flags[col] = n_coerced
                print(f"  [!]  '{col}': {n_coerced} non-numeric values coerced to NaN")

    # ── 3. Build anomaly_flags column ─────────────────────────────────────────
    df["anomaly_flags"] = ""

    # Flag rows where key return values are NaN (coercion failures)
    for col in ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]:
        if col in df.columns:
            mask = df[col].isna()
            df.loc[mask, "anomaly_flags"] += f"{col}:null;"

    # ── 4. Validate expense_ratio_pct range ───────────────────────────────────
    if "expense_ratio_pct" in df.columns:
        out_of_range = (
            (df["expense_ratio_pct"] < EXPENSE_RATIO_MIN) |
            (df["expense_ratio_pct"] > EXPENSE_RATIO_MAX)
        )
        n_out = out_of_range.sum()
        if n_out:
            print(f"  [!]  expense_ratio_pct out of [{EXPENSE_RATIO_MIN}, {EXPENSE_RATIO_MAX}]: {n_out} rows -- flagged")
            df.loc[out_of_range, "anomaly_flags"] += "expense_ratio_out_of_range;"

    # ── 5. Validate morningstar_rating 1–5 ────────────────────────────────────
    if "morningstar_rating" in df.columns:
        df["morningstar_rating"] = pd.to_numeric(df["morningstar_rating"], errors="coerce")
        bad_rating = ~df["morningstar_rating"].isin([1, 2, 3, 4, 5])
        n_bad = bad_rating.sum()
        if n_bad:
            print(f"  [!]  morningstar_rating outside 1–5: {n_bad} rows -- flagged")
            df.loc[bad_rating, "anomaly_flags"] += "invalid_morningstar_rating;"

    # ── 6. Validate risk_grade enum ───────────────────────────────────────────
    if "risk_grade" in df.columns:
        invalid_risk = ~df["risk_grade"].isin(VALID_RISK_GRADES)
        n_bad_risk = invalid_risk.sum()
        if n_bad_risk:
            print(f"  [!]  Unrecognised risk_grade: {n_bad_risk} rows -- flagged")
            df.loc[invalid_risk, "anomaly_flags"] += "invalid_risk_grade;"

    # ── 7. Summary of anomalies ───────────────────────────────────────────────
    has_anomaly = df["anomaly_flags"] != ""
    print(f"  Rows with anomalies (flagged, not dropped): {has_anomaly.sum()}")
    print(f"  Anomaly breakdown:\n{df[has_anomaly]['anomaly_flags'].value_counts().to_string()}" if has_anomaly.sum() else "  No anomalies found.")

    # ── 8. Drop exact duplicates ──────────────────────────────────────────────
    dupes = df.duplicated(subset=["amfi_code"]).sum()
    if dupes:
        print(f"  [!]  Duplicate amfi_code rows: {dupes} -- keeping first")
        df = df.drop_duplicates(subset=["amfi_code"])

    # ── 9. Tidy ───────────────────────────────────────────────────────────────
    df["amfi_code"] = df["amfi_code"].astype(int)
    df = df.sort_values("amfi_code").reset_index(drop=True)

    # ── 10. Save ──────────────────────────────────────────────────────────────
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    df.to_csv(OUT_PATH.parent / "07_scheme_performance.csv", index=False)
    print(f"  [OK]  Saved  : {len(df):,} rows -> {OUT_PATH} and 07_scheme_performance.csv")
    print()
    return df


if __name__ == "__main__":
    clean_scheme_performance()
