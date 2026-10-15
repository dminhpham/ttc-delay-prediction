# tests/test_evaluate.py — run with: python -m tests.test_evaluate
"""Checks for src/evaluate.py. Plain asserts, so no extra package is needed."""

import math

import numpy as np

from src.evaluate import bootstrap_ci, bootstrap_mae_ci, evaluate, mae, rmse


def test_toy_example_from_plan():
    # Worked by hand: errors 2.73, 14.58, 2.24, 1.92, 4.37
    y = np.array([10, 33, 10, 18, 10])
    pred = np.array([12.73, 18.42, 12.24, 16.08, 14.37])
    assert round(mae(y, pred), 2) == 5.17, mae(y, pred)
    assert round(rmse(y, pred), 2) == 7.04, rmse(y, pred)


def test_perfect_prediction_scores_zero():
    y = np.array([1.0, 7.0, 30.0])
    assert mae(y, y) == 0
    assert rmse(y, y) == 0


def test_median_beats_mean_on_mae_and_mean_beats_median_on_rmse():
    # Why the naive benchmark is the median: it minimises MAE; the mean minimises RMSE.
    y = np.array([5, 8, 10, 10, 12, 90], dtype=float)
    med = np.full(len(y), np.median(y))
    avg = np.full(len(y), y.mean())
    assert mae(y, med) < mae(y, avg)
    assert rmse(y, avg) < rmse(y, med)


def test_bootstrap_same_seed_same_interval():
    rng = np.random.default_rng(0)
    y = rng.exponential(12, size=2000)
    pred = np.full_like(y, 10.0)
    a = bootstrap_mae_ci(y, pred, n_boot=300, seed=42)
    b = bootstrap_mae_ci(y, pred, n_boot=300, seed=42)
    assert a == b
    assert a[0] < mae(y, pred) < a[1]
    assert bootstrap_ci(y, pred, "mae", n_boot=300, seed=42) == a


def test_evaluate_returns_all_columns():
    y = np.arange(1, 101, dtype=float)
    out = evaluate(y, np.full(100, 50.0), n_boot=100)
    assert set(out) == {"n", "mae", "mae_ci_low", "mae_ci_high", "rmse", "rmse_ci_low", "rmse_ci_high"}
    assert out["n"] == 100
    assert math.isclose(out["mae"], 25.0)


def test_rejects_bad_input():
    for y, pred in [([1, 2], [1, 2, 3]), ([1, np.nan], [1, 2])]:
        try:
            mae(y, pred)
        except ValueError:
            continue
        raise AssertionError(f"mae({y}, {pred}) should raise ValueError")

def test_delays_in_range():
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    df = clean_data(config)
    
    # Ensures there are no missing values in min_delay.
    assert df["min_delay"].isna().sum() == 0, "Missing values found in min_delay"
    
    # Checks the lower bound and ensures every row is above the limit.
    assert (df["min_delay"] > config["target"]["lower_min_delay"]).all(), "Some delays are below the lower limit"
    
    # Checks upper bound and ensure no delay exceeds the maximum limit
    assert (df["min_delay"] <= config["target"]["upper_min_delay"]).all(), "Some delays exceed the upper limit"
    
    print("test_delays_in_range passed:", len(df), "rows checked")

if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_") and callable(f)]
    for test in tests:
        test()
        print(f"{test.__name__} passed")
    print(f"{len(tests)} tests passed")
