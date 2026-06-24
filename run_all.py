"""
run_all.py
==========
Day 2 -- Master Orchestration Script

Runs the full Day 2 pipeline end-to-end:
  1. Clean nav_history.csv
  2. Clean investor_transactions.csv
  3. Clean scheme_performance.csv
  4. Load all cleaned data into bluestock_mf.db (SQLite)
  5. Print summary stats and row count verification
"""

import time
from pathlib import Path

# Ensure data_cleaning/ modules are importable regardless of cwd
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "data_cleaning"))

from clean_nav_history          import clean_nav_history
from clean_investor_transactions import clean_investor_transactions
from clean_scheme_performance   import clean_scheme_performance
from clean_remaining            import clean_remaining_files
from load_to_sqlite             import load_to_sqlite


def print_banner(title: str):
    width = 60
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def main():
    start = time.time()

    print_banner("Bluestock Mutual Fund Analytics -- Day 2 Pipeline")
    print("  Capstone Project I | Data Cleaning + SQLite DB Design")
    print()

    # ── Step 1: Clean NAV History ──────────────────────────────────────────────
    nav_df  = clean_nav_history()

    # ── Step 2: Clean Investor Transactions ───────────────────────────────────
    txn_df  = clean_investor_transactions()

    # ── Step 3: Clean Scheme Performance ──────────────────────────────────────
    perf_df = clean_scheme_performance()

    # ── Step 3.5: Clean Remaining Files ───────────────────────────────────────
    clean_remaining_files()

    # ── Step 4: Load to SQLite ────────────────────────────────────────────────
    load_to_sqlite()

    # ── Step 5: Summary ───────────────────────────────────────────────────────
    elapsed = time.time() - start
    print_banner("Pipeline Complete -- Summary")
    print(f"  {'Dataset':<35} {'Rows':>10}")
    print(f"  {'-'*35} {'-'*10}")
    print(f"  {'nav_history_clean.csv':<35} {len(nav_df):>10,}")
    print(f"  {'investor_transactions_clean.csv':<35} {len(txn_df):>10,}")
    print(f"  {'scheme_performance_clean.csv':<35} {len(perf_df):>10,}")
    print()
    print(f"  Total time elapsed : {elapsed:.1f}s")
    print()
    print("  Deliverables:")
    print("    data/processed/nav_history_clean.csv")
    print("    data/processed/investor_transactions_clean.csv")
    print("    data/processed/scheme_performance_clean.csv")
    print("    bluestock_mf.db")
    print("    sql/schema.sql")
    print("    sql/queries.sql")
    print("    data_dictionary.md")
    print()
    print("  Next: git commit -m 'Day 2: Cleaned data + SQLite DB loaded'")
    print()


if __name__ == "__main__":
    main()
