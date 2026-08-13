"""dag_05_dbt_layered_orchestration - layered dbt end-to-end shape.

Purpose
  Run last - full layered orchestration.
  Run dbt by layer, gate on critical tests, then warn_only + docs in parallel,
  then a publish stub.

Flow
  raw_data_ready -> staging -> intermediate -> marts -> test_critical
                       test_critical -> test_warn_only -> publish_ready
                       test_critical -> docs_generate  -> publish_ready

Notes
  critical  = hard gate (must pass)
  warn_only = heads-up (WARN OK when ERROR=0)
  EmptyOperator / echo publish = placeholders for “upstream ready” / “BI may refresh”

Needs DBT_BIN, DBT_PROJECT_DIR, DBT_ENV_FILE (see airflow-install.md).
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
    dag_id="dag_05_dbt_layered_orchestration",
    description="Layered dbt run, critical gate, warn_only, docs, publish",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=False,  # show as active in UI on first load
    default_args=default_args,
    tags=["demo", "dbt", "orchestration", "e2e"],
) as dag:

    # Placeholder: in class, RAW is already loaded in Snowflake
    raw_data_ready = EmptyOperator(task_id="raw_data_ready")

    # Layered model builds (tag selects that layer only)
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

    # Hard gate - fail here and publish should not look “clean”
    test_critical = BashOperator(
        task_id="test_critical",
        bash_command=dbt_bash("test --target dev --select tag:critical"),
    )

    # Soft checks - dirty RAW rows may WARN; ERROR should stay 0
    test_warn_only = BashOperator(
        task_id="test_warn_only",
        bash_command=dbt_bash("test --target dev --select tag:warn_only"),
    )

    docs_generate = BashOperator(
        task_id="docs_generate",
        bash_command=dbt_bash("docs generate")
        + '; echo "Docs catalog: target/index.html (ANALYTICS_DEV models)"',
    )

    # Placeholder: “downstream consumers may refresh”
    publish_ready = BashOperator(
        task_id="publish_ready",
        bash_command='echo "Publish ready: OLIST_DB.ANALYTICS_DEV.FCT_ORDERS"',
    )

    # Main spine: layers then gate
    raw_data_ready >> run_staging >> run_intermediate >> run_marts >> test_critical
    # After the gate, warn_only and docs can run side by side; both feed publish
    test_critical >> test_warn_only >> publish_ready
    test_critical >> docs_generate >> publish_ready
