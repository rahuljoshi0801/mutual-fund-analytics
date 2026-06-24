# Data Dictionary — Bluestock Mutual Fund Analytics

> **Project**: Capstone Project I — Mutual Fund Analytics  
> **Database**: `bluestock_mf.db` (SQLite)  
> **Schema file**: `sql/schema.sql`  
> **Last updated**: 2026-06-24  

---

## Table of Contents

1. [dim_fund](#1-dim_fund)
2. [dim_date](#2-dim_date)
3. [fact_nav](#3-fact_nav)
4. [fact_transactions](#4-fact_transactions)
5. [fact_performance](#5-fact_performance)
6. [fact_aum](#6-fact_aum)
7. [Source Files & Cleaning Notes](#7-source-files--cleaning-notes)

---

## 1. `dim_fund`

**Description**: Fund master dimension. One row per unique mutual fund scheme identified by its AMFI code.  
**Source**: `data/raw/01_fund_master.csv`  
**Grain**: One row per `amfi_code`

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| `amfi_code` | INTEGER | No — PK | AMFI-assigned unique numeric code for the fund scheme |
| `fund_house` | TEXT | No | Asset Management Company (AMC) name, e.g. `SBI Mutual Fund` |
| `scheme_name` | TEXT | No | Full official scheme name as registered with SEBI |
| `category` | TEXT | Yes | Broad category: `Equity`, `Debt`, `Hybrid`, `Solution Oriented` |
| `sub_category` | TEXT | Yes | Sub-category: `Large Cap`, `Mid Cap`, `Gilt`, `Liquid`, etc. |
| `plan` | TEXT | Yes | `Regular` (distributor) or `Direct` (no commission) |
| `launch_date` | TEXT | Yes | Scheme launch date in `YYYY-MM-DD` format |
| `benchmark` | TEXT | Yes | Benchmark index name, e.g. `NIFTY 100 TRI` |
| `expense_ratio_pct` | REAL | Yes | Annual Total Expense Ratio as a percentage (e.g. `1.54` = 1.54%) |
| `exit_load_pct` | REAL | Yes | Exit load charged on redemption within lock-in period |
| `min_sip_amount` | REAL | Yes | Minimum monthly SIP investment in INR |
| `min_lumpsum_amount` | REAL | Yes | Minimum lumpsum investment in INR |
| `fund_manager` | TEXT | Yes | Name of the primary fund manager |
| `risk_category` | TEXT | Yes | SEBI-mandated risk label: `Low`, `Moderate`, `High`, `Very High` |
| `sebi_category_code` | TEXT | Yes | Internal SEBI scheme classification code (e.g. `EC01`, `DC02`) |

---

## 2. `dim_date`

**Description**: Calendar date dimension. Covers the full date range across all fact tables.  
**Source**: Generated programmatically in `data_cleaning/load_to_sqlite.py`  
**Grain**: One row per calendar day

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| `date_id` | TEXT | No — PK | ISO 8601 date string `YYYY-MM-DD`. Used as FK in all fact tables |
| `full_date` | TEXT | No | Same as `date_id` — stored for readability |
| `year` | INTEGER | No | 4-digit year (e.g. `2024`) |
| `quarter` | INTEGER | No | Quarter of the year: `1`, `2`, `3`, or `4` |
| `month` | INTEGER | No | Month number 1–12 |
| `month_name` | TEXT | No | Full month name, e.g. `January` |
| `week_of_year` | INTEGER | No | ISO week number 1–53 |
| `day_of_week` | INTEGER | No | Day of week: `0` = Monday … `6` = Sunday |
| `day_name` | TEXT | No | Full day name, e.g. `Monday` |
| `is_weekend` | INTEGER | No | `1` if Saturday or Sunday, `0` otherwise |

---

## 3. `fact_nav`

**Description**: Daily Net Asset Value (NAV) for each fund.  
**Source**: `data/processed/nav_history_clean.csv` (cleaned from `data/raw/02_nav_history.csv`)  
**Grain**: One row per `(amfi_code, date)`

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| `nav_id` | INTEGER | No — PK (auto) | Surrogate primary key |
| `amfi_code` | INTEGER | No — FK → `dim_fund` | Fund identifier |
| `date_id` | TEXT | No — FK → `dim_date` | Trading / calendar date |
| `nav` | REAL | No | Net Asset Value in INR per unit. Must be > 0 |

**Cleaning notes**:
- Dates parsed to `datetime64`; sorted by `amfi_code + date`
- Missing NAVs (weekends/holidays) forward-filled within each fund group
- Exact duplicates on `(amfi_code, date)` removed (keep first)
- Rows with `nav <= 0` dropped

---

## 4. `fact_transactions`

**Description**: Individual investor transactions — SIP instalments, lumpsum purchases, and redemptions.  
**Source**: `data/processed/investor_transactions_clean.csv` (cleaned from `data/raw/08_investor_transactions.csv`)  
**Grain**: One row per investor transaction event

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| `txn_id` | INTEGER | No — PK (auto) | Surrogate primary key |
| `investor_id` | TEXT | No | Unique investor identifier, e.g. `INV003054` |
| `amfi_code` | INTEGER | No — FK → `dim_fund` | Fund invested in |
| `date_id` | TEXT | No — FK → `dim_date` | Transaction date |
| `transaction_type` | TEXT | No | Canonical type: `SIP`, `Lumpsum`, or `Redemption` |
| `amount_inr` | REAL | No | Transaction amount in INR. Must be > 0 |
| `state` | TEXT | Yes | Indian state of the investor |
| `city` | TEXT | Yes | Investor's city |
| `city_tier` | TEXT | Yes | City classification: `T30` (top 30) or `B30` (beyond top 30) |
| `age_group` | TEXT | Yes | Age bracket: `18-25`, `26-35`, `36-45`, `46-55`, `56+` |
| `gender` | TEXT | Yes | `Male`, `Female`, or `Other` |
| `annual_income_lakh` | REAL | Yes | Self-declared annual income in lakhs INR |
| `payment_mode` | TEXT | Yes | Payment method: `UPI`, `Mandate`, `Cheque`, `Net Banking` |
| `kyc_status` | TEXT | No | KYC compliance status: `Verified`, `Pending`, or `Rejected` |

**Cleaning notes**:
- `transaction_type` standardised (case-insensitive map) to `SIP | Lumpsum | Redemption`
- Rows with unrecognised `transaction_type` dropped
- `amount_inr <= 0` or null rows dropped
- `kyc_status` standardised to `Verified | Pending | Rejected`; unrecognised values dropped
- Exact duplicate rows removed

---

## 5. `fact_performance`

**Description**: Point-in-time performance and risk metrics snapshot for each fund scheme.  
**Source**: `data/processed/scheme_performance_clean.csv` (cleaned from `data/raw/07_scheme_performance.csv`)  
**Grain**: One row per `amfi_code`

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| `perf_id` | INTEGER | No — PK (auto) | Surrogate primary key |
| `amfi_code` | INTEGER | No — FK → `dim_fund` | Fund identifier |
| `return_1yr_pct` | REAL | Yes | 1-year trailing return as a percentage |
| `return_3yr_pct` | REAL | Yes | 3-year CAGR return as a percentage |
| `return_5yr_pct` | REAL | Yes | 5-year CAGR return as a percentage |
| `benchmark_3yr_pct` | REAL | Yes | Benchmark 3-year CAGR return for alpha comparison |
| `alpha` | REAL | Yes | Jensen's Alpha — excess return over benchmark |
| `beta` | REAL | Yes | Sensitivity of fund returns to market movements |
| `sharpe_ratio` | REAL | Yes | Risk-adjusted return: (return − risk-free rate) / std dev |
| `sortino_ratio` | REAL | Yes | Downside-adjusted Sharpe; penalises only negative volatility |
| `std_dev_ann_pct` | REAL | Yes | Annualised standard deviation of returns (volatility) |
| `max_drawdown_pct` | REAL | Yes | Maximum peak-to-trough decline. Negative values expected |
| `aum_crore` | REAL | Yes | Assets Under Management in crore INR |
| `expense_ratio_pct` | REAL | Yes | Annual expense ratio %. Valid range: 0.1%–2.5% per SEBI |
| `morningstar_rating` | INTEGER | Yes | Morningstar star rating: 1 (worst) to 5 (best) |
| `risk_grade` | TEXT | Yes | Qualitative risk label: `Low`, `Moderate`, `High`, `Very High`, etc. |
| `anomaly_flags` | TEXT | Yes | Semicolon-separated list of data quality flags (empty = clean) |

**Anomaly flag values**:
| Flag | Meaning |
|------|---------|
| `return_1yr_pct:null` | 1-year return could not be parsed |
| `return_3yr_pct:null` | 3-year return could not be parsed |
| `return_5yr_pct:null` | 5-year return could not be parsed |
| `expense_ratio_out_of_range` | Expense ratio outside 0.1%–2.5% SEBI bounds |
| `invalid_morningstar_rating` | Rating not in 1–5 |
| `invalid_risk_grade` | Unrecognised risk grade value |

**Cleaning notes**:
- All numeric columns coerced with `pd.to_numeric(errors='coerce')`
- Anomalous rows **flagged** (not dropped) to preserve all fund records for analysis
- Duplicate `amfi_code` rows: keep first

---

## 6. `fact_aum`

**Description**: Fund house–level AUM snapshots at quarterly / half-yearly intervals.  
**Source**: `data/raw/03_aum_by_fund_house.csv` (no cleaning required — used as-is)  
**Grain**: One row per `(fund_house, date)`

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| `aum_id` | INTEGER | No — PK (auto) | Surrogate primary key |
| `date_id` | TEXT | No — FK → `dim_date` | Snapshot date |
| `fund_house` | TEXT | No | AMC name, e.g. `SBI Mutual Fund` |
| `aum_lakh_crore` | REAL | Yes | AUM in lakh crore INR (rounded, for display) |
| `aum_crore` | REAL | No | AUM in crore INR (precise, for computation) |
| `num_schemes` | INTEGER | Yes | Total number of active schemes offered by the fund house |

---

## 7. Source Files & Cleaning Notes

| Raw File | Cleaned Output | Script | Key Cleaning Steps |
|---|---|---|---|
| `02_nav_history.csv` | `nav_history_clean.csv` | `clean_nav_history.py` | Parse dates, sort, ffill NAV, dedup, validate nav > 0 |
| `08_investor_transactions.csv` | `investor_transactions_clean.csv` | `clean_investor_transactions.py` | Standardise txn_type, validate amount > 0, fix dates, validate KYC enum |
| `07_scheme_performance.csv` | `scheme_performance_clean.csv` | `clean_scheme_performance.py` | Coerce numeric cols, flag expense ratio anomalies, validate enums |
| `01_fund_master.csv` | _(used as-is for dim_fund)_ | `load_to_sqlite.py` | — |
| `03_aum_by_fund_house.csv` | _(used as-is for fact_aum)_ | `load_to_sqlite.py` | — |

### General Conventions
- All dates stored as ISO 8601 strings (`YYYY-MM-DD`) in SQLite
- Monetary amounts in INR (Indian Rupees)
- Percentages stored as raw floats (e.g. `1.54` = 1.54%, not 0.0154)
- `amfi_code` is the universal join key across all tables
