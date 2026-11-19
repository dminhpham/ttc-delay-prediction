# Expected Results (pre-registered)

Written **before** any model is evaluated on the validation year (2023).

## Where the numbers come from

Every number below is computed on the **training split only** (2014–2022, 683,475 rows, after
cleaning and the `0 < min_delay <= 180` filter). We did not look at the 2023 or 2024 targets for
this file. Reproduce every number with `notebooks/expected_results.ipynb` (Run All from a clean kernel).

| Training-set statistic | Value |
|---|---|
| Median `min_delay` | 10.0 min |
| Mean `min_delay` | 13.42 min |
| MAE of "always predict the median" (in-sample) | 7.17 min |
| MAE of "always predict the mean" (in-sample) | 8.01 min |
| RMSE of "always predict the mean" (in-sample) | 15.06 min |
| RMSE of "always predict the median" (in-sample) | 15.45 min |
| Share of delays > 30 min / > 60 min | 4.0% / 1.6% |
| Median: bus / streetcar | 10.0 / 7.0 min |

The median wins on MAE and the mean wins on RMSE. That is what theory predicts: the constant that
minimises absolute error is the median, and the constant that minimises squared error is the mean.

**Trend by year:** the median is 10.0 min in every year from 2014 to 2022, but the mean rises
steadily, from 12.3 (2014) to 15.7 (2022). The typical delay is unchanged, but the long delays are
getting longer. On 2022 rows alone, the global training median has an MAE of 7.7 min, compared
with 7.17 min over all training years.

## Expectations for validation (2023)

| Model | Expected validation MAE | Expected validation RMSE |
|---|---|---|
| Global median (naive) | 7.7 – 8.5 min | 16 – 18 min |
| Route × hour median (naive) | 0.2 – 0.6 min better than the global median | about the same as the global median |
| Linear Regression | close to the global median: anywhere from 0.5 min better to slightly worse | better than both medians |

### Reasoning

1. **Global median, about 7.7–8.5 min.** The in-sample anchor is 7.17, but the tail grows every
   year and 2022 alone already gives 7.7. If the trend continues, 2023 will be at or above the 2022
   value. RMSE is driven by the tail, so we expect it to rise more than MAE does.
2. **Route × hour median is slightly better.** Delays differ by route (bus median 10 vs streetcar
   7) and by time of day, so a grouped median should beat a single number. The gain should be small:
   most of the variation is within a route and hour, not between them. Rare route × hour pairs
   fall back to the global median, which limits the gain.
3. **Linear Regression wins on RMSE but not clearly on MAE.** LR minimises squared error, so it is
   pulled toward the mean (13.4) and the long tail. That helps RMSE and can hurt MAE, because the
   median (10) is closer to most delays. A "win" on RMSE and a tie or loss on MAE would be a loss-function
   mismatch, not a bug. Our features (incident type, route frequency, time) are coarse, so we do
   not expect a large improvement.
4. **Validation is worse than training for every model.** 2023 lies outside the training years,
   and the yearly trend says its tail is heavier. The training years also include 2020–2021
   (COVID), when logged incidents fell by about 40% (71,634 in 2019 vs 41,378 in 2020).

## What would surprise us

- LR beats the global median on MAE by more than 1 min. This would mean the features carry more
  signal than we think, so check for leakage first.
- Validation MAE lower than the in-sample training anchor (7.17).
- The route × hour median doing worse than the global median.

Any of these gets investigated before it is reported.

---

## Decision Tree (Milestone 5), before the tree is trained

**What we already knew when writing this:** the 2023 scores of the M3 baselines
(`results/baseline_table.csv`) and the 2023 delay summary (notebook Section 5). The tree's 2023
score was unknown: no tree had been trained.

**Evidence:** `notebooks/expected_results.ipynb`, Section 6. We held back 2022 as a practice test
inside the training years: learn from 2014–2021, test on 2022. Instead of a real tree we used
"fake trees": group similar incidents and predict the group's mean, which is what a tree leaf does.

### Expectations for validation (2023)

| Model | Expected validation MAE | Expected validation RMSE |
|---|---|---|
| Decision Tree (tuned) | **6.6 – 7.2 min**: about the same as the route × hour median (6.97) | **14.0 – 16.0 min**: clearly better than the route × hour median (17.62), close to Linear Regression (14.62) |

### Reasoning

1. **The fake tree ties our best baseline.** On the 2022 practice test, the best fake trees score
   6.36–6.58 MAE, and the route × hour median scores 6.39.
2. **Two effects cancel out.** Smaller, more specific groups help by about 0.2 min. But a tree
   predicts the group's **mean**, not its median, and that costs 0.15–0.5 min: a few very long
   delays pull the mean up, so it is too high for most normal incidents.
3. **2023 is harder than 2022.** Delays are longer in 2023 (median 10 → 11, mean 15.65 → 16.78),
   and every baseline scored 0.4–0.6 min worse on MAE and about 5% worse on RMSE in 2023.
   Adding that to the fake-tree scores gives 6.76–7.18. A real tree picks its own groups and may do
   a little better than our hand-made ones, so we lowered the bottom of the range to 6.6.
4. **RMSE should improve a lot.** RMSE punishes big misses. Predicting the mean is better for big
   misses, and a tree is built to reduce squared error, like Linear Regression. The fake trees'
   RMSE (13.95–15.10 on 2022, plus 5%) gives 14.6–15.9; a real tree may do slightly better.

### What would surprise us

- **Tree MAE below 6.4**: better than any fake tree, even after the 2023 shift. Check for leakage first.
- **Tree MAE above 7.71** (worse than Linear Regression): suspect a bug or bad settings.
- **Tree RMSE above 17.6** (worse than the route × hour median): this would contradict reason 4.

Any of these gets investigated before it is reported.

---

