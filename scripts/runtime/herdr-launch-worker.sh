#!/usr/bin/env bash
# herdr-launch-worker.sh — herdr ペインに Worker を起動する (launch-worker.sh の herdr 版)
#
# Usage:
#   herdr-launch-worker.sh --model claude --task "タスク内容"
#   herdr-launch-worker.sh --model codex --task "タスク内容" [--keep]
#   herdr-launch-worker.sh --model gemini --task "タスク内容" [--keep]
#
# 完了検出は herdr-collect-result.sh (ブロッキング wait) で行う。
# 単発 worker (codex/gemini) は失敗時に pane が残り観察できる。
# 回収後の pane 掃除は herdr-collect-result.sh --close に委ねる
# (cmux 版と違い launch 側で close チェーンを組むと DONE 検出とレースするため)。
#
# Output: pane_id worker_id (space-separated)
# ponytail: --worktree は未移植。worktree 分離が要る場合は cmux 版 launch-worker.sh を使う

set -euo pipefail

# このスクリプトが作る一時ファイル (TASK_FILE / .keep) を private に。
# 注: worker 本体が書く RESULT_FILE / .status は herdr が spawn する
# プロセスの umask に従うため、これらの perms は共通 lib (dispatch_logger.sh)
# の /tmp/cmux-results 設計に依存する (cmux 版から継承、本 PR の scope 外)。
umask 077

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../lib" 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
source "${LIB_DIR}/dispatch_logger.sh"

command -v herdr >/dev/null 2>&1 || { echo "[herdr-launch-worker] herdr not found" >&2; exit 3; }
herdr status server >/dev/null 2>&1 || { echo "[herdr-launch-worker] herdr server is not running" >&2; exit 1; }

MODEL=""
TASK=""
KEEP=""
DONE_SIGNAL="${DISPATCH_DONE_SIGNAL}"

# --- 引数パース ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --task)  TASK="$2"; shift 2 ;;
    --keep)  KEEP=1; shift ;;
    *) echo "[herdr-launch-worker] Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$MODEL" || -z "$TASK" ]]; then
  echo "[herdr-launch-worker] Usage: herdr-launch-worker.sh --model <claude|codex|gemini> --task \"タスク内容\"" >&2
  exit 1
fi

# --- ワーカーID生成 ---
# 末尾の model 名は herdr-collect-result.sh の完了検出方式の分岐に使う
# nonce (pid + $RANDOM) で同一秒・並列起動時の ID 衝突と予測を防ぐ。
# model は末尾に置き、collect 側の `${WORKER_ID##*-}` 抽出と検証正規表現に合わせる。
WORKER_ID="w-$(date +%s)-$$-${RANDOM}-${MODEL}"
RESULT_FILE="${DISPATCH_RESULT_DIR}/${WORKER_ID}.md"

# タスク内容をファイルに書き出す（コマンドインジェクション防止）
TASK_FILE="${DISPATCH_RESULT_DIR}/${WORKER_ID}.task"
mkdir -p "$DISPATCH_RESULT_DIR"
printf '%s' "$TASK" > "$TASK_FILE"
chmod 600 "$TASK_FILE"

dispatch_log_state "$WORKER_ID" "pending" "launching"

# launching 以降の失敗は state ログに failed を残してから exit する
# (JSONL ログから worker 状態を再構築する側が「launching のままハング」と誤読しないため)
_fail() {
  dispatch_log_state "$WORKER_ID" "launching" "failed"
  echo "[herdr-launch-worker] $1" >&2
  exit 1
}

# --- エージェント起動 (JSON 出力から pane_id を抽出) ---
start_agent() {
  herdr agent start "$WORKER_ID" --cwd "$PWD" --no-focus -- "$@" \
    | jq -r '.result.agent.pane_id'
}

PANE=""
case "$MODEL" in
  claude)
    # 結果はファイルでなく応答末尾で回収する。worker の claude はユーザーの
    # permission 設定 (disableBypassPermissionsMode) に従うため cwd 外への
    # ファイル書き出しは blocked になる (memory: feedback_bg_agent_edit_permission)
    PROMPT="以下のタスクを実行してください。

## タスク
${TASK}

## 完了時の手順
結果を応答の最後にまとめて出力してください。ファイルへの書き出しは不要です。"
    # set -e の暗黙 exit では _fail (failed state ログ) を経由しないため if で受ける
    if ! PANE=$(start_agent claude --dangerously-skip-permissions); then
      _fail "herdr agent start に失敗した (claude)"
    fi
    # 起動完了 (= idle 検出) を待ってからプロンプト送信。検出失敗時は cmux 版と同じ固定待ち
    herdr wait agent-status "$PANE" --status idle --timeout 30000 >/dev/null 2>&1 || sleep 5
    # agent send は入力欄に入れるだけで submit しない — paste 完了を待って Enter を送る
    herdr agent send "$WORKER_ID" "$PROMPT" >/dev/null || _fail "agent send に失敗した (pane: ${PANE})"
    sleep 2
    herdr pane send-keys "$PANE" enter >/dev/null || _fail "send-keys に失敗した (pane: ${PANE})"
    # submit 確認: working 遷移を待つ。paste 処理直後の enter は飲まれることが
    # あるため、遷移しなければ一度だけ再送する。
    if ! herdr wait agent-status "$PANE" --status working --timeout 10000 >/dev/null 2>&1; then
      herdr pane send-keys "$PANE" enter >/dev/null || _fail "send-keys に失敗した (pane: ${PANE})"
      if ! herdr wait agent-status "$PANE" --status working --timeout 10000 >/dev/null 2>&1; then
        # 数秒で終わるタスクは working を見逃しうる。done = 完走済み (未閲覧) なので
        # 送信成功とみなす。idle は「未送信で入力欄のまま」と区別できないため失敗に倒す
        STATUS=$(herdr agent get "$PANE" 2>/dev/null \
          | jq -r '.result.agent.agent_status // "unknown"' 2>/dev/null || echo unknown)
        [[ "$STATUS" == "done" ]] || \
          _fail "プロンプト送信を確認できなかった (pane: ${PANE}, status: ${STATUS})"
      fi
    fi
    dispatch_log_prompt "$WORKER_ID" "$PROMPT"
    ;;
  codex|gemini)
    # argv 直接 spawn なのでコマンドラインは画面にエコーされない。
    # DONE_SIGNAL が画面に出る = 実行終了時のみ、が保証される (成否は .status で判別)。
    # 変数は positional args で渡し quoting 破壊 (DONE_SIGNAL の env override 等) を防ぐ。
    # 終了後も bash に落として pane を保持 (close は collect 側)
    # codex は positional prompt なので `--` で option 終端し、task 文字列が
    # `--sandbox=...` 等の option として解釈される injection を塞ぐ。
    # gemini は `-p <value>` で束縛済みだが対称性のため同様に扱う。
    if [[ "$MODEL" == "codex" ]]; then
      WORKER_CMD='codex exec --skip-git-repo-check --color never -- "$(cat "$1")"'
    else
      WORKER_CMD='gemini -p "$(cat "$1")"'
    fi
    if ! PANE=$(start_agent bash -c \
      "${WORKER_CMD}"' > "$2" 2>&1; echo $? > "$2.status"; echo "$3"; exec bash' \
      bash "$TASK_FILE" "$RESULT_FILE" "$DONE_SIGNAL"); then
      _fail "herdr agent start に失敗した (${MODEL})"
    fi
    dispatch_log_prompt "$WORKER_ID" "$TASK"
    ;;
  *)
    _fail "Unknown model: $MODEL"
    ;;
esac

if [[ -z "$PANE" || "$PANE" == "null" ]]; then
  _fail "failed to start agent (no pane_id)"
fi

# --keep はマーカーファイルで enforce する (collect が --close 指定でも close をスキップ)。
# running ログより先に作成し、ログ駆動で collect する observer が marker 作成前に
# close するレースを防ぐ
if [[ -n "$KEEP" ]]; then
  touch "${RESULT_FILE}.keep"
fi

# --- ログ記録 ---
dispatch_log_dispatch "$WORKER_ID" "$MODEL" "$TASK" "$PANE"
dispatch_log_state "$WORKER_ID" "launching" "running"

# --- 結果を stdout に出力 ---
echo "${PANE} ${WORKER_ID}"
