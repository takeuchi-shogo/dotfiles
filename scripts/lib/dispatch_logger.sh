#!/usr/bin/env bash
# dispatch_logger.sh — cmux dispatch 通信ログ記録共通関数
# Usage: source scripts/lib/dispatch_logger.sh

set -euo pipefail

# セッションID（プロセス起動時に1回生成）
DISPATCH_SESSION_ID="${DISPATCH_SESSION_ID:-$(date +%Y%m%d-%H%M%S)-$$}"
DISPATCH_LOG_DIR="/tmp/cmux-dispatch-log"
DISPATCH_LOG_FILE="${DISPATCH_LOG_DIR}/${DISPATCH_SESSION_ID}.jsonl"
DISPATCH_RESULT_DIR="/tmp/cmux-results"

# ディレクトリ初期化
_dispatch_init() {
  mkdir -p "$DISPATCH_LOG_DIR" "$DISPATCH_RESULT_DIR"
}

# JSONL 1行を追記
# Usage: _dispatch_log '{"from":"master","to":"w-1",...}'
_dispatch_log() {
  _dispatch_init
  local entry="$1"
  local ts
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  # ts フィールドを先頭に挿入
  echo "$entry" | /usr/bin/python3 -c "
import sys, json
entry = json.loads(sys.stdin.read())
entry = {'ts': '${ts}', **entry}
print(json.dumps(entry, ensure_ascii=False))
" >> "$DISPATCH_LOG_FILE"
}

# dispatch イベント記録
# Usage: dispatch_log_dispatch <worker_id> <model> <task_summary> <workspace>
dispatch_log_dispatch() {
  local worker_id="$1" model="$2" task="$3" workspace="$4"
  _dispatch_log "{\"from\":\"master\",\"to\":\"${worker_id}\",\"type\":\"dispatch\",\"model\":\"${model}\",\"task\":\"${task}\",\"workspace\":\"${workspace}\"}"
}

# prompt イベント記録（長文は500文字で切り詰め）
# Usage: dispatch_log_prompt <worker_id> <body>
dispatch_log_prompt() {
  local worker_id="$1" body="$2"
  local truncated=0
  if [[ ${#body} -gt 500 ]]; then
    truncated=1
    body="${body:0:500}"
  fi
  # JSON エスケープは python に任せる
  /usr/bin/python3 -c "
import json, sys
body = sys.stdin.read()
entry = {'from': 'master', 'to': '${worker_id}', 'type': 'prompt', 'body': body}
if ${truncated}:
    entry['truncated_at'] = 500
print(json.dumps(entry, ensure_ascii=False))
" <<< "$body" | while IFS= read -r line; do
    _dispatch_log "$line"
  done
}

# result イベント記録
# Usage: dispatch_log_result <worker_id> <status> [result_file_or_error]
dispatch_log_result() {
  local worker_id="$1" status="$2" detail="${3:-}"
  local detail_field=""
  if [[ "$status" == "completed" && -n "$detail" ]]; then
    detail_field=",\"result_file\":\"${detail}\""
  elif [[ "$status" == "failed" && -n "$detail" ]]; then
    detail_field=",\"error\":\"${detail}\""
  fi
  _dispatch_log "{\"from\":\"${worker_id}\",\"to\":\"master\",\"type\":\"result\",\"status\":\"${status}\"${detail_field}}"
}

# retry イベント記録
# Usage: dispatch_log_retry <worker_id> <attempt>
dispatch_log_retry() {
  local worker_id="$1" attempt="$2"
  _dispatch_log "{\"from\":\"master\",\"to\":\"${worker_id}\",\"type\":\"retry\",\"attempt\":${attempt}}"
}

# state_change イベント記録
# Usage: dispatch_log_state <worker_id> <old_state> <new_state>
dispatch_log_state() {
  local worker_id="$1" old_state="$2" new_state="$3"
  _dispatch_log "{\"from\":\"${worker_id}\",\"to\":\"master\",\"type\":\"state_change\",\"old_state\":\"${old_state}\",\"new_state\":\"${new_state}\"}"
}

# escalate イベント記録
# Usage: dispatch_log_escalate <worker_id> <reason>
dispatch_log_escalate() {
  local worker_id="$1" reason="$2"
  _dispatch_log "{\"from\":\"${worker_id}\",\"to\":\"master\",\"type\":\"escalate\",\"reason\":\"${reason}\"}"
}

# 現在のセッションのログファイルパスを返す
dispatch_log_path() {
  echo "$DISPATCH_LOG_FILE"
}
