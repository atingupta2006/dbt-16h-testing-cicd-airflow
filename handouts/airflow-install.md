# Airflow installation (students)

Install **Apache Airflow** in its **own virtualenv** (do not mix with the dbt `.venv`).  
Use **Linux (Ubuntu)** for this course. Windows/WSL may work but is not the class path.

**Repo:** https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow  

After install, follow DAG demos in [`student-commands.md`](student-commands.md) §3–§4.

---

## Before you start

| Requirement | Notes |
|-------------|--------|
| Course repo cloned | You can `cd` to the repo root |
| Python 3 | `python3 --version` works |
| dbt already set up | `dbt_project/.venv` exists; `~/.dbt/env.sh` and `~/.dbt/profiles.yml` work (`dbt debug` OK) |
| Network | Needed once to download Airflow + constraints |

Paths used below (recommended):

| Item | Path |
|------|------|
| Airflow venv | `~/training/venvs/airflow` |
| `AIRFLOW_HOME` | `~/training/airflow_home` |
| Course repo | wherever you cloned it (examples use that as “repo root”) |

---

## 1. Create a dedicated Airflow venv

From **anywhere**:

```bash
mkdir -p ~/training/venvs
python3 -m venv ~/training/venvs/airflow
source ~/training/venvs/airflow/bin/activate
python -m pip install --upgrade pip
```

Confirm you are in the Airflow venv (prompt usually shows `(airflow)`):

```bash
which python
# expect: .../training/venvs/airflow/bin/python
```

---

## 2. Install Airflow 2.9.3 (with official constraints)

Always install with the **constraints file** matching your Python minor version (avoids dependency conflicts).

```bash
source ~/training/venvs/airflow/bin/activate

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "Python version for constraints: ${PY_MM}"

pip install "apache-airflow==2.9.3" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PY_MM}.txt"
```

Check:

```bash
airflow version
# expect: 2.9.3
```

---

## 3. Create `AIRFLOW_HOME`

```bash
export AIRFLOW_HOME=~/training/airflow_home
mkdir -p "$AIRFLOW_HOME/dags"
echo "AIRFLOW_HOME=$AIRFLOW_HOME"
```

Put `export AIRFLOW_HOME=~/training/airflow_home` in every new shell before using Airflow (or add it to your shell profile if you prefer).

---

## 4. Wire course DAGs into Airflow

From **repo root** (folder that contains `airflow/` and `dbt_project/`):

```bash
cd /path/to/dbt-16h-testing-cicd-airflow   # your clone path

export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate

REPO_DIR="$(pwd)"
for f in "$REPO_DIR"/airflow/dags/*.py; do
  ln -sfn "$f" "$AIRFLOW_HOME/dags/$(basename "$f")"
done

ls -la "$AIRFLOW_HOME/dags"
# expect symlinks: demo_schedule_retries.py, dbt_core_run_test.py,
#                  dbt_core_e2e_pipeline.py, dbt_paths.py
```

Re-run the `ln -sfn` loop if you pull new DAG files later.

---

## 5. Point Airflow at your dbt project

dbt DAGs call the **dbt** binary and Snowflake env file. Export these in the **same shell** that will start Airflow (UI triggers inherit that process environment):

```bash
# still at repo root, Airflow venv active, AIRFLOW_HOME set
REPO_DIR="$(pwd)"

export DBT_BIN="$REPO_DIR/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$REPO_DIR/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"

# quick checks
test -x "$DBT_BIN" && echo "dbt binary OK" || echo "FIX: create dbt_project/.venv and install requirements"
test -f "$DBT_ENV_FILE" && echo "env.sh OK" || echo "FIX: create ~/.dbt/env.sh"
"$DBT_BIN" --version
```

`airflow/dags/dbt_paths.py` can also default to `$REPO/dbt_project/.venv/bin/dbt` when DAGs are symlinked from this repo — exporting `DBT_*` is still the safest for class.

---

## 6. Start Airflow (UI)

`airflow standalone` creates a local DB, starts the webserver, and prints an admin password the **first** time.

**Tip:** run it in `tmux` so it can stay up while you use another terminal:

```bash
tmux new -s airflow
# inside tmux:
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
export DBT_BIN=...          # same as §5
export DBT_PROJECT_DIR=...
export DBT_ENV_FILE=...
airflow standalone
# Detach: Ctrl-b then d
# Re-attach later: tmux attach -t airflow
```

Without tmux (blocks that terminal):

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
# export DBT_* as in §5
airflow standalone
```

Open the UI URL shared in class (often `http://<host>:8080`).  
Login: user **`admin`** and the password printed by `standalone` (or the password shared by the instructor on the shared VM).

---

## 7. Confirm install worked

**New terminal** (Airflow venv + `AIRFLOW_HOME` + `DBT_*`):

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
# export DBT_* from §5 if you will run dbt DAGs

airflow dags list | grep -E 'demo_schedule|dbt_core'
```

Expect to see at least:

- `demo_schedule_retries`
- `dbt_core_run_test`
- `dbt_core_e2e_pipeline`

Optional smoke (unique timestamp each time):

```bash
RUN_DATE="$(date -u +%Y-%m-%dT%H:%M:%S)"
airflow dags test demo_schedule_retries "$RUN_DATE"
```

Full dbt DAG commands: [`student-commands.md`](student-commands.md) §3.

---

## Every new shell (cheat sheet)

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
cd /path/to/dbt-16h-testing-cicd-airflow
export DBT_BIN="$(pwd)/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$(pwd)/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"
```

---

## Common problems

| Symptom | What to check |
|---------|----------------|
| `airflow: command not found` | `source ~/training/venvs/airflow/bin/activate` |
| DAGs missing in UI | Symlinks in `$AIRFLOW_HOME/dags`; wait ~30s; check import errors in standalone log |
| dbt task fails / “dbt not found” | `DBT_BIN` points at `dbt_project/.venv/bin/dbt`; that venv exists |
| Snowflake auth errors from DAG | `source` / path of `~/.dbt/env.sh`; same values that work for `dbt debug` |
| Port 8080 busy | Another Airflow already running (`tmux ls`); or change host/port per instructor |
| pip / dependency errors | Use the **constraints** URL for your `PY_MM`; don’t install Airflow into the dbt venv |

---

## What this course does *not* require

- Docker / Astronomer / MWAA / Composer  
- Installing Airflow into the dbt virtualenv  
- Changing the pinned version away from **2.9.3** (unless the instructor says so)
