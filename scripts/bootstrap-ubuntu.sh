#!/usr/bin/env bash
# Trainer helper: create dbt + airflow venvs with pinned installs on Ubuntu.
# Full narrative: internals/TRAINER-ENV-SETUP-UBUNTU-AZURE.md
set -euo pipefail

TRAINING_ROOT="${TRAINING_ROOT:-$HOME/training}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "$TRAINING_ROOT/venvs" "$TRAINING_ROOT/airflow_home/dags" "$HOME/.dbt"

echo "==> dbt venv"
"$PYTHON_BIN" -m venv "$TRAINING_ROOT/venvs/dbt"
# shellcheck disable=SC1091
source "$TRAINING_ROOT/venvs/dbt/bin/activate"
python -m pip install --upgrade pip
pip install "dbt-core==1.9.8" "dbt-snowflake==1.9.4"
dbt --version
deactivate

echo "==> airflow venv"
"$PYTHON_BIN" -m venv "$TRAINING_ROOT/venvs/airflow"
# shellcheck disable=SC1091
source "$TRAINING_ROOT/venvs/airflow/bin/activate"
python -m pip install --upgrade pip
PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
pip install "apache-airflow==2.9.3" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PY_MM}.txt"
airflow version
deactivate

echo "Done. Next: configure ~/.dbt/profiles.yml and ~/.dbt/env.sh, then airflow standalone."
