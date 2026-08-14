# Airflow installation (students)

Use a **separate** venv from dbt.  
Version: **Apache Airflow 2.9.3**.

Repo: https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow  

After this, use [`airflow-dags.md`](airflow-dags.md) (also linked from [`student-commands.md`](student-commands.md) §3).

**Python:** try **3.14** first. If `pip install apache-airflow==2.9.3` fails (no constraints file, or pip errors), use **3.12**. Airflow **2.9.3** is officially built for **3.8–3.12**; 3.12 is the class fallback.

**OS:** class VM is **Linux (Ubuntu)** — §1–3 below. **Windows (CMD)** — §1W.

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

Open **Command Prompt** (`cmd.exe`), not Git Bash.

Check Python, then pick 3.14 if it works, else 3.12:

```cmd
py -0p
py -3.14 --version
py -3.12 --version
```

**Create the venv** (use the line that matches a version you have):

```cmd
mkdir %USERPROFILE%\training\venvs
py -3.14 -m venv %USERPROFILE%\training\venvs\airflow
```

If that fails (`No suitable Python`), use 3.12:

```cmd
py -3.12 -m venv %USERPROFILE%\training\venvs\airflow
```

**Install Airflow 2.9.3:**

```cmd
%USERPROFILE%\training\venvs\airflow\Scripts\activate.bat
python -m pip install --upgrade pip

for /f "delims=" %i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PY_MM=%i
echo Using Python %PY_MM%

pip install "apache-airflow==2.9.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-%PY_MM%.txt"
```

If that `pip` line fails (typical on **3.14** — no `constraints-3.14.txt` for 2.9.3): deactivate, delete the venv folder, recreate with **`py -3.12`**, activate again, and rerun the `pip install` (you should see `Using Python 3.12`).

```cmd
set AIRFLOW_HOME=%USERPROFILE%\training\airflow_home
mkdir %AIRFLOW_HOME%\dags
airflow version
```

Copy DAGs (from **repo root**):

```cmd
set AIRFLOW_HOME=%USERPROFILE%\training\airflow_home
copy /Y airflow\dags\*.py %AIRFLOW_HOME%\dags\
mkdir %AIRFLOW_HOME%\sample_data
copy /Y airflow\sample_data\*.csv %AIRFLOW_HOME%\sample_data\
```

Set dbt paths (**same CMD window** before `airflow standalone`). Use your real clone path:

```cmd
set REPO_DIR=C:\25-Trainings\2-Confirmed\31-8-26-DBT-16-Hours
set DBT_BIN=%REPO_DIR%\dbt_project\.venv\Scripts\dbt.exe
set DBT_PROJECT_DIR=%REPO_DIR%\dbt_project
set DBT_ENV_FILE=%USERPROFILE%\.dbt\env.sh
```

On Windows, `env.sh` is for Git Bash. If dbt already works from CMD, you can instead put the same `SNOWFLAKE_*` values in a `.bat` and `call` it, or set them with `set SNOWFLAKE_ACCOUNT=...` in this window. `DBT_PROJECT_DIR` and `DBT_BIN` must still be set so DAG 04–05 do not `cd` to a bad path.

Start:

```cmd
set AIRFLOW_HOME=%USERPROFILE%\training\airflow_home
%USERPROFILE%\training\venvs\airflow\Scripts\activate.bat
airflow standalone
```

UI: http://localhost:8080 — **admin** + password printed by standalone.

Every new CMD window: activate the venv, `set AIRFLOW_HOME=...`, and set `DBT_*` again (same values as above).

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
