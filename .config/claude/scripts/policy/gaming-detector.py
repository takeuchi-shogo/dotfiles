#!/usr/bin/env python3
"""Gaming detector — detects specification gaming patterns in AutoEvolve.

Triggered by: hooks.PostToolUse (Skill)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext warning on stdout

Detects proxy metric divergence (Goodhart's Law), self-referential
improvement attempts, and single-metric evaluations per improve-policy
Rules 21-23.

Note: This is an initial implementation focused on proxy metric checks.
Future iterations will add assertion counting and scope narrowing detection.
Rule 23 (Metric Diversity) implemented — detects single-metric evaluations.
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
SCORE_JUMP_THRESHOLD = 5  # +5pp triggers Goodhart warning
MIN_METRIC_COUNT = 2  # Rule 23: require at least 2 distinct metrics
PROTECTED_FILES = [
    "improve-policy.md",
    "skill-benchmarks.jsonl",
    "benchmark-dimensions.md",
]
# Note: \b は日本語で誤動作するため lookaround を使用
IMPROVE_SKILL_PATTERNS = [
    re.compile(r"(?<![a-zA-Z])improve(?![a-zA-Z])", re.IGNORECASE),
    re.compile(r"(?<![a-zA-Z])autoevolve(?![a-zA-Z])", re.IGNORECASE),
    re.compile(r"(?<![a-zA-Z])evolve(?![a-zA-Z])", re.IGNORECASE),
]

# Rule 22: proximity pattern — edit indicator と protected file が 80 文字以内に共起
_EDIT_NEAR_FILE_PATTERN = re.compile(
    r"(?:Edit|Write|modified|updated|changed)\b.{0,80}(?:"
    + "|".join(re.escape(f) for f in PROTECTED_FILES)
    + r")|(?:"
    + "|".join(re.escape(f) for f in PROTECTED_FILES)
    + r").{0,80}(?:Edit|Write|modified|updated|changed)\b",
    re.IGNORECASE,
)


# --- Detection Logic ---


def _is_improve_related(tool_input: dict) -> bool:
    """Check if the skill invocation is related to AutoEvolve/improve."""
    skill_name = tool_input.get("skill", "")
    args = tool_input.get("args", "")
    text = f"{skill_name} {args}"
    return any(p.search(text) for p in IMPROVE_SKILL_PATTERNS)


def _detect_self_referential_edit(tool_output: str) -> str | None:
    """Rule 22: Detect attempts to modify evaluation criteria files.

    Limitation: This checks tool_output text for co-occurrence of edit
    indicators and protected file names within 80 chars. A more robust
    approach would be a separate PostToolUse(Edit|Write) hook checking
    tool_input.file_path directly.
    """
    match = _EDIT_NEAR_FILE_PATTERN.search(tool_output)
    if match:
        matched_text = match.group(0)
        protected = next(
            (f for f in PROTECTED_FILES if f in matched_text), "evaluation criteria"
        )
        return (
            f"[Gaming Detector] Rule 23 警告: "
            f"評価基準ファイル '{protected}' への変更が検出されました。"
            f"AutoEvolve が自身の評価基準を変更することは禁止されています。"
            f"評価基準の変更は人間の承認を必要とします。"
        )
    return None


def _parse_score_pair(before_str: str, after_str: str) -> tuple[float, float] | None:
    """Parse before/after score strings. Returns (before, after) or None."""
    try:
        return (float(before_str), float(after_str))
    except ValueError:
        return None


def _parse_single_delta(delta_str: str) -> float | None:
    """Parse a single delta string and return float, or None on failure."""
    try:
        return float(delta_str)
    except ValueError:
        return None


def _detect_single_metric(tool_output: str) -> str | None:
    """Rule 23: Detect evaluations relying on a single metric.

    When an improve/evolve result reports scores, check that multiple
    distinct metrics are present. Single-metric optimization is vulnerable
    to Goodhart's Law exploitation.

    Inspired by "Don't trust your agents" (0xSero & SarahXC):
    "If your only measure is 'gets things done fast,' you'll hire people
    who cut corners."
    """
    # Look for score/metric reporting patterns
    metric_patterns = [
        re.compile(
            r"(?:score|metric|accuracy|pass_rate|recall|precision|f1|bleu|rouge)\s*[=:]\s*[\d.]+",
            re.I,
        ),
        re.compile(r"checklist_pass_rate\s*[=:]\s*[\d.]+", re.I),
        re.compile(r"\b(?:improvement|delta|change)\s*[=:]\s*[+-]?[\d.]+", re.I),
    ]

    found_metrics: set[str] = set()
    for pattern in metric_patterns:
        for match in pattern.finditer(tool_output):
            # Extract the metric name (first word before = or :)
            text = match.group(0)
            name = re.split(r"\s*[=:]\s*", text)[0].strip().lower()
            found_metrics.add(name)

    # Only warn if we found exactly 1 metric (indicates evaluation happened
    # but with insufficient breadth). 0 metrics = not a scoring context.
    if len(found_metrics) == 1:
        metric_name = next(iter(found_metrics))
        return (
            f"[Gaming Detector] Rule 23 警告: "
            f"評価が単一メトリクス '{metric_name}' のみに依存しています。"
            f"少なくとも {MIN_METRIC_COUNT} 個の独立したメトリクスで評価してください。"
            f"単一メトリクスはエージェントの搾取対象になります。"
        )

    return None


def _detect_score_jump(tool_output: str) -> str | None:
    """Rule 21: Detect suspiciously large score improvements."""
    # Pattern: "score: 70 → 80" or "score 70 -> 80" (narrow match)
    pair_pattern = re.compile(
        r"\bscore[:\s]+(\d+(?:\.\d+)?)\s*(?:→|->|to)\s*(\d+(?:\.\d+)?)"
    )
    match = pair_pattern.search(tool_output)
    if match:
        parsed = _parse_score_pair(match.group(1), match.group(2))
        if parsed is not None:
            before, after = parsed
            delta = after - before
            if delta >= SCORE_JUMP_THRESHOLD:
                return (
                    f"[Gaming Detector] Rule 21 Goodhart 警告: "
                    f"スコアが +{delta:.1f}pp 上昇しました "
                    f"({before:.1f} → {after:.1f})。"
                    f"以下を確認してください: "
                    f"(1) テスト難易度が下がっていないか "
                    f"(2) assertion 数が減っていないか "
                    f"(3) スコープが狭まっていないか"
                )

    # Pattern: "improvement +8pp" or "delta +8%"
    delta_pattern = re.compile(r"(?:improvement|delta).*?[+](\d+(?:\.\d+)?)\s*(?:pp|%)")
    match = delta_pattern.search(tool_output)
    if match:
        delta = _parse_single_delta(match.group(1))
        if delta is not None and delta >= SCORE_JUMP_THRESHOLD:
            return (
                f"[Gaming Detector] Rule 21 Goodhart 警告: "
                f"スコアが +{delta:.1f}pp 上昇しました。"
                f"Goodhart's Law に注意: スコア上昇の原因を説明してください。"
            )

    return None


# --- Main ---


def main() -> None:
    data = load_hook_input()
    if not data:
        return
    if not check_tool(data, "Skill"):
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    tool_output = data.get("tool_output", "") or ""

    # Only check improve-related skill invocations
    if not _is_improve_related(tool_input):
        output_passthrough(data)
        return

    # Rule 22: Self-referential improvement check
    warning = _detect_self_referential_edit(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "21_self_referential",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    # Rule 21: Proxy metric divergence check
    warning = _detect_score_jump(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "20_proxy_metric",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    # Rule 23: Metric diversity check
    warning = _detect_single_metric(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "22_metric_diversity",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("gaming-detector", main, fail_closed=True)
