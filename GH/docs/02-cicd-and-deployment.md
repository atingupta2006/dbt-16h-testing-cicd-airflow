# 02 — CI/CD workflows and deployment

Practice: Git-based CI/CD and a simple deployment strategy (`dev` vs `prod` targets).

## Files

- `.github/workflows/dbt-ci.yml` — runs on pull requests  
- `.github/workflows/dbt-deploy.yml` — runs on push to `main`  
- `dbt_project/profiles.yml.example` — `dev` and `prod` outputs

## GitHub secrets required

- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_ROLE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_SCHEMA_DEV`, `SNOWFLAKE_SCHEMA_PROD`

## Steps

### A) Open a PR and watch CI

```bash
git checkout -b practice/ci-check
# optional: make a small intentional mistake to see a red run
git add -A && git commit -m "practice: ci check"
git push -u origin HEAD
```

Open the PR → Actions → confirm `dbt CI` runs `dbt build` and `tag:every_build`.

### B) Fix if red, merge when green

### C) Deployment strategy

- **dev** target → `ANALYTICS_DEV` (local + PR CI)  
- **prod** target → `ANALYTICS` (after merge to `main`)

After merge, confirm:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```
# GHA CI smoke 2026-08-13T02:44:19Z
