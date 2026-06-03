#!/usr/bin/env bash
# launch-worker.sh — cmux ワークスペースに Worker を起動する
#
# Usage:
#   launch-worker.sh --model claude --task "タスク内容" [--worktree branch-name]
#   launch-worker.sh --model codex --task "タスク内容"
#   launch-worker.sh --model gemini --task "タスク内容"
#
# Output: workspace_id worker_id (space-separated)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../lib" 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
source "${LIB_DIR}/dispatch_logger.sh"
source "${LIB_DIR}/cmux_resolver.sh"

CMUX_CLI="$(_resolve_cmux_cli)" || { echo "[launch-worker] cmux not found" >&2; exit 3; }
MODEL=""
TASK=""
WORKTREE=""
DONE_SIGNAL="${DISPATCH_DONE_SIGNAL}"

# --- 引数パース ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)   MODEL="$2"; shift 2 ;;
    --task)    TASK="$2"; shift 2 ;;
    --worktree) WORKTREE="$2"; shift 2 ;;
    *) echo "[launch-worker] Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$MODEL" || -z "$TASK" ]]; then
  echo "[launch-worker] Usage: launch-worker.sh --model <claude|codex|gemini> --task \"タスク内容\"" >&2
  exit 1
fi

# --- ワーカーID生成 ---
WORKER_ID="w-$(date +%s)-${MODEL}"

# --- cmux 利用可否チェック ---
if ! "$CMUX_CLI" ping &>/dev/null; then
  echo "[launch-worker] cmux is not available. Are you running inside cmux?" >&2
  exit 1
fi

# --- ワークスペース作成 ---
WS_RAW=$("$CMUX_CLI" new-workspace --name "${WORKER_ID}")
WS=$(echo "$WS_RAW" | awk '{print $NF}')
if [[ ! "$WS" =~ ^workspace:[0-9]+$ ]]; then
  echo "[launch-worker] new-workspace returned unexpected output: ${WS_RAW}" >&2
  exit 1
fi
echo "[launch-worker] Created workspace: ${WS}" >&2

# --- surface ref の解決 ---
# cmux の surface ref はグローバル (surface:1 等の固定ではない)。新ワークスペースの
# 実際の surface ref を解決する。即座に ready になるが、念のため数回リトライする。
SURFACE=""
for _ in 1 2 3 4 5; do
  # grep no-match (exit 1) で set -e/pipefail に捕まらないよう || true で空文字に倒す
  SURFACE=$("$CMUX_CLI" list-pane-surfaces --workspace "$WS" 2>/dev/null \
    | grep -oE 'surface:[0-9]+' | head -1 || true)
  [[ -n "$SURFACE" ]] && break
  sleep 0.3
done
if [[ -z "$SURFACE" ]]; then
  echo "[launch-worker] failed to resolve surface for ${WS}" >&2
  exit 1
fi

dispatch_log_state "$WORKER_ID" "pending" "launching"

# --- worktree 作成 (Claude Code の場合) ---
WORK_DIR="$(pwd)"
if [[ "$MODEL" == "claude" && -n "$WORKTREE" ]]; then
  WORK_DIR="/tmp/cmux-worktrees/${WORKER_ID}"
  git worktree add "$WORK_DIR" -b "cmux/${WORKTREE}" 2>/dev/null || \
    git worktree add "$WORK_DIR" "cmux/${WORKTREE}" || {
      echo "[launch-worker] Failed to create worktree for branch: cmux/${WORKTREE}" >&2
      exit 1
    }
  "$CMUX_CLI" send --workspace "$WS" --surface "$SURFACE" "cd '${WORK_DIR}'\n"
  sleep 1
fi

# --- モデル別起動 ---
case "$MODEL" in
  claude)
    "$CMUX_CLI" send --workspace "$WS" --surface "$SURFACE" \
      "claude --dangerously-skip-permissions\n"
    echo "[launch-worker] Waiting for Claude Code to start..." >&2
    sleep 5
    ;;
  codex)
    # Codex は単発実行なのでプロンプトごと送る
    ;;
  gemini)
    # Gemini も単発実行
    ;;
  *)
    echo "[launch-worker] Unknown model: $MODEL" >&2
    exit 1
    ;;
esac

# --- プロンプト構築 ---
RESULT_FILE="${DISPATCH_RESULT_DIR}/${WORKER_ID}.md"

# タスク内容をファイルに書き出す（コマンドインジェクション防止）
TASK_FILE="${DISPATCH_RESULT_DIR}/${WORKER_ID}.task"
printf '%s' "$TASK" > "$TASK_FILE"
chmod 600 "$TASK_FILE"

PROMPT="以下のタスクを実行してください。

## タスク
${TASK}

## 完了時の手順
1. 結果を ${RESULT_FILE} に書き出してください
2. 最後に「${DONE_SIGNAL}」と出力してください"

# --- プロンプト送信 ---
case "$MODEL" in
  claude)
    "$CMUX_CLI" send --workspace "$WS" --surface "$SURFACE" "$PROMPT"
    "$CMUX_CLI" send-key --workspace "$WS" --surface "$SURFACE" return
    ;;
  codex)
    # タスクはファイル経由で渡す（cmux send のシェル再解釈によるインジェクション防止）
    "$CMUX_CLI" send --workspace "$WS" --surface "$SURFACE" \
      "codex exec --skip-git-repo-check --color never \"\$(cat '${TASK_FILE}')\" > '${RESULT_FILE}' 2>&1 && echo '${DONE_SIGNAL}'\n"
    ;;
  gemini)
    "$CMUX_CLI" send --workspace "$WS" --surface "$SURFACE" \
      "gemini -p \"\$(cat '${TASK_FILE}')\" > '${RESULT_FILE}' 2>&1 && echo '${DONE_SIGNAL}'\n"
    ;;
esac

# --- ログ記録 ---
dispatch_log_dispatch "$WORKER_ID" "$MODEL" "$TASK" "$WS"
dispatch_log_prompt "$WORKER_ID" "$PROMPT"
dispatch_log_state "$WORKER_ID" "launching" "running"

# --- サイドバーにステータス表示 ---
"$CMUX_CLI" set-status --workspace "$WS" --icon "🤖" --text "${MODEL}: running" 2>/dev/null || true

# --- 結果を stdout に出力 ---
echo "${WS} ${WORKER_ID}"
