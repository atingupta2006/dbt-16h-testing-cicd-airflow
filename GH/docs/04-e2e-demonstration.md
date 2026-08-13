# 04 — End-to-end practice

Chain the previous guides. Do not add new topics.

## Flow

1. `dbt build --target dev` green  
2. `dbt test --select tag:every_build` green  
3. GitHub Actions PR CI green (if you use GitHub)  
4. Optional: merge/deploy to `prod` target  
5. Airflow `dbt_core_e2e_pipeline` success

## Cheat sheet

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh

dbt build --target dev
dbt test --select tag:every_build
```

Snowflake:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.FCT_ORDERS;
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```
