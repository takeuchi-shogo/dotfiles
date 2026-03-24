#!/usr/bin/env python3
"""User input jailbreak detector (UserPromptSubmit).

ユーザー入力段階で自然言語ジェイルブレイクパターンを検出する。
Layer 1 防御: LLM に到達する前にブロック。
"""

from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import guard_action, load_hook_input, run_hook

# ---------------------------------------------------------------------------
# Jailbreak patterns
# ---------------------------------------------------------------------------

JAILBREAK_PATTERNS = [
    (
        re.compile(
            r"(?i)ignore\s+(?:previous|all|above)\s+instructions?",
        ),
        "ignore-instructions",
    ),
    (
        re.compile(
            r"(?i)reveal\s+(?:your\s+)?system\s+prompt",
        ),
        "reveal-system-prompt",
    ),
    (
        re.compile(
            r"(?i)forget\s+(?:everything|your\s+instructions?)",
        ),
        "forget-instructions",
    ),
    (
        re.compile(r"<system\s*>"),
        "system-tag-forgery",
    ),
    (
        re.compile(
            r"(?i)system\s*:\s*(?:override|new\s+instruction)",
        ),
        "system-override",
    ),
]

# Base64 suspicious payload detection
BASE64_CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/=]{20,}")
SUSPICIOUS_DECODED = ("eval(", "exec(", "import os", "subprocess", "__import__")


def _check_base64(text: str) -> tuple[bool, str]:
    """Check for base64-encoded suspicious payloads."""
    for match in BASE64_CANDIDATE_RE.finditer(text):
        candidate = match.group()
        try:
            decoded = base64.b64decode(candidate, validate=True).decode(
                "utf-8", errors="ignore"
            )
        except Exception:  # noqa: BLE001
            continue
        for pattern in SUSPICIOUS_DECODED:
            if pattern in decoded:
                return True, f"base64 decoded contains '{pattern}'"
    return False, ""


def _scan_user_input(text: str) -> tuple[bool, str, str]:
    """Scan user prompt for jailbreak patterns.

    Returns (blocked, pattern_name, detail).
    """
    for regex, name in JAILBREAK_PATTERNS:
        m = regex.search(text)
        if m:
            return True, name, m.group()[:80]

    found, detail = _check_base64(text)
    if found:
        return True, "base64-payload", detail

    return False, "", ""


def main() -> None:
    data = load_hook_input()
    if not data:
        return

    user_prompt = data.get("user_prompt", "")
    if not user_prompt:
        return

    blocked, pattern_name, detail = _scan_user_input(user_prompt)

    if blocked:
        if guard_action("user-input-guard", pattern_name, detail):
            sys.exit(2)


if __name__ == "__main__":
    run_hook("user-input-guard", main, fail_closed=False)
