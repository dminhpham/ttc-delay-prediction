# Milestone 3 Technical Memo: Baseline Reproduction
**Group 4: TTC Delay Duration Prediction**

### 1. Repository
* **URL:** https://github.com/dminhpham/ttc-delay-prediction
* **Release Tag:** `v0.3-baseline`

### 2. Reproducible Environment
* **Software:** Python 3.13.7. Dependencies installed via `pip install -r requirements.txt`.
* **Execution:** A single command (`python run_baseline.py`) runs the entire pipeline end-to-end.
* **Randomness:** Global seed is pinned to `42` inside `config/config.yaml`.
* **Dataset Versioning:** Data was sourced from the City of Toronto Open Data Portal. The exact, immutable dataset version used for this baseline is locked to the specific Git commit hash containing the `data/raw/csv/` directory (decided Oct 12, 2026).

### 3. Data Pipeline
Our automated pipeline standardizes 6 different raw header layouts upon loading, cleans the data, applies a target filter ($0 < \text{delay} \le 180$ minutes) to drop logging artifacts, and performs a strict chronological split to prevent data leakage.

**Row Counts:**
| Stage | Row Count |
|---|---|
| Raw Surface Transit | 852,320 |
| Deduplicated | 850,590 |
| Cleaned & Filtered | 809,682 |

**Chronological Split:**
| Partition | Row Count |
|---|---|
| Training Set (2014–2022) | 683,475 |
| Validation Set (2023) | 62,924 |
| Testing Set (2024) | 63,283 (Strictly held out) |

### 4. Baselines and Features
All data transformations and models were fitted exclusively on the training set to prevent leakage. 

* **Features:** The preprocessor outputs 57 features available at incident-log time (including one-hot encoded incidents/directions, frequency-encoded routes, and sine/cosine cyclical time features). 
* **Leakage Safeguard:** The `min_gap` column was strictly excluded from our features because it is recorded after the incident occurs and represents direct target leakage.
* **Naive Baselines:** 
  * Global Median (Primary naive benchmark)
  * Global Mean (For loss-function comparison)
  * Route $\times$ Hour Median (Grouped heuristic)
* **Course-Level Baseline:**
  * Linear Regression (scikit-learn `Pipeline`, using default settings and completely untuned).

  ### 5. Baseline Table
Evaluated on the 62,924 validation records of 2023. Uncertainty bounds are 95% bootstrap confidence intervals generated across 1,000 resamples (`seed=42`).

| Model | Val MAE (min) | 95% Bootstrap CI | Val RMSE (min) | Expected MAE |
|---|---|---|---|---|
| **Global Median** | 8.28 | [8.14, 8.42] | 18.76 | 7.7 – 8.5 |
| **Global Mean** | 8.55 | [8.42, 8.68] | 17.81 | > Global Median |
| **Route × Hour Median** | **6.97** | [6.83, 7.09] | 17.62 | 0.2 – 0.6 better |
| **Linear Regression** | 7.71 | [7.60, 7.80] | **14.62** | 0.5 better to slightly worse |

### 6. Discrepancy Analysis

| Model | Expected MAE | Actual MAE (95% CI) | Inside range? | Most likely cause |
|---|---|---|---|---|
| **Global Median** | 7.7 – 8.5 | 8.28 [8.14, 8.42] | Yes | The 2023 delay tail grew as expected compared to the in-sample baseline. |
| **Route × Hour Median** | 0.2 – 0.6 better | 6.97 (1.3 better) | No (Better) | Route/time interactions carry much stronger predictive signal than we anticipated. |
| **Linear Regression** | 0.5 better to slightly worse | 7.71 (0.58 better) | Yes (Borderline) | OLS minimizes squared error (RMSE), pulling predictions away from the absolute-error median. |

**Diagnostic Findings:**
1. **Global Median Alignment:** The global median MAE landed at 8.28 minutes, squarely inside our pre-registered expectation. This confirms our hypothesis that 2023 validation data exhibits a heavier delay tail than the 2014-2022 training average, likely due to post-COVID ridership shifts.
2. **Route × Hour Performance:** The Route × Hour median beat the global median by 1.31 minutes, far exceeding our conservative 0.2–0.6 minute expectation. Because the confidence intervals do not overlap, this shows local congestion patterns are highly significant.
3. **Squared-Loss Mismatch:** As anticipated by statistical theory, Linear Regression secured a massive win on RMSE (14.62 min) but struggled on MAE (7.71 min). OLS minimizes squared error, so the algorithm prioritized fitting extreme outliers over improving the typical median error.
4. **Boundary Violations:** Despite producing 9 negative delay predictions on the training data, Linear Regression produced exactly 0 negative predictions on the 2023 validation set.
5. **Reproducibility Verification:** Thanh Thuy’s fresh-clone execution on an independent machine successfully reproduced these exact metrics to the decimal, confirming full pipeline reproducibility.

### 7. Team Retrospective (Start / Stop / Continue) ...