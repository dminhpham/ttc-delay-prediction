# Test protocol (pre-registered)

Written and merged **before** any model is scored on the test year (2024).

## 1. What gets tested
| Model | Settings (frozen) |
|---|---|
| Global median | none |
| Route × hour median | falls back to global median for unseen pairs |
| Linear Regression | defaults|
| Decision Tree | max_depth=None, min_samples_leaf=100, random_state=42 |

The tree settings are the winner (`results/tuning_tree.csv`).

The leaf-median ablation will run on 2023 before the freeze. If it beats the mean tree,it is added to this table.

## 2. Training data
Refit every model on 2014–2023 (746,399 rows). Score once on 2024 (63,283 rows).

2023 was the validation year: it was used to choose the settings above. Those settings are now
frozen, so 2023 becomes training data. We add it because it is the most recent year and delays
drift upward (mean 16.78 min in 2023 vs 13.42 in 2014–2022). Nothing is chosen using 2024.

## 3. Metrics and uncertainty
Primary MAE, secondary RMSE. 95% bootstrap intervals,
1,000 resamples, seed 42 (`evaluate()`).

## 4. Expected results
| Model | Expected test MAE | Expected test RMSE |
|---|---|---|
| Global median | 8.3 – 8.9 | 18.6 – 19.8 |
| Route × hour median | 7.0 – 7.6 | 17.4 – 18.6 |
| Linear Regression | 7.5 – 8.2 | 14.2 – 15.2 |
| Decision Tree | 6.5 – 7.1 | 13.8 – 14.9 |

### Reasoning
1. No model had been trained on 2023 when it was scored, so the 2023
   scores in `results/main_table.csv` measure one-year-ahead performance. Every range starts from them.
2. The median delay has been 10 min every
   year while the mean rose from 12.3 (2014) to 15.7 (2022) and 16.78 (2023)
   (`docs/expected_results.md`). A median model predicts the same value regardless, so its error
   grows with the tail. The global median went from 7.7 on 2022 to 8.28 on 2023, about +0.6 min in
   one year. If the trend continues, we expect the median models to be worse on 2024 than on 2023. Adding 2023 to training does not help them: the median stays 10.
3. In the training-window
   experiment (`results/training_window.csv`), recent data lowered the tree's RMSE from 14.22 to
   13.96, but did not improve MAE (6.64 vs 6.69). So we allow LR and the tree to score slightly
   better than in 2023, mostly on RMSE, while drift may still make them worse.


### What would surprise us
- Any model clearly **better** on 2024


## 5. 2024 Testing data

No model has been fitted or scored on 2024. The 2024 row count (63,283) is known from the split.

## 6. Observation
We may observe:
- how well the chosen models predict one unseen year (2024), with 95% intervals;
- whether the 2023 ranking of models held on 2024.

