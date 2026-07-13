#!/usr/bin/env bash
# herdr-collect-result.sh — herdr Worker の完了待ち + 結果回収 (collect-result.sh の herdr 版)
#
# Usage:
#   herdr-collect-result.sh --pane <pane_id> --worker <worker_id> [--timeout 1800] [--close]
#
# herdr wait はブロッキングなので cmux 版のポーリングループは不要。
# --close: 回収成功後に pane を閉じる (単発 worker の使い捨て用。launch --keep の
#          マーカーがある場合は --close 指定でも close をスキップする)
# ponytail: 画面のエラーパターン検出→自動リトライは未移植。失敗時は pane が残るので conductor が判断する
#
# Trust boundary: task 文字列と worker は conductor (親 AI) が発行する trusted 入力で、
# 敵対者ではない前提。よって DONE_SIGNAL は固定文字列で十分としている。task を
# 外部の untrusted 入力から組む運用に変える場合は per-worker random token に変えること。
#
# Output: 結果テキスト (stdout)
# Exit: 0=completed, 1=error, 2=timeout, 3=herdr not found, 4=blocked (人間の承認待ち)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../lib" 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
source "${LIB_DIR}/dispatch_logger.sh"

command -v herdr >/dev/null 2>&1 || { echo "[herdr-collect-result] herdr not found" >&2; exit 3; }

PANE=""
WORKER_ID=""
TIMEOUT=1800
CLOSE=""
DONE_SIGNAL="${DISPATCH_DONE_SIGNAL}"

# --- 引数パース ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pane)    PANE="$2"; shift 2 ;;
    --worker)  WORKER_ID="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --close)   CLOSE=1; shift ;;
    *) echo "[herdr-collect-result] Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PANE" || -z "$WORKER_ID" ]]; then
  echo "[herdr-collect-result] Usage: herdr-collect-result.sh --pane <pane_id> --worker <worker_id>" >&2
  exit 1
fi

# WORKER_ID は RESULT_FILE の path とモデル分岐の両方に使うため厳格に検証する。
# launch が生成する形式 `w-<ts>-<pid>-<rand>-<model>` に一致させ、slash/.. による
# path traversal と、未知 model が codex/gemini 分岐に落ちる誤判定を同時に防ぐ。
if [[ ! "$WORKER_ID" =~ ^w-[0-9]+(-[0-9]+)*-(claude|codex|gemini)$ ]]; then
  echo "[herdr-collect-result] invalid --worker: ${WORKER_ID}" >&2
  exit 1
fi

# timeout は算術展開 ($((TIMEOUT * 1000))) に使うため数値であることを保証する
if [[ ! "$TIMEOUT" =~ ^[0-9]+$ ]]; then
  echo "[herdr-collect-result] --timeout must be a positive integer: ${TIMEOUT}" >&2
  exit 1
fi

RESULT_FILE="${DISPATCH_RESULT_DIR}/${WORKER_ID}.md"
MODEL="${WORKER_ID##*-}"

echo "[herdr-collect-result] Waiting for ${WORKER_ID} on ${PANE} (timeout: ${TIMEOUT}s)" >&2

# --- ブロッキング待機 ---
# claude: プロンプト文面に DONE_SIGNAL 相当が画面表示されるため output match は誤検出する。
#         herdr のエージェント状態検出 (turn 完了 = done) を使う。
# codex/gemini: argv 直接 spawn でコマンドラインが画面に出ないため DONE_SIGNAL match が安全。
_timeout_exit() {
  dispatch_log_result "$WORKER_ID" "failed" "timeout after ${TIMEOUT}s"
  dispatch_log_state "$WORKER_ID" "running" "failed"
  echo "[herdr-collect-result] Timeout after ${TIMEOUT}s" >&2
  exit 2
}

if [[ "$MODEL" == "claude" ]]; then
  # 完了 = working から idle/done への遷移。フォーカス中の workspace では done を
  # 経由せず直接 idle に落ちる (live_prompt_box 判定) ため両方を完了とみなす。
  # launch 側が working 遷移を確認してから返るので、ここで idle = 完了後と判断できる。
  # blocked (承認待ち) は解除に人間が要るため timeout まで待たず即エスカレーションする
  STEP=15
  ELAPSED=0
  while :; do
    if herdr wait agent-status "$PANE" --status idle --timeout $((STEP * 1000)) >/dev/null 2>&1; then
      break
    fi
    STATUS=$(herdr agent get "$PANE" 2>/dev/null \
      | jq -r '.result.agent.agent_status // .result.agent_status // "unknown"' 2>/dev/null || echo unknown)
    case "$STATUS" in
      done|idle) break ;;
      blocked)
        dispatch_log_state "$WORKER_ID" "running" "blocked"
        echo "[herdr-collect-result] Worker is blocked (承認待ち)。pane ${PANE} で人間の対応が必要" >&2
        exit 4
        ;;
    esac
    ELAPSED=$((ELAPSED + STEP))
    [[ $ELAPSED -ge $TIMEOUT ]] && _timeout_exit
  done
else
  # --source visible 必須: デフォルトの recent はスクロールバックで、出力が
  # 1 画面に収まるとスクロールが発生せず空のまま = DONE_SIGNAL を見逃す。
  # DONE_SIGNAL は最後の出力なので visible に残り続ける
  WAIT_OUT=$(herdr wait output "$PANE" --match "$DONE_SIGNAL" --source visible --timeout $((TIMEOUT * 1000)) 2>&1) || {
    CODE=$(echo "$WAIT_OUT" | jq -r '.error.code // "unknown"' 2>/dev/null || echo unknown)
    [[ "$CODE" == "timeout" ]] && _timeout_exit
    echo "[herdr-collect-result] wait failed: ${WAIT_OUT}" >&2
    exit 1
  }
fi

# --- worker の exit status 判定 (codex/gemini のみ。launch が .status を書く) ---
if [[ "$MODEL" != "claude" ]]; then
  WSTATUS=$(cat "${RESULT_FILE}.status" 2>/dev/null || echo missing)
  if [[ "$WSTATUS" != "0" ]]; then
    dispatch_log_result "$WORKER_ID" "failed" "worker exit status: ${WSTATUS}"
    dispatch_log_state "$WORKER_ID" "running" "failed"
    echo "[herdr-collect-result] Worker failed (exit: ${WSTATUS})。エラー出力: ${RESULT_FILE}" >&2
    exit 1
  fi
fi

# --- 結果回収 ---
# codex/gemini: exec のリダイレクトで RESULT_FILE に書かれている (プライマリ)。
# claude: 応答テキストが成果物なので画面から回収する (worker からのファイル
#         書き出しは permission 制約で不可)。
# ponytail: 画面回収は直近 200 行まで。長大な結果は切れるので、長い成果物が
#           要るタスクは worker に「cwd 配下への書き出し」を明示指示する
if [[ ! -f "$RESULT_FILE" ]]; then
  # recent (スクロールバック) は短い応答だと空のことがあるため visible も重ねる
  if ! RAW=$(herdr pane read "$PANE" --source recent-unwrapped --lines 200 2>/dev/null); then
    dispatch_log_result "$WORKER_ID" "failed" "pane read failed (pane closed?)"
    dispatch_log_state "$WORKER_ID" "running" "failed"
    echo "[herdr-collect-result] pane read failed (pane ${PANE} は閉じている可能性)" >&2
    exit 1
  fi
  if [[ -z "$RAW" ]]; then
    RAW=$(herdr pane read "$PANE" --source visible --lines 80 2>/dev/null || true)
  fi
  printf '%s\n' "$RAW" | grep -vF "$DONE_SIGNAL" > "$RESULT_FILE" || true
fi

# 空結果は成功扱いしない (回収失敗の握り潰し防止)
if [[ ! -s "$RESULT_FILE" ]]; then
  dispatch_log_result "$WORKER_ID" "failed" "empty result"
  dispatch_log_state "$WORKER_ID" "running" "failed"
  echo "[herdr-collect-result] 結果が空です (${RESULT_FILE})" >&2
  exit 1
fi

dispatch_log_result "$WORKER_ID" "completed" "$RESULT_FILE"
dispatch_log_state "$WORKER_ID" "running" "completed"

if [[ -n "$CLOSE" ]]; then
  # launch --keep のマーカーがあれば close しない (観察用に pane を残す意図を enforce)
  if [[ -f "${RESULT_FILE}.keep" ]]; then
    echo "[herdr-collect-result] --keep マーカーがあるため pane ${PANE} は残します" >&2
  else
    herdr pane close "$PANE" >/dev/null 2>&1 || true
  fi
fi

cat "$RESULT_FILE"
