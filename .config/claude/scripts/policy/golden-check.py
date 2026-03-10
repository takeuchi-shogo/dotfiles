#!/usr/bin/env python3
from __future__ import annotations
"""Golden Principles check — detects deviations on file edit/write.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext warning on stdout
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input, output_passthrough, output_context,
    check_tool, run_hook, get_emitter,
)

emit = get_emitter()


DEPENDENCY_FILES = {
    "package.json", "go.mod", "Cargo.toml",
    "requirements.txt", "pyproject.toml",
}

EMPTY_CATCH_PATTERNS = [
    re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}", re.MULTILINE),
    re.compile(r"except\s*.*:\s*\n\s*pass", re.MULTILINE),
]

UNSAFE_TYPE_PATTERNS = [
    re.compile(r":\s*any\b"),
    re.compile(r"\bas\s+any\b"),
    re.compile(r"\binterface\{\}"),
]


def check_dependency_file(file_path: str) -> str | None:
    basename = os.path.basename(file_path)
    if basename in DEPENDENCY_FILES:
        return (
            f"[GP-003] 依存ファイル `{basename}` が変更されました。"
            "新規依存の追加は慎重に — 退屈な技術を好む原則を確認してください。"
        )
    return None


def check_empty_catch(content: str) -> str | None:
    for pattern in EMPTY_CATCH_PATTERNS:
        if pattern.search(content):
            return (
                "[GP-004] 空の catch/except ブロックが検出されました。"
                "エラーを握り潰さず、適切にハンドリングしてください。"
            )
    return None


def check_unsafe_types(content: str, file_path: str = "") -> str | None:
    ext = os.path.splitext(file_path)[1].lower()
    patterns: list[re.Pattern[str]] = []
    if ext in (".ts", ".tsx", ".js", ".jsx"):
        patterns = [re.compile(r":\s*any\b"), re.compile(r"\bas\s+any\b")]
    elif ext in (".go",):
        patterns = [re.compile(r"\binterface\{\}")]
    # Python Any is generally acceptable; skip for .py

    for pattern in patterns:
        if pattern.search(content):
            return (
                "[GP-005] `any` または `interface{}` の使用が検出されました。"
                "具体的な型を使用し、型安全性を維持してください。"
            )
    return None


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    if not check_tool(data, ["Edit", "Write"]):
        output_passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Write uses 'content', Edit uses 'new_string'
    tool_name = data.get("tool_name", "")
    if tool_name == "Write":
        content = tool_input.get("content", "")
    else:
        content = tool_input.get("new_string", "")

    if not content:
        content = data.get("tool_output", "") or ""

    warnings: list[str] = []

    dep_warn = check_dependency_file(file_path)
    if dep_warn:
        warnings.append(dep_warn)
        emit("quality", {
            "rule": "GP-003",
            "file": file_path,
            "detail": dep_warn[:200],
        })

    catch_warn = check_empty_catch(content)
    if catch_warn:
        warnings.append(catch_warn)
        emit("quality", {
            "rule": "GP-004",
            "file": file_path,
            "detail": catch_warn[:200],
        })

    type_warn = check_unsafe_types(content, file_path)
    if type_warn:
        warnings.append(type_warn)
        emit("quality", {
            "rule": "GP-005",
            "file": file_path,
            "detail": type_warn[:200],
        })

    if warnings:
        warnings.append(
            "golden-cleanup エージェントで詳細なプリンシプルスキャンを実行できます。"
        )
        output_context("PostToolUse", "\n".join(warnings))
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("golden-check", main)
