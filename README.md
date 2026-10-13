# TTC-delay-prediction
### Group 4 - CSCI 3052U

Predict how long a TTC bus or streetcar delay will last (minutes), at the moment the incident is logged.

#### Data
Raw data is included in `data/raw/csv/`: TTC Bus, Streetcar and Subway Delay Data, Jan 2014 – Dec 2024,
from the [City of Toronto Open Data Portal](https://open.toronto.ca/), under the
Open Government Licence – Toronto.

One change from the original download: the July and August 2021 files in the bus folder were copies of
the streetcar data and have been removed (see `docs/notes.md`, Issue 1).

#### Setup
Python 3.13 (tested on 3.13.7, 3.13.16 and 3.14.0). Package versions are pinned in `requirements.txt`.
```
python -m venv .venv
.venv\Scripts\activate        # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

#### Run
Always run from the repo root, with `python -m` (not `python src/data/clean.py`, which fails with
`No module named 'src'`):
```
python -m src.data.load       # load bus + streetcar into one table (850,590 rows after dedupe)
python -m src.data.clean      # clean and save data/processed/clean.csv (809,682 rows)
```
`clean` prints the row count removed at each step. It takes about a minute. The output CSV is not
in git; rerun the command to rebuild it.

To use the cleaned data in a notebook without the CSV:
```python
import yaml
from src.data.clean import clean_data

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)
df = clean_data(config)
```
#### Baselines (one command)
```
python run_baseline.py
```
Runs load → clean → chronological split → features → fits four models on 2014–2022 → scores them on
validation 2023. Takes about 20 seconds and writes:
- `results/baseline_table.csv`: MAE (primary) with a 95% bootstrap interval, RMSE (secondary), and
  the expected MAE from `docs/expected_results.md`
- `results/run_log.txt`: date, git commit, Python and package versions, config, row counts,
  model settings and the number of negative Linear Regression predictions

Models: global median, global mean, route × hour median, and Linear Regression (scikit-learn
defaults, no tuning). `min_gap` is never a feature (leakage); `location` and `vehicle` are deferred.
The test split (2024) is never requested. Reproduction steps and results: `docs/reproducibility.md`.

Tests:
```
python -m tests.test_evaluate
```

Notebooks live in `notebooks/`; if you open one there, change directory to the repo root first
(e.g. `%cd ..`) so `src` and `config/` can be found.

#### Settings
`config/config.yaml` holds every threshold, so nothing is hard-coded: the random seed, the target
filter (`0 < min_delay <= 180`), the chronological split (train 2014–2022, validation 2023,
test 2024) and the valid route range (1–999).

#### Updated Progress
- Load raw data (`src/data/load.py`)
- Clean data: timestamp, direction, route, target filter (`src/data/clean.py`); steps and row counts in `docs/notes.md`
- Subway profiled and excluded (`notebooks/raw_data_profile.ipynb`)
