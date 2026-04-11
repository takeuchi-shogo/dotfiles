#!/usr/bin/env python3
"""Agent invocation logger — records Agent tool calls to agent-invocations.jsonl.

Triggered by: hooks.PostToolUse (Agent)
Input: JSON with tool_name, tool_input, tool_response on stdin
Output: passthrough (no warnings; best-effort logger)

Part of Routing Observability Wave 1:
  docs/plans/2026-04-11-routing-observability-closed-loop.md

Records one line per Agent tool invocation for later analysis by skill-audit
Dominant tier detection (Expert Collapse) and agent-level usage histograms.

Also parses cascade promotion gate markers from description (see
references/cascade-routing.md). Marker format: [cascade:<name>/step:<N>]
When present, cascade_name and cascade_step are added to the invocation
record so AutoEvolve can aggregate cascade chains by name.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import load_hook_input, output_passthrough, run_hook  # noqa: E402
from session_events import emit_agent_invocation  # noqa: E402

# Cascade marker: [cascade:<name>/step:<N>] where:
#   - name is [A-Za-z0-9_-]+ (ASCII only, see references/cascade-routing.md)
#   - step is a positive integer starting from 1 (step:0 is rejected by regex;
#     [1-9][0-9]* prevents leading zeros and forbids fullwidth digits via
#     explicit [0-9] instead of \d which would match Unicode digits).
# Only the first marker per description is captured (single cascade per
# invocation is the convention; see cascade-routing.md Anti-Patterns).
_CASCADE_MARKER_RE = re.compile(
    r"\[cascade:(?P<name>[A-Za-z0-9_-]+)/step:(?P<step>[1-9][0-9]*)\]"
)


def _extract_cascade_marker(description: str) -> dict:
    """Parse [cascade:<name>/step:<N>] from description.

    Returns dict with cascade_name and cascade_step if marker present,
    empty dict otherwise. Never raises.

    The regex alone guarantees that name is ASCII alphanumeric/underscore/
    hyphen and step is a positive integer, so no post-parse validation or
    exception handling is needed here.
    """
    if not isinstance(description, str):
        return {}
    match = _CASCADE_MARKER_RE.search(description)
    if not match:
        return {}
    return {
        "cascade_name": match.group("name"),
        "cascade_step": int(match.group("step")),
    }


def _extract_usage(tool_response: object) -> dict:
    """tool_response から token usage を抽出する (形式が揺れるため防御的に読む)."""
    if not isinstance(tool_response, dict):
        return {}
    usage = tool_response.get("usage")
    if not isinstance(usage, dict):
        return {}
    return {
        "token_in": usage.get("input_tokens") or usage.get("cache_read_input_tokens"),
        "token_out": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


def main() -> None:
    payload = load_hook_input()
    if payload.get("tool_name") != "Agent":
        output_passthrough(payload)
        return

    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response") or {}

    raw_description = tool_input.get("description", "")
    description = raw_description[:120] if isinstance(raw_description, str) else ""

    invocation = {
        "agent_type": tool_input.get("subagent_type") or "general-purpose",
        "model": tool_input.get("model"),
        "description": description,
        "run_in_background": bool(tool_input.get("run_in_background")),
    }

    # Cascade promotion gate marker (see references/cascade-routing.md).
    # Parse from the full description so long markers are not clipped by [:120].
    cascade = _extract_cascade_marker(
        raw_description if isinstance(raw_description, str) else ""
    )
    invocation.update(cascade)

    usage = _extract_usage(tool_response)
    invocation.update({k: v for k, v in usage.items() if v is not None})

    # best-effort duration if present
    if isinstance(tool_response, dict) and tool_response.get("duration_ms") is not None:
        invocation["duration_ms"] = tool_response["duration_ms"]

    invocation["exit_status"] = "completed" if tool_response else "unknown"

    try:
        emit_agent_invocation(invocation)
    except Exception:  # noqa: BLE001  best-effort, never block
        pass

    output_passthrough(payload)


if __name__ == "__main__":
    run_hook("agent-invocation-logger", main)
