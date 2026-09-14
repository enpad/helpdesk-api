#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

VENV_DIR="$(mktemp -d)"
python3 -m venv "$VENV_DIR"
"${VENV_DIR}/bin/pip" install --quiet -r "${REPO_ROOT}/infra/demo/requirements-runtime.txt" requests

cd "$REPO_ROOT"
HELPDESK_HOST=127.0.0.1 HELPDESK_PORT=8000 "${VENV_DIR}/bin/python" run.py &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$VENV_DIR"' EXIT

for _ in $(seq 1 30); do
  if "${REPO_ROOT}/infra/demo/scripts/check_health.sh" 127.0.0.1; then
    break
  fi
  sleep 0.5
done

HELPDESK_BASE_URL=http://127.0.0.1:8000 "${VENV_DIR}/bin/python" \
  "${REPO_ROOT}/infra/demo/scripts/seed_tickets.py" 20

SUMMARY="$(curl -fsS http://127.0.0.1:8000/tickets/stats/summary)"
echo "$SUMMARY"

TOTAL="$(echo "$SUMMARY" | python3 -c 'import json,sys; print(json.load(sys.stdin)["total"])')"
# 4 tickets already exist from the app's own startup seed data (app/storage/seed_data.py).
if [[ "$TOTAL" -lt 24 ]]; then
  echo "FAIL: expected at least 24 tickets total (4 startup + 20 seeded), got $TOTAL" >&2
  exit 1
fi

UNASSIGNED="$(echo "$SUMMARY" | python3 -c 'import json,sys; print(json.load(sys.stdin)["unassigned"])')"
if [[ "$UNASSIGNED" -eq "$TOTAL" ]]; then
  echo "FAIL: expected some tickets to be assigned to agents, all $TOTAL are unassigned" >&2
  exit 1
fi

echo "PASS"
