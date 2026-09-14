#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <bucket-name> <aws-region> <aws-profile>" >&2
  exit 1
fi

BUCKET="$1"
REGION="$2"
PROFILE="$3"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
KEY="releases/helpdesk-api-${SHA}.tar.gz"

TARBALL="$(mktemp -t helpdesk-api-XXXXXX)"
trap 'rm -f "$TARBALL"' EXIT

git -C "$REPO_ROOT" archive --format=tar.gz --output "$TARBALL" HEAD

aws s3 cp "$TARBALL" "s3://${BUCKET}/${KEY}" --region "$REGION" --profile "$PROFILE" >&2

echo "$KEY"
