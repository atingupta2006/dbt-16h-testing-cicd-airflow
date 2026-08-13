#!/usr/bin/env bash
# One-shot Ubuntu VM provision for this course (idempotent-ish).
# Run on the VM from the repo root:  bash scripts/vm-provision.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRAINING_ROOT="${TRAINING_ROOT:-$HOME/training}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> [1/4] apt packages"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  python3 python3-pip python3-venv python3-dev build-essential \
  git curl ca-certificates libpq-dev tmux >/dev/null

echo "==> [2/4] dirs"
mkdir -p "$TRAINING_ROOT/venvs" "$TRAINING_ROOT/airflow_home/dags" "$HOME/.dbt"

echo "==> [3/4] dbt venv"
if [[ ! -x "$TRAINING_ROOT/venvs/dbt/bin/dbt" ]]; then
  "$PYTHON_BIN" -m venv "$TRAINING_ROOT/venvs/dbt"
  # shellcheck disable=SC1091
  source "$TRAINING_ROOT/venvs/dbt/bin/activate"
  python -m pip install -q --upgrade pip
  pip install -q "dbt-core==1.9.8" "dbt-snowflake==1.9.4"
  deactivate
fi
"$TRAINING_ROOT/venvs/dbt/bin/dbt" --version | head -n 3

echo "==> [4/4] airflow venv"
if [[ ! -x "$TRAINING_ROOT/venvs/airflow/bin/airflow" ]]; then
  "$PYTHON_BIN" -m venv "$TRAINING_ROOT/venvs/airflow"
  # shellcheck disable=SC1091
  source "$TRAINING_ROOT/venvs/airflow/bin/activate"
  python -m pip install -q --upgrade pip
  PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  pip install -q "apache-airflow==2.9.3" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PY_MM}.txt"
  deactivate
fi
"$TRAINING_ROOT/venvs/airflow/bin/airflow" version

if [[ ! -f "$HOME/.dbt/profiles.yml" ]]; then
  cp "$REPO_ROOT/dbt_project/profiles.yml.example" "$HOME/.dbt/profiles.yml"
  echo "NOTE: wrote ~/.dbt/profiles.yml from example — set ~/.dbt/env.sh before dbt debug"
fi

# Symlink DAGs
for f in "$REPO_ROOT"/airflow/dags/*.py; do
  ln -sfn "$f" "$TRAINING_ROOT/airflow_home/dags/$(basename "$f")"
done

echo "PROVISION_OK repo=$REPO_ROOT"
