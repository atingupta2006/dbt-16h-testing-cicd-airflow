# Incremental models

A **table** rebuilds the whole model on every `dbt run`.  
An **incremental** model keeps the table and, on later runs, loads only new or changed rows.

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

select
    order_id,
    customer_id,
    order_status,
    updated_at
from {{ source('raw', 'orders') }}

{% if is_incremental() %}
  where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

| Piece | Meaning |
|-------|---------|
| `materialized='incremental'` | Keep the table; do not rebuild from scratch every time |
| `unique_key='order_id'` | Match rows for insert vs update |
| `is_incremental()` | `false` on the first run; `true` when the table already exists |
| `{{ this }}` | This model’s table (e.g. to read `max(updated_at)`) |

| Run | `is_incremental()` | Behavior |
|-----|--------------------|----------|
| First | false | `{% if %}` skipped → load all rows |
| Later | true | `{% if %}` applied → load only newer rows; merge by `unique_key` |
