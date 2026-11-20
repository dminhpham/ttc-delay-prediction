# Reproducibility check

Goal: anyone can rebuild `results/baseline_table.csv` from a fresh clone by following the README
only, and get the same numbers.

## How to check

```
git clone https://github.com/dminhpham/ttc-delay-prediction.git
cd ttc-delay-prediction
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_baseline.py
git diff --stat results/
```

`results/baseline_table.csv` should be **unchanged** (`git diff` shows nothing for it).
`results/run_log.txt` will differ in the date, git commit, platform and possibly package versions;
that file records the environment, it is not a result. Its row counts must match.

## Runs

| # | Who / where | OS | Python | numpy / pandas / scikit-learn | Result |
|---|---|---|---|---|---|
| 1 | Thanh Thuy, development run (commit `038c59f`) | Linux x86_64 | 3.13.16 | 2.5.3 / 3.0.5 / 1.9.1 | First full run; LR val MAE 7.7059 |
| 2 | Thanh Thuy, fresh clone into a new folder, new venv | Linux x86_64 | 3.13.16 | 2.5.3 / 3.0.5 / 1.9.1 | `baseline_table.csv` and row counts byte-identical to run 1 |
| 3 | Thanh Thuy, own laptop, fresh clone, `pip install -r requirements.txt` | macOS arm64 | 3.14.0 | 2.5.3 / 3.0.6 / 1.9.1 | Medians and row counts identical; Linear Regression differs only in the 4th decimal (val MAE 7.7055 vs 7.7059, RMSE 14.6175 vs 14.6174). Accepted, see note below. **This run produced the committed table** (exact pinned versions) |
| 4 | Minh, own laptop (author of the model code) | _to fill_ | 3.13.7 | _to fill_ | _to fill_ |
| 5 | Selin, fresh clone (`~/m5-check`), new venv (commit `866f1c3`) | macOS 27.2 arm64 | 3.14.0 | 2.5.3 / 3.0.6 / 1.9.1 | `baseline_table.csv` byte-identical to committed table (`git diff` empty); ran in 7.7s |

Run time: about 20 seconds for the whole pipeline (load, clean, fit four models, 1,000 bootstrap
resamples per metric).

## Notes

- Runs 1 and 2 used pandas 3.0.5, one patch version below the pinned 3.0.6, because the package
  index was not reachable from that environment. The results still matched the pinned-environment
  expectations (training-set median MAE 7.17, the same value as `docs/expected_results.md`).
  Run 3 must use the exact pins.
- Everything that could vary is fixed: the split is by year from `config/config.yaml`, the
  bootstrap uses `seed: 42`, Linear Regression and the medians are deterministic, and every
  model is scored on the same bootstrap resamples.
- If a later run does **not** match: record the difference here (which column, how large), then
  check in this order: package versions and row counts in `results/run_log.txt`
  (a different raw file set changes everything), then floating-point
  differences in the last decimal of Linear Regression (CPU / BLAS). A documented mismatch is
  still acceptable; an undocumented one is not.
- Run 3 (macOS, Python 3.14) matched every model exactly except Linear Regression, which differs by at most 0.0004 min in validation MAE and 0.0001 min in RMSE. Its training MAE/RMSE were identical. This is floating-point rounding in the least-squares solve (different OS, CPU and Python version), it is far smaller than the 95% interval (about ±0.1 min), and it does not change any conclusion. The committed `results/baseline_table.csv` comes from run 3, because it used the exact pinned package versions.

---

## Milestone 5 reproduction (experiments and tests)

Goal: rebuild the Milestone 5 experiment tables and pass all unit tests from a fresh clone in a
separate folder (`~/m5-check`), using a clean virtual environment with the exact pinned packages.

### Commands run (commit `866f1c3`)
cd ~
git clone https://github.com/dminhpham/ttc-delay-prediction.git m5-check
cd m5-check
/opt/homebrew/bin/python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m tests.test_no_leakage
python -m tests.test_filter
python -m tests.test_clean_incident
python -m tests.test_evaluate
python run_baseline.py
python run_experiments.py
python run_training_window.py

### Run summary (Selin)

| Item | Result |
|---|---|
| Date & commit | 2026-11-20, `866f1c3` (`main`) |
| Machine / OS | macOS 27.2 (Apple Silicon, arm64) |
| Python & packages | Python 3.14.0; `numpy 2.5.3` / `pandas 3.0.6` / `scikit-learn 1.9.1` (exact `requirements.txt` pins) |
| Unit tests | All 4 test files passed: `test_no_leakage`, `test_filter` (809,682 rows), `test_clean_incident` (4/4), `test_evaluate` (11/11) |
| `run_baseline.py` | **7.7s** — `results/baseline_table.csv` byte-identical (`git diff` empty) |
| `run_experiments.py` | **10m 18.4s** (613s across all 24 Decision Tree fits; `max_depth=None, min_samples_leaf=1` took 368s) — `results/tuning_tree.csv` exact match (`max_numeric_diff = 0.0` on all columns except `fit_seconds`) |
| `run_training_window.py` | **30.6s** — `results/training_window.csv` exact match (`max_numeric_diff = 0.0` on all columns except `fit_seconds`); appended 3 matching rows to `results/experiment_log.csv` as expected |

### Notes and README bugs found

- **Exact numeric match:** Every metric (`train_mae`, `val_mae`, `val_rmse`, 95% bootstrap CIs, and paired bootstrap differences) matched the committed CSVs on GitHub with `0.0` difference. Only `fit_seconds` differed due to hardware (Apple Silicon MacBook Pro M4 Pro chip).
- **Pending `main_table.csv`:** At commit `866f1c3`, `run_experiments.py` generates `results/tuning_tree.csv` only and does not yet write `results/main_table.csv`. If `run_experiments.py` is expanded before tagging, re-run in `~/m5-check` to verify `results/main_table.csv`.
- **README bug 1 (missing M5 run commands):** `README.md` documents `python run_baseline.py`, but omits `python run_experiments.py` (including `--quick` mode) and `python run_training_window.py`.
- **README bug 2 (incomplete test list):** `README.md` only lists `python -m tests.test_evaluate` and omits `tests.test_no_leakage`, `tests.test_filter`, and `tests.test_clean_incident`.
- **README bug 3 (macOS multi-Python venv note):** `README.md` correctly lists Python 3.13 / 3.14.0, but `python -m venv .venv` fails on macOS machines where `python` is unaliased or default `python3` points to `<3.12` (Python 3.11.9 failed on `numpy==2.5.3`, which requires Python >=3.12). Creating the venv explicitly with `python3.14 -m venv .venv` resolved it; `README.md` should note invoking `python3.13` or `python3.14` explicitly.
- **README bug 4 (stale progress list):** The `Updated Progress` section stops at Milestone 3 cleaning and does not reflect Milestone 5 experiments.