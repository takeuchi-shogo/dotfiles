# cmux マルチエージェントオーケストレーション Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** cmux-team ベースでコーディネーター（Master Claude Code）が複数 Worker（Claude Code / Codex / Gemini）を cmux ペインで起動・指揮・ログ記録する仕組みを構築する

**Architecture:** Master セッションが `/dispatch` スキルでタスクの振り分け先を判定し、`launch-worker.sh` で cmux ワークスペースに Worker を起動、`collect-result.sh` で結果を回収する。全通信は `dispatch_logger.sh` で JSONL ログに記録される。

**Tech Stack:** Bash (cmux CLI), JSONL (通信ログ), Claude Code Skill (Markdown)

**Spec:** `docs/superpowers/specs/2026-03-30-cmux-multi-agent-orchestration-design.md`

---

### Task 0: cmux-team / using-cmux プラグインのインストール

**Files:**
- なし（プラグインインストールのみ）

- [ ] **Step 1: using-cmux をインストール**

```bash
claude /plugin install hummer98/using-cmux
```

Expected: Plugin installed successfully

- [ ] **Step 2: cmux-team をインストール**

```bash
claude /plugin install hummer98/cmux-team
```

Expected: Plugin installed successfully

- [ ] **Step 3: cmux CLI の動作確認**

```bash
/Applications/cmux.app/Contents/Resources/bin/cmux ping
```

Expected: `pong` (cmux 内で実行している場合)

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "🔧 chore(cmux): install using-cmux and cmux-team plugins"
```

---

### Task 1: 通信ログ共通関数 (`dispatch_logger.sh`)

全スクリプトが共有するログ記録関数。他のスクリプトの依存元なので最初に作る。

**Files:**
- Create: `scripts/lib/dispatch_logger.sh`

- [ ] **Step 1: dispatch_logger.sh を作成**

```bash
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
entry = {'ts': '$ts', **entry}
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
  local truncated_at=""
  if [[ ${#body} -gt 500 ]]; then
    truncated_at=",\"truncated_at\":500"
    body="${body:0:500}"
  fi
  # JSON エスケープは python に任せる
  /usr/bin/python3 -c "
import json, sys
body = sys.stdin.read()
entry = {'from': 'master', 'to': '${worker_id}', 'type': 'prompt', 'body': body}
$([ -n "$truncated_at" ] && echo "entry['truncated_at'] = 500")
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
```

- [ ] **Step 2: ソース読み込みテスト**

```bash
source scripts/lib/dispatch_logger.sh && echo "OK: sourced"
```

Expected: `OK: sourced`

- [ ] **Step 3: ログ記録の動作確認**

```bash
source scripts/lib/dispatch_logger.sh
dispatch_log_dispatch "w-1" "claude" "テストタスク" "workspace:w-1"
dispatch_log_prompt "w-1" "これはテストプロンプトです"
dispatch_log_result "w-1" "completed" "/tmp/cmux-results/w-1.md"
cat "$(dispatch_log_path)"
```

Expected: 3行の JSONL が出力される。各行に `ts`, `from`, `to`, `type` がある。

- [ ] **Step 4: Commit**

```bash
git add scripts/lib/dispatch_logger.sh
git commit -m "$(cat <<'EOF'
✨ feat(dispatch): add dispatch_logger.sh for agent communication logging

JSONL-based logging for all cmux worker communication events.
Records dispatch, prompt, result, retry, state_change, escalate events.
EOF
)"
```

---

### Task 2: Worker 起動スクリプト (`launch-worker.sh`)

cmux ワークスペースの作成 → モデル別 CLI 起動 → プロンプト送信を一括で行う。

**Files:**
- Create: `scripts/runtime/launch-worker.sh`

- [ ] **Step 1: launch-worker.sh を作成**

```bash
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

CMUX_CLI="/Applications/cmux.app/Contents/Resources/bin/cmux"
MODEL=""
TASK=""
WORKTREE=""
DONE_SIGNAL="===DISPATCH_DONE==="

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
WS=$("$CMUX_CLI" new-workspace "${WORKER_ID}")
echo "[launch-worker] Created workspace: ${WS}" >&2

dispatch_log_state "$WORKER_ID" "pending" "launching"

# --- worktree 作成 (Claude Code の場合) ---
WORK_DIR="$(pwd)"
if [[ "$MODEL" == "claude" && -n "$WORKTREE" ]]; then
  WORK_DIR="/tmp/cmux-worktrees/${WORKER_ID}"
  git worktree add "$WORK_DIR" -b "cmux/${WORKTREE}" 2>/dev/null || \
    git worktree add "$WORK_DIR" "cmux/${WORKTREE}" 2>/dev/null || \
    git worktree add "$WORK_DIR" HEAD
  "$CMUX_CLI" send --workspace "$WS" --surface surface:1 "cd ${WORK_DIR}\n"
  sleep 1
fi

# --- モデル別起動 ---
case "$MODEL" in
  claude)
    "$CMUX_CLI" send --workspace "$WS" --surface surface:1 \
      "claude --dangerously-skip-permissions\n"
    # Trust 確認待ち（Claude Code のプロンプト出現を待つ）
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

PROMPT="以下のタスクを実行してください。

## タスク
${TASK}

## 完了時の手順
1. 結果を ${RESULT_FILE} に書き出してください
2. 最後に「${DONE_SIGNAL}」と出力してください"

# --- プロンプト送信 ---
case "$MODEL" in
  claude)
    "$CMUX_CLI" send --workspace "$WS" --surface surface:1 "$PROMPT"
    "$CMUX_CLI" send-key --workspace "$WS" --surface surface:1 return
    ;;
  codex)
    "$CMUX_CLI" send --workspace "$WS" --surface surface:1 \
      "codex exec --skip-git-repo-check -q \"${TASK}\" > ${RESULT_FILE} 2>&1 && echo '${DONE_SIGNAL}'\n"
    ;;
  gemini)
    "$CMUX_CLI" send --workspace "$WS" --surface surface:1 \
      "gemini -p \"${TASK}\" > ${RESULT_FILE} 2>&1 && echo '${DONE_SIGNAL}'\n"
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
```

- [ ] **Step 2: 引数バリデーションの確認**

```bash
bash scripts/runtime/launch-worker.sh 2>&1 | head -1
```

Expected: `[launch-worker] Usage: launch-worker.sh --model <claude|codex|gemini> --task "タスク内容"`

- [ ] **Step 3: --help フラグなしでエラー終了を確認**

```bash
bash scripts/runtime/launch-worker.sh --model claude 2>&1; echo "exit: $?"
```

Expected: Usage メッセージ + `exit: 1`

- [ ] **Step 4: 実行権限を付与**

```bash
chmod +x scripts/runtime/launch-worker.sh
```

- [ ] **Step 5: Commit**

```bash
git add scripts/runtime/launch-worker.sh
git commit -m "$(cat <<'EOF'
✨ feat(dispatch): add launch-worker.sh for cmux worker startup

Abstracts model-specific pane creation: Claude Code (with worktree),
Codex (exec), Gemini (CLI). Logs all dispatch/prompt events.
EOF
)"
```

---

### Task 3: 結果回収ユーティリティ (`collect-result.sh`)

Worker の完了をポーリング監視し、結果を回収する。

**Files:**
- Create: `scripts/runtime/collect-result.sh`

- [ ] **Step 1: collect-result.sh を作成**

```bash
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
    # 通知
    "${SCRIPT_DIR}/cmux-notify.sh" "Worker ${WORKER_ID}" "タスク完了" "hero" 2>/dev/null || true
    cat "$RESULT_FILE"
    exit 0
  fi

  # 方法2: 画面から完了シグナル検出（フォールバック）
  SCREEN=$("$CMUX_CLI" read-screen --workspace "$WORKSPACE" --surface surface:1 --scrollback 50 2>/dev/null || echo "")
  if echo "$SCREEN" | grep -q "$DONE_SIGNAL"; then
    echo "[collect-result] Done signal detected on screen" >&2
    # 結果ファイルがまだ書かれていない場合、画面内容をフォールバックとして使う
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
      # リトライ: 画面にリトライ指示を送信
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
```

- [ ] **Step 2: 引数バリデーションの確認**

```bash
bash scripts/runtime/collect-result.sh 2>&1 | head -1
```

Expected: `[collect-result] Usage: collect-result.sh --workspace <ws_id> --worker <worker_id>`

- [ ] **Step 3: 実行権限を付与**

```bash
chmod +x scripts/runtime/collect-result.sh
```

- [ ] **Step 4: Commit**

```bash
git add scripts/runtime/collect-result.sh
git commit -m "$(cat <<'EOF'
✨ feat(dispatch): add collect-result.sh for worker result collection

Polls cmux workspace for completion (file-based primary, screen-based
fallback). Auto-retry on errors (max 2), escalate on failure.
EOF
)"
```

---

### Task 4: 通信ログユーティリティ (`dispatch-log.sh`)

ログの閲覧・フィルタ・サマリを提供する。

**Files:**
- Create: `scripts/runtime/dispatch-log.sh`

- [ ] **Step 1: dispatch-log.sh を作成**

```bash
#!/usr/bin/env bash
# dispatch-log.sh — cmux dispatch 通信ログの閲覧・分析
#
# Usage:
#   dispatch-log.sh show [--session <session-id>]   最新セッションのログ表示
#   dispatch-log.sh filter --worker <worker-id>     特定ワーカーのログ
#   dispatch-log.sh summary [--session <session-id>] サマリ表示

set -euo pipefail

LOG_DIR="/tmp/cmux-dispatch-log"
SUBCOMMAND="${1:-show}"
shift || true

SESSION_ID=""
WORKER_FILTER=""

# --- 引数パース ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --session) SESSION_ID="$2"; shift 2 ;;
    --worker)  WORKER_FILTER="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# 最新セッションのログファイルを取得
_latest_log() {
  if [[ -n "$SESSION_ID" ]]; then
    echo "${LOG_DIR}/${SESSION_ID}.jsonl"
  else
    ls -t "${LOG_DIR}"/*.jsonl 2>/dev/null | head -1
  fi
}

case "$SUBCOMMAND" in
  show)
    LOG_FILE=$(_latest_log)
    if [[ -z "$LOG_FILE" || ! -f "$LOG_FILE" ]]; then
      echo "[dispatch-log] No log files found in ${LOG_DIR}" >&2
      exit 1
    fi
    echo "=== Session: $(basename "$LOG_FILE" .jsonl) ===" >&2
    /usr/bin/python3 -c "
import json, sys
for line in open('$LOG_FILE'):
    e = json.loads(line.strip())
    ts = e.get('ts', '?')[:19]
    fr = e.get('from', '?')
    to = e.get('to', '?')
    tp = e.get('type', '?')
    detail = ''
    if tp == 'dispatch':
        detail = f\"[{e.get('model','')}] {e.get('task','')}\"
    elif tp == 'result':
        detail = e.get('status', '')
    elif tp == 'retry':
        detail = f\"attempt {e.get('attempt','')}\"
    elif tp == 'state_change':
        detail = f\"{e.get('old_state','')} → {e.get('new_state','')}\"
    elif tp == 'escalate':
        detail = e.get('reason', '')
    elif tp == 'prompt':
        body = e.get('body', '')
        detail = body[:80] + '...' if len(body) > 80 else body
    print(f'{ts}  {fr:>10} → {to:<10}  [{tp:^14}]  {detail}')
"
    ;;

  filter)
    if [[ -z "$WORKER_FILTER" ]]; then
      echo "[dispatch-log] --worker is required for filter" >&2
      exit 1
    fi
    LOG_FILE=$(_latest_log)
    if [[ -z "$LOG_FILE" || ! -f "$LOG_FILE" ]]; then
      echo "[dispatch-log] No log files found" >&2
      exit 1
    fi
    grep "\"${WORKER_FILTER}\"" "$LOG_FILE" | /usr/bin/python3 -c "
import json, sys
for line in sys.stdin:
    e = json.loads(line.strip())
    ts = e.get('ts', '?')[:19]
    fr = e.get('from', '?')
    to = e.get('to', '?')
    tp = e.get('type', '?')
    print(f'{ts}  {fr:>10} → {to:<10}  [{tp}]')
"
    ;;

  summary)
    LOG_FILE=$(_latest_log)
    if [[ -z "$LOG_FILE" || ! -f "$LOG_FILE" ]]; then
      echo "[dispatch-log] No log files found" >&2
      exit 1
    fi
    echo "=== Dispatch Summary ===" >&2
    /usr/bin/python3 -c "
import json, sys
from collections import Counter
from datetime import datetime

dispatches = []
results = []
models = Counter()

for line in open('$LOG_FILE'):
    e = json.loads(line.strip())
    tp = e.get('type')
    if tp == 'dispatch':
        dispatches.append(e)
        models[e.get('model', 'unknown')] += 1
    elif tp == 'result':
        results.append(e)

completed = sum(1 for r in results if r.get('status') == 'completed')
failed = sum(1 for r in results if r.get('status') == 'failed')

print(f'Total dispatches: {len(dispatches)}')
print(f'Results: {completed} completed, {failed} failed')
if dispatches:
    print(f'Success rate: {completed/len(dispatches)*100:.0f}%')
print(f'Models used: {dict(models)}')
"
    ;;

  *)
    echo "[dispatch-log] Unknown subcommand: $SUBCOMMAND" >&2
    echo "Usage: dispatch-log.sh {show|filter|summary}" >&2
    exit 1
    ;;
esac
```

- [ ] **Step 2: テストデータで動作確認**

```bash
# テストログ作成
mkdir -p /tmp/cmux-dispatch-log
cat > /tmp/cmux-dispatch-log/test-session.jsonl << 'JSONL'
{"ts":"2026-03-30T10:00:00Z","from":"master","to":"w-1","type":"dispatch","model":"claude","task":"API実装","workspace":"ws:1"}
{"ts":"2026-03-30T10:00:01Z","from":"master","to":"w-1","type":"prompt","body":"APIエンドポイントを実装してください"}
{"ts":"2026-03-30T10:00:02Z","from":"master","to":"w-2","type":"dispatch","model":"codex","task":"セキュリティ分析","workspace":"ws:2"}
{"ts":"2026-03-30T10:30:00Z","from":"w-1","to":"master","type":"result","status":"completed","result_file":"/tmp/cmux-results/w-1.md"}
{"ts":"2026-03-30T10:45:00Z","from":"w-2","to":"master","type":"result","status":"failed","error":"timeout"}
JSONL
bash scripts/runtime/dispatch-log.sh show --session test-session
```

Expected: 5行のフォーマット済みログ出力

- [ ] **Step 3: summary サブコマンドの確認**

```bash
bash scripts/runtime/dispatch-log.sh summary --session test-session
```

Expected: `Total dispatches: 2`, `Results: 1 completed, 1 failed`, `Success rate: 50%`

- [ ] **Step 4: テストデータを削除 + 実行権限付与**

```bash
rm /tmp/cmux-dispatch-log/test-session.jsonl
chmod +x scripts/runtime/dispatch-log.sh
```

- [ ] **Step 5: Commit**

```bash
git add scripts/runtime/dispatch-log.sh
git commit -m "$(cat <<'EOF'
✨ feat(dispatch): add dispatch-log.sh for communication log viewing

Provides show/filter/summary subcommands for JSONL dispatch logs.
Human-readable formatted output with timestamps and event details.
EOF
)"
```

---

### Task 5: Worker Router スキル (`/dispatch`)

全体を束ねるスキル。タスクの振り分け判定 + Worker 起動 + 結果回収を Claude Code に指示する。

**Files:**
- Create: `.config/claude/skills/dispatch/SKILL.md`

- [ ] **Step 1: スキルディレクトリ作成**

```bash
mkdir -p .config/claude/skills/dispatch
```

- [ ] **Step 2: SKILL.md を作成**

```markdown
---
name: dispatch
description: cmux Worker Router — タスクをサブエージェントまたは cmux Worker（Claude Code / Codex / Gemini）に振り分けて実行する。長時間タスク・マルチモデル・高並列の場合に cmux Worker を使用。
user_invocable: true
---

# /dispatch — cmux Worker Router

タスクを受けて「サブエージェント or cmux Worker」を判定し、適切な実行環境で起動する。

## 判定フロー

以下の順序で判定する。最初にマッチした条件で実行先を決定:

1. **5分以内 & 構造化結果が必要** → サブエージェント（Agent tool）
2. **Codex 向きタスク** → cmux Codex Worker
   - 実装前リスク分析、セキュリティ深掘り、設計判断、トレードオフ分析
   - 複雑デバッグ、コードレビュー（100行以上）、Plan 批評
   - 参照: `rules/codex-delegation.md`
3. **Gemini 向きタスク** → cmux Gemini Worker
   - コードベース全体分析（200K超）、外部リサーチ（Google Search grounding）
   - マルチモーダル処理（PDF/動画/音声）、ドキュメント全体分析
   - 参照: `rules/gemini-delegation.md`
4. **30分以上 or 人間介入の可能性** → cmux Claude Code Worker
5. **5+ 並列タスク** → cmux Worker（モデルはタスク性質で選択）
6. **それ以外** → サブエージェント（デフォルト）

## 使い方

```
/dispatch タスク内容をここに記述
```

## 実行手順

### サブエージェントに振り分ける場合

通常の Agent tool で実行する。特別な手順なし。

### cmux Worker に振り分ける場合

<IMPORTANT>
cmux 内で実行していることを確認すること。`CMUX_WORKSPACE_ID` 環境変数が設定されていない場合は cmux 外なのでサブエージェントにフォールバックする。
</IMPORTANT>

**Step 1: Worker を起動する**

Bash tool で `launch-worker.sh` を実行:

```bash
# Claude Code Worker の場合
scripts/runtime/launch-worker.sh --model claude --task "タスク内容" --worktree feature/branch-name

# Codex Worker の場合
scripts/runtime/launch-worker.sh --model codex --task "タスク内容"

# Gemini Worker の場合
scripts/runtime/launch-worker.sh --model gemini --task "タスク内容"
```

出力される `workspace_id` と `worker_id` を記録する。

**Step 2: 結果を回収する**

Bash tool で `collect-result.sh` を実行:

```bash
scripts/runtime/collect-result.sh --workspace <workspace_id> --worker <worker_id> --timeout 1800
```

- 完了: 結果テキストが stdout に出力される
- タイムアウト: exit code 2
- エラー: exit code 1（リトライ上限超過）

**Step 3: 結果をユーザーに報告する**

回収した結果をユーザーに要約して報告する。

### 複数 Worker を並列起動する場合

複数の `launch-worker.sh` を Bash tool で並列実行し、その後 `collect-result.sh` をそれぞれ実行する。

```bash
# 並列起動
WS1=$(scripts/runtime/launch-worker.sh --model claude --task "API実装" --worktree feature/api)
WS2=$(scripts/runtime/launch-worker.sh --model codex --task "セキュリティ分析")

# 結果回収（それぞれバックグラウンドで）
scripts/runtime/collect-result.sh --workspace $(echo $WS1 | cut -d' ' -f1) --worker $(echo $WS1 | cut -d' ' -f2) &
scripts/runtime/collect-result.sh --workspace $(echo $WS2 | cut -d' ' -f1) --worker $(echo $WS2 | cut -d' ' -f2) &
wait
```

## 通信ログ

全通信は自動的に `/tmp/cmux-dispatch-log/` に JSONL 形式で記録される。

```bash
# ログ閲覧
scripts/runtime/dispatch-log.sh show

# 特定ワーカーのフィルタ
scripts/runtime/dispatch-log.sh filter --worker <worker_id>

# サマリ
scripts/runtime/dispatch-log.sh summary
```

## cmux 外での挙動

cmux 外で実行された場合、全てサブエージェントにフォールバックする。cmux Worker 機能は無効化される。
```

- [ ] **Step 3: スキルが認識されることを確認**

```bash
ls .config/claude/skills/dispatch/SKILL.md
```

Expected: ファイルが存在する

- [ ] **Step 4: Commit**

```bash
git add .config/claude/skills/dispatch/SKILL.md
git commit -m "$(cat <<'EOF'
✨ feat(dispatch): add /dispatch skill for cmux worker routing

Routes tasks to subagents or cmux workers (Claude Code/Codex/Gemini)
based on task characteristics. Integrates existing delegation rules.
EOF
)"
```

---

### Task 6: 統合テスト + ドキュメント整合性

全コンポーネントの整合性を確認し、リファレンスを更新する。

**Files:**
- Modify: `.config/claude/references/cmux-ecosystem.md` (dispatch セクション追加)

- [ ] **Step 1: スクリプトの source チェーン確認**

```bash
# dispatch_logger.sh が他スクリプトから source できることを確認
bash -c 'source scripts/lib/dispatch_logger.sh && echo "dispatch_logger: OK"'
bash -c 'source scripts/lib/dispatch_logger.sh && dispatch_log_dispatch "test" "claude" "test task" "ws:test" && echo "logging: OK"'
```

Expected: 両方 `OK`

- [ ] **Step 2: launch-worker.sh の引数バリデーション**

```bash
bash scripts/runtime/launch-worker.sh --model invalid --task "test" 2>&1 | head -1
```

Expected: `[launch-worker] Unknown model: invalid`

- [ ] **Step 3: collect-result.sh の引数バリデーション**

```bash
bash scripts/runtime/collect-result.sh 2>&1 | head -1
```

Expected: Usage メッセージ

- [ ] **Step 4: dispatch-log.sh の全サブコマンド確認**

```bash
bash scripts/runtime/dispatch-log.sh invalid 2>&1 | head -1
```

Expected: `[dispatch-log] Unknown subcommand: invalid`

- [ ] **Step 5: cmux-ecosystem.md に dispatch セクションを追加**

`.config/claude/references/cmux-ecosystem.md` の末尾（`## Plugin vs Agent Skills の使い分け` の前）に追加:

```markdown
## dispatch (Worker Router)

サブエージェントと cmux Worker を自動振り分けする `/dispatch` スキル。

### コンポーネント

| ファイル | 役割 |
|---------|------|
| `skills/dispatch/SKILL.md` | Worker Router スキル（判定ロジック） |
| `scripts/runtime/launch-worker.sh` | Worker 起動（cmux ワークスペース作成 + モデル別 CLI 起動） |
| `scripts/runtime/collect-result.sh` | 結果回収（ポーリング + 完了検出 + リトライ） |
| `scripts/runtime/dispatch-log.sh` | 通信ログ閲覧（show / filter / summary） |
| `scripts/lib/dispatch_logger.sh` | ログ記録共通関数（JSONL 追記） |
| `references/subagent-vs-cmux-worker.md` | 判定基準の比較表 |

### 振り分け基準

- **デフォルト**: サブエージェント（Agent tool）
- **cmux Worker 昇格条件**: 長時間(30分+)、マルチモデル(Codex/Gemini)、高並列(5+)、人間介入

### 通信ログ

`/tmp/cmux-dispatch-log/{session-id}.jsonl` に全通信を記録。`dispatch-log.sh summary` でサマリ表示。
```

- [ ] **Step 6: テストログの残りカスを掃除**

```bash
rm -f /tmp/cmux-dispatch-log/test-*.jsonl 2>/dev/null; echo "cleaned"
```

- [ ] **Step 7: Commit**

```bash
git add .config/claude/references/cmux-ecosystem.md
git commit -m "$(cat <<'EOF'
📝 docs(cmux): add dispatch Worker Router section to ecosystem reference

Documents component layout, routing criteria, and communication logging.
EOF
)"
```

---

## Implementation Order

```
Task 0: Plugin install (prerequisite)
  ↓
Task 1: dispatch_logger.sh (shared dependency)
  ↓
Task 2: launch-worker.sh (uses logger)
  ↓
Task 3: collect-result.sh (uses logger)
  ↓
Task 4: dispatch-log.sh (reads logs, standalone)
  ↓
Task 5: /dispatch skill (ties everything together)
  ↓
Task 6: Integration test + docs update
```

Tasks 2-4 could be parallelized after Task 1, but sequential is simpler for a first implementation.
