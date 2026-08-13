"""TOC: Running DBT from Airflow (run / test / build / docs).

Demo: Trigger, then walk the graph left to right.
  dbt_run → dbt_test_critical → dbt_build → dbt_docs_generate

If short on time, stop after run + test and only mention the last two tasks.
Requires DBT_BIN, DBT_PROJECT_DIR, DBT_ENV_FILE (see handouts/airflow-install.md).
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
    dag_id="dbt_core_commands",
    description="dbt run → critical test → build → docs generate",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "dbt"],
) as dag:

    # 1) Build models (dev)
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=dbt_bash("run --target dev"),
    )

    # 2) Must-pass tests only (not warn_only)
    dbt_test_critical = BashOperator(
        task_id="dbt_test_critical",
        bash_command=dbt_bash("test --target dev --select tag:critical"),
    )

    # 3) Full build (models + all tests; WARN on warn_only is OK)
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=dbt_bash("build --target dev"),
    )

    # 4) Catalog for docs (file under dbt_project/target/; no docs serve in class)
    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=dbt_bash("docs generate")
        + f'; echo "Docs catalog: {dbt_project_dir()}/target/index.html"',
    )

    dbt_run >> dbt_test_critical >> dbt_build >> dbt_docs_generate
