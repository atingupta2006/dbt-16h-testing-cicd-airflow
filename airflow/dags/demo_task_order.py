"""Airflow basics: task order (A must finish before B).

UI: open Graph — arrows show the order — then Trigger.
No dbt.
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
    description="Task order: start >> process >> finish",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow"],
) as dag:

    start = BashOperator(
        task_id="start",
        bash_command='echo "START at $(date -u)"',
    )

    process = BashOperator(
        task_id="process",
        bash_command='echo "PROCESS at $(date -u)"',
    )

    finish = BashOperator(
        task_id="finish",
        bash_command='echo "FINISH at $(date -u)"',
    )

    # Arrow in the Graph = this order
    start >> process >> finish
