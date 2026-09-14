#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <ip-or-host>" >&2
  exit 1
fi

HOST="$1"
URL="http://${HOST}:8000/health"

if BODY="$(curl -fsS --max-time 5 "$URL" 2>/dev/null)" && grep -q '"status":\s*"ok"' <<< "$BODY"; then
  echo "healthy"
  exit 0
fi

echo "not healthy yet"
exit 1
