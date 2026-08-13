"""Demo DAG: schedule + retries only (no dbt yet)."""

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
    description="DAG scheduling and retries",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow"],
) as dag:

    hello = BashOperator(
        task_id="hello",
        bash_command='echo "Airflow demo OK at $(date -u)"',
    )
