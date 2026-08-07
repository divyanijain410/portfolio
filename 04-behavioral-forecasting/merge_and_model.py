import pandas as pd, sqlite3, numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

train = pd.read_csv("data/train.csv")
features = pd.read_csv("data/features.csv")
stores = pd.read_csv("data/stores.csv")
print("train:", train.shape, "features:", features.shape, "stores:", stores.shape)

conn = sqlite3.connect("walmart.db")
train.to_sql("sales", conn, if_exists="replace", index=False)
features.to_sql("features", conn, if_exists="replace", index=False)
stores.to_sql("stores", conn, if_exists="replace", index=False)

merge_sql = """
SELECT s.Store, s.Dept, s.Date, s.Weekly_Sales, s.IsHoliday,
       f.Temperature, f.Fuel_Price, f.CPI, f.Unemployment,
       st.Type, st.Size
FROM sales s
JOIN features f ON s.Store = f.Store AND s.Date = f.Date
JOIN stores st ON s.Store = st.Store
"""
df = pd.read_sql(merge_sql, conn)
print("Merged shape:", df.shape)
df = df.dropna(subset=["CPI", "Unemployment", "Weekly_Sales"])
print("After dropping rows with missing CPI/Unemployment:", df.shape)

with open("sql/merge_query.sql", "w") as f:
    f.write(merge_sql.strip() + "\n")

# --- Regression: does CPI / Unemployment predict Weekly_Sales, controlling for store size, temp, fuel, holiday? ---
df["IsHolidayNum"] = df["IsHoliday"].astype(int)
X = df[["CPI", "Unemployment", "Temperature", "Fuel_Price", "IsHolidayNum", "Size"]]
y = df["Weekly_Sales"]
model = LinearRegression().fit(X, y)
r2 = r2_score(y, model.predict(X))
print("\n--- Linear regression: Weekly_Sales ~ CPI + Unemployment + Temperature + Fuel_Price + IsHoliday + Size ---")
for name, coef in zip(X.columns, model.coef_):
    print(f"  {name}: {coef:.4f}")
print(f"  Intercept: {model.intercept_:.2f}")
print(f"  R^2: {r2:.4f}")

# standardized coefficients for fair comparison of driver strength
Xz = (X - X.mean()) / X.std()
model_z = LinearRegression().fit(Xz, y)
print("\n--- Standardized coefficients (comparable magnitude across features) ---")
std_coefs = sorted(zip(X.columns, model_z.coef_), key=lambda t: -abs(t[1]))
for name, coef in std_coefs:
    print(f"  {name}: {coef:.1f}")

# --- Department-level sensitivity to unemployment (a proxy for "category") ---
dept_counts = df.groupby("Dept").size()
valid_depts = dept_counts[dept_counts > 30].index
dept_corr = (
    df[df["Dept"].isin(valid_depts)]
    .groupby("Dept")
    .apply(lambda g: g["Weekly_Sales"].corr(g["Unemployment"]))
    .dropna()
    .sort_values()
)

print("\n--- 5 departments MOST hurt by rising unemployment (most negative correlation) ---")
print(dept_corr.head(5))
print("\n--- 5 departments MOST resilient / counter-cyclical (most positive correlation) ---")
print(dept_corr.tail(5))

dept_corr.to_csv("output/dept_unemployment_sensitivity.csv", header=["corr_with_unemployment"])
pd.DataFrame({"feature": X.columns, "raw_coef": model.coef_, "std_coef": model_z.coef_}).to_csv(
    "output/regression_coefficients.csv", index=False)
print("\nSaved outputs.")
