#!/usr/bin/env python3
"""Impact scan — lists files that reference the edited file.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext advisory on stdout

Advisory only — never blocks.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input,
    output_passthrough,
    output_context,
    run_hook,
    get_emitter,
)

emit = get_emitter()

_SKIP_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".lock",
    ".sum",
    ".svg",
    ".png",
    ".jpg",
    ".gif",
}

_MAX_RESULTS = 10
_TIMEOUT = 4


def _get_repo_root() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _find_references(
    file_path: str,
    repo_root: str,
) -> list[str]:
    """Find files that import/reference the given file."""
    p = Path(file_path)
    stem = p.stem
    rel = str(p.relative_to(repo_root)) if repo_root else p.name

    # Build search patterns: filename stem, relative path fragments
    patterns = [stem]
    # Add path-based import pattern (e.g., "components/Button")
    rel_no_ext = str(Path(rel).with_suffix(""))
    if "/" in rel_no_ext:
        patterns.append(rel_no_ext)

    results: set[str] = set()
    for pattern in patterns:
        try:
            out = subprocess.check_output(
                [
                    "rg",
                    "--files-with-matches",
                    "--glob",
                    "!node_modules",
                    "--glob",
                    "!vendor",
                    "--glob",
                    "!.git",
                    "--glob",
                    "!*.lock",
                    "--max-count",
                    "1",
                    "-l",
                    pattern,
                    repo_root,
                ],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=_TIMEOUT,
            )
            for line in out.strip().splitlines():
                ref = line.strip()
                if ref and ref != file_path:
                    results.add(ref)
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            continue

    return sorted(results)[:_MAX_RESULTS]


def _find_doc_references(
    file_path: str,
    repo_root: str,
) -> list[str]:
    """Find docs/specs/README that mention this file."""
    stem = Path(file_path).stem
    docs_dirs = ["docs", "README.md", "CLAUDE.md"]
    results: list[str] = []

    for d in docs_dirs:
        target = os.path.join(repo_root, d)
        if not os.path.exists(target):
            continue
        try:
            out = subprocess.check_output(
                [
                    "rg",
                    "--files-with-matches",
                    "--max-count",
                    "1",
                    "-l",
                    stem,
                    target,
                ],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=_TIMEOUT,
            )
            for line in out.strip().splitlines():
                ref = line.strip()
                if ref:
                    results.append(ref)
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            continue

    return results[:5]


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        output_passthrough(data)
        return

    ext = Path(file_path).suffix
    if ext in _SKIP_EXTENSIONS:
        output_passthrough(data)
        return

    repo_root = _get_repo_root()
    if not repo_root:
        output_passthrough(data)
        return

    code_refs = _find_references(file_path, repo_root)
    doc_refs = _find_doc_references(file_path, repo_root)

    if not code_refs and not doc_refs:
        output_passthrough(data)
        return

    emit(
        "impact_scan",
        {
            "file": file_path,
            "code_refs": len(code_refs),
            "doc_refs": len(doc_refs),
        },
    )

    lines = ["[impact-scan] この変更の影響範囲:"]
    if code_refs:
        lines.append(f"  📦 コード参照 ({len(code_refs)}件):")
        for ref in code_refs[:5]:
            try:
                rel = os.path.relpath(ref, repo_root)
            except ValueError:
                rel = ref
            lines.append(f"    - {rel}")
        if len(code_refs) > 5:
            lines.append(f"    ... 他 {len(code_refs) - 5} 件")
    if doc_refs:
        lines.append(f"  📝 ドキュメント参照 ({len(doc_refs)}件):")
        for ref in doc_refs:
            try:
                rel = os.path.relpath(ref, repo_root)
            except ValueError:
                rel = ref
            lines.append(f"    - {rel}")
    lines.append("💡 上記ファイルへの影響を確認してください")

    output_context("PostToolUse", "\n".join(lines))


if __name__ == "__main__":
    run_hook("impact-scan", main, fail_closed=False)
