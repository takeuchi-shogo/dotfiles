#!/usr/bin/env bash
# nightly-status.sh — 夜間 task の status 管理 + catch-up gate
# Source from run-*.sh: `source "$(dirname "$0")/lib/nightly-status.sh"`
#
# Public functions:
#   status_begin "$TASK"
#   status_end "ok|fail" "$msg" ["k=v" ...]    # 内部で mark_run_today を必ず呼ぶ (Q9: fail でも mark)
#   should_run_today "$TASK" "DAILY|DOW|DOM" "$gate_value" "$catch_up_days"
#   mark_run_today "$TASK"                      # idempotent
#   acquire_claude_lock                          # Q12: グローバル claude -p lock (atomic mkdir)
#   release_claude_lock                          # release_claude_lock を必ず trap で呼ぶ
#
# Codex Gate 反映:
#   Q8: status JSONL の正本は ~/.cache/nightly/status-${DATE}.jsonl (volatile /tmp 廃止)
#   Q9: status_end は内部で mark_run_today を呼ぶ (catch-up 再試行防止)
#   Q12: claude_lock で 23:45 同時実行 (audit + skill-audit) を回避
#   M1: status_end before status_begin で _NIGHTLY_CURRENT_TASK fallback
#   FM-4: last_run の date format validation (YYYY-MM-DD regex)

set -uo pipefail

# notify-discord を同梱
# shellcheck source=./notify-discord.sh
source "$(dirname "${BASH_SOURCE[0]}")/notify-discord.sh"

NIGHTLY_DATE="${NIGHTLY_DATE_OVERRIDE:-$(date +%Y-%m-%d)}"
NIGHTLY_TZ_TS="${NIGHTLY_TZ_TS_OVERRIDE:-$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z)}"
NIGHTLY_CACHE_DIR="${NIGHTLY_CACHE_DIR_OVERRIDE:-$HOME/.cache/nightly}"
NIGHTLY_STATUS_JSONL="${NIGHTLY_CACHE_DIR}/status-${NIGHTLY_DATE}.jsonl"
NIGHTLY_CLAUDE_LOCK_DIR="${NIGHTLY_CACHE_DIR}/.lock-claude-p"
NIGHTLY_CLAUDE_LOCK_WAIT_SEC="${NIGHTLY_CLAUDE_LOCK_WAIT_SEC:-300}"  # 5 min

mkdir -p "$NIGHTLY_CACHE_DIR" 2>/dev/null || true

# Internal state
_NIGHTLY_BEGIN_TS=0
_NIGHTLY_CURRENT_TASK=""

status_begin() {
    _NIGHTLY_CURRENT_TASK="$1"
    _NIGHTLY_BEGIN_TS=$SECONDS
    echo "[nightly] begin task=$_NIGHTLY_CURRENT_TASK at $NIGHTLY_TZ_TS" >&2
}

status_end() {
    local status="$1" msg="${2:-}"
    shift 2 2>/dev/null || shift $#
    local extra_kv=("$@")

    # M1: status_end が status_begin 前に呼ばれた場合、TASK env fallback
    local task="${_NIGHTLY_CURRENT_TASK:-${TASK:-unknown}}"
    if [[ -z "$_NIGHTLY_CURRENT_TASK" ]]; then
        echo "[nightly] WARN: status_end called without status_begin, using fallback task=$task" >&2
    fi

    # cron 環境では shell 起動直後に status_begin → SECONDS=0 のため、
    # `_NIGHTLY_BEGIN_TS -gt 0` 条件にすると常に duration=0 になる bug があった
    local duration_sec=$((SECONDS - _NIGHTLY_BEGIN_TS))

    # extra_kv から report=, detail=, metric.* を抽出
    local report_path=""
    local detail_text=""
    local metric_obj="{}"
    local kv k v mk
    if [[ ${#extra_kv[@]} -gt 0 ]]; then
        for kv in "${extra_kv[@]}"; do
            k="${kv%%=*}"
            v="${kv#*=}"
            case "$k" in
                report) report_path="$v" ;;
                detail) detail_text="$v" ;;
                metric.*)
                    mk="${k#metric.}"
                    metric_obj=$(echo "$metric_obj" | jq --arg k "$mk" --arg v "$v" '. + {($k): $v}')
                    ;;
                *)
                    metric_obj=$(echo "$metric_obj" | jq --arg k "$k" --arg v "$v" '. + {($k): $v}')
                    ;;
            esac
        done
    fi

    # message も metric に含める
    [[ -n "$msg" ]] && metric_obj=$(echo "$metric_obj" | jq --arg msg "$msg" '. + {msg: $msg}')

    # JSONL: detail も含めて永続化 (morning-briefing で活用可能)
    local line
    line=$(jq -nc \
        --arg ts "$NIGHTLY_TZ_TS" \
        --arg task "$task" \
        --arg status "$status" \
        --argjson duration_sec "$duration_sec" \
        --arg report "$report_path" \
        --arg detail "$detail_text" \
        --argjson metric "$metric_obj" \
        '{ts: $ts, task: $task, status: $status, duration_sec: $duration_sec, report: $report, detail: $detail, metric: $metric}')

    echo "$line" >> "$NIGHTLY_STATUS_JSONL"

    # Discord 通知 (detail を 6th arg として渡す)
    local metric_summary
    metric_summary=$(echo "$metric_obj" | jq -r 'to_entries | map("\(.key)=\(.value)") | join(", ")' 2>/dev/null || echo "")
    notify_discord "$status" "$task" "$duration_sec" "$report_path" "$metric_summary" "$detail_text"

    # Q9 (Codex C6): fail でも mark_run_today を呼ぶ (catch-up 再試行防止)
    mark_run_today "$task"

    echo "[nightly] end task=$task status=$status duration=${duration_sec}s" >&2

    _NIGHTLY_CURRENT_TASK=""
    _NIGHTLY_BEGIN_TS=0
}

# FM-4: last_run format validation
_is_valid_date() {
    [[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]
}

should_run_today() {
    local task="$1" gate_kind="$2" gate_value="$3" catch_up_days="${4:-0}"
    local last_run_file="${NIGHTLY_CACHE_DIR}/last-run-${task}.txt"

    local last_run
    last_run=$(cat "$last_run_file" 2>/dev/null || echo "1970-01-01")
    # FM-4: 破損していたら 1970-01-01 fallback
    if ! _is_valid_date "$last_run"; then
        echo "[nightly] WARN: invalid last_run='$last_run' in $last_run_file, falling back to 1970-01-01" >&2
        last_run="1970-01-01"
    fi

    local today="$NIGHTLY_DATE"

    # 既に今日実行済 → skip
    if [[ "$last_run" == "$today" ]]; then
        echo "[nightly] skip $task: already ran today" >&2
        return 1
    fi

    # FORCE_RUN=1 → 強制 (検証用)
    if [[ "${FORCE_RUN:-0}" == "1" ]]; then
        return 0
    fi

    local today_dow today_dom
    today_dow=$(date -j -f "%Y-%m-%d" "$today" +%u 2>/dev/null || date -d "$today" +%u)
    today_dom=$(date -j -f "%Y-%m-%d" "$today" +%-d 2>/dev/null || date -d "$today" +%-d)

    case "$gate_kind" in
        DAILY)
            return 0
            ;;
        DOW)
            if [[ "$today_dow" == "$gate_value" ]]; then return 0; fi
            local days_since_gate=$(( (today_dow - gate_value + 7) % 7 ))
            if [[ $days_since_gate -gt $catch_up_days ]]; then
                echo "[nightly] skip $task: outside catch-up window (days_since_gate=$days_since_gate > $catch_up_days)" >&2
                return 1
            fi
            local last_gate_date
            last_gate_date=$(date -j -v-${days_since_gate}d -f "%Y-%m-%d" "$today" +%Y-%m-%d 2>/dev/null \
                || date -d "$today -$days_since_gate days" +%Y-%m-%d)
            if [[ "$last_run" < "$last_gate_date" ]]; then
                echo "[nightly] catch-up $task: last_run=$last_run < last_gate=$last_gate_date" >&2
                return 0
            fi
            echo "[nightly] skip $task: last_run=$last_run >= last_gate=$last_gate_date" >&2
            return 1
            ;;
        DOM)
            if [[ "$today_dom" == "$gate_value" ]]; then return 0; fi
            if [[ $today_dom -gt $((gate_value + catch_up_days)) ]]; then
                echo "[nightly] skip $task: outside DOM catch-up (today_dom=$today_dom > $((gate_value + catch_up_days)))" >&2
                return 1
            fi
            local this_month_gate="${today:0:7}-$(printf '%02d' "$gate_value")"
            if [[ "$last_run" < "$this_month_gate" ]]; then
                echo "[nightly] catch-up $task: last_run=$last_run < this_month_gate=$this_month_gate" >&2
                return 0
            fi
            echo "[nightly] skip $task: last_run=$last_run >= this_month_gate=$this_month_gate" >&2
            return 1
            ;;
        *)
            echo "[nightly] ERROR: unknown gate_kind=$gate_kind" >&2
            return 1
            ;;
    esac
}

mark_run_today() {
    local task="$1"
    [[ -z "$task" ]] && return 0  # nothing to mark
    echo "$NIGHTLY_DATE" > "${NIGHTLY_CACHE_DIR}/last-run-${task}.txt"
}

# Q12 (Codex FM-7): claude -p の同時実行を回避
# atomic mkdir で lock 取得、5 分 (NIGHTLY_CLAUDE_LOCK_WAIT_SEC) 待っても取れなければ failure
acquire_claude_lock() {
    local waited=0
    while ! mkdir "$NIGHTLY_CLAUDE_LOCK_DIR" 2>/dev/null; do
        if [[ $waited -ge $NIGHTLY_CLAUDE_LOCK_WAIT_SEC ]]; then
            echo "[nightly] ERROR: claude -p lock timeout after ${waited}s (held by another nightly task)" >&2
            return 1
        fi
        sleep 5
        waited=$((waited + 5))
    done
    echo "[nightly] acquired claude lock (waited=${waited}s)" >&2
    return 0
}

release_claude_lock() {
    rmdir "$NIGHTLY_CLAUDE_LOCK_DIR" 2>/dev/null || true
}
