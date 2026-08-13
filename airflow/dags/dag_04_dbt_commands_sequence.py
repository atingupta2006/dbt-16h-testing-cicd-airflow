"""dag_04_dbt_commands_sequence - run dbt commands from Airflow (in order).

Purpose
  Run after the basics DAGs (01-03).
  Show Airflow calling the same dbt CLI you use in the terminal.

Flow
  dbt_run -> dbt_test_critical -> dbt_build -> dbt_docs_generate

Needs DBT_BIN, DBT_PROJECT_DIR, DBT_ENV_FILE in the Airflow process
(see handouts/airflow-install.md).
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

from dbt_paths import dbt_bash, dbt_project_dir

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="dag_04_dbt_commands_sequence",
    description="dbt run -> critical test -> build -> docs generate",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # Trigger from the UI in class
    catchup=False,
    default_args=default_args,
    tags=["demo", "dbt"],
) as dag:

    # 1) Models only (dev schema)
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=dbt_bash("run --target dev"),
    )

    # 2) Must-pass tests only (tag:critical -> severity error)
    dbt_test_critical = BashOperator(
        task_id="dbt_test_critical",
        bash_command=dbt_bash("test --target dev --select tag:critical"),
    )

    # 3) Models + all tests once (WARN on warn_only is OK if ERROR=0)
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=dbt_bash("build --target dev"),
    )

    # 4) Build the docs catalog files under target/ (no docs serve in class)
    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=dbt_bash("docs generate")
        + f'; echo "Docs catalog: {dbt_project_dir()}/target/index.html"',
    )

    # Left-to-right order in the Graph
    dbt_run >> dbt_test_critical >> dbt_build >> dbt_docs_generate
