#!/usr/bin/env python3
"""MCP response content inspector (PostToolUse/mcp__.*).

VeriGrey (arXiv:2603.17639) Gap #5: MCP サーバーのレスポンスに
埋め込まれたインジェクションパターンを検査する。
AgentWatcher (arXiv:2604.01194) の 10 種ルール分類に基づくルール ID 付きログ。

強度:
  - デフォルト: Soft warning (advisory) — 検出時は stderr + ログ記録、ブロックしない。
  - MCP_INSPECTOR_MODE=block: 高信頼度パターン (R2/R3/R4) はブロック。

ルール分類: references/injection-rule-taxonomy.md
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import (
    get_emitter,
    load_hook_input,
    output_context,
    output_passthrough,
    rotate_and_append,
    run_hook,
)

MAX_RESPONSE_SIZE = 10 * 1024  # 10KB truncation limit
LARGE_CONTENT_THRESHOLD = 5 * 1024  # 5KB — contextual learning bias advisory

# Block mode: MCP_INSPECTOR_MODE=block enables blocking for HIGH-confidence rules
BLOCK_MODE = os.environ.get("MCP_INSPECTOR_MODE", "warn") == "block"

# ---------------------------------------------------------------------------
# AgentWatcher Rule ID mapping (arXiv:2604.01194)
# See references/injection-rule-taxonomy.md for full taxonomy
# ---------------------------------------------------------------------------
# Confidence: HIGH = block-eligible, MEDIUM = warn, LOW = log-only
RULE_MAP: dict[str, tuple[str, str]] = {
    "injection-directive": ("R1/R2", "HIGH"),  # Hijacking or System Override
    "url-secret-cooccurrence": ("R4", "HIGH"),  # Resource Exfiltration
    "zero-width-char": ("R10", "MEDIUM"),  # System Spoofing (obfuscation)
    "ansi-escape": ("R10", "MEDIUM"),  # System Spoofing (obfuscation)
    "null-byte": ("R10", "MEDIUM"),  # System Spoofing (obfuscation)
    "css-display-none": ("R6", "LOW"),  # Attention Diversion
    "css-visibility-hidden": ("R6", "LOW"),  # Attention Diversion
    "css-offscreen": ("R6", "LOW"),  # Attention Diversion
    "aria-label-injection": ("R1", "MEDIUM"),  # Instruction Hijacking
    "markdown-link-injection": ("R9", "MEDIUM"),  # External Redirection
    "html-comment-injection": ("R1", "MEDIUM"),  # Instruction Hijacking
}

# ---------------------------------------------------------------------------
# Injection directive patterns (natural-language social engineering)
# ---------------------------------------------------------------------------
INJECTION_DIRECTIVES = re.compile(
    r"(?i)"
    r"(?:ignore\s+(?:previous|all|above)\s+(?:instructions?|context))"
    r"|(?:before\s+you\s+can\s+solve)"
    r"|(?:重要なメッセージ)"
    r"|(?:IMPORTANT\s*:\s*(?:you\s+must|first|before))"
    r"|(?:system\s*:\s*(?:override|new\s+instruction))"
    r"|(?:forget\s+(?:everything|your\s+instructions?))"
)

# ---------------------------------------------------------------------------
# URL + secret reference co-occurrence
# ---------------------------------------------------------------------------
URL_RE = re.compile(r"https?://[^\s\"'<>]+")
SECRET_RE = re.compile(
    r"(?i)(?:SECRET|API_KEY|TOKEN|PASSWORD|CREDENTIALS|\.env\b|private_key)"
)

# ---------------------------------------------------------------------------
# Technical injection patterns (reused from prompt-injection-detector.py)
# Built dynamically to avoid triggering the injection detector on this source.
# ---------------------------------------------------------------------------
ZERO_WIDTH_RE = re.compile("[\u200b\u200c\u200d\ufeff]")
ANSI_ESCAPE_RE = re.compile(re.escape("\x1b") + r"\[")
NULL_BYTE_RE = re.compile(chr(0))

# ---------------------------------------------------------------------------
# Content Injection patterns (CSS/HTML obfuscation) — Franklin et al. (2026)
# WASP benchmark: up to 86% partial control via these techniques
# ---------------------------------------------------------------------------
CONTENT_INJECTION_PATTERNS = [
    (re.compile(r"display\s*:\s*none", re.IGNORECASE), "css-display-none"),
    (re.compile(r"visibility\s*:\s*hidden", re.IGNORECASE), "css-visibility-hidden"),
    (
        re.compile(
            r"position\s*:\s*absolute[^;\"']*"
            r"(?:left|top|right|bottom)\s*:\s*-\d{4,}px",
            re.IGNORECASE,
        ),
        "css-offscreen",
    ),
    (
        re.compile(
            r"aria-label\s*=\s*[\"'][^\"']*"
            r"(?:ignore|system|instructions?|exfiltrate)"
            r"[^\"']*[\"']",
            re.IGNORECASE,
        ),
        "aria-label-injection",
    ),
]

# ---------------------------------------------------------------------------
# Syntactic Masking patterns (Markdown/HTML comment obfuscation)
# ---------------------------------------------------------------------------
SYNTACTIC_MASKING_PATTERNS = [
    (
        re.compile(
            r"\[(?:[^\]]*(?:system|ignore|exfiltrate|override)[^\]]*)\]\([^\)]+\)",
            re.IGNORECASE,
        ),
        "markdown-link-injection",
    ),
    (
        re.compile(
            r"<!--[^>]*(?:ignore|system|instructions|override)[^>]*-->",
            re.IGNORECASE,
        ),
        "html-comment-injection",
    ),
]


def _inspect(text: str) -> tuple[str, str] | None:
    """Inspect text for injection patterns.

    Returns (pattern_name, detail) or None.
    """
    m = INJECTION_DIRECTIVES.search(text)
    if m:
        return "injection-directive", m.group()[:80]

    if URL_RE.search(text) and SECRET_RE.search(text):
        return "url-secret-cooccurrence", "URL + secret reference in MCP response"

    if ZERO_WIDTH_RE.search(text):
        return "zero-width-char", "Zero-width character in MCP response"

    if ANSI_ESCAPE_RE.search(text):
        return "ansi-escape", "ANSI escape sequence in MCP response"

    if NULL_BYTE_RE.search(text):
        return "null-byte", "Null byte in MCP response"

    for pattern, name in CONTENT_INJECTION_PATTERNS:
        m = pattern.search(text)
        if m:
            return name, m.group()[:80]

    for pattern, name in SYNTACTIC_MASKING_PATTERNS:
        m = pattern.search(text)
        if m:
            return name, m.group()[:80]

    return None


def _log_finding(data: dict, pattern_name: str, detail: str, log_path: str) -> None:
    rule_id, confidence = RULE_MAP.get(pattern_name, ("R?", "LOW"))
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": data.get("tool_name", ""),
        "pattern": pattern_name,
        "rule_id": rule_id,
        "confidence": confidence,
        "detail": detail[:200],
        "session_id": data.get("session_id", "unknown"),
    }
    rotate_and_append(log_path, json.dumps(entry))


def _main() -> None:
    data = load_hook_input()
    if not data:
        return

    tool_name = data.get("tool_name", "")
    if not tool_name.startswith("mcp__"):
        output_passthrough(data)
        return

    tool_output = data.get("tool_output", "") or ""
    if not isinstance(tool_output, str):
        tool_output = str(tool_output)

    # Truncate large responses
    if len(tool_output) > MAX_RESPONSE_SIZE:
        tool_output = tool_output[:MAX_RESPONSE_SIZE]

    result = _inspect(tool_output)

    # T9: Large content advisory (contextual learning bias)
    if len(tool_output) > LARGE_CONTENT_THRESHOLD and not result:
        msg = (
            f"[MCP Response Inspector] {tool_name} のレスポンスが "
            f"{len(tool_output)}B ({len(tool_output) / 1024:.1f}KB) — "
            f"外部コンテンツによる in-context learning バイアスに注意"
        )
        print(msg, file=sys.stderr)

    if result:
        pattern_name, detail = result

        # Log finding
        log_dir = os.path.expanduser("~/.claude/agent-memory/logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "mcp-response-inspection.jsonl")
        _log_finding(data, pattern_name, detail, log_path)

        # Resolve rule ID and confidence
        rule_id, confidence = RULE_MAP.get(pattern_name, ("R?", "LOW"))

        # Emit event
        emit = get_emitter()
        emit(
            "security",
            {
                "type": "mcp_response_injection",
                "pattern": pattern_name,
                "rule_id": rule_id,
                "confidence": confidence,
                "tool": tool_name,
            },
        )

        # Write suspicious flag for PreToolUse block chain (atomic via tempfile)
        import tempfile

        flag_dir = os.path.expanduser("~/.claude/agent-memory/flags")
        os.makedirs(flag_dir, exist_ok=True)
        flag_path = os.path.join(flag_dir, "mcp-suspicious.json")
        flag_entry = {
            "tool": tool_name,
            "pattern": pattern_name,
            "rule_id": rule_id,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            with tempfile.NamedTemporaryFile(
                "w", dir=flag_dir, suffix=".json", delete=False, encoding="utf-8"
            ) as tmp:
                json.dump(flag_entry, tmp)
                tmp_path = tmp.name
            os.replace(tmp_path, flag_path)
        except OSError as exc:
            print(f"[MCP Response Inspector] flag write error: {exc}", file=sys.stderr)

        # Block HIGH-confidence patterns when block mode is enabled
        if BLOCK_MODE and confidence == "HIGH":
            msg = (
                f"[MCP Response Inspector] BLOCKED: {tool_name} — "
                f"rule {rule_id} ({pattern_name}): {detail}"
            )
            print(msg, file=sys.stderr)
            print(json.dumps({"error": msg}))
            return

        # Soft warning (advisory, do not block)
        msg = (
            f"[MCP Response Inspector] {tool_name} のレスポンスに"
            f"疑わしいパターンを検出: [{rule_id}] {pattern_name} — {detail}"
        )
        print(msg, file=sys.stderr)
        output_context("PostToolUse", msg)
        return

    output_passthrough(data)


if __name__ == "__main__":
    run_hook("mcp-response-inspector", _main, fail_closed=False)
