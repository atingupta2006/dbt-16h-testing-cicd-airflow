# Airflow DAGs

Install first: [`airflow-install.md`](airflow-install.md)  
Commands index: [`student-commands.md`](student-commands.md) §3

Work in this **numbered** order (file name = DAG id):

| Order | DAG id | Purpose |
|------:|--------|---------|
| 01 | `dag_01_check_raw_freshness` | Daily RAW file check + schedule/retries |
| 02 | `dag_02_prepare_raw_ordered` | Validate → quarantine → publish (ordered) |
| 03 | `dag_03_ingest_parallel_join` | Parallel ingest → join → ready |
| 04 | `dag_04_dbt_commands_sequence` | dbt run → critical → build → docs |
| 05 | `dag_05_dbt_layered_orchestration` | Layered dbt + gates + publish |

Before you start: copy the course DAG `.py` files into `$AIRFLOW_HOME/dags` (see install), restart Airflow if it was already running, and set `DBT_*` in the shell that starts Airflow (needed from DAG 04 onward).

---

## Words used here

| Word | Meaning |
|------|---------|
| **DAG** | One pipeline in Airflow (a graph of steps) |
| **Task** | One step in that graph |
| **Trigger** | Run the DAG now from the UI (play button) |
| **Dependency** | An arrow: this task waits for that task |

## Run any DAG from the UI

1. Open the Airflow URL → login.  
2. Click the DAG name → open **Graph**.  
3. Click **Trigger**.  
4. When a task turns green, click it → **Log**.

---

## Built-in example DAGs (from Airflow itself)

After `airflow standalone`, the UI may also list DAGs whose ids start with **`example_`** (for example `example_bash_operator`). Those ship with Airflow — they are **not** files in this course repo.

| What to do | Why |
|------------|-----|
| Open one `example_*` DAG → **Graph** | See how Airflow authors show operators and arrows |
| Trigger it once | Confirm a green run without our course code |
| Then return to the course DAGs below | Course DAGs match this training path |

If you see **no** `example_*` DAGs, examples were turned off in config — use the course DAGs only; that is fine.

---

## DAG 1 — `dag_01_check_raw_freshness`

**Why:** first look at Airflow — schedule and retries. Does **not** call dbt.

**File:** `airflow/dags/dag_01_check_raw_freshness.py`

**Story:** a **daily** job that checks Olist **sample** RAW CSVs exist, are non-empty, and have required headers. If the check fails, Airflow **retries**.

**Graph:** one task — `check_raw_olist_freshness` (`PythonOperator`).

| Setting in code | Meaning |
|-----------------|---------|
| `schedule="@daily"` | Would run once per day on its own |
| `retries=2` | On failure, try again up to 2 more times |
| `retry_delay` (1 minute) | Wait between retries |

Install must copy `airflow/sample_data/*.csv` into `$AIRFLOW_HOME/sample_data` (see install handout).

In class, **Trigger** it so you see a run now (do not wait for the daily schedule).

**Do:** UI → `dag_01_check_raw_freshness` → Graph → Trigger → task Log.  
**Success:** green; log shows `OK orders.csv` / `OK payments.csv` / `OK customers.csv` with row counts.

---

## DAG 2 — `dag_02_prepare_raw_ordered`

**Why:** how **order** works — one task after another.

**File:** `airflow/dags/dag_02_prepare_raw_ordered.py`

**Story:** validate sample RAW → quarantine zero `payment_value` rows to a CSV → write a `RAW_READY` marker under `$AIRFLOW_HOME/olist_work/`.

**Graph:**

```text
validate_raw_files → quarantine_bad_rows → publish_raw_ready
```

| Task | What it really does |
|------|---------------------|
| `validate_raw_files` | Reads CSVs; writes `olist_work/validate_report.json` |
| `quarantine_bad_rows` | Writes `quarantine_zero_payments.csv` + `payments_clean.csv` |
| `publish_raw_ready` | Writes marker file `olist_work/RAW_READY` |

**Do:** UI → `dag_02_prepare_raw_ordered` → Graph → Trigger → open each Log.  
**Success:** all green; work files appear under `$AIRFLOW_HOME/olist_work/`.

---

## DAG 3 — `dag_03_ingest_parallel_join`

**Why:** some tasks can run **at the same time**, then a later task waits for all of them.

**File:** `airflow/dags/dag_03_ingest_parallel_join.py`

**Story:** copy `orders.csv` and `payments.csv` into landing **in parallel**, join on `order_id`, write staging CSV, then a ready marker.

**Graph:**

```text
ingest_orders ──┐
                ├──→ join_orders_payments → mark_ready_for_dbt
ingest_payments ┘
```

| Task | What it really does |
|------|---------------------|
| `ingest_orders` / `ingest_payments` | Copy sample CSV → `olist_work/landing/` |
| `join_orders_payments` | Build `olist_work/stg_orders_payments.csv` |
| `mark_ready_for_dbt` | Write `olist_work/READY_FOR_DBT` |

**Do:** UI → `dag_03_ingest_parallel_join` → Graph → Trigger.  
**Success:** both ingest green, then join, then ready; open Log for row counts / output paths.

---

## DAG 4 — `dag_04_dbt_commands_sequence`

**Why:** Airflow runs **dbt** commands in order.

**File:** `airflow/dags/dag_04_dbt_commands_sequence.py`

**Graph:**

```text
dbt_run → dbt_test_critical → dbt_build → dbt_docs_generate
```

| Task | What it runs | What to expect |
|------|----------------|----------------|
| `dbt_run` | `dbt run --target dev` | Models only |
| `dbt_test_critical` | `dbt test --select tag:critical` | `PASS=3 WARN=0 ERROR=0` |
| `dbt_build` | `dbt build --target dev` | Full build; `WARN=2` OK if `ERROR=0` |
| `dbt_docs_generate` | `dbt docs generate` | Files under `dbt_project/target/` |

**Do:** UI → `dag_04_dbt_commands_sequence` → Graph → Trigger → open `dbt_test_critical` Log.

---

## DAG 5 — `dag_05_dbt_layered_orchestration`

**Why:** layered dbt run, quality checks, then a publish stub (full orchestration).

**File:** `airflow/dags/dag_05_dbt_layered_orchestration.py`

**Graph:**

```text
raw_data_ready → run_staging → run_intermediate → run_marts → test_critical
                     test_critical → test_warn_only → publish_ready
                     test_critical → docs_generate  → publish_ready
```

| Task | Role |
|------|------|
| `raw_data_ready` | Placeholder: RAW is already in Snowflake (no COPY in this DAG) |
| `run_staging` / `run_intermediate` / `run_marts` | `dbt run` for that layer |
| `test_critical` | Must-pass (`PASS=3 WARN=0 ERROR=0`) |
| `test_warn_only` | Heads-up (`PASS=2 WARN=2 ERROR=0`) — includes the dirty-row checks |
| `docs_generate` | `dbt docs generate` |
| `publish_ready` | **Signal only** (not a real BI refresh). Echoes that `FCT_ORDERS` in `ANALYTICS_DEV` is ready. At work this would notify BI or kick a dashboard. Runs only after **both** `test_warn_only` and `docs_generate` (and those wait on `test_critical`). |

**Do:** UI → `dag_05_dbt_layered_orchestration` → Graph → Trigger → check `test_critical` and `test_warn_only` logs.  
**Success:** all tasks green.
