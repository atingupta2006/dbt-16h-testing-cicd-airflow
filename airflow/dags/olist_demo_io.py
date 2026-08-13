"""Shared paths + CSV helpers for Olist Airflow demo DAGs (no dbt / Snowflake).

Sample CSVs live in AIRFLOW_HOME/sample_data (copied at install).
Work products go under AIRFLOW_HOME/olist_work/.
"""

from __future__ import annotations

import csv
import os
import shutil
from pathlib import Path

REQUIRED_RAW = ("orders.csv", "payments.csv", "customers.csv")


def airflow_home() -> Path:
    return Path(os.environ.get("AIRFLOW_HOME", str(Path.home() / "training" / "airflow_home")))


def sample_dir() -> Path:
    """Prefer install copy, then env, then repo path next to this file."""
    candidates = []
    if os.environ.get("OLIST_SAMPLE_DIR"):
        candidates.append(Path(os.environ["OLIST_SAMPLE_DIR"]))
    candidates.append(airflow_home() / "sample_data")
    # When DAGs run from repo (not copied): .../airflow/dags/this → .../airflow/sample_data
    candidates.append(Path(__file__).resolve().parents[1] / "sample_data")
    for path in candidates:
        if path.is_dir() and (path / "orders.csv").is_file():
            return path
    raise FileNotFoundError(
        "Olist sample_data not found. Copy airflow/sample_data into "
        f"{airflow_home() / 'sample_data'} (see handouts/airflow-install.md)."
    )


def work_dir() -> Path:
    path = airflow_home() / "olist_work"
    path.mkdir(parents=True, exist_ok=True)
    return path


def landing_dir() -> Path:
    path = work_dir() / "landing"
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_sample_to_landing(filename: str) -> Path:
    src = sample_dir() / filename
    if not src.is_file():
        raise FileNotFoundError(f"Missing sample file: {src}")
    dest = landing_dir() / filename
    shutil.copy2(src, dest)
    return dest
