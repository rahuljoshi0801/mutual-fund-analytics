-- =============================================================================
-- schema.sql  —  Bluestock Mutual Fund Analytics
-- SQLite Star Schema
-- =============================================================================
-- Tables:
--   dim_fund         — Fund master dimension
--   dim_date         — Date dimension (calendar)
--   fact_nav         — Daily NAV fact table
--   fact_transactions— Investor transaction fact table
--   fact_performance — Fund performance metrics fact table
--   fact_aum         — Fund house AUM fact table
-- =============================================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- DIMENSION: dim_fund
-- Source: 01_fund_master.csv + 07_scheme_performance.csv (enriched)
-- Grain: one row per unique amfi_code (fund scheme)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER     PRIMARY KEY,
    fund_house          TEXT        NOT NULL,
    scheme_name         TEXT        NOT NULL,
    category            TEXT,                   -- e.g. Equity, Debt
    sub_category        TEXT,                   -- e.g. Large Cap, Gilt
    plan                TEXT        CHECK(plan IN ('Regular', 'Direct')),
    launch_date         TEXT,                   -- ISO 8601 date string
    benchmark           TEXT,
    expense_ratio_pct   REAL        CHECK(expense_ratio_pct BETWEEN 0.0 AND 3.0),
    exit_load_pct       REAL,
    min_sip_amount      REAL,
    min_lumpsum_amount  REAL,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

-- -----------------------------------------------------------------------------
-- DIMENSION: dim_date
-- Grain: one row per calendar day
-- Populated programmatically in load_to_sqlite.py
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_id         TEXT    PRIMARY KEY,    -- ISO date 'YYYY-MM-DD'
    full_date       TEXT    NOT NULL,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,       -- 1-4
    month           INTEGER NOT NULL,       -- 1-12
    month_name      TEXT    NOT NULL,       -- e.g. 'January'
    week_of_year    INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,       -- 0=Monday … 6=Sunday
    day_name        TEXT    NOT NULL,       -- e.g. 'Monday'
    is_weekend      INTEGER NOT NULL        -- 0 or 1
);

-- -----------------------------------------------------------------------------
-- FACT: fact_nav
-- Source: nav_history_clean.csv
-- Grain: one row per (amfi_code, date)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    date_id     TEXT    NOT NULL REFERENCES dim_date(date_id),
    nav         REAL    NOT NULL CHECK(nav > 0),
    UNIQUE(amfi_code, date_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi   ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_nav_date   ON fact_nav(date_id);

-- -----------------------------------------------------------------------------
-- FACT: fact_transactions
-- Source: investor_transactions_clean.csv
-- Grain: one row per investor transaction
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT    NOT NULL,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    date_id             TEXT    NOT NULL REFERENCES dim_date(date_id),
    transaction_type    TEXT    NOT NULL CHECK(transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr          REAL    NOT NULL CHECK(amount_inr > 0),
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT    CHECK(gender IN ('Male','Female','Other')),
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT    NOT NULL CHECK(kyc_status IN ('Verified','Pending','Rejected'))
);

CREATE INDEX IF NOT EXISTS idx_fact_txn_amfi   ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_txn_date   ON fact_transactions(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_txn_type   ON fact_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_fact_txn_state  ON fact_transactions(state);

-- -----------------------------------------------------------------------------
-- FACT: fact_performance
-- Source: scheme_performance_clean.csv
-- Grain: one row per amfi_code (point-in-time snapshot)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           REAL,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER CHECK(morningstar_rating BETWEEN 1 AND 5),
    risk_grade          TEXT,
    anomaly_flags       TEXT    DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_fact_perf_amfi  ON fact_performance(amfi_code);

-- -----------------------------------------------------------------------------
-- FACT: fact_aum
-- Source: 03_aum_by_fund_house.csv
-- Grain: one row per (fund_house, date)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id         TEXT    NOT NULL REFERENCES dim_date(date_id),
    fund_house      TEXT    NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       REAL    NOT NULL,
    num_schemes     INTEGER,
    UNIQUE(date_id, fund_house)
);

CREATE INDEX IF NOT EXISTS idx_fact_aum_date       ON fact_aum(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_aum_fundhouse  ON fact_aum(fund_house);
