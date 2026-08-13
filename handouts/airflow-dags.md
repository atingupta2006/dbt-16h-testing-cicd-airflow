# Airflow DAGs (class)

Install first: [`airflow-install.md`](airflow-install.md)  
Command index: [`student-commands.md`](student-commands.md) §3

**Start here (new to Airflow):** DAG 1 → DAG 2 → DAG 3.

Copy DAG files into `$AIRFLOW_HOME/dags` after clone/pull, then restart Airflow if it is already running.

---

## At work vs in this class

| In a company | What we show here |
|--------------|-------------------|
| Scheduler runs pipelines on a timetable | DAG 1: `schedule="@daily"` + retries |
| Orchestrator calls dbt CLI | DAG 2: run / test / build / docs |
| Layered warehouse job with a quality gate | DAG 3: staging → intermediate → marts → critical → publish |

---

## Glossary

| Term | Meaning |
|------|---------|
| **DAG** | The pipeline graph (tasks + order) |
| **Task** | One box (here: a Bash command, often `dbt …`) |
| **Trigger** | Manual run from the UI |
| **`airflow dags test`** | Run the DAG **once from the terminal** — **not** `dbt test` |
| **Logical date** | Timestamp you pass to `dags test` (use a **new** one each re-run) |

---

## Every shell (before CLI or after restart)

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
cd /path/to/dbt-16h-testing-cicd-airflow
export DBT_BIN="$(pwd)/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$(pwd)/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"
```

```bash
RUN_DATE="$(date -u +%Y-%m-%dT%H:%M:%S)"
```

---

## DAG 1 — `demo_schedule_retries`

**TOC:** intro, scheduling, retries. **No dbt.**

```text
hello
```

Point at in code: `schedule="@daily"`, `retries`, `retry_delay`.

**UI:** Trigger → task `hello` success.  
**CLI:** `airflow dags test demo_schedule_retries "$RUN_DATE"`

**Success:** `Airflow demo OK at …` in the log.

---

## DAG 2 — `dbt_core_commands`

**TOC:** running dbt (run / test / build / docs).

```text
dbt_run → dbt_test_critical → dbt_build → dbt_docs_generate
```

| Task | dbt command | Note |
|------|-------------|------|
| `dbt_run` | `run --target dev` | Models only |
| `dbt_test_critical` | `test --select tag:critical` | Must-pass; expect `PASS=3 WARN=0 ERROR=0` |
| `dbt_build` | `build --target dev` | All tests too; `WARN=2` OK |
| `dbt_docs_generate` | `docs generate` | Writes `dbt_project/target/index.html` (no docs server in class) |

Walk the graph left to right. The first two tasks show the core pattern (`run` then must-pass tests); `build` and `docs generate` complete the same DAG.

**UI:** Trigger → open `dbt_test_critical` log.  
**CLI:** `airflow dags test dbt_core_commands "$RUN_DATE"`

---

## DAG 3 — `dbt_orchestrated_pipeline`

**TOC:** dependency orchestration + end-to-end (this is the “star” DAG).

```text
raw_data_ready → run_staging → run_intermediate → run_marts → test_critical
                     test_critical → test_warn_only → publish_ready
                     test_critical → docs_generate  → publish_ready
```

| Task | Role |
|------|------|
| `raw_data_ready` | Stub — RAW is already in Snowflake |
| `run_staging` / `intermediate` / `marts` | Layered `dbt run --select tag:…` |
| `test_critical` | Hard gate (`WARN=0`) |
| `test_warn_only` | Heads-up (`WARN=2` OK, ERROR=0) |
| `docs_generate` | Catalog after the gate |
| `publish_ready` | Stub — “consumers may refresh” |

**UI:** Graph view first, then Trigger.  
**CLI:** `airflow dags test dbt_orchestrated_pipeline "$RUN_DATE"`

**Success:** all tasks green; `test_critical` log `PASS=3 WARN=0 ERROR=0`; `test_warn_only` log `PASS=2 WARN=2 ERROR=0`.

---

## Local vs CI vs Airflow

| | Local / CI `dbt build` | Airflow critical task |
|--|------------------------|------------------------|
| Tests | All (including warn_only) | `tag:critical` only |
| Typical summary | `PASS=35 WARN=2 ERROR=0` | `PASS=3 WARN=0 ERROR=0` |

WARN=2 in a full build does **not** mean Airflow is hiding bad data — those tests are simply **not selected** on the critical task.

---

## What to click (UI)

1. Open the Airflow URL from class → login.  
2. Filter tags `airflow` or `dbt` if the list is long.  
3. Open the DAG → **Graph**.  
4. **Trigger** (play button).  
5. Click a task → **Log**.

Older `dbt_core_run_test` / `dbt_core_e2e_pipeline` files were removed from the repo. If they still show in your UI from an earlier copy, delete them from `$AIRFLOW_HOME/dags/` and re-copy using [`airflow-install.md`](airflow-install.md).

---

## FAQ

| Question | Answer |
|----------|--------|
| Is `airflow dags test` the same as `dbt test`? | No. It runs the **whole DAG** once from the CLI. |
| Why a new `$RUN_DATE`? | Airflow treats each timestamp as a run. Reuse can look skipped/confusing. |
| Where did payment WARN go in critical? | Not selected. See `test_warn_only` on DAG 3. |
| Docs site? | We only **generate** files under `target/`. No `dbt docs serve` in class. |

---

## Trainer checklist

- [ ] DAGs copied to `$AIRFLOW_HOME/dags`; Airflow restarted if needed  
- [ ] `DBT_*` exported in the **same** process that runs standalone  
- [ ] Show DAG 1 first (no warehouse wait)  
- [ ] DAG 2: open `dbt_test_critical` log  
- [ ] DAG 3: Graph before Trigger  
