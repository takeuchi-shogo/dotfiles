#!/bin/bash
# Daily health check - runs /check-health via headless Claude
# Triggered by: launchd (com.claude.daily-health-check.plist) or manual cron
# Inspired by: 724-office self_check cron pattern
#
# Install:
#   cp scripts/runtime/com.claude.daily-health-check.plist ~/Library/LaunchAgents/
#   launchctl load ~/Library/LaunchAgents/com.claude.daily-health-check.plist
#
# Or via claude remote triggers (preferred, requires `claude login`):
#   claude trigger create --name daily-health-check \
#     --schedule "0 21 * * *" \
#     --prompt "/check-health" \
#     --project ~/dotfiles

set -euo pipefail

LOG_DIR="${HOME}/.claude/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/daily-health-check.log"

echo "[$(date -Iseconds)] Starting daily health check" >> "$LOG_FILE"

cd "${HOME}/dotfiles"

if command -v claude &>/dev/null; then
  if claude -p "/check-health" --output-format stream-json 2>&1 \
    | tail -5 >> "$LOG_FILE"; then
    echo "[$(date -Iseconds)] Health check completed" >> "$LOG_FILE"
  else
    echo "[$(date -Iseconds)] WARN: claude health check exited non-zero" >> "$LOG_FILE"
  fi
else
  echo "[$(date -Iseconds)] ERROR: claude CLI not found" >> "$LOG_FILE"
fi

# --- patterns.jsonl rotation & dedup ---
ROTATE_SCRIPT="$(dirname "$0")/rotate-patterns.py"
if [[ -x "$ROTATE_SCRIPT" ]]; then
  if output=$(python3 "$ROTATE_SCRIPT" 2>&1); then
    echo "[$(date -Iseconds)] OK: patterns rotation -- $output" >> "$LOG_FILE"
  else
    echo "[$(date -Iseconds)] WARN: patterns rotation failed -- $output" >> "$LOG_FILE"
  fi
else
  echo "[$(date -Iseconds)] SKIP: rotate-patterns.py not found or not executable" >> "$LOG_FILE"
fi

# --- Patrol Agent heartbeat verification ---
HEARTBEAT_FILE="${HOME}/.claude/patrol-heartbeat"
HEARTBEAT_MAX_AGE_MINUTES=15

if [[ -f "$HEARTBEAT_FILE" ]]; then
  heartbeat_age=$(( ($(date +%s) - $(stat -f %m "$HEARTBEAT_FILE")) / 60 ))
  if (( heartbeat_age > HEARTBEAT_MAX_AGE_MINUTES )); then
    echo "[$(date -Iseconds)] WARN: patrol-agent heartbeat is stale (${heartbeat_age}m old, threshold: ${HEARTBEAT_MAX_AGE_MINUTES}m)" >> "$LOG_FILE"
  else
    echo "[$(date -Iseconds)] OK: patrol-agent heartbeat fresh (${heartbeat_age}m old)" >> "$LOG_FILE"
  fi
else
  echo "[$(date -Iseconds)] WARN: patrol-agent heartbeat file not found -- patrol may not be running" >> "$LOG_FILE"
fi
