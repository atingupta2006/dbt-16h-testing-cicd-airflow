# DBT 16 Hours

Course project for advanced testing, GitHub Actions CI/CD, and Airflow with dbt Core.

**GitHub (use this repo only):** https://github.com/atingupta2006/dbt-16h-testing-cicd-airflow

## Contents

| Path | Purpose |
|------|---------|
| `dbt_project/` | dbt models (staging → intermediate → marts) and custom generic tests |
| `airflow/dags/` | Airflow DAGs used in class |
| `.github/workflows/` | PR CI and production deploy workflows |
| `handouts/student-commands.md` | Commands to follow along |
| `handouts/olist-data-and-flow.md` | Olist schema and end-to-end data flow |
| `handouts/airflow-install.md` | Install Airflow (separate venv) for class |
| `handouts/incremental-quick-look.md` | Concept only: how incremental models work (not a lab) |
| `course-content.txt` | Course topics |
| `.env.example` | Names of environment variables you will need |
| `dbt_project/profiles.yml.example` | Example dbt profile (`dev` / `prod`) |

## How to use

1. Open `handouts/olist-data-and-flow.md` for the dataset and pipeline picture.  
2. Open `handouts/student-commands.md` and follow the commands.  
3. For Airflow setup, use `handouts/airflow-install.md`.  
4. Use the connection details shared in class for Snowflake and related tools.
