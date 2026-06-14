#!/usr/bin/env bash
# launchd-install.sh — nightly task の launchd LaunchAgent plist を生成 + load
# 理由: cron は Aqua session 外 + PATH/env が最小で起動するため LLM CLI が不安定。
# launchd LaunchAgent (~/Library/LaunchAgents/) は user の Aqua session 内で起動し、
# EnvironmentVariables で PATH/HOME/TZ/モデル設定を明示注入できる。
# (2026-06-14: 夜間 LLM 呼び出しは claude -p → codex に移行済。codex は CODEX_HOME 認証)
set -euo pipefail

NIGHTLY_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$AGENTS_DIR"

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# 夜間バッチの LLM 呼び出しは 2026-06-14 に claude -p → codex へ移行。codex は CODEX_HOME 認証で
# headless 安定 (claude -p の default model / Keychain 依存の不安定を回避)。モデルと推論強度を
# 明示固定する (env で上書き可。run-*.sh / lib も同じ既定にフォールバックする)。
# CODEX_HOME を明示注入し headless で認証経路を確定させる (未注入だと OPENAI_API_KEY 等への
# 暗黙フォールバックで挙動がぶれる)。
NIGHTLY_CODEX_MODEL="${NIGHTLY_CODEX_MODEL:-gpt-5.5}"
NIGHTLY_CODEX_EFFORT="${NIGHTLY_CODEX_EFFORT:-high}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

# codex バイナリの絶対パスを install 時 (= operator の対話シェル) に解決して plist env に焼く。
# launchd の bash -lc (login shell) は .bash_profile 再読込で mise を活性化せず、PATH 解決だと
# stale な /usr/local/bin/codex 0.39.0 (--output-last-message 短縮形 / remote MCP 非対応) に
# 落ちて全ジョブ失敗する (2026-06-14 実夜で実証)。絶対パスで PATH 非依存にする。
NIGHTLY_CODEX_BIN="${NIGHTLY_CODEX_BIN:-$(command -v codex || true)}"
if [[ -z "$NIGHTLY_CODEX_BIN" || ! -x "$NIGHTLY_CODEX_BIN" ]]; then
    echo "[ERROR] codex CLI が見つからない (command -v codex)。先に codex を install/activate せよ" >&2
    exit 1
fi
# 解決した codex が --output-last-message を持つか検証 (古い 0.39.0 等を弾く)。
if ! "$NIGHTLY_CODEX_BIN" exec --help 2>/dev/null | grep -q -- '--output-last-message'; then
    echo "[ERROR] $NIGHTLY_CODEX_BIN は --output-last-message 非対応 (古すぎ)。codex を更新せよ" >&2
    "$NIGHTLY_CODEX_BIN" --version >&2 || true
    exit 1
fi
echo "[install] codex bin: $NIGHTLY_CODEX_BIN ($("$NIGHTLY_CODEX_BIN" --version 2>/dev/null))"

# wake/caffeinate 時刻の単一真実源 (setup-nightly-wake.sh の pmset と揃える)
# shellcheck source=./nightly-wake.env
source "${NIGHTLY_DIR}/nightly-wake.env"

[[ "${NIGHTLY_WAKE_HOUR:-}" =~ ^[0-9]+$ && "${NIGHTLY_WAKE_MINUTE:-}" =~ ^[0-9]+$ ]] \
    || { echo "[ERROR] nightly-wake.env: NIGHTLY_WAKE_HOUR/MINUTE must be integers" >&2; exit 1; }

# orchestrator バイナリをビルド（launchd は絶対パスでバイナリを叩く）
ORCH_DIR="${TASKFILE_DIR:-$(git -C "$NIGHTLY_DIR" rev-parse --show-toplevel)}/tools/nightly-orchestrator"
echo "=== Building nightly-orchestrator ==="
( cd "$ORCH_DIR" && go build -o nightly-orchestrator . ) || { echo "ERROR: orchestrator build failed" >&2; exit 1; }
ORCH_BIN="${ORCH_DIR}/nightly-orchestrator"

# 移行後: 個別 11 ジョブは orchestrator が内部で並列実行する。
# launchd エントリは caffeinate（スリープ抑止）と orchestrator の 2 本のみ。
TASKS=(
    # caffeinate アンブレラ: wake 時刻に発火し、バッチ完了までスリープを抑止する
    "caffeinate|${NIGHTLY_WAKE_HOUR}|${NIGHTLY_WAKE_MINUTE}|nightly-caffeinate.sh"
)
# orchestrator は別関数で専用 plist を生成（ProgramArguments が go バイナリで bash と異なるため）

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
        <key>CODEX_HOME</key>
        <string>${CODEX_HOME}</string>
        <key>OBSIDIAN_VAULT_PATH</key>
        <string>${VAULT_PATH}</string>
        <key>NIGHTLY_CODEX_MODEL</key>
        <string>${NIGHTLY_CODEX_MODEL}</string>
        <key>NIGHTLY_CODEX_EFFORT</key>
        <string>${NIGHTLY_CODEX_EFFORT}</string>
        <key>NIGHTLY_CODEX_BIN</key>
        <string>${NIGHTLY_CODEX_BIN}</string>
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

generate_orchestrator_plist() {
    local plist="$AGENTS_DIR/com.user.nightly.orchestrator.plist"
    # caffeinate (NIGHTLY_WAKE_HOUR:NIGHTLY_WAKE_MINUTE) の 2 分後に起動し、スリープ抑止下で全ジョブを回す
    cat > "$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.nightly.orchestrator</string>
    <key>ProgramArguments</key>
    <array>
        <string>${ORCH_BIN}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>${NIGHTLY_WAKE_HOUR}</integer>
        <key>Minute</key><integer>$((NIGHTLY_WAKE_MINUTE + 2))</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/nightly-orchestrator.launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/nightly-orchestrator.launchd.log</string>
    <key>WorkingDirectory</key>
    <string>${HOME}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key><string>/Applications/cmux.app/Contents/Resources/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key><string>${HOME}</string>
        <key>TZ</key><string>Asia/Tokyo</string>
        <key>CODEX_HOME</key><string>${CODEX_HOME}</string>
        <key>OBSIDIAN_VAULT_PATH</key><string>${VAULT_PATH}</string>
        <key>NIGHTLY_CODEX_MODEL</key><string>${NIGHTLY_CODEX_MODEL}</string>
        <key>NIGHTLY_CODEX_EFFORT</key><string>${NIGHTLY_CODEX_EFFORT}</string>
        <key>NIGHTLY_CODEX_BIN</key><string>${NIGHTLY_CODEX_BIN}</string>
    </dict>
</dict>
</plist>
PLIST
    plutil -lint "$plist" >/dev/null || { echo "ERROR: invalid orchestrator plist" >&2; return 1; }
    echo "$plist"
}

echo "=== Installing ${#TASKS[@]} nightly LaunchAgents ==="
for entry in "${TASKS[@]}"; do
    IFS='|' read -r task hour minute script <<< "$entry"
    generate_plist "$task" "$hour" "$minute" "$script"
done

echo "=== Installing orchestrator LaunchAgent ==="
orch_plist=$(generate_orchestrator_plist) || exit 1
launchctl unload "$orch_plist" 2>/dev/null || true
launchctl load "$orch_plist"
echo "  loaded com.user.nightly.orchestrator (starts $((NIGHTLY_WAKE_MINUTE + 2)) past ${NIGHTLY_WAKE_HOUR}:00)"

echo
echo "=== Verification: launchctl list (nightly entries) ==="
launchctl list | grep "com.user.nightly." || echo "(no nightly entries found)"

echo
echo "次の手順: crontab -e で 'scripts/runtime/nightly/' を含む旧 cron 行を削除 (移行済みなら不要)"
echo "確認: crontab -l | grep nightly  (削除後は何も出ないはず)"
