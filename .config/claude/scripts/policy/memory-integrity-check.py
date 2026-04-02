#!/usr/bin/env python3
"""Memory file integrity check (SessionStart hook).

Franklin et al. (2026) Gap #1: Latent Memory Poisoning — 0.1% 未満の汚染で
80% 超の攻撃成功率。メモリファイルの想定外の変更を検知する。

強度: Soft warning (advisory) — 不一致時は stderr に WARNING、ブロックしない。
完全な改ざん防止ではなく「想定外の変更検知」が目的。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import load_hook_input, output_context, run_hook

MEMORY_DIRS = [
    os.path.expanduser("~/.claude/projects/*/memory"),
]
CHECKSUM_PATH = os.path.expanduser("~/.claude/agent-memory/memory-checksums.json")


def _glob_memory_files() -> list[Path]:
    """Collect all memory .md files across project scopes."""
    import glob

    files: list[Path] = []
    for pattern in MEMORY_DIRS:
        for path_str in glob.glob(os.path.join(pattern, "*.md")):
            files.append(Path(path_str))
    return sorted(files)


def _compute_checksums(files: list[Path]) -> dict[str, str]:
    """Compute SHA-256 checksums for given files."""
    checksums: dict[str, str] = {}
    for f in files:
        try:
            content = f.read_bytes()
            checksums[str(f)] = hashlib.sha256(content).hexdigest()[:16]
        except OSError:
            continue
    return checksums


def _load_stored_checksums() -> dict[str, str] | None:
    """Load previously stored checksums.

    Returns None if no checksum file exists (first run).
    Returns {} if file exists but is corrupted (warns on stderr).
    """
    if not os.path.exists(CHECKSUM_PATH):
        return None
    try:
        with open(CHECKSUM_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
            return data.get("checksums", {})
    except json.JSONDecodeError:
        print(
            "[Memory Integrity] チェックサムファイルが破損しています。"
            "改ざんの可能性があります。手動確認を推奨します。",
            file=sys.stderr,
        )
        return {}
    except OSError:
        return None


def _save_checksums(checksums: dict[str, str]) -> None:
    """Save checksums atomically."""
    os.makedirs(os.path.dirname(CHECKSUM_PATH), exist_ok=True)
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "checksums": checksums,
    }
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(
            "w",
            dir=os.path.dirname(CHECKSUM_PATH),
            suffix=".json",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = tmp.name
        os.replace(tmp_path, CHECKSUM_PATH)
    except OSError as exc:
        print(
            f"[Memory Integrity] checksum save error: {exc}",
            file=sys.stderr,
        )


def _main() -> None:
    load_hook_input()

    files = _glob_memory_files()
    if not files:
        return

    current = _compute_checksums(files)
    stored = _load_stored_checksums()

    if stored is None:
        # First run — store initial checksums
        _save_checksums(current)
        return

    # Compare
    changed: list[str] = []
    added: list[str] = []
    removed: list[str] = []

    for path, checksum in current.items():
        if path not in stored:
            added.append(path)
        elif stored[path] != checksum:
            changed.append(path)

    for path in stored:
        if path not in current:
            removed.append(path)

    if not changed and not added and not removed:
        return

    # Build warning
    parts: list[str] = []
    if changed:
        names = [os.path.basename(p) for p in changed]
        parts.append(f"変更: {', '.join(names)}")
    if added:
        names = [os.path.basename(p) for p in added]
        parts.append(f"追加: {', '.join(names)}")
    if removed:
        names = [os.path.basename(p) for p in removed]
        parts.append(f"削除: {', '.join(names)}")

    detail = "; ".join(parts)
    msg = f"[Memory Integrity] メモリファイル変更検出 — {detail}"
    print(msg, file=sys.stderr)
    output_context("SessionStart", msg)

    # NOTE: soft advisory 設計 — 変更検出後も新状態をベースラインに採用。
    # 目的は「1度知らせる」こと。永続アラームではない。
    _save_checksums(current)


if __name__ == "__main__":
    run_hook("memory-integrity-check", _main, fail_closed=False)
