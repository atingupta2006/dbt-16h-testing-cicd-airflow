"""Airflow basics: parallel tasks, then join.

UI: open Graph — extract and transform run side by side, then load — Trigger.
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
    dag_id="demo_parallel_join",
    description="Parallel extract/transform, then join into load",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command='echo "EXTRACT at $(date -u)"',
    )

    transform = BashOperator(
        task_id="transform",
        bash_command='echo "TRANSFORM at $(date -u)"',
    )

    load = BashOperator(
        task_id="load",
        bash_command='echo "LOAD at $(date -u)"',
    )

    # extract and transform can run at the same time; load waits for both
    [extract, transform] >> load
