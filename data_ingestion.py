import pandas as pd
import os

DATA_DIR = "data/raw"

print("Starting data ingestion...")

# ─────────────────────────────────────────────────────────────
# SECTION 1 : Load all 10 CSV datasets — shape, dtypes, head()
# ─────────────────────────────────────────────────────────────
for file in sorted(os.listdir(DATA_DIR)):
    if file.endswith(".csv"):
        file_path = os.path.join(DATA_DIR, file)

        try:
            df = pd.read_csv(file_path)

            print("\n" + "=" * 60)
            print(f"File     : {file}")
            print(f"Shape    : {df.shape}")
            print(f"Columns  : {df.columns.tolist()}")
            print("\nData Types:")
            print(df.dtypes)
            print("\nFirst 5 Rows:")
            print(df.head())
            print("\nMissing Values:")
            missing = df.isnull().sum()
            print(missing[missing > 0] if missing.any() else "  None")

            # Flag anomalies
            anomalies = []
            if df.isnull().values.any():
                anomalies.append(f"  [!] Missing values detected: {df.isnull().sum().sum()} cells")
            if df.duplicated().any():
                anomalies.append(f"  [!] Duplicate rows: {df.duplicated().sum()}")
            if anomalies:
                print("\nAnomalies:")
                for a in anomalies:
                    print(a)
            else:
                print("\nAnomalies : None detected")

        except Exception as e:
            print(f"Error reading {file}: {e}")

# ─────────────────────────────────────────────────────────────
# SECTION 2 : Explore Fund Master
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("FUND MASTER EXPLORATION")
print("=" * 60)

fund_master = pd.read_csv(os.path.join(DATA_DIR, "01_fund_master.csv"))

print(f"\nUnique Fund Houses ({fund_master['fund_house'].nunique()}):")
for fh in sorted(fund_master["fund_house"].unique()):
    print(f"  - {fh}")

print(f"\nUnique Categories ({fund_master['category'].nunique()}):")
for cat in sorted(fund_master["category"].unique()):
    print(f"  - {cat}")

print(f"\nUnique Sub-Categories ({fund_master['sub_category'].nunique()}):")
for sub in sorted(fund_master["sub_category"].unique()):
    print(f"  - {sub}")

print(f"\nUnique Risk Grades ({fund_master['risk_category'].nunique()}):")
for risk in sorted(fund_master["risk_category"].unique()):
    count = len(fund_master[fund_master["risk_category"] == risk])
    print(f"  - {risk}: {count} fund(s)")

print(f"\nAMFI Scheme Code Structure:")
print(f"  Code range : {fund_master['amfi_code'].min()} — {fund_master['amfi_code'].max()}")
print(f"  Total codes: {fund_master['amfi_code'].nunique()}")

# ─────────────────────────────────────────────────────────────
# SECTION 3 : Validate AMFI Codes (fund_master vs nav_history)
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("AMFI CODE VALIDATION")
print("=" * 60)

nav_history = pd.read_csv(os.path.join(DATA_DIR, "02_nav_history.csv"))

master_codes  = set(fund_master["amfi_code"].unique())
history_codes = set(nav_history["amfi_code"].unique())

in_both       = master_codes & history_codes
only_master   = master_codes - history_codes
only_history  = history_codes - master_codes

print(f"\n  Codes in fund_master          : {len(master_codes)}")
print(f"  Codes in nav_history          : {len(history_codes)}")
print(f"  Codes present in BOTH         : {len(in_both)}")
print(f"  In fund_master but NOT history: {len(only_master)}")
print(f"  In history but NOT fund_master: {len(only_history)}")

if only_master:
    print(f"\n  [!] Missing from nav_history: {sorted(only_master)}")
else:
    print("\n  [OK] All fund_master codes found in nav_history")

if only_history:
    print(f"\n  [i] Extra codes in nav_history (no master record): {sorted(only_history)}")

# ─────────────────────────────────────────────────────────────
# SECTION 4 : Data Quality Summary
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("DATA QUALITY SUMMARY")
print("=" * 60)

datasets = {
    "01_fund_master"        : fund_master,
    "02_nav_history"        : nav_history,
}

for fname in sorted(os.listdir(DATA_DIR)):
    if fname.endswith(".csv") and fname not in ["01_fund_master.csv", "02_nav_history.csv"]:
        datasets[fname.replace(".csv", "")] = pd.read_csv(os.path.join(DATA_DIR, fname))

for name, df in datasets.items():
    issues = []
    if df.isnull().values.any():
        issues.append(f"missing={df.isnull().sum().sum()}")
    if df.duplicated().any():
        issues.append(f"duplicates={df.duplicated().sum()}")
    status = "[!] " + ", ".join(issues) if issues else "[OK] Clean"
    print(f"  {name:<35} rows={len(df):<7} {status}")

print("\nData ingestion completed.")