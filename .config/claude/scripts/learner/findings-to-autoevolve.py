#!/usr/bin/env python3
"""R-11: review-findings.jsonl → AutoEvolve L1 Recovery Tips 変換.

review-findings.jsonl の各 finding を AutoEvolve L1 (Recovery Tips) に変換し、
/improve 実行時の入力ソースとして提供する。

Usage:
    python findings-to-autoevolve.py [--dry-run]

出力: advisory テキスト (stdout) + learnings/recovery-tips.jsonl への追記
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from storage import get_data_dir, read_jsonl

# FM → L1 カテゴリマッピング
FM_TO_CATEGORY: dict[str, str] = {
    "FM-001": "errors",
    "FM-002": "errors",
    "FM-003": "quality",
    "FM-004": "quality",
    "FM-005": "quality",
    "FM-006": "errors",
    "FM-007": "errors",
    "FM-008": "errors",
    "FM-009": "errors",
    "FM-010": "evaluators",
    "FM-011": "agents",
    "FM-012": "errors",
    "FM-013": "agents",
    "FM-014": "agents",
    "FM-015": "agents",
    "FM-016": "evaluators",
    "FM-017": "quality",
    "FM-018": "evaluators",
    "FM-019": "agents",
    "FM-020": "quality",
}

# 昇格条件: watch が L1 に昇格するために必要な出現回数
WATCH_PROMOTION_THRESHOLD = 3


def load_findings() -> list[dict]:
    """review-findings.jsonl を読み込む."""
    path = get_data_dir() / "learnings" / "review-findings.jsonl"
    return read_jsonl(path)


def load_existing_tips() -> set[str]:
    """既存の recovery-tips.jsonl から finding_id を収集し重複防止."""
    path = get_data_dir() / "learnings" / "recovery-tips.jsonl"
    tips = read_jsonl(path)
    return {t.get("source_finding_id", "") for t in tips if t.get("source_finding_id")}


def count_watch_occurrences(findings: list[dict]) -> Counter[str]:
    """watch severity の failure_mode 出現回数をカウント."""
    counter: Counter[str] = Counter()
    for f in findings:
        if f.get("severity") == "watch" and f.get("failure_mode"):
            counter[f["failure_mode"]] += 1
    return counter


def should_promote(finding: dict, watch_counts: Counter[str]) -> bool:
    """finding を L1 に昇格すべきか判定."""
    severity = finding.get("severity", "watch")
    if severity in ("critical", "important"):
        return True
    if severity == "watch":
        fm = finding.get("failure_mode", "")
        return watch_counts.get(fm, 0) >= WATCH_PROMOTION_THRESHOLD
    return False


def finding_to_tip(finding: dict) -> dict:
    """finding を recovery-tips.jsonl のエントリ形式に変換."""
    fm = finding.get("failure_mode", "")
    category = FM_TO_CATEGORY.get(fm, "errors")
    reviewer = finding.get("reviewer", "unknown")
    severity = finding.get("severity", "watch")
    finding_text = finding.get("finding", finding.get("message", ""))

    return {
        "error_pattern": f"[{fm}] {finding_text[:200]}",
        "failure_mode": fm,
        "recovery_action": f"Review finding from {reviewer}: {finding_text[:300]}",
        "trigger_condition": f"reviewer={reviewer}, severity={severity}",
        "importance": 0.9 if severity == "critical" else 0.7,
        "source": "review-findings",
        "source_finding_id": finding.get("id", finding.get("finding_id", "")),
        "l1_category": category,
        "reviewer_id": reviewer,
        "human_verdict": finding.get("human_verdict", "UNKNOWN"),
    }


def generate_advisory(promoted: list[dict], skipped: int) -> str:
    """advisory テキストを生成."""
    if not promoted:
        return "[FINDINGS_TO_AUTOEVOLVE] No new findings to promote to L1."

    lines = [
        "[FINDINGS_TO_AUTOEVOLVE] "
        f"{len(promoted)} findings promoted to L1 Recovery Tips "
        f"(skipped {skipped} duplicates/below-threshold).",
        "",
    ]

    # カテゴリ別サマリ
    by_category: dict[str, int] = {}
    for tip in promoted:
        cat = tip.get("l1_category", "errors")
        by_category[cat] = by_category.get(cat, 0) + 1

    for cat, count in sorted(by_category.items()):
        lines.append(f"  - {cat}: {count} tips")

    # reviewer 別サマリ
    by_reviewer: dict[str, int] = {}
    for tip in promoted:
        rev = tip.get("reviewer_id", "unknown")
        by_reviewer[rev] = by_reviewer.get(rev, 0) + 1

    lines.append("")
    lines.append("  Reviewer breakdown:")
    for rev, count in sorted(by_reviewer.items(), key=lambda x: -x[1]):
        lines.append(f"    - {rev}: {count}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="R-11: findings → AutoEvolve L1")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show advisory without writing"
    )
    args = parser.parse_args()

    findings = load_findings()
    if not findings:
        print("[FINDINGS_TO_AUTOEVOLVE] No review findings found.")
        return

    existing_ids = load_existing_tips()
    watch_counts = count_watch_occurrences(findings)

    promoted: list[dict] = []
    skipped = 0

    for finding in findings:
        fid = finding.get("id", finding.get("finding_id", ""))
        if fid and fid in existing_ids:
            skipped += 1
            continue

        if not should_promote(finding, watch_counts):
            skipped += 1
            continue

        tip = finding_to_tip(finding)
        promoted.append(tip)

    advisory = generate_advisory(promoted, skipped)
    print(advisory)

    if not args.dry_run and promoted:
        from session_events import append_to_learnings

        for tip in promoted:
            append_to_learnings("recovery-tips", tip)


if __name__ == "__main__":
    main()
