"""01_check_raw_freshness - schedule + retries (Olist RAW check).

Purpose
  Run this DAG first in class.
  Show @daily schedule and automatic retries. One real check task (no dbt).

Flow
  check_raw_olist_freshness
    -> confirms sample CSVs exist, are non-empty, and have key columns
    -> on failure, Airflow retries (see default_args)

Class tip: Trigger now; do not wait for the daily schedule.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from olist_demo_io import REQUIRED_RAW, sample_dir

# Minimum columns we require in each file
EXPECTED_HEADERS = {
    "orders.csv": {"order_id", "customer_id", "order_status"},
    "payments.csv": {"order_id", "payment_value"},
    "customers.csv": {"customer_id"},
}


def check_raw_olist_freshness() -> str:
    """Fail the task if any required RAW file is missing, empty, or missing columns."""
    raw = sample_dir()
    lines = [f"RAW root: {raw}"]
    for name in REQUIRED_RAW:
        path = raw / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing RAW landing: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"Empty RAW landing: {path}")

        # First line = header; set difference finds missing column names
        header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
        missing_cols = EXPECTED_HEADERS[name] - set(header)
        if missing_cols:
            raise ValueError(f"{name} missing columns: {sorted(missing_cols)}")

        # Count data rows (total lines minus the header)
        row_count = max(0, sum(1 for _ in path.open(encoding="utf-8")) - 1)
        lines.append(f"OK {name}: {row_count} data rows")

    summary = " | ".join(lines)
    print(summary)
    return summary


# Shared task settings - retries apply when the Python check raises
default_args = {
    "owner": "data-team",
    "retries": 2,  # after a failure, try again up to 2 more times
    "retry_delay": timedelta(minutes=1),  # wait between retries
}

with DAG(
    dag_id="01_check_raw_freshness",
    description="Olist: daily RAW freshness check (schedule + retries)",
    start_date=datetime(2024, 1, 1),  # Airflow needs a start; catchup is off
    schedule="@daily",  # would run once per day if left unattended
    catchup=False,  # do not backfill old days
    default_args=default_args,
    tags=["demo", "airflow", "olist"],
) as dag:

    # Single task keeps the Graph simple while teaching schedule + retries
    PythonOperator(
        task_id="check_raw_olist_freshness",
        python_callable=check_raw_olist_freshness,
    )
