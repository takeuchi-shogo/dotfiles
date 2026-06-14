#!/usr/bin/env bash
# nightly-status.sh — 夜間 task の status 管理 + catch-up gate
# Source from run-*.sh: `source "$(dirname "$0")/lib/nightly-status.sh"`
#
# Public functions:
#   status_begin "$TASK"
#   status_end "ok|fail" "$msg" ["k=v" ...]
#     ok          → mark_run_today (last-run 更新 + fail-count リセット)
#     fail 1 回目  → mark しない (翌日 catch-up が 1 回だけ再試行)
#     fail 2 連続  → mark する (次ゲートまで諦め)
#     FORCE_RUN=1 → mark も fail-count も更新しない (検証実行は本番状態を汚さない)
#   should_run_today "$TASK" "DAILY|DOW|DOM" "$gate_value" "$catch_up_days"
#   mark_run_today "$TASK"                      # idempotent
#   acquire_claude_lock                          # Q12: グローバル claude -p lock (atomic mkdir)
#   release_claude_lock                          # release_claude_lock を必ず trap で呼ぶ
#
# Codex Gate 反映:
#   Q8: status JSONL の正本は ~/.cache/nightly/status-${DATE}.jsonl (volatile /tmp 廃止)
#   Q9 改訂 (2026-06-11): fail の自動再試行は 1 回まで (旧: fail でも必ず mark)
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
# 20 min: audit の claude -p timeout (1200s) を直列待ちで吸収する (300s では 6/8 のように
# 前段タスクが長引いただけで lock timeout fail になる)
NIGHTLY_CLAUDE_LOCK_WAIT_SEC="${NIGHTLY_CLAUDE_LOCK_WAIT_SEC:-1200}"
# グローバル circuit-breaker: このファイルが存在する間、全 nightly 自動ループを停止する。
# 停止: touch ~/.claude/agent-memory/LOOP_DISABLED / 解除: rm 同ファイル
NIGHTLY_LOOP_DISABLED="${NIGHTLY_LOOP_DISABLED_OVERRIDE:-$HOME/.claude/agent-memory/LOOP_DISABLED}"

mkdir -p "$NIGHTLY_CACHE_DIR" 2>/dev/null || true

# Internal state
_NIGHTLY_BEGIN_TS=0
_NIGHTLY_CURRENT_TASK=""
_NIGHTLY_HAS_LOCK=0

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

    # 偽成功検出 (全ジョブ横展開): claude -p が失敗しつつ exit 0 で返り、呼び出し側が ok と
    # 誤判定したケースを最終 md から拾う。報告が Vault 相対 .md で実在する場合のみ検査する
    # (PR URL や別パスは対象外)。2 つの signal を見る:
    #   (a) 空 or 極小レポート (<50B): claude -p がほぼ何も書かず終わった = 失敗の典型。
    #       Execution error / Overloaded / Rate limit / 途中切れ等、マーカー文字列に依存せず
    #       捕捉できる最も頑健な signal。
    #   (b) 末尾 20 行に行頭 "execution error": マーカーが残るケース。全文 grep だと大規模
    #       レポート (audit/daily-report) の本文中の言及で False Fail するため末尾に限定する。
    if [[ "$status" == "ok" && -n "$report_path" && "$report_path" == *.md && -n "${OBSIDIAN_VAULT_PATH:-}" ]]; then
        local _report_abs="${OBSIDIAN_VAULT_PATH}/${report_path}"
        if [[ -f "$_report_abs" ]]; then
            local _sz
            _sz=$(wc -c < "$_report_abs" 2>/dev/null | tr -d ' ' || echo 0)
            if [[ "$_sz" =~ ^[0-9]+$ ]] && (( _sz < 50 )); then
                echo "[nightly] $task: false success (report nearly empty ${_sz}B); flipping ok→fail" >&2
                status="fail"
                msg="${msg:+$msg; }false success: report nearly empty (${_sz}B)"
            elif tail -n 20 "$_report_abs" 2>/dev/null | grep -qiE '^[[:space:]]*execution error'; then
                echo "[nightly] $task: false success (Execution error at report tail); flipping ok→fail" >&2
                status="fail"
                msg="${msg:+$msg; }false success: Execution error at report tail"
            fi
        fi
    fi

    # Q9 改訂 (2026-06-11): fail の自動再試行は 1 回まで。
    # - fail 1 回目: mark しない → 翌日の catch-up が 1 回だけ再試行する
    # - fail 2 回連続 (当日/前日): mark する (次ゲートまで諦め)
    # - ok: mark + fail-count リセット (mark_run_today 内)
    # 旧 Q9/C6 (fail でも必ず mark) の「catch-up 再試行スパム防止」の意図は
    # 「再試行上限 1 回」として保存している。
    local _do_mark=1 _fail_count=0
    if [[ "${NIGHTLY_ORCHESTRATED:-0}" == "1" ]]; then
        # orchestrator がリトライを制御する。bash の fail-count/翌日 catch-up 機構はバイパス。
        # ok → mark (last-run 更新で同日重複防止), fail → mark しない
        # (orchestrator が即リトライ。最終 fail でも未 mark → DAILY は翌夜再実行 /
        #  DOW・DOM は catch-up window で翌夜再試行)。
        # これをしないと前夜の fail-count が今夜 1 回目 fail を即 count=2 に押し上げ mark し、
        # orchestrator の再起動が should_run_today の "already ran today" で死ぬ (Gemini CRITICAL)。
        if [[ "$status" == "ok" ]]; then _do_mark=1; else _do_mark=0; fi
    elif [[ "${FORCE_RUN:-0}" == "1" ]]; then
        # 検証実行 (FORCE_RUN) は last-run も fail-count も汚さない (本番スケジュールと独立)
        _do_mark=0
    elif [[ "$status" == "fail" ]]; then
        _fail_count=$(( $(_read_fail_count "$task") + 1 ))
        if (( _fail_count >= 2 )); then
            echo "[nightly] $task: ${_fail_count} consecutive fails; giving up until next gate" >&2
            metric_obj=$(echo "$metric_obj" | jq --argjson n "$_fail_count" '. + {consecutive_fails: $n, retry: "gave up until next gate"}')
        else
            _do_mark=0
            _write_fail_count "$task" "$_fail_count"
            echo "[nightly] $task: fail (attempt ${_fail_count}); will retry via tomorrow catch-up" >&2
            metric_obj=$(echo "$metric_obj" | jq --argjson n "$_fail_count" '. + {consecutive_fails: $n, retry: "tomorrow catch-up"}')
        fi
    fi

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

    # 並列実行 (orchestrator) で複数ジョブが同時追記する際の行混ざりを防ぐ。detail が
    # PIPE_BUF (macOS 4096B) を超えると O_APPEND のアトミック性が崩れ、混ざった行を reader が
    # malformed スキップ → fail ジョブが missing 扱いで silent loss する (Gemini HIGH)。
    # atomic mkdir lock — 書き込みは一瞬なので競合待ちは最小。launchd 直叩き (単一プロセス) でも
    # 即取得で無害。macOS の flock(1) は標準で無いため mkdir を使う (既存 acquire_claude_lock 同様)。
    local _jsonl_lock="${NIGHTLY_STATUS_JSONL}.lockd" _jw=0
    while ! mkdir "$_jsonl_lock" 2>/dev/null; do
        sleep 0.05; _jw=$((_jw + 1))
        (( _jw >= 200 )) && { echo "[nightly] WARN: JSONL lock timeout (10s), writing anyway" >&2; break; }
    done
    echo "$line" >> "$NIGHTLY_STATUS_JSONL"
    rmdir "$_jsonl_lock" 2>/dev/null || true

    # Discord 通知 (detail を 6th arg として渡す)
    local metric_summary
    metric_summary=$(echo "$metric_obj" | jq -r 'to_entries | map("\(.key)=\(.value)") | join(", ")' 2>/dev/null || echo "")
    notify_discord "$status" "$task" "$duration_sec" "$report_path" "$metric_summary" "$detail_text"

    if [[ "$_do_mark" -eq 1 ]]; then
        mark_run_today "$task"
    fi

    echo "[nightly] end task=$task status=$status duration=${duration_sec}s" >&2

    _NIGHTLY_CURRENT_TASK=""
    _NIGHTLY_BEGIN_TS=0
}

# FM-4: last_run format validation
_is_valid_date() {
    [[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]
}

# --- 連続 fail カウント (Q9 改訂 2026-06-11) ---
# ファイル形式: "YYYY-MM-DD N" の 1 行。日付は書き込み実時刻 (NIGHTLY_DATE は source 時固定の
# ため日付跨ぎでずれる)。当日/前日以外の記録は鮮度切れとして 0 扱い。破損も 0 扱い (fail safe)。
_fail_count_file() {
    echo "${NIGHTLY_CACHE_DIR}/fail-count-${1}.txt"
}

_read_fail_count() {
    local task="$1" line fdate count today yesterday
    line=$(cat "$(_fail_count_file "$task")" 2>/dev/null || echo "")
    fdate="${line%% *}"
    count="${line##* }"
    if ! [[ "$count" =~ ^[0-9]+$ ]] || ! _is_valid_date "$fdate"; then
        echo 0
        return 0
    fi
    today=$(date +%Y-%m-%d)
    yesterday=$(date -j -v-1d +%Y-%m-%d 2>/dev/null || date -d 'yesterday' +%Y-%m-%d)
    if [[ "$fdate" == "$today" || "$fdate" == "$yesterday" ]]; then
        echo "$count"
    else
        echo 0
    fi
}

_write_fail_count() {
    # tmpfile + mv のアトミック置換 (SIGKILL 等での途中書きを防ぐ)
    local task="$1" count="$2" f tmp
    f="$(_fail_count_file "$task")"
    tmp=$(mktemp "${f}.XXXXXX" 2>/dev/null) || {
        echo "[nightly] WARN: mktemp failed for fail-count" >&2
        return 1
    }
    if printf '%s %s\n' "$(date +%Y-%m-%d)" "$count" > "$tmp" && mv -f "$tmp" "$f"; then
        return 0
    else
        rm -f "$tmp" 2>/dev/null
        return 1
    fi
}

should_run_today() {
    local task="$1" gate_kind="$2" gate_value="$3" catch_up_days="${4:-0}"
    local last_run_file="${NIGHTLY_CACHE_DIR}/last-run-${task}.txt"

    # グローバル circuit-breaker (FORCE_RUN より優先。-f: file の存在を厳密にチェック)
    if [[ -f "$NIGHTLY_LOOP_DISABLED" ]]; then
        echo "[nightly] skip $task: LOOP_DISABLED present ($NIGHTLY_LOOP_DISABLED)" >&2
        return 1
    fi

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
    rm -f "$(_fail_count_file "$task")"
}

# Q12 (Codex FM-7): claude -p の同時実行を回避
# atomic mkdir で lock 取得、5 分 (NIGHTLY_CLAUDE_LOCK_WAIT_SEC) 待っても取れなければ failure
acquire_claude_lock() {
    # NIGHTLY_ORCHESTRATED=1: orchestrator が同時実行数を制御する場合、bash 内 lock を無効化する。
    # launchd 直叩き (移行前 / フォールバック) では未設定 → 従来どおり lock 有効。
    if [[ "${NIGHTLY_ORCHESTRATED:-0}" == "1" ]]; then
        _NIGHTLY_HAS_LOCK=0
        echo "[nightly] claude lock skipped (NIGHTLY_ORCHESTRATED=1, orchestrator-managed)" >&2
        return 0
    fi
    local waited=0
    while ! mkdir "$NIGHTLY_CLAUDE_LOCK_DIR" 2>/dev/null; do
        if [[ $waited -ge $NIGHTLY_CLAUDE_LOCK_WAIT_SEC ]]; then
            echo "[nightly] ERROR: claude -p lock timeout after ${waited}s (held by another nightly task)" >&2
            return 1
        fi
        sleep 5
        waited=$((waited + 5))
    done
    _NIGHTLY_HAS_LOCK=1
    echo "[nightly] acquired claude lock (waited=${waited}s)" >&2
    return 0
}

release_claude_lock() {
    if [[ "$_NIGHTLY_HAS_LOCK" -eq 1 ]]; then
        rmdir "$NIGHTLY_CLAUDE_LOCK_DIR" 2>/dev/null || true
        _NIGHTLY_HAS_LOCK=0
    fi
}

# ============================================================
# Codex runtime (2026-06-14: 夜間 LLM 呼び出しを claude -p → codex に移行)
# ------------------------------------------------------------
# 理由: launchd 直叩きの claude -p は default model / Keychain 依存で不安定
# (fable-5 classifier outage 等)。codex exec は CODEX_HOME 認証で headless 安定。
#
# 出力分離: codex の stdout は reasoning trace なので、最終メッセージは
# --output-last-message で専用ファイルに書き出す (claude -p は stdout=本文だったため
# redirect で取れた)。プロンプトは stdin 経由で渡す (positional arg だと stdin EOF 待ちで
# hang する — 2026-06-14 実地確認)。
#
# codex バイナリは NIGHTLY_CODEX_BIN の絶対パスを使う。launchd の bash -lc (login shell) は
# .bash_profile 再読込で mise を活性化せず PATH に新しい codex が乗らないため、PATH 解決だと
# stale な /usr/local/bin/codex 0.39.0 に落ちる (2026-06-14 実夜で実証)。install 時に
# command -v codex で解決した絶対パスを plist env 経由で渡す。
#
# --ignore-user-config: 無人バッチを ~/.codex/config.toml の drift から隔離する (remote MCP
# サーバ等が壊れると codex 起動ごと失敗するため)。auth は CODEX_HOME から読むので維持される。
#
# モデル/推論強度は env で上書き可:
#   NIGHTLY_CODEX_MODEL  (既定 gpt-5.5)
#   NIGHTLY_CODEX_EFFORT (既定 high — golden パイロットで検証済)
#   NIGHTLY_CODEX_BIN    (既定 codex — install 時に絶対パスへ解決)
# ============================================================
NIGHTLY_CODEX_MODEL="${NIGHTLY_CODEX_MODEL:-gpt-5.5}"
NIGHTLY_CODEX_EFFORT="${NIGHTLY_CODEX_EFFORT:-high}"
NIGHTLY_CODEX_BIN="${NIGHTLY_CODEX_BIN:-codex}"

# run_codex_report — read-only 分析 → レポート生成の共通ラッパー (claude -p 置換)。
# Usage: run_codex_report <timeout_sec> <out_file> <prompt>
#   最終メッセージを --output-last-message で <out_file> に書く。codex の trace は捨てる。
# 戻り値: 成功 0 / 失敗 非0。失敗時はグローバル CODEX_ERR_HEAD に trace 先頭 200B。
# timeout は TIMEOUT_BIN (呼び出し側 preflight で解決済) を使う。未解決なら自前で探す。
CODEX_ERR_HEAD=""
run_codex_report() {
    local timeout_sec="$1" out_file="$2" prompt="$3"
    local tbin="${TIMEOUT_BIN:-}"
    [[ -z "$tbin" ]] && tbin=$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null || true)
    if [[ -z "$tbin" ]]; then
        CODEX_ERR_HEAD="timeout/gtimeout not found"
        return 1
    fi
    local trace
    trace=$(mktemp -t "nightly-codex-trace.XXXXXX")
    if ! printf '%s' "$prompt" | "$tbin" "${timeout_sec}s" "$NIGHTLY_CODEX_BIN" exec \
            --skip-git-repo-check -m "$NIGHTLY_CODEX_MODEL" --sandbox read-only \
            --ignore-user-config --config model_reasoning_effort="$NIGHTLY_CODEX_EFFORT" \
            --output-last-message "$out_file" > "$trace" 2>&1; then
        CODEX_ERR_HEAD=$(head -c 200 "$trace" 2>/dev/null || echo "")
        rm -f "$trace"
        return 1
    fi
    rm -f "$trace"
    CODEX_ERR_HEAD=""
    return 0
}
