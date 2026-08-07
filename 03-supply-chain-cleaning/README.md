# Chaos to clarity: cleaning a 180K-order supply chain dataset

**Tools:** Python (Pandas)
**Data:** [DataCo Smart Supply Chain dataset](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis): 180,519 real order-line records, 53 raw fields covering orders, shipping, customers, and products.

## Business problem
A logistics operation needed to know exactly where shipments were going late, not "shipping is slow" in general, but which specific mode, region, or process step was the actual bottleneck.

## The real cleaning hurdle 
This dataset is deceptively clean on the surface: only one column (`Customer Zipcode`, 0.002% of rows) had any missing values at all, and there were zero duplicate rows. The real obstacles were structural, not statistical:
1. **It isn't UTF-8.** A naive `pd.read_csv()` fails immediately on byte `0xe1`: the file needs `encoding="latin1"`. This is a one-line fix, but it's also exactly the kind of thing that silently breaks a pipeline in production if nobody catches it.
2. **It ships with live-looking PII columns:** `Customer Email`, `Customer Fname`, `Customer Lname`, and even a `Customer Password` column. None of that belongs in an analysis file, so it gets dropped before anything else happens, on principle, not because it was needed for this particular question.
3. **The actual metric doesn't exist yet:** the file has `Days for shipping (real)` and `Days for shipment (scheduled)` as separate columns; the delay everyone actually cares about is the difference, which has to be engineered.

## Method
1. Loaded all 180,519 rows with the correct encoding.
2. Dropped 8 PII / non-analytical columns.
3. Checked for duplicates (none) and nulls (negligible, see above).
4. Parsed both date columns and engineered `shipping_delay_days = Days for shipping (real) − Days for shipment (scheduled)`.
5. Grouped late-delivery rate (the dataset's own `Late_delivery_risk` flag) by shipping mode, region, and market to isolate the actual bottleneck.

## Results (real, computed from all 180,519 rows)

| Shipping Mode | Orders | Late-delivery rate | Avg delay (days) |
|---|---|---|---|
| **First Class** | 27,814 | **95.3%** | +1.00 |
| Second Class | 35,216 | 76.6% | +1.99 |
| Same Day | 9,737 | 45.7% | +0.48 |
| Standard Class | 107,752 | 38.1% | ~0.00 |

Overall late-delivery rate: 54.8%.

**The headline finding:** shipping mode, not geography, is the bottleneck. Late rates by region and market are all clustered tightly in the 54-58% range, a roughly 4-point spread. Late rates by shipping mode span nearly **60 points**, from 38% to 95%. "First Class" (presumably the premium, fastest-promised option) is late almost every single time it's used, far worse than "Standard Class." That's not a shipping-speed problem, it's very likely a promise-setting problem: First Class is probably quoting a delivery window the carrier can't actually hit.

## Recommendation
Don't spend fix-it budget on regional logistics. The region-to-region variance is small. Audit the First Class carrier contract and delivery-window promise first; it's the single biggest lever in the dataset by a wide margin.

## Files
- `clean_and_analyze.py`: the full pipeline, runs end to end on the raw file
- `output/late_rate_by_shipping_mode.csv`, `_by_region.csv`, `_by_market.csv`: the aggregates behind every number above
- `output/cleaned_sample_5000rows.csv`: a 5,000-row cleaned sample (the full cleaned file is ~180K rows; the raw source is too large to commit to a lean repo, so it's linked above instead of checked in)

## Honest next step
`Late_delivery_risk` is the dataset's own label, not independently verified: the natural next step is confirming it's computed consistently (e.g., cross-checking a sample against the raw shipping/scheduled day columns) before this goes anywhere near a stakeholder deck.
