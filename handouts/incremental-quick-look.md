# Incremental models — quick look (concept only)

**Not a hands-on lab.** Use this page only to understand the idea while the instructor shows it.  
Your practical work stays on the normal staging → intermediate → marts project (`student-commands.md`).

---

## What problem does it solve?

A **table** materialization rebuilds the **whole** model every `dbt run`.

An **incremental** materialization keeps the existing table and, on later runs, loads **only new (or changed) rows**.

```text
Day 1 (first run)     → build full table from all history
Day 2 (next run)      → add/update only rows that are new since last run
Day 3                 → same idea again
```

Useful for large facts (orders, events) where a full rebuild is slow or expensive.

---

## Tiny example (toy, not in the course project)

Imagine a source of orders with an `updated_at` timestamp.

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
  -- On later runs only: skip rows already loaded
  where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

| Piece | Plain meaning |
|-------|----------------|
| `materialized='incremental'` | Keep the table; don’t rebuild from scratch every time |
| `unique_key='order_id'` | How dbt matches an incoming row to an existing row (update vs insert) |
| `is_incremental()` | `false` on the **first** run; `true` on later runs when the table already exists |
| `{{ this }}` | The incremental table itself (so you can read `max(updated_at)`) |
| `where updated_at > …` | “Only pull rows newer than what we already have” |

---

## First run vs later run

| Run | `is_incremental()` | What SQL does |
|-----|--------------------|---------------|
| **First** | false | The `{% if %}` block is **skipped** → select **all** rows → create/replace full table |
| **Later** | true | The `{% if %}` block is **included** → select only **new/changed** rows → merge into the existing table using `unique_key` |

```text
Source orders          Incremental table
─────────────          ─────────────────
order_id | updated_at   order_id | updated_at
A        | day1    →    A        | day1      (first run loads A, B)
B        | day1         B        | day1
C        | day2    →    C        | day2      (second run adds C only)
B        | day2    →    B        | day2      (second run updates B if unique_key matches)
```

---

## How this relates to *this* course project

The Olist mart `fct_orders` in this repo is a normal **`table`** (full rebuild). That is intentional for class: simple, easy to test, and the dataset is small.

Incremental is shown here as a **pattern** you will meet in production — not something you must build for the labs.

---

## Optional one-liner (instructor may show)

```bash
# Concept only — do not add this file to the course models for labs
# dbt run --select <incremental_model_name>
```

On the first run you would see a full load; on the next run, fewer rows processed (if the filter works and new data arrived).
