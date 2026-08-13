# Airflow DAGs (class)

Install first: [`airflow-install.md`](airflow-install.md)  
Command index: [`student-commands.md`](student-commands.md) §3

**Order:** DAG 1 → DAG 2 → DAG 3.

Copy DAG files into `$AIRFLOW_HOME/dags` after clone/pull, then restart Airflow if it is already running. Set `DBT_*` in the **same shell** that starts Airflow (see install handout).

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
| **Trigger** | Manual run from the UI (play button) |

---

## How to run a DAG (UI)

1. Open the Airflow URL from class → login.  
2. Open the DAG → **Graph**.  
3. **Trigger** (play button).  
4. Click a task → **Log**.

---

## DAG 1 — `demo_schedule_retries`

**TOC:** intro, scheduling, retries. **No dbt.**

```text
hello
```

In code: `schedule="@daily"`, `retries`, `retry_delay`.

**Success:** task `hello` green; log shows `Airflow demo OK at …`.

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
| `dbt_docs_generate` | `docs generate` | Writes `dbt_project/target/index.html` |

Walk the graph left to right. Open the `dbt_test_critical` log after Trigger.

---

## DAG 3 — `dbt_orchestrated_pipeline`

**TOC:** dependency orchestration + end-to-end (star DAG).

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
| `publish_ready` | Stub — consumers may refresh |

Open **Graph** first, then Trigger.  
**Success:** all tasks green; `test_critical` → `PASS=3 WARN=0 ERROR=0`; `test_warn_only` → `PASS=2 WARN=2 ERROR=0`.

---

## Local vs CI vs Airflow

| | Local / CI `dbt build` | Airflow critical task |
|--|------------------------|------------------------|
| Tests | All (including warn_only) | `tag:critical` only |
| Typical summary | `PASS=35 WARN=2 ERROR=0` | `PASS=3 WARN=0 ERROR=0` |

WARN=2 in a full build does **not** mean Airflow is hiding bad data — those tests are simply **not selected** on the critical task.

---

## FAQ

| Question | Answer |
|----------|--------|
| Where did payment WARN go in critical? | Not selected. See `test_warn_only` on DAG 3. |
| Docs output? | `dbt docs generate` writes files under `target/` (including `index.html`). |
