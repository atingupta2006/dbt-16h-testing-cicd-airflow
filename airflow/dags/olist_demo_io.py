"""Shared helpers for Olist demo DAGs (CSV paths only — no dbt / Snowflake).

Where files live
  sample_data/  input CSVs (copied at install into AIRFLOW_HOME)
  olist_work/   outputs written by the demo DAGs
"""

from __future__ import annotations

import csv
import os
import shutil
from pathlib import Path

# Files every basics DAG expects under sample_data/
REQUIRED_RAW = ("orders.csv", "payments.csv", "customers.csv")


def airflow_home() -> Path:
    """Airflow home folder (env AIRFLOW_HOME, or the class default)."""
    return Path(os.environ.get("AIRFLOW_HOME", str(Path.home() / "training" / "airflow_home")))


def sample_dir() -> Path:
    """Folder with input CSVs. Tries env, then AIRFLOW_HOME, then the repo copy."""
    candidates = []
    if os.environ.get("OLIST_SAMPLE_DIR"):
        candidates.append(Path(os.environ["OLIST_SAMPLE_DIR"]))
    candidates.append(airflow_home() / "sample_data")
    # Repo layout: airflow/dags/this_file → airflow/sample_data
    candidates.append(Path(__file__).resolve().parents[1] / "sample_data")
    for path in candidates:
        if path.is_dir() and (path / "orders.csv").is_file():
            return path
    raise FileNotFoundError(
        "sample_data not found. Copy airflow/sample_data → "
        f"{airflow_home() / 'sample_data'} (see airflow-install.md)."
    )


def work_dir() -> Path:
    """Output folder for validate / quarantine / join results."""
    path = airflow_home() / "olist_work"
    path.mkdir(parents=True, exist_ok=True)
    return path


def landing_dir() -> Path:
    """Landing zone used by the parallel-ingest DAG."""
    path = work_dir() / "landing"
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: Path) -> list[dict[str, str]]:
    """Load a CSV as a list of row dicts (header → values)."""
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    """Write row dicts to a CSV (creates parent folders if needed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_sample_to_landing(filename: str) -> Path:
    """Copy one sample CSV into landing/ (ingest step)."""
    src = sample_dir() / filename
    if not src.is_file():
        raise FileNotFoundError(f"Missing sample file: {src}")
    dest = landing_dir() / filename
    shutil.copy2(src, dest)  # copy2 keeps file metadata
    return dest
