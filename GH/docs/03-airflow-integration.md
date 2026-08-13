# 03 — Airflow integration (dbt Core)

Practice: Airflow DAGs, scheduling, retries, running `dbt run` / `dbt test`, and task dependencies.

Use a **Linux** environment (Ubuntu VM is ideal). Keep Airflow in a separate venv from dbt.

## Files

- `airflow/dags/demo_schedule_retries.py`
- `airflow/dags/dbt_core_run_test.py`
- `airflow/dags/dbt_core_e2e_pipeline.py`
- `airflow/dags/dbt_paths.py`
- `airflow/README.md`

## Install Airflow (pinned)

```bash
python3 -m venv ~/training/venvs/airflow
source ~/training/venvs/airflow/bin/activate
python -m pip install --upgrade pip
PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
pip install "apache-airflow==2.9.3" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PY_MM}.txt"

export AIRFLOW_HOME=~/training/airflow_home
mkdir -p "$AIRFLOW_HOME/dags"
airflow standalone
```

Save the admin password printed on first start. UI: `http://localhost:8080` (or your VM IP).

Also create a dbt venv and `~/.dbt/env.sh` as in [00 Setup](00-setup.md). Point `DBT_BIN` at that venv’s `dbt` binary if it is not under `~/training/venvs/dbt/bin/dbt`.

## Wire DAGs

From the **repo root**:

```bash
export AIRFLOW_HOME=~/training/airflow_home
REPO_DIR="$(pwd)"
for f in "$REPO_DIR"/airflow/dags/*.py; do
  ln -sfn "$f" "$AIRFLOW_HOME/dags/$(basename "$f")"
done
```

## Practice sequence

1. Unpause `demo_schedule_retries` → Trigger → confirm retries config in code/UI.  
2. Unpause `dbt_core_run_test` → Trigger → `dbt_run` then `dbt_test`.  
3. Open `dbt_core_e2e_pipeline` graph: upstream → run → test → downstream → Trigger.  
4. Break a critical test → watch the Airflow task fail → fix → clear → success.
