# Airflow installation (students)

Use a **separate** venv from dbt. Version: **Apache Airflow 2.9.3**.

Repo: https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow  

Then: [`airflow-dags.md`](airflow-dags.md).

**Python for 2.9.3:** use **3.12** (any 3.12.x). **3.14.3 alone cannot install 2.9.3.** Install 3.12 from https://www.python.org/downloads/ (keep 3.14 if you want). If 3.12 is not available: **3.11**.

Linux (class VM): §1–3. Windows CMD: §1W.

---

## 1. Install (once) — Linux (Ubuntu)

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

## 1W. Install (once) — Windows (CMD)

`cmd.exe`. `py -0p` lists Pythons.

```cmd
py -3.12 -m venv %USERPROFILE%\training\venvs\airflow
%USERPROFILE%\training\venvs\airflow\Scripts\activate.bat
python -m pip install --upgrade pip
pip install "apache-airflow==2.9.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.12.txt"
set AIRFLOW_HOME=%USERPROFILE%\training\airflow_home
mkdir %AIRFLOW_HOME%\dags
airflow version
```

If `py -3.12` fails: install **3.12**, or use **3.11** (change `3.12` → `3.11` in both lines). Do not use 3.14.3 for 2.9.3.

From **repo root** (edit `REPO_DIR`):

```cmd
copy /Y airflow\dags\*.py %AIRFLOW_HOME%\dags\
mkdir %AIRFLOW_HOME%\sample_data
copy /Y airflow\sample_data\*.csv %AIRFLOW_HOME%\sample_data\
set REPO_DIR=C:\path\to\dbt-16h-testing-cicd-airflow
set DBT_BIN=%REPO_DIR%\dbt_project\.venv\Scripts\dbt.exe
set DBT_PROJECT_DIR=%REPO_DIR%\dbt_project
airflow standalone
```

UI: http://localhost:8080 — **admin** + password from standalone. Set `SNOWFLAKE_*` in this window before DAG 04–05.

---

## 2. Copy DAGs + set dbt paths (once per machine / after clone)

From **repo root** (`dbt-16h-testing-cicd-airflow`):

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate

REPO_DIR="$(pwd)"
cp "$REPO_DIR"/airflow/dags/*.py "$AIRFLOW_HOME/dags/"
mkdir -p "$AIRFLOW_HOME/sample_data"
cp "$REPO_DIR"/airflow/sample_data/*.csv "$AIRFLOW_HOME/sample_data/"
# Drop older class DAG filenames if they still exist from a previous copy
rm -f "$AIRFLOW_HOME"/dags/demo_*.py \
      "$AIRFLOW_HOME"/dags/dbt_core_commands.py \
      "$AIRFLOW_HOME"/dags/dbt_orchestrated_pipeline.py \
      "$AIRFLOW_HOME"/dags/0*_*.py

export DBT_BIN="$REPO_DIR/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$REPO_DIR/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"
```

Set `DBT_*` from **repo root** (`REPO_DIR="$(pwd)"`). If `REPO_DIR` is empty you get `cd /dbt_project` and DAG 04–05 fail.

`DBT_*` is required here (copied DAGs do not sit inside the repo).  
dbt venv + `~/.dbt/env.sh` must already work.

If Airflow is already running, **restart** it after copying DAGs (stop `standalone`, start again — or restart the `tmux` session).

If a course DAG shows as **paused** in the UI, toggle it on (or: `airflow dags unpause <dag_id>`).

---

## 3. Start UI

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
# export DBT_* as in §2 (same shell)

# First start may also show Airflow's own example_* DAGs in the UI
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

Re-copy DAGs after `git pull` if DAG files changed, then restart Airflow if it is running.
