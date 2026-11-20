# tests/test_evaluate.py — run with: python -m tests.test_evaluate
"""Checks for src/evaluate.py. Plain asserts, so no extra package is needed."""

import math

import numpy as np

import os
import tempfile

import pandas as pd

from src.evaluate import bootstrap_ci, bootstrap_diff_ci, bootstrap_mae_ci, evaluate, mae, rmse
from src.experiment_log import COLUMNS, log_experiment


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



def test_paired_diff_toy_example_from_plan():
    # MAE(A) = (2 + 0 + 5) / 3 = 2.33, MAE(B) = (0 + 5 + 0) / 3 = 1.67, difference 0.67
    y = np.array([10, 20, 30])
    a = np.array([12, 20, 25])
    b = np.array([10, 25, 30])
    diff, low, high = bootstrap_diff_ci(y, a, b, n_boot=500)
    assert round(diff, 2) == 0.67, diff
    assert low <= diff <= high


def test_paired_diff_identical_models_is_exactly_zero():
    y = np.array([5.0, 10.0, 60.0, 8.0])
    p = np.array([10.0, 10.0, 10.0, 10.0])
    assert bootstrap_diff_ci(y, p, p, n_boot=200) == (0.0, 0.0, 0.0)


def test_paired_diff_is_reproducible():
    rng = np.random.default_rng(1)
    y = rng.exponential(12, size=1000)
    a, b = np.full_like(y, 10.0), np.full_like(y, 13.0)
    assert bootstrap_diff_ci(y, a, b, seed=42) == bootstrap_diff_ci(y, a, b, seed=42)


def test_log_appends_and_writes_header_once():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "log.csv")
        log_experiment({"experiment": "toy", "model": "A", "val_mae": 1.0}, path=path)
        log_experiment({"experiment": "toy", "model": "B", "val_mae": 2.0}, path=path)
        df = pd.read_csv(path)
        assert list(df.columns) == COLUMNS
        assert len(df) == 2 and list(df["run_id"]) == [1, 2]
        assert list(df["model"]) == ["A", "B"]


def test_log_rejects_unknown_column():
    with tempfile.TemporaryDirectory() as d:
        try:
            log_experiment({"not_a_column": 1}, path=os.path.join(d, "log.csv"))
        except ValueError:
            return
        raise AssertionError("unknown column should raise ValueError")

if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_") and callable(f)]
    for test in tests:
        test()
        print(f"{test.__name__} passed")
    print(f"{len(tests)} tests passed")
