### Nov 15 — Untuned Decision Tree (first fit)
**Setup:** `python -m src.models.tree`. `DecisionTreeRegressor(random_state=42)`, no other settings.
Same preprocessor as Linear Regression. Trained on 2014–2022 (683,475 rows). Not scored on 2023 yet.
- **Result:** depth 51, 397,367 leaves, 1.7 training rows per leaf on average. Training took about 15 minutes.
- **Observation:** It looked like that the tree memorised the training data: most leaves predict from one or two past
incidents. Leaves are not exactly 1 row because some incidents have identical features but
different delays, so no split can separate them.
- **Decision:** Do not use the untuned tree. Tune `max_depth` and `min_samples_leaf` to force
larger, more stable leaves. Expect the untuned tree to score worse on 2023 than the tuned range in
`docs/expected_results.md` (6.6–7.2 MAE).

### Nov 15 — Untuned Decision Tree, scored on 2023
**Setup:** Same tree as above, same command. This time I also timed the training and scored
the tree on two sets of rows:
- the **training rows** (2014–2022, 683,475 rows), which the tree has already seen
- the **validation rows** (2023, 62,924 rows), which the tree has never seen

**Result:**

| Rows scored | MAE (min) | RMSE (min) |
|---|---|---|
| Training 2014–2022 | 1.11 | — |
| Validation 2023 | **9.10** (95% CI 8.96–9.24) | **20.39** (95% CI 20.02–20.77) |

For comparison, the M3 baselines on the same 2023 rows:

| Model | MAE (min) | RMSE (min) |
|---|---|---|
| Global median (always guess 10) | 8.28 | 18.76 |
| Linear Regression | 7.71 | 14.62 |
| Route × hour median | 6.97 | 17.62 |
| **Untuned tree** | **9.10** | **20.39** |

Training took about 11 minutes, not the 15, I guessed above. Predicting all of 2023
took 0.1 s.

**What I noticed:**
1. **Huge difference between the two sets of rows.** On rows it has seen, the tree is off by
   about 1 minute **on average**. On new rows it is off by about 9 minutes **on average**.
   (MAE is an average: some 2023 incidents are predicted almost exactly, others are off by
   much more than 9.) That 8-minute difference is what overfitting looks like: the tree is
   good at remembering, not at predicting.
2. **It is worse than just guessing 10 minutes.** The untuned tree loses to every baseline,
   even the simplest one. Its interval (8.96–9.24) does not overlap the global median's
   (8.14–8.42), so this isn't just luck in the resampling.
   I think the reason is that most leaves hold only 1 or 2 past incidents. For a new
   incident, the tree copies the delay of one old incident that looked similar. One
   incident is a noisy guide, so the tree is often far off.
3. **RMSE is the worst too (20.39).** RMSE punishes big misses the most. Copying one old
   incident sometimes gives a very wrong answer (for example, a 90-minute delay copied onto
   a normal 10-minute one), and those big misses push RMSE up.
4. A training error of 1.11 means the model did learn the training
   rows. So I guess, the problem is the settings (no limit on how deep the tree grows), not the code.
   Training MAE is not exactly 0 because some incidents look identical but had different
   delays, and the leaf predicts their average.

**Expected vs what happened:** The entry above expected the untuned tree to do worse than
the tuned range. It did, and by more than I expected: I didn't expect it to also
lose to the simple baselines.

**Decision:** Don't use the untuned tree. Next, tune `max_depth` and `min_samples_leaf`


### Nov 16 — Tuning plan
The untuned tree memorised the training data (training MAE 1.11,
validation MAE 9.10). Before trying other settings, I'm writing down what I will try and how
I will pick the winner.

- **Decision Tree:** `max_depth` 4, 8, 12, 16, 20, no limit × `min_samples_leaf` 1, 20, 100,
  500 = 24 fits. Depth limits how many questions the tree can ask. Leaf size sets the smallest number of past incidents a prediction can be based on. The grid goes from
  "too simple" (depth 4) to "memorising"
- **Ridge:** `alpha` 0.1, 1, 10, 100, 1000 = 5 fits. Alpha is how strongly large
  coefficients are penalised.
- **Random Forest:** 100 trees, `max_depth` 12 or 20 × `min_samples_leaf` 20 or 100, with
  `max_features` fixed at 0.5 = 4 fits.

**How I will pick the winner:** lowest validation MAE on 2023.


### Nov 19 — Tree grid, quick mode (testing the code)
**Setup:** `python run_experiments.py --quick`. All 24 settings from the Nov 16 plan, trained on
20% of the training rows (136,695, sampled with seed 42). Scored on the same 62,924 rows from 2023.
24 fits in 84 s. This run was to check that the code works, not to pick the winner.

**Result (top 3 and worst):**

| max_depth | min_samples_leaf | Training MAE | Validation MAE |
|---|---|---|---|
| no limit | 100 | 6.04 | **6.98** |
| 20 | 100 | 6.07 | 6.98 |
| 16 | 100 | 6.18 | 7.00 |
| no limit | 1 | 0.36 | 9.41 |

**What I noticed:**
1. The top 3 all use leaf 100. Once every guess is based on 100+ past incidents, depth hardly matters.
2. With leaf 1, validation MAE gets worse the deeper the tree goes (7.34 → 9.41). That is overfitting.
3. Bug: `max_depth=None` was saved as an empty value in the CSV. I now save it as the text "None".

**Decision:** The code works. Run the full grid.

### Nov 19 — Tree grid, full training set (total training time is about 19min)
**Setup:** `python run_experiments.py`. Same 24 settings, all 683,475 training rows, same 2023 rows.
24 fits in 1,162 s (about 19 min). Results in `results/tuning_tree.csv`.

**Result:**

| Model | Training MAE | Validation MAE (95% CI) | Validation RMSE |
|---|---|---|---|
| **Tree: no limit, leaf 100 (winner)** | 5.58 | **6.64** (6.54–6.74) | **14.22** |
| Tree: depth 20, leaf 100 (runner-up) | 5.71 | 6.72 (6.62–6.82) | 14.24 |
| Tree: no limit, leaf 1 (= untuned) | 1.11 | 9.10 | 20.39 |
| Route × hour median | — | 6.97 (6.83–7.09) | 17.62 |
| Linear Regression | — | 7.71 (7.60–7.80) | 14.62 |
| Global median | — | 8.28 (8.14–8.42) | 18.76 |

The winner took 34 s to train. The untuned tree took about 11 min.

**What I noticed:**
1. I expected 6.6–7.2. It landed at 6.64, near the bottom of the range.
2. **Best model so far.** It beats route × hour by 0.33 min, and their intervals don't overlap.
3. **Winner vs runner-up:** their intervals overlap, so they are close to a tie. My rule is lowest
   validation MAE, so the winner is no limit / leaf 100.
4. **Less overfitting.** The gap between training and validation MAE went from 8 min
   (1.11 vs 9.10) to 1 min (5.58 vs 6.64). Big leaves stop the tree from copying single incidents.
5. **Same result as before.** No limit / leaf 1 gave 9.10, exactly the untuned run from Nov 15.
   Same code and seed give the same number.

**Decision:** Use the tree with `max_depth=None, min_samples_leaf=100`. 

### Nov 20 — Training window (experiment B, robustness)
**Question:** Does recent data beat more data? Delays drift upward after 2020, so a model trained
only on recent years might fit 2023 better.

**Setup:** `python run_training_window.py`. The tuned tree (`max_depth=None, min_samples_leaf=100`)
trained on three windows, each scored on the same 62,924 rows from 2023. Paired bootstrap
(1,000 resamples, seed 42) for MAE(window) − MAE(2014–2022). Results in
`results/training_window.csv`; one row per fit in `results/experiment_log.csv`.

**Result:**

| Training years | Rows | Training MAE | Validation MAE (95% CI) | Validation RMSE | Δ MAE vs 2014–22 (95% CI) | Fit time |
|---|---|---|---|---|---|---|
| 2014–2022 | 683,475 | 5.58 | **6.64** (6.54–6.75) | 14.22 | — | 16.8 s |
| 2018–2022 | 321,959 | 5.99 | 6.70 (6.59–6.79) | 14.16 | +0.05 (+0.02 to +0.08) | 4.7 s |
| 2020–2022 | 163,476 | 5.74 | 6.70 (6.59–6.79) | **13.96** | +0.05 (+0.01 to +0.09) | 1.7 s |

**What I noticed:**
1. **More data wins on MAE, but only just.** Both shorter windows are about 0.05 min (3 seconds)
   worse. The paired intervals exclude 0, so this is unlikely to be luck, but it is far too small to
   matter to a rider.
2. **Recent data wins slightly on RMSE.** 2020–2022 has the lowest RMSE (13.96 vs 14.22). Recent
   years have more long delays, like 2023, so the tree misses them by less. We did not compute a
   paired interval for RMSE, so this is an observation, not a result.
3. The 2014–2022 row (6.643) is exactly the tuning-grid winner from Nov 19, so the run reproduces.
4. Training on 2020–2022 is about 10× faster for almost the same accuracy.

**Decision:** Keep training on 2014–2022 (best MAE, our primary metric). Report the RMSE trade-off
as a robustness finding in R5.
