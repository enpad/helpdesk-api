#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CHECK="${REPO_ROOT}/infra/demo/scripts/check_health.sh"

# 1. Nothing listening yet: expect failure.
if "$CHECK" 127.0.0.1; then
  echo "FAIL: expected check_health.sh to fail with no server running" >&2
  exit 1
fi

# 2. Start the real app locally on 127.0.0.1:8000, using a throwaway venv
#    with the same pinned runtime deps the EC2 instance installs (the repo's
#    dev environment does not have fastapi/uvicorn installed by default).
VENV_DIR="$(mktemp -d)"
python3 -m venv "$VENV_DIR"
"${VENV_DIR}/bin/pip" install --quiet -r "${REPO_ROOT}/infra/demo/requirements-runtime.txt"

cd "$REPO_ROOT"
HELPDESK_HOST=127.0.0.1 HELPDESK_PORT=8000 "${VENV_DIR}/bin/python" run.py &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$VENV_DIR"' EXIT

for _ in $(seq 1 30); do
  if "$CHECK" 127.0.0.1; then
    break
  fi
  sleep 0.5
done

if ! "$CHECK" 127.0.0.1; then
  echo "FAIL: expected check_health.sh to succeed once the server is up" >&2
  exit 1
fi

echo "PASS"
