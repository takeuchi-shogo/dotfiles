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

# JSON を安全に構築して JSONL に追記
# Usage: _dispatch_log_entry <json_from_python>
# python で構築済みの JSON 文字列に ts を付与して書き込む
_dispatch_log_entry() {
  _dispatch_init
  local json_line="$1"
  local ts
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  /usr/bin/python3 -c "
import json, sys
entry = json.loads(sys.stdin.read())
entry = {'ts': '${ts}', **entry}
print(json.dumps(entry, ensure_ascii=False))
" <<< "$json_line" >> "$DISPATCH_LOG_FILE"
}

# dispatch イベント記録
# Usage: dispatch_log_dispatch <worker_id> <model> <task_summary> <workspace>
dispatch_log_dispatch() {
  local worker_id="$1" model="$2" task="$3" workspace="$4"
  local json
  json=$(/usr/bin/python3 -c "
import json, sys
print(json.dumps({
    'from': 'master',
    'to': sys.argv[1],
    'type': 'dispatch',
    'model': sys.argv[2],
    'task': sys.argv[3],
    'workspace': sys.argv[4]
}, ensure_ascii=False))
" "$worker_id" "$model" "$task" "$workspace")
  _dispatch_log_entry "$json"
}

# prompt イベント記録（長文は500文字で切り詰め）
# Usage: dispatch_log_prompt <worker_id> <body>
dispatch_log_prompt() {
  local worker_id="$1" body="$2"
  local json
  json=$(/usr/bin/python3 -c "
import json, sys
worker_id = sys.argv[1]
body = sys.stdin.read()
entry = {'from': 'master', 'to': worker_id, 'type': 'prompt', 'body': body}
if len(body) > 500:
    entry['body'] = body[:500]
    entry['truncated_at'] = 500
print(json.dumps(entry, ensure_ascii=False))
" "$worker_id" <<< "$body")
  _dispatch_log_entry "$json"
}

# result イベント記録
# Usage: dispatch_log_result <worker_id> <status> [result_file_or_error]
dispatch_log_result() {
  local worker_id="$1" result_status="$2" detail="${3:-}"
  local json
  json=$(/usr/bin/python3 -c "
import json, sys
entry = {'from': sys.argv[1], 'to': 'master', 'type': 'result', 'status': sys.argv[2]}
detail = sys.argv[3] if len(sys.argv) > 3 else ''
if detail:
    if sys.argv[2] == 'completed':
        entry['result_file'] = detail
    elif sys.argv[2] == 'failed':
        entry['error'] = detail
print(json.dumps(entry, ensure_ascii=False))
" "$worker_id" "$result_status" ${detail:+"$detail"})
  _dispatch_log_entry "$json"
}

# retry イベント記録
# Usage: dispatch_log_retry <worker_id> <attempt>
dispatch_log_retry() {
  local worker_id="$1" attempt="$2"
  local json
  json=$(/usr/bin/python3 -c "
import json, sys
print(json.dumps({
    'from': 'master',
    'to': sys.argv[1],
    'type': 'retry',
    'attempt': int(sys.argv[2])
}, ensure_ascii=False))
" "$worker_id" "$attempt")
  _dispatch_log_entry "$json"
}

# state_change イベント記録
# Usage: dispatch_log_state <worker_id> <old_state> <new_state>
dispatch_log_state() {
  local worker_id="$1" old_state="$2" new_state="$3"
  local json
  json=$(/usr/bin/python3 -c "
import json, sys
print(json.dumps({
    'from': sys.argv[1],
    'to': 'master',
    'type': 'state_change',
    'old_state': sys.argv[2],
    'new_state': sys.argv[3]
}, ensure_ascii=False))
" "$worker_id" "$old_state" "$new_state")
  _dispatch_log_entry "$json"
}

# escalate イベント記録
# Usage: dispatch_log_escalate <worker_id> <reason>
dispatch_log_escalate() {
  local worker_id="$1" reason="$2"
  local json
  json=$(/usr/bin/python3 -c "
import json, sys
print(json.dumps({
    'from': sys.argv[1],
    'to': 'master',
    'type': 'escalate',
    'reason': sys.argv[2]
}, ensure_ascii=False))
" "$worker_id" "$reason")
  _dispatch_log_entry "$json"
}

# 現在のセッションのログファイルパスを返す
dispatch_log_path() {
  echo "$DISPATCH_LOG_FILE"
}
