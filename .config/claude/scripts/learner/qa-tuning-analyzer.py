#!/usr/bin/env python3
"""R-12: QA チューニングフィードバックループ.

review-findings.jsonl の蓄積データを分析し、
reviewer プロンプトの改善提案を自動生成する。

検出対象:
  - 見逃しパターン: human_verdict=DISAGREE が多い reviewer x failure_mode
  - 過検出パターン: watch レベル findings を大量発出する reviewer
  - Rationalization パターン: RATIONALIZATION_WARNING 頻度が高い reviewer

Usage:
    python qa-tuning-analyzer.py [--min-findings 10]

出力: advisory テキスト (stdout)
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from storage import get_data_dir, read_jsonl

# 閾値
DEFAULT_MIN_FINDINGS = 10
DISAGREE_RATE_THRESHOLD = 0.3  # 30% 以上で見逃し警告
WATCH_RATIO_THRESHOLD = 0.7  # 70% 以上が watch なら過検出
RATIONALIZATION_THRESHOLD = 5  # 5 回以上で警告

# reviewer-capability-scores.md のドメイン一覧
DOMAINS = [
    "Logic",
    "Security",
    "Performance",
    "Style",
    "Architecture",
    "UX",
    "Documentation",
]


def load_findings() -> list[dict]:
    """review-findings.jsonl を読み込む."""
    path = get_data_dir() / "learnings" / "review-findings.jsonl"
    return read_jsonl(path)


def load_rationalization_events() -> list[dict]:
    """current-session.jsonl / telemetry から rationalization 警告を収集."""
    path = get_data_dir() / "learnings" / "telemetry.jsonl"
    events = read_jsonl(path)
    return [
        e
        for e in events
        if "RATIONALIZATION_WARNING" in str(e.get("message", ""))
        or "rationalization" in str(e.get("type", "")).lower()
    ]


def detect_miss_patterns(findings: list[dict], min_findings: int) -> list[dict]:
    """見逃しパターン: DISAGREE 率が高い reviewer x failure_mode."""
    # reviewer x failure_mode ごとに集計
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for f in findings:
        reviewer = f.get("reviewer", "")
        fm = f.get("failure_mode", "")
        verdict = f.get("outcome") or f.get("human_verdict", "UNKNOWN")
        if reviewer and fm and verdict != "UNKNOWN":
            groups[(reviewer, fm)].append(verdict)

    patterns = []
    for (reviewer, fm), verdicts in groups.items():
        if len(verdicts) < min_findings:
            continue
        disagree_count = sum(1 for v in verdicts if v == "DISAGREE")
        rate = disagree_count / len(verdicts)
        if rate >= DISAGREE_RATE_THRESHOLD:
            patterns.append(
                {
                    "type": "miss",
                    "reviewer": reviewer,
                    "failure_mode": fm,
                    "disagree_rate": round(rate, 2),
                    "total": len(verdicts),
                    "disagree_count": disagree_count,
                }
            )
    return sorted(patterns, key=lambda x: -x["disagree_rate"])


def detect_overdetection(findings: list[dict], min_findings: int) -> list[dict]:
    """過検出パターン: watch 比率が高い reviewer."""
    by_reviewer: dict[str, list[str]] = defaultdict(list)
    for f in findings:
        reviewer = f.get("reviewer", "")
        severity = f.get("severity", "watch")
        if reviewer:
            by_reviewer[reviewer].append(severity)

    patterns = []
    for reviewer, severities in by_reviewer.items():
        if len(severities) < min_findings:
            continue
        watch_count = sum(1 for s in severities if s == "watch")
        ratio = watch_count / len(severities)
        if ratio >= WATCH_RATIO_THRESHOLD:
            patterns.append(
                {
                    "type": "overdetection",
                    "reviewer": reviewer,
                    "watch_ratio": round(ratio, 2),
                    "total": len(severities),
                    "watch_count": watch_count,
                }
            )
    return sorted(patterns, key=lambda x: -x["watch_ratio"])


def detect_rationalization(
    rationalization_events: list[dict],
) -> list[dict]:
    """Rationalization パターン: R-01 warning 頻度が高い reviewer."""
    by_reviewer: Counter[str] = Counter()
    for e in rationalization_events:
        reviewer = e.get("reviewer", e.get("data", {}).get("reviewer", "unknown"))
        by_reviewer[reviewer] += 1

    return [
        {
            "type": "rationalization",
            "reviewer": reviewer,
            "warning_count": count,
        }
        for reviewer, count in by_reviewer.most_common()
        if count >= RATIONALIZATION_THRESHOLD
    ]


def generate_score_proposals(
    miss_patterns: list[dict],
    overdetection: list[dict],
) -> list[dict]:
    """reviewer-capability-scores.md のスコア更新提案を生成."""
    proposals = []
    for p in miss_patterns:
        proposals.append(
            {
                "reviewer": p["reviewer"],
                "action": "decrease",
                "domain": _fm_to_domain(p["failure_mode"]),
                "reason": (
                    f"FM {p['failure_mode']} の見逃し率 "
                    f"{p['disagree_rate']:.0%} "
                    f"({p['disagree_count']}/{p['total']})"
                ),
                "suggested_delta": -0.05,
            }
        )
    for p in overdetection:
        proposals.append(
            {
                "reviewer": p["reviewer"],
                "action": "decrease_style",
                "domain": "Style",
                "reason": (
                    f"watch 比率 {p['watch_ratio']:.0%} "
                    f"({p['watch_count']}/{p['total']}) — "
                    "過検出傾向"
                ),
                "suggested_delta": -0.05,
            }
        )
    return proposals


def _fm_to_domain(fm: str) -> str:
    """failure_mode をドメインにマッピング."""
    mapping = {
        "FM-001": "Logic",
        "FM-002": "Logic",
        "FM-003": "Style",
        "FM-004": "Style",
        "FM-005": "Style",
        "FM-006": "Security",
        "FM-007": "Logic",
        "FM-008": "Logic",
        "FM-009": "Performance",
        "FM-010": "Security",
        "FM-016": "Logic",
        "FM-018": "Logic",
    }
    return mapping.get(fm, "Logic")


def generate_advisory(
    miss_patterns: list[dict],
    overdetection: list[dict],
    rationalization: list[dict],
    score_proposals: list[dict],
) -> str:
    """advisory テキストを生成."""
    total = len(miss_patterns) + len(overdetection) + len(rationalization)
    if total == 0:
        return "[QA_TUNING] No tuning recommendations found."

    lines = [f"[QA_TUNING] {total} tuning recommendations found.", ""]

    if miss_patterns:
        lines.append("## Miss Patterns (見逃し)")
        for p in miss_patterns:
            lines.append(
                f"  - {p['reviewer']}: {p['failure_mode']} "
                f"disagree rate {p['disagree_rate']:.0%} "
                f"({p['disagree_count']}/{p['total']})"
            )
            lines.append(
                f"    -> チェックリストに {p['failure_mode']} の明示追加を推奨"
            )
        lines.append("")

    if overdetection:
        lines.append("## Overdetection (過検出)")
        for p in overdetection:
            lines.append(
                f"  - {p['reviewer']}: watch ratio "
                f"{p['watch_ratio']:.0%} "
                f"({p['watch_count']}/{p['total']})"
            )
            lines.append("    -> style weight を下げることを推奨")
        lines.append("")

    if rationalization:
        lines.append("## Rationalization (合理化)")
        for p in rationalization:
            lines.append(f"  - {p['reviewer']}: {p['warning_count']} warnings")
            lines.append("    -> 懐疑的ペルソナの強化を推奨")
        lines.append("")

    if score_proposals:
        lines.append("## Score Update Proposals")
        for sp in score_proposals:
            lines.append(
                f"  - {sp['reviewer']}.{sp['domain']}: "
                f"{sp['suggested_delta']:+.2f} "
                f"({sp['reason']})"
            )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="R-12: QA tuning feedback loop")
    parser.add_argument(
        "--min-findings",
        type=int,
        default=DEFAULT_MIN_FINDINGS,
        help="Minimum findings per group to analyze",
    )
    args = parser.parse_args()

    findings = load_findings()
    if not findings:
        print("[QA_TUNING] No review findings found.")
        return

    rationalization_events = load_rationalization_events()

    miss_patterns = detect_miss_patterns(findings, args.min_findings)
    overdetection = detect_overdetection(findings, args.min_findings)
    rationalization = detect_rationalization(rationalization_events)
    score_proposals = generate_score_proposals(miss_patterns, overdetection)

    advisory = generate_advisory(
        miss_patterns, overdetection, rationalization, score_proposals
    )
    print(advisory)


if __name__ == "__main__":
    main()
