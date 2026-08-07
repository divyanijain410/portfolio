-- Bank Customer Churn Analysis
-- Data: Bank Customer Churn dataset (10,000 customers)
-- Run against the `customers` table (see load_and_analyze.py for how it's loaded into SQLite;
-- the same queries run unmodified against Snowflake/Postgres/MySQL with this schema).

-- 1. Baseline churn rate
SELECT COUNT(*) AS n, ROUND(100.0 * SUM(Exited) / COUNT(*), 2) AS churn_rate
FROM customers;

-- 2. Churn rate by geography
SELECT Geography, COUNT(*) AS n, ROUND(100.0 * SUM(Exited) / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY Geography
ORDER BY churn_rate DESC;

-- 3. Churn rate by number of products held
SELECT NumOfProducts, COUNT(*) AS n, ROUND(100.0 * SUM(Exited) / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY NumOfProducts
ORDER BY NumOfProducts;

-- 4. Churn rate by activity status
SELECT IsActiveMember, COUNT(*) AS n, ROUND(100.0 * SUM(Exited) / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY IsActiveMember;

-- 5. Churn rate by age band
SELECT
  CASE WHEN Age < 30 THEN '<30' WHEN Age < 45 THEN '30-44' WHEN Age < 60 THEN '45-59' ELSE '60+' END AS age_band,
  COUNT(*) AS n, ROUND(100.0 * SUM(Exited) / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY age_band
ORDER BY churn_rate DESC;

-- 6. Risk segmentation — built from the driver analysis above, not guessed:
--    holding 3+ products is the single strongest signal (83-100% churn),
--    followed by inactive + only 1 product + age 40+.
SELECT
  CASE
    WHEN NumOfProducts >= 3 THEN 'High risk'
    WHEN IsActiveMember = 0 AND NumOfProducts = 1 AND Age >= 40 THEN 'High risk'
    WHEN IsActiveMember = 0 OR NumOfProducts = 1 OR (Age BETWEEN 45 AND 59) THEN 'Medium risk'
    ELSE 'Low risk'
  END AS risk_tier,
  COUNT(*) AS n_customers,
  ROUND(100.0 * SUM(Exited) / COUNT(*), 2) AS actual_churn_rate,
  ROUND(SUM(Balance), 2) AS total_balance
FROM customers
GROUP BY risk_tier
ORDER BY actual_churn_rate DESC;
