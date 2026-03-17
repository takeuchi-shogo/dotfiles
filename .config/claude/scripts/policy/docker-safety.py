#!/usr/bin/env python3
"""Docker container safety hook.

Blocks docker run/exec commands that lack safety flags:
- docker run without --rm (prevents container accumulation)
- docker run with --privileged (security risk)
"""

import json
import re
import sys

CHECKS = [
    (
        lambda cmd: bool(re.search(r"\bdocker\s+run\b", cmd)) and "--rm" not in cmd,
        "docker run without --rm detected. Add --rm to auto-remove container after exit.",
    ),
    (
        lambda cmd: bool(re.search(r"\bdocker\b.*--privileged", cmd)),
        "Privileged Docker container detected. Remove --privileged flag.",
    ),
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    if data.get("tool_name") != "Bash":
        return

    command = data.get("tool_input", {}).get("command", "")
    if "docker" not in command:
        return

    for check_fn, message in CHECKS:
        if check_fn(command):
            print(f"BLOCKED: {message}", file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()
