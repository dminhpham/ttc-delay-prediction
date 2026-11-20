"""Error analysis: where does a model go wrong?

One overall MAE hides which incidents are hard. These helpers split the validation rows
into groups ("slices") and compute the error inside each group.
"""

import pandas as pd

# True-delay buckets (minutes). Bins are (left, right]: 0 < delay <= 5, ...
DELAY_BINS = [0, 5, 10, 20, 30, 60, 180]
DELAY_LABELS = ["1-5", "6-10", "11-20", "21-30", "31-60", "61-180"]


def add_delay_bucket(df, true_col="y_true"):
    """Return a copy of df with a 'delay_bucket' column built from the true delay."""
    df = df.copy()
    df["delay_bucket"] = pd.cut(df[true_col], bins=DELAY_BINS, labels=DELAY_LABELS)
    return df


def mae_by_group(df, group_col, true_col="y_true", pred_col="y_pred"):
    """MAE and bias for each value of group_col, worst group first.

    n    = incidents in the group (small groups can't support strong claims)
    mae  = mean |true - pred|, how far off the model is
    bias = mean (pred - true): negative = guesses too low, positive = guesses too high
    """
    df = df.copy()
    df["error"] = df[pred_col] - df[true_col]
    df["abs_error"] = df["error"].abs()

    table = df.groupby(group_col, observed=True).agg(
        n=("abs_error", "size"),
        mae=("abs_error", "mean"),
        bias=("error", "mean"),
    )
    return table.sort_values("mae", ascending=False).reset_index()


if __name__ == "__main__":
    # Toy check, worked out by hand:
    # bus n=2 mae 4 bias -4 (guesses too low), streetcar n=1 mae 4 bias +4 (too high)
    toy = pd.DataFrame(
        {
            "mode": ["bus", "bus", "streetcar"],
            "y_true": [10, 20, 5],
            "y_pred": [8, 14, 9],
        }
    )
    print(mae_by_group(toy, "mode"))
    print(add_delay_bucket(toy)[["y_true", "delay_bucket"]])
