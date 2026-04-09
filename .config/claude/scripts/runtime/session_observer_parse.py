#!/usr/bin/env python3
"""Transcript + debug log parsers for Session Observer."""

from __future__ import annotations

import re

from session_observer_router import make_event

# --- tool classification ---

_TOOL_CAT = {"Agent": "agents", "Skill": "skills"}


def _classify_tool(name: str) -> str:
    if name in _TOOL_CAT:
        return _TOOL_CAT[name]
    if name.startswith("mcp__"):
        return "mcp"
    return "tools"


# --- transcript entry parsing ---


def parse_entry(entry: dict, sid: str) -> list[dict]:
    """Parse one transcript JSONL entry into categorized events."""
    etype = entry.get("type", "")
    dispatch = _ENTRY_DISPATCH.get(etype)
    if dispatch:
        return dispatch(entry, sid)
    return []


def _parse_user(entry: dict, sid: str) -> list[dict]:
    msg = entry.get("message", {})
    content = msg.get("content", "")
    if isinstance(content, list):
        texts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        content = " ".join(texts)
    return [make_event("user", "message", sid, content=content)]


def _parse_assistant(entry: dict, sid: str) -> list[dict]:
    msg = entry.get("message", {})
    if not msg:
        return []
    events: list[dict] = []
    model = msg.get("model", "")

    for block in msg.get("content", []):
        if not isinstance(block, dict):
            continue
        handler = _BLOCK_DISPATCH.get(block.get("type", ""))
        if handler:
            ev = handler(block, model, sid)
            if ev:
                events.append(ev)

    usage = msg.get("usage")
    if usage:
        events.append(_make_usage_event(usage, model, msg, sid))

    return events


def _block_thinking(block: dict, model: str, sid: str) -> dict:
    return make_event(
        "thinking",
        "block",
        sid,
        content=block.get("thinking", ""),
        model=model,
    )


def _block_text(block: dict, model: str, sid: str) -> dict | None:
    txt = block.get("text", "")
    if not txt.strip():
        return None
    return make_event("responses", "text", sid, content=txt, model=model)


def _block_tool_use(block: dict, model: str, sid: str) -> dict:
    name = block.get("name", "?")
    cat = _classify_tool(name)
    inp = block.get("input", {})
    ev = make_event(
        cat,
        "invoke",
        sid,
        tool=name,
        tool_id=block.get("id", ""),
        input=inp,
        model=model,
    )
    if cat == "agents":
        ev["agent_type"] = inp.get("subagent_type", "")
        ev["description"] = inp.get("description", "")
        ev["agent_model"] = inp.get("model", "")
    elif cat == "skills":
        ev["skill"] = inp.get("skill", "")
    elif cat == "mcp":
        parts = name.split("__", 2)
        ev["server"] = parts[1] if len(parts) > 1 else ""
        ev["mcp_tool"] = parts[2] if len(parts) > 2 else name
    return ev


def _make_usage_event(usage: dict, model: str, msg: dict, sid: str) -> dict:
    return make_event(
        "tokens",
        "usage",
        sid,
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        cache_read=usage.get("cache_read_input_tokens", 0),
        cache_create=usage.get("cache_creation_input_tokens", 0),
        model=model,
        stop_reason=msg.get("stop_reason", ""),
    )


_BLOCK_DISPATCH = {
    "thinking": _block_thinking,
    "text": _block_text,
    "tool_use": _block_tool_use,
}

# --- attachment parsing ---

_HOOK_TYPES = {
    "hook_success",
    "hook_additional_context",
    "hook_system_message",
}


def _parse_attachment(entry: dict, sid: str) -> list[dict]:
    att = entry.get("attachment", {})
    att_type = att.get("type", "")

    if att_type in _HOOK_TYPES:
        return [
            make_event(
                "hooks",
                att_type,
                sid,
                hook_name=att.get("hookName", ""),
                hook_event=att.get("hookEvent", ""),
                content=att.get("content", ""),
                stdout=att.get("stdout", ""),
                stderr=att.get("stderr", ""),
                exit_code=att.get("exitCode"),
            )
        ]

    if att_type == "skill_listing":
        return [
            make_event(
                "skills",
                "listing",
                sid,
                count=att.get("skillCount", 0),
                content=att.get("content", "")[:200],
            )
        ]

    if att_type in ("deferred_tools_delta", "mcp_instructions_delta"):
        return [
            make_event(
                "system",
                att_type,
                sid,
                added=att.get("addedNames", []),
                removed=att.get("removedNames", []),
            )
        ]

    if att_type:
        return [make_event("system", att_type, sid, raw=att)]
    return []


def _parse_system(entry: dict, sid: str) -> list[dict]:
    msg = entry.get("message", {})
    c = str(msg.get("content", ""))[:500]
    return [make_event("system", "message", sid, content=c)]


def _parse_permission(entry: dict, sid: str) -> list[dict]:
    return [
        make_event(
            "system",
            "permission_mode",
            sid,
            mode=entry.get("permissionMode", ""),
        )
    ]


def _parse_file_snapshot(entry: dict, sid: str) -> list[dict]:
    return [make_event("system", "file_snapshot", sid)]


_ENTRY_DISPATCH = {
    "user": _parse_user,
    "assistant": _parse_assistant,
    "attachment": _parse_attachment,
    "system": _parse_system,
    "permission-mode": _parse_permission,
    "file-history-snapshot": _parse_file_snapshot,
}


# --- debug log parsing ---

_DEBUG_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T[\d:.]+Z)\s+"
    r"\[(DEBUG|ERROR|WARN)]\s+"
    r"(?:\[([^\]]+)]\s+)?"
    r"(.*)$"
)

_DEBUG_CAT_MAP = {
    "api": "debug",
    "STARTUP": "system",
    "init": "system",
    "mcp": "mcp",
    "claudeai-mcp": "mcp",
}


def parse_debug_line(line: str, sid: str) -> dict | None:
    """Parse a --debug-file line into an event."""
    m = _DEBUG_RE.match(line.strip())
    if not m:
        return None
    _ts, level, subcat, message = m.groups()
    cat = "debug"
    if subcat:
        base = subcat.split(":")[0]
        cat = _DEBUG_CAT_MAP.get(base, "debug")
    return make_event(
        cat,
        "log",
        sid,
        level=level,
        subcategory=subcat or "",
        message=message[:1000],
    )
