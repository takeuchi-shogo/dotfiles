#!/usr/bin/env python3
"""Structure Check — lightweight structural quality gate.

Detects functions with too many parameters, deep nesting, oversized files/functions.
Covers GP-006 (OCP), GP-007 (ISP), GP-008 (DIP) heuristics that golden-check.py cannot detect.

Triggered by: hooks.PostToolUse(Edit|Write)
Output: JSON with additionalContext on stdout (advisory warnings only, never blocks)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    check_tool,
    get_emitter,
    load_hook_input,
    output_context,
    output_passthrough,
    run_hook,
)

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
MAX_FUNC_PARAMS = 5
MAX_NESTING_DEPTH = 3
MAX_FILE_LINES = 300
MAX_FUNC_LINES = 50

# ---------------------------------------------------------------------------
# Language configuration
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {".go", ".ts", ".tsx", ".py", ".rs"}

TEST_FILE_PATTERNS = (
    "_test.go",
    ".test.ts",
    ".test.tsx",
    ".spec.ts",
    ".spec.tsx",
)

SKIP_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".toml"}

# ---------------------------------------------------------------------------
# Regex patterns — per language
# ---------------------------------------------------------------------------

# Function definition patterns: capture the parameter list start
# We use named groups: `name` for function name, match ends just before `(`
_FUNC_DEF: dict[str, re.Pattern[str]] = {
    ".go": re.compile(
        r"^func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(", re.MULTILINE
    ),
    ".ts": re.compile(
        r"(?:^|\s)(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*[=:]\s*(?:async\s*)?\()",
        re.MULTILINE,
    ),
    ".tsx": re.compile(
        r"(?:^|\s)(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*[=:]\s*(?:async\s*)?\()",
        re.MULTILINE,
    ),
    ".py": re.compile(
        r"^[ \t]*def\s+(\w+)\s*\(", re.MULTILINE
    ),
    ".rs": re.compile(
        r"^[ \t]*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]*>)?\s*\(", re.MULTILINE
    ),
}

# Nesting depth triggers: lines that open a new nesting scope
_NESTING_OPEN: dict[str, re.Pattern[str]] = {
    ".go":  re.compile(r"^\s*(?:if|for|switch|select)\b"),
    ".ts":  re.compile(r"^\s*(?:if|for|while|switch)\b"),
    ".tsx": re.compile(r"^\s*(?:if|for|while|switch)\b"),
    ".py":  re.compile(r"^\s*(?:if|elif|for|while|match)\b"),
    ".rs":  re.compile(r"^\s*(?:if|for|while|match|loop)\b"),
}

# Lines that close a scope (Go/TS/RS use `}`, Python uses dedent — handled separately)
_NESTING_CLOSE_BRACE = re.compile(r"^\s*\}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

emit = get_emitter()


def _is_test_file(file_path: str) -> bool:
    basename = os.path.basename(file_path)
    return any(basename.endswith(p) or basename.startswith("test_") for p in TEST_FILE_PATTERNS)


def _should_skip(file_path: str) -> bool:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in SKIP_EXTENSIONS:
        return True
    if ext not in SUPPORTED_EXTENSIONS:
        return True
    if _is_test_file(file_path):
        return True
    return False


def _resolve_content(tool_name: str, tool_input: dict) -> str:
    """Return the changed content from Edit (new_string) or Write (content)."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    return tool_input.get("new_string", "")


def _resolve_full_content(file_path: str, tool_name: str, tool_input: dict) -> str:
    """Return full file content for file-level checks.

    For Edit hooks the file already has the edit applied on disk, so we read it.
    For Write hooks the content in tool_input IS the full file.
    Falls back to empty string on any I/O error.
    """
    if tool_name == "Write":
        return tool_input.get("content", "")
    try:
        return Path(file_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Check 1: function parameter count  (GP-007 ISP)
# ---------------------------------------------------------------------------

def _extract_params(param_str: str, ext: str) -> int:
    """Count parameters from a raw parameter-list string (between parentheses).

    Handles nested generics/brackets by tracking depth.
    Returns 0 if the string appears empty.
    """
    # Strip outer parens if present
    s = param_str.strip()
    if not s:
        return 0

    # Walk character-by-character, splitting on top-level commas
    depth = 0
    parts = 0
    in_content = False

    for ch in s:
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>" :
            depth -= 1
        elif ch == "," and depth == 0:
            parts += 1
            in_content = False
            continue
        if ch not in " \t\n" and not in_content:
            in_content = True

    # parts+1 only if there was actual content
    if in_content or parts > 0:
        return parts + 1
    return 0


def _find_param_list(content: str, match_end: int) -> tuple[str, int]:
    """Starting at match_end (just after `(`), collect the balanced param list.

    Returns (param_content, line_number_of_open_paren).
    """
    depth = 1
    i = match_end
    buf: list[str] = []
    while i < len(content) and depth > 0:
        ch = content[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        buf.append(ch)
        i += 1
    return "".join(buf), content[:match_end].count("\n") + 1


def check_func_params(content: str, file_path: str) -> list[str]:
    ext = os.path.splitext(file_path)[1].lower()
    pattern = _FUNC_DEF.get(ext)
    if not pattern:
        return []

    warnings: list[str] = []
    for m in pattern.finditer(content):
        # Find the opening paren position
        paren_pos = content.find("(", m.start())
        if paren_pos == -1:
            continue
        param_str, line_no = _find_param_list(content, paren_pos + 1)
        count = _extract_params(param_str, ext)
        if count > MAX_FUNC_PARAMS:
            fname = next((g for g in m.groups() if g), "<anonymous>")
            warnings.append(
                f"[structure-check] \u26a0 {file_path}:{line_no} \u2014 "
                f"[GP-007 ISP] 関数 `{fname}` の引数が {count} 個 (閾値: {MAX_FUNC_PARAMS})。"
                "引数オブジェクトへの集約またはインターフェース分割を検討してください。"
            )
    return warnings


# ---------------------------------------------------------------------------
# Check 2: nesting depth  (GP-006 OCP)
# ---------------------------------------------------------------------------

def _nesting_depth_brace(lines: list[str], open_pat: re.Pattern[str]) -> int:
    """Track brace-based nesting depth for Go/TS/RS."""
    max_depth = 0
    depth = 0
    for line in lines:
        stripped = line.strip()
        if open_pat.match(line) and stripped.endswith("{"):
            depth += 1
            max_depth = max(max_depth, depth)
        elif _NESTING_CLOSE_BRACE.match(line):
            depth = max(0, depth - 1)
        elif open_pat.match(line):
            # opening keyword without same-line brace — depth will increase later
            depth += 1
            max_depth = max(max_depth, depth)
    return max_depth


def _nesting_depth_indent(lines: list[str], open_pat: re.Pattern[str]) -> int:
    """Track indent-based nesting depth for Python."""
    max_depth = 0
    depth = 0
    prev_indent = 0
    for line in lines:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent < prev_indent:
            dedent_levels = (prev_indent - indent) // 4
            depth = max(0, depth - dedent_levels)
        if open_pat.match(line):
            depth += 1
            max_depth = max(max_depth, depth)
        prev_indent = indent
    return max_depth


def check_nesting_depth(content: str, file_path: str) -> list[str]:
    ext = os.path.splitext(file_path)[1].lower()
    open_pat = _NESTING_OPEN.get(ext)
    if not open_pat:
        return []

    lines = content.splitlines()
    if ext == ".py":
        depth = _nesting_depth_indent(lines, open_pat)
    else:
        depth = _nesting_depth_brace(lines, open_pat)

    if depth > MAX_NESTING_DEPTH:
        return [
            f"[structure-check] \u26a0 {file_path} \u2014 "
            f"[GP-006 OCP] 条件分岐のネスト深さ {depth} 段 (閾値: {MAX_NESTING_DEPTH})。"
            "早期リターン・ポリモーフィズム・ストラテジーパターンを検討してください。"
        ]
    return []


# ---------------------------------------------------------------------------
# Check 3: file line count
# ---------------------------------------------------------------------------

def check_file_lines(content: str, file_path: str) -> list[str]:
    line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
    if line_count > MAX_FILE_LINES:
        return [
            f"[structure-check] \u26a0 {file_path} \u2014 "
            f"ファイル行数 {line_count} 行 (閾値: {MAX_FILE_LINES})。"
            "責務の分割・モジュール分離を検討してください。"
        ]
    return []


# ---------------------------------------------------------------------------
# Check 4: function body line count  (GP-008 DIP — oversized impl)
# ---------------------------------------------------------------------------

def check_func_body_lines(content: str, file_path: str) -> list[str]:
    ext = os.path.splitext(file_path)[1].lower()
    pattern = _FUNC_DEF.get(ext)
    if not pattern:
        return []

    lines = content.splitlines()
    warnings: list[str] = []

    for m in pattern.finditer(content):
        func_start_line = content[:m.start()].count("\n")  # 0-indexed
        fname = next((g for g in m.groups() if g), "<anonymous>")

        if ext == ".py":
            # Python: body ends when indentation returns to base level
            base_indent = len(lines[func_start_line]) - len(lines[func_start_line].lstrip())
            body_lines = 0
            for line in lines[func_start_line + 1:]:
                stripped = line.strip()
                if not stripped:
                    body_lines += 1
                    continue
                indent = len(line) - len(line.lstrip())
                if indent <= base_indent:
                    break
                body_lines += 1
        else:
            # Brace-based: find the opening `{` then track balance
            open_brace = content.find("{", m.end())
            if open_brace == -1:
                continue
            depth = 1
            i = open_brace + 1
            while i < len(content) and depth > 0:
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                i += 1
            func_end_line = content[:i].count("\n")
            body_lines = func_end_line - func_start_line

        if body_lines > MAX_FUNC_LINES:
            line_no = func_start_line + 1
            warnings.append(
                f"[structure-check] \u26a0 {file_path}:{line_no} \u2014 "
                f"[GP-008 DIP] 関数 `{fname}` の本体が {body_lines} 行 (閾値: {MAX_FUNC_LINES})。"
                "依存関係の注入・責務分割を検討してください。"
            )

    return warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    data = load_hook_input()
    if not data:
        return

    if not check_tool(data, ["Edit", "Write"]):
        output_passthrough(data)
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or _should_skip(file_path):
        output_passthrough(data)
        return

    changed_content = _resolve_content(tool_name, tool_input)
    full_content = _resolve_full_content(file_path, tool_name, tool_input)

    if not changed_content and not full_content:
        output_passthrough(data)
        return

    warnings: list[str] = []

    # Run checks against the changed fragment (param / nesting) and full file
    check_target = changed_content or full_content

    warnings += check_func_params(check_target, file_path)
    warnings += check_nesting_depth(check_target, file_path)
    warnings += check_file_lines(full_content, file_path)
    warnings += check_func_body_lines(check_target, file_path)

    if warnings:
        for w in warnings:
            print(w, file=sys.stderr)
            emit(
                "quality",
                {
                    "rule": "structure-check",
                    "file": file_path,
                    "detail": w[:200],
                },
            )
        output_context("PostToolUse", "\n".join(warnings))
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("structure-check", main)
