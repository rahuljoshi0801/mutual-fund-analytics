"""
clean_investor_transactions.py
==============================
Day 2 -- Data Cleaning: 08_investor_transactions.csv

Steps:
  1. Parse transaction_date to datetime
  2. Standardise transaction_type -> SIP | Lumpsum | Redemption
  3. Validate amount_inr > 0; drop/flag non-positives
  4. Validate kyc_status enum: Verified | Pending | Rejected
  5. Drop exact duplicates
  6. Output to data/processed/investor_transactions_clean.csv
"""

import pandas as pd
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "08_investor_transactions.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "investor_transactions_clean.csv"

# ── Enum definitions ──────────────────────────────────────────────────────────
VALID_TXN_TYPES = {"SIP", "Lumpsum", "Redemption"}
VALID_KYC_STATUS = {"Verified", "Pending", "Rejected"}

# Map common raw variants -> canonical form
TXN_TYPE_MAP = {
    "sip": "SIP",
    "lumpsum": "Lumpsum",
    "lump sum": "Lumpsum",
    "lump_sum": "Lumpsum",
    "redemption": "Redemption",
    "redeem": "Redemption",
    "redmption": "Redemption",
    "redem": "Redemption",
}

KYC_MAP = {
    "verified": "Verified",
    "pending": "Pending",
    "rejected": "Rejected",
    "reject": "Rejected",
    "unverified": "Pending",
}


def clean_investor_transactions() -> pd.DataFrame:
    print("=" * 60)
    print("Cleaning: investor_transactions.csv")
    print("=" * 60)

    # ── 1. Load ────────────────────────────────────────────────────────────────
    df = pd.read_csv(RAW_PATH)
    print(f"  Loaded   : {len(df):,} rows | columns: {list(df.columns)}")

    # ── 2. Parse transaction_date ─────────────────────────────────────────────
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    bad_dates = df["transaction_date"].isna().sum()
    if bad_dates:
        print(f"  [!]  Unparseable transaction_date: {bad_dates} -- dropping")
        df = df.dropna(subset=["transaction_date"])

    # ── 3. Standardise transaction_type ───────────────────────────────────────
    raw_types_before = df["transaction_type"].unique()
    df["transaction_type"] = (
        df["transaction_type"]
        .str.strip()
        .map(lambda x: TXN_TYPE_MAP.get(x.lower(), x) if isinstance(x, str) else x)
    )
    # Ensure casing is canonical for already-correct values
    df["transaction_type"] = df["transaction_type"].apply(
        lambda x: x if x in VALID_TXN_TYPES else (
            TXN_TYPE_MAP.get(str(x).lower(), None) if isinstance(x, str) else None
        )
    )
    invalid_types = df["transaction_type"].isna() | ~df["transaction_type"].isin(VALID_TXN_TYPES)
    n_invalid_types = invalid_types.sum()
    if n_invalid_types:
        print(f"  [!]  Unrecognised transaction_type: {n_invalid_types} -- dropping")
        df = df[~invalid_types]
    print(f"  transaction_type values: {sorted(df['transaction_type'].unique())}")

    # ── 4. Validate amount_inr > 0 ────────────────────────────────────────────
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    bad_amount = (df["amount_inr"].isna()) | (df["amount_inr"] <= 0)
    n_bad_amount = bad_amount.sum()
    if n_bad_amount:
        print(f"  [!]  Rows with amount_inr <= 0 or null: {n_bad_amount} -- dropping")
        df = df[~bad_amount]

    # ── 5. Validate kyc_status enum ───────────────────────────────────────────
    df["kyc_status"] = (
        df["kyc_status"]
        .str.strip()
        .map(lambda x: KYC_MAP.get(x.lower(), x) if isinstance(x, str) else x)
    )
    invalid_kyc = ~df["kyc_status"].isin(VALID_KYC_STATUS)
    n_invalid_kyc = invalid_kyc.sum()
    if n_invalid_kyc:
        print(f"  [!]  Invalid kyc_status values: {n_invalid_kyc} -- dropping")
        df = df[~invalid_kyc]
    print(f"  kyc_status values: {sorted(df['kyc_status'].unique())}")

    # ── 6. Drop exact duplicates ──────────────────────────────────────────────
    dupes = df.duplicated().sum()
    if dupes:
        print(f"  [!]  Exact duplicate rows: {dupes} -- dropping")
        df = df.drop_duplicates()

    # ── 7. Tidy dtypes ────────────────────────────────────────────────────────
    df["amfi_code"] = df["amfi_code"].astype(int)
    df["amount_inr"] = df["amount_inr"].round(2)
    df = df.sort_values(["transaction_date", "investor_id"]).reset_index(drop=True)

    # ── 8. Save ───────────────────────────────────────────────────────────────
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    df.to_csv(OUT_PATH.parent / "08_investor_transactions.csv", index=False)
    print(f"  [OK]  Saved  : {len(df):,} rows -> {OUT_PATH} and 08_investor_transactions.csv")
    print()
    return df


if __name__ == "__main__":
    clean_investor_transactions()
