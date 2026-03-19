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

# --- タスクレジストリ登録 ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY_SCRIPT="${SCRIPT_DIR}/../../scripts/lib/task_registry.py"
TASK_NAME=$(basename "$TASK_DIR")
ENTRY_ID=""
if [[ -f "$REGISTRY_SCRIPT" ]]; then
  LIB_DIR=$(dirname "$REGISTRY_SCRIPT")
  ENTRY_ID=$(LIB_DIR="$LIB_DIR" TASK_NAME="$TASK_NAME" PROGRESS="$PROGRESS" python3 - <<'PYEOF'
import sys, os
sys.path.insert(0, os.environ["LIB_DIR"])
from task_registry import register
print(register("async", "autonomous", os.environ["TASK_NAME"], output_path=os.environ["PROGRESS"]))
PYEOF
  ) 2>/dev/null
  if [[ -n "$ENTRY_ID" ]]; then
    echo "Registry entry: $ENTRY_ID"
  else
    echo "WARNING: Failed to register task in registry" >&2
  fi
fi

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

  SESSION_EXIT=0
  claude -p "$PROMPT" \
    --allowedTools "Read,Write,Edit,Bash,Glob,Grep" \
    --max-cost "$BUDGET" \
    > "${SESSION_LOG}/session-${i}.md" 2>&1 || SESSION_EXIT=$?

  # Detect which tasks were completed in this session
  AFTER_DONE=$(grep -c '^\- \[x\]' "$TASK_LIST" 2>/dev/null || echo 0)
  REMAINING=$((TOTAL_TASKS - AFTER_DONE))
  COMPLETED_THIS=$((AFTER_DONE - BEFORE_DONE))

  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "Session $i completed: +${COMPLETED_THIS} tasks done, ${REMAINING} remaining"

  # Determine session status
  if [[ "$SESSION_EXIT" -ne 0 && "$COMPLETED_THIS" -eq 0 ]]; then
    SESSION_STATUS="failed (exit code: ${SESSION_EXIT})"
  else
    SESSION_STATUS="completed"
  fi

  # Structured progress entry
  {
    echo "### Session $i — ${TIMESTAMP}"
    echo ""
    echo "- **Status**: ${SESSION_STATUS}"
    echo "- **Tasks completed this session**: ${COMPLETED_THIS}"
    echo "- **Total progress**: ${AFTER_DONE}/${TOTAL_TASKS}"
    echo "- **Output**: session-${i}.md"
    if [[ "$COMPLETED_THIS" -gt 0 ]]; then
      echo "- **Newly completed**:"
      # diff でチェック済みタスクを比較（順序非依存）
      diff <(grep '^\- \[x\]' "$TASK_LIST" 2>/dev/null | head -n "$BEFORE_DONE" | sort) \
           <(grep '^\- \[x\]' "$TASK_LIST" 2>/dev/null | sort) \
        | grep '^>' | sed 's/^> /  /' || true
    fi
    echo ""
  } >> "$PROGRESS"
done

# --- タスクレジストリ更新 ---
if [[ -n "$ENTRY_ID" && -f "$REGISTRY_SCRIPT" ]]; then
  LIB_DIR=$(dirname "$REGISTRY_SCRIPT")
  # 残タスクがあれば failed、なければ completed
  if grep -q '^\- \[ \]' "$TASK_LIST" 2>/dev/null; then
    FINAL_STATUS="failed"
  else
    FINAL_STATUS="completed"
  fi
  LIB_DIR="$LIB_DIR" ENTRY_ID="$ENTRY_ID" FINAL_STATUS="$FINAL_STATUS" PROGRESS="$PROGRESS" python3 - <<'PYEOF' 2>/dev/null || echo "WARNING: Failed to update registry" >&2
import sys, os
sys.path.insert(0, os.environ["LIB_DIR"])
from task_registry import update_status
update_status(os.environ["ENTRY_ID"], os.environ["FINAL_STATUS"], output_path=os.environ["PROGRESS"])
PYEOF
fi

# --- PR Delivery (Stripe Minions pattern) ---
COMPLETION_MODE="${COMPLETION_MODE:-strict}"
CREATE_PR="${CREATE_PR:-false}"

if [[ "$CREATE_PR" == "true" ]]; then
  BRANCH_NAME=$(git branch --show-current 2>/dev/null || echo "")

  if [[ -n "$BRANCH_NAME" && "$BRANCH_NAME" != "master" && "$BRANCH_NAME" != "main" ]]; then
    # Determine PR title and status
    if [[ "$FINAL_STATUS" == "completed" ]]; then
      PR_TITLE="${PR_TITLE_PREFIX:-[autonomous]} ${TASK_NAME}"
      COMPLETION_LABEL="Full"
    elif [[ "$COMPLETION_MODE" == "graduated" ]]; then
      PR_TITLE="[WIP] ${PR_TITLE_PREFIX:-[autonomous]} ${TASK_NAME}"
      COMPLETION_LABEL="Partial"
    else
      echo "Skipping PR creation: task not completed and graduated mode not enabled"
      COMPLETION_LABEL="Blocked"
    fi

    if [[ "$COMPLETION_LABEL" != "Blocked" ]]; then
      # Build PR body from template
      TEMPLATE="${TASK_DIR}/../../templates/pr-template.md"
      if [[ -f "$TEMPLATE" ]]; then
        TASK_PROGRESS=$(cat "$TASK_LIST" 2>/dev/null || echo "N/A")
        CHANGES=$(git diff --stat HEAD~1 2>/dev/null || echo "N/A")
        PR_BODY=$(sed \
          -e "s|{summary}|Automated task: ${TASK_NAME}|g" \
          -e "s|{blueprint_name}|${BLUEPRINT:-default}|g" \
          -e "s|{session_count}|${i}|g" \
          -e "s|{completion_status}|${COMPLETION_LABEL}|g" \
          "$TEMPLATE")
        # Replace multiline placeholders
        PR_BODY=$(echo "$PR_BODY" | sed "s|{changes}|${CHANGES}|g")
        PR_BODY=$(echo "$PR_BODY" | sed "s|{task_progress}|See progress.md|g")
        PR_BODY=$(echo "$PR_BODY" | sed "s|{handback_report}|See session logs|g")
      else
        PR_BODY="Automated PR by /autonomous. See progress.md for details."
      fi

      git push -u origin "$BRANCH_NAME" 2>/dev/null
      gh pr create --title "$PR_TITLE" --body "$PR_BODY" 2>/dev/null && \
        echo "PR created successfully" || \
        echo "WARNING: Failed to create PR" >&2
    fi
  fi

  # Notification (macOS)
  if command -v osascript &>/dev/null; then
    osascript -e "display notification \"${TASK_NAME}: ${COMPLETION_LABEL}\" with title \"Autonomous Complete\" sound name \"Glass\"" 2>/dev/null || true
  fi
fi

echo "Autonomous execution finished."
