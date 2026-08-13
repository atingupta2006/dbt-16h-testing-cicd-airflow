"""TOC: Dependency orchestration + End-to-End (Olist + dbt Core).

Demo: open Graph view, then Trigger.
  raw_data_ready → staging → intermediate → marts → test_critical
       test_critical → test_warn_only → publish_ready
       test_critical → docs_generate  → publish_ready

Critical is the hard gate. warn_only is a heads-up (does not fail the DAG).
Requires DBT_BIN, DBT_PROJECT_DIR, DBT_ENV_FILE (see handouts/airflow-install.md).
"""

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
    dag_id="dbt_orchestrated_pipeline",
    description="Layered dbt run, critical gate, warn_only, docs, publish",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["demo", "dbt", "orchestration", "e2e"],
) as dag:

    # Upstream stub — RAW already loaded in class Snowflake
    raw_data_ready = EmptyOperator(task_id="raw_data_ready")

    run_staging = BashOperator(
        task_id="run_staging",
        bash_command=dbt_bash("run --target dev --select tag:staging"),
    )

    run_intermediate = BashOperator(
        task_id="run_intermediate",
        bash_command=dbt_bash("run --target dev --select tag:intermediate"),
    )

    run_marts = BashOperator(
        task_id="run_marts",
        bash_command=dbt_bash("run --target dev --select tag:marts"),
    )

    # Hard gate — must-pass tests
    test_critical = BashOperator(
        task_id="test_critical",
        bash_command=dbt_bash("test --target dev --select tag:critical"),
    )

    # Heads-up — dirty staging rows; dbt WARN with ERROR=0
    test_warn_only = BashOperator(
        task_id="test_warn_only",
        bash_command=dbt_bash("test --target dev --select tag:warn_only"),
    )

    docs_generate = BashOperator(
        task_id="docs_generate",
        bash_command=dbt_bash("docs generate")
        + '; echo "Docs catalog: target/index.html (ANALYTICS_DEV models)"',
    )

    # Downstream stub — BI / consumers could refresh after this
    publish_ready = BashOperator(
        task_id="publish_ready",
        bash_command='echo "Publish ready: OLIST_DB.ANALYTICS_DEV.FCT_ORDERS"',
    )

    raw_data_ready >> run_staging >> run_intermediate >> run_marts >> test_critical
    test_critical >> test_warn_only >> publish_ready
    test_critical >> docs_generate >> publish_ready
