# Airflow installation

Separate venv from dbt. **Airflow 2.9.3.** Then [`airflow-dags.md`](airflow-dags.md).

**Python:** **3.12** (any 3.12.x). **3.14.x cannot install 2.9.3.** If no 3.12: **3.11**. https://www.python.org/downloads/

Class VM = Linux. Laptop = Windows CMD (§1W).

---

## 1. Linux (once)

```bash
python3 -m venv ~/training/venvs/airflow
source ~/training/venvs/airflow/bin/activate
python -m pip install --upgrade pip
pip install "apache-airflow==2.9.3" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.12.txt"
# If python is 3.11, use constraints-3.11.txt instead.

export AIRFLOW_HOME=~/training/airflow_home
mkdir -p "$AIRFLOW_HOME/dags" "$AIRFLOW_HOME/sample_data"
airflow version
```

From **repo root** (`pwd` must be the clone — empty `REPO_DIR` → DAG 04–05 `cd /dbt_project` fail):

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
REPO_DIR="$(pwd)"
cp "$REPO_DIR"/airflow/dags/*.py "$AIRFLOW_HOME/dags/"
cp "$REPO_DIR"/airflow/sample_data/*.csv "$AIRFLOW_HOME/sample_data/"
export DBT_BIN="$REPO_DIR/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$REPO_DIR/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"
airflow standalone
```

Login: **admin** + password from standalone. UI: port **8080**. `tmux` to keep it running. After `git pull`, re-copy DAGs and restart. Unpause DAGs in the UI if needed.

**New shell:** same `AIRFLOW_HOME`, activate, `cd` repo, export `DBT_*`, then `airflow standalone`.

---

## 1W. Windows (CMD)

Airflow 2.9.3 is **not supported on native Windows** (POSIX only). The `RuntimeWarning` is expected. SQLite must use **forward slashes** or you get `Cannot use relative path ... sqlite:///C:\...`.

```cmd
py -3.12 -m venv %USERPROFILE%\training\venvs\airflow
%USERPROFILE%\training\venvs\airflow\Scripts\activate.bat
python -m pip install --upgrade pip
pip install "apache-airflow==2.9.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.12.txt"
set AIRFLOW_HOME=%USERPROFILE%/training/airflow_home
set AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:///%AIRFLOW_HOME%/airflow.db
mkdir "%USERPROFILE%\training\airflow_home\dags" "%USERPROFILE%\training\airflow_home\sample_data"
airflow version
```

If `py -3.12` fails: install 3.12, or swap **3.11** in the venv + constraints URL.

From **repo root** (edit `REPO_DIR`). Keep `AIRFLOW_HOME` with `/` as above.

```cmd
copy /Y airflow\dags\*.py "%USERPROFILE%\training\airflow_home\dags\"
copy /Y airflow\sample_data\*.csv "%USERPROFILE%\training\airflow_home\sample_data\"
set REPO_DIR=C:/path/to/dbt-16h-testing-cicd-airflow
set DBT_BIN=%REPO_DIR%/dbt_project/.venv/Scripts/dbt.exe
set DBT_PROJECT_DIR=%REPO_DIR%/dbt_project
airflow standalone
```

Ignore `OSError ... symlink the latest log directory` if standalone still starts. UI: http://localhost:8080 — **admin** + password from standalone. Set `SNOWFLAKE_*` in this window before DAG 04–05.

If `airflow standalone` still crashes: use **WSL2** (Ubuntu) and follow §1, not CMD.
