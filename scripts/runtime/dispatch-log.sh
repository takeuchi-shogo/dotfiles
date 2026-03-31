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
    LOG_FILE=$(_latest_log)
    if [[ -z "$LOG_FILE" || ! -f "$LOG_FILE" ]]; then
      echo "[dispatch-log] No log files found" >&2
      exit 1
    fi
    grep -F "\"${WORKER_FILTER}\"" "$LOG_FILE" | /usr/bin/python3 -c "
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

  *)
    echo "[dispatch-log] Unknown subcommand: $SUBCOMMAND" >&2
    echo "Usage: dispatch-log.sh {show|filter|summary}" >&2
    exit 1
    ;;
esac
