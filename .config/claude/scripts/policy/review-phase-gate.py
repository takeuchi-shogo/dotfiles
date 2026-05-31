#!/usr/bin/env python3
"""Review phase gate — deterministic replacement for the type:prompt gate.

Triggered by: skills/review/SKILL.md PreToolUse (Edit|Write), skill-scoped.
Input:  hook JSON on stdin (uses `transcript_path`).
Output: hookSpecificOutput.permissionDecision = "allow" | "ask".

Replaces the former LLM-judge (type:prompt) gate, which false-blocked
Edit/Write even after a Verdict was emitted or the user approved a fix.

allow when EITHER holds in the recent transcript tail:
  (A) a recent assistant text contains "## Verdict" or
      "verdict: (PASS|BLOCK|NEEDS_FIX|NEEDS_HUMAN_REVIEW)"  (Synthesis done)
  (B) a recent user text contains an explicit fix-approval phrase.
Otherwise "ask" (still exploring / no approval).

Fail-safe: missing/corrupt/empty input -> "ask" (never silently allow,
never hard-block — defer to the human).

This hook is skill-scoped, so it is only active during /review; scanning
the recent transcript tail is sufficient (no cross-session bleed).
"""

from __future__ import annotations

import json
import re
import sys
import traceback
from collections import deque
from pathlib import Path

# How many trailing transcript entries to inspect.
#
# Rationale: the gate is skill-scoped (active only during /review). A /review
# run is ~10-15 agent exchanges; the Verdict is emitted at Step 4 (Synthesis),
# and the fix-approval / Edit happens within a few entries after. 40 entries
# comfortably covers "Verdict (or approval) -> Edit" while staying bounded so an
# old Verdict from earlier in a long session is pushed out of scope. If
# production shows false-ask (Verdict pushed past the window before the Edit),
# raise this; if false-allow from stale Verdicts, lower it.
_TAIL_ENTRIES = 40

_VERDICT_RE = re.compile(
    r"verdict:\s*(PASS|BLOCK|NEEDS_FIX|NEEDS_HUMAN_REVIEW)",
    re.IGNORECASE,
)

# Explicit fix-approval phrases. Substring match (Japanese: avoid \b, which
# misbehaves across CJK boundaries). Phrases must be imperative / action forms
# so that mere mentions do NOT match:
#   - "修正は不要" (don't fix) must not match -> use "修正して", not bare "修正"
#   - "not applicable" / "git apply failed" must not match -> use "apply the
#     fix", not bare "apply"
#   - "go to step 5 first?" must not match -> use "proceed to step 5"
_APPROVAL_PHRASES = (
    # 日本語: 命令形 (誤検出しにくい)
    "修正して",
    "修正をして",
    "修正をお願い",
    "直して",
    "反映して",
    "適用して",
    "対応して",
    "fix して",
    "fixして",
    "block を解消",
    "ブロックを解消",
    "step 5 に進",
    # 英語: 動作句のみ (短い単語の部分一致を避ける)
    "apply the fix",
    "apply it",
    "apply this",
    "apply changes",
    "please apply",
    "go ahead and fix",
    "proceed with the fix",
    "proceed to step 5",
)


def _emit(decision: str, reason: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,  # "allow" | "ask"
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )


def _collect_text(content: object) -> list[str]:
    """Collect "text" content blocks; ignore tool_use/tool_result blocks."""
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "text":
            continue
        text = block.get("text")
        if isinstance(text, str):
            parts.append(text)
    return parts


def _extract_texts(entry: dict) -> tuple[str | None, str]:
    """Return (role, joined-text) for an assistant/user transcript entry."""
    msg = entry.get("message")
    if not isinstance(msg, dict):
        return None, ""
    role = msg.get("role")
    if role not in ("assistant", "user"):
        return None, ""
    return role, "\n".join(_collect_text(msg.get("content")))


def _decide(transcript_path: str) -> tuple[str, str]:
    """Return (decision, reason) by scanning the transcript tail."""
    path = Path(transcript_path)
    if not path.is_file():
        return "ask", "transcript not found — defer to human"

    # Read only the trailing window; deque bounds memory regardless of file
    # size (guards against a huge transcript exhausting memory).
    with path.open(encoding="utf-8", errors="replace") as fh:
        tail = list(deque(fh, maxlen=_TAIL_ENTRIES))

    assistant_text: list[str] = []
    user_text: list[str] = []
    parsed = 0
    corrupt = 0
    for line in tail:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            corrupt += 1  # skip a corrupt line, keep scanning the rest
            continue
        if not isinstance(entry, dict):
            continue
        parsed += 1
        role, text = _extract_texts(entry)
        if not text:
            continue
        if role == "assistant":
            assistant_text.append(text)
        elif role == "user":
            user_text.append(text)

    joined_assistant = "\n".join(assistant_text)
    if "## Verdict" in joined_assistant or _VERDICT_RE.search(joined_assistant):
        return "allow", "Verdict present in recent assistant output (Synthesis done)"

    joined_user_lower = "\n".join(user_text).lower()
    for phrase in _APPROVAL_PHRASES:
        if phrase in joined_user_lower:
            return "allow", f"user fix-approval phrase detected: {phrase!r}"

    # Distinguish "transcript was unreadable" from "genuinely still exploring":
    # if nothing parsed and lines were corrupt, surface that in the reason so a
    # fail-safe ask is not mistaken for a normal mid-review ask.
    if parsed == 0 and corrupt > 0:
        return (
            "ask",
            f"transcript unreadable ({corrupt} corrupt lines) — fail-safe to ask",
        )

    return "ask", "no Verdict and no fix-approval — still exploring"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        _emit("ask", "unreadable hook input — fail-safe to ask")
        return

    transcript_path = data.get("transcript_path") if isinstance(data, dict) else None
    if not transcript_path:
        _emit("ask", "no transcript_path — fail-safe to ask")
        return

    try:
        decision, reason = _decide(transcript_path)
    except Exception as exc:  # noqa: BLE001 — any failure must fail-safe to ask
        # Keep the stack trace for diagnosis; the reason field alone loses it.
        traceback.print_exc(file=sys.stderr)
        _emit("ask", f"gate error ({exc}) — fail-safe to ask")
        return

    _emit(decision, reason)


if __name__ == "__main__":
    main()
