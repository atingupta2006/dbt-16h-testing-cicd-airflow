# End-to-end walkthrough (Olist + dbt Core + Airflow)

One chain: dataset → tests you already know → CI/deploy → Snowflake proof → Airflow.

**No new testing ideas** — reuse `critical` / `warn_only` from Module 1.

| Doc | When |
|-----|------|
| [`olist-data-and-flow.md`](olist-data-and-flow.md) | Dataset picture |
| [`cicd-and-deployment.md`](cicd-and-deployment.md) | PR CI + prod deploy |
| [`airflow-install.md`](airflow-install.md) | Airflow once |
| [`airflow-dags.md`](airflow-dags.md) | The three class DAGs |
| [`student-commands.md`](student-commands.md) | Command index |

---

## Checklist (follow in order)

### E1 — Dataset + tags (~20 min)

- Staging → intermediate → marts; `fct_orders` grain = one row per order.  
- `critical` = must pass. `warn_only` = heads-up on dirty RAW rows.

### E2 — Local dbt (~20 min)

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh
dbt build --target dev
dbt test --select tag:critical
```

**Expect:** `PASS=35 WARN=2 ERROR=0` then `PASS=3 WARN=0 ERROR=0`.

### E3 — CI/CD + three strategies (~45–50 min)

Follow [`cicd-and-deployment.md`](cicd-and-deployment.md): PR → one CI build → merge → Deploy Prod.

Say aloud: **dev vs prod schemas**, **gate before release**, **rebuild not move**.

### E4 — Snowflake (~15 min)

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.FCT_ORDERS;
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```

### E5 — Airflow tour (~35–40 min)

1. `demo_schedule_retries` (schedule + retries)  
2. `dbt_core_commands` (run → critical test; mention build + docs)

### E6 — Orchestration (~35–40 min)

Trigger `dbt_orchestrated_pipeline`. Graph: layers → critical → warn_only + docs → publish.

### E7 — Failure drill (~20 min)

Temporarily break a **critical** test (same idea as Module 1) → red CI or red `test_critical` → restore → green.

---

## One-sentence recap

Fixed Olist in Snowflake → dbt layers and tags → GitHub builds **dev** then gates **critical** → merge rebuilds **prod** → Airflow runs the same Core CLI in a layered DAG.
