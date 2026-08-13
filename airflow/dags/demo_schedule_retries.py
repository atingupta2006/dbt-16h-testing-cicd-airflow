"""TOC: Airflow intro + DAGs, scheduling, retries.

Demo: open this DAG in the UI, point at schedule / retries / retry_delay, then Trigger.
No dbt — one Bash task so beginners see a green run first.
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
    description="Intro: schedule + retries (no dbt)",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow"],
) as dag:

    # Single task so the graph stays obvious
    hello = BashOperator(
        task_id="hello",
        bash_command='echo "Airflow demo OK at $(date -u)"',
    )
