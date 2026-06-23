import pandas as pd
import os

DATA_DIR = "data/raw"

print("loading files...\n")

# load each csv and print basic info
for file in sorted(os.listdir(DATA_DIR)):
    if not file.endswith(".csv"):
        continue

    path = os.path.join(DATA_DIR, file)

    try:
        df = pd.read_csv(path)

        print("-" * 50)
        print(file)
        print("shape:", df.shape)
        print("columns:", df.columns.tolist())
        print("\ndtypes:")
        print(df.dtypes)
        print("\nhead:")
        print(df.head())

        missing = df.isnull().sum()
        if missing.any():
            print("\nmissing values:")
            print(missing[missing > 0])
        else:
            print("\nno missing values")

        if df.duplicated().any():
            print(f"note: {df.duplicated().sum()} duplicate rows found")

        print()

    except Exception as e:
        print(f"error reading {file}: {e}")


# explore fund master
print("-" * 50)
print("fund master breakdown\n")

fm = pd.read_csv(os.path.join(DATA_DIR, "01_fund_master.csv"))

print("fund houses:")
print(fm["fund_house"].unique())

print("\ncategories:")
print(fm["category"].unique())

print("\nsub-categories:")
print(fm["sub_category"].unique())

print("\nrisk grades:")
print(fm["risk_category"].value_counts())

print(f"\namfi code range: {fm['amfi_code'].min()} to {fm['amfi_code'].max()}")
print(f"total schemes in master: {len(fm)}")


# check if all amfi codes in fund master exist in nav history
print("\n" + "-" * 50)
print("validating amfi codes...\n")

nav = pd.read_csv(os.path.join(DATA_DIR, "02_nav_history.csv"))

master_codes = set(fm["amfi_code"])
nav_codes = set(nav["amfi_code"])

missing_from_nav = master_codes - nav_codes
extra_in_nav = nav_codes - master_codes

if missing_from_nav:
    print(f"codes in fund_master but missing from nav_history: {missing_from_nav}")
else:
    print("all fund_master codes found in nav_history")

if extra_in_nav:
    print(f"extra codes in nav_history (no master entry): {extra_in_nav}")


# quick data quality check across all files
print("\n" + "-" * 50)
print("data quality summary\n")

all_files = sorted(os.listdir(DATA_DIR))
for fname in all_files:
    if not fname.endswith(".csv"):
        continue
    df = pd.read_csv(os.path.join(DATA_DIR, fname))
    issues = []
    if df.isnull().values.any():
        issues.append(f"missing={df.isnull().sum().sum()}")
    if df.duplicated().any():
        issues.append(f"dupes={df.duplicated().sum()}")
    tag = " | issues: " + ", ".join(issues) if issues else " | ok"
    print(f"  {fname:<40} rows={len(df)}{tag}")

print("\ndone.")