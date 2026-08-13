# DBT 16 Hours

Course project for advanced testing, GitHub Actions CI/CD, and Airflow with dbt Core.

**GitHub (use this repo only):** https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow

## Contents

| Path | Purpose |
|------|---------|
| `dbt_project/` | dbt models (staging → intermediate → marts) and custom generic tests |
| `airflow/dags/` | Airflow DAGs used in class |
| `.github/workflows/` | PR CI and production deploy workflows |
| `handouts/README.md` | Handout reading order |
| `handouts/student-commands.md` | Command index |
| `handouts/olist-data-and-flow.md` | Olist schema and data flow |
| `handouts/cicd-and-deployment.md` | GitHub Actions CI + prod deploy |
| `handouts/airflow-install.md` | Install Airflow (separate venv) |
| `handouts/airflow-dags.md` | Class DAGs (schedule, dbt commands, orchestration) |
| `handouts/e2e-production-walkthrough.md` | End-to-end session order |
| `handouts/incremental-quick-look.md` | Incremental models (short example) |
| `course-content.txt` | Course topics |
| `.env.example` | Names of environment variables you will need |
| `dbt_project/profiles.yml.example` | Example dbt profile (`dev` / `prod`) |

## How to use

1. Open `handouts/README.md` for reading order, then `olist-data-and-flow.md`.  
2. Open `handouts/student-commands.md` as the command index.  
3. CI/CD: `handouts/cicd-and-deployment.md`. Airflow: `handouts/airflow-install.md` then `handouts/airflow-dags.md`.  
4. Use the connection details shared in class for Snowflake and related tools.
