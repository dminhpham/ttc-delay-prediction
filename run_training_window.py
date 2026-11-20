"""
Experiment B (robustness): does recent data beat more data?

Fit the tuned Decision Tree (max_depth=None, min_samples_leaf=100, chosen in run_experiments.py)
on three training windows and score each on the SAME 2023 validation rows:

    2014-2022 (all training years) · 2018-2022 · 2020-2022

Run from the repo root:
    python run_training_window.py

Writes results/training_window.csv and appends one row per fit to results/experiment_log.csv.
The test year (2024) is never requested.
"""

import time

import pandas as pd
import yaml

from src.data.clean import clean_data
from src.data.split import get_split
from src.evaluate import bootstrap_diff_ci, evaluate, mae
from src.experiment_log import log_experiment
from src.features.build import add_time_features
from src.models.tree import make_decision_tree

CONFIG_PATH = "config/config.yaml"
TARGET = "min_delay"
TREE_PARAMS = {"max_depth": None, "min_samples_leaf": 100}  # winner of the tuning grid
WINDOWS = [(2014, 2022), (2018, 2022), (2020, 2022)]


def main():
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    seed = config["seed"]

    df = clean_data(config)
    train_all = add_time_features(get_split(df, config, "training_set"))
    val = add_time_features(get_split(df, config, "validation_set"))
    X_val, y_val = val.drop(columns=TARGET), val[TARGET]

    rows, preds = [], {}
    for start, end in WINDOWS:
        train = train_all[train_all["timestamp"].dt.year.between(start, end)]
        X_train, y_train = train.drop(columns=TARGET), train[TARGET]

        model = make_decision_tree(seed, **TREE_PARAMS)
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        fit_seconds = time.perf_counter() - t0

        pred = model.predict(X_val)
        preds[(start, end)] = pred
        scores = evaluate(y_val, pred, seed=seed)
        rows.append({
            "train_years": f"{start}-{end}",
            "n_train": len(y_train),
            "train_mae": mae(y_train, model.predict(X_train)),
            "val_mae": scores["mae"],
            "mae_ci_low": scores["mae_ci_low"],
            "mae_ci_high": scores["mae_ci_high"],
            "val_rmse": scores["rmse"],
            "fit_seconds": fit_seconds,
        })
        print(f"{start}-{end}: n_train {len(y_train):,}  val MAE {scores['mae']:.3f} "
              f"[{scores['mae_ci_low']:.3f}, {scores['mae_ci_high']:.3f}]  RMSE {scores['rmse']:.3f}")

    # Paired difference against the full window: MAE(window) - MAE(2014-2022).
    # Negative = the shorter, more recent window is better.
    base = preds[WINDOWS[0]]
    for row, window in zip(rows, WINDOWS):
        diff, low, high = bootstrap_diff_ci(y_val, preds[window], base, seed=seed)
        row.update({"diff_vs_2014_2022": diff, "diff_ci_low": low, "diff_ci_high": high})

    table = pd.DataFrame(rows)
    table.round(4).to_csv("results/training_window.csv", index=False)

    for row in rows:
        same = row["train_years"] == "2014-2022"
        observation = (
            "reference window (all training years)" if same else
            f"MAE(window) - MAE(2014-2022) = {row['diff_vs_2014_2022']:+.3f} "
            f"[{row['diff_ci_low']:+.3f}, {row['diff_ci_high']:+.3f}] (paired bootstrap)"
        )
        log_experiment({
            "experiment": "B training window",
            "model": "decision tree",
            "params": "max_depth=None, min_samples_leaf=100",
            "train_years": row["train_years"],
            "n_train": row["n_train"],
            "train_mae": round(row["train_mae"], 4),
            "val_mae": round(row["val_mae"], 4),
            "mae_ci_low": round(row["mae_ci_low"], 4),
            "mae_ci_high": round(row["mae_ci_high"], 4),
            "val_rmse": round(row["val_rmse"], 4),
            "fit_seconds": round(row["fit_seconds"], 1),
            "observation": observation,
        })

    print("\n" + table.round(3).to_string(index=False))
    print("\nWrote results/training_window.csv and appended 3 rows to results/experiment_log.csv")


if __name__ == "__main__":
    main()
