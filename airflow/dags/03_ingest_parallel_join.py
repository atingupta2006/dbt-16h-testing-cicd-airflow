"""03_ingest_parallel_join - parallel ingest, then join.

Purpose
  Run after 02_prepare_raw_ordered.
  Show two tasks that can run at the same time, then one task that waits for both.

Flow
  ingest_orders ──┐
                  ├──-> join_orders_payments -> mark_ready_for_dbt
  ingest_payments ┘

  1) Copy orders.csv and payments.csv into landing/ (in parallel)
  2) Join on order_id -> stg_orders_payments.csv
  3) Write READY_FOR_DBT marker (handoff to later dbt DAGs)
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from olist_demo_io import copy_sample_to_landing, landing_dir, read_csv, work_dir, write_csv


def ingest_orders() -> str:
    """Copy orders.csv into the landing folder."""
    time.sleep(2)  # short pause so the UI Graph clearly shows parallel work
    dest = copy_sample_to_landing("orders.csv")
    n = max(0, sum(1 for _ in dest.open(encoding="utf-8")) - 1)
    msg = f"Ingested orders -> {dest} ({n} rows)"
    print(msg)
    return msg


def ingest_payments() -> str:
    """Copy payments.csv into the landing folder."""
    time.sleep(2)
    dest = copy_sample_to_landing("payments.csv")
    n = max(0, sum(1 for _ in dest.open(encoding="utf-8")) - 1)
    msg = f"Ingested payments -> {dest} ({n} rows)"
    print(msg)
    return msg


def join_orders_payments() -> str:
    """Sum payments per order_id, then write one staging CSV."""
    orders = read_csv(landing_dir() / "orders.csv")
    payments = read_csv(landing_dir() / "payments.csv")

    # One order can have many payment rows - add them up
    pay_by_order: dict[str, float] = {}
    for row in payments:
        oid = row["order_id"]
        pay_by_order[oid] = pay_by_order.get(oid, 0.0) + float(row["payment_value"] or 0)

    joined = []
    for row in orders:
        oid = row["order_id"]
        joined.append(
            {
                "order_id": oid,
                "customer_id": row.get("customer_id", ""),
                "order_status": row.get("order_status", ""),
                "total_payment_value": f"{pay_by_order.get(oid, 0.0):.2f}",
            }
        )

    out = work_dir() / "stg_orders_payments.csv"
    write_csv(
        out,
        joined,
        ["order_id", "customer_id", "order_status", "total_payment_value"],
    )
    msg = f"Joined {len(joined)} orders -> {out}"
    print(msg)
    return msg


def mark_ready_for_dbt() -> str:
    """Confirm the join file exists, then write a ready marker."""
    stg = work_dir() / "stg_orders_payments.csv"
    if not stg.is_file():
        raise FileNotFoundError(f"Expected join output missing: {stg}")

    marker = work_dir() / "READY_FOR_DBT"
    marker.write_text(
        f"ready_at_utc={datetime.utcnow().isoformat()}Z\n"
        f"staging_file={stg}\n"
        f"next=04_dbt_commands_sequence / 05_dbt_layered_orchestration\n",
        encoding="utf-8",
    )
    msg = f"Ready marker written -> {marker}"
    print(msg)
    return msg


default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="03_ingest_parallel_join",
    description="Olist: parallel CSV ingest -> join -> ready for dbt",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow", "olist"],
) as dag:

    orders = PythonOperator(task_id="ingest_orders", python_callable=ingest_orders)
    payments = PythonOperator(task_id="ingest_payments", python_callable=ingest_payments)
    join = PythonOperator(task_id="join_orders_payments", python_callable=join_orders_payments)
    ready = PythonOperator(task_id="mark_ready_for_dbt", python_callable=mark_ready_for_dbt)

    # List on the left = those tasks may run together; join waits for both
    [orders, payments] >> join >> ready
