"""Airflow basics: parallel ingest, then join (Olist orders + payments).

Real work: copy sample CSVs into landing in parallel, join on order_id,
write a staging CSV, then a ready marker. No dbt / Snowflake yet.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from olist_demo_io import copy_sample_to_landing, landing_dir, read_csv, work_dir, write_csv


def ingest_orders() -> str:
    time.sleep(2)  # keep Graph parallel story visible in class
    dest = copy_sample_to_landing("orders.csv")
    n = max(0, sum(1 for _ in dest.open(encoding="utf-8")) - 1)
    msg = f"Ingested orders → {dest} ({n} rows)"
    print(msg)
    return msg


def ingest_payments() -> str:
    time.sleep(2)
    dest = copy_sample_to_landing("payments.csv")
    n = max(0, sum(1 for _ in dest.open(encoding="utf-8")) - 1)
    msg = f"Ingested payments → {dest} ({n} rows)"
    print(msg)
    return msg


def join_orders_payments() -> str:
    orders = read_csv(landing_dir() / "orders.csv")
    payments = read_csv(landing_dir() / "payments.csv")
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
    msg = f"Joined {len(joined)} orders → {out}"
    print(msg)
    return msg


def mark_ready_for_dbt() -> str:
    stg = work_dir() / "stg_orders_payments.csv"
    if not stg.is_file():
        raise FileNotFoundError(f"Expected join output missing: {stg}")
    marker = work_dir() / "READY_FOR_DBT"
    marker.write_text(
        f"ready_at_utc={datetime.utcnow().isoformat()}Z\n"
        f"staging_file={stg}\n"
        f"next=dbt_core_commands / dbt_orchestrated_pipeline\n",
        encoding="utf-8",
    )
    msg = f"Ready marker written → {marker}"
    print(msg)
    return msg


default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="demo_parallel_join",
    description="Olist: parallel CSV ingest → join → ready for dbt",
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

    [orders, payments] >> join >> ready
