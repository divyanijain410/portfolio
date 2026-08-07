import pandas as pd, sqlite3, json

df = pd.read_csv("data/churn.csv")
df = df.drop(columns=["RowNumber", "Surname"])  # drop PII / non-predictive noise

conn = sqlite3.connect("churn.db")
df.to_sql("customers", conn, if_exists="replace", index=False)

def q(sql):
    return pd.read_sql(sql, conn)

overall = q("SELECT COUNT(*) n, ROUND(100.0*SUM(Exited)/COUNT(*),2) churn_rate FROM customers")
by_geo = q("""SELECT Geography, COUNT(*) n, ROUND(100.0*SUM(Exited)/COUNT(*),2) churn_rate
              FROM customers GROUP BY Geography ORDER BY churn_rate DESC""")
by_products = q("""SELECT NumOfProducts, COUNT(*) n, ROUND(100.0*SUM(Exited)/COUNT(*),2) churn_rate
                    FROM customers GROUP BY NumOfProducts ORDER BY NumOfProducts""")
by_active = q("""SELECT IsActiveMember, COUNT(*) n, ROUND(100.0*SUM(Exited)/COUNT(*),2) churn_rate
                  FROM customers GROUP BY IsActiveMember""")
by_age = q("""SELECT CASE WHEN Age<30 THEN '<30' WHEN Age<45 THEN '30-44' WHEN Age<60 THEN '45-59' ELSE '60+' END age_band,
              COUNT(*) n, ROUND(100.0*SUM(Exited)/COUNT(*),2) churn_rate
              FROM customers GROUP BY age_band ORDER BY churn_rate DESC""")

# risk segment, built FROM the actual driver analysis above:
# 3+ products is the single strongest signal (83-100% churn), so it alone = High risk.
# Inactive + only 1 product + age 40+ is the second real pattern = High risk too.
# Everything else with any one flag (inactive OR 1 product OR age 45-59) = Medium.
risk = q("""
SELECT
  CASE
    WHEN NumOfProducts >= 3 THEN 'High risk'
    WHEN IsActiveMember=0 AND NumOfProducts=1 AND Age>=40 THEN 'High risk'
    WHEN IsActiveMember=0 OR NumOfProducts=1 OR (Age BETWEEN 45 AND 59) THEN 'Medium risk'
    ELSE 'Low risk'
  END AS risk_tier,
  COUNT(*) n_customers,
  ROUND(100.0*SUM(Exited)/COUNT(*),2) actual_churn_rate,
  ROUND(SUM(Balance),2) total_balance
FROM customers GROUP BY risk_tier ORDER BY actual_churn_rate DESC
""")

print("OVERALL\n", overall, "\n")
print("BY GEOGRAPHY\n", by_geo, "\n")
print("BY # PRODUCTS\n", by_products, "\n")
print("BY ACTIVE STATUS\n", by_active, "\n")
print("BY AGE BAND\n", by_age, "\n")
print("RISK SEGMENTS\n", risk, "\n")

total_balance = df["Balance"].sum()
high_risk_row = risk[risk.risk_tier=="High risk"].iloc[0]
pct_of_base = round(100*high_risk_row.n_customers/len(df),1)
pct_of_balance = round(100*high_risk_row.total_balance/total_balance,1)
print(f"High risk tier = {pct_of_base}% of customers, holding {pct_of_balance}% of total balance,"
      f" with an actual churn rate of {high_risk_row.actual_churn_rate}% vs {overall.churn_rate[0]}% baseline")

# export a clean, Tableau-ready CSV with the risk tier attached
df["risk_tier"] = pd.read_sql("""
SELECT CASE
    WHEN NumOfProducts >= 3 THEN 'High risk'
    WHEN IsActiveMember=0 AND NumOfProducts=1 AND Age>=40 THEN 'High risk'
    WHEN IsActiveMember=0 OR NumOfProducts=1 OR (Age BETWEEN 45 AND 59) THEN 'Medium risk'
    ELSE 'Low risk'
  END AS risk_tier
FROM customers""", conn)["risk_tier"]
df.to_csv("tableau/churn_customers_with_risk_tier.csv", index=False)
print("\nExported tableau/churn_customers_with_risk_tier.csv:", df.shape)
