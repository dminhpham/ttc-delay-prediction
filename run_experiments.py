"""
Experiment with the tuning grid for the model
2 modes:
        - quick mode will train the model with 20% of the training set and
        - regular mode will train the model with the entire training set

Run from the repo root:
    python run_experiments.py           # full run
    python run_experiments.py --quick   # 20% of training rows, for testing the code
"""

import argparse
import os
import time
from itertools import product

import pandas as pd
import yaml

from src.data.clean import clean_data
from src.data.split import get_split
from src.evaluate import evaluate, mae
from src.features.build import add_time_features
from src.models.tree import make_decision_tree

CONFIG_PATH = "config/config.yaml"
TARGET = "min_delay"


def results_dir(quick):
    """Quick runs go to results/quick/ so they can never overwrite the real results."""
    path = "results/quick" if quick else "results"
    os.makedirs(path, exist_ok=True)
    return path


def load_train_val(config, quick):
    """Training (2014-2022) and validation (2023) rows, with time features added.

    In quick mode only the training rows are sampled, so every score is still measured
    on the same validation rows.
    """
    df = clean_data(config)
    train = add_time_features(get_split(df, config, "training_set"))
    val = add_time_features(get_split(df, config, "validation_set"))

    if quick:
        train = train.sample(
            frac=config["tuning"]["quick_fraction"], random_state=config["seed"]
        )

    return train, val


def fit_and_score(model, X_train, y_train, X_val, y_val, seed):
    """Fit one model and score it the same way every time. Returns one row of a results table."""
    start = time.perf_counter()
    model.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - start

    train_mae = mae(y_train, model.predict(X_train))  # rows it has seen: no interval needed
    val = evaluate(y_val, model.predict(X_val), seed=seed)  # 2023, with 95% bootstrap intervals

    return {
        "n_train": len(y_train),
        "train_mae": train_mae,
        "val_mae": val["mae"],
        "mae_ci_low": val["mae_ci_low"],
        "mae_ci_high": val["mae_ci_high"],
        "val_rmse": val["rmse"],
        "rmse_ci_low": val["rmse_ci_low"],
        "rmse_ci_high": val["rmse_ci_high"],
        "fit_seconds": fit_seconds,
    }


def tune_tree(config, X_train, y_train, X_val, y_val):
    """Fit every max_depth x min_samples_leaf pair in the config grid. Sorted best first."""
    grid = config["tuning"]["decision_tree"]
    rows = []
    for depth, leaf in product(grid["max_depth"], grid["min_samples_leaf"]):
        model = make_decision_tree(config["seed"], max_depth=depth, min_samples_leaf=leaf)
        # "None" as text: pandas would otherwise turn None into NaN in the CSV
        row = {"max_depth": "None" if depth is None else depth, "min_samples_leaf": leaf}
        row.update(fit_and_score(model, X_train, y_train, X_val, y_val, config["seed"]))
        print(
            f"depth={str(depth):>4} leaf={leaf:>3}  train MAE {row['train_mae']:.2f}  "
            f"val MAE {row['val_mae']:.2f}  fit {row['fit_seconds']:.0f}s"
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("val_mae")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quick", action="store_true", help="train on 20%% of the training rows"
    )
    args = parser.parse_args()

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    train, val = load_train_val(config, args.quick)
    # Split inputs (X) from the target (y) after sampling, so they have the same rows.
    # Dropping the target makes it visible that the model cannot see the answer.
    X_train, y_train = train.drop(columns=TARGET), train[TARGET]
    X_val, y_val = val.drop(columns=TARGET), val[TARGET]

    print(f"quick mode: {args.quick}")
    print(f"training rows:   {len(X_train):,} (targets: {len(y_train):,})")
    print(f"validation rows: {len(X_val):,} (targets: {len(y_val):,})")

    out = results_dir(args.quick)
    start = time.perf_counter()
    tree_table = tune_tree(config, X_train, y_train, X_val, y_val)
    tree_table.to_csv(f"{out}/tuning_tree.csv", index=False)
    print(f"\ntree grid: {len(tree_table)} fits in {time.perf_counter() - start:.0f}s")
    print(tree_table.head().to_string(index=False))


if __name__ == "__main__":
    main()
