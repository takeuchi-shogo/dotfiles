#!/usr/bin/env bash
# notify-discord.sh — Discord webhook 通知 (curl 片方向)
# Source from run-*.sh: `source "$(dirname "$0")/lib/notify-discord.sh"`
# Usage: notify_discord "status" "task" "duration_sec" "report_path" "metric_summary" "detail_text"
#
# Env:
#   DISCORD_WEBHOOK_URL (from ~/.config/notifications/discord.env)
#   DISCORD_ENV_PATH override (default: ~/.config/notifications/discord.env)
#
# Behavior:
#   - URL 未設定 → stderr WARN + return 0 (silent skip、呼び出し側は ok 継続)
#   - curl 失敗 → stderr WARN + return 0 (通知は副作用、task は失敗にしない)
#   - status="ok"   → 緑 embed (color 3066993)
#   - status="fail" → 赤 embed (color 15158332) + "@here" mention
#
# .env file mode validation (FM-11 mitigation): mode 600 必須、それ以外は WARN

set -uo pipefail  # -e は付けない (notify 失敗で呼び出し側を巻き込まないため)

_DISCORD_ENV_PATH="${DISCORD_ENV_PATH:-$HOME/.config/notifications/discord.env}"
if [[ -f "$_DISCORD_ENV_PATH" ]]; then
    # FM-11: file mode validation
    _env_mode=$(stat -f "%Lp" "$_DISCORD_ENV_PATH" 2>/dev/null || stat -c "%a" "$_DISCORD_ENV_PATH" 2>/dev/null || echo "unknown")
    if [[ "$_env_mode" != "600" ]] && [[ "$_env_mode" != "unknown" ]]; then
        echo "[notify-discord] WARN: $_DISCORD_ENV_PATH mode is $_env_mode, expected 600. Run: chmod 600 $_DISCORD_ENV_PATH" >&2
    fi
    # shellcheck source=/dev/null
    source "$_DISCORD_ENV_PATH"
fi

notify_discord() {
    local status="$1" task="$2" duration_sec="$3" report_path="$4" metric_summary="${5:-}" detail_text="${6:-}"

    if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
        echo "[notify-discord] WARN: DISCORD_WEBHOOK_URL not set, skipping notification for task=$task" >&2
        return 0
    fi

    local emoji color content
    if [[ "$status" == "ok" ]]; then
        emoji="✅"; color=3066993; content=""
    else
        emoji="❌"; color=15158332; content="@here"
    fi

    # bash "\n" はリテラル 2 文字のため、$'\n' で実改行を使い jq --arg 経由で Discord に改行として届ける
    local nl=$'\n'
    local title="${emoji} nightly: ${task} (${duration_sec}s)"
    local description="報告: \`${report_path}\`"
    [[ -n "$metric_summary" ]] && description="${description}${nl}メトリクス: ${metric_summary}"
    # 詳細 (任意): embed description に追加、Discord 4096 char 上限。合計 ~2000 char に収めるため本体は 1950 で cut
    if [[ -n "$detail_text" ]]; then
        local truncated="${detail_text:0:1950}"
        [[ ${#detail_text} -gt 1950 ]] && truncated="${truncated}${nl}... (truncated, full report in Vault)"
        description="${description}${nl}${nl}**詳細:**${nl}\`\`\`${nl}${truncated}${nl}\`\`\`"
    fi

    local payload
    payload=$(jq -n \
        --arg content "$content" \
        --arg title "$title" \
        --arg description "$description" \
        --argjson color "$color" \
        --arg timestamp "$(date -Iseconds 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            content: $content,
            embeds: [{
                title: $title,
                description: $description,
                color: $color,
                timestamp: $timestamp
            }]
        }')

    # FM-10: use mktemp for response file (predictable /tmp race)
    # RETURN trap を使わず explicit cleanup (set -u + 早期 return との相性問題回避)
    local response_file
    response_file=$(mktemp -t "notify-discord-response.XXXXXX")

    local http_code
    http_code=$(curl -s -o "$response_file" -w "%{http_code}" \
        -H "Content-Type: application/json" \
        -X POST -d "$payload" \
        --max-time 10 \
        "$DISCORD_WEBHOOK_URL" 2>/dev/null || echo "000")

    if [[ "$http_code" != "204" ]] && [[ "$http_code" != "200" ]]; then
        echo "[notify-discord] WARN: HTTP $http_code, response: $(head -c 200 "$response_file" 2>/dev/null || echo "")" >&2
        rm -f "$response_file"
        return 0
    fi

    rm -f "$response_file"
    return 0
}
