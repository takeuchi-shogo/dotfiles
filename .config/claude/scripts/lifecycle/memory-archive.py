#!/usr/bin/env python3
"""MEMORY.md archive — 180行超過時に古いセクションをアーカイブに退避する。

Claude Code のハード上限は 200行/25KB。180行で proactive にアーカイブを発動し、
サイレント切り捨てを防ぐ。

手動実行: python3 ~/.claude/scripts/lifecycle/memory-archive.py
/improve や /memory-status から呼び出し可能。
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

# Claude Code ハード上限: 200行 / 25,000 bytes
# 180行で発動し、上限到達前にアーカイブする
MEMORY_THRESHOLD = 180
MEMORY_BYTES_THRESHOLD = 23_000  # 25KB の 92%
ARCHIVE_KEEP_LINES = 150  # アーカイブ後に残す目標行数


def find_memory_files() -> list[Path]:
    """プロジェクトメモリの MEMORY.md を検出する。"""
    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return []
    return sorted(base.rglob("memory/MEMORY.md"))


def archive_memory(memory_path: Path) -> str | None:
    """MEMORY.md が閾値を超えている場合、古いセクションをアーカイブする。"""
    if not memory_path.exists():
        return None

    content = memory_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    byte_size = len(content.encode("utf-8"))
    if len(lines) <= MEMORY_THRESHOLD and byte_size <= MEMORY_BYTES_THRESHOLD:
        return None

    # セクション境界を検出 (## で始まる行)
    sections: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if re.match(r"^## ", line):
            sections.append((i, line))

    if len(sections) < 3:
        return None  # セクションが少なすぎてアーカイブ不可

    # 先頭 (# タイトル) と最後の N セクションを保持
    # 残りをアーカイブに移動
    keep_sections = max(3, len(sections) // 2)  # 少なくとも半分 or 3セクション保持
    archive_end = sections[-keep_sections][0]

    # ヘッダー行 (# で始まる最初の行まで)
    header_end = sections[0][0] if sections else 0

    archived_content = "\n".join(lines[header_end:archive_end])
    kept_content = "\n".join(lines[:header_end] + lines[archive_end:])

    if not archived_content.strip():
        return None

    # アーカイブファイルに保存
    archive_dir = memory_path.parent / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m")
    archive_path = archive_dir / f"{ts}.md"

    existing_archive = ""
    if archive_path.exists():
        existing_archive = archive_path.read_text(encoding="utf-8")

    if not existing_archive:
        existing_archive = f"# Memory Archive ({ts})\n\n"

    archive_path.write_text(
        existing_archive.rstrip() + "\n\n" + archived_content.strip() + "\n",
        encoding="utf-8",
    )

    # MEMORY.md を更新
    memory_path.write_text(kept_content.strip() + "\n", encoding="utf-8")

    archived_lines = len(archived_content.splitlines())
    remaining_lines = len(kept_content.splitlines())
    return (
        f"Archived {archived_lines} lines from {memory_path.name} "
        f"to archive/{ts}.md ({remaining_lines} lines remaining)"
    )


def main() -> None:
    results: list[str] = []
    for memory_path in find_memory_files():
        result = archive_memory(memory_path)
        if result:
            results.append(result)

    if results:
        for r in results:
            print(r)
    else:
        print("No MEMORY.md files exceed the threshold.")


if __name__ == "__main__":
    main()
