#!/usr/bin/env python3
"""Cross-Domain Failure Mapper.

異なるドメイン（カテゴリ）間で共通する root_cause を検出し、
カテゴリ A の修正パターンがカテゴリ B にも適用可能な候補を提案する。

Hyperagents (arXiv:2603.19461) のクロスドメイン転移知見に基づく。

Usage:
    python cross-domain-mapper.py [--data-dir DIR]
"""

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path


def _get_data_dir(override: str | None = None) -> Path:
    """データディレクトリを返す。

    --data-dir 引数 > AUTOEVOLVE_DATA_DIR 環境変数 > デフォルトパス の優先順位。
    テスト時に AUTOEVOLVE_DATA_DIR を差し替えられるよう、呼び出しごとに環境変数を読む。
    """
    if override:
        return Path(override)
    env_override = os.environ.get("AUTOEVOLVE_DATA_DIR")
    if env_override:
        return Path(env_override)
    return Path.home() / ".claude" / "agent-memory"


def _load_jsonl(path: Path) -> list[dict]:
    """JSONL ファイルを読み込み、各行を dict のリストとして返す。"""
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _extract_root_cause(entry: dict) -> str | None:
    """root_cause を抽出する。

    root_cause が無ければ message をフォールバック。
    """
    rc = entry.get("root_cause")
    if rc:
        return rc.strip()
    msg = entry.get("message")
    if msg:
        return msg.strip()
    return None


def _extract_category(entry: dict) -> str | None:
    """エントリから category を抽出する。"""
    cat = entry.get("category")
    if cat:
        return cat.strip()
    return None


def scan_cross_domain(data_dir: Path) -> list[dict]:
    """errors.jsonl と patterns.jsonl を横断スキャンし、クロスドメイン転移候補を返す。

    同一 root_cause が 2 カテゴリ以上に出現する場合を検出する。

    Returns:
        list of dict with keys: root_cause, categories, count, suggestion
    """
    learnings_dir = data_dir / "learnings"
    errors_path = learnings_dir / "errors.jsonl"
    patterns_path = learnings_dir / "patterns.jsonl"

    errors = _load_jsonl(errors_path)
    patterns = _load_jsonl(patterns_path)

    # root_cause -> set of categories
    cause_categories: defaultdict[str, set[str]] = defaultdict(set)
    # root_cause -> total occurrence count
    cause_count: defaultdict[str, int] = defaultdict(int)

    for entry in errors + patterns:
        rc = _extract_root_cause(entry)
        cat = _extract_category(entry)
        if rc and cat:
            cause_categories[rc].add(cat)
            cause_count[rc] += 1

    # Filter: only root_causes appearing in 2+ categories
    candidates = []
    for rc, cats in sorted(cause_categories.items()):
        if len(cats) >= 2:
            sorted_cats = sorted(cats)
            candidates.append(
                {
                    "root_cause": rc,
                    "categories": sorted_cats,
                    "count": cause_count[rc],
                    "suggestion": _generate_suggestion(sorted_cats),
                }
            )

    # Sort by count descending for prioritization
    candidates.sort(key=lambda x: x["count"], reverse=True)
    return candidates


def _generate_suggestion(categories: list[str]) -> str:
    """カテゴリリストから転移候補の提案文を生成する。"""
    if len(categories) == 2:
        return f"{categories[0]} の修正パターンを {categories[1]} に転移可能か検証"
    return f"{', '.join(categories)} 間で共通修正パターンの抽出を推奨"


def format_markdown_table(candidates: list[dict]) -> str:
    """候補リストを markdown テーブル形式にフォーマットする。"""
    lines = [
        "| root_cause | categories | count | suggestion |",
        "|------------|------------|-------|------------|",
    ]

    if not candidates:
        lines.append(
            "| (該当なし) | — | — | クロスドメイン転移候補は検出されませんでした |"
        )
    else:
        for c in candidates:
            rc = c["root_cause"]
            # Truncate long root_cause for table readability
            if len(rc) > 80:
                rc = rc[:77] + "..."
            cats = ", ".join(c["categories"])
            lines.append(f"| {rc} | {cats} | {c['count']} | {c['suggestion']} |")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cross-Domain Failure Mapper: "
            "異なるカテゴリ間で共通する root_cause を検出する"
        )
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help=(
            "データディレクトリ"
            " (default: $AUTOEVOLVE_DATA_DIR"
            " or ~/.claude/agent-memory)"
        ),
    )
    args = parser.parse_args()

    data_dir = _get_data_dir(args.data_dir)
    candidates = scan_cross_domain(data_dir)

    print(f"## Cross-Domain Transfer Candidates ({len(candidates)} found)\n")
    print(format_markdown_table(candidates))

    if candidates:
        print(
            "\n> 上記の候補を cross-model-insights.md の"
            " Cross-Domain Transfer Candidates セクションに記録してください。"
        )


if __name__ == "__main__":
    main()
