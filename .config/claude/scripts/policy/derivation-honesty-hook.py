#!/usr/bin/env python3
"""Derivation honesty hook — detects FM-016 (Result Fabrication) banned phrases.

Triggered by: hooks.PostToolUse (Bash|Write|Edit)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext warning on stdout

Detects step-skipping, unverified claims, and unsupported generalizations
per derivation-honesty.md principles. Four categories:
  1. Unverified Confirmation — "confirmed", "verified" without evidence
  2. Step Skipping — "this becomes", "for consistency" hiding reasoning gaps
  3. Unsupported Generalization — "generally", "typically" without citation
  4. Obvious Justification — "obvious", "self-explanatory" blocking scrutiny

False positive suppression: Category 1 is skipped for Bash tool when the
command contains test/verification keywords (test, check, verify, lint,
pytest, go test, npm test).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    check_tool,
    get_emitter,
    load_hook_input,
    output_context,
    output_passthrough,
    run_hook,
)

emit = get_emitter()

# --- Constants ---

# Note: \b は日本語で誤動作するため lookaround を使用
CATEGORIES: dict[str, list[re.Pattern[str]]] = {
    "unverified_confirmation": [
        re.compile(r"(?<![a-zA-Z])confirmed(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"(?<![a-zA-Z])verified(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"確認しました"),
        re.compile(r"検証済み"),
    ],
    "step_skipping": [
        re.compile(r"(?<![a-zA-Z])this becomes(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"(?<![a-zA-Z])for consistency(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"これは[^\n]{0,20}になります"),
        re.compile(r"整合性のため"),
    ],
    "unsupported_generalization": [
        re.compile(r"(?<![a-zA-Z])generally(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"(?<![a-zA-Z])typically(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"一般的には"),
        re.compile(r"通常は"),
    ],
    "obvious_justification": [
        re.compile(r"(?<![a-zA-Z])obvious(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"(?<![a-zA-Z])obviously(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"(?<![a-zA-Z])self-explanatory(?![a-zA-Z])", re.IGNORECASE),
        re.compile(r"自明"),
        re.compile(r"言うまでもな"),
    ],
}

CATEGORY_LABELS: dict[str, str] = {
    "unverified_confirmation": "未検証の確認表現",
    "step_skipping": "ステップ飛ばし表現",
    "unsupported_generalization": "根拠なき一般化",
    "obvious_justification": "自明性による正当化",
}

# Commands that legitimately produce "confirmed"/"verified" output
_VERIFICATION_CMD_PATTERN = re.compile(
    r"(?<![a-zA-Z])(?:test|check|verify|lint|pytest|go\s+test|npm\s+test)(?![a-zA-Z])",
    re.IGNORECASE,
)


# --- Detection Logic ---


def _is_verification_command(tool_input: dict) -> bool:
    """Check if the Bash command is a test/verification command."""
    command = tool_input.get("command", "")
    return bool(_VERIFICATION_CMD_PATTERN.search(command))


def _detect_banned_phrases(
    tool_output: str, skip_categories: set[str]
) -> tuple[str, str, str] | None:
    """Scan tool_output for banned phrases across all categories.

    Returns (category_name, category_label, matched_text) or None.
    """
    for cat_name, patterns in CATEGORIES.items():
        if cat_name in skip_categories:
            continue
        for pattern in patterns:
            match = pattern.search(tool_output)
            if match:
                return (cat_name, CATEGORY_LABELS[cat_name], match.group(0))
    return None


# --- Main ---


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    if not (
        check_tool(data, "Bash")
        or check_tool(data, "Write")
        or check_tool(data, "Edit")
    ):
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    tool_output = data.get("tool_output", "") or ""

    # False positive suppression: skip Category 1 for Bash verification commands
    skip_categories: set[str] = set()
    if check_tool(data, "Bash") and _is_verification_command(tool_input):
        skip_categories.add("unverified_confirmation")

    result = _detect_banned_phrases(tool_output, skip_categories)
    if result:
        cat_name, cat_label, matched_text = result
        warning = (
            f"[DERIVATION_HONESTY_WARNING] "
            f"FM-016 検出 — カテゴリ: {cat_label} ({cat_name}), "
            f"マッチ: '{matched_text}'. "
            f"根拠のない断定・ステップ飛ばし・未検証の確認を避け、"
            f"推論過程を明示してください。"
        )
        emit(
            "pattern",
            {
                "type": "derivation_honesty_violation",
                "category": cat_name,
                "pattern": matched_text,
            },
        )
        output_context("PostToolUse", warning)
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("derivation-honesty-hook", main, fail_closed=True)
