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


META_IMPROVEMENT_CATEGORIES = {
    "memory_addition": "永続メモリ・状態保持の追加",
    "checklist_creation": "チェックリスト・ルールの構造化",
    "pipeline_stage": "パイプラインへのステージ追加",
    "prompt_refinement": "プロンプト・指示の精緻化",
    "guard_addition": "ガードレール・制約の追加",
    "feedback_loop": "フィードバックループの追加",
}

# カテゴリ推定用キーワードマップ
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "memory_addition": [
        "memory",
        "メモリ",
        "persist",
        "永続",
        "state",
        "状態保持",
    ],
    "checklist_creation": [
        "checklist",
        "チェックリスト",
        "rule",
        "ルール",
        "list",
    ],
    "pipeline_stage": [
        "pipeline",
        "パイプライン",
        "stage",
        "ステージ",
        "phase",
    ],
    "prompt_refinement": [
        "prompt",
        "プロンプト",
        "instruction",
        "指示",
        "refine",
    ],
    "guard_addition": [
        "guard",
        "ガード",
        "constraint",
        "制約",
        "limit",
        "制限",
    ],
    "feedback_loop": [
        "feedback",
        "フィードバック",
        "loop",
        "ループ",
        "iterate",
    ],
}


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


def classify_improvement_method(entry: dict) -> str | None:
    """実験エントリから改善手法カテゴリを推定する。

    hypothesis, causal_hypothesis, proposal_type のテキストから
    キーワードマッチでカテゴリを推定する。

    Returns:
        META_IMPROVEMENT_CATEGORIES のキー、または None
    """
    text_parts = []
    for field in ("hypothesis", "causal_hypothesis", "forward_plan"):
        val = entry.get(field)
        if val:
            text_parts.append(val.lower())
    text = " ".join(text_parts)
    if not text.strip():
        return None

    best_cat = None
    best_count = 0
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw.lower() in text)
        if count > best_count:
            best_count = count
            best_cat = cat

    return best_cat


def scan_meta_patterns(data_dir: Path) -> list[dict]:
    """手法カテゴリ×ドメインカテゴリの転移パターンを検出する。

    experiment_tracker のレジストリを読み込み、
    カテゴリ A で成功した手法がカテゴリ B に未適用の場合を検出。

    Returns:
        list of dict: method, successful_in, not_tried_in, suggestion
    """
    registry_path = data_dir / "experiments" / "experiment-registry.jsonl"
    entries = _load_jsonl(registry_path)

    # method_cat -> {domain_cat: {"tried": bool, "succeeded": bool}}
    method_domain: dict[str, dict[str, dict]] = {}
    all_domains: set[str] = set()

    for entry in entries:
        method = classify_improvement_method(entry)
        domain = entry.get("category")
        if not method or not domain:
            continue

        all_domains.add(domain)
        if method not in method_domain:
            method_domain[method] = {}
        if domain not in method_domain[method]:
            method_domain[method][domain] = {
                "tried": False,
                "succeeded": False,
            }

        method_domain[method][domain]["tried"] = True
        status = entry.get("status")
        if status == "merged":
            method_domain[method][domain]["succeeded"] = True

    # 転移候補: 手法 M がドメイン A で成功、ドメイン B で未試行
    candidates = []
    for method, domains in sorted(method_domain.items()):
        successful_in = [d for d, info in domains.items() if info["succeeded"]]
        not_tried_in = sorted(all_domains - set(domains.keys()))

        if successful_in and not_tried_in:
            desc = META_IMPROVEMENT_CATEGORIES.get(method, method)
            candidates.append(
                {
                    "method": method,
                    "method_description": desc,
                    "successful_in": sorted(successful_in),
                    "not_tried_in": not_tried_in,
                    "suggestion": (
                        f"{method} ({desc}) を"
                        f" {', '.join(not_tried_in)} に転移可能か検証"
                    ),
                }
            )

    return candidates


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

    # メタ改善パターン転移候補
    meta_candidates = scan_meta_patterns(data_dir)
    print(f"\n## Meta-Improvement Transfer Candidates ({len(meta_candidates)} found)\n")
    if meta_candidates:
        print("| method | description | successful_in | not_tried_in |")
        print("|--------|-------------|---------------|--------------|")
        for mc in meta_candidates:
            method = mc["method"]
            desc = mc["method_description"]
            succ = ", ".join(mc["successful_in"])
            nottried = ", ".join(mc["not_tried_in"])
            print(f"| {method} | {desc} | {succ} | {nottried} |")
    else:
        print("メタ改善パターン転移候補は検出されませんでした。")


if __name__ == "__main__":
    main()
