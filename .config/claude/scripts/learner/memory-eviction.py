#!/usr/bin/env python3
"""メモリファイルの重要度ベース淘汰管理.

effective_score (freshness * importance_weight) でメモリファイルをスコアリングし、
上限を超えた場合に淘汰候補を報告・実行する。

Usage:
    python memory-eviction.py [--dry-run] [--execute] [--max 60]
    python memory-eviction.py --dry-run --max 50
    python memory-eviction.py --execute
    python memory-eviction.py --dry-run --memory-dir /path/to/memory
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path

# staleness-detector.py をハイフン付きファイル名からインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
_staleness_detector = importlib.import_module("staleness-detector")
analyze_memory_staleness = _staleness_detector.analyze_memory_staleness
IMPORTANCE_WEIGHTS = _staleness_detector.IMPORTANCE_WEIGHTS

# ------------------------------------------------------------------ 定数
MAX_MEMORY_FILES = 60  # デフォルトのメモリファイル数上限
PROTECTED_TYPES: set[str] = {"feedback"}  # eviction 対象外の type


# ------------------------------------------------------------------ 検索
def find_memory_dirs() -> list[Path]:
    """~/.claude/projects/*/memory/ ディレクトリを列挙する.

    MEMORY.md が存在するディレクトリのみを返す。
    """
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return []
    return sorted(p.parent for p in projects_dir.glob("*/memory/MEMORY.md"))


# ------------------------------------------------------------------ スコアリング
def compute_eviction_candidates(
    memory_dir: Path,
    max_files: int = MAX_MEMORY_FILES,
) -> tuple[list[dict], int]:
    """淘汰候補リストを計算する.

    Returns:
        (candidates, total_files) のタプル。
        candidates は eviction_rank 付きの dict リスト（effective_score 昇順）。
        ファイル数が max_files 以下の場合は candidates が空リスト。
    """
    all_files = analyze_memory_staleness(memory_dir)
    total = len(all_files)

    # PROTECTED_TYPES を除外
    evictable = [f for f in all_files if f.get("type") not in PROTECTED_TYPES]

    # ファイル数が上限以下なら淘汰不要
    # total (保護含む) が超えていなければ不要
    if total <= max_files:
        return [], total

    # 超過数を計算（保護ファイルは削除できないので evictable から選ぶ）
    # 上限を超えた件数分だけ effective_score の低い順に候補とする
    excess = total - max_files
    # evictable を effective_score 昇順でソート
    evictable_sorted = sorted(evictable, key=lambda x: x["effective_score"])
    candidates = evictable_sorted[:excess]

    # eviction_rank を付与（1始まり）
    for rank, candidate in enumerate(candidates, start=1):
        candidate["eviction_rank"] = rank

    return candidates, total


# ------------------------------------------------------------------ 削除実行
def evict_files(candidates: list[dict], memory_dir: Path) -> int:
    """淘汰候補ファイルを物理削除し、MEMORY.md から対応行を除去する.

    Returns:
        実際に削除したファイル数。
    """
    if not candidates:
        return 0

    # 削除対象ファイル名のセット（stem と name の両方でマッチできるように保持）
    target_stems = {Path(c["file"]).stem for c in candidates}
    target_names = {c["file"] for c in candidates}

    deleted_count = 0

    # 物理削除
    for candidate in candidates:
        file_path = memory_dir / candidate["file"]
        if file_path.exists():
            file_path.unlink()
            deleted_count += 1

    # MEMORY.md から対応行を除去
    memory_md = memory_dir / "MEMORY.md"
    if memory_md.exists():
        original = memory_md.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        kept_lines = []
        for line in lines:
            # ファイル名（stem または name）を含む行を除去
            if _line_references_target(line, target_stems, target_names):
                continue
            kept_lines.append(line)
        memory_md.write_text("".join(kept_lines), encoding="utf-8")

    return deleted_count


def _line_references_target(
    line: str,
    target_stems: set[str],
    target_names: set[str],
) -> bool:
    """行がいずれかの対象ファイルを参照しているか判定する.

    Markdown リンク形式 `[text](filename.md)` およびファイル名の直接出現を検出する。
    """
    # Markdown リンクから参照先ファイル名を抽出
    link_pattern = re.compile(r"\[.*?\]\(([^)]+\.md)\)")
    for match in link_pattern.finditer(line):
        ref = match.group(1)
        ref_path = Path(ref)
        if ref_path.name in target_names or ref_path.stem in target_stems:
            return True

    # リンク形式でないファイル名の直接出現もチェック
    for name in target_names:
        if name in line:
            return True

    return False


# ------------------------------------------------------------------ レポート生成
def generate_eviction_report(
    candidates: list[dict],
    memory_dir: Path,
    max_files: int,
    total_files: int,
    *,
    executed: bool = False,
) -> str:
    """淘汰レポートを生成する.

    候補がなければ「淘汰不要」を、あれば各ファイルのスコア・type・経過日数を表示する。
    """
    lines = [
        f"[MEMORY_EVICTION] Memory directory: {memory_dir}",
        f"  Total files: {total_files}, Max: {max_files}",
    ]

    if not candidates:
        lines.append("  No eviction needed ✓")
        return "\n".join(lines)

    lines.append(f", Candidates: {len(candidates)}")
    lines.append("")

    for c in candidates:
        rank = c.get("eviction_rank", "?")
        fname = c["file"]
        effective = c.get("effective_score", 0.0)
        ftype = c.get("type") or "unknown"
        days_old = c.get("days_old", "?")
        lines.append(
            f"  #{rank} {fname} "
            f"(effective={effective:.3f}, type={ftype}, {days_old}日更新なし)"
        )

    lines.append("")

    if executed:
        lines.append(f"  [EXECUTED] {len(candidates)} ファイルを削除しました。")
    else:
        lines.append("  [DRY-RUN] --execute を渡すと上記ファイルを削除します")

    return "\n".join(lines)


# ------------------------------------------------------------------ main
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "メモリファイル数が上限を超えた場合に"
            " effective_score の低いファイルを淘汰する"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="淘汰候補を表示するのみ（削除しない）。デフォルト動作",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="実際に削除を実行する（--dry-run を上書き）",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=MAX_MEMORY_FILES,
        metavar="N",
        help=f"メモリファイル数の上限（デフォルト: {MAX_MEMORY_FILES}）",
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="メモリディレクトリを直接指定（省略時は自動検出）",
    )
    args = parser.parse_args()

    # --execute が明示されない限り dry-run
    execute = args.execute

    # メモリディレクトリの決定
    if args.memory_dir is not None:
        memory_dirs: list[Path] = [args.memory_dir]
    else:
        memory_dirs = find_memory_dirs()

    if not memory_dirs:
        print("[MEMORY_EVICTION] No memory directories found.")
        sys.exit(0)

    for memory_dir in memory_dirs:
        candidates, total = compute_eviction_candidates(memory_dir, args.max)

        if execute and candidates:
            deleted = evict_files(candidates, memory_dir)
            report = generate_eviction_report(
                candidates,
                memory_dir,
                args.max,
                total,
                executed=True,
            )
            print(report)
            print(f"  削除件数: {deleted}")
        else:
            report = generate_eviction_report(
                candidates,
                memory_dir,
                args.max,
                total,
                executed=False,
            )
            print(report)


if __name__ == "__main__":
    main()
