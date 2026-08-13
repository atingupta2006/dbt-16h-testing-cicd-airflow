# DBT 16 Hours — Advanced Testing, CI/CD & Airflow

Duration: **16 hours** (live) · After class: **self-paced hands-on** using this repo

Topics are limited to `course-content.txt`:

1. Custom generic tests and production-style test selection  
2. Git-based CI/CD and simple `dev` → `prod` deployment  
3. Apache Airflow running dbt Core (`dbt run` / `dbt test`) with task dependencies  
4. End-to-end demo on the fixed Olist dataset  

## Who this repo is for

| During live training | After training |
|----------------------|----------------|
| Instructor demonstrates from this project | You clone and practice the same commands |

Trainer-only notes (Azure VM runbooks, timing, build plans) are **not** in this shared tree.

## Repository map

| Path | Purpose |
|------|---------|
| `dbt_project/` | dbt Core project (Olist) + custom generic tests |
| `airflow/dags/` | Airflow DAGs for the demos / practice |
| `.github/workflows/` | PR CI + main → prod deploy |
| `data/raw/` | Olist CSVs to load into Snowflake |
| `scripts/` | Snowflake bootstrap + Ubuntu venv helper |
| `GH/docs/` | Step-by-step practice guides (same flow as class demos) |

## Prerequisites

- Basic dbt (`ref`, models, built-in tests)
- Basic Git / pull requests
- A Snowflake account you can use for practice
- Linux recommended for Airflow (Ubuntu). Windows is fine for dbt-only practice.

## Quick start (after training)

1. Clone this repository.  
2. Create a Python venv and install dbt:

```bash
cd dbt_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copy `dbt_project/profiles.yml.example` to `~/.dbt/profiles.yml` and set Snowflake env vars (see [00 Setup](docs/00-setup.md)).  
4. Load `data/raw/*.csv` into `OLIST_DB.RAW` using `scripts/snowflake-setup.sql`.  
5. Run:

```bash
dbt debug
dbt build --target dev
```

6. Optional — Airflow: follow [03 Airflow integration](docs/03-airflow-integration.md).

## Practice guides

- [00 Setup](docs/00-setup.md)
- [01 Advanced testing](docs/01-advanced-testing.md)
- [02 CI/CD and deployment](docs/02-cicd-and-deployment.md)
- [03 Airflow integration](docs/03-airflow-integration.md)
- [04 E2E practice](docs/04-e2e-demonstration.md)
