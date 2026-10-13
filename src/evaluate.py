"""
Evaluation metrics shared by every model in the project.

- MAE (primary) and RMSE (secondary), in minutes.
- A paired bootstrap 95% interval for each metric.

Linear Regression and the median baselines are deterministic, so running them with different
seeds gives the same number. The uncertainty we report comes from the validation sample instead:
we resample the validation rows with replacement, recompute the metric, and take the 2.5th and
97.5th percentiles. Every model is scored on the *same* resamples (same seed), so the intervals
of two models can be compared fairly.
"""

import numpy as np


def mae(y_true, y_pred) -> float:
    """Mean Absolute Error, in minutes."""
    y_true, y_pred = _as_arrays(y_true, y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred) -> float:
    """Root Mean Squared Error, in minutes."""
    y_true, y_pred = _as_arrays(y_true, y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


METRICS = {"mae": mae, "rmse": rmse}


def bootstrap_ci(y_true, y_pred, metric, n_boot=1000, seed=42, alpha=0.05, chunk=50):
    """
    Percentile bootstrap interval for `metric` (a function or "mae"/"rmse").

    Draws `n_boot` resamples of the rows (with replacement) using `seed`, and returns
    (low, high) for the (1 - alpha) interval. Resamples are drawn in chunks so memory stays small.
    """
    if isinstance(metric, str):
        metric = METRICS[metric]
    y_true, y_pred = _as_arrays(y_true, y_pred)
    n = len(y_true)
    if n == 0:
        raise ValueError("cannot bootstrap an empty sample")

    rng = np.random.default_rng(seed)
    scores = np.empty(n_boot)
    done = 0
    while done < n_boot:
        size = min(chunk, n_boot - done)
        idx = rng.integers(0, n, size=(size, n))
        for i in range(size):
            scores[done + i] = metric(y_true[idx[i]], y_pred[idx[i]])
        done += size

    low, high = np.percentile(scores, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(low), float(high)


def bootstrap_mae_ci(y_true, y_pred, n_boot=1000, seed=42):
    """(low, high) of the 95% bootstrap interval for MAE. Pass seed=config["seed"]."""
    return bootstrap_ci(y_true, y_pred, mae, n_boot=n_boot, seed=seed)


def evaluate(y_true, y_pred, n_boot=1000, seed=42) -> dict:
    """MAE and RMSE with 95% bootstrap intervals, plus the number of rows scored."""
    y_true, y_pred = _as_arrays(y_true, y_pred)
    result = {"n": len(y_true)}
    for name, fn in METRICS.items():
        low, high = bootstrap_ci(y_true, y_pred, fn, n_boot=n_boot, seed=seed)
        result[name] = fn(y_true, y_pred)
        result[f"{name}_ci_low"] = low
        result[f"{name}_ci_high"] = high
    return result


def _as_arrays(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_true.shape != y_pred.shape:
        raise ValueError(f"shape mismatch: y_true {y_true.shape} vs y_pred {y_pred.shape}")
    if np.isnan(y_true).any() or np.isnan(y_pred).any():
        raise ValueError("y_true and y_pred must not contain NaN")
    return y_true, y_pred


if __name__ == "__main__":
    # Self-check with a toy example you can do by hand
    y = np.array([10, 33, 10, 18, 10])
    pred = np.array([12.73, 18.42, 12.24, 16.08, 14.37])
    print(f"MAE {mae(y, pred):.2f}  RMSE {rmse(y, pred):.2f}   (expected 5.17 and 7.04)")
    print("MAE 95% interval:", bootstrap_mae_ci(y, pred, n_boot=1000, seed=42))
    print("same seed, same interval:", bootstrap_mae_ci(y, pred, seed=42) == bootstrap_mae_ci(y, pred, seed=42))
