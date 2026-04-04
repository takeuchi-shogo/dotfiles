#!/usr/bin/env python3
"""
Claude Code Context Monitor
Real-time context usage monitoring with visual indicators and session analytics
"""

from __future__ import annotations

import json
import os
import subprocess
import sys


def get_context_from_data(data):
    """Get context usage directly from context_window data."""
    context_window = data.get("context_window")
    if not context_window:
        return None

    try:
        percent = float(context_window.get("used_percentage", 0))
    except (TypeError, ValueError):
        percent = 0

    return {
        "percent": percent,
    }


def get_git_branch(workspace):
    """Get current git branch name."""
    current_dir = workspace.get("current_dir", "")
    if not current_dir:
        return None

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=current_dir,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return None


def get_context_display(context_info):
    """Generate context display with visual indicators."""
    if not context_info:
        return "🔵 ???"

    percent = context_info.get("percent", 0)

    # Color and icon based on usage level
    if percent >= 95:
        icon, color = "🚨", "\033[31;1m"  # Blinking red
        alert = "CRIT"
    elif percent >= 90:
        icon, color = "🔴", "\033[31m"  # Red
        alert = "HIGH"
    elif percent >= 75:
        icon, color = "🟠", "\033[91m"  # Light red
        alert = ""
    elif percent >= 50:
        icon, color = "🟡", "\033[33m"  # Yellow
        alert = ""
    else:
        icon, color = "🟢", "\033[32m"  # Green
        alert = ""

    # Create progress bar
    segments = 8
    filled = int((percent / 100) * segments)
    bar = "█" * filled + "▁" * (segments - filled)

    reset = "\033[0m"
    alert_str = f" {alert}" if alert else ""

    return f"{icon}{color}{bar}{reset} {percent:.0f}%{alert_str}"


def truncate(text, max_len=20):
    """Truncate text with ellipsis if it exceeds max_len."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def get_directory_display(workspace_data):
    """Get directory display name."""
    current_dir = workspace_data.get("current_dir", "")
    project_dir = workspace_data.get("project_dir", "")

    if current_dir and project_dir:
        if current_dir.startswith(project_dir):
            rel_path = current_dir[len(project_dir) :].lstrip("/")
            return rel_path or os.path.basename(project_dir)
        else:
            return os.path.basename(current_dir)
    elif project_dir:
        return os.path.basename(project_dir)
    elif current_dir:
        return os.path.basename(current_dir)
    else:
        return "unknown"


def get_session_metrics(cost_data):
    """Get session metrics display."""
    if not cost_data:
        return ""

    metrics = []

    # Cost
    cost_usd = cost_data.get("total_cost_usd", 0)
    if cost_usd > 0:
        if cost_usd >= 0.10:
            cost_color = "\033[31m"  # Red for expensive
        elif cost_usd >= 0.05:
            cost_color = "\033[33m"  # Yellow for moderate
        else:
            cost_color = "\033[32m"  # Green for cheap

        cost_str = f"{cost_usd * 100:.0f}¢" if cost_usd < 0.01 else f"${cost_usd:.3f}"
        metrics.append(f"{cost_color}💰 {cost_str}\033[0m")

    # Duration
    duration_ms = cost_data.get("total_duration_ms", 0)
    if duration_ms > 0:
        minutes = duration_ms / 60000
        if minutes >= 30:
            duration_color = "\033[33m"  # Yellow for long sessions
        else:
            duration_color = "\033[32m"  # Green

        if minutes < 1:
            duration_str = f"{duration_ms // 1000}s"
        else:
            duration_str = f"{minutes:.0f}m"

        metrics.append(f"{duration_color}⏱ {duration_str}\033[0m")

    # Lines changed
    lines_added = cost_data.get("total_lines_added", 0)
    lines_removed = cost_data.get("total_lines_removed", 0)
    if lines_added > 0 or lines_removed > 0:
        net_lines = lines_added - lines_removed

        if net_lines > 0:
            lines_color = "\033[32m"  # Green for additions
        elif net_lines < 0:
            lines_color = "\033[31m"  # Red for deletions
        else:
            lines_color = "\033[33m"  # Yellow for neutral

        sign = "+" if net_lines >= 0 else ""
        metrics.append(f"{lines_color}📝 {sign}{net_lines}\033[0m")

    return f" \033[90m|\033[0m {' '.join(metrics)}" if metrics else ""


def get_limit_color(pct):
    """Get ANSI color based on rate limit usage percentage."""
    if pct >= 80:
        return "\033[31m"  # Red
    elif pct >= 50:
        return "\033[33m"  # Yellow
    return "\033[36m"  # Cyan


def make_progress_bar(pct, width=10):
    """Generate a progress bar string."""
    filled = int(pct * width / 100)
    return "█" * filled + "░" * (width - filled)


def get_rate_limits_display(data):
    """Generate rate limits display from v2.1.80+ rate_limits field."""
    rate_limits = data.get("rate_limits")
    if not rate_limits:
        return ""

    import time as _time

    parts = []

    five_hour = rate_limits.get("five_hour")
    if five_hour:
        pct = float(five_hour.get("used_percentage", 0))
        color = get_limit_color(pct)
        bar = make_progress_bar(pct)
        time_left = ""
        resets_at = five_hour.get("resets_at")
        if resets_at:
            diff = int(resets_at - _time.time())
            if diff > 0:
                time_left = (
                    f" \033[90m({diff // 3600}h{(diff % 3600) // 60:02d}m)\033[0m"
                )
        parts.append(f"⏱️  5h {color}{bar}\033[0m {color}{pct:.0f}%\033[0m{time_left}")

    seven_day = rate_limits.get("seven_day")
    if seven_day:
        pct = float(seven_day.get("used_percentage", 0))
        color = get_limit_color(pct)
        bar = make_progress_bar(pct)
        parts.append(f"📅 7d {color}{bar}\033[0m {color}{pct:.0f}%\033[0m")

    return " ".join(parts)


def main():
    try:
        # Read JSON input from Claude Code
        data = json.load(sys.stdin)

        # Extract information
        model_name = data.get("model", {}).get("display_name", "Claude")
        workspace = data.get("workspace", {})
        cost_data = data.get("cost", {})

        # Get context usage directly from data
        context_info = get_context_from_data(data)

        # Write context pressure to state file for hooks (post-any reads this)
        if context_info:
            import time

            pressure_dir = os.environ.get(
                "CLAUDE_SESSION_STATE_DIR",
                os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
            )
            try:
                os.makedirs(pressure_dir, exist_ok=True)
                pressure_file = os.path.join(pressure_dir, "context-pressure.json")
                with open(pressure_file, "w") as f:
                    json.dump(
                        {"used_pct": context_info["percent"], "ts": time.time()}, f
                    )
            except OSError as e:
                # Non-critical: hook will skip stale data if write fails
                sys.stderr.write(f"[context-monitor] pressure write failed: {e}\n")

        # Get git branch
        git_branch = get_git_branch(workspace)

        # Build status components
        context_display = get_context_display(context_info)
        directory = get_directory_display(workspace)
        session_metrics = get_session_metrics(cost_data)

        # Model display with context-aware coloring
        if context_info:
            percent = context_info.get("percent", 0)
            if percent >= 90:
                model_color = "\033[31m"  # Red
            elif percent >= 75:
                model_color = "\033[33m"  # Yellow
            else:
                model_color = "\033[32m"  # Green

            model_display = f"{model_color}[{model_name}]\033[0m"
        else:
            model_display = f"\033[94m[{model_name}]\033[0m"

        # Git branch display (truncate long branch names)
        branch_display = (
            f" \033[35m🌿{truncate(git_branch, 25)}\033[0m" if git_branch else ""
        )

        # Rate limits (v2.1.80+)
        rate_limits_display = get_rate_limits_display(data)

        # Line 1: Model, branch, directory
        dir_str = f"\033[93m📁 {truncate(directory, 25)}\033[0m"
        line1 = f"{model_display}{branch_display} {dir_str}"
        # Line 2: Context usage and session metrics
        line2 = f"🧠 {context_display}{session_metrics}"

        print(line1)
        print(line2)
        # Line 3: Rate limits (only after first API response in session)
        if rate_limits_display:
            print(rate_limits_display)

    except Exception as e:
        # Fallback display on any error
        cwd = os.path.basename(os.getcwd())
        err = str(e)[:20]
        print(
            f"\033[94m[Claude]\033[0m"
            f" \033[93m📁{cwd}\033[0m"
            f" 🧠 \033[31m[Error: {err}]\033[0m"
        )


if __name__ == "__main__":
    main()
