# TTC-delay-prediction
### Group 4 - CSCI 3052U

Predict how long a TTC bus or streetcar delay will last (minutes), at the moment the incident is logged.

**Current result (Milestone 5, validation 2023):** a tuned Decision Tree has MAE 6.64 min, 0.32 min
better than the best baseline (route × hour median, 6.97). Full write-up: `docs/results_draft.md`.

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
Always run from the repo root. Each script loads and cleans the raw data itself, so they can be run
in any order.

| Command | What it does | Time | Writes |
|---|---|---|---|
| `python -m src.data.clean` | Load + clean, print row counts at each step | ~1 min | `data/processed/clean.csv` (809,682 rows, not in git) |
| `python run_baseline.py` | Baselines + Linear Regression (Milestone 3) | ~20 s | `results/baseline_table.csv`, `results/run_log.txt` |
| `python run_experiments.py` | Decision Tree tuning grid, 24 settings (add `--quick` to test on 20% of the training rows) | ~20 min | `results/tuning_tree.csv` |
| `python run_main.py` | Main table: every model, tree with 5 seeds, paired comparisons, Figure 1 | ~4 min | `results/main_table.csv`, `seeds_tree.csv`, `paired_diffs.csv`, `main_mae.png` |
| `python run_training_window.py` | Robustness: tuned tree trained on 2014–22, 2018–22, 2020–22 | ~1 min | `results/training_window.csv` |
| `notebooks/error_analysis.ipynb` | Error analysis: error by group + case studies | ~1 min | `results/error_by_group.csv`, `case_studies.csv`, `error_by_bucket.png` |

Use `python -m` for modules inside `src/` (not `python src/data/clean.py`, which fails with
`No module named 'src'`). The `run_*.py` scripts also add one row per fit to
`results/experiment_log.csv`.

**The test split (2024) is never used by any script.** It is kept for one final evaluation in
Milestone 6. `min_gap` is never a feature (leakage); `location` and `vehicle` are not used.

To use the cleaned data in a notebook without the CSV:
```python
import yaml
from src.data.clean import clean_data

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)
df = clean_data(config)
```

#### Notebooks
Open notebooks from the `notebooks/` folder and run them top to bottom. They add the repo root to
the Python path themselves, so `src` and `config/` are found.

| Notebook | Purpose |
|---|---|
| `raw_data_profile.ipynb` | Raw data profile; why subway is excluded |
| `data_vis.ipynb` | Exploratory plots |
| `expected_results.ipynb` | Numbers behind the pre-registered expectations (training years only) |
| `error_analysis.ipynb` | Where the tuned tree goes wrong (Milestone 5) |

#### Tests
```
python -m tests.test_evaluate
python -m tests.test_filter
python -m tests.test_no_leakage
python -m tests.test_clean_incident
```

#### Settings
`config/config.yaml` holds every threshold, so nothing is hard-coded: the random seed, the target
filter (`0 < min_delay <= 180`), the chronological split (train 2014–2022, validation 2023,
test 2024), the valid route range (1–999) and the tuning grids.

#### Where to find things
| What | Where |
|---|---|
| Results section draft (Milestone 5) | `docs/results_draft.md` |
| Experiment log, every run including failures | `docs/experiment_log.md`, `results/experiment_log.csv` |
| Expected results, written before each model was scored | `docs/expected_results.md` |
| Cleaning steps and row counts | `docs/notes.md`, `docs/cleaning.md` |
| Data card | `docs/data_card.md` |
| How a decision tree chooses a split | `docs/theory_tree_split.md` |
| Reproducibility check | `docs/reproducibility.md` |
| Who did what | `CONTRIBUTIONS.md` |

#### Progress
- **Milestone 2:** load and clean the raw data (`src/data/`); subway profiled and excluded.
- **Milestone 3** (tag `v0.3-baseline`): chronological split, features, baselines and Linear Regression.
- **Milestone 5** (tag `v0.5-experiments`): Decision Tree tuning, main table with paired
  comparisons and seeds, training-window robustness check, error analysis, results section draft.
