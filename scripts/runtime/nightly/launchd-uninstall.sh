#!/usr/bin/env bash
# launchd-uninstall.sh — 7 nightly LaunchAgent を unload + 削除
set -euo pipefail
AGENTS_DIR="$HOME/Library/LaunchAgents"
TASKS=(dep-audit golden-check friction-aggregate health-check daily-report audit skill-audit)
for task in "${TASKS[@]}"; do
    plist="$AGENTS_DIR/com.user.nightly.${task}.plist"
    [[ -f "$plist" ]] || { echo "[skip] $plist not found"; continue; }
    launchctl unload "$plist" 2>/dev/null || true
    rm -f "$plist"
    echo "[uninstall] $task"
done
echo "完了。state は ~/.cache/nightly/ に残ります (削除する場合は手動)"
