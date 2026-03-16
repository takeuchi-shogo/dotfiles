#!/usr/bin/env python3
"""Golden Principles check — detects deviations on file edit/write.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext warning on stdout
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    load_hook_input,
    output_passthrough,
    output_context,
    check_tool,
    run_hook,
    get_emitter,
)

WARNING_COOLDOWN_SECONDS = 300  # 5 minutes
WARNING_STATE_FILE = (
    Path(
        os.environ.get(
            "CLAUDE_SESSION_STATE_DIR",
            os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
        ),
    )
    / "golden-warnings.json"
)


def _load_warning_state() -> dict:
    try:
        return json.loads(WARNING_STATE_FILE.read_text())
    except Exception:
        return {}


def _save_warning_state(state: dict) -> None:
    try:
        WARNING_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        WARNING_STATE_FILE.write_text(json.dumps(state))
    except OSError:
        pass  # Non-critical state — loss is acceptable


def _is_duplicate_warning(file_path: str, rule: str) -> bool:
    """同じファイル+ルールの警告がクールダウン期間内に出ていたら True."""
    state = _load_warning_state()
    now = time.time()
    key = f"{file_path}:{rule}"
    last_warned = state.get(key, 0)
    if now - last_warned < WARNING_COOLDOWN_SECONDS:
        return True
    # Prune old entries and record this warning
    state = {k: v for k, v in state.items() if now - v < WARNING_COOLDOWN_SECONDS}
    state[key] = now
    _save_warning_state(state)
    return False


emit = get_emitter()


DEPENDENCY_FILES = {
    "package.json",
    "go.mod",
    "Cargo.toml",
    "requirements.txt",
    "pyproject.toml",
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

# GP-002 Guard: Only apply boundary validation to input-boundary files
# AgentRx-inspired guarded evaluation — constraints apply only in relevant context
_BOUNDARY_FILE_KEYWORDS = (
    "handler",
    "controller",
    "api",
    "endpoint",
    "cmd",
    "route",
    "server",
    "middleware",
    "view",
)

# GP-005 Guard: Skip type safety checks in test files
_TEST_FILE_PATTERNS = (
    "_test.go",
    ".test.ts",
    ".test.tsx",
    ".test.js",
    ".test.jsx",
    ".spec.ts",
    ".spec.tsx",
    ".spec.js",
    ".spec.jsx",
    "_test.py",
    "test_",
)


def _is_boundary_file(file_path: str) -> bool:
    """Check if a file is at an input boundary (handler, controller, etc.)."""
    lower = file_path.lower()
    return any(kw in lower for kw in _BOUNDARY_FILE_KEYWORDS)


def _is_test_file(file_path: str) -> bool:
    """Check if a file is a test file."""
    basename = os.path.basename(file_path).lower()
    return any(
        basename.endswith(p) or basename.startswith(p) for p in _TEST_FILE_PATTERNS
    )


# GP-002: Boundary validation — raw input used without validation
RAW_INPUT_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "js": [
        re.compile(r"req\.body\["),
        re.compile(r"req\.query\["),
        re.compile(r"req\.params\["),
        re.compile(r"request\.body\["),
    ],
    "py": [
        re.compile(r"sys\.argv\["),
        re.compile(r"request\.form\["),
        re.compile(r"request\.args\["),
        re.compile(r"request\.json\["),
    ],
    "go": [
        re.compile(r"os\.Args\["),
        re.compile(r"r\.URL\.Query\(\)\.Get\("),
        re.compile(r"r\.FormValue\("),
    ],
}


def _strip_comment_lines(content: str, ext: str) -> str:
    """Remove single-line comment lines before pattern matching."""
    if ext in (".py",):
        return "\n".join(
            line for line in content.splitlines() if not line.lstrip().startswith("#")
        )
    if ext in (".ts", ".tsx", ".js", ".jsx", ".go"):
        return "\n".join(
            line for line in content.splitlines() if not line.lstrip().startswith("//")
        )
    return content


def check_boundary_validation(content: str, file_path: str = "") -> str | None:
    """Detect raw external input access without boundary validation (GP-002).

    Guarded: Only applies to input-boundary files (handler, controller, etc.).
    Strips comment lines to reduce false positives.
    """
    # Guard condition: skip non-boundary files (AgentRx guarded evaluation)
    if file_path and not _is_boundary_file(file_path):
        return None

    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".ts", ".tsx", ".js", ".jsx"):
        patterns = RAW_INPUT_PATTERNS["js"]
    elif ext == ".py":
        patterns = RAW_INPUT_PATTERNS["py"]
    elif ext == ".go":
        patterns = RAW_INPUT_PATTERNS["go"]
    else:
        return None

    filtered = _strip_comment_lines(content, ext)
    for pattern in patterns:
        if pattern.search(filtered):
            return (
                "[GP-002] 外部入力の直接使用が検出されました。"
                "バウンダリでバリデーションを行ってください（Zod, Pydantic 等）。"
            )
    return None


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
    # Guard condition: skip test files (AgentRx guarded evaluation)
    if file_path and _is_test_file(file_path):
        return None

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


def check_ghost_file(file_path: str, tool_name: str) -> str | None:
    """Detect creation of new files when similar files already exist (GP-009).

    Only triggers for Write tool (new file creation).
    """
    if tool_name != "Write":
        return None
    if os.path.exists(file_path):
        return None  # Overwrite of existing file, not ghost

    dir_path = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(basename)[0].lower()

    if not dir_path or not os.path.isdir(dir_path):
        return None

    try:
        existing = os.listdir(dir_path)
    except OSError:
        return None

    for existing_file in existing:
        existing_name = os.path.splitext(existing_file)[0].lower()
        ratio = SequenceMatcher(None, name_without_ext, existing_name).ratio()
        if ratio > 0.7 and existing_file != basename:
            return (
                f"[GP-009] 類似名のファイル `{existing_file}` が同ディレクトリに存在します。"
                "新規作成ではなく既存ファイルの修正を検討してください。"
            )
    return None


def check_comment_ratio(content: str, file_path: str = "") -> str | None:
    """Detect excessive comment-to-code ratio (GP-010).

    Warns when comment lines exceed 40% of total non-empty lines.
    Skips files under 20 lines (too small to judge).
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".md", ".txt", ".json", ".yaml", ".yml", ".toml"):
        return None  # Non-code files

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) < 20:
        return None

    comment_markers = {
        ".py": ("#",),
        ".ts": ("//",),
        ".tsx": ("//",),
        ".js": ("//",),
        ".jsx": ("//",),
        ".go": ("//",),
        ".rs": ("//",),
        ".sh": ("#",),
        ".bash": ("#",),
    }
    markers = comment_markers.get(ext, ("//", "#"))
    comment_count = sum(1 for line in lines if any(line.startswith(m) for m in markers))
    ratio = comment_count / len(lines)

    if ratio > 0.4:
        pct = int(ratio * 100)
        return (
            f"[GP-010] コメント比率が {pct}% と高すぎます（閾値: 40%）。"
            "コードが自己文書化されるよう、冗長なコメントを削除してください。"
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

    checks: list[tuple[str, str | None]] = [
        ("GP-002", check_boundary_validation(content, file_path)),
        ("GP-003", check_dependency_file(file_path)),
        ("GP-004", check_empty_catch(content)),
        ("GP-005", check_unsafe_types(content, file_path)),
        ("GP-009", check_ghost_file(file_path, tool_name)),
        ("GP-010", check_comment_ratio(content, file_path)),
    ]

    for rule, warn in checks:
        if warn and not _is_duplicate_warning(file_path, rule):
            warnings.append(warn)
            emit(
                "quality",
                {
                    "rule": rule,
                    "file": file_path,
                    "detail": warn[:200],
                },
            )

    if warnings:
        warnings.append(
            "golden-cleanup エージェントで詳細なプリンシプルスキャンを実行できます。"
        )
        output_context("PostToolUse", "\n".join(warnings))
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("golden-check", main)
