#!/usr/bin/env python3
"""Context-file injection scanner (SessionStart).

Claude Code は session 起動時に cwd の CLAUDE.md / AGENTS.md / .cursorrules を
自動で system prompt に読み込む。他リポジトリ (clone した untrusted repo) に
cd した状態で起動すると、その context ファイルに仕込まれた prompt injection が
そのまま読み込まれる経路が残る。

このフックは「読み込まれる context ファイル」を起動時にスキャンし、
正規ファイルには現れない難読化シグナル (zero-width / ANSI escape / null byte /
base64 eval payload) を検出したら additionalContext で警告する。

設計判断:
- 自然言語の jailbreak ("ignore previous instructions" 等) は対象外。
  false-positive が高く、SessionStart で誤警告を出すと毎回ノイズになる。
  難読化系は正規の CLAUDE.md には絶対に現れない高シグナル指標なので、
  trust-skip (dotfiles 自身を除外する allowlist) なしで全 cwd をスキャンしても
  誤警告が出ない。
- warn-only (exit 2 でブロックしない)。起動を妨げず、判断は人間に委ねる。
- 出典: Hermes Harness (NousResearch) の "context tier runs prompt-injection
  scanning before loading cwd project files" を /absorb (2026-05-30) で採用。
  難読化パターンは prompt-injection-detector.py と同期 (DRY: 3 consumer 目で lib 化)。
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (  # noqa: E402
    load_hook_input,
    output_context,
    rotate_and_append,
    run_hook,
)

# ---------------------------------------------------------------------------
# Obfuscation patterns — synced with prompt-injection-detector.py
# (正規の context ファイルには現れない高シグナル指標のみ)
# ---------------------------------------------------------------------------

# zero-width + bidi/format 制御文字 (U+202E RTL override = CVE-2021-42574
# Trojan Source を含む)。4 codepoint では Trojan Source 攻撃を取りこぼすため広域指定。
ZERO_WIDTH_RE = re.compile(
    "[​-‏"  # ZWSP/ZWNJ/ZWJ/LRM/RLM
    "‪-‮"  # bidi embeddings + RTL override (U+202E)
    "⁠-⁤"  # word joiner / invisible operators
    "⁪-⁯"  # deprecated format chars
    "؜᠎﻿]"  # arabic letter mark / mongolian vowel sep / BOM
    "|[\U000e0000-\U000e007f]"  # invisible Unicode tag block
)
ANSI_ESCAPE_RE = re.compile(r"\x1b\[|\\033\[|\\x1b\[")
NULL_BYTE_RE = re.compile(r"\x00|\\x00|\\0(?![0-9])")
BASE64_CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/=]{20,}")
# Python 系 + shell 系 (curl|sh / rm 等、現実的な "decode して実行" payload)
SUSPICIOUS_DECODED = (
    "eval(",
    "exec(",
    "import os",
    "subprocess",
    "__import__",
    "curl ",
    "wget ",
    "| sh",
    "|sh",
    "bash -c",
    "chmod +x",
    "os.system",
    "/bin/",
)

# cwd 起動時に Claude Code が読み込む可能性のある context ファイル
CONTEXT_FILES = ("CLAUDE.md", "AGENTS.md", ".cursorrules", ".claude/CLAUDE.md")

# 巨大ファイルの誤検出 / 性能対策 (context ファイルは通常 KB オーダー)
MAX_SCAN_BYTES = 256 * 1024


def _check_base64(text: str) -> str | None:
    for match in BASE64_CANDIDATE_RE.finditer(text):
        try:
            decoded = base64.b64decode(match.group(), validate=True).decode(
                "utf-8", errors="ignore"
            )
        except Exception:
            continue
        for pattern in SUSPICIOUS_DECODED:
            if pattern in decoded:
                return f"base64 decoded contains '{pattern}'"
    return None


def _scan_text(text: str) -> tuple[str, str] | None:
    """Return (pattern_name, detail) if an obfuscation signal is found."""
    m = ZERO_WIDTH_RE.search(text)
    if m:
        return "zero-width-unicode", f"U+{ord(m.group()):04X}"
    if ANSI_ESCAPE_RE.search(text):
        return "ansi-escape", "ANSI escape sequence detected"
    if NULL_BYTE_RE.search(text):
        return "null-byte", "null byte detected"
    detail = _check_base64(text)
    if detail:
        return "base64-payload", detail
    return None


def _log(
    cwd: str, rel_path: str, pattern_name: str, detail: str, session_id: str
) -> None:
    log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
    os.makedirs(log_dir, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "scan-context-files",
        "cwd": cwd,
        "file": rel_path,
        "pattern": pattern_name,
        "detail": detail,
        "session_id": session_id,
    }
    rotate_and_append(
        os.path.join(log_dir, "prompt-injection.jsonl"), json.dumps(entry)
    )


def main() -> None:
    data = load_hook_input()
    cwd = data.get("cwd") or os.getcwd()
    session_id = data.get("session_id", "unknown")

    findings = []
    for rel_path in CONTEXT_FILES:
        fpath = Path(cwd) / rel_path
        try:
            # symlink された context ファイルは読まない。CLAUDE.md -> /etc/passwd の
            # ような hostile symlink を follow すると「CLAUDE.md をスキャンした」という
            # false assurance になる。正規 repo は context ファイルを tree 外に
            # symlink しないため、symlink 自体を injection シグナルとして報告する。
            if fpath.is_symlink():
                detail = f"-> {os.readlink(fpath)}"
                _log(cwd, rel_path, "symlink", detail, session_id)
                findings.append((rel_path, "symlink", detail))
                continue
            if not fpath.is_file():
                continue
            if fpath.stat().st_size > MAX_SCAN_BYTES:
                continue
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        result = _scan_text(text)
        if result:
            pattern_name, detail = result
            _log(cwd, rel_path, pattern_name, detail, session_id)
            findings.append((rel_path, pattern_name, detail))

    if findings:
        lines = [
            "⚠️ SECURITY: cwd の context ファイルに難読化された injection "
            "シグナルを検出しました。",
            "これらのファイルは起動時に system prompt へ読み込まれます。"
            "内容を信頼する前に確認してください:",
        ]
        for rel_path, pattern_name, detail in findings:
            lines.append(f"  - {rel_path}: {pattern_name} ({detail})")
        output_context("SessionStart", "\n".join(lines))
        return

    # Clean — emit nothing (no additionalContext noise)
    json.dump({}, sys.stdout)


if __name__ == "__main__":
    run_hook("scan-context-files", main, fail_closed=False)
