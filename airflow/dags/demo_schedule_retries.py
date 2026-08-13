"""Airflow basics: schedule + retries (Olist-style story).

Story (simulated — no Snowflake / dbt yet):
  Every day, check that RAW Olist landings arrived.
  If the check fails, Airflow retries (retries=2, 1 minute apart).

Demo: open Graph, point at schedule / retries / retry_delay, then Trigger
(do not wait for the daily schedule).
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

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

    # One task keeps the Graph obvious while teaching schedule/retries
    check_raw_olist_freshness = BashOperator(
        task_id="check_raw_olist_freshness",
        bash_command=(
            'echo "[$(date -u +%H:%M:%S)] DAILY CHECK: RAW Olist landings '
            '(orders, order_items, payments, customers, …)"; '
            'echo "[$(date -u +%H:%M:%S)] OK — freshness within SLA '
            '(simulated). On real fail, Airflow would retry 2x."'
        ),
    )
