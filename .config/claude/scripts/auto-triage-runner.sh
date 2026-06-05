#!/bin/bash
# Auto-Triage Dry-Run Runner
#
# learned 昇格候補を無人分類し .triage/ レポートを生成する (PR は作らない)。
# Wave3 (mechanical 限定の無人 PR 化) の要否を判断するための 2 週間 calibration 用。
# dry-run なので artifact 編集・commit・PR・ledger 書き込みは一切しない (auto-triage skill が保証)。
#
# Designed for cron (毎朝 9 時):
#   0 9 * * * ~/.claude/scripts/auto-triage-runner.sh >> ~/.claude/agent-memory/logs/auto-triage-cron.log 2>&1

set -euo pipefail

DOTFILES_DIR="$HOME/dotfiles"
DATA_DIR="$HOME/.claude/agent-memory"
LOG_FILE="$DATA_DIR/logs/auto-triage-cron.log"
TODAY=$(date +%F)
REPORT="$DOTFILES_DIR/.triage/${TODAY}-triage-report.md"

mkdir -p "$DATA_DIR/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Auto-Triage Dry-Run Starting ==="

# 冪等ガード: 今日のレポートが既にあれば二重起動しない
if [ -f "$REPORT" ]; then
    log "Today's report already exists ($REPORT). Skipping."
    exit 0
fi

# 候補数チェック: 0 件なら claude を起動しない (起動コスト節約 + ノイズ防止)
CAND=$(python3 "$HOME/.claude/scripts/learner/extract-promotion-candidates.py" 2>/dev/null \
    | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null \
    || echo 0)
if [ "$CAND" -lt 1 ]; then
    log "No pending learned candidates. Skipping."
    exit 0
fi
log "Pending candidates: $CAND"

# dry-run triage を headless で実行 (auto-triage skill が .triage/ レポートを書く)
cd "$DOTFILES_DIR"
claude --print --dangerously-skip-permissions "/auto-triage" >> "$LOG_FILE" 2>&1 || {
    log "ERROR: Claude CLI failed with exit code $?"
    exit 1
}

# fail loud: レポートが生成されたか検証 (silent fail 禁止)
if [ -f "$REPORT" ]; then
    log "Report generated: $REPORT"
else
    log "WARN: claude ran but no report at $REPORT — auto-triage skill output path may have changed"
fi

log "=== Auto-Triage Dry-Run Finished ==="
