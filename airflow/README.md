# Airflow DAGs for this course

These DAGs call **dbt Core** via `BashOperator` (not dbt Cloud).

## Files

| DAG | Purpose |
|-----|---------|
| `demo_schedule_retries.py` | Schedule + retries |
| `dbt_core_run_test.py` | `dbt run` then `dbt test` |
| `dbt_core_e2e_pipeline.py` | Upstream → run → test → downstream |
| `dbt_paths.py` | Shared path helpers (not a DAG) |

## Wire into Airflow

```bash
export AIRFLOW_HOME=~/training/airflow_home   # or your Airflow home
mkdir -p "$AIRFLOW_HOME/dags"

REPO_DIR="$(pwd)"   # repo root
for f in "$REPO_DIR"/airflow/dags/*.py; do
  ln -sfn "$f" "$AIRFLOW_HOME/dags/$(basename "$f")"
done
```

Override paths if needed:

```bash
export DBT_PROJECT_DIR=/absolute/path/to/dbt_project
export DBT_BIN=/absolute/path/to/venv/bin/dbt
export DBT_ENV_FILE=$HOME/.dbt/env.sh
```

Install Airflow in a **separate** venv from dbt. See `GH/docs/03-airflow-integration.md`.
