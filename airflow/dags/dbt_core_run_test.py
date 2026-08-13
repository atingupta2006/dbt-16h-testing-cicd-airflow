"""DAG: dbt Core run then test (BashOperator)."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

from dbt_paths import dbt_bash

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="dbt_core_run_test",
    description="Airflow runs dbt Core run then test",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "dbt"],
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=dbt_bash("run --target dev"),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=dbt_bash("test --target dev --select tag:every_build"),
    )

    dbt_run >> dbt_test
