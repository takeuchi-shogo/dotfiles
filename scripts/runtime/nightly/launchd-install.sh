#!/usr/bin/env bash
# launchd-install.sh — nightly task の launchd LaunchAgent plist を生成 + load
# 理由: cron は Aqua session 外で起動 → Keychain access 不可 → claude -p が Execution error で fail
# launchd LaunchAgent (~/Library/LaunchAgents/) は user の Aqua session 内で起動 → Keychain OK
set -euo pipefail

NIGHTLY_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$AGENTS_DIR"

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

TASKS=(
    "dep-audit|22|30|run-dep-audit.sh"
    "golden-check|23|15|run-golden-check.sh"
    "friction-aggregate|23|20|run-friction-aggregate.sh"
    "health-check|23|25|run-health-check.sh"
    "daily-report|23|35|run-daily-report.sh"
    "audit|23|45|run-audit.sh"
    "skill-audit|23|45|run-skill-audit.sh"
    "plan-close-scan|0|50|run-plan-close-scan.sh"
    # tech-researcher: nightly ゲート相乗り (別ディレクトリ、.. は exec 時に解決)。
    # audit/skill-audit (23:45) の後に置き claude lock 競合を避ける。
    "tech-researcher|23|55|../tech-researcher/run-tech-researcher.sh"
)

generate_plist() {
    local task="$1" hour="$2" minute="$3" script="$4"
    local plist="$AGENTS_DIR/com.user.nightly.${task}.plist"
    cat > "$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.nightly.${task}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-lc</string>
        <string>${NIGHTLY_DIR}/${script}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>${hour}</integer>
        <key>Minute</key>
        <integer>${minute}</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Applications/cmux.app/Contents/Resources/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>${HOME}</string>
        <key>TZ</key>
        <string>Asia/Tokyo</string>
        <key>OBSIDIAN_VAULT_PATH</key>
        <string>${VAULT_PATH}</string>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/nightly-${task}.launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/nightly-${task}.launchd.log</string>
    <key>WorkingDirectory</key>
    <string>${HOME}</string>
</dict>
</plist>
PLIST
    plutil -lint "$plist" || { echo "[ERROR] $plist: plist invalid" >&2; return 1; }
    launchctl unload "$plist" 2>/dev/null || true
    launchctl load "$plist"
    echo "[install] ${task}: ${hour}:${minute} → $(basename "$plist")"
}

echo "=== Installing ${#TASKS[@]} nightly LaunchAgents ==="
for entry in "${TASKS[@]}"; do
    IFS='|' read -r task hour minute script <<< "$entry"
    generate_plist "$task" "$hour" "$minute" "$script"
done

echo
echo "=== Verification: launchctl list (nightly entries) ==="
launchctl list | grep "com.user.nightly." || echo "(no nightly entries found)"

echo
echo "次の手順: crontab -e で 'scripts/runtime/nightly/' を含む旧 cron 行を削除 (移行済みなら不要)"
echo "確認: crontab -l | grep nightly  (削除後は何も出ないはず)"
