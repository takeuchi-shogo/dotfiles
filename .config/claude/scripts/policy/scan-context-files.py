#!/usr/bin/env python3
"""Context-file injection scanner (SessionStart).

Claude Code は session 起動時に cwd の CLAUDE.md / AGENTS.md / .cursorrules を
自動で system prompt に読み込む。他リポジトリ (clone した untrusted repo) に
cd した状態で起動すると、その context ファイルに仕込まれた prompt injection が
そのまま読み込まれる経路が残る。

このフックは「読み込まれる context ファイル」を起動時にスキャンし、
正規ファイルには現れない難読化シグナル (zero-width / ANSI escape / null byte /
base64 eval payload) を検出したら additionalContext で警告する。

加えて、Forever Security が報告した Downloads 経由の平文攻撃指標
(ANTHROPIC_BASE_URL / --dangerously-bypass-approvals-and-sandbox /
mcp_servers 追加指示) と、cwd が ~/Downloads 配下であることも警告する。
難読化検出の挙動は変えない。

設計判断:
- 自然言語の汎用 jailbreak ("ignore previous instructions" 等) は対象外。
  false-positive が高く、SessionStart で誤警告を出すと毎回ノイズになる。
  難読化系は正規の CLAUDE.md には絶対に現れない高シグナル指標なので、
  trust-skip (dotfiles 自身を除外する allowlist) なしで全 cwd をスキャンしても
  誤警告が出ない。
- 平文の危険指示は攻撃 PoC に現れる固定トークンに限定する (汎用 jailbreak ではない)。
- symlink: repo 内の相対リンク (例: CLAUDE.md -> AGENTS.md) は正規運用として
  follow + 中身スキャン。絶対パスや cwd 外へ逃げるリンクだけを hostile として警告する。
- warn-only (exit 2 でブロックしない)。起動を妨げず、判断は人間に委ねる。
- 出典: Hermes Harness (NousResearch) の "context tier runs prompt-injection
  scanning before loading cwd project files" を /absorb (2026-05-30) で採用。
  難読化パターンは prompt-injection-detector.py と同期 (DRY: 3 consumer 目で lib 化)。
  平文指標・Downloads 警告は Forever Security (2026-10-22) Downloads hijack を
  2026-10-27 に採用。
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

# Forever Security Downloads hijack で観測された平文の危険指示 (高シグナル固定語)
# 汎用 jailbreak 文言は対象外。攻撃 PoC に現れるトークンのみ。
PLAINTEXT_THREAT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("anthropic-base-url", re.compile(r"ANTHROPIC_BASE_URL")),
    (
        "dangerously-bypass-approvals-and-sandbox",
        re.compile(r"--dangerously-bypass-approvals-and-sandbox"),
    ),
    (
        "mcp-servers-add",
        re.compile(
            r"\[mcp_servers\b"
            r"|mcp_servers\.[A-Za-z0-9_-]+"
            r"|(?:add|append|register|追加|登録).{0,120}mcp_servers"
            r"|mcp_servers.{0,120}(?:add|append|register|追加|登録|config\.toml)",
            re.IGNORECASE,
        ),
    ),
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


def _scan_plaintext_threats(text: str) -> list[tuple[str, str]]:
    """Return list of (pattern_name, detail) for plain-text attack indicators."""
    hits: list[tuple[str, str]] = []
    for name, pattern in PLAINTEXT_THREAT_PATTERNS:
        match = pattern.search(text)
        if match:
            hits.append((name, match.group(0)[:80]))
    return hits


def _is_under_downloads(cwd: Path) -> bool:
    """True when cwd resolves under ~/Downloads (web-writable drop folder)."""
    downloads = (Path.home() / "Downloads").resolve()
    try:
        cwd.resolve().relative_to(downloads)
    except (ValueError, OSError):
        return False
    return True


def _is_in_repo_relative_symlink(fpath: Path, cwd: Path) -> bool:
    """True when symlink target stays inside cwd via a relative link.

    Allows CLAUDE.md -> AGENTS.md (monorepo 等の正規運用)。
    Absolute targets and links that resolve outside cwd remain hostile.
    """
    try:
        raw = os.readlink(fpath)
    except OSError:
        return False
    if os.path.isabs(raw):
        return False
    try:
        resolved = fpath.resolve(strict=True)
        cwd_resolved = cwd.resolve(strict=True)
    except OSError:
        return False
    try:
        resolved.relative_to(cwd_resolved)
    except ValueError:
        return False
    return True


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


def _emit_warnings(
    findings: list[tuple[str, str, str]], under_downloads: bool
) -> None:
    lines: list[str] = []
    if under_downloads:
        lines.extend(
            [
                "⚠️ SECURITY: cwd が ~/Downloads 配下です。",
                "Web ページが無操作で AGENTS.md / CLAUDE.md を落とせる場所なので、"
                "ここでの agent 起動は設定書き換え攻撃の対象になります。"
                "別ディレクトリへ移してから起動してください。",
            ]
        )
    if findings:
        if lines:
            lines.append("")
        lines.extend(
            [
                "⚠️ SECURITY: cwd の context ファイルに injection / 危険指示 "
                "シグナルを検出しました。",
                "これらのファイルは起動時に system prompt へ読み込まれます。"
                "内容を信頼する前に確認してください:",
            ]
        )
        for rel_path, pattern_name, detail in findings:
            lines.append(f"  - {rel_path}: {pattern_name} ({detail})")
    output_context("SessionStart", "\n".join(lines))


def main() -> None:
    data = load_hook_input()
    cwd = data.get("cwd") or os.getcwd()
    session_id = data.get("session_id", "unknown")
    cwd_path = Path(cwd)

    findings: list[tuple[str, str, str]] = []
    for rel_path in CONTEXT_FILES:
        fpath = cwd_path / rel_path
        try:
            # Hostile: absolute or cwd-escaping symlink (e.g. CLAUDE.md -> /etc/passwd).
            # Safe: in-repo relative symlink (e.g. CLAUDE.md -> AGENTS.md) — follow
            # and scan target contents for obfuscation instead of warning on the link.
            if fpath.is_symlink() and not _is_in_repo_relative_symlink(fpath, cwd_path):
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
        for pattern_name, detail in _scan_plaintext_threats(text):
            _log(cwd, rel_path, pattern_name, detail, session_id)
            findings.append((rel_path, pattern_name, detail))

    under_downloads = _is_under_downloads(cwd_path)
    if under_downloads:
        _log(cwd, "(cwd)", "downloads-cwd", str(cwd_path), session_id)

    if findings or under_downloads:
        _emit_warnings(findings, under_downloads)
        return

    # Clean — emit nothing (no additionalContext noise)
    json.dump({}, sys.stdout)


if __name__ == "__main__":
    run_hook("scan-context-files", main, fail_closed=False)
