#!/bin/bash
# AutoEvolve Background Runner v2
# Runs 4-category parallel improvement cycles.
# Usage: autoevolve-runner.sh [--dry-run]
#
# Designed for cron:
#   0 3 * * * ~/.claude/scripts/autoevolve-runner.sh >> ~/.claude/agent-memory/logs/autoevolve-cron.log 2>&1

set -euo pipefail

DOTFILES_DIR="$HOME/dotfiles"
DATA_DIR="$HOME/.claude/agent-memory"
LOG_FILE="$DATA_DIR/logs/autoevolve-cron.log"
DRY_RUN="${1:-}"

mkdir -p "$DATA_DIR/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== AutoEvolve v2 Background Run Starting ==="

# Check if enough data exists (threshold: 1 session)
SESSION_COUNT=$(wc -l < "$DATA_DIR/metrics/session-metrics.jsonl" 2>/dev/null || echo "0")
SESSION_COUNT=$(echo "$SESSION_COUNT" | tr -d ' ')

if [ "$SESSION_COUNT" -lt 1 ]; then
    log "Insufficient data: $SESSION_COUNT sessions (need >= 1). Skipping."
    exit 0
fi

log "Data available: $SESSION_COUNT sessions"

# Check pending autoevolve branches
PENDING_BRANCHES=$(cd "$DOTFILES_DIR" && git branch --list "autoevolve/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PENDING_BRANCHES" -gt 0 ]; then
    log "Pending autoevolve branches exist ($PENDING_BRANCHES). Review them first. Skipping."
    exit 0
fi

# Scan categories for available data
CATEGORIES=""
for cat in errors quality patterns; do
    FILE="$DATA_DIR/learnings/${cat}.jsonl"
    if [ -f "$FILE" ] && [ -s "$FILE" ]; then
        COUNT=$(wc -l < "$FILE" | tr -d ' ')
        log "Category $cat: $COUNT entries"
        CATEGORIES="$CATEGORIES $cat"
    fi
done

if [ -z "$CATEGORIES" ]; then
    log "No learnings data found in any category. Skipping."
    exit 0
fi

log "Active categories:$CATEGORIES"

if [ "$DRY_RUN" = "--dry-run" ]; then
    log "Dry run mode. Would run autoevolve for:$CATEGORIES. Exiting."
    exit 0
fi

# Run the improvement cycle via Claude CLI
log "Launching Claude CLI for autoevolve v2..."
cd "$DOTFILES_DIR"

claude --print --dangerously-skip-permissions \
    "/improve" \
    >> "$LOG_FILE" 2>&1 || {
    log "ERROR: Claude CLI failed with exit code $?"
    exit 1
}

log "AutoEvolve v2 cycle completed. Check autoevolve/* branches for proposed changes."
log "=== AutoEvolve v2 Background Run Finished ==="
