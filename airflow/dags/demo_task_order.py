"""Airflow basics: task order (Olist-style story).

Story (simulated — no Snowflake / dbt yet):
  Before dbt runs, RAW must be validated, bad rows set aside, then marked ready.
  Order matters: validate → quarantine → publish.

UI: open Graph — arrows show the chain — then Trigger.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="demo_task_order",
    description="Olist: validate RAW → quarantine → publish ready (ordered)",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow", "olist"],
) as dag:

    validate_raw_files = BashOperator(
        task_id="validate_raw_files",
        bash_command=(
            'sleep 1; '
            'echo "[$(date -u +%H:%M:%S)] VALIDATE: required Olist CSVs present '
            '(orders, order_items, payments, customers, …)"'
        ),
    )

    quarantine_bad_rows = BashOperator(
        task_id="quarantine_bad_rows",
        bash_command=(
            'sleep 1; '
            'echo "[$(date -u +%H:%M:%S)] QUARANTINE: flag known dirty RAW rows '
            '(e.g. zero payment_value) for later warn_only tests"'
        ),
    )

    publish_raw_ready = BashOperator(
        task_id="publish_raw_ready",
        bash_command=(
            'echo "[$(date -u +%H:%M:%S)] PUBLISH: RAW ready for staging/dbt '
            '(next: parallel ingest demo or dbt DAGs)"'
        ),
    )

    # Arrow in the Graph = this order
    validate_raw_files >> quarantine_bad_rows >> publish_raw_ready
