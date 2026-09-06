#!/usr/bin/env bash
# race-runner.sh — 複数モデルで同一タスクを並列実装し、最初の完了を採用
#
# Usage:
#   race-runner.sh --task "タスク内容" [--models claude,codex] [--timeout 1800]
#
# Output: 勝者の結果テキスト (stdout)
# Exit: 0=completed, 1=error, 2=timeout, 3=no cmux

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../lib" 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
source "${LIB_DIR}/dispatch_logger.sh" 2>/dev/null || true
source "${LIB_DIR}/cmux_resolver.sh"

CMUX_CLI="$(_resolve_cmux_cli)" || { echo "[race-runner] cmux not found" >&2; exit 3; }
TASK=""
MODELS="claude,codex"
TIMEOUT=1800

# --- 引数パース ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)    TASK="$2"; shift 2 ;;
    --models)  MODELS="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    *) echo "[race-runner] Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$TASK" ]]; then
  echo "[race-runner] --task is required" >&2
  exit 1
fi

# cmux 環境チェック
if [[ -z "${CMUX_WORKSPACE_ID:-}" ]]; then
  echo "[race-runner] CMUX_WORKSPACE_ID not set. Falling back to single model." >&2
  FALLBACK_MODEL="${MODELS%%,*}"
  echo "[race-runner] Running with first model only: ${FALLBACK_MODEL}" >&2
  "${SCRIPT_DIR}/launch-worker.sh" --model "$FALLBACK_MODEL" --task "$TASK"
  exit $?
fi

# --- モデルリスト分割 ---
IFS=',' read -ra MODEL_ARRAY <<< "$MODELS"
if [[ ${#MODEL_ARRAY[@]} -lt 2 ]]; then
  echo "[race-runner] Need at least 2 models for race. Got: ${MODELS}" >&2
  exit 1
fi

echo "[race-runner] Starting race: ${MODELS} (timeout: ${TIMEOUT}s)" >&2

# race 開始をログ
if type dispatch_log_dispatch &>/dev/null; then
  dispatch_log_dispatch "race-$$" "multi" "race: ${TASK}" "${CMUX_WORKSPACE_ID}"
fi

# --- 各モデルを起動 ---
declare -A WORKER_IDS
declare -A WORKSPACES

for model in "${MODEL_ARRAY[@]}"; do
  echo "[race-runner] Launching ${model} worker (worktree: cmux/race-$$-${model})..." >&2
  # 同一タスクを複数モデルに走らせるので、worktree なしだと全員が同じ working tree を
  # 書き換えて互いを上書きする (AGENTS.md「並列なら worktree で filesystem を分離」)。
  LAUNCH_OUTPUT=$("${SCRIPT_DIR}/launch-worker.sh" --model "$model" --task "$TASK" \
    --worktree "race-$$-${model}" 2>&1) || {
    echo "[race-runner] Failed to launch ${model}: ${LAUNCH_OUTPUT}" >&2
    continue
  }
  # launch-worker.sh は "workspace_id worker_id" をスペース区切りで stdout に出力する
  WS=$(echo "$LAUNCH_OUTPUT" | tail -1 | awk '{print $1}')
  WID=$(echo "$LAUNCH_OUTPUT" | tail -1 | awk '{print $2}')
  if [[ -n "$WID" && -n "$WS" ]]; then
    WORKER_IDS[$model]="$WID"
    WORKSPACES[$model]="$WS"
    echo "[race-runner] ${model} → workspace=${WS} worker_id=${WID}" >&2
  else
    echo "[race-runner] Could not parse launch output for ${model}: ${LAUNCH_OUTPUT}" >&2
  fi
done

if [[ ${#WORKER_IDS[@]} -lt 1 ]]; then
  echo "[race-runner] No workers launched successfully." >&2
  exit 1
fi

# --- Race: 並列ポーリング、最初の完了者を採用 ---
RACE_DIR="/tmp/race-$$"
# 前回が SIGKILL 等で trap cleanup EXIT を発火せず終了していると、PID 再利用時に
# 古い ready/winner.txt が残ったまま起動し、最初の wait -n 直後に stale marker を
# 勝者として採用してしまう。作り直してから使う。
rm -rf "$RACE_DIR"
mkdir -p "$RACE_DIR"
WINNER_FILE="${RACE_DIR}/winner.txt"
WINNER_RESULT="${RACE_DIR}/result.txt"
# noclobber はファイル作成が atomic なだけで中身は後から書かれる。WINNER_FILE の
# 存在だけで勝者を判定すると空を読み、WINNER_MODEL が空のまま cleanup が走って
# 勝者の worktree ごと消える。全部書き終えてから触る ready marker で境界を作る。
WINNER_READY="${RACE_DIR}/ready"

cleanup() {
  local winner_model="${WINNER_MODEL:-}"
  # 残りの Worker をクリーンアップ (勝者の worktree は成果物なので残す)
  for model in "${!WORKER_IDS[@]}"; do
    if [[ "$model" == "$winner_model" ]]; then
      continue
    fi
    local ws="${WORKSPACES[$model]}"
    local wid="${WORKER_IDS[$model]}"
    # launch-worker は surface ref を動的に解決する (グローバル連番で surface:1 とは限らない)。
    # 決め打ちの close-surface は別 surface の worker を閉じ損ね、それを握り潰したまま
    # worktree を強制削除すると稼働中の作業ごと消える。worker ごとに専用 workspace を
    # 作っているので workspace ごと閉じ、閉じられたときだけ worktree を回収する。
    if "$CMUX_CLI" close-workspace --workspace "$ws" 2>/dev/null; then
      git worktree remove --force "/tmp/cmux-worktrees/${wid}" 2>/dev/null || true
      git branch -D "cmux/race-$$-${model}" 2>/dev/null || true
      echo "[race-runner] Cleaned up ${model} worker (workspace=${ws}, worktree removed)" >&2
    else
      # 敗者が自力で close 済み (codex/gemini の成功時 auto-close) の場合もここに来る。
      # 生死が判定できない以上、消さずに残す方を選ぶ。回収は手動。
      echo "[race-runner] ${model}: close-workspace failed (workspace=${ws})." \
           "worktree /tmp/cmux-worktrees/${wid} と branch cmux/race-$$-${model} は残します" >&2
    fi
  done
  # 勝者確定で break した後も残りの collector は --timeout (既定 1800s) まで polling を
  # 続け、race 終了後に dispatch log を書く。子の collect-result.sh ごと落とす。
  for pid in ${COLLECT_PIDS[@]+"${COLLECT_PIDS[@]}"}; do
    pkill -P "$pid" 2>/dev/null || true
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  rm -rf "$RACE_DIR"
}
trap cleanup EXIT

WINNER_MODEL=""

# 各 Worker の collect を並列実行
declare -a COLLECT_PIDS=()
for model in "${!WORKER_IDS[@]}"; do
  (
    WID="${WORKER_IDS[$model]}"
    WS="${WORKSPACES[$model]}"
    # collect-result.sh の stderr は捨てる（レース中のノイズを抑制）
    RESULT=$("${SCRIPT_DIR}/collect-result.sh" \
      --workspace "$WS" \
      --worker "$WID" \
      --timeout "$TIMEOUT" \
      --interval 10 2>/dev/null) && {
      # 最初に winner ファイルに書き込めた者が勝者（mkdir -p で作成済みの空ファイルを atomic に置き換え）
      if ( set -o noclobber; echo "$model $WID" > "$WINNER_FILE" ) 2>/dev/null; then
        echo "$RESULT" > "$WINNER_RESULT"
        : > "$WINNER_READY"
      fi
    }
  ) &
  COLLECT_PIDS+=($!)
done

# 「最初に終了した collector」ではなく「最初に成功した collector」まで待つ。
# 失敗 (exit 1) や timeout (exit 2) で先に抜けると WINNER_MODEL が未設定のまま
# cleanup が走り、まだ勝ちうる worker の worktree と branch まで強制削除される。
REMAINING=${#COLLECT_PIDS[@]}
while (( REMAINING > 0 )); do
  wait -n 2>/dev/null || true
  REMAINING=$((REMAINING - 1))
  if [[ -f "$WINNER_READY" ]]; then
    break
  fi
done

if [[ -f "$WINNER_READY" ]]; then
  read -r WINNER_MODEL WINNER_WID < "$WINNER_FILE"
  echo "[race-runner] Winner: ${WINNER_MODEL}" >&2
  echo "[race-runner] Winner's changes are on branch cmux/race-$$-${WINNER_MODEL} " \
       "(worktree: /tmp/cmux-worktrees/${WINNER_WID})" >&2

  # race 結果をログ
  if type dispatch_log_result &>/dev/null; then
    dispatch_log_result "race-$$" "completed" "winner=${WINNER_MODEL}"
  fi

  # race 結果を outcomes ファイルに記録
  OUTCOMES_DIR="${HOME}/.claude/agent-memory/learnings"
  mkdir -p "$OUTCOMES_DIR"
  /usr/bin/python3 -c "
import json, sys, datetime
record = {
    'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'task_type': 'implementation',
    'models': sys.argv[1].split(','),
    'winner': sys.argv[2],
    'completion_time_s': None,
    'quality_score': None
}
print(json.dumps(record, ensure_ascii=False))
" "$MODELS" "$WINNER_MODEL" >> "${OUTCOMES_DIR}/race-outcomes.jsonl"

  cat "$WINNER_RESULT"
  exit 0
else
  echo "[race-runner] No worker completed within timeout." >&2
  if type dispatch_log_result &>/dev/null; then
    dispatch_log_result "race-$$" "failed" "timeout after ${TIMEOUT}s"
  fi
  exit 2
fi
