#!/usr/bin/env bash
# collect-result.sh — cmux Worker の完了検出 + 結果回収
#
# Usage:
#   collect-result.sh --workspace <ws_id> --worker <worker_id> [--timeout 1800] [--interval 10]
#
# Output: 結果テキスト (stdout)
# Exit: 0=completed, 1=error, 2=timeout

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../lib" 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
source "${LIB_DIR}/dispatch_logger.sh"

CMUX_CLI="/Applications/cmux.app/Contents/Resources/bin/cmux"
WORKSPACE=""
WORKER_ID=""
TIMEOUT=1800
INTERVAL=10
DONE_SIGNAL="===DISPATCH_DONE==="
MAX_RETRY=2

# --- 引数パース ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --worker)    WORKER_ID="$2"; shift 2 ;;
    --timeout)   TIMEOUT="$2"; shift 2 ;;
    --interval)  INTERVAL="$2"; shift 2 ;;
    *) echo "[collect-result] Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$WORKSPACE" || -z "$WORKER_ID" ]]; then
  echo "[collect-result] Usage: collect-result.sh --workspace <ws_id> --worker <worker_id>" >&2
  exit 1
fi

RESULT_FILE="${DISPATCH_RESULT_DIR}/${WORKER_ID}.md"
ELAPSED=0
RETRY_COUNT=0

echo "[collect-result] Monitoring ${WORKER_ID} (timeout: ${TIMEOUT}s, interval: ${INTERVAL}s)" >&2

# --- ポーリングループ ---
while [[ $ELAPSED -lt $TIMEOUT ]]; do
  # 方法1: 結果ファイルの存在チェック（プライマリ）
  if [[ -f "$RESULT_FILE" ]]; then
    echo "[collect-result] Result file found: ${RESULT_FILE}" >&2
    dispatch_log_result "$WORKER_ID" "completed" "$RESULT_FILE"
    dispatch_log_state "$WORKER_ID" "running" "completed"
    "$CMUX_CLI" set-status --workspace "$WORKSPACE" --icon "✅" --text "completed" 2>/dev/null || true
    "${SCRIPT_DIR}/cmux-notify.sh" "Worker ${WORKER_ID}" "タスク完了" "hero" 2>/dev/null || true
    cat "$RESULT_FILE"
    exit 0
  fi

  # 方法2: 画面から完了シグナル検出（フォールバック）
  SCREEN=$("$CMUX_CLI" read-screen --workspace "$WORKSPACE" --surface surface:1 --scrollback 50 2>/dev/null || echo "")
  if echo "$SCREEN" | grep -q "$DONE_SIGNAL"; then
    echo "[collect-result] Done signal detected on screen" >&2
    if [[ ! -f "$RESULT_FILE" ]]; then
      echo "$SCREEN" | sed "/${DONE_SIGNAL}/d" > "$RESULT_FILE"
    fi
    dispatch_log_result "$WORKER_ID" "completed" "$RESULT_FILE"
    dispatch_log_state "$WORKER_ID" "running" "completed"
    "$CMUX_CLI" set-status --workspace "$WORKSPACE" --icon "✅" --text "completed" 2>/dev/null || true
    "${SCRIPT_DIR}/cmux-notify.sh" "Worker ${WORKER_ID}" "タスク完了" "hero" 2>/dev/null || true
    cat "$RESULT_FILE"
    exit 0
  fi

  # エラーパターン検出
  if echo "$SCREEN" | grep -qE "(Error:|FATAL|panic:|Traceback)"; then
    echo "[collect-result] Error detected in worker output" >&2
    if [[ $RETRY_COUNT -lt $MAX_RETRY ]]; then
      RETRY_COUNT=$((RETRY_COUNT + 1))
      dispatch_log_retry "$WORKER_ID" "$RETRY_COUNT"
      dispatch_log_state "$WORKER_ID" "running" "failed"
      echo "[collect-result] Retrying (${RETRY_COUNT}/${MAX_RETRY})..." >&2
      "$CMUX_CLI" send --workspace "$WORKSPACE" --surface surface:1 \
        "前回エラーが発生しました。タスクを再試行してください。"
      "$CMUX_CLI" send-key --workspace "$WORKSPACE" --surface surface:1 return
      dispatch_log_state "$WORKER_ID" "failed" "running"
    else
      dispatch_log_escalate "$WORKER_ID" "max retries exceeded"
      dispatch_log_state "$WORKER_ID" "failed" "escalated"
      "$CMUX_CLI" set-status --workspace "$WORKSPACE" --icon "🚨" --text "escalated" 2>/dev/null || true
      "${SCRIPT_DIR}/cmux-notify.sh" "Worker ${WORKER_ID}" "リトライ上限超過。人間の介入が必要です。" "glass" 2>/dev/null || true
      echo "[collect-result] Max retries exceeded. Escalating." >&2
      exit 1
    fi
  fi

  # プログレス更新
  PROGRESS=$(echo "scale=2; $ELAPSED / $TIMEOUT" | bc)
  "$CMUX_CLI" set-progress --workspace "$WORKSPACE" --value "$PROGRESS" 2>/dev/null || true

  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done

# --- タイムアウト ---
echo "[collect-result] Timeout after ${TIMEOUT}s" >&2
dispatch_log_result "$WORKER_ID" "failed" "timeout after ${TIMEOUT}s"
dispatch_log_state "$WORKER_ID" "running" "failed"
"$CMUX_CLI" set-status --workspace "$WORKSPACE" --icon "⏰" --text "timeout" 2>/dev/null || true
"${SCRIPT_DIR}/cmux-notify.sh" "Worker ${WORKER_ID}" "タイムアウト (${TIMEOUT}s)" "glass" 2>/dev/null || true
exit 2
