#!/usr/bin/env python3
"""
Measure total instruction budget exposed to the model per session.

Categories:
  - claude_md: CLAUDE.md content (always exposed)
  - references: ~/.claude/references/*.md files (loaded on demand)
  - mcp_descriptions: MCP tool descriptions (estimated from settings.json)
  - skill_descriptions: SKILL.md frontmatter `description` fields (always exposed)

Note: a `hook_injected` category (hook output text injected into the prompt)
existed here until 2026-08-03 but was removed. No producer in this repo ever
wrote the hook-output-body log format it read (`session-*.jsonl` with
`hook_output`/`tool_result`/`context_injection` events), so it always
measured 0 -- a silent zero, not a real measurement. Reviving it requires
first building a mechanism that logs hook output bodies to JSONL; see
docs/research/2026-08-03-prompt-improver-nudge-injection-absorb-analysis.md.

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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import get_references_dir  # noqa: E402

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
            "measurable": False,
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
            "measurable": False,
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
            "measurable": False,
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


def measure_references() -> dict:
    """Measure total line count of ~/.claude/references/*.md files.

    These are not always exposed, but represent the on-demand instruction budget.
    Recorded separately as 'available_budget' rather than 'active_budget'.
    """
    refs_dir = get_references_dir()
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
            "measurable": False,
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
    """Collect all budget measurements and return (results_dict, log_path).

    Status priority: degraded outranks warn. Each of claude_md/
    mcp_descriptions/skill_descriptions marks its own early-return fallback
    branches with an explicit `"measurable": False` key when the branch
    means "could not measure this" (missing file, missing dir, unparseable
    JSON) rather than "measured and the answer is zero" (e.g. 0 enabled MCP
    servers is a legitimate, fully-measured value). Only components carrying
    `measurable: False` count as degraded_sources; `note` alone is not a
    signal because measure_mcp_descriptions also attaches a `note` to its
    normal success path (the "~N tokens/server approximation" explanation).
    `references` is excluded here because it's advisory-only and already
    outside total_tokens_est.

    threshold_exceeded is recorded independently of status, and is
    tri-state: True / False / None. Component totals are non-negative, so
    a partial sum (computed while some components are unmeasurable) that
    already exceeds THRESHOLD_TOKENS proves the true total exceeds it too
    — that stays True even when status is "degraded". The converse does
    not hold: a partial sum under the threshold says nothing about the
    unmeasured remainder, so that case is None (unknown), never False.
    Reporting False there would assert "within budget" from an
    incomplete measurement, which is the exact silent-misinformation
    this module was fixed to stop emitting (2026-08-03).
    """
    components = [
        measure_claude_md(claude_dir),
        measure_mcp_descriptions(claude_dir / "settings.json"),
        measure_skill_descriptions(claude_dir),
    ]
    references_info = measure_references()
    total_tokens = sum(c["tokens_est"] for c in components)
    degraded_sources = [c["source"] for c in components if c.get("measurable") is False]
    if total_tokens > THRESHOLD_TOKENS:
        threshold_exceeded = True
    elif degraded_sources:
        threshold_exceeded = None
    else:
        threshold_exceeded = False
    if degraded_sources:
        status = "degraded"
    elif threshold_exceeded:
        status = "warn"
    else:
        status = "ok"
    results = {
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "components": components,
        "references_advisory": references_info,
        "total_tokens_est": total_tokens,
        "threshold": THRESHOLD_TOKENS,
        "status": status,
        "degraded_sources": degraded_sources,
        "threshold_exceeded": threshold_exceeded,
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
    if results.get("degraded_sources"):
        reason = f"measurement unavailable for {', '.join(results['degraded_sources'])}"
        if results.get("threshold_exceeded"):
            reason += "; partial total already exceeds threshold"
        print(f"  degraded: {reason}")
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
