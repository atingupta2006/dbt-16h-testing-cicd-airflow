"""Airflow basics: parallel branches, then a join (Olist-style story).

Story (simulated — no Snowflake / dbt yet):
  Ingest orders.csv and payments.csv at the same time,
  then join them into one staging file, then mark ready for dbt.

UI: Graph shows two ingest tasks side by side → join → ready. Then Trigger.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# Tiny sleeps so the Graph clearly shows both ingest tasks green before the join
_INGEST = 'sleep 3; echo "[$(date -u +%H:%M:%S)] {label}: rows ready under /tmp/olist_demo/{file}"'

with DAG(
    dag_id="demo_parallel_join",
    description="Olist: parallel CSV ingest → join → ready for dbt",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow", "olist"],
) as dag:

    ingest_orders = BashOperator(
        task_id="ingest_orders",
        bash_command=_INGEST.format(label="INGEST orders.csv", file="orders.csv"),
    )

    ingest_payments = BashOperator(
        task_id="ingest_payments",
        bash_command=_INGEST.format(label="INGEST payments.csv", file="payments.csv"),
    )

    join_orders_payments = BashOperator(
        task_id="join_orders_payments",
        bash_command=(
            'sleep 1; '
            'echo "[$(date -u +%H:%M:%S)] JOIN orders+payments '
            '→ /tmp/olist_demo/stg_orders_payments.csv (simulated)"'
        ),
    )

    mark_ready_for_dbt = BashOperator(
        task_id="mark_ready_for_dbt",
        bash_command=(
            'echo "[$(date -u +%H:%M:%S)] READY: staging landings OK — '
            'next step in class is dbt (DAG 4+)"'
        ),
    )

    # Parallel ingest; join waits for both; then a clear handoff
    [ingest_orders, ingest_payments] >> join_orders_payments >> mark_ready_for_dbt
