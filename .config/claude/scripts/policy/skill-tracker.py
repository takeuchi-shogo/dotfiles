#!/usr/bin/env python3
"""Skill execution tracker — PostToolUse hook for Skill tool.

Skill tool が呼ばれた時に skill 名を自動記録する。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hook_utils import output_passthrough
from session_events import emit_skill_event


def main() -> None:
    data = json.loads(sys.stdin.read())

    tool_name = data.get("tool_name", "")
    if tool_name != "Skill":
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    skill_name = tool_input.get("skill", "")

    if skill_name:
        emit_skill_event(
            "invocation",
            {
                "skill_name": skill_name,
            },
        )

    output_passthrough(data)


if __name__ == "__main__":
    main()
