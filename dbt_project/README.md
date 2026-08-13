# olist_dbt_project

Fixed Olist dataset project for the 16-hour advanced testing / CI/CD / Airflow course.

## Layout

- `models/staging/` — source-aligned views  
- `models/marts/fct_orders.sql` — order-grain fact  
- `tests/generic/` — custom generic tests (`positive_value`, `not_null_if`)

## Commands

```bash
source .venv/bin/activate
source ~/.dbt/env.sh
dbt build --target dev
dbt test --select tag:every_build
dbt build --target prod
```
