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
