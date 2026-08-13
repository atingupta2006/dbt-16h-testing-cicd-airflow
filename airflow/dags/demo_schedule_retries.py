"""Airflow basics: schedule + retries (Olist RAW freshness).

Real check: required sample CSVs exist, are non-empty, and have expected headers.
If the check fails, Airflow retries (retries=2).

Demo: Trigger now — do not wait for @daily.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from olist_demo_io import REQUIRED_RAW, sample_dir

EXPECTED_HEADERS = {
    "orders.csv": {"order_id", "customer_id", "order_status"},
    "payments.csv": {"order_id", "payment_value"},
    "customers.csv": {"customer_id"},
}


def check_raw_olist_freshness() -> str:
    raw = sample_dir()
    lines = [f"RAW root: {raw}"]
    for name in REQUIRED_RAW:
        path = raw / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing RAW landing: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"Empty RAW landing: {path}")
        header = path.read_text(encoding="utf-8").splitlines()[0].split(",")
        missing_cols = EXPECTED_HEADERS[name] - set(header)
        if missing_cols:
            raise ValueError(f"{name} missing columns: {sorted(missing_cols)}")
        # subtract header
        row_count = max(0, sum(1 for _ in path.open(encoding="utf-8")) - 1)
        lines.append(f"OK {name}: {row_count} data rows")
    summary = " | ".join(lines)
    print(summary)
    return summary


default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="demo_schedule_retries",
    description="Olist: daily RAW freshness check (schedule + retries)",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow", "olist"],
) as dag:

    PythonOperator(
        task_id="check_raw_olist_freshness",
        python_callable=check_raw_olist_freshness,
    )
