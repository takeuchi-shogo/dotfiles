#!/usr/bin/env python3
"""Skill Tier Shadow Report — report-only tier analysis.

Joins skill-inventory.md declared tiers with skill-executions.jsonl usage data
to produce a shadow analysis. Does NOT modify runtime behavior.

Output:
  - metrics/skill-tier-shadow.jsonl (machine-readable)
  - insights/skill-tier-shadow-YYYY-MM-DD.md (human-readable)

Usage:
    python skill-tier-shadow.py [--days 30]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from storage import get_data_dir, read_jsonl

# --- Tier Mapping ---

# skill-inventory.md の category → tier
CATEGORY_TO_TIER = {
    "Core Workflow": "core",
    "Cross-Model / Research": "core",
    "Domain / Specialist": "optional",
    "Automation / Meta": "optional",
    "Personal Ops": "optional",
}

DEFAULT_DAYS = 30


def parse_skill_inventory(inventory_path: Path) -> dict[str, str]:
    """skill-inventory.md を解析し {skill_name: tier} を返す."""
    if not inventory_path.exists():
        return {}

    result: dict[str, str] = {}
    current_category = ""
    pattern = re.compile(r"^- `([^`]+)`")

    for line in inventory_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("## "):
            current_category = line[3:].strip()
        elif line.startswith("- `"):
            match = pattern.match(line)
            if match and current_category:
                skill_name = match.group(1)
                tier = CATEGORY_TO_TIER.get(current_category, "optional")
                result[skill_name] = tier

    return result


def load_executions(data_dir: Path, days: int) -> list[dict]:
    """指定期間の skill-executions.jsonl を読み込む."""
    path = data_dir / "learnings" / "skill-executions.jsonl"
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    return [e for e in read_jsonl(path) if e.get("timestamp", "") >= cutoff]


def analyze_skills(
    declared: dict[str, str],
    executions: list[dict],
) -> list[dict]:
    """Declared tier と実行データを join して shadow analysis を生成."""
    # 実行データを集計
    exec_stats: dict[str, dict] = {}
    for entry in executions:
        name = entry.get("skill_name", "")
        if not name:
            continue
        if name not in exec_stats:
            exec_stats[name] = {"count": 0, "scores": [], "last_seen": ""}
        exec_stats[name]["count"] += 1
        score = entry.get("score")
        if isinstance(score, (int, float)):
            exec_stats[name]["scores"].append(score)
        ts = entry.get("timestamp", "")
        if ts > exec_stats[name]["last_seen"]:
            exec_stats[name]["last_seen"] = ts

    # 全スキル名を集める (declared + executed)
    all_skills = set(declared.keys()) | set(exec_stats.keys())

    results = []
    for skill in sorted(all_skills):
        tier = declared.get(skill, "undeclared")
        stats = exec_stats.get(skill, {"count": 0, "scores": [], "last_seen": ""})
        count = stats["count"]
        scores = stats["scores"]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        last_seen = stats["last_seen"]

        # Shadow status 判定
        shadow_status = _classify_shadow_status(tier, count, avg_score)

        results.append(
            {
                "skill": skill,
                "declared_tier": tier,
                "executions_period": count,
                "avg_score": avg_score,
                "last_seen": last_seen[:10] if last_seen else "",
                "shadow_status": shadow_status,
            }
        )

    return results


def _classify_shadow_status(tier: str, count: int, avg_score: float) -> str:
    """Shadow status を判定する.

    - aligned: tier と使用実態が一致
    - cold_core: core 宣言だが使われていない
    - hot_optional: optional/undeclared だが高頻度で使用
    - at_risk: 使用されているが品質が低い
    - no_data: 実行データなし
    """
    if count == 0:
        if tier == "core":
            return "cold_core"
        return "no_data"

    # score=1.0 は session-learner のデフォルト（データ不十分）なので
    # at_risk 判定には scored_by=retroactive 等の高信頼スコアのみ使う。
    # bimodal 分布（1.0 と 8.5）を考慮し、中間帯 (1.5, 5.0) を at_risk とする。
    if avg_score >= 1.5 and avg_score < 5.0:
        return "at_risk"

    if tier in ("optional", "undeclared") and count >= 5:
        return "hot_optional"

    return "aligned"


def write_jsonl_report(results: list[dict], data_dir: Path) -> Path:
    """metrics/skill-tier-shadow.jsonl に書き込む."""
    path = data_dir / "metrics" / "skill-tier-shadow.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for entry in results:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def write_markdown_report(results: list[dict], data_dir: Path, days: int) -> Path:
    """insights/skill-tier-shadow-YYYY-MM-DD.md に書き込む."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = data_dir / "insights" / f"skill-tier-shadow-{today}.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    # Status 別に分類
    by_status: dict[str, list[dict]] = {}
    for r in results:
        by_status.setdefault(r["shadow_status"], []).append(r)

    lines = [
        f"# Skill Tier Shadow Report — {today}",
        "",
        f"Analysis period: {days} days | Total skills: {len(results)}",
        "",
    ]

    # Summary
    for status in ["cold_core", "hot_optional", "at_risk", "no_data", "aligned"]:
        items = by_status.get(status, [])
        if items:
            lines.append(f"## {status} ({len(items)})")
            lines.append("")
            lines.append("| Skill | Tier | Executions | Avg Score | Last Seen |")
            lines.append("|-------|------|-----------|-----------|-----------|")
            for r in sorted(items, key=lambda x: -x["executions_period"]):
                lines.append(
                    f"| {r['skill']} | {r['declared_tier']} | "
                    f"{r['executions_period']} | {r['avg_score']} | "
                    f"{r['last_seen']} |"
                )
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill Tier Shadow Report")
    parser.add_argument(
        "--days", type=int, default=DEFAULT_DAYS, help="Analysis period in days"
    )
    parser.add_argument(
        "--json-only", action="store_true", help="Only output JSONL, skip markdown"
    )
    args = parser.parse_args()

    data_dir = get_data_dir()
    inventory_path = Path.home() / ".claude" / "references" / "skill-inventory.md"

    declared = parse_skill_inventory(inventory_path)
    executions = load_executions(data_dir, args.days)
    results = analyze_skills(declared, executions)

    jsonl_path = write_jsonl_report(results, data_dir)
    print(f"JSONL: {jsonl_path} ({len(results)} skills)")

    if not args.json_only:
        md_path = write_markdown_report(results, data_dir, args.days)
        print(f"Report: {md_path}")

    # Summary to stdout
    from collections import Counter

    status_counts = Counter(r["shadow_status"] for r in results)
    for status, count in status_counts.most_common():
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
