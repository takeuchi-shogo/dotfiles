#!/usr/bin/env python3
"""
Measure total instruction budget exposed to the model per session.

Categories:
  - claude_md: CLAUDE.md content (always exposed)
  - references: ~/.claude/references/*.md files (loaded on demand)
  - hook_injected: PreToolUse/PostToolUse hook outputs from recent session
  - mcp_descriptions: MCP tool descriptions (estimated from settings.json)
  - skill_descriptions: SKILL.md frontmatter `description` fields (always exposed)

Output: JSONL to ~/.claude/logs/instruction-budget-YYYY-MM-DD.jsonl
Threshold: warn if total > 6000 tokens (approx. Stanford "Lost in the Middle"
           2000-token safe zone x3 for headroom)

Usage:
  python3 measure-instruction-budget.py   # observe-only (exit 0 unless > threshold)
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

THRESHOLD_TOKENS = 6000
CHARS_PER_TOKEN = 4  # rough estimate: ~4 chars per token for Japanese/English mixed


# ---------------------------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------------------------


def measure_claude_md(claude_dir: Path) -> dict:
    """Measure CLAUDE.md character count and token estimate."""
    claude_md = claude_dir / "CLAUDE.md"
    if not claude_md.exists():
        return {
            "source": "claude_md",
            "chars": 0,
            "tokens_est": 0,
            "note": "file not found",
        }
    chars = len(claude_md.read_text(encoding="utf-8"))
    return {
        "source": "claude_md",
        "chars": chars,
        "tokens_est": chars // CHARS_PER_TOKEN,
    }


def measure_mcp_descriptions(settings_path: Path) -> dict:
    """Estimate MCP tool description budget from settings.json.

    Real descriptions are only accessible via running MCP servers, so we use
    a conservative approximation: 500 tokens per enabled server.
    """
    TOKENS_PER_MCP_SERVER = 500

    if not settings_path.exists():
        return {
            "source": "mcp_descriptions",
            "chars": 0,
            "tokens_est": 0,
            "server_count": 0,
            "note": "settings.json not found",
        }

    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {
            "source": "mcp_descriptions",
            "chars": 0,
            "tokens_est": 0,
            "server_count": 0,
            "note": f"JSON parse error: {e}",
        }

    # Count enabled MCP servers from enabledMcpjsonServers and mcpServers
    server_count = 0

    # enabledMcpjsonServers: list of server names enabled from .mcp.json files
    enabled_list = settings.get("enabledMcpjsonServers", [])
    server_count += len(enabled_list)

    # mcpServers: direct server configs in settings.json
    mcp_servers = settings.get("mcpServers", {})
    server_count += len(mcp_servers)

    tokens_est = server_count * TOKENS_PER_MCP_SERVER
    chars_est = tokens_est * CHARS_PER_TOKEN

    return {
        "source": "mcp_descriptions",
        "chars": chars_est,
        "tokens_est": tokens_est,
        "server_count": server_count,
        "note": f"~{TOKENS_PER_MCP_SERVER} tokens/server approximation",
    }


_HOOK_EVENT_TYPES = frozenset(("hook_output", "tool_result", "context_injection"))


def _extract_content_chars(record: dict) -> int:
    """Extract character count from a hook event record's content field."""
    content = record.get("content") or record.get("output") or ""
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(
            len(item.get("text", "")) for item in content if isinstance(item, dict)
        )
    return 0


def _parse_hook_log(log_path: Path) -> tuple[int, int]:
    """Parse a session JSONL log and return (total_chars, event_count)."""
    total_chars = 0
    event_count = 0
    for raw in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if record.get("type", "") not in _HOOK_EVENT_TYPES:
            continue
        chars = _extract_content_chars(record)
        if chars:
            total_chars += chars
            event_count += 1
    return total_chars, event_count


def measure_hook_outputs(log_dir: Path) -> dict:
    """Estimate hook injection size from the most recent session JSONL log.

    Looks for PreToolUse/PostToolUse hook output fields in the latest session log.
    Returns 0 if no logs are found.
    """
    if not log_dir.exists():
        return {
            "source": "hook_injected",
            "chars": 0,
            "tokens_est": 0,
            "note": "log dir not found",
        }

    session_logs = sorted(
        log_dir.glob("session-*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not session_logs:
        return {
            "source": "hook_injected",
            "chars": 0,
            "tokens_est": 0,
            "note": "no session logs found",
        }

    latest = session_logs[0]
    try:
        total_chars, event_count = _parse_hook_log(latest)
    except OSError as e:
        return {
            "source": "hook_injected",
            "chars": 0,
            "tokens_est": 0,
            "note": f"read error: {e}",
        }

    return {
        "source": "hook_injected",
        "chars": total_chars,
        "tokens_est": total_chars // CHARS_PER_TOKEN,
        "hook_events": event_count,
        "log_file": latest.name,
    }


def measure_references(claude_dir: Path) -> dict:
    """Measure total line count of ~/.claude/references/*.md files.

    These are not always exposed, but represent the on-demand instruction budget.
    Recorded separately as 'available_budget' rather than 'active_budget'.
    """
    refs_dir = claude_dir / "references"
    if not refs_dir.exists():
        return {
            "source": "references",
            "chars": 0,
            "tokens_est": 0,
            "file_count": 0,
            "total_lines": 0,
            "note": "references dir not found",
        }

    total_chars = 0
    total_lines = 0
    file_count = 0

    for md_file in sorted(refs_dir.glob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
            total_chars += len(text)
            total_lines += text.count("\n")
            file_count += 1
        except OSError:
            continue

    return {
        "source": "references",
        "chars": total_chars,
        "tokens_est": total_chars // CHARS_PER_TOKEN,
        "file_count": file_count,
        "total_lines": total_lines,
        "note": "on-demand budget (not always active)",
    }


_FRONTMATTER_RE = re.compile(r"^---\n(.+?)\n---", re.DOTALL)
_DESCRIPTION_RE = re.compile(
    r"^description:\s*(.+?)(?=\n[a-zA-Z_][a-zA-Z0-9_-]*:|\Z)",
    re.DOTALL | re.MULTILINE,
)
# Leading YAML block scalar indicator: `>`, `>-`, `>+`, `|`, `|-`, `|+`
_BLOCK_SCALAR_INDICATOR_RE = re.compile(r"^[>|][-+]?\s*\n")


def _extract_description(skill_md: Path) -> str | None:
    """Return the trimmed `description` field of a SKILL.md frontmatter, or None.

    Handles YAML block scalars (`>`, `|`, with optional `-`/`+` chomp), surrounding
    quotes, CRLF line endings, and empty values. Returns None when the field is
    absent or empty after stripping decorations.
    """
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    text = text.replace("\r\n", "\n")
    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        return None
    # Append "\n" so a description in the last position terminates at \Z.
    desc_match = _DESCRIPTION_RE.search(fm_match.group(1) + "\n")
    if not desc_match:
        return None
    raw = desc_match.group(1).strip()
    # Strip block scalar indicator line (`>`, `|`, optional `-`/`+`) so the
    # YAML syntax characters don't inflate the token count.
    raw = _BLOCK_SCALAR_INDICATOR_RE.sub("", raw, count=1).strip()
    # Strip surrounding quotes if the entire value is wrapped in matching quotes.
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        raw = raw[1:-1].strip()
    return raw or None


def measure_skill_descriptions(claude_dir: Path) -> dict:
    """Measure total chars of all SKILL.md frontmatter `description` fields.

    Skill descriptions are always injected into the system prompt, so they
    represent a continuous tax on the instruction budget. See
    `docs/specs/2026-05-04-skill-tier-pruning.md`.
    """
    skills_dir = claude_dir / "skills"
    if not skills_dir.exists():
        return {
            "source": "skill_descriptions",
            "chars": 0,
            "tokens_est": 0,
            "skill_count": 0,
            "note": "skills dir not found",
        }

    total_chars = 0
    skill_count = 0
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        desc = _extract_description(skill_md)
        if desc is None:
            continue
        total_chars += len(desc)
        skill_count += 1

    return {
        "source": "skill_descriptions",
        "chars": total_chars,
        "tokens_est": total_chars // CHARS_PER_TOKEN,
        "skill_count": skill_count,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _collect_results(claude_dir: Path, log_dir: Path) -> tuple[dict, Path]:
    """Collect all budget measurements and return (results_dict, log_path)."""
    components = [
        measure_claude_md(claude_dir),
        measure_mcp_descriptions(claude_dir / "settings.json"),
        measure_hook_outputs(log_dir),
        measure_skill_descriptions(claude_dir),
    ]
    references_info = measure_references(claude_dir)
    total_tokens = sum(c["tokens_est"] for c in components)
    results = {
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "components": components,
        "references_advisory": references_info,
        "total_tokens_est": total_tokens,
        "threshold": THRESHOLD_TOKENS,
        "status": "warn" if total_tokens > THRESHOLD_TOKENS else "ok",
    }
    log_path = log_dir / f"instruction-budget-{date.today()}.jsonl"
    return results, log_path


def _write_results(results: dict, log_path: Path) -> None:
    """Append results as JSONL to log_path."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(results, ensure_ascii=False) + "\n")


def _print_summary(results: dict, log_path: Path) -> None:
    """Print human-readable budget summary to stdout."""
    total = results["total_tokens_est"]
    status = results["status"]
    print(f"[instruction-budget] total={total} tokens, status={status}")
    for c in results["components"]:
        print(f"  {c['source']}: {c['tokens_est']} tokens")
    ref = results["references_advisory"]
    ref_tokens = ref["tokens_est"]
    ref_files = ref.get("file_count", 0)
    print(f"  references (advisory): {ref_tokens} tokens ({ref_files} files)")
    print(f"  output: {log_path}")


def main() -> None:
    claude_dir = Path.home() / ".claude"
    log_dir = claude_dir / "logs"

    results, log_path = _collect_results(claude_dir, log_dir)
    _write_results(results, log_path)
    _print_summary(results, log_path)

    if results["status"] == "warn":
        print(
            f"[WARN] instruction budget {results['total_tokens_est']} tokens"
            f" exceeds threshold {THRESHOLD_TOKENS}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
