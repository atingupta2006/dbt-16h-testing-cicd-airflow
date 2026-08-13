#!/usr/bin/env bash
# Run FROM your Windows/Git Bash (or WSL) machine — not on the VM.
# Syncs this repo to the VM and runs provision + e2e-verify over SSH.
#
# Required env (or edit defaults below):
#   VM_HOST=x.x.x.x
#   VM_USER=azureuser
#   SSH_KEY=$HOME/.ssh/id_ed25519   # or id_rsa
#
# Snowflake: place a local gitignored file internals/vm-env.sh then this script
# copies it to ~/.dbt/env.sh on the VM.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VM_HOST="${VM_HOST:?set VM_HOST}"
VM_USER="${VM_USER:-azureuser}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"
REMOTE_DIR="${REMOTE_DIR:-~/training/repos/dbt-16h}"
SKIP_AIRFLOW="${SKIP_AIRFLOW:-0}"

SSH=(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes "${VM_USER}@${VM_HOST}")
SCP=(scp -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes)

echo "==> sync repo -> ${VM_USER}@${VM_HOST}:${REMOTE_DIR}"
"${SSH[@]}" "mkdir -p $(dirname "$REMOTE_DIR") $REMOTE_DIR"
# Prefer rsync if available; else tar-over-ssh
if command -v rsync >/dev/null 2>&1; then
  rsync -az --delete \
    --exclude '.git/' \
    --exclude 'internals/' \
    --exclude '.venv/' \
    --exclude '**/target/' \
    --exclude '**/logs/' \
    -e "ssh -i $SSH_KEY -o IdentitiesOnly=yes" \
    "$ROOT/" "${VM_USER}@${VM_HOST}:${REMOTE_DIR}/"
else
  tar -C "$ROOT" \
    --exclude .git --exclude internals --exclude .venv \
    --exclude 'dbt_project/target' --exclude 'dbt_project/logs' \
    -czf - . | "${SSH[@]}" "mkdir -p $REMOTE_DIR && tar -C $REMOTE_DIR -xzf -"
fi

if [[ -f "$ROOT/internals/vm-env.sh" ]]; then
  echo "==> copy internals/vm-env.sh -> ~/.dbt/env.sh"
  "${SCP[@]}" "$ROOT/internals/vm-env.sh" "${VM_USER}@${VM_HOST}:.dbt-env.sh.tmp"
  "${SSH[@]}" 'mkdir -p ~/.dbt && mv ~/.dbt-env.sh.tmp ~/.dbt/env.sh && chmod 600 ~/.dbt/env.sh'
else
  echo "WARN: internals/vm-env.sh missing — dbt debug will fail until Snowflake env is on the VM"
fi

echo "==> provision"
"${SSH[@]}" "bash -lc 'cd $REMOTE_DIR && bash scripts/vm-provision.sh'"

echo "==> e2e-verify"
"${SSH[@]}" "bash -lc 'cd $REMOTE_DIR && SKIP_AIRFLOW=$SKIP_AIRFLOW bash scripts/e2e-verify.sh'"

echo "REMOTE_E2E_FINISHED"
