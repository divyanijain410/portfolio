# Reading the market's mood: forecasting demand through economic shifts

**Tools:** SQL (join) · Python (scikit-learn)
**Data:** [Walmart Store Sales Forecasting](https://www.kaggle.com/datasets/abubakkar123/walmart-stores-weekly-sales-forecasting): 421,570 weekly store/department sales records across 45 stores, joined against regional CPI, unemployment, temperature, and fuel price.

## Business problem
Merchandising teams plan inventory months ahead. When inflation or unemployment shifts, does that actually move sales enough to justify reacting to it, and if so, which departments should get the inventory dollars redirected first?

## Method
1. Joined the sales, features, and stores tables in SQL (`sql/merge_query.sql`): 421,570 rows after the join, no rows lost to missing CPI/unemployment.
2. Ran a linear regression of `Weekly_Sales` on CPI, unemployment, temperature, fuel price, holiday flag, and store size, both in raw and standardized form (so the coefficients are comparable to each other despite very different units).
3. Correlated each department's weekly sales against regional unemployment to find which departments are most exposed to a downturn versus which hold up.

## Results (real regression output, see `merge_and_model.py`)

**What actually predicts weekly sales**, standardized coefficients (larger magnitude = stronger driver, holding the others constant):

| Feature | Standardized effect | Direction |
|---|---|---|
| Store size | 5,533 | larger stores sell more (unsurprising, included as a control) |
| CPI | -736 | higher inflation → lower sales |
| Temperature | +538 | warmer weeks → higher sales |
| Unemployment | -494 | higher unemployment → lower sales |
| Holiday week | +358 | holiday weeks sell more |
| Fuel price | -208 | pricier gas → lower sales |

CPI and unemployment are both real, negative, and larger in magnitude than the holiday effect: the economic climate moves the needle more than the calendar does. The full model's R² is a modest 0.061, which is honest and expected: this is 6 economic/operational features with no store or department fixed effects, so it explains the *economic* slice of variance, not total sales variance.

**Department-level exposure** (correlation between weekly sales and regional unemployment, across departments with 30+ weeks of data):

| Most exposed to downturns | Correlation | Most resilient | Correlation |
|---|---|---|---|
| Dept 50 | -0.66 | Dept 34 | +0.15 |
| Dept 87 | -0.28 | Dept 60 | +0.14 |
| Dept 65 | -0.26 | Dept 24 | +0.13 |

## Recommendation
When unemployment is trending up, shift inventory dollars away from Dept 50 (its sales move almost in lockstep with the unemployment rate) and toward Depts 34/60/24, which barely react to it at all.

## Files
- `sql/merge_query.sql`: the join
- `merge_and_model.py`: full pipeline, join, regression, department sensitivity
- `output/regression_coefficients.csv`, `output/dept_unemployment_sensitivity.csv`

## Honest limitation
The public version of this dataset anonymizes department names to numbers: "Dept 50" is real and its sensitivity is real, but this repo can't say whether it's electronics, seasonal goods, or something else. In an actual work setting, the fix is a two-minute lookup against the internal department table.
