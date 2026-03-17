#!/usr/bin/env python3
"""Docker container safety hook (PreToolUse/Bash).

Blocks docker run/exec commands that lack safety flags:
- docker run without --rm (prevents container accumulation)
- docker run with --privileged (security risk)
"""

from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import load_hook_input, run_hook


def _has_rm_flag(command: str) -> bool:
    """Check if --rm is present as an actual flag (not in a string value).

    On shlex.split failure (malformed quotes), falls back to blocking
    (returns False) to err on the safe side.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False  # fail-closed: block when parsing is ambiguous
    return "--rm" in tokens


def _check_docker(data: dict) -> None:
    if data.get("tool_name") != "Bash":
        return

    command = data.get("tool_input", {}).get("command", "")
    if "docker" not in command:
        return

    # Check: docker run without --rm (re.DOTALL for multiline commands)
    if re.search(
        r"(?<![a-zA-Z0-9_-])docker\s+run(?=[^a-zA-Z0-9]|$)", command, re.DOTALL
    ) and not _has_rm_flag(command):
        print(
            "BLOCKED: docker run without --rm detected. Add --rm to auto-remove container after exit.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Check: docker with --privileged (re.DOTALL for multiline commands)
    if re.search(r"(?<![a-zA-Z0-9_-])docker\b.*?--privileged", command, re.DOTALL):
        print(
            "BLOCKED: Privileged Docker container detected. Remove --privileged flag.",
            file=sys.stderr,
        )
        sys.exit(2)


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    _check_docker(data)


if __name__ == "__main__":
    run_hook("docker-safety", main, fail_closed=True)
