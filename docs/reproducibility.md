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
