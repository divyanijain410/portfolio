df <- read.csv("data/superstore.csv", stringsAsFactors = FALSE)
cat("Rows:", nrow(df), "\n")

df$ProfitMargin <- df$Profit / df$Sales

df$DiscountTier <- cut(df$Discount,
  breaks = c(-0.01, 0, 0.10, 0.20, 0.30, 1),
  labels = c("0%", "1-10%", "11-20%", "21-30%", "31%+"))

tier_summary <- aggregate(cbind(Sales, Profit) ~ DiscountTier, data = df, sum)
tier_summary$n <- as.vector(table(df$DiscountTier))
tier_summary$avg_margin <- round(100 * tier_summary$Profit / tier_summary$Sales, 2)
cat("\n--- Revenue, profit, and margin by discount tier ---\n")
print(tier_summary)

cat("\n--- ANOVA: does discount tier affect profit margin? ---\n")
fit_aov <- aov(ProfitMargin ~ DiscountTier, data = df)
print(summary(fit_aov))

cat("\n--- Linear regression: Profit ~ Discount + Sales ---\n")
fit_lm <- lm(Profit ~ Discount + Sales, data = df)
print(summary(fit_lm))

cat("\n--- T-test: profit margin at 0% discount vs 21%+ discount ---\n")
g1 <- df$ProfitMargin[df$DiscountTier == "0%"]
g2 <- df$ProfitMargin[df$DiscountTier %in% c("21-30%","31%+")]
print(t.test(g1, g2))

# find approx breakeven discount: bin by 5% discount and find where avg profit crosses 0
df$bin5 <- floor(df$Discount * 20) / 20
breakeven <- aggregate(Profit ~ bin5, data = df, mean)
breakeven <- breakeven[order(breakeven$bin5), ]
cat("\n--- Avg profit per order by 5%-discount bin (breakeven search) ---\n")
print(breakeven)

write.csv(tier_summary, "output/discount_tier_summary.csv", row.names = FALSE)
write.csv(breakeven, "output/breakeven_by_discount_bin.csv", row.names = FALSE)
