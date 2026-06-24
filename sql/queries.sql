-- =============================================================================
-- queries.sql  —  Bluestock Mutual Fund Analytics
-- 10 Analytical SQL Queries
-- Database: bluestock_mf.db  (SQLite)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Q1. Top 5 Funds by AUM (Assets Under Management)
-- Source: fact_performance + dim_fund
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    p.aum_crore,
    p.expense_ratio_pct,
    p.morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
WHERE p.aum_crore IS NOT NULL
ORDER BY p.aum_crore DESC
LIMIT 5;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q2. Average NAV per Month (across all funds)
-- Source: fact_nav + dim_date
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4)  AS avg_nav,
    ROUND(MIN(n.nav), 4)  AS min_nav,
    ROUND(MAX(n.nav), 4)  AS max_nav,
    COUNT(DISTINCT n.amfi_code) AS num_funds
FROM fact_nav n
JOIN dim_date d ON d.date_id = n.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q3. SIP Year-on-Year Growth
-- Source: fact_transactions + dim_date
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    d.year,
    ROUND(SUM(t.amount_inr), 2)                            AS total_sip_inr,
    COUNT(*)                                               AS sip_count,
    ROUND(
        100.0 * (SUM(t.amount_inr) - LAG(SUM(t.amount_inr)) OVER (ORDER BY d.year))
        / NULLIF(LAG(SUM(t.amount_inr)) OVER (ORDER BY d.year), 0),
        2
    )                                                      AS yoy_growth_pct
FROM fact_transactions t
JOIN dim_date d ON d.date_id = t.date_id
WHERE t.transaction_type = 'SIP'
GROUP BY d.year
ORDER BY d.year;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q4. Transactions by State — Count and Total Amount
-- Source: fact_transactions
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    state,
    COUNT(*)                             AS txn_count,
    ROUND(SUM(amount_inr), 2)            AS total_amount_inr,
    ROUND(AVG(amount_inr), 2)            AS avg_amount_inr,
    COUNT(DISTINCT investor_id)          AS unique_investors
FROM fact_transactions
WHERE state IS NOT NULL
GROUP BY state
ORDER BY total_amount_inr DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q5. Funds with Expense Ratio < 1% — sorted by 3-Year Return
-- Source: fact_performance + dim_fund
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.plan,
    p.expense_ratio_pct,
    p.return_1yr_pct,
    p.return_3yr_pct,
    p.return_5yr_pct,
    p.sharpe_ratio,
    p.morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
WHERE p.expense_ratio_pct < 1.0
  AND p.expense_ratio_pct IS NOT NULL
ORDER BY p.return_3yr_pct DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q6. Monthly Transaction Volume Trend (all types)
-- Source: fact_transactions + dim_date
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    d.year,
    d.month,
    d.month_name,
    t.transaction_type,
    COUNT(*)                         AS txn_count,
    ROUND(SUM(t.amount_inr), 2)      AS total_amount_inr
FROM fact_transactions t
JOIN dim_date d ON d.date_id = t.date_id
GROUP BY d.year, d.month, t.transaction_type
ORDER BY d.year, d.month, t.transaction_type;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q7. Top 10 Investors by Total Invested Amount (SIP + Lumpsum)
-- Source: fact_transactions
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    investor_id,
    COUNT(*)                                                          AS total_txns,
    ROUND(SUM(CASE WHEN transaction_type IN ('SIP','Lumpsum') THEN amount_inr ELSE 0 END), 2)
                                                                      AS total_invested_inr,
    ROUND(SUM(CASE WHEN transaction_type = 'Redemption' THEN amount_inr ELSE 0 END), 2)
                                                                      AS total_redeemed_inr,
    COUNT(DISTINCT amfi_code)                                         AS funds_invested
FROM fact_transactions
GROUP BY investor_id
ORDER BY total_invested_inr DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q8. Category-wise Average Sharpe Ratio and Risk Metrics
-- Source: fact_performance + dim_fund
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    f.category,
    f.sub_category,
    COUNT(*)                              AS num_funds,
    ROUND(AVG(p.sharpe_ratio), 4)         AS avg_sharpe_ratio,
    ROUND(AVG(p.sortino_ratio), 4)        AS avg_sortino_ratio,
    ROUND(AVG(p.beta), 4)                 AS avg_beta,
    ROUND(AVG(p.return_3yr_pct), 2)       AS avg_return_3yr_pct,
    ROUND(AVG(p.std_dev_ann_pct), 4)      AS avg_std_dev,
    ROUND(AVG(p.max_drawdown_pct), 4)     AS avg_max_drawdown
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
GROUP BY f.category, f.sub_category
ORDER BY avg_sharpe_ratio DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q9. KYC Pending Transactions — Total Exposure by State
-- Source: fact_transactions
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    kyc_status,
    state,
    COUNT(*)                              AS txn_count,
    ROUND(SUM(amount_inr), 2)             AS total_exposure_inr,
    COUNT(DISTINCT investor_id)           AS unique_investors
FROM fact_transactions
WHERE kyc_status = 'Pending'
GROUP BY kyc_status, state
ORDER BY total_exposure_inr DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q10. Fund-wise NAV % Change — First NAV vs Latest NAV
-- Source: fact_nav + dim_fund
-- ─────────────────────────────────────────────────────────────────────────────
WITH first_nav AS (
    SELECT
        n.amfi_code,
        n.nav           AS nav_first,
        n.date_id       AS first_date
    FROM fact_nav n
    WHERE n.date_id = (
        SELECT MIN(date_id) FROM fact_nav WHERE amfi_code = n.amfi_code
    )
),
last_nav AS (
    SELECT
        n.amfi_code,
        n.nav           AS nav_last,
        n.date_id       AS last_date
    FROM fact_nav n
    WHERE n.date_id = (
        SELECT MAX(date_id) FROM fact_nav WHERE amfi_code = n.amfi_code
    )
)
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    fn.first_date,
    ln.last_date,
    ROUND(fn.nav_first, 4)                                              AS nav_first,
    ROUND(ln.nav_last, 4)                                               AS nav_last,
    ROUND(100.0 * (ln.nav_last - fn.nav_first) / fn.nav_first, 2)      AS total_return_pct
FROM first_nav fn
JOIN last_nav ln ON ln.amfi_code = fn.amfi_code
JOIN dim_fund f  ON f.amfi_code  = fn.amfi_code
ORDER BY total_return_pct DESC;
