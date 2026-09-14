#!/usr/bin/env python3
"""PreToolUse hook: hard-blocks destructive terraform/aws commands for the
course demo. Claude may plan and apply; only the human operator destroys."""

import json
import re
import sys

BLOCK_PATTERNS = [
    re.compile(r"\bterraform\s+destroy\b"),
    re.compile(r"\bterraform\s+apply\b[^\n]*\s-destroy\b"),
    re.compile(r"\baws\b[^\n]*\b(terminate-instances|delete-bucket|delete-object|"
                r"delete-objects|delete-role|delete-instance-profile|"
                r"delete-security-group|deregister-image)\b"),
    # `aws s3` has friendly-name subcommands that don't spell out the
    # underlying API verb (e.g. `s3 rb` calls DeleteBucket) — caught this
    # bypassing the pattern above during a live rehearsal.
    re.compile(r"\baws\s+s3\s+rb\b"),
]

# Strips single- and double-quoted substrings (e.g. commit messages, -m
# "...") before pattern matching, so mentioning "terraform destroy" in a
# string literal doesn't get treated as running the command.
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")


def _unquoted(command: str) -> str:
    return _QUOTED.sub("", command)


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    inspectable = _unquoted(command)

    for pattern in BLOCK_PATTERNS:
        if pattern.search(inspectable):
            print(
                "Blocked by the course-demo governance hook: "
                f"'{command}' matches a destructive pattern. "
                "Destroy actions for this demo are run manually by the "
                "operator, outside Claude.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
