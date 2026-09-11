#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
STUB_DIR="$(mktemp -d)"
AWS_LOG="${STUB_DIR}/aws_calls.log"
trap 'rm -rf "$STUB_DIR"' EXIT

# Stub `aws` on PATH: records the call instead of touching real AWS, and
# extracts the tarball it was asked to upload so we can inspect its contents.
cat > "${STUB_DIR}/aws" <<STUB
#!/usr/bin/env bash
echo "\$@" >> "${AWS_LOG}"
# args: s3 cp <tarball> s3://<bucket>/<key> --region <region>
cp "\$3" "${STUB_DIR}/uploaded.tar.gz"
STUB
chmod +x "${STUB_DIR}/aws"

export PATH="${STUB_DIR}:${PATH}"

OUTPUT_KEY="$("${REPO_ROOT}/infra/demo/scripts/build_and_publish.sh" test-bucket-123 us-east-1)"

# 1. The script printed a well-formed S3 key on stdout.
if [[ ! "$OUTPUT_KEY" =~ ^releases/helpdesk-api-[0-9a-f]{7,}\.tar\.gz$ ]]; then
  echo "FAIL: unexpected output key: $OUTPUT_KEY" >&2
  exit 1
fi

# 2. The stub `aws` was invoked with the expected bucket/key/region.
if ! grep -q "s3://test-bucket-123/${OUTPUT_KEY} --region us-east-1" "${AWS_LOG}"; then
  echo "FAIL: aws s3 cp was not called with the expected destination" >&2
  cat "${AWS_LOG}" >&2
  exit 1
fi

# 3. The tarball contains runtime files and excludes .git and venv.
TAR_LIST="$(tar tzf "${STUB_DIR}/uploaded.tar.gz")"
for expected in "run.py" "requirements-runtime.txt"; do
  if ! grep -q "$expected" <<< "$TAR_LIST"; then
    echo "FAIL: tarball is missing $expected" >&2
    exit 1
  fi
done
if grep -q "^\.git/" <<< "$TAR_LIST"; then
  echo "FAIL: tarball contains .git/" >&2
  exit 1
fi

echo "PASS"
