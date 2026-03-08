#!/bin/bash
# AutoEvolve Background Runner
# Runs the improvement cycle non-interactively.
# Usage: autoevolve-runner.sh [--dry-run]
#
# Designed for cron:
#   0 3 * * * ~/.claude/scripts/autoevolve-runner.sh >> ~/.claude/agent-memory/logs/autoevolve-cron.log 2>&1

set -euo pipefail

DOTFILES_DIR="$HOME/dotfiles"
DATA_DIR="$HOME/.claude/agent-memory"
LOG_FILE="$DATA_DIR/logs/autoevolve-cron.log"
DRY_RUN="${1:-}"

# Ensure log directory exists
mkdir -p "$DATA_DIR/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== AutoEvolve Background Run Starting ==="

# Check if enough data exists
SESSION_COUNT=$(wc -l < "$DATA_DIR/metrics/session-metrics.jsonl" 2>/dev/null || echo "0")
SESSION_COUNT=$(echo "$SESSION_COUNT" | tr -d ' ')

if [ "$SESSION_COUNT" -lt 3 ]; then
    log "Insufficient data: $SESSION_COUNT sessions (need >= 3). Skipping."
    exit 0
fi

log "Data available: $SESSION_COUNT sessions"

# Check if there are already pending autoevolve branches
PENDING_BRANCHES=$(cd "$DOTFILES_DIR" && git branch --list "autoevolve/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PENDING_BRANCHES" -gt 0 ]; then
    log "Pending autoevolve branches exist ($PENDING_BRANCHES). Review them first. Skipping."
    exit 0
fi

if [ "$DRY_RUN" = "--dry-run" ]; then
    log "Dry run mode. Would run autoevolve cycle. Exiting."
    exit 0
fi

# Run the improvement cycle via Claude CLI
log "Launching Claude CLI for autoevolve..."
cd "$DOTFILES_DIR"

claude --print --dangerously-skip-permissions \
    "AutoEvolve バックグラウンド実行。以下を順番に実行してください:

1. autolearn エージェントを起動して ~/.claude/agent-memory/ のデータを分析
2. knowledge-gardener エージェントを起動して知識を整理
3. autoevolve エージェントを起動して設定改善を提案・実装
   - improve-policy.md を必ず読む
   - autoevolve/$(date +%Y-%m-%d) ブランチで作業
   - 変更は最大3ファイル
   - テスト通過を確認

バックグラウンド実行のため、ユーザー確認なしで変更をブランチにコミットしてください。
master への merge は行わないでください。" \
    >> "$LOG_FILE" 2>&1 || {
    log "ERROR: Claude CLI failed with exit code $?"
    exit 1
}

log "AutoEvolve cycle completed. Check autoevolve/* branches for proposed changes."
log "Review: cd $DOTFILES_DIR && git log autoevolve/$(date +%Y-%m-%d) --oneline"
log "=== AutoEvolve Background Run Finished ==="
