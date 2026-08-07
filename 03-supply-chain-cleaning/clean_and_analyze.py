import pandas as pd

RAW_PATH = "data/supplychain.csv"

# --- Step 1: load. utf-8 fails on this file (byte 0xe1) - it's latin1. ---
df_raw = pd.read_csv(RAW_PATH, encoding="latin1", low_memory=False)
n_raw, cols_raw = df_raw.shape
print(f"Raw shape: {n_raw:,} rows x {cols_raw} columns")

# --- Step 2: drop PII / not-useful-for-analysis columns ---
pii_cols = ["Customer Email", "Customer Fname", "Customer Lname", "Customer Password",
            "Customer Street", "Product Image", "Product Description", "Order Zipcode"]
df = df_raw.drop(columns=[c for c in pii_cols if c in df_raw.columns])

# --- Step 3: duplicates ---
dupes = df.duplicated().sum()
df = df.drop_duplicates()

# --- Step 4: null audit (top offenders) ---
null_pct = (df.isna().mean() * 100).sort_values(ascending=False)
top_nulls = null_pct[null_pct > 0].head(10)

# --- Step 5: parse dates, standardize ---
df["order date (DateOrders)"] = pd.to_datetime(df["order date (DateOrders)"], errors="coerce")
df["shipping date (DateOrders)"] = pd.to_datetime(df["shipping date (DateOrders)"], errors="coerce")
bad_dates = df["order date (DateOrders)"].isna().sum()

# --- Step 6: engineer the delay metric ---
df["shipping_delay_days"] = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]

n_clean, cols_clean = df.shape

print(f"Duplicates removed: {dupes:,}")
print(f"Clean shape: {n_clean:,} rows x {cols_clean} columns")
print(f"Unparseable order dates: {bad_dates:,}")
print("\nTop null columns (%):")
print(top_nulls)

# --- Step 7: bottleneck analysis ---
print("\n--- Late delivery rate by Shipping Mode ---")
by_mode = df.groupby("Shipping Mode").agg(
    n_orders=("Late_delivery_risk", "size"),
    late_rate_pct=("Late_delivery_risk", lambda x: round(100 * x.mean(), 2)),
    avg_delay_days=("shipping_delay_days", lambda x: round(x.mean(), 2)),
).sort_values("late_rate_pct", ascending=False)
print(by_mode)

print("\n--- Late delivery rate by Order Region (top 10) ---")
by_region = df.groupby("Order Region").agg(
    n_orders=("Late_delivery_risk", "size"),
    late_rate_pct=("Late_delivery_risk", lambda x: round(100 * x.mean(), 2)),
).sort_values("late_rate_pct", ascending=False)
print(by_region.head(10))

print("\n--- Late delivery rate by Market ---")
by_market = df.groupby("Market").agg(
    n_orders=("Late_delivery_risk", "size"),
    late_rate_pct=("Late_delivery_risk", lambda x: round(100 * x.mean(), 2)),
).sort_values("late_rate_pct", ascending=False)
print(by_market)

overall_late_rate = round(100 * df["Late_delivery_risk"].mean(), 2)
print(f"\nOverall late-delivery rate: {overall_late_rate}%")

# save cleaned aggregates for the case study
by_mode.to_csv("output/late_rate_by_shipping_mode.csv")
by_region.to_csv("output/late_rate_by_region.csv")
by_market.to_csv("output/late_rate_by_market.csv")

# save a manageable cleaned sample (full 180k-row clean file is too big for a lean git repo)
df.sample(n=5000, random_state=42).to_csv("output/cleaned_sample_5000rows.csv", index=False)
print("\nSaved aggregates + a 5,000-row cleaned sample to output/")
