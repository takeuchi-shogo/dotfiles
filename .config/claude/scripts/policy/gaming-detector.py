#!/usr/bin/env python3
"""Gaming detector — detects specification gaming patterns in AutoEvolve.

Triggered by: hooks.PostToolUse (Skill)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext warning on stdout

Detects proxy metric divergence (Goodhart's Law), self-referential
improvement attempts, and single-metric evaluations per improve-policy.

Implemented rules:
- Rule 21: Proxy metric score jump detection (+5pp threshold)
- Rule 21_eval_shrinkage: Eval suite shrinkage detection (20%)
- Rule 21_fm_skew: Per-FM detection rate skew (4:1 ratio)
- Rule 22: Self-referential evaluation criteria modification
- Rule 23: Metric diversity (minimum 2 distinct metrics)
- Rule 29: Acceleration Guard (accept rate +20pp jump)
- Rule 30: Selective improvement (one metric up, another down)
"""

from __future__ import annotations

import json
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
EVAL_SHRINKAGE_THRESHOLD = 0.20  # 20% 以上の減少で WARNING
FM_SKEW_RATIO_THRESHOLD = 4.0  # max/min 比が 4:1 以上で WARNING
ACCEPT_RATE_JUMP_THRESHOLD = 20  # Rule 29: +20pp triggers Acceleration Guard
SELECTIVE_IMPROVE_THRESHOLD = 5  # Rule 30: +5pp improvement in one metric
SELECTIVE_DEGRADE_THRESHOLD = 3  # Rule 30: -3pp degradation in another
# T4 (Autogenesis): ceiling effect detection
CEILING_BASELINE_THRESHOLD = 0.9  # baseline >= 0.9 で天井付近とみなす
CEILING_DELTA_THRESHOLD = 0.03  # delta < 0.03 は天井効果で真の改善ではない
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


def _detect_acceleration_guard(tool_output: str) -> str | None:
    """Rule 29: Detect suspiciously rapid increase in accept rate.

    When accept_rate jumps by +20pp or more compared to previous cycle,
    it may indicate lowered standards or gaming of the acceptance criteria.
    """
    # Pattern: "accept rate: 80%" or "accept_rate: 85.5%"
    rate_pattern = re.compile(
        r"accept[_ ]rate\s*[=:]\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE
    )
    matches = rate_pattern.findall(tool_output)
    if len(matches) < 2:
        return None

    # Compare last two values (previous and current)
    try:
        prev_rate = float(matches[-2])
        curr_rate = float(matches[-1])
    except (ValueError, IndexError):
        return None

    delta = curr_rate - prev_rate
    if delta >= ACCEPT_RATE_JUMP_THRESHOLD:
        return (
            f"[Gaming Detector] Rule 29 Acceleration Guard 警告: "
            f"accept rate が +{delta:.1f}pp 急上昇しました "
            f"({prev_rate:.1f}% → {curr_rate:.1f}%)。"
            f"以下を確認してください: "
            f"(1) 提案の品質基準が下がっていないか "
            f"(2) 評価スコープが狭まっていないか "
            f"(3) Codex Gate の判定閾値が変更されていないか"
        )
    return None


def _detect_selective_improvement(tool_output: str) -> str | None:
    """Rule 30: Detect selective improvement.

    Detects when one metric improves while others degrade.
    When a single metric improves by +5pp or more while another
    degrades by -3pp or more, this indicates potential metric
    gaming — optimizing for a specific target at the expense of
    overall quality.
    """
    # Pattern: "metric_name: +X.Xpp" or "metric_name: -X.Xpp"
    # or "metric_name: X% (delta: +Y)"
    delta_pattern = re.compile(
        r"(\w[\w\s]*?)\s*[=:]\s*[+-]?[\d.]+%?\s*\([^\n]*?([+-]\d+(?:\.\d+)?)\s*(?:pp|%)",
        re.IGNORECASE,
    )
    # Also match: "metric_name delta: +X.Xpp"
    simple_delta = re.compile(
        r"(\w[\w\s]*?)\s+delta\s*[=:]\s*([+-]\d+(?:\.\d+)?)\s*(?:pp|%)",
        re.IGNORECASE,
    )

    deltas: dict[str, float] = {}
    for pattern in [delta_pattern, simple_delta]:
        for match in pattern.finditer(tool_output):
            name = match.group(1).strip().lower()
            try:
                delta_val = float(match.group(2))
                deltas[name] = delta_val
            except ValueError:
                continue

    if len(deltas) < 2:
        return None

    improvements = {k: v for k, v in deltas.items() if v >= SELECTIVE_IMPROVE_THRESHOLD}
    degradations = {
        k: v for k, v in deltas.items() if v <= -SELECTIVE_DEGRADE_THRESHOLD
    }

    if improvements and degradations:
        imp_str = ", ".join(f"{k} (+{v:.1f}pp)" for k, v in improvements.items())
        deg_str = ", ".join(f"{k} ({v:.1f}pp)" for k, v in degradations.items())
        return (
            f"[Gaming Detector] Rule 30 選択的改善警告: "
            f"改善: {imp_str} / 劣化: {deg_str}。"
            f"特定メトリクスの改善が他の品質指標を犠牲にしている可能性があります。"
            f"全体的な品質バランスを確認してください。"
        )
    return None


def _get_last_eval_tuple_count() -> int | None:
    """Read the last eval_tuple_count from improve-history.jsonl."""
    history_path = (
        Path.home() / ".claude" / "agent-memory" / "metrics" / "improve-history.jsonl"
    )
    if not history_path.exists():
        return None
    try:
        last_line = ""
        with open(history_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    last_line = line
        if not last_line:
            return None
        entry = json.loads(last_line)
        count = entry.get("eval_tuple_count")
        return int(float(count)) if count is not None else None
    except (ValueError, KeyError, json.JSONDecodeError, OSError) as e:
        sys.stderr.write(f"[gaming-detector] improve-history parse error: {e}\n")
        return None


def _detect_eval_suite_shrinkage(tool_output: str) -> str | None:
    """Detect eval suite shrinkage — fewer tuples may indicate hill-climbing.

    Checks for patterns like "eval tuples: 42", "regression tests: 15",
    "test count: 30" in tool output and compares against the last known
    count from improve-history.jsonl.
    """
    # パターン: "eval tuples: N" / "regression tests: N" / "test count: N"
    # Note: \b は日本語で誤動作するため lookaround を使用しない (ASCII only context)
    count_pattern = re.compile(
        r"(?:eval\s+tuples?|regression\s+tests?|test\s+count)\s*[=:]\s*(\d+)",
        re.IGNORECASE,
    )
    match = count_pattern.search(tool_output)
    if not match:
        return None

    current_count = int(match.group(1))

    prev_count = _get_last_eval_tuple_count()
    if prev_count is None or prev_count == 0:
        return None  # 比較データなし

    shrinkage = (prev_count - current_count) / prev_count
    if shrinkage >= EVAL_SHRINKAGE_THRESHOLD:
        return (
            f"[Gaming Detector] Eval Suite 縮小警告: "
            f"eval タプル数が {prev_count} → {current_count} に減少しました "
            f"({shrinkage:.0%} 減)。"
            f"テストの削除・無効化によるスコア操作の可能性があります。"
            f"タプル数の変更理由を確認してください。"
        )
    return None


def _detect_ceiling_effect(tool_output: str) -> str | None:
    """T4 (Autogenesis): Detect ceiling-effect false positives in skill benchmarks.

    When baseline_score >= 0.9 and delta < 0.03, the apparent improvement
    is more likely measurement noise at the ceiling than a real gain. Flag
    it so reviewers do not merge a benchmark-positive change that has no
    headroom to improve.

    Pattern: "baseline: 0.92 delta: 0.02" or "quality_baseline=9.2, delta=+0.2"
    (normalized to 0-1 scale — scores >= 10 are interpreted as percentages).
    """
    # Pattern: baseline and delta reported together
    baseline_pattern = re.compile(
        r"(?:baseline|quality_baseline|baseline_score)"
        r"\s*[=:]\s*([+-]?\d+(?:\.\d+)?)",
        re.IGNORECASE,
    )
    delta_pattern = re.compile(
        r"(?:delta|improvement)\s*[=:]\s*([+-]?\d+(?:\.\d+)?)", re.IGNORECASE
    )

    baseline_match = baseline_pattern.search(tool_output)
    delta_match = delta_pattern.search(tool_output)
    if not (baseline_match and delta_match):
        return None

    try:
        baseline = float(baseline_match.group(1))
        delta = float(delta_match.group(1))
    except ValueError:
        return None

    # Normalize both to 0-1 scale using the same factor derived from baseline.
    # Delta is assumed to be on the same scale as baseline.
    if baseline > 10.0:
        scale = 100.0
    elif baseline > 1.0:
        scale = 10.0
    else:
        scale = 1.0
    baseline /= scale
    delta /= scale

    if baseline >= CEILING_BASELINE_THRESHOLD and 0 < delta < CEILING_DELTA_THRESHOLD:
        return (
            f"[Gaming Detector] T4 Ceiling Effect 警告: "
            f"baseline {baseline:.2f} は天井付近 (>= {CEILING_BASELINE_THRESHOLD}) "
            f"かつ delta {delta:+.3f} が {CEILING_DELTA_THRESHOLD} 未満です。"
            f"見かけ上の改善は測定ノイズの可能性があります。"
            f"真の改善かを判定するには: (1) task_category 別 MDE を適用、"
            f"(2) 異なるモデル階層で再評価、(3) 複数 seed で検証。"
        )
    return None


def _detect_fm_skew(tool_output: str) -> str | None:
    """Detect skewed per-FM detection rates indicating over-reliance on specific FMs.

    Checks for patterns like "FM-001: 80%" or "FM-003: 15.5%" and warns
    if the max/min ratio exceeds the threshold.
    """
    # パターン: "FM-NNN: XX%" or "FM-NNN: XX.X%"
    fm_pattern = re.compile(r"FM-\d{3}\s*[=:]\s*(\d+(?:\.\d+)?)\s*%")
    rates = [float(m.group(1)) for m in fm_pattern.finditer(tool_output)]

    if len(rates) < 2:
        return None  # 比較に2つ以上必要

    min_rate = min(rates)
    max_rate = max(rates)

    if min_rate <= 0:
        return (
            "[Gaming Detector] FM 検出率警告: "
            "検出率 0% の FM が存在します。"
            "eval スイートから特定の failure mode が除外されている可能性があります。"
        )

    ratio = max_rate / min_rate
    if ratio >= FM_SKEW_RATIO_THRESHOLD:
        return (
            f"[Gaming Detector] FM 検出率偏り警告: "
            f"per-FM 検出率の max/min 比が {ratio:.1f}:1 です "
            f"(閾値: {FM_SKEW_RATIO_THRESHOLD:.0f}:1)。"
            f"特定 FM への過度な依存は eval の信頼性を下げます。"
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

    # Eval suite integrity: shrinkage check
    warning = _detect_eval_suite_shrinkage(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "21_eval_shrinkage",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    # Eval suite integrity: FM skew check
    warning = _detect_fm_skew(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "21_fm_skew",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    # Rule 29: Acceleration Guard
    warning = _detect_acceleration_guard(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "29_acceleration_guard",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    # Rule 30: Selective improvement detection
    warning = _detect_selective_improvement(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "30_selective_improvement",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    # T4 (Autogenesis): Ceiling effect detection
    warning = _detect_ceiling_effect(tool_output)
    if warning:
        emit(
            "pattern",
            {
                "type": "gaming_detected",
                "rule": "t4_ceiling_effect",
                "message": warning,
            },
        )
        output_context("PostToolUse", warning)
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("gaming-detector", main, fail_closed=True)
