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