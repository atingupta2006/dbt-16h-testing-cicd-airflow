# Airflow DAGs

Install first: [`airflow-install.md`](airflow-install.md)  
Commands index: [`student-commands.md`](student-commands.md) §3

Work in this order: **DAG 1 → DAG 2 → DAG 3**.

Before you start: copy the DAG `.py` files into `$AIRFLOW_HOME/dags` (see install), restart Airflow if it was already running, and set `DBT_*` in the shell that starts Airflow.

---

## Words used here

| Word | Meaning |
|------|---------|
| **DAG** | One pipeline in Airflow (a graph of steps) |
| **Task** | One step in that graph |
| **Trigger** | Run the DAG now from the UI (play button) |

## Run any DAG from the UI

1. Open the Airflow URL → login.  
2. Click the DAG name → open **Graph**.  
3. Click **Trigger**.  
4. When a task turns green, click it → **Log**.

---

## DAG 1 — `demo_schedule_retries`

**Why this DAG:** first look at Airflow only — schedule and retries. It does **not** call dbt.

**File:** `airflow/dags/demo_schedule_retries.py`

**Graph:** one task named `hello` (prints a short message).

**What to notice in the code:**

| Setting | In this file | Meaning |
|---------|--------------|---------|
| `schedule="@daily"` | on the DAG | Airflow would run it once per day on its own |
| `retries=2` | in `default_args` | If the task fails, try again up to 2 more times |
| `retry_delay` | 1 minute | Wait this long between retries |

In class you still **Trigger** it manually so you see a run immediately (you do not wait for the daily schedule).

**What to do:** UI → `demo_schedule_retries` → Graph → Trigger → open task `hello` → Log.

**Success:** task is green; log contains a line like `Airflow demo OK at …`.

---

## DAG 2 — `dbt_core_commands`

**Why this DAG:** Airflow runs dbt commands in order.

**File:** `airflow/dags/dbt_core_commands.py`

**Graph:**

```text
dbt_run → dbt_test_critical → dbt_build → dbt_docs_generate
```

| Task | What it runs | What to expect |
|------|----------------|----------------|
| `dbt_run` | `dbt run --target dev` | Models only |
| `dbt_test_critical` | `dbt test --select tag:critical` | `PASS=3 WARN=0 ERROR=0` |
| `dbt_build` | `dbt build --target dev` | Full build; `WARN=2` OK if `ERROR=0` |
| `dbt_docs_generate` | `dbt docs generate` | Files under `dbt_project/target/` (e.g. `index.html`) |

**What to do:** UI → `dbt_core_commands` → Graph → Trigger → open `dbt_test_critical` Log.

---

## DAG 3 — `dbt_orchestrated_pipeline`

**Why this DAG:** layered dbt run, then quality checks, then a “publish” stub (dependency orchestration).

**File:** `airflow/dags/dbt_orchestrated_pipeline.py`

**Graph:**

```text
raw_data_ready → run_staging → run_intermediate → run_marts → test_critical
                     test_critical → test_warn_only → publish_ready
                     test_critical → docs_generate  → publish_ready
```

| Task | Role |
|------|------|
| `raw_data_ready` | Marks “RAW is ready” (data already in Snowflake) |
| `run_staging` / `run_intermediate` / `run_marts` | `dbt run` for that layer |
| `test_critical` | Must-pass tests (`PASS=3 WARN=0 ERROR=0`) |
| `test_warn_only` | Heads-up tests (`PASS=2 WARN=2 ERROR=0`) |
| `docs_generate` | `dbt docs generate` |
| `publish_ready` | Marks “downstream may refresh” |

**What to do:** UI → `dbt_orchestrated_pipeline` → **Graph** (see the arrows) → Trigger → check `test_critical` and `test_warn_only` logs.

**Success:** all tasks green.

---

## Local / CI build vs Airflow critical task

| | `dbt build` (local or CI) | Airflow `test_critical` / `dbt_test_critical` |
|--|---------------------------|-----------------------------------------------|
| Which tests? | All (including `warn_only`) | Only `tag:critical` |
| Typical line | `PASS=35 WARN=2 ERROR=0` | `PASS=3 WARN=0 ERROR=0` |

The payment WARN still exists in the data; the critical task simply does not select those tests. DAG 3’s `test_warn_only` shows them.

---

## FAQ

| Question | Answer |
|----------|--------|
| Where is the payment WARN in the critical task? | Not selected. Open `test_warn_only` on DAG 3. |
| Where are docs files? | After `docs_generate` / `dbt_docs_generate`: under `dbt_project/target/`. |
