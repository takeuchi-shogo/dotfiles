#!/usr/bin/env python3
"""Rationalization scanner — detects reviewer self-rationalization patterns.

Triggered by: hooks.PostToolUse (Agent)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext warning on stdout

Detects patterns where a reviewer finds a problem but then convinces itself
the issue is minor and approves anyway (FM-018 Evaluator Rationalization).
Scans for minimization expressions in both English and Japanese.

Note: \\b doesn't work with Japanese text boundaries. This hook uses
lookaround patterns consistent with gaming-detector.py conventions.
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
# English minimization patterns
_EN_PATTERNS = [
    r"(?<![a-zA-Z])minor\s+issue(?![a-zA-Z])",
    r"(?<![a-zA-Z])not\s+critical(?![a-zA-Z])",
    r"(?<![a-zA-Z])acceptable(?![a-zA-Z])",
    r"(?<![a-zA-Z])not\s+a\s+big\s+deal(?![a-zA-Z])",
    r"(?<![a-zA-Z])can\s+be\s+addressed\s+later(?![a-zA-Z])",
    r"(?<![a-zA-Z])low\s+priority\s+but(?![a-zA-Z])",
    r"(?<![a-zA-Z])not\s+a\s+blocker(?![a-zA-Z])",
    r"(?<![a-zA-Z])negligible(?![a-zA-Z])",
    r"(?<![a-zA-Z])trivial\s+issue(?![a-zA-Z])",
]

# Japanese minimization patterns
_JA_PATTERNS = [
    r"軽微",
    r"許容範囲",
    r"大きな問題ではない",
    r"後で対応",
    r"致命的ではない",
    r"ブロッカーではない",
    r"些細",
]

_MINIMIZATION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _EN_PATTERNS] + [
    re.compile(p) for p in _JA_PATTERNS
]

# Threshold: 1 occurrence triggers warning
MINIMIZATION_THRESHOLD = 1


# --- Detection Logic ---


def _detect_rationalization(tool_output: str) -> tuple[str, list[str]] | None:
    """Detect minimization expressions that indicate rationalization.

    Returns (warning_message, matched_texts) or None if no detection.
    """
    matched: list[str] = []
    for pattern in _MINIMIZATION_PATTERNS:
        for match in pattern.finditer(tool_output):
            matched.append(match.group(0).strip())

    if len(matched) < MINIMIZATION_THRESHOLD:
        return None

    unique_matches = list(dict.fromkeys(matched))  # preserve order, dedupe
    matches_display = ", ".join(f"'{m}'" for m in unique_matches[:5])

    warning = (
        f"[RATIONALIZATION_WARNING] レビューアーの出力に矮小化表現が検出されました: "
        f"{matches_display}。"
        f"問題を発見したにもかかわらず、自己説得で承認する "
        f"Evaluator Rationalization (FM-018) の兆候です。"
        f"指摘された問題が本当に軽微か、根拠を再確認してください。"
    )
    return warning, unique_matches


# --- Main ---


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    if not check_tool(data, "Agent"):
        output_passthrough(data)
        return

    tool_output = data.get("tool_output", "") or ""

    result = _detect_rationalization(tool_output)
    if result:
        warning, matched_texts = result
        emit(
            "pattern",
            {
                "type": "rationalization_detected",
                "pattern": matched_texts,
            },
        )

        # telemetry stream にも emit（staleness-detector / qa-tuning-analyzer が参照）
        try:
            from session_events import emit_event

            emit_event(
                "telemetry",
                {
                    "type": "rationalization_detected",
                    "hook_name": "rationalization-scanner",
                    "action_taken": True,
                    "pattern": matched_texts,
                },
            )
        except Exception as exc:
            emit("error", {"message": f"telemetry emit failed: {exc}"})

        output_context("PostToolUse", warning)
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("rationalization-scanner", main, fail_closed=True)
