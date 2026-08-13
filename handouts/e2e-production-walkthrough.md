# End-to-end walkthrough (Olist + dbt Core + Airflow)

One chain for the final module: **dataset → tests you already know → CI/deploy → Snowflake proof → Airflow**.

**No new testing ideas** — reuse `critical` / `warn_only` from Module 1. This walkthrough **connects** pieces you already practiced.

| Typical time | ~3–3.5 hours (with discussion) |
|--------------|--------------------------------|
| Repo | https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow |

### Companion docs (use when a step needs detail)

| Doc | When you need it |
|-----|------------------|
| [`olist-data-and-flow.md`](olist-data-and-flow.md) | Dataset layers and `fct_orders` grain |
| [`student-commands.md`](student-commands.md) | Exact commands and expect lines |
| [`cicd-and-deployment.md`](cicd-and-deployment.md) | PR CI, Deploy Prod, three strategies |
| [`airflow-install.md`](airflow-install.md) | First-time Airflow setup |
| [`airflow-dags.md`](airflow-dags.md) | Each class DAG (Graph → Trigger → Log) |

---

## Big picture

```text
Snowflake RAW (Olist)
        ↓
dbt Core: staging → intermediate → marts (+ critical / warn_only tests)
        ↓
GitHub:  PR → dbt CI (build → ANALYTICS_DEV)
         merge → Deploy Prod (build → ANALYTICS)
        ↓
Airflow: schedule / task order / parallel → dbt commands → layered orchestration
```

**What “done” looks like at the end**

| Proof | You can show |
|-------|----------------|
| Local | `dbt build --target dev` → `PASS=35 WARN=2 ERROR=0` |
| Tags | `tag:critical` → `PASS=3 WARN=0`; `tag:warn_only` may WARN |
| CI | Green **Build (dev)** on a PR |
| Deploy | Green **Deploy (prod)** after merge |
| Snowflake | Counts exist in both `ANALYTICS_DEV` and `ANALYTICS` |
| Airflow | Basics DAGs green; `dbt_orchestrated_pipeline` all green |

---

## E1 — Dataset + tags (~20 min)

**Goal:** One shared picture of the warehouse and why two tag groups exist.

**Why:** Later CI and Airflow do not invent new quality rules — they run the same tags.

### Talk through

1. **RAW** = source Olist tables in Snowflake (already loaded for class).  
2. **Staging → intermediate → marts** = dbt models that clean and join.  
3. **`fct_orders`** = one row per order (the mart you care about for demos).  
4. **`critical`** = must-pass (`severity: error`). Fail → gate fails.  
5. **`warn_only`** = heads-up on dirty RAW rows (`severity: warn`). WARN with `ERROR=0` is OK.

**Detail:** [`olist-data-and-flow.md`](olist-data-and-flow.md)

**Checkpoint:** You can say in one sentence: “Critical stops the pipeline; warn_only is a signal on known dirty data.”

---

## E2 — Local dbt refresh (~20–25 min)

**Goal:** Prove the project still builds on **dev** before touching GitHub or Airflow.

**Why:** If local is red, CI and Airflow will be red for the same reason.

### Steps

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh

dbt build --target dev
dbt test --select tag:critical
# optional: dbt test --select tag:warn_only
```

### Expect

| Command | Typical summary |
|---------|-----------------|
| `dbt build --target dev` | `Done. PASS=35 WARN=2 ERROR=0 SKIP=0 TOTAL=37` |
| `dbt test --select tag:critical` | `Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3` |
| `dbt test --select tag:warn_only` | often `PASS=2 WARN=2 ERROR=0` (dirty-row heads-up) |

**Checkpoint:** `ERROR=0` on build; critical has **zero** WARN.

**If red:** Fix locally first (see Module 1 / [`student-commands.md`](student-commands.md) §1). Do not open a PR yet.

---

## E3 — CI/CD + three strategies (~45–50 min)

**Goal:** Show Git-based CI on a PR, then prod deploy on merge — and name the three strategies out loud.

**Detail:** follow every click in [`cicd-and-deployment.md`](cicd-and-deployment.md). Below is the walkthrough spine only.

### Three strategies (say these while demos run)

| # | Strategy | Live proof |
|---|----------|------------|
| 1 | **Dev vs prod environments** | CI → `dev` / `ANALYTICS_DEV`. Deploy → `prod` / `ANALYTICS`. |
| 2 | **Gate = critical inside build** | Critical tests run inside `dbt build`. Fail → Actions job red. WARN alone can still be green. |
| 3 | **Promotion by rebuild** | Prod is **not** “move the table.” Deploy runs `dbt build --target prod` again into `ANALYTICS`. |

### Student git spine

```bash
# from repo root
git checkout -b practice/ci-check
# optional: tiny comment / whitespace so the PR has a real change
git add -A
git commit -m "practice: ci check"
git push -u origin HEAD
```

1. GitHub → **Compare & pull request** → create the PR.  
2. Wait for **dbt CI** → job **Build (dev)** → green.  
3. Open the log: you may see `WARN=2` and still green (`ERROR=0`).  
4. **Merge** the PR to `main`.  
5. **Actions** → **dbt Deploy Prod** → job **Deploy (prod)** → green.

### Workflow shape

```text
Pull Request  →  dbt CI     →  one job: Build (dev)   →  ANALYTICS_DEV
Merge to main →  Deploy Prod →  one job: Deploy (prod) →  ANALYTICS
```

**Checkpoint:** You saw **one** CI job and **one** deploy job — not a second “critical-only” Actions job. Critical already gated inside `dbt build`.

---

## E4 — Snowflake proof (~15 min)

**Goal:** Prove strategy 3 with two queries (two schemas, two copies of the mart).

```sql
-- After local build and/or CI
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.FCT_ORDERS;

-- After a successful Deploy Prod only
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```

| Result | Meaning |
|--------|---------|
| Both return a count | Dev and prod both have the mart |
| Prod query fails (`does not exist`) | Deploy never ran successfully yet — expected until E3 finishes green |

**Checkpoint:** Counts are not “moved”; they were **built** into each schema.

---

## E5 — Airflow tour (~40–45 min)

**Goal:** Learn Airflow vocabulary with small DAGs, then run dbt once from Airflow.

**Prerequisite:** Airflow installed and course DAGs copied — [`airflow-install.md`](airflow-install.md).  
**Per-DAG detail:** [`airflow-dags.md`](airflow-dags.md).

### How every DAG is run in class

1. Open Airflow UI → login.  
2. Click the DAG → **Graph**.  
3. **Trigger**.  
4. Click a green task → **Log**.

### Order (do not skip ahead)

| Step | DAG | What you learn |
|------|-----|----------------|
| 0 | `example_*` (if listed) | Airflow’s own sample DAGs (not in this repo) |
| 1 | `demo_schedule_retries` | Schedule + retries (no dbt) |
| 2 | `demo_task_order` | Linear order: `start >> process >> finish` |
| 3 | `demo_parallel_join` | Parallel `extract` / `transform`, then `load` |
| 4 | `dbt_core_commands` | Airflow runs dbt CLI: run → **critical** → build → docs |

On **DAG 4**, open the **`dbt_test_critical`** log and confirm something like:

```text
Done. PASS=3 WARN=0 ERROR=0
```

**Checkpoint:** You can explain schedule, retries, `>>`, parallel join, and “Airflow shells out to the same `dbt` you used locally.”

---

## E6 — Orchestration (~35–40 min)

**Goal:** One end-to-end DAG: layered run → hard gate → heads-up + docs → publish stub.

**DAG:** `dbt_orchestrated_pipeline`  
**Detail:** [`airflow-dags.md`](airflow-dags.md) (DAG 5)

### Graph (read this before Trigger)

```text
raw_data_ready → run_staging → run_intermediate → run_marts → test_critical
                     test_critical → test_warn_only → publish_ready
                     test_critical → docs_generate  → publish_ready
```

| Task | Role |
|------|------|
| `raw_data_ready` | Stub: RAW already in Snowflake for class |
| `run_staging` / `run_intermediate` / `run_marts` | `dbt run` per layer |
| `test_critical` | **Hard gate** — must stay green |
| `test_warn_only` | Heads-up — WARN OK if `ERROR=0` |
| `docs_generate` | `dbt docs generate` (runs in parallel with warn_only after critical) |
| `publish_ready` | Stub: “downstream may refresh” |

### Do

1. UI → `dbt_orchestrated_pipeline` → **Graph** (point at the arrows).  
2. **Trigger**.  
3. Open **`test_critical`** log → expect `PASS=3 WARN=0 ERROR=0`.  
4. Open **`test_warn_only`** log → expect WARN allowed (`PASS=2 WARN=2` typical).  
5. Confirm **`publish_ready`** is green only after both branches finish.

**CI vs this DAG (say once):** CI uses one `dbt build` (models + all tests). This DAG uses **layered `dbt run`**, then **separate** `tag:critical` and `tag:warn_only` tasks — same tags, different orchestration shape.

**Checkpoint:** All tasks green; you can narrate why critical sits before publish.

---

## E7 — Failure drill (~20 min)

**Goal:** Prove the gate: break **critical** → red; restore → green.

Use the same idea as Module 1 (temporarily break a **critical** test — severity error / `tag:critical`). Do **not** break only a warn_only test for this drill.

### Suggested path (pick one)

**A — Local / Airflow**

1. Break a critical test (or force bad mart data so a critical test fails).  
2. Re-run `dbt test --select tag:critical` → expect `ERROR > 0`.  
3. Or Trigger `dbt_orchestrated_pipeline` → **`test_critical`** red → pipeline stops before a clean publish story.  
4. Restore the change.  
5. Re-run → critical green again.

**B — CI (if time)**

1. Push a change that fails a critical check on a branch.  
2. PR → **Build (dev)** red.  
3. Revert / fix → PR green → merge only when green.

**Checkpoint:** Everyone saw at least one **red** critical path and one **restore to green**.

---

## One-page recap

| Stage | What happened |
|-------|----------------|
| Data | Fixed Olist in Snowflake RAW |
| dbt | Layers + `critical` / `warn_only` |
| GitHub | PR builds **dev**; merge rebuilds **prod** |
| Gate | Critical inside `dbt build` (CI) or as its own Airflow task |
| Airflow | Same Core CLI, scheduled and layered in a DAG |

**One sentence:** Fixed Olist in Snowflake → dbt layers and tags → GitHub builds **dev** then gates **critical** → merge rebuilds **prod** → Airflow runs the same Core CLI in a layered DAG.
