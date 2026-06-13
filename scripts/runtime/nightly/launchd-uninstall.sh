#!/usr/bin/env bash
# launchd-uninstall.sh — nightly LaunchAgent を unload + 削除
# glob で com.user.nightly.*.plist を全削除（旧 11 個別エントリ + orchestrator 両対応）
set -euo pipefail
AGENTS_DIR="$HOME/Library/LaunchAgents"
echo "=== Uninstalling all com.user.nightly.* LaunchAgents ==="
for plist in "$AGENTS_DIR"/com.user.nightly.*.plist; do
    [[ -f "$plist" ]] || continue
    label=$(basename "$plist" .plist)
    launchctl unload "$plist" 2>/dev/null || true
    rm -f "$plist"
    echo "  removed $label"
done
echo "完了。state は ~/.cache/nightly/ に残ります (削除する場合は手動)"
