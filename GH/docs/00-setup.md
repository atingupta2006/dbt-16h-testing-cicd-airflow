# 00 — Setup

Get the fixed Olist project building before the other practice guides.

**Assumption:** Snowflake already has `OLIST_DB.RAW` tables loaded with the course dataset (your trainer provides access). You do not need to learn warehouse bootstrap for this course.

## 1. dbt virtualenv

```bash
cd dbt_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
dbt --version
```

Pinned versions: `dbt-core==1.9.8`, `dbt-snowflake==1.9.4`.

## 2. Snowflake profile

```bash
mkdir -p ~/.dbt
cp profiles.yml.example ~/.dbt/profiles.yml
```

Create `~/.dbt/env.sh` (do not commit this file) using the connection values your trainer shared:

```bash
export SNOWFLAKE_ACCOUNT="..."
export SNOWFLAKE_USER="..."
export SNOWFLAKE_PASSWORD="..."
export SNOWFLAKE_ROLE="..."
export SNOWFLAKE_DATABASE="OLIST_DB"
export SNOWFLAKE_WAREHOUSE="..."
export SNOWFLAKE_SCHEMA_DEV="ANALYTICS_DEV"
export SNOWFLAKE_SCHEMA_PROD="ANALYTICS"
chmod 600 ~/.dbt/env.sh
source ~/.dbt/env.sh
```

## 3. Smoke test

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh

dbt debug
dbt build --target dev
```

Expected:

- Connection test OK  
- Staging models + `fct_orders` built in `ANALYTICS_DEV`  
- Critical tests (`tag:every_build`) pass; some `nightly` warns may appear on raw staging

Spot-check:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.FCT_ORDERS;
```
