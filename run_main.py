"""
Main results table: every model, fitted on 2014-2022 and scored on 2023.

Run from the repo root:
    python run_main.py          (about 4 minutes)

Steps:
    1. Fit each model once and score it on 2023 (MAE, RMSE, 95% intervals, fit time).
    2. Refit the tuned tree with 5 seeds to show how much the score changes between runs.
    3. Compare the tree with each other model on the same 2023 rows (paired bootstrap).
    4. Draw the main figure: validation MAE per model with its 95% interval.

Writes:
    results/main_table.csv     one row per model
    results/seeds_tree.csv     one row per seed
    results/paired_diffs.csv   tree vs each other model
    results/main_mae.png       the main figure
and appends one row per fit to results/experiment_log.csv.

The test year (2024) is never requested.
"""

import time

import matplotlib

matplotlib.use("Agg")  # save figures to files without opening a window
import matplotlib.pyplot as plt
import pandas as pd
import yaml

from src.data.clean import clean_data
from src.data.split import get_split
from src.evaluate import bootstrap_diff_ci, evaluate
from src.experiment_log import log_experiment
from src.features.build import add_time_features
from src.models.baselines import GlobalMedian, RouteHourMedian
from src.models.linear import make_linear_regression
from src.models.tree import make_decision_tree

CONFIG_PATH = "config/config.yaml"
TARGET = "min_delay"
TREE_NAME = "Decision Tree (tuned)"


def best_tree_settings():
    """The winning tree settings: the row with the lowest validation MAE in the tuning table."""
    best = pd.read_csv("results/tuning_tree.csv").sort_values("val_mae").iloc[0]
    # "no limit" is saved as the text "None", and read_csv reads it back as NaN
    max_depth = None if pd.isna(best["max_depth"]) else int(best["max_depth"])
    return {"max_depth": max_depth, "min_samples_leaf": int(best["min_samples_leaf"])}


def fit_and_score(model, X_train, y_train, X_val, y_val, seed):
    """Fit one model, predict 2023, and return (predictions, scores)."""
    start = time.perf_counter()
    model.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - start

    pred = model.predict(X_val)
    scores = evaluate(y_val, pred, seed=seed)  # MAE and RMSE with 95% bootstrap intervals
    scores["fit_seconds"] = fit_seconds
    return pred, scores


def main():
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    seed = config["seed"]

    # Training (2014-2022) and validation (2023) rows only
    df = clean_data(config)
    train = add_time_features(get_split(df, config, "training_set"))
    val = add_time_features(get_split(df, config, "validation_set"))
    X_train, y_train = train.drop(columns=TARGET), train[TARGET]
    X_val, y_val = val.drop(columns=TARGET), val[TARGET]

    tree_settings = best_tree_settings()
    print(f"tuned tree settings: {tree_settings}")

    # ---- 1. Every model, fitted once ----
    models = {
        "Global median": GlobalMedian(),
        "Route x hour median": RouteHourMedian(),
        "Linear Regression": make_linear_regression(),
        TREE_NAME: make_decision_tree(seed, **tree_settings),
    }
    predictions = {}
    rows = []
    for name, model in models.items():
        pred, scores = fit_and_score(model, X_train, y_train, X_val, y_val, seed)
        predictions[name] = pred
        rows.append({
            "model": name,
            "val_mae": scores["mae"],
            "mae_ci_low": scores["mae_ci_low"],
            "mae_ci_high": scores["mae_ci_high"],
            "val_rmse": scores["rmse"],
            "rmse_ci_low": scores["rmse_ci_low"],
            "rmse_ci_high": scores["rmse_ci_high"],
            "fit_seconds": scores["fit_seconds"],
        })
        log_experiment({
            "experiment": "main table", "model": name,
            "params": str(tree_settings) if name == TREE_NAME else "default",
            "train_years": "2014-2022", "n_train": len(y_train),
            "val_mae": round(scores["mae"], 4), "mae_ci_low": round(scores["mae_ci_low"], 4),
            "mae_ci_high": round(scores["mae_ci_high"], 4), "val_rmse": round(scores["rmse"], 4),
            "fit_seconds": round(scores["fit_seconds"], 1),
            "observation": "final comparison on validation 2023",
        })
        print(f"{name:<24} val MAE {scores['mae']:.3f}  fit {scores['fit_seconds']:.1f}s")

    # ---- 2. The tree again, with 5 seeds ----
    # The other models give the same answer every time, so only the tree is refitted.
    seed_rows = []
    for s in config["tuning"]["seeds"]:
        _, scores = fit_and_score(make_decision_tree(s, **tree_settings),
                                  X_train, y_train, X_val, y_val, seed)
        seed_rows.append({"seed": s, "val_mae": scores["mae"], "val_rmse": scores["rmse"],
                          "fit_seconds": scores["fit_seconds"]})
        print(f"tree seed {s:>2}: val MAE {scores['mae']:.4f}")
    seeds = pd.DataFrame(seed_rows)
    seeds.to_csv("results/seeds_tree.csv", index=False)

    table = pd.DataFrame(rows)
    is_tree = table["model"] == TREE_NAME
    table.loc[is_tree, "seed_mae_mean"] = seeds["val_mae"].mean()
    table.loc[is_tree, "seed_mae_sd"] = seeds["val_mae"].std()
    table.round(4).to_csv("results/main_table.csv", index=False)

    # ---- 3. Paired comparison: tree vs each other model, on the same rows ----
    # diff = MAE(tree) - MAE(other). Negative = the tree is better.
    # If the interval does not include 0, the difference is unlikely to be luck.
    diff_rows = []
    for name in models:
        if name == TREE_NAME:
            continue
        diff, low, high = bootstrap_diff_ci(y_val, predictions[TREE_NAME], predictions[name], seed=seed)
        diff_rows.append({"comparison": f"tree - {name}", "mae_diff": diff,
                          "diff_ci_low": low, "diff_ci_high": high})
    diffs = pd.DataFrame(diff_rows)
    diffs.round(4).to_csv("results/paired_diffs.csv", index=False)

    # ---- 4. Main figure ----
    fig, ax = plt.subplots(figsize=(7, 4))
    error_below = table["val_mae"] - table["mae_ci_low"]
    error_above = table["mae_ci_high"] - table["val_mae"]
    ax.bar(table["model"], table["val_mae"], yerr=[error_below, error_above], capsize=6)
    ax.set_ylabel("Validation MAE (minutes)")
    ax.set_title("Validation MAE on 2023, with 95% bootstrap intervals")
    ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout()
    fig.savefig("results/main_mae.png", dpi=150)

    print("\n" + table.round(3).to_string(index=False))
    print("\n" + seeds.round(4).to_string(index=False))
    print("\n" + diffs.round(3).to_string(index=False))
    print("\nWrote results/main_table.csv, seeds_tree.csv, paired_diffs.csv, main_mae.png")


if __name__ == "__main__":
    main()
