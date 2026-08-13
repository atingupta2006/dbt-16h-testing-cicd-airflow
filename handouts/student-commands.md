# Commands — DBT 16 Hours

Command list for this course project.

**Repository (use this only):** https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow

Use connection values shared in class. Prefer Linux (Ubuntu) for Airflow sections.

Model layers in `dbt_project/models/`: **staging** → **intermediate** → **marts**.

Dataset and flow: [`olist-data-and-flow.md`](olist-data-and-flow.md) · Handout order: [`README.md`](README.md)  
CI/CD and deploy: [`cicd-and-deployment.md`](cicd-and-deployment.md)  
Airflow install (once): [`airflow-install.md`](airflow-install.md)  
Airflow DAGs: [`airflow-dags.md`](airflow-dags.md)  
End-to-end walkthrough: [`e2e-production-walkthrough.md`](e2e-production-walkthrough.md)  
Incremental models: [`incremental-quick-look.md`](incremental-quick-look.md)

**How to read dbt summaries:** look at the last line, e.g. `Done. PASS=35 WARN=2 ERROR=0`.  
**ERROR=0** means nothing blocked the run. **WARN** means “heads-up” (dirty rows), not a hard stop.  
When you see WARN or FAIL, do not stop at the summary — use **§1e** to open the test name, YAML, generic SQL, compiled SQL, and the actual rows.

---

## 0. Environment (once)

```bash
git clone https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow.git
cd dbt-16h-testing-cicd-airflow
```

### dbt virtualenv

```bash
cd dbt_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Snowflake profile and env

```bash
mkdir -p ~/.dbt
cp profiles.yml.example ~/.dbt/profiles.yml
```

Create `~/.dbt/env.sh` (fill in values from class):

```bash
cat > ~/.dbt/env.sh <<'EOF'
export SNOWFLAKE_ACCOUNT="..."
export SNOWFLAKE_USER="..."
export SNOWFLAKE_PASSWORD="..."
export SNOWFLAKE_ROLE="..."
export SNOWFLAKE_DATABASE="OLIST_DB"
export SNOWFLAKE_WAREHOUSE="..."
export SNOWFLAKE_SCHEMA_DEV="ANALYTICS_DEV"
export SNOWFLAKE_SCHEMA_PROD="ANALYTICS"
EOF
chmod 600 ~/.dbt/env.sh
source ~/.dbt/env.sh
```

### Smoke test

```bash
# expect: staging  intermediate  marts
ls models
dbt debug
dbt build --target dev
```

**Expect — `dbt debug`:**

```text
All checks passed!
```

**Expect — `dbt build --target dev`:** builds staging → intermediate → marts, then runs tests.  
Summary should look like:

```text
Done. PASS=35 WARN=2 ERROR=0 SKIP=0 TOTAL=37
```

The **2 WARN**s are expected (dirty raw rows on staging). **ERROR=0** is required.  
Scroll the log for lines like `WARN 9 positive_value_stg_payments_...` and `WARN 8 not_null_if_stg_orders_...` — those names are what you inspect in §1e.

In later sections, always:

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh
```

---

## 1. Advanced testing

### Files

- `dbt_project/tests/generic/positive_value.sql`
- `dbt_project/tests/generic/not_null_if.sql`
- `dbt_project/models/staging/schema.yml`
- `dbt_project/models/intermediate/schema.yml`
- `dbt_project/models/intermediate/int_order_items_aggregated.sql`
- `dbt_project/models/intermediate/int_order_payments_aggregated.sql`
- `dbt_project/models/marts/schema.yml`

### Commands

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh
```

#### 1a. Foundations — run can succeed while some rows are dirty

```bash
dbt run --select stg_payments
dbt test --select stg_payments
```

**Expect:** model builds OK; one payment test **warns** (about 9 rows with `payment_value` = 0).

```text
Done. PASS=2 WARN=1 ERROR=0 SKIP=0 TOTAL=3
```

In the log you should also see a line like:

```text
WARN 9 positive_value_stg_payments_payment_value
```

That means: test name `positive_value` on model `stg_payments` column `payment_value`, and **9** rows broke the rule.  
Quick data check with **`dbt show`** (preview query results in the terminal — details in **§1e** Step 5):

```bash
dbt show --limit 10 --inline "select order_id, payment_value from {{ ref('stg_payments') }} where payment_value <= 0"
```

Use `--limit` on the command; do **not** put `LIMIT` inside the SQL.

**Expect (sample):**

```text
| ORDER_ID             | PAYMENT_VALUE |
| -------------------- | ------------- |
| 8bcbe01d44d147f90... |             0 |
| fa65dad1b0e818e3c... |             0 |
...
```

#### 1b. Built-in tests on a model

```bash
dbt test --select stg_customers
```

**Expect:** all pass (example: unique / not_null on `customer_id`).

```text
Done. PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4
```

#### 1c. Custom generic tests (by type + name)

```bash
dbt test --select "test_type:generic,test_name:positive_value"
dbt test --select "test_type:generic,test_name:not_null_if"
```

**Expect — `positive_value`:** most pass; staging payments still **warn**.

```text
Done. PASS=3 WARN=1 ERROR=0 SKIP=0 TOTAL=4
```

**Expect — `not_null_if`:** mart **passes** (dirty delivered rows filtered out); staging **warns** (~8 rows).

```text
Done. PASS=1 WARN=1 ERROR=0 SKIP=0 TOTAL=2
```

#### 1d. Tags — must-pass vs warn-only

```bash
dbt test --select tag:critical
dbt test --select tag:warn_only
dbt build --target dev
```

**`tag:critical`** = must-pass checks. **Expect no warnings:**

```text
Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3
```

**`tag:warn_only`** = warning-only checks (dirty raw data). There are **four** tests in this tag; typically **two** WARN (zero payments + delivered-null dates). The other two usually PASS. Summary still looks like:

```text
Done. PASS=2 WARN=2 ERROR=0 SKIP=0 TOTAL=4
```

**`dbt build --target dev` again:** same idea as smoke test — **ERROR=0**, **WARN=2** OK.

```text
Done. PASS=35 WARN=2 ERROR=0 SKIP=0 TOTAL=37
```

#### 1e. Interpret and validate a WARN (or FAIL)

When the summary shows WARN or ERROR, walk this path so you can **prove** what broke (same idea for FAIL in the optional fail→fix loop).

**Step 1 — Read the status line (not only the summary)**

Example from a real run:

```text
WARN 9 positive_value_stg_payments_payment_value
WARN 8 not_null_if_stg_orders_order_delivered_customer_date__order_status__delivered
```

| Piece | Meaning |
|-------|---------|
| `WARN` / `FAIL` | Severity outcome for this test |
| `9` / `8` | How many rows the test returned (bad rows) |
| Name after that | Which test + model + column (and parameters for `not_null_if`) |

**Step 2 — Find the YAML config (why warn vs error)**

Open `models/staging/schema.yml` (and for mart: `models/marts/schema.yml`).

Look for:

- `positive_value` under `stg_payments.payment_value` → `severity: warn`, `tags: ["warn_only"]`
- `not_null_if` under `stg_orders.order_delivered_customer_date` → same warn / warn_only
- On **mart** `fct_orders`, the matching `not_null_if` / some `positive_value` use `severity: error` + `tags: ["critical"]`

Severity controls warn vs fail. Tags only choose **which** tests to run (`--select tag:...`).  
Staging still WARNs because dirty rows are present there. The mart test can still **pass** because those rows are removed in the model SQL (next step) — not because of the tag name.

**Step 3 — Read the generic test code (the rule)**

```bash
# from dbt_project/
less tests/generic/positive_value.sql
less tests/generic/not_null_if.sql
```

- `positive_value` selects rows where the column is not null and `<= 0`.
- `not_null_if` selects rows where `condition_column = condition_value` and the tested column **is null**.

The test “fails/warns” when that SELECT returns one or more rows.

**Step 4 — Open the compiled SQL (the exact query dbt ran)**

After any `dbt test` / `dbt build`, compiled tests land under `target/compiled/`:

```bash
# list compiled tests (names match the log)
find target/compiled -type f -name '*positive_value*stg_payments*' 2>/dev/null | head
find target/compiled -type f -name '*not_null_if*stg_orders*' 2>/dev/null | head
```

Open one file (editor or `less`). You should see plain SQL against `ANALYTICS_DEV` (or your schema) — no Jinja.  
That SQL is what Snowflake ran; the row count in the WARN line is how many rows it returned.

**Step 5 — Inspect the data (prove the rows exist)**

Use **`dbt show`** to run a small SQL preview **through dbt** (same profile / `ref()` as your models) and print a table in the terminal. It does **not** create a new model.

| Piece | Meaning |
|-------|---------|
| `dbt show` | Preview query results from the warehouse |
| `--inline "..."` | SQL string to run (can use `{{ ref('...') }}`) |
| `--limit N` | Cap how many rows are printed (**put limit here**, not as `LIMIT` inside the SQL — Snowflake errors if both wrap) |

Payments (zeros):

```bash
dbt show --limit 10 --inline "select order_id, payment_value from {{ ref('stg_payments') }} where payment_value <= 0"
```

Delivered with null delivery date:

```bash
dbt show --limit 10 --inline "select order_id, order_status, order_delivered_customer_date from {{ ref('stg_orders') }} where order_status = 'delivered' and order_delivered_customer_date is null"
```

You should see real rows (e.g. `PAYMENT_VALUE = 0`). That proves the WARN is about **data**, not a broken test definition.

Optional same checks in Snowflake worksheet (dev schema) — same idea, without dbt:

```sql
SELECT order_id, payment_value
FROM OLIST_DB.ANALYTICS_DEV.STG_PAYMENTS
WHERE payment_value <= 0;

SELECT order_id, order_status, order_delivered_customer_date
FROM OLIST_DB.ANALYTICS_DEV.STG_ORDERS
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NULL;
```

**Step 6 — Validate why the mart test still passes**

Open `models/marts/fct_orders.sql` — it **filters out** delivered rows with a null delivery date (and only keeps orders that join to items).  
So the same `not_null_if` rule on `fct_orders` finds **0** bad rows.

```bash
dbt show --limit 5 --inline "select order_id, order_status, order_delivered_customer_date from {{ ref('fct_orders') }} where order_status = 'delivered' and order_delivered_customer_date is null"
dbt test --select "test_type:generic,test_name:not_null_if"
```

**Expect:** empty (or no) bad rows on the mart; staging still WARNs; mart `not_null_if` PASSes.

Optional: `dbt test --select tag:critical` should also be green (`PASS=3 WARN=0 ERROR=0`) because those must-pass tests (including mart checks) have clean data.

**Quick checklist**

| Question | Where to look |
|----------|----------------|
| Did anything block the run? | Summary: `ERROR` must be 0 (unless you are in fail→fix) |
| Which test / how many rows? | WARN/FAIL line in the log |
| Warn or hard fail by design? | `schema.yml` → `severity` (`warn` / `error`) |
| Which group of tests to run? | `schema.yml` → `tags` + `--select tag:...` |
| What is the rule? | `tests/generic/*.sql` |
| Exact SQL that ran? | `target/compiled/...` |
| Are the dirty rows real? | `dbt show` (preview via dbt + `ref()`) or the same SQL in Snowflake |
| Why is the mart test still green? | `fct_orders.sql` removes those dirty rows — the mart test has nothing left to fail |

### Understanding `--select`, tags, and parameters

#### Why `--select`?

Without `--select`, `dbt test` runs **all** tests.  
With `--select`, you choose a **smaller set** (faster demos / clearer CI).

These words are **dbt selection methods** (not Snowflake SQL).

| Example | Plain meaning |
|---------|----------------|
| `dbt test --select stg_customers` | Tests for the **model** `stg_customers`. |
| `dbt test --select "test_type:generic,test_name:positive_value"` | All **generic** tests named **`positive_value`**. |
| `dbt test --select tag:critical` | Only tests tagged **critical** (must pass). |
| `dbt test --select tag:warn_only` | Only tests tagged **warn_only** (warnings OK). |

| Piece | Meaning |
|-------|---------|
| `test_type:generic` | Reusable tests (`tests/generic/` or built-ins like `not_null`). |
| `test_name:positive_value` | Name from `{% test positive_value ... %}`. |
| `test_name:not_null_if` | Name from `{% test not_null_if ... %}`. |
| `tag:...` | Label in YAML `tags:`. |
| `,` | **AND** (both must match). |
| `"..."` | Quotes so the shell does not break on the comma. |

#### Why tags? (`critical` vs `warn_only`)

| Tag | Plain meaning | If data breaks the rule |
|-----|----------------|-------------------------|
| `critical` | **Must pass** | Counts as **ERROR** → treat as a failed gate |
| `warn_only` | **Warning only** | Counts as **WARN** → continue; it is a heads-up |

So `dbt test --select tag:warn_only` means: “Show me the warn-only group.” Seeing WARN is **expected** for some Olist rows.

#### Why parameters?

A **generic** test is one reusable rule. **Parameters** in YAML change how that rule is applied.

Example — `not_null_if`: “this column must not be null **when** another column equals a value.”  
Parameters: `condition_column`, `condition_value` → here, when `order_status = delivered`, delivery date must not be null.

#### Severity vs tags

- **Tag** = which **group** to run (`--select tag:...`)  
- **Severity** in YAML (`error` / `warn`) = how hard a failure counts  

In this project: `critical` ↔ `severity: error`; `warn_only` ↔ `severity: warn`.

### Fail → fix (optional)

Use the same interpret path as **§1e**, but expect **FAIL / ERROR** instead of WARN.

1. Temporarily edit `tests/generic/positive_value.sql` so valid rows fail (e.g. change `<= 0` to `< 1000000`).  
2. `dbt test --select tag:critical` → expect **FAIL** and `ERROR > 0`.  
3. Read the FAIL line → open YAML / generic SQL / `target/compiled/` → `dbt show` the bad rows (§1e steps 1–5).  
4. Restore the original `positive_value.sql`.  
5. `dbt test --select tag:critical` → expect:

```text
Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3
```

---

## 2. CI/CD (GitHub Actions)

**Full guide:** [`cicd-and-deployment.md`](cicd-and-deployment.md)  
(two CI jobs: Build dev → Gate critical; one Deploy Prod job; three strategies; Snowflake proof).

```bash
cd ..   # if you are still inside dbt_project
git checkout -b practice/ci-check
git add -A
git commit -m "practice: ci check"
git push -u origin HEAD
```

PR → **dbt CI** (both jobs green; WARN on build OK). Merge `main` → **dbt Deploy Prod**.

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.FCT_ORDERS;  -- dev
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;      -- prod (after deploy)
```

---

## 3. Airflow + dbt Core

**Install (copy the three class DAGs first):** [`airflow-install.md`](airflow-install.md)  
**DAGs (use these three):** [`airflow-dags.md`](airflow-dags.md)

| Order | DAG id | Point of the demo |
|------:|--------|-------------------|
| 1 | `demo_schedule_retries` | Schedule + retries (no dbt) |
| 2 | `dbt_core_commands` | `run` → `tag:critical` → `build` → `docs generate` |
| 3 | `dbt_orchestrated_pipeline` | Layered run + critical gate + warn_only + publish |

```bash
export AIRFLOW_HOME=~/training/airflow_home
source ~/training/venvs/airflow/bin/activate
export DBT_BIN="$(pwd)/dbt_project/.venv/bin/dbt"
export DBT_PROJECT_DIR="$(pwd)/dbt_project"
export DBT_ENV_FILE="$HOME/.dbt/env.sh"

RUN_DATE="$(date -u +%Y-%m-%dT%H:%M:%S)"
airflow dags test demo_schedule_retries "$RUN_DATE"
airflow dags test dbt_core_commands "$RUN_DATE"
airflow dags test dbt_orchestrated_pipeline "$RUN_DATE"
```

`airflow dags test` runs a **DAG** once from the CLI — it is **not** `dbt test`. Full explanation: [`airflow-dags.md`](airflow-dags.md).

---

## 4. End-to-end

**Full walkthrough:** [`e2e-production-walkthrough.md`](e2e-production-walkthrough.md)

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh
dbt build --target dev
dbt test --select tag:critical
```

**Expect:** `PASS=35 WARN=2 ERROR=0` then `PASS=3 WARN=0 ERROR=0`.

Then CI/deploy ([`cicd-and-deployment.md`](cicd-and-deployment.md)), Snowflake two-schema counts, then Airflow DAG 1 → 2 → 3 ([`airflow-dags.md`](airflow-dags.md)). Star DAG: `dbt_orchestrated_pipeline`.
