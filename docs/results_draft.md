# Results (draft)



## Sensitivity, robustness and ablation

All numbers are on the 62,924 validation incidents from 2023. Lower MAE is better. 95% intervals
come from 1,000 bootstrap resamples (seed 42); "paired" intervals use the same resamples for both
models, so they measure the difference directly.

### Sensitivity: how much do the tree's settings matter?

The tuning grid (24 settings, `results/tuning_tree.csv`) shows that leaf size matters far more than
depth:

| max_depth | min_samples_leaf = 1 | min_samples_leaf = 100 |
|---|---|---|
| 4 | 7.33 | 7.33 |
| 8 | 7.32 | 7.30 |
| 12 | 7.30 | 7.11 |
| 16 | 7.65 | 6.89 |
| 20 | 7.91 | 6.72 |
| no limit | 9.10 | **6.64** |

With leaf size 1, validation MAE gets worse as the tree grows deeper (7.30 at depth 12 to 9.10
with no limit), while training MAE falls to 1.11: the tree memorises single incidents. With leaf
size 100, every prediction is the mean of at least 100 past incidents, so a deeper tree keeps
improving and the train–validation gap shrinks from about 8 min to about 1 min (5.58 vs 6.64). The
result is not fragile around the winner: the runner-up (depth 20, leaf 100) scores 6.72, and its
interval (6.62–6.82) overlaps the winner's (6.54–6.74). Leaf sizes 20 and 500 with no depth limit
score 6.85 and 6.89, so too-small and too-large leaves both cost about 0.2 min.

*[Seeds: to add once the tuned tree is refit with random_state ∈ {42, 0, 1, 2, 3} (plan C3).]*

### Robustness: does recent data beat more data? (experiment B)

Delays drifted upward after 2020 (training mean 13.42 min vs 16.78 in 2023), so we tested whether
training only on recent years fits 2023 better. We refit the tuned tree on three windows
(`run_training_window.py`, `results/training_window.csv`):

| Training years | Rows | Validation MAE (95% CI) | Δ MAE vs 2014–22 (paired 95% CI) | Validation RMSE |
|---|---|---|---|---|
| 2014–2022 | 683,475 | **6.64** (6.54–6.75) | — | 14.22 |
| 2018–2022 | 321,959 | 6.70 (6.59–6.79) | +0.05 (+0.02 to +0.08) | 14.16 |
| 2020–2022 | 163,476 | 6.70 (6.59–6.79) | +0.05 (+0.01 to +0.09) | **13.96** |

Using all training years gives the best MAE, but only by about 0.05 min (3 seconds); the paired
intervals exclude 0, so the gap is unlikely to be luck, but it is too small to matter in practice.
On RMSE the most recent window is slightly better (13.96 vs 14.22), consistent with recent years
containing more long delays, like 2023; we did not compute a paired interval for RMSE. Our main
result is therefore robust to the training window, and we keep 2014–2022 because MAE is our
primary metric.

### Ablation A: route encoding (frequency vs one-hot)

### Ablation C: leaf median instead of leaf mean

