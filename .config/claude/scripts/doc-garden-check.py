#!/usr/bin/env python3
from __future__ import annotations
"""Doc Garden check — detects stale documentation at session start.

Triggered by: hooks.SessionStart
Input: (none — SessionStart hooks receive no stdin)
Output: stdout message as additionalContext

Three staleness checks:
  A) git diff: code changed but docs not updated
  B) timestamp: docs not updated in 30+ days
  C) content: docs reference non-existent file paths
"""
import os
import re
import subprocess
import time
from pathlib import Path
from typing import List, Tuple

DOC_DIRS = [
    ".config/claude/references",
    ".config/claude/rules",
    ".config/claude/agents",
]

# Reference check is limited to references/ only — agents/ and rules/ contain
# pattern definitions with file names that are not actual file references.
REF_CHECK_DIRS = [
    ".config/claude/references",
]

CODE_DIRS = [
    ".config/claude/scripts",
    ".config/claude/skills",
]

STALE_DAYS = 30
FILE_REF_PATTERN = re.compile(
    r'[`"\']([a-zA-Z0-9_./-]+\.(py|js|ts|md|json|sh))[`"\']'
)


def get_repo_root() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def check_git_diff(repo_root: str) -> List[str]:
    """A) Check if code changed but related docs didn't."""
    warnings = []
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:", "-n", "10"],
            capture_output=True, text=True, cwd=repo_root, timeout=10,
        )
        if result.returncode != 0:
            return []
        changed_files = set(f.strip() for f in result.stdout.split("\n") if f.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    code_changed = any(
        any(f.startswith(cd) for cd in CODE_DIRS) for f in changed_files
    )
    doc_changed = any(
        any(f.startswith(dd) for dd in DOC_DIRS) for f in changed_files
    )

    if code_changed and not doc_changed:
        warnings.append("直近10コミットでコード変更あり、ドキュメント更新なし")

    return warnings


def check_timestamps(repo_root: str) -> List[str]:
    """B) Find docs not updated in STALE_DAYS."""
    warnings = []
    now = time.time()
    threshold = now - (STALE_DAYS * 86400)

    for doc_dir in DOC_DIRS:
        full_dir = os.path.join(repo_root, doc_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for fname in files:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                mtime = os.path.getmtime(fpath)
                if mtime < threshold:
                    rel = os.path.relpath(fpath, repo_root)
                    days = int((now - mtime) / 86400)
                    warnings.append(f"{rel} ({days}日間未更新)")

    return warnings


def _strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks and pattern-definition lines to avoid false positives."""
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'^-\s+\*\*(?:検出パターン|ファイル|キーワード)\*\*:.*$', '', text, flags=re.MULTILINE)
    return text


def _find_in_skills(repo_root: str, filename: str) -> bool:
    """Recursively search for filename under .config/claude/skills/."""
    skills_dir = os.path.join(repo_root, ".config/claude/skills")
    if not os.path.isdir(skills_dir):
        return False
    for root, _, files in os.walk(skills_dir):
        if filename in files:
            return True
    return False


def check_references(repo_root: str) -> List[str]:
    """C) Find docs referencing non-existent file paths."""
    warnings = []

    for doc_dir in REF_CHECK_DIRS:
        full_dir = os.path.join(repo_root, doc_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for fname in files:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    content = Path(fpath).read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                cleaned = _strip_code_blocks(content)
                refs = FILE_REF_PATTERN.findall(cleaned)
                for ref_path, _ in refs:
                    if ref_path.startswith(("http", "//", "#")):
                        continue
                    candidates = [
                        os.path.join(repo_root, ref_path),
                        os.path.join(repo_root, ".config/claude", ref_path),
                        os.path.join(os.path.dirname(fpath), ref_path),
                    ]
                    if any(os.path.exists(c) for c in candidates):
                        continue
                    if _find_in_skills(repo_root, os.path.basename(ref_path)):
                        continue
                    rel = os.path.relpath(fpath, repo_root)
                    warnings.append(f"{rel} → `{ref_path}` が存在しない")

    return warnings


def main() -> None:
    repo_root = get_repo_root()
    if not repo_root:
        return

    all_warnings: List[Tuple[str, List[str]]] = []

    git_warnings = check_git_diff(repo_root)
    if git_warnings:
        all_warnings.append(("git diff", git_warnings))

    ts_warnings = check_timestamps(repo_root)
    if ts_warnings:
        all_warnings.append(("タイムスタンプ", ts_warnings))

    ref_warnings = check_references(repo_root)
    if ref_warnings:
        all_warnings.append(("参照チェック", ref_warnings))

    if not all_warnings:
        return

    lines = ["[doc-garden] ドキュメント陳腐化の可能性:"]
    for category, warns in all_warnings:
        lines.append(f"  [{category}]")
        for w in warns[:5]:
            lines.append(f"    - {w}")

    lines.append("doc-gardener エージェントで詳細分析・自動修正できます。")

    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import sys
        print(f"[doc-garden-check] error: {e}", file=sys.stderr)
