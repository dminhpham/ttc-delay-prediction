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

import yaml

from src.data.clean import clean_data
from src.data.split import get_split
from src.features.build import add_time_features

CONFIG_PATH = "config/config.yaml"


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quick", action="store_true", help="train on 20%% of the training rows"
    )
    args = parser.parse_args()

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    train, val = load_train_val(config, args.quick)
    # Take the targets after sampling, so y_train has the same rows as train
    y_train = train["min_delay"]
    y_val = val["min_delay"]

    print(f"quick mode: {args.quick}")
    print(f"training rows:   {len(train):,} (targets: {len(y_train):,})")
    print(f"validation rows: {len(val):,} (targets: {len(y_val):,})")


if __name__ == "__main__":
    main()
