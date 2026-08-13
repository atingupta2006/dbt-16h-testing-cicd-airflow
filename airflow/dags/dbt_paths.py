"""Shared path defaults for demo DAGs.

Override with env vars on any machine:

  DBT_PROJECT_DIR  absolute path to dbt_project/
  DBT_BIN          absolute path to dbt executable in the dbt venv
  DBT_ENV_FILE     shell file that exports Snowflake env vars
"""

from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DBT_DIR = _REPO_ROOT / "dbt_project"
_DEFAULT_ENV = Path.home() / ".dbt" / "env.sh"
_DEFAULT_DBT_BIN = _REPO_ROOT / "dbt_project" / ".venv" / "bin" / "dbt"


def dbt_project_dir() -> str:
    return os.environ.get("DBT_PROJECT_DIR", str(_DEFAULT_DBT_DIR))


def dbt_bin() -> str:
    return os.environ.get("DBT_BIN", str(_DEFAULT_DBT_BIN))


def dbt_env_file() -> str:
    return os.environ.get("DBT_ENV_FILE", str(_DEFAULT_ENV))


def dbt_bash(command: str) -> str:
    """Build a bash snippet that loads env and runs a dbt CLI command."""
    env_file = dbt_env_file()
    dbt_dir = dbt_project_dir()
    binary = dbt_bin()
    return (
        "set -euo pipefail; "
        f"source {env_file}; "
        f"cd {dbt_dir}; "
        f"{binary} {command}"
    )
