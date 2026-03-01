#!/usr/bin/env python3
"""Context Drift Detection for Claude Code dotfiles.

Analyzes git history to detect when code changes (agents, hooks, scripts)
aren't reflected in corresponding documentation updates.
Based on "Codified Context" paper (Vasilopoulos, 2026).
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Subsystem definitions
# ---------------------------------------------------------------------------

SUBSYSTEMS: Dict[str, Dict[str, Any]] = {
    "agents": {
        "code_paths": [".config/claude/agents/"],
        "doc_paths": [
            ".config/claude/references/workflow-guide.md",
            ".config/claude/CLAUDE.md",
        ],
        "priority": "HIGH",
        "description": "Agent definitions and routing",
    },
    "hooks": {
        "code_paths": [".config/claude/settings.json"],
        "doc_paths": [".config/claude/references/workflow-guide.md"],
        "priority": "HIGH",
        "description": "Hook configuration and lifecycle",
    },
    "scripts": {
        "code_paths": [".config/claude/scripts/"],
        "doc_paths": [".config/claude/references/"],
        "priority": "HIGH",
        "description": "Automation scripts",
    },
    "rules": {
        "code_paths": [".config/claude/rules/"],
        "doc_paths": [".config/claude/references/"],
        "priority": "MEDIUM",
        "description": "Rule files for code quality",
    },
    "references": {
        "code_paths": [".config/claude/references/"],
        "doc_paths": [".config/claude/CLAUDE.md"],
        "priority": "MEDIUM",
        "description": "Reference documentation",
    },
    "skills": {
        "code_paths": [".config/claude/skills/", ".claude/skills/"],
        "doc_paths": [".config/claude/references/workflow-guide.md"],
        "priority": "LOW",
        "description": "Skill definitions",
    },
    "commands": {
        "code_paths": [".config/claude/commands/", ".claude/commands/"],
        "doc_paths": [".config/claude/references/"],
        "priority": "LOW",
        "description": "Slash command definitions",
    },
}

PRIORITY_THRESHOLDS = {
    "HIGH": 1,    # Always report
    "MEDIUM": 3,  # Report if >3 commits without doc update
    "LOW": 5,     # Report if >5 commits without doc update
}

DISMISS_FILE = os.path.expanduser("~/.claude/.context-drift-dismissed.json")
AUTO_DISMISS_COUNT = 2
ADJACENCY_WINDOW = 3  # commits within this window count as "together"

# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def get_repo_root() -> Optional[str]:
    """Return the git repository root, or None if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def get_recent_commits(repo_root: str, count: int) -> List[Dict[str, Any]]:
    """Return recent commits with their changed files.

    Each entry: {"hash", "short_hash", "subject", "date", "files"}
    """
    try:
        result = subprocess.run(
            [
                "git", "log",
                "--pretty=format:%H%n%h%n%s%n%ai",
                "--name-only",
                "-n", str(count),
            ],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=30,
        )
        if result.returncode != 0:
            return []
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    commits = []  # type: List[Dict[str, Any]]
    raw_blocks = result.stdout.strip().split("\n\n")

    for block in raw_blocks:
        lines = block.strip().split("\n")
        if len(lines) < 4:
            continue
        full_hash = lines[0]
        short_hash = lines[1]
        subject = lines[2]
        date_str = lines[3]
        files = [f for f in lines[4:] if f.strip()]

        commits.append({
            "hash": full_hash,
            "short_hash": short_hash,
            "subject": subject,
            "date": date_str,
            "files": files,
        })

    return commits


# ---------------------------------------------------------------------------
# Drift analysis
# ---------------------------------------------------------------------------


def file_matches_paths(filepath: str, paths: List[str]) -> bool:
    """Check whether *filepath* falls under any of the given path prefixes."""
    for p in paths:
        if filepath.startswith(p):
            return True
    return False


def analyze_git_drift(
    commits: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Analyze commits for documentation drift per subsystem.

    Returns a dict keyed by subsystem name with analysis results.
    """
    results = {}  # type: Dict[str, Dict[str, Any]]

    for name, info in SUBSYSTEMS.items():
        code_paths = info["code_paths"]
        doc_paths = info["doc_paths"]

        last_code_commit = None  # type: Optional[Dict[str, Any]]
        last_doc_commit = None   # type: Optional[Dict[str, Any]]
        code_changes_since_doc = 0
        last_code_idx = -1
        last_doc_idx = -1

        for idx, commit in enumerate(commits):
            has_code = any(
                file_matches_paths(f, code_paths) for f in commit["files"]
            )
            has_doc = any(
                file_matches_paths(f, doc_paths) for f in commit["files"]
            )

            if has_code and last_code_commit is None:
                last_code_commit = commit
                last_code_idx = idx

            if has_doc and last_doc_commit is None:
                last_doc_commit = commit
                last_doc_idx = idx

        # Count code changes since last doc update
        for idx, commit in enumerate(commits):
            has_code = any(
                file_matches_paths(f, code_paths) for f in commit["files"]
            )
            has_doc = any(
                file_matches_paths(f, doc_paths) for f in commit["files"]
            )

            if has_doc:
                break  # Stop counting once we hit a doc update
            if has_code:
                code_changes_since_doc += 1

        # Check adjacency: if last code and doc are within ADJACENCY_WINDOW,
        # consider them paired (no drift).
        adjacent = False
        if last_code_idx >= 0 and last_doc_idx >= 0:
            if abs(last_code_idx - last_doc_idx) <= ADJACENCY_WINDOW:
                adjacent = True

        has_drift = code_changes_since_doc > 0 and not adjacent

        results[name] = {
            "priority": info["priority"],
            "description": info["description"],
            "code_changes_since_doc": code_changes_since_doc,
            "last_code_commit": last_code_commit,
            "last_doc_commit": last_doc_commit,
            "has_drift": has_drift,
            "doc_paths": doc_paths,
        }

    return results


def should_report(subsystem_result: Dict[str, Any]) -> bool:
    """Decide whether a subsystem's drift should be reported based on priority
    thresholds."""
    if not subsystem_result["has_drift"]:
        return False
    priority = subsystem_result["priority"]
    threshold = PRIORITY_THRESHOLDS.get(priority, 1)
    return subsystem_result["code_changes_since_doc"] >= threshold


# ---------------------------------------------------------------------------
# Dismiss logic
# ---------------------------------------------------------------------------


def load_dismissed() -> Dict[str, Any]:
    """Load the dismissed warnings state from disk."""
    try:
        with open(DISMISS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_dismissed(state: Dict[str, Any]) -> None:
    """Persist the dismissed warnings state."""
    dismiss_dir = os.path.dirname(DISMISS_FILE)
    os.makedirs(dismiss_dir, exist_ok=True)
    with open(DISMISS_FILE, "w") as f:
        json.dump(state, f, indent=2)


def dismiss_key(name: str, last_code_hash: Optional[str]) -> str:
    """Create a unique key for a drift warning."""
    h = last_code_hash or "none"
    return "{}:{}".format(name, h[:8])


def apply_dismiss_logic(
    results: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    """Filter results through dismiss logic. Returns (filtered_results,
    updated_dismiss_state).

    Items auto-dismiss after being shown AUTO_DISMISS_COUNT times.
    Items clear when doc is updated (last_doc_commit changes).
    """
    state = load_dismissed()
    updated_state = {}  # type: Dict[str, Any]
    filtered = {}  # type: Dict[str, Dict[str, Any]]

    for name, info in results.items():
        if not info["has_drift"] or not should_report(info):
            filtered[name] = info
            continue

        code_hash = (
            info["last_code_commit"]["hash"]
            if info["last_code_commit"]
            else None
        )
        key = dismiss_key(name, code_hash)

        existing = state.get(key, None)
        if existing is not None:
            count = existing.get("count", 0)
            if count >= AUTO_DISMISS_COUNT:
                # Auto-dismissed; keep it quiet but preserve state
                info["dismissed"] = True
                filtered[name] = info
                updated_state[key] = existing
                continue
            # Increment count
            updated_state[key] = {
                "count": count + 1,
                "first_seen": existing.get(
                    "first_seen", datetime.now().strftime("%Y-%m-%d")
                ),
            }
        else:
            updated_state[key] = {
                "count": 1,
                "first_seen": datetime.now().strftime("%Y-%m-%d"),
            }

        filtered[name] = info

    save_dismissed(updated_state)
    return filtered, updated_state


def reset_dismissed() -> None:
    """Clear all dismissed warnings."""
    if os.path.exists(DISMISS_FILE):
        os.remove(DISMISS_FILE)


# ---------------------------------------------------------------------------
# Session analysis (optional)
# ---------------------------------------------------------------------------


def analyze_sessions() -> Optional[Dict[str, Any]]:
    """Scan recent Claude Code session files for debug-heavy patterns.

    Returns summary dict or None if no sessions found.
    """
    projects_dir = Path(os.path.expanduser("~/.claude/projects"))
    if not projects_dir.exists():
        return None

    debug_keywords = {"debug", "error", "fix", "bug", "broken", "fail"}
    total_sessions = 0
    debug_sessions = 0

    try:
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            for session_file in project_dir.glob("*.jsonl"):
                total_sessions += 1
                try:
                    content = session_file.read_text(
                        encoding="utf-8", errors="ignore"
                    )[:5000]  # Read first 5KB only
                    content_lower = content.lower()
                    if any(kw in content_lower for kw in debug_keywords):
                        debug_sessions += 1
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        return None

    if total_sessions == 0:
        return None

    ratio = debug_sessions / total_sessions
    return {
        "total_sessions": total_sessions,
        "debug_sessions": debug_sessions,
        "ratio": round(ratio, 2),
        "needs_review": ratio > 0.3,
    }


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def days_ago(date_str: str) -> str:
    """Return a human-readable 'N days ago' string from a git date."""
    try:
        # git date format: 2026-03-01 12:34:56 +0900
        dt = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - dt
        days = delta.days
        if days == 0:
            return "today"
        elif days == 1:
            return "1 day ago"
        else:
            return "{} days ago".format(days)
    except (ValueError, IndexError):
        return date_str


def format_text(
    results: Dict[str, Dict[str, Any]],
    session_info: Optional[Dict[str, Any]],
    verbose: bool,
) -> str:
    """Format results as human-readable text."""
    lines = []  # type: List[str]
    drift_found = False
    no_drift_names = []  # type: List[str]

    # Group by priority for ordered output
    for priority in ("HIGH", "MEDIUM", "LOW"):
        for name, info in sorted(results.items()):
            if info["priority"] != priority:
                continue
            if not info["has_drift"] or not should_report(info):
                no_drift_names.append(name)
                continue
            if info.get("dismissed", False):
                continue

            drift_found = True
            count = info["code_changes_since_doc"]
            last_code = info["last_code_commit"]
            last_doc = info["last_doc_commit"]

            lines.append(
                "[{}] {}: {} code change{} since last doc update".format(
                    priority,
                    name,
                    count,
                    "s" if count != 1 else "",
                )
            )

            if last_code:
                lines.append(
                    '  Last code change: {} "{}"'.format(
                        last_code["short_hash"], last_code["subject"]
                    )
                )
            if last_doc:
                lines.append(
                    '  Last doc update:  {} "{}" ({})'.format(
                        last_doc["short_hash"],
                        last_doc["subject"],
                        days_ago(last_doc["date"]),
                    )
                )
            else:
                lines.append("  Last doc update:  (none found in history)")

            # Suggest which doc to update
            doc_targets = info.get("doc_paths", [])
            if doc_targets:
                lines.append(
                    "  -> Update: {}".format(", ".join(doc_targets))
                )
            lines.append("")

    header = []  # type: List[str]
    if drift_found:
        header.append("Warning: Context Drift Detected:\n")
    else:
        header.append("No context drift detected.\n")

    if no_drift_names and (verbose or not drift_found):
        header.append(
            "No drift: {}\n".format(", ".join(sorted(no_drift_names)))
        )

    # Session analysis
    if session_info and session_info.get("needs_review", False):
        lines.append(
            "Note: {}/{} recent sessions are debug-heavy ({}%). "
            "Consider reviewing configurations.".format(
                session_info["debug_sessions"],
                session_info["total_sessions"],
                int(session_info["ratio"] * 100),
            )
        )

    return "\n".join(header + lines).strip()


def format_json(
    results: Dict[str, Dict[str, Any]],
    session_info: Optional[Dict[str, Any]],
) -> str:
    """Format results as JSON for hook consumption."""
    output = {
        "drift": {},
        "no_drift": [],
        "session_analysis": session_info,
    }  # type: Dict[str, Any]

    for name, info in results.items():
        if info["has_drift"] and should_report(info) and not info.get(
            "dismissed", False
        ):
            last_code = info["last_code_commit"]
            last_doc = info["last_doc_commit"]
            output["drift"][name] = {
                "priority": info["priority"],
                "description": info["description"],
                "code_changes_since_doc": info["code_changes_since_doc"],
                "last_code_commit": (
                    {
                        "hash": last_code["short_hash"],
                        "subject": last_code["subject"],
                        "date": last_code["date"],
                    }
                    if last_code
                    else None
                ),
                "last_doc_commit": (
                    {
                        "hash": last_doc["short_hash"],
                        "subject": last_doc["subject"],
                        "date": last_doc["date"],
                    }
                    if last_doc
                    else None
                ),
                "update_targets": info.get("doc_paths", []),
            }
        else:
            output["no_drift"].append(name)

    return json.dumps(output, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Detect context drift between code and documentation "
        "in Claude Code dotfiles.",
    )
    parser.add_argument(
        "--commits",
        type=int,
        default=20,
        help="Number of recent commits to analyze (default: 20)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all subsystems including no-drift ones",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON for hook consumption",
    )
    parser.add_argument(
        "--reset-dismissed",
        action="store_true",
        help="Clear all dismissed warnings",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()

    # Handle --reset-dismissed
    if args.reset_dismissed:
        reset_dismissed()
        print("Dismissed warnings cleared.")
        return 0

    # Find repo root
    repo_root = get_repo_root()
    if repo_root is None:
        if args.json_output:
            print(json.dumps({"error": "Not a git repository"}))
        else:
            print("Error: Not a git repository.")
        return 0  # Exit 0 for hook compatibility

    # Change to repo root for consistent path matching
    original_dir = os.getcwd()
    os.chdir(repo_root)

    try:
        # Fetch commits
        commits = get_recent_commits(repo_root, args.commits)
        if not commits:
            if args.json_output:
                print(json.dumps({"error": "No commits found"}))
            else:
                print("No commits found in history.")
            return 0

        # Analyze drift
        results = analyze_git_drift(commits)

        # Apply dismiss logic
        results, _ = apply_dismiss_logic(results)

        # Session analysis (optional)
        session_info = analyze_sessions()

        # Output
        if args.json_output:
            print(format_json(results, session_info))
        else:
            print(format_text(results, session_info, args.verbose))

    finally:
        os.chdir(original_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
