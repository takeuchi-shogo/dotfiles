#!/usr/bin/env bash
set -euo pipefail

# Autonomous session runner — claude -p でヘッドレス実行
TASK_DIR="${1:-.autonomous/default}"
MAX_SESSIONS="${2:-10}"
BUDGET="${3:-5.00}"

LOCK_FILE="${TASK_DIR}/run.lock"
TASK_LIST="${TASK_DIR}/task_list.md"
PROGRESS="${TASK_DIR}/progress.md"
SESSION_LOG="${TASK_DIR}/sessions"

# Lock check
if [[ -f "$LOCK_FILE" ]]; then
  echo "ERROR: Another session is running (${LOCK_FILE} exists)" >&2
  exit 1
fi

# Create lock
echo "$$" > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

mkdir -p "$SESSION_LOG"

for i in $(seq 1 "$MAX_SESSIONS"); do
  # Check if all tasks are done
  if ! grep -q '^\- \[ \]' "$TASK_LIST" 2>/dev/null; then
    echo "All tasks completed!"
    break
  fi

  echo "=== Session $i/$MAX_SESSIONS ==="

  # Snapshot task state before session
  BEFORE_DONE=$(grep -c '^\- \[x\]' "$TASK_LIST" 2>/dev/null || echo 0)
  TOTAL_TASKS=$(grep -c '^\- \[' "$TASK_LIST" 2>/dev/null || echo 0)

  TASK_CONTENT=$(cat "$TASK_LIST")
  PROMPT=$(sed "s|{task_list_content}|${TASK_CONTENT}|g; s|{work_dir}|$(pwd)|g" \
    "${TASK_DIR}/executor-prompt.md" 2>/dev/null || echo "$TASK_CONTENT")

  claude -p "$PROMPT" \
    --allowedTools "Read,Write,Edit,Bash,Glob,Grep" \
    --max-cost "$BUDGET" \
    > "${SESSION_LOG}/session-${i}.md" 2>&1 || true

  # Detect which tasks were completed in this session
  AFTER_DONE=$(grep -c '^\- \[x\]' "$TASK_LIST" 2>/dev/null || echo 0)
  REMAINING=$((TOTAL_TASKS - AFTER_DONE))
  COMPLETED_THIS=$((AFTER_DONE - BEFORE_DONE))

  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "Session $i completed: +${COMPLETED_THIS} tasks done, ${REMAINING} remaining"

  # Structured progress entry
  {
    echo "### Session $i — ${TIMESTAMP}"
    echo ""
    echo "- **Status**: completed"
    echo "- **Tasks completed this session**: ${COMPLETED_THIS}"
    echo "- **Total progress**: ${AFTER_DONE}/${TOTAL_TASKS}"
    echo "- **Output**: session-${i}.md"
    if [[ "$COMPLETED_THIS" -gt 0 ]]; then
      echo "- **Newly completed**:"
      # Extract task names that are now checked (compare before/after)
      grep '^\- \[x\]' "$TASK_LIST" | tail -n "$COMPLETED_THIS" | sed 's/^/  /'
    fi
    echo ""
  } >> "$PROGRESS"
done

rm -f "$LOCK_FILE"
echo "Autonomous execution finished."
