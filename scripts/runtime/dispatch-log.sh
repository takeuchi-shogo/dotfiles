#!/usr/bin/env bash
# dispatch-log.sh — cmux dispatch 通信ログの閲覧・分析
#
# Usage:
#   dispatch-log.sh show [--session <session-id>]   最新セッションのログ表示
#   dispatch-log.sh filter --worker <worker-id>     特定ワーカーのログ (全セッション横断)
#   dispatch-log.sh summary [--session <session-id>] サマリ表示
#   dispatch-log.sh pending                          起動済みで未回収の worker (全セッション横断)
#
# セッション ID は "日時-$$" でプロセスごとに振られるため、launch と collect を
# 別コマンドで実行すると 1 つの worker のログが 2 ファイルに分かれる。
# worker 単位で見る filter / pending は最新 1 ファイルではなく全ファイルを読む。

set -euo pipefail

LOG_DIR="${DISPATCH_LOG_DIR:-/tmp/cmux-dispatch-log}"
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

# 全セッションのログファイル (worker 単位で追うとき用)
_all_logs() {
  if [[ -n "$SESSION_ID" ]]; then
    echo "${LOG_DIR}/${SESSION_ID}.jsonl"
  else
    # ヒット無しの ls は exit 1。set -e で握り潰されないよう明示的に成功させる
    ls -t "${LOG_DIR}"/*.jsonl 2>/dev/null || true
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
    /usr/bin/python3 - "$LOG_FILE" <<'PYEOF'
import json, sys
for line in open(sys.argv[1]):
    e = json.loads(line.strip())
    ts = e.get('ts', '?')[:19]
    fr = e.get('from', '?')
    to = e.get('to', '?')
    tp = e.get('type', '?')
    detail = ''
    if tp == 'dispatch':
        detail = f"[{e.get('model','')}] {e.get('task','')}"
    elif tp == 'result':
        detail = e.get('status', '')
    elif tp == 'retry':
        detail = f"attempt {e.get('attempt','')}"
    elif tp == 'state_change':
        detail = f"{e.get('old_state','')} → {e.get('new_state','')}"
    elif tp == 'escalate':
        detail = e.get('reason', '')
    elif tp == 'prompt':
        body = e.get('body', '')
        detail = body[:80] + '...' if len(body) > 80 else body
    print(f'{ts}  {fr:>10} → {to:<10}  [{tp:^14}]  {detail}')
PYEOF
    ;;

  filter)
    if [[ -z "$WORKER_FILTER" ]]; then
      echo "[dispatch-log] --worker is required for filter" >&2
      exit 1
    fi
    LOG_FILES=$(_all_logs)
    if [[ -z "$LOG_FILES" ]]; then
      echo "[dispatch-log] No log files found" >&2
      exit 1
    fi
    # ログのパスは生成物で空白を含まないため単語分割で渡す (bash 3.2 で動かすため
    # mapfile は使わない)
    # shellcheck disable=SC2086
    grep -hF "\"${WORKER_FILTER}\"" $LOG_FILES | /usr/bin/python3 -c "
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
    /usr/bin/python3 - "$LOG_FILE" <<'PYEOF'
import json, sys
from collections import Counter

dispatches = []
results = []
models = Counter()

for line in open(sys.argv[1]):
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
PYEOF
    ;;

  pending)
    # 起動されたが result が来ていない worker を全セッション横断で洗う。
    # collect を呼び忘れた / 呼び出し元が落ちた worker はここにしか現れない。
    LOG_FILES=$(_all_logs)
    if [[ -z "$LOG_FILES" ]]; then
      echo "[dispatch-log] No log files found in ${LOG_DIR}" >&2
      exit 1
    fi
    # shellcheck disable=SC2086
    /usr/bin/python3 - $LOG_FILES <<'PYEOF'
import json, sys
from datetime import datetime, timezone

launched = {}   # worker_id -> dict
resolved = set()
state = {}

for path in sys.argv[1:]:
    try:
        fh = open(path)
    except OSError:
        continue
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            frm, to = e.get('from', ''), e.get('to', '')
            worker = to if frm == 'master' else frm
            if not worker or worker == 'master':
                continue
            tp = e.get('type')
            if tp == 'dispatch':
                launched[worker] = {
                    'ts': e.get('ts', ''),
                    'model': e.get('model', '?'),
                    'task': (e.get('task') or '')[:60],
                }
            elif tp == 'result':
                resolved.add(worker)
            elif tp == 'state_change':
                state[worker] = e.get('new_state', '?')

stuck = [(w, d) for w, d in launched.items() if w not in resolved]
if not stuck:
    print('未回収の worker はありません')
    sys.exit(0)

now = datetime.now(timezone.utc)
print(f'未回収 {len(stuck)} 件 (起動済みで result 未着):')
for worker, d in sorted(stuck, key=lambda x: x[1]['ts']):
    age = ''
    try:
        started = datetime.fromisoformat(d['ts'].replace('Z', '+00:00'))
        age = f'{int((now - started).total_seconds() // 60)}分経過'
    except (ValueError, AttributeError):
        age = '経過時間不明'
    print(f"  {worker}  [{d['model']}]  {age}  last_state={state.get(worker, '?')}")
    print(f"      task: {d['task']}")
PYEOF
    ;;

  *)
    echo "[dispatch-log] Unknown subcommand: $SUBCOMMAND" >&2
    echo "Usage: dispatch-log.sh {show|filter|summary|pending}" >&2
    exit 1
    ;;
esac
