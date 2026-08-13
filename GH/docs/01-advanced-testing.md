# 01 — Advanced testing (custom generic tests)

Practice the TOC items: custom **generic** tests and a simple production test strategy.

## Files

- `dbt_project/tests/generic/positive_value.sql`
- `dbt_project/tests/generic/not_null_if.sql`
- `dbt_project/models/staging/schema.yml`
- `dbt_project/models/marts/schema.yml`

## Steps

### A) Built-ins (brief)

```bash
cd dbt_project
source .venv/bin/activate
source ~/.dbt/env.sh
dbt test --select stg_customers
```

### B) Custom generic: `positive_value`

Read the test macro, then where YAML applies it (`stg_order_items.price`, `fct_orders.total_order_value`).

```bash
dbt test --select test_type:generic,test_name:positive_value
```

### C) Custom generic: `not_null_if`

Conditional rule: when `order_status = 'delivered'`, delivery timestamp must be present.

```bash
dbt test --select test_type:generic,test_name:not_null_if
```

Note: on staging this is `severity: warn` + `tag:nightly` because raw Olist has a few dirty delivered rows. On `fct_orders` it is a critical gate (`tag:every_build`) after the mart filters those rows.

### D) Production-style selection

**Every build (critical):**

```bash
dbt test --select tag:every_build
```

**Broader / nightly-style:**

```bash
dbt test --select tag:nightly
```

**Full suite:**

```bash
dbt test
```

### E) Fail → fix

1. Temporarily change `positive_value.sql` so valid rows fail (for example compare `< 1000000`).  
2. Run `dbt test --select tag:every_build` → expect failure.  
3. Revert the file → green again.
