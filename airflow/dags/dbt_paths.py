"""Shared dbt path helpers for DAG 4 and DAG 5.

Why env vars?
  DAG .py files are copied into AIRFLOW_HOME/dags, so paths based on this
  file alone may not point at the git repo. Set these when starting Airflow:

  DBT_PROJECT_DIR  path to dbt_project/
  DBT_BIN          path to the dbt binary (dbt venv)
  DBT_ENV_FILE     shell file that exports Snowflake credentials
"""

from __future__ import annotations

import os
from pathlib import Path

# Fallback only if DAGs still sit inside the repo tree
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DBT_DIR = _REPO_ROOT / "dbt_project"
_DEFAULT_ENV = Path.home() / ".dbt" / "env.sh"
_DEFAULT_DBT_BIN = _REPO_ROOT / "dbt_project" / ".venv" / "bin" / "dbt"


def dbt_project_dir() -> str:
    """Folder that contains dbt_project.yml."""
    return os.environ.get("DBT_PROJECT_DIR", str(_DEFAULT_DBT_DIR))


def dbt_bin() -> str:
    """Full path to the dbt CLI."""
    return os.environ.get("DBT_BIN", str(_DEFAULT_DBT_BIN))


def dbt_env_file() -> str:
    """Shell file with Snowflake exports (sourced before every dbt call)."""
    return os.environ.get("DBT_ENV_FILE", str(_DEFAULT_ENV))


def dbt_bash(command: str) -> str:
    """Build one bash line: load env → cd project → run dbt <command>."""
    env_file = dbt_env_file()
    dbt_dir = dbt_project_dir()
    binary = dbt_bin()
    return (
        "set -euo pipefail; "  # stop on first error
        f"source {env_file}; "
        f"cd {dbt_dir}; "
        f"{binary} {command}"
    )
