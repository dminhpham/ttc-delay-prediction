"""
Reproduce the baselines with one command, from the repo root:

    python run_baseline.py

load -> clean -> split (training + validation only) -> add_time_features -> fit on 2014-2022 ->
score on validation 2023.

Writes:
    results/baseline_table.csv  model, val_mae, mae_ci_low, mae_ci_high, val_rmse, expected_mae
    results/run_log.txt         date, git commit, versions, config, row counts, model settings

The test split ("testing_set", 2024) is never requested.
"""

import glob
import platform
import subprocess
from datetime import datetime

import numpy as np
import pandas as pd
import sklearn
import yaml

from src.data.clean import clean_direction, clean_route, filter_target, parse_datetime
from src.data.load import load_data, raw_data_dir
from src.data.split import get_split
from src.evaluate import bootstrap_mae_ci, mae, rmse
from src.features.build import add_time_features
from src.models.baselines import GlobalMean, GlobalMedian, RouteHourMedian
from src.models.linear import make_linear_regression

CONFIG_PATH = "config/config.yaml"
TABLE_PATH = "results/baseline_table.csv"
LOG_PATH = "results/run_log.txt"
N_BOOT = 1000

# Expected validation MAE, copied from docs/expected_results.md (committed Oct 12, before any
# model was scored on 2023). Do not edit these after seeing results.
EXPECTED_MAE = {
    "Global median": "7.7–8.5",
    "Global mean": "worse than the global median",
    "Route x hour median": "0.2–0.6 better than the global median",
    "Linear Regression": "0.5 better than the global median to slightly worse",
}


def count_raw_rows() -> int:
    """Rows in the raw bus + streetcar CSVs, before duplicates are removed."""
    total = 0
    for mode in ["bus", "streetcar"]:
        paths = glob.glob(f"{raw_data_dir}/ttc-{mode}-delay-data-*/*.csv")
        paths += glob.glob(f"{raw_data_dir}/ttc-{mode}-delay-data-20*.csv")
        total += sum(len(pd.read_csv(path, usecols=[0])) for path in paths)
    return total


def clean_with_counts(config):
    """Same steps as src.data.clean.clean_data, recording the row count along the way."""
    counts = {"raw": count_raw_rows()}
    df = load_data()
    counts["deduped"] = len(df)
    df = parse_datetime(df)
    df = clean_direction(df)
    df = clean_route(df, config)
    df = filter_target(df, config)
    counts["cleaned"] = len(df)
    return df, counts


def git(*args) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except Exception:
        return "unknown"


def main():
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    seed = config["seed"]

    # 1. Load and clean, then take the training and validation years only
    df, counts = clean_with_counts(config)
    train = get_split(df, config, "training_set")
    val = get_split(df, config, "validation_set")
    counts["train"] = len(train)
    counts["validation"] = len(val)

    # 2. Time features (row by row, so nothing is learned here)
    train = add_time_features(train)
    val = add_time_features(val)
    y_train = train["min_delay"]
    y_val = val["min_delay"]

    # 3. Fit each model on training rows, score on validation 2023
    models = {
        "Global median": GlobalMedian(),
        "Global mean": GlobalMean(),
        "Route x hour median": RouteHourMedian(),
        "Linear Regression": make_linear_regression(),
    }
    rows = []
    lr_negative = None
    for name, model in models.items():
        model.fit(train, y_train)
        pred = np.asarray(model.predict(val), dtype=float)
        low, high = bootstrap_mae_ci(y_val, pred, n_boot=N_BOOT, seed=seed)
        rows.append(
            {
                "model": name,
                "val_mae": round(mae(y_val, pred), 4),
                "mae_ci_low": round(low, 4),
                "mae_ci_high": round(high, 4),
                "val_rmse": round(rmse(y_val, pred), 4),
                "expected_mae": EXPECTED_MAE[name],
            }
        )
        if name == "Linear Regression":
            lr_negative = int((pred < 0).sum())

    table = pd.DataFrame(rows)
    table.to_csv(TABLE_PATH, index=False)

    # 4. Run log: everything needed to reproduce and describe this run
    log = [
        f"date: {datetime.now().isoformat(timespec='seconds')}",
        "command: python run_baseline.py",
        f"git commit: {git('rev-parse', 'HEAD')}",
        f"raw data version (last commit touching data/raw/csv): {git('log', '-1', '--format=%H', '--', 'data/raw/csv')}",
        f"python: {platform.python_version()} ({platform.platform()})",
        f"numpy {np.__version__}, pandas {pd.__version__}, scikit-learn {sklearn.__version__}, pyyaml {yaml.__version__}",
        "",
        "config:",
        yaml.safe_dump(config, sort_keys=False).rstrip(),
        "",
        "row counts:",
        *[f"  {step}: {n:,}" for step, n in counts.items()],
        "",
        "models:",
        "  Global median / Global mean: training-set constant",
        "  Route x hour median: training-set median per (route, hour), global median for unseen pairs",
        "  Linear Regression: default settings, untuned",
        "  features: incident, direction, mode, day_of_week (one-hot); route frequency (scaled);",
        "            hour_sin, hour_cos, month_sin, month_cos, rush_hour (scaled)",
        "  excluded: min_gap (leakage), location and vehicle (deferred)",
        f"  bootstrap: {N_BOOT} resamples of the validation rows, seed {seed}",
        f"Linear Regression negative predictions on validation: {lr_negative}",
        "",
        "validation 2023:",
        table.to_string(index=False),
    ]
    with open(LOG_PATH, "w") as f:
        f.write("\n".join(log) + "\n")

    print("\nRow counts:", ", ".join(f"{k} {v:,}" for k, v in counts.items()))
    print(f"Linear Regression negative predictions on validation: {lr_negative}")
    print("\nValidation 2023 (MAE in minutes, 95% bootstrap interval):")
    print(table.to_string(index=False))
    print(f"\nWrote {TABLE_PATH} and {LOG_PATH}")


if __name__ == "__main__":
    main()
