# Airflow installation (students)

**Linux (Ubuntu).** Use a **separate** venv from dbt.  
Version: **Apache Airflow 2.9.3**.

Repo: https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow  

After this, use [`student-commands.md`](student-commands.md) §3 for DAG demos.

---

## 1. Install (once)

```bash
python3 -m venv ~/training/venvs/airflow
source ~/training/venvs/airflow/bin/activate
python -m pip install --upgrade pip

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
pip install "apache-airflow==2.9.3" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PY_MM}.txt"

export AIRFLOW_HOME=~/training/airflow_home
mkdir -p "$AIRFLOW_HOME/dags"
airflow version
```

---

## 2. Wire DAGs + dbt paths (once per machine / after clone)

From **repo root** (`dbt-16h-testing-cicd-airflow`):

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate

REPO_DIR="$(pwd)"
for f in "$REPO_DIR"/airflow/dags/*.py; do
  ln -sfn "$f" "$AIRFLOW_HOME/dags/$(basename "$f")"
done

export DBT_BIN="$REPO_DIR/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$REPO_DIR/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"
```

(dbt venv + `~/.dbt/env.sh` must already work.)

---

## 3. Start UI (optional)

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
# export DBT_* as in §2 (same shell)

airflow standalone
```

Login: **admin** + password from the standalone output (or shared in class).  
UI URL: shared in class (often port **8080**).

Use `tmux` if you want the UI to keep running in the background.

---

## Every new shell

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
cd /path/to/dbt-16h-testing-cicd-airflow
export DBT_BIN="$(pwd)/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$(pwd)/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"
```
