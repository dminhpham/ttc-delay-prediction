"""
Append-only experiment log: one row per model fit, including failed or worse runs.

    from src.experiment_log import log_experiment
    log_experiment({"experiment": "training window", "model": "tree", ...})

The CSV only ever grows. If the file exists the row is appended without a header; otherwise the
file is created with the header. Columns follow the M5 plan (C4); missing keys are left empty.
"""

import os
import subprocess
from datetime import datetime

import pandas as pd

LOG_PATH = "results/experiment_log.csv"

COLUMNS = [
    "run_id", "date", "git_commit", "experiment", "model", "params", "train_years", "n_train",
    "train_mae", "val_mae", "mae_ci_low", "mae_ci_high", "val_rmse", "fit_seconds", "observation",
]


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def log_experiment(row: dict, path: str = LOG_PATH) -> dict:
    """Append one row to the log and return it (with run_id, date and git_commit filled in)."""
    unknown = set(row) - set(COLUMNS)
    if unknown:
        raise ValueError(f"unknown log columns: {sorted(unknown)}")

    row = dict(row)
    exists = os.path.exists(path)
    if "run_id" not in row:
        row["run_id"] = (len(pd.read_csv(path)) + 1) if exists else 1
    row.setdefault("date", datetime.now().isoformat(timespec="seconds"))
    row.setdefault("git_commit", _git_commit())

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    pd.DataFrame([row], columns=COLUMNS).to_csv(path, mode="a", header=not exists, index=False)
    return row
