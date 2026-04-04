#!/usr/bin/env python3
"""メモリファイル間の矛盾候補を自動検出.

同一 type のメモリファイル間で description の類似度をチェックし、
矛盾キーワードの存在を検出して候補を報告する。

Usage:
    python contradiction-scanner.py [--memory-dir <path>]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# 矛盾とみなすキーワードペア（片方が A に、他方が B に存在する場合に候補とする）
CONTRADICTION_PAIRS: list[tuple[str, str]] = [
    ("禁止", "推奨"),
    ("使わない", "使う"),
    ("しない", "する"),
    ("避ける", "採用"),
    ("不要", "必須"),
    ("disable", "enable"),
    ("never", "always"),
    ("don't", "do"),
    ("avoid", "prefer"),
]


def parse_frontmatter(file_path: Path) -> dict:
    """YAML frontmatter を簡易パースして主要フィールドを返す.

    PyYAML に依存せず、正規表現と行ごとの key: value パースで実装する。
    frontmatter がなければ空 dict を返す。

    Args:
        file_path: パース対象の .md ファイルパス

    Returns:
        name, description, type フィールドを含む dict（存在するもののみ）
    """
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    # frontmatter は --- で始まり --- で終わる
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)
    result: dict = {}

    for line in frontmatter_text.splitlines():
        # key: value 形式の行のみを処理
        kv_match = re.match(r"^(\w+):\s*(.*)", line)
        if not kv_match:
            continue
        key, value = kv_match.group(1).strip(), kv_match.group(2).strip()
        # 引用符を除去
        value = re.sub(r'^["\']|["\']$', "", value)
        if key in ("name", "description", "type"):
            result[key] = value

    return result


def load_memory_files(memory_dir: Path) -> list[dict]:
    """memory_dir 内の全 .md ファイル（MEMORY.md を除く）を読み込む.

    各ファイルの frontmatter と本文を構造化して返す。

    Args:
        memory_dir: メモリファイルが格納されているディレクトリ

    Returns:
        各ファイルの情報を格納した dict のリスト。
        各 dict は path, name, description, type, body を持つ。
    """
    records: list[dict] = []

    for md_file in sorted(memory_dir.glob("*.md")):
        # MEMORY.md はインデックスファイルなので除外
        if md_file.name == "MEMORY.md":
            continue

        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        frontmatter = parse_frontmatter(md_file)

        # frontmatter を除いた本文を取得
        body_match = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
        body = body_match.group(1).strip() if body_match else text.strip()

        records.append(
            {
                "path": md_file,
                "name": frontmatter.get("name", md_file.stem),
                "description": frontmatter.get("description", ""),
                "type": frontmatter.get("type", ""),
                "body": body,
            }
        )

    return records


def word_overlap_ratio(text_a: str, text_b: str) -> float:
    """2つのテキストの単語重複率を計算する.

    英語・日本語混在対応: 空白と句読点で分割する。
    overlap = len(words_a & words_b) / min(len(words_a), len(words_b))

    Args:
        text_a: 比較対象テキスト A
        text_b: 比較対象テキスト B

    Returns:
        重複率 (0.0〜1.0)。どちらかが空の場合は 0.0。
    """
    # 空白、句読点、日本語の読点・句点で分割
    split_pattern = (
        r"[\s\u3001\u3002\uff0c\uff0e、。,.\-_/|！？!?「」『』【】\[\]()（）]+"
    )

    words_a = set(w for w in re.split(split_pattern, text_a) if w)
    words_b = set(w for w in re.split(split_pattern, text_b) if w)

    if not words_a or not words_b:
        return 0.0

    overlap = len(words_a & words_b)
    return overlap / min(len(words_a), len(words_b))


def detect_contradictions(
    memories: list[dict],
    similarity_threshold: float = 0.3,
) -> list[dict]:
    """同一 type のメモリペアを比較して矛盾候補を検出する.

    Step 1: description の word_overlap_ratio が similarity_threshold 以上のペアを抽出。
    Step 2: 各ペアの body を比較し、CONTRADICTION_PAIRS の片方が A にあり
            他方が B にある場合に候補とする。

    Args:
        memories: load_memory_files の返り値
        similarity_threshold: description 類似度の下限閾値（デフォルト 0.3）

    Returns:
        矛盾候補のリスト。各要素は file_a, file_b, type, similarity, reason を持つ。
    """
    candidates: list[dict] = []

    # type でグループ化
    by_type: dict[str, list[dict]] = {}
    for mem in memories:
        mem_type = mem["type"] or "_untyped"
        by_type.setdefault(mem_type, []).append(mem)

    for mem_type, group in by_type.items():
        # 同一 type 内のペアをすべて比較
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                mem_a = group[i]
                mem_b = group[j]

                # Step 1: description の類似度チェック
                similarity = word_overlap_ratio(
                    mem_a["description"], mem_b["description"]
                )
                if similarity < similarity_threshold:
                    continue

                # Step 2: 本文の矛盾キーワードチェック
                body_a = mem_a["body"].lower()
                body_b = mem_b["body"].lower()

                for kw_positive, kw_negative in CONTRADICTION_PAIRS:
                    kw_pos = kw_positive.lower()
                    kw_neg = kw_negative.lower()

                    # A に positive・B に negative、またはその逆
                    a_has_pos = kw_pos in body_a
                    a_has_neg = kw_neg in body_a
                    b_has_pos = kw_pos in body_b
                    b_has_neg = kw_neg in body_b

                    if (a_has_pos and b_has_neg) or (a_has_neg and b_has_pos):
                        reason = (
                            f"キーワード矛盾: "
                            f"'{kw_positive}' vs '{kw_negative}' "
                            f"(description 類似度: {similarity:.2f})"
                        )
                        candidates.append(
                            {
                                "file_a": str(mem_a["path"]),
                                "file_b": str(mem_b["path"]),
                                "type": mem_type,
                                "similarity": similarity,
                                "reason": reason,
                            }
                        )
                        break  # 同一ペアで複数ヒットしても1件として扱う

    return candidates


def generate_contradiction_report(candidates: list[dict]) -> str:
    """矛盾候補のレポートを生成する.

    候補があれば [CONTRADICTION_CANDIDATE] タグ付きで報告する。

    Args:
        candidates: detect_contradictions の返り値

    Returns:
        フォーマット済みレポート文字列
    """
    lines = ["[CONTRADICTION_SCAN] メモリ矛盾スキャン結果"]

    if not candidates:
        lines.append("  矛盾候補なし ✓")
        return "\n".join(lines)

    lines.append(f"  矛盾候補: {len(candidates)} 件")
    lines.append("")

    for idx, c in enumerate(candidates, 1):
        file_a = Path(c["file_a"]).name
        file_b = Path(c["file_b"]).name
        lines.append(f"[CONTRADICTION_CANDIDATE] #{idx}: {file_a} vs {file_b}")
        lines.append(f"  type     : {c['type']}")
        lines.append(f"  reason   : {c['reason']}")
        lines.append(f"  file_a   : {c['file_a']}")
        lines.append(f"  file_b   : {c['file_b']}")
        lines.append("")

    lines.append("→ /improve で矛盾を解消してください")

    return "\n".join(lines)


def find_memory_dirs() -> list[Path]:
    """projects/ 以下の memory ディレクトリを自動検出する.

    Path.home() / ".claude" / "projects" 以下を glob で検索し、
    MEMORY.md が存在するディレクトリを返す。

    Returns:
        検出されたメモリディレクトリのリスト
    """
    projects_root = Path.home() / ".claude" / "projects"
    if not projects_root.is_dir():
        return []

    return [p.parent for p in projects_root.glob("*/memory/MEMORY.md")]


def main() -> None:
    """エントリポイント."""
    parser = argparse.ArgumentParser(
        description="メモリファイル間の矛盾候補を自動検出する"
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        help="メモリディレクトリのパス（省略時は自動検出）",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.3,
        help="description 類似度の閾値 (デフォルト: 0.3)",
    )
    args = parser.parse_args()

    # メモリディレクトリの決定
    if args.memory_dir:
        memory_dirs = [args.memory_dir]
    else:
        memory_dirs = find_memory_dirs()

    if not memory_dirs:
        print("[CONTRADICTION_SCAN] メモリディレクトリが見つかりません")
        sys.exit(0)

    all_candidates: list[dict] = []

    for memory_dir in memory_dirs:
        if not memory_dir.is_dir():
            print(f"[CONTRADICTION_SCAN] ディレクトリが存在しません: {memory_dir}")
            continue

        memories = load_memory_files(memory_dir)
        if len(memories) < 2:
            # ファイルが2件未満では比較不可
            continue

        candidates = detect_contradictions(memories, args.threshold)
        all_candidates.extend(candidates)

    report = generate_contradiction_report(all_candidates)
    print(report)


if __name__ == "__main__":
    main()
