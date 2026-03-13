#!/usr/bin/env python3
"""MCP Server Template for Project-Specific Context.

Copy this template and customize SUBSYSTEMS and AGENTS for your project.
Based on "Codified Context" paper (Vasilopoulos, 2026).

Usage:
    uv pip install mcp[cli]
    mcp run server.py
"""

from mcp.server.fastmcp import FastMCP
import subprocess
from pathlib import Path
from typing import Optional

mcp = FastMCP("project-context")

# ============================================================
# CUSTOMIZE THESE FOR YOUR PROJECT
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent  # Adjust as needed

# Map subsystem names to their directories and key files
SUBSYSTEMS: dict[str, dict] = {
    # "auth": {
    #     "paths": ["src/auth/", "src/middleware/auth.ts"],
    #     "description": "Authentication and authorization",
    #     "key_files": ["src/auth/provider.ts", "src/auth/types.ts"],
    # },
    # "api": {
    #     "paths": ["src/api/", "src/routes/"],
    #     "description": "API endpoints and routing",
    #     "key_files": ["src/api/router.ts"],
    # },
}

# Map agent names to their roles
AGENTS: dict[str, str] = {
    # "auth-specialist": "Authentication flow expert",
    # "api-designer": "API endpoint design specialist",
}

# ============================================================
# TOOLS (7 standard tools)
# ============================================================


@mcp.tool()
def get_subsystem_overview(subsystem: str) -> str:
    """Get overview of a project subsystem including structure, key files, and recent changes."""
    if subsystem not in SUBSYSTEMS:
        available = ", ".join(SUBSYSTEMS.keys())
        return f"Unknown subsystem '{subsystem}'. Available: {available}"

    info = SUBSYSTEMS[subsystem]
    result = [f"# {subsystem}", "", info["description"], ""]

    # List files in subsystem
    for path in info["paths"]:
        full_path = PROJECT_ROOT / path
        if full_path.is_dir():
            files = sorted(full_path.rglob("*"))
            result.append(f"## Files in {path}")
            for f in files[:50]:  # Limit output
                if f.is_file() and not f.name.startswith("."):
                    result.append(f"  {f.relative_to(PROJECT_ROOT)}")
        elif full_path.is_file():
            result.append(f"## {path}")

    # Recent git changes
    result.append("\n## Recent Changes")
    for path in info["paths"]:
        try:
            log = subprocess.run(
                ["git", "log", "--oneline", "-5", "--", path],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            if log.stdout.strip():
                result.append(log.stdout.strip())
        except Exception:
            pass

    return "\n".join(result)


@mcp.tool()
def list_subsystems() -> str:
    """List all configured project subsystems with descriptions."""
    if not SUBSYSTEMS:
        return "No subsystems configured. Edit SUBSYSTEMS dict in server.py."

    lines = ["# Project Subsystems", ""]
    for name, info in SUBSYSTEMS.items():
        lines.append(f"- **{name}**: {info['description']}")
        lines.append(f"  Paths: {', '.join(info['paths'])}")
    return "\n".join(lines)


@mcp.tool()
def get_key_file(subsystem: str, filename: Optional[str] = None) -> str:
    """Read a key file from a subsystem. If filename not specified, lists available key files."""
    if subsystem not in SUBSYSTEMS:
        available = ", ".join(SUBSYSTEMS.keys())
        return f"Unknown subsystem '{subsystem}'. Available: {available}"

    info = SUBSYSTEMS[subsystem]
    key_files = info.get("key_files", [])

    if not filename:
        if not key_files:
            return f"No key files configured for '{subsystem}'."
        return "Key files:\n" + "\n".join(f"- {f}" for f in key_files)

    # Find the file
    target = PROJECT_ROOT / filename
    if not target.exists():
        return f"File not found: {filename}"

    try:
        content = target.read_text(encoding="utf-8")
        if len(content) > 10000:
            content = content[:10000] + "\n\n... (truncated, file is large)"
        return f"# {filename}\n\n```\n{content}\n```"
    except Exception as e:
        return f"Error reading {filename}: {e}"


@mcp.tool()
def search_codebase(query: str, subsystem: Optional[str] = None) -> str:
    """Search the codebase using ripgrep. Optionally scope to a subsystem."""
    args = ["rg", "--no-heading", "-n", "--max-count", "20", query]

    if subsystem and subsystem in SUBSYSTEMS:
        for path in SUBSYSTEMS[subsystem]["paths"]:
            args.append(path)

    try:
        result = subprocess.run(args, capture_output=True, text=True, cwd=PROJECT_ROOT)
        if result.stdout.strip():
            return result.stdout.strip()
        return f"No results for '{query}'"
    except FileNotFoundError:
        # Fallback to grep
        args = ["grep", "-rn", "--max-count=20", query]
        if subsystem and subsystem in SUBSYSTEMS:
            for path in SUBSYSTEMS[subsystem]["paths"]:
                args.append(path)
        try:
            result = subprocess.run(
                args, capture_output=True, text=True, cwd=PROJECT_ROOT
            )
            return result.stdout.strip() or f"No results for '{query}'"
        except Exception as e:
            return f"Search error: {e}"


@mcp.tool()
def get_recent_changes(days: int = 7, subsystem: Optional[str] = None) -> str:
    """Get recent git changes, optionally filtered by subsystem."""
    args = ["git", "log", f"--since={days} days ago", "--oneline", "--stat"]

    if subsystem and subsystem in SUBSYSTEMS:
        args.append("--")
        args.extend(SUBSYSTEMS[subsystem]["paths"])

    try:
        result = subprocess.run(args, capture_output=True, text=True, cwd=PROJECT_ROOT)
        return result.stdout.strip() or "No recent changes"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_agent_info(agent_name: Optional[str] = None) -> str:
    """Get information about available project-specific agents."""
    if not AGENTS:
        return "No project-specific agents configured. Edit AGENTS dict in server.py."

    if agent_name:
        if agent_name in AGENTS:
            return f"**{agent_name}**: {AGENTS[agent_name]}"
        return f"Unknown agent '{agent_name}'. Available: {', '.join(AGENTS.keys())}"

    lines = ["# Project Agents", ""]
    for name, desc in AGENTS.items():
        lines.append(f"- **{name}**: {desc}")
    return "\n".join(lines)


@mcp.tool()
def check_context_drift() -> str:
    """Check for documentation drift in the project."""
    drift_warnings = []

    for name, info in SUBSYSTEMS.items():
        code_mtime = 0
        doc_mtime = 0

        for path in info["paths"]:
            full = PROJECT_ROOT / path
            if full.is_dir():
                for f in full.rglob("*"):
                    if f.is_file():
                        code_mtime = max(code_mtime, f.stat().st_mtime)
            elif full.is_file():
                code_mtime = max(code_mtime, full.stat().st_mtime)

        for path in info.get("doc_paths", []):
            full = PROJECT_ROOT / path
            if full.is_file():
                doc_mtime = max(doc_mtime, full.stat().st_mtime)

        if code_mtime > doc_mtime and doc_mtime > 0:
            from datetime import datetime

            code_dt = datetime.fromtimestamp(code_mtime)
            doc_dt = datetime.fromtimestamp(doc_mtime)
            days = (code_dt - doc_dt).days
            if days > 3:
                drift_warnings.append(
                    f"WARNING {name}: code updated {code_dt:%Y-%m-%d}, "
                    f"docs last updated {doc_dt:%Y-%m-%d} ({days} days behind)"
                )

    if not drift_warnings:
        return "No context drift detected."

    return "# Context Drift Report\n\n" + "\n".join(drift_warnings)


if __name__ == "__main__":
    mcp.run()
