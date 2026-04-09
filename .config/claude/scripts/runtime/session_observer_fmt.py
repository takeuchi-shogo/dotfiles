#!/usr/bin/env python3
"""Session Observer formatters.

Transcript JSONL の各エントリを人間可読な文字列に変換する。
"""

from __future__ import annotations


class C:
    """ANSI color codes."""

    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"
    RED = "\033[31m"


def thinking(text: str, compact: bool) -> str:
    """Format a thinking block."""
    if compact:
        preview = text[:120].replace("\n", " ")
        return f"[think] {preview}..."

    lines = text.strip().split("\n")
    if len(lines) <= 8:
        body = text.strip()
        return _colored(C.MAGENTA, "💭 thinking:", C.DIM, body)

    shown = "\n".join(lines[:6])
    rest = len(lines) - 6
    header = f"💭 thinking ({len(lines)} lines):"
    footer = f"  ...({rest} more lines)"
    return _colored(C.MAGENTA, header, C.DIM, shown + "\n" + footer)


def tool_use(block: dict, compact: bool) -> str:
    """Format a tool_use block."""
    name = block.get("name", "?")
    inp = block.get("input", {})

    if compact:
        return _compact_tool(name, inp)

    return _rich_tool(name, inp)


def text(body: str, compact: bool) -> str:
    """Format a text response block."""
    if compact:
        preview = body[:120].replace("\n", " ")
        return f"[text] {preview}"

    lines = body.strip().split("\n")
    if len(lines) <= 5:
        return _colored(C.GREEN, "📝 response:", "", body.strip())

    shown = "\n".join(lines[:4])
    rest = len(lines) - 4
    header = f"📝 response ({len(lines)} lines):"
    footer = f"{C.DIM}  ...({rest} more){C.RESET}"
    return f"{C.GREEN}{header}{C.RESET}\n{shown}\n{footer}"


def user(message: dict, compact: bool) -> str:
    """Format a user message."""
    content = message.get("content", "")
    if isinstance(content, list):
        texts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        content = " ".join(texts)
    if compact:
        return f"[user] {content[:100]}"
    return f"{C.YELLOW}👤 user:{C.RESET} {content[:300]}"


def system(content: str | list, compact: bool) -> str:
    """Format a system message."""
    if isinstance(content, str):
        preview = content[:100].replace("\n", " ")
    else:
        preview = str(content)[:100]
    if compact:
        return f"[system] {preview}"
    return f"{C.RED}⚙️  system:{C.RESET} {preview}"


def usage(data: dict, compact: bool) -> str:
    """Format token usage."""
    inp = data.get("input_tokens", 0)
    out = data.get("output_tokens", 0)
    cr = data.get("cache_read_input_tokens", 0)
    cw = data.get("cache_creation_input_tokens", 0)
    if compact:
        return f"[usage] in={inp} out={out} cr={cr} cw={cw}"
    return (
        f"{C.DIM}📊 tokens: in={inp:,} out={out:,}"
        f" cache_read={cr:,}"
        f" cache_create={cw:,}{C.RESET}"
    )


# --- internal helpers ---


def _colored(header_color: str, header: str, body_color: str, body: str) -> str:
    return f"{header_color}{header}{C.RESET}\n{body_color}{body}{C.RESET}"


_COMPACT_KEYS: dict[str, str] = {
    "Bash": "command",
    "Read": "file_path",
    "Write": "file_path",
    "Edit": "file_path",
    "Grep": "pattern",
    "Glob": "pattern",
    "Agent": "description",
}


def _compact_tool(name: str, inp: dict) -> str:
    key = _COMPACT_KEYS.get(name)
    if key:
        val = str(inp.get(key, "?"))[:80]
        return f"[tool] {name}: {val}"
    return f"[tool] {name}"


def _rich_tool(name: str, inp: dict) -> str:
    parts = [f"{C.CYAN}🔧 {name}{C.RESET}"]

    if name == "Bash":
        cmd = inp.get("command", "?")
        parts.append(f"  {C.DIM}$ {cmd[:200]}{C.RESET}")
    elif name in ("Read", "Write", "Edit"):
        fp = inp.get("file_path", "?")
        parts.append(f"  {C.DIM}{fp}{C.RESET}")
        if name == "Edit":
            old = inp.get("old_string", "")[:60]
            parts.append(f"  {C.DIM}old: {old}...{C.RESET}")
    elif name in ("Grep", "Glob"):
        pat = inp.get("pattern", "?")
        parts.append(f"  {C.DIM}pattern: {pat}{C.RESET}")
    elif name == "Agent":
        desc = inp.get("description", "?")
        model = inp.get("model", "default")
        parts.append(f"  {C.DIM}{desc} ({model}){C.RESET}")
    elif name == "Skill":
        skill = inp.get("skill", "?")
        parts.append(f"  {C.DIM}skill: {skill}{C.RESET}")
    else:
        for k, v in list(inp.items())[:2]:
            parts.append(f"  {C.DIM}{k}: {str(v)[:80]}{C.RESET}")

    return "\n".join(parts)


# --- structured event formatting (for observer pipeline) ---

_EVENT_FORMATTERS: dict[str, str] = {}


def format_event(ev: dict, compact: bool) -> str:
    """Format a categorized event dict for display."""
    cat = ev.get("cat", "")
    handler = _CAT_FORMATTERS.get(cat)
    if handler:
        return handler(ev, compact)
    return ""


def _fmt_skill(ev: dict, compact: bool) -> str:
    s = ev.get("skill", ev.get("evt", "?"))
    if compact:
        return f"[skill] {s}"
    return f"{C.CYAN}📦 skill: {s}{C.RESET}"


def _fmt_agent(ev: dict, compact: bool) -> str:
    desc = ev.get("description", "?")
    m = ev.get("agent_model", "?")
    if compact:
        return f"[agent] {desc} ({m})"
    return f"{C.CYAN}🤖 agent: {desc} ({m}){C.RESET}"


def _fmt_mcp(ev: dict, compact: bool) -> str:
    srv = ev.get("server", "?")
    t = ev.get("mcp_tool", "?")
    if compact:
        return f"[mcp] {srv}/{t}"
    return f"{C.CYAN}🔌 mcp: {srv}/{t}{C.RESET}"


def _fmt_hook(ev: dict, compact: bool) -> str:
    nm = ev.get("hook_name", "?")
    he = ev.get("hook_event", "")
    if compact:
        return f"[hook] {nm} ({he})"
    return f"{C.DIM}🪝 hook: {nm} ({he}){C.RESET}"


def _fmt_system(ev: dict, compact: bool) -> str:
    msg = str(ev.get("content", ev.get("evt", "")))[:120]
    if compact:
        return f"[sys] {msg}"
    return f"{C.RED}⚙️  {msg}{C.RESET}"


def _fmt_debug(ev: dict, compact: bool) -> str:
    lvl = ev.get("level", "?")
    msg = ev.get("message", "")[:120]
    if compact:
        return f"[dbg:{lvl}] {msg}"
    return f"{C.DIM}[{lvl}] {msg}{C.RESET}"


def _fmt_thinking_ev(ev: dict, compact: bool) -> str:
    return thinking(ev.get("content", ""), compact)


def _fmt_responses_ev(ev: dict, compact: bool) -> str:
    return text(ev.get("content", ""), compact)


def _fmt_user_ev(ev: dict, compact: bool) -> str:
    return user({"content": ev.get("content", "")}, compact)


def _fmt_tokens_ev(ev: dict, compact: bool) -> str:
    return usage(ev, compact)


def _fmt_tools_ev(ev: dict, compact: bool) -> str:
    return tool_use(
        {"name": ev.get("tool", "?"), "input": ev.get("input", {})},
        compact,
    )


_CAT_FORMATTERS = {
    "thinking": _fmt_thinking_ev,
    "responses": _fmt_responses_ev,
    "user": _fmt_user_ev,
    "tokens": _fmt_tokens_ev,
    "tools": _fmt_tools_ev,
    "skills": _fmt_skill,
    "agents": _fmt_agent,
    "mcp": _fmt_mcp,
    "hooks": _fmt_hook,
    "system": _fmt_system,
    "debug": _fmt_debug,
}
