# Olist data and end-to-end flow

This course uses a fixed **Olist** ecommerce dataset in Snowflake.  
Use this page to understand the tables, keys, and how data moves from raw load through dbt into the order fact you test and orchestrate.

**GitHub (use this repo only):** https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow  

Commands: [`student-commands.md`](student-commands.md)

---

## 1. What is Olist?

Olist is a Brazilian ecommerce marketplace dataset (public sample).  
RAW tables are **already loaded** in the class Snowflake account. You do not load CSVs in class. You still configure dbt (`profiles.yml` + `env.sh`) to connect.

| Item | Value |
|------|--------|
| Database | `OLIST_DB` |
| Raw schema | `RAW` |
| dbt `dev` schema | `ANALYTICS_DEV` |
| dbt `prod` schema | `ANALYTICS` |
| Grain of the main mart | **one row per order** (`fct_orders`) |

---

## 2. Raw tables (Snowflake `OLIST_DB.RAW`)

These are declared as dbt source `olist_raw` in `dbt_project/models/staging/sources.yml`.

| RAW table | Role | Important columns (as used in this project) |
|-----------|------|-----------------------------------------------|
| `customers` | Who bought | `customer_id`, `customer_unique_id`, `customer_city`, `customer_state` |
| `orders` | Order header | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_delivered_customer_date` |
| `order_items` | Line items on an order | `order_id`, `order_item_id`, `product_id`, `price`, `freight_value` |
| `payments` | Payments for an order | `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value` |
| `products` | Product attributes | `product_id`, `product_category_name`, dimensions / weight |

### How tables relate

```text
customers 1───* orders 1───* order_items *───1 products
                 │
                 └───* payments
```

- One **customer** can have many **orders** (`customer_id`).  
- One **order** can have many **order_items** and many **payments** (`order_id`).  
- Each **order_item** points to one **product** (`product_id`).

Typical order statuses in the data include: `delivered`, `shipped`, `canceled`, `unavailable`, `invoiced`, `processing`, `created`, `approved`.

### Data quality notes (why some tests WARN)

Real Olist rows are imperfect. In this project:

- A small number of `payment_value` values are `0` (staging **warn_only** / warn).  
- A small number of `delivered` orders have a null `order_delivered_customer_date` (staging **warn_only** / warn). Those rows are **not** kept in `fct_orders`, so the mart **critical** test can pass.

That is intentional: models can build successfully while some raw rows are still dirty.

---

## 3. dbt layers in this project

Models live under `dbt_project/models/`:

```text
RAW (source)
  → staging (stg_*)        source-aligned views (column subset)
  → intermediate (int_*)   order-grain aggregates
  → marts (fct_*)          business-facing fact table
```

### Staging (`models/staging/`)

| Model | Built from | Purpose |
|-------|------------|---------|
| `stg_customers` | `customers` | Customer attributes used on the fact |
| `stg_orders` | `orders` | Order header |
| `stg_order_items` | `order_items` | Item price / freight |
| `stg_payments` | `payments` | Payment amounts |
| `stg_products` | `products` | Present for completeness (not joined into `fct_orders` in this course) |

Staging mostly **selects the columns this project needs** from RAW. Materialized as **views**.

### Intermediate (`models/intermediate/`)

| Model | Built from | Purpose |
|-------|------------|---------|
| `int_order_items_aggregated` | `stg_order_items` | Per `order_id`: `total_order_value`, `total_freight_value` |
| `int_order_payments_aggregated` | `stg_payments` | Per `order_id`: `total_payment_value` |

These roll line-level rows up to **order grain** so the mart can join cleanly. Materialized as **views**.

### Marts (`models/marts/`)

| Model | Built from | Purpose |
|-------|------------|---------|
| `fct_orders` | `stg_orders` + `stg_customers` + both `int_*` | One row per order with customer context and totals |

`fct_orders`:

- **Inner-joins** item totals — orders with no line items are excluded.  
- **Left-joins** payments — `total_payment_value` can be null if there is no payment.  
- **Excludes** delivered orders that still have a missing delivery date, so the must-pass mart test can stay green.  

Materialized as a **table**.

Columns on `fct_orders`:

| Column | Meaning |
|--------|---------|
| `order_id` | Order key |
| `customer_id` | Buyer |
| `customer_city` / `customer_state` | From customer |
| `order_status` | Lifecycle status |
| `order_purchase_timestamp` | When purchased |
| `order_delivered_customer_date` | When delivered (may be null if not delivered) |
| `total_order_value` | Sum of item `price` |
| `total_freight_value` | Sum of item `freight_value` |
| `total_payment_value` | Sum of `payment_value` (null if no payments) |

---

## 4. End-to-end data flow (start → finish)

### A. Inside dbt (transform)

```text
OLIST_DB.RAW.*
        │
        ▼
   stg_*  (views)
        │
        ├── stg_order_items  → int_order_items_aggregated
        ├── stg_payments     → int_order_payments_aggregated
        ├── stg_orders ─────────────┐
        └── stg_customers ──────────┤
                                    ▼
                              fct_orders
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
     ANALYTICS_DEV.FCT_ORDERS            ANALYTICS.FCT_ORDERS
           (--target dev)                    (--target prod)
```

Useful commands:

```bash
dbt build --target dev          # writes into ANALYTICS_DEV
dbt build --target prod         # writes into ANALYTICS (separate copy)
```

### B. Quality gates (tests)

- **critical** (error) — must pass; blocks the build if they fail.  
- **warn_only** (warn) — useful to see (dirty raw rows); does not have to block the build.

### C. Delivery path used in class

```text
1. Snowflake RAW already loaded
2. dbt build --target dev                    → ANALYTICS_DEV
3. GitHub PR → dbt CI
      one job: dbt build --target dev         → ANALYTICS_DEV
      (critical tests gate the job inside build)
4. Merge to main → dbt Deploy Prod
      one job: dbt build --target prod         → ANALYTICS
5. Airflow
      example_* (if present)             → Airflow’s own samples
      demo_schedule_retries              → schedule + retries
      demo_task_order                    → task order
      demo_parallel_join                 → parallel Olist ingest → join
      dbt_core_commands                  → run / critical / build / docs
      dbt_orchestrated_pipeline          → layered run + gates + publish
```

Airflow does not replace dbt models; it **schedules** the same project (see [`airflow-dags.md`](airflow-dags.md)).

---

## 5. Quick mental model

| Question | Answer |
|----------|--------|
| Where does data start? | `OLIST_DB.RAW` |
| What does staging do? | Select needed columns into `stg_*` views |
| What does intermediate do? | Aggregate items/payments to order grain |
| What does the mart do? | Join + filter → `fct_orders` for consumers |
| What do students query most? | `OLIST_DB.ANALYTICS_DEV.FCT_ORDERS` for day-to-day / CI. `OLIST_DB.ANALYTICS.FCT_ORDERS` is the separate prod copy (built with `--target prod`). |
