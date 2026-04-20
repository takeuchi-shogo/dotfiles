#!/usr/bin/env python3
"""Plan→Implement bridge advisory hook.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input on stdin
Output: advisory message when Success Criteria is added/changed in PLANS.md
        or docs/plans/active/*.md. Always exit 0 (never blocks).

Classification: Semantic Advisory (ADR-0006).
Purpose: Prompt user to /grill-interview right after defining Success Criteria,
         when stress-testing the plan is highest-leverage.

Origin: "How I got banned from GitHub due to my harness pipeline" (2026-04) —
        Plan→Implement boundary is where attestation pipelines fail silently.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    check_tool,
    load_hook_input,
    output_context,
    output_passthrough,
    run_hook,
)

# match: any docs/plans/active/*.md (active plan files)
ACTIVE_PLAN_RE = re.compile(r"(^|/)docs/plans/active/[^/]+\.md$")
# match: exact "## Success Criteria" heading or success_criteria: frontmatter
TRIGGER_RE = re.compile(
    r"(^|\n)\s*(##\s+Success Criteria\s*$|success_criteria:)", re.MULTILINE
)
# Cap input to avoid 5s timeout on huge plan files (Success Criteria is in plan header)
TEXT_CAP_BYTES = 262_144


def _is_plan_file(file_path: str) -> bool:
    """Match repo-root PLANS.md or docs/plans/active/*.md.

    Excludes nested PLANS.md (e.g. docs/plans/PLANS.md) to avoid false positives.
    """
    if not file_path:
        return False
    if ACTIVE_PLAN_RE.search(file_path):
        return True
    # repo-root PLANS.md only: filename is PLANS.md AND parent is not under docs/plans
    p = Path(file_path)
    if p.name == "PLANS.md" and "docs/plans" not in str(p.parent).replace("\\", "/"):
        return True
    return False


def _changed_text(tool_input: dict) -> str:
    # Edit uses new_string, Write uses content. Empty new_string = deletion (skip).
    raw = tool_input.get("new_string") or tool_input.get("content") or ""
    return raw[:TEXT_CAP_BYTES]


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    if not (check_tool(data, "Edit") or check_tool(data, "Write")):
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not _is_plan_file(file_path):
        output_passthrough(data)
        return

    text = _changed_text(tool_input)
    if not TRIGGER_RE.search(text):
        output_passthrough(data)
        return

    advisory = (
        "[advisory] Success Criteria を更新しました。\n"
        "Plan→Implement の境界です。実装に入る前に /grill-interview で\n"
        "Plan のストレステスト (前提・抜け・撤退条件) を推奨します。\n"
        "(advisory only — block しません。ADR-0006 Semantic Advisory 分類)"
    )
    output_context("PostToolUse", advisory)


if __name__ == "__main__":
    run_hook("plan-implement-bridge", main, fail_closed=False)
