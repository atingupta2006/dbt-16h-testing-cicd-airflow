#!/usr/bin/env bash
# End-to-end verify on the VM. Prints compact PASS/FAIL lines. Exit 0 only if all required checks pass.
# Usage (on VM, repo root):  bash scripts/e2e-verify.sh
# Optional: SKIP_AIRFLOW=1 bash scripts/e2e-verify.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRAINING_ROOT="${TRAINING_ROOT:-$HOME/training}"
DBT_BIN="${DBT_BIN:-$TRAINING_ROOT/venvs/dbt/bin/dbt}"
AF_BIN="${AF_BIN:-$TRAINING_ROOT/venvs/airflow/bin/airflow}"
SKIP_AIRFLOW="${SKIP_AIRFLOW:-0}"
FAILS=0

pass() { echo "PASS  $*"; }
fail() { echo "FAIL  $*"; FAILS=$((FAILS + 1)); }

echo "=== e2e-verify $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

# --- env ---
if [[ -f "$HOME/.dbt/env.sh" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/.dbt/env.sh"
  pass "sourced ~/.dbt/env.sh"
else
  fail "missing ~/.dbt/env.sh"
fi

if [[ -f "$HOME/.dbt/profiles.yml" ]]; then
  pass "profiles.yml present"
else
  fail "missing ~/.dbt/profiles.yml"
fi

if [[ -x "$DBT_BIN" ]]; then
  pass "dbt binary $DBT_BIN"
else
  fail "dbt binary missing ($DBT_BIN)"
fi

# --- dbt ---
cd "$REPO_ROOT/dbt_project"
export DBT_PROFILES_DIR="${DBT_PROFILES_DIR:-$HOME/.dbt}"

if "$DBT_BIN" debug 2>&1 | tee /tmp/dbt-debug.txt | tail -n 5; then
  if grep -q "All checks passed" /tmp/dbt-debug.txt || grep -qi "Connection test:.*OK" /tmp/dbt-debug.txt; then
    pass "dbt debug"
  else
    # dbt 1.9 may still exit 0; require OK text
    if grep -qi "ok" /tmp/dbt-debug.txt; then
      pass "dbt debug (ok seen)"
    else
      fail "dbt debug — see /tmp/dbt-debug.txt"
    fi
  fi
else
  fail "dbt debug exited non-zero"
fi

if "$DBT_BIN" build --target dev 2>&1 | tee /tmp/dbt-build.txt | tail -n 20; then
  if grep -Eqi "Completed successfully|Done\\." /tmp/dbt-build.txt || grep -Eqi "PASS=|ERROR=0" /tmp/dbt-build.txt; then
    pass "dbt build --target dev"
  else
    # accept exit 0 as success if no ERROR=
    if grep -Eqi "ERROR=[1-9]" /tmp/dbt-build.txt; then
      fail "dbt build had errors"
    else
      pass "dbt build --target dev (exit 0)"
    fi
  fi
else
  fail "dbt build --target dev"
fi

if "$DBT_BIN" test --target dev --select tag:every_build 2>&1 | tee /tmp/dbt-test-critical.txt | tail -n 15; then
  if grep -Eqi "ERROR=[1-9]|Failing" /tmp/dbt-test-critical.txt; then
    fail "critical tests"
  else
    pass "dbt test tag:every_build"
  fi
else
  fail "dbt test tag:every_build"
fi

# --- airflow (optional) ---
if [[ "$SKIP_AIRFLOW" == "1" ]]; then
  pass "airflow skipped (SKIP_AIRFLOW=1)"
else
  if [[ -x "$AF_BIN" ]]; then
    export AIRFLOW_HOME="${AIRFLOW_HOME:-$TRAINING_ROOT/airflow_home}"
    mkdir -p "$AIRFLOW_HOME/dags"
    for f in "$REPO_ROOT"/airflow/dags/*.py; do
      ln -sfn "$f" "$AIRFLOW_HOME/dags/$(basename "$f")"
    done
    # Ensure metadata DB exists without starting full UI long-running
    if "$AF_BIN" db migrate >/tmp/af-migrate.txt 2>&1; then
      pass "airflow db migrate"
    else
      fail "airflow db migrate"
    fi
    if "$AF_BIN" dags list 2>/tmp/af-dags-err.txt | tee /tmp/af-dags.txt | grep -q "dbt_core_e2e_pipeline"; then
      pass "DAG dbt_core_e2e_pipeline listed"
    else
      fail "DAG dbt_core_e2e_pipeline not listed"
      tail -n 20 /tmp/af-dags-err.txt || true
    fi
    if "$AF_BIN" dags list 2>/dev/null | grep -q "dbt_core_run_test"; then
      pass "DAG dbt_core_run_test listed"
    else
      fail "DAG dbt_core_run_test not listed"
    fi
  else
    fail "airflow binary missing"
  fi
fi

echo "=== summary fails=$FAILS ==="
if [[ "$FAILS" -gt 0 ]]; then
  exit 1
fi
echo "E2E_OK"
exit 0
