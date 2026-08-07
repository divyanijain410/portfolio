# Priced to convert: what discounting actually does to profit

**Tools:** R (base stats, `aov`, `lm`) · Google Sheets
**Data:** [Sample Superstore dataset](https://github.com/mikemooreviz/superstore): 9,994 real order-line transactions with sales, discount, and profit.

## Business problem
Sales teams love discounting to close deals; finance rarely gets a straight answer on where it stops paying for itself. This project finds the actual discount level where profitability breaks down, using real transaction-level data instead of a gut-feel policy.

**[View the Interactive Google Sheets Dashboard Here](https://docs.google.com/spreadsheets/d/e/2PACX-1vT6pygXEyUocXEbn2gtBHETwGDrn2okfKTvYSn9YD9CRb0tm5z4cjCe2SGE8bvBnI_8TkQYv1spzbwl/pubhtml?gid=0&single=true)** 

## Method
1. Computed profit margin per order and bucketed every transaction into 5 discount tiers (0%, 1-10%, 11-20%, 21-30%, 31%+).
2. Ran a one-way ANOVA testing whether discount tier significantly affects profit margin.
3. Ran a linear regression of `Profit ~ Discount + Sales` to isolate discount's effect from order size.
4. Ran a Welch t-test comparing full-price orders against heavily-discounted (21%+) orders.
5. Swept discount in 5-point bins to find the approximate breakeven point.

## Results (real R output, see `r/pricing_analysis.R`)

| Discount tier | Orders | Blended profit margin |
|---|---|---|
| 0% | 4,798 | **+29.5%** |
| 1-10% | 94 | +16.6% |
| 11-20% | 3,709 | +11.6% |
| 21-30% | 227 | **-10.1%** |
| 31%+ | 1,166 | **-48.2%** |

- **ANOVA:** discount tier has a highly significant effect on margin (F = 5,590, p < 2.2e-16).
- **Regression:** the `Discount` coefficient is -233.91 (p < 2.2e-16) on the dataset's 0-1 discount scale: going from 0% to a 10-point discount is associated with roughly a **$23 drop in profit per order**, controlling for order size. Discount is by far the strongest lever in the model (R² = 0.27 with just two predictors).
- **T-test:** full-price orders average +34.0% margin vs. -78.4% for orders discounted 21%+ (t = 63.7, p < 2.2e-16), not a small effect.
- **Breakeven point:** average profit per order stays positive through the 20-25% discount bin, then turns negative and keeps falling, down to roughly -$310/order by the 50% discount bin.

**Strategic Recommendation:** Discounts up to ~20% look defensible; every tier past that is destroying margin, and the 31%+ tier alone accounts for -$125,007 in aggregate profit on just $259,543 of sales.

**Explore the exact breakeven point visually in the [Interactive Google Sheets Dashboard](https://docs.google.com/spreadsheets/d/e/2PACX-1vT6pygXEyUocXEbn2gtBHETwGDrn2okfKTvYSn9YD9CRb0tm5z4cjCe2SGE8bvBnI_8TkQYv1spzbwl/pubhtml?gid=0&single=true).**

## Files
- `r/pricing_analysis.R`: the full analysis, runs as-is in RStudio
- `output/discount_tier_summary.csv`, `output/breakeven_by_discount_bin.csv`: ready for Sheets
- **Live dashboard:** [Interactive Google Sheets Dashboard](https://docs.google.com/spreadsheets/d/e/2PACX-1vT6pygXEyUocXEbn2gtBHETwGDrn2okfKTvYSn9YD9CRb0tm5z4cjCe2SGE8bvBnI_8TkQYv1spzbwl/pubhtml?gid=0&single=true)

## Honest next step
This is observational, not a true randomized A/B test. Discount level here is a business decision, not an assignment, so some of this correlation could reflect that harder-to-sell products get discounted more, not that discounting causes lower margin. The proposed next step: a randomized price test on a slice of live traffic to confirm causation.
