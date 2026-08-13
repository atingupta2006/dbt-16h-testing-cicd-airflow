"""DAG: upstream stub -> dbt run -> dbt test -> downstream stub."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from dbt_paths import dbt_bash

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="dbt_core_e2e_pipeline",
    description="Dependency orchestration around dbt Core",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "dbt", "e2e"],
) as dag:

    raw_data_ready = EmptyOperator(task_id="raw_data_ready")

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=dbt_bash("run --target dev"),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=dbt_bash("test --target dev --select tag:critical"),
    )

    publish_ready = BashOperator(
        task_id="publish_ready",
        bash_command='echo "Downstream consumers may refresh now"',
    )

    raw_data_ready >> dbt_run >> dbt_test >> publish_ready
