#!/usr/bin/env python3
"""Type safety delta check — detects increases in type escape hatches.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext advisory on stdout

Advisory only — never blocks.
"""

from __future__ import annotations

import re
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

TS_PATTERNS = [
    (r"\bany\b", "any type"),
    (r"\bas\s+any\b", "as any cast"),
    (r"//\s*@ts-ignore", "@ts-ignore"),
    (r"//\s*@ts-expect-error", "@ts-expect-error"),
    (r"(?<!=)!(?!=)\s*[.;\)\]\n]", "non-null assertion (!)"),
]

GO_PATTERNS = [
    (r"\binterface\s*\{\s*\}", "interface{}"),
    (r"\bany\b", "any (Go 1.18+)"),
    (r'"unsafe"', "unsafe package"),
]

PY_PATTERNS = [
    (r"#\s*type:\s*ignore", "# type: ignore"),
    (r"\bAny\b", "typing.Any"),
    (r"\bcast\s*\(", "typing.cast()"),
]

_TEST_PATTERNS = re.compile(
    r"_test\.go$|\.test\.[jt]sx?$|\.spec\.[jt]sx?$|test_.*\.py$|__tests__/"
)

_EXT_MAP: dict[str, list[tuple[str, str]]] = {
    ".ts": TS_PATTERNS,
    ".tsx": TS_PATTERNS,
    ".js": TS_PATTERNS,
    ".jsx": TS_PATTERNS,
    ".go": GO_PATTERNS,
    ".py": PY_PATTERNS,
}


def _count_matches(text: str, patterns: list[tuple[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for pattern, name in patterns:
        counts[name] = len(re.findall(pattern, text))
    return counts


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

    ext = Path(file_path).suffix
    patterns = _EXT_MAP.get(ext)
    if not patterns:
        output_passthrough(data)
        return

    if _TEST_PATTERNS.search(file_path):
        output_passthrough(data)
        return

    if tool_name == "Edit":
        new_text = tool_input.get("new_string", "")
        old_text = tool_input.get("old_string", "")
        new_counts = _count_matches(new_text, patterns)
        old_counts = _count_matches(old_text, patterns)
        deltas = {
            name: new_counts.get(name, 0) - old_counts.get(name, 0)
            for name in new_counts
        }
    else:
        content = tool_input.get("content", "")
        deltas = _count_matches(content, patterns)

    findings = []
    for name, delta in deltas.items():
        if delta > 0:
            findings.append(f"  +{delta} {name}")

    if not findings:
        output_passthrough(data)
        return

    emit("type_safety_delta", {"file": file_path, "findings": findings})

    msg = f"[type-safety-delta] {ext} 型安全性の低下を検出:\n" + "\n".join(findings)
    msg += "\n💡 型安全な代替案を検討してください"
    output_context("PostToolUse", msg)


if __name__ == "__main__":
    run_hook("type-safety-delta", main, fail_closed=False)
