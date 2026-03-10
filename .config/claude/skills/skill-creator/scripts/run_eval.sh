#!/usr/bin/env bash
set -euo pipefail

# run_eval.sh — Run claude -p with and without a skill for A/B benchmarking
#
# Usage: run_eval.sh <skill-name> <evals-json> [workspace-dir]
#
# For each eval in evals.json, launches two parallel claude -p processes:
#   1. With skill   → eval-{name}/with_skill/outputs/response.md
#   2. Without skill → eval-{name}/without_skill/outputs/response.md
# Records timing data (duration_ms) for each run.

##############################################################################
# Arguments
##############################################################################

if [[ $# -lt 2 ]]; then
  echo "Usage: run_eval.sh <skill-name> <evals-json> [workspace-dir]" >&2
  exit 1
fi

SKILL_NAME="$1"
EVALS_JSON="$2"
WORKSPACE="${3:-.skill-eval/${SKILL_NAME}}"

##############################################################################
# Resolve skill path
##############################################################################

SKILL_DIR="${HOME}/.claude/skills/${SKILL_NAME}"

if [[ ! -d "$SKILL_DIR" ]]; then
  echo "ERROR: Skill directory not found: ${SKILL_DIR}" >&2
  exit 1
fi

if [[ ! -f "${SKILL_DIR}/SKILL.md" ]]; then
  echo "ERROR: SKILL.md not found in: ${SKILL_DIR}" >&2
  exit 1
fi

##############################################################################
# Validate evals file
##############################################################################

if [[ ! -f "$EVALS_JSON" ]]; then
  echo "ERROR: Evals file not found: ${EVALS_JSON}" >&2
  exit 1
fi

# Validate JSON structure
if ! jq empty "$EVALS_JSON" 2>/dev/null; then
  echo "ERROR: Invalid JSON in: ${EVALS_JSON}" >&2
  exit 1
fi

EVAL_COUNT=$(jq 'length' "$EVALS_JSON")
if [[ "$EVAL_COUNT" -eq 0 ]]; then
  echo "ERROR: No evals found in: ${EVALS_JSON}" >&2
  exit 1
fi

##############################################################################
# Auto-increment iteration number
##############################################################################

mkdir -p "$WORKSPACE"

ITERATION=1
while [[ -d "${WORKSPACE}/iteration-${ITERATION}" ]]; do
  ITERATION=$((ITERATION + 1))
done

ITER_DIR="${WORKSPACE}/iteration-${ITERATION}"
mkdir -p "$ITER_DIR"

echo "=== Skill Eval: ${SKILL_NAME} ==="
echo "  Skill:     ${SKILL_DIR}"
echo "  Evals:     ${EVALS_JSON} (${EVAL_COUNT} cases)"
echo "  Iteration: ${ITERATION}"
echo "  Output:    ${ITER_DIR}"
echo ""

##############################################################################
# Allowed tools for claude -p runs
##############################################################################

ALLOWED_TOOLS="Read,Grep,Glob,Bash,WebFetch,WebSearch"

##############################################################################
# Run helper — executes claude -p and records timing
##############################################################################

run_claude() {
  local output_dir="$1"
  local prompt="$2"
  local skill_dir="$3"  # skill directory path, or empty for baseline

  mkdir -p "${output_dir}/outputs"

  local start_ms
  start_ms=$(python3 -c 'import time; print(int(time.time() * 1000))')

  # Run claude -p (|| true to capture exit code under set -e)
  local exit_code=0
  if [[ -n "$skill_dir" ]]; then
    claude -p "$prompt" \
      --allowedTools "$ALLOWED_TOOLS" \
      --skill "$skill_dir" \
      > "${output_dir}/outputs/response.md" 2>/dev/null || exit_code=$?
  else
    claude -p "$prompt" \
      --allowedTools "$ALLOWED_TOOLS" \
      > "${output_dir}/outputs/response.md" 2>/dev/null || exit_code=$?
  fi

  local end_ms
  end_ms=$(python3 -c 'import time; print(int(time.time() * 1000))')
  local duration_ms=$((end_ms - start_ms))

  # Write timing.json
  cat > "${output_dir}/timing.json" <<TIMING_EOF
{
  "duration_ms": ${duration_ms},
  "total_duration_seconds": $(python3 -c "print(round(${duration_ms} / 1000.0, 1))"),
  "exit_code": ${exit_code}
}
TIMING_EOF

  return $exit_code
}

##############################################################################
# Main loop — launch parallel runs for each eval
##############################################################################

PIDS=()
EVAL_NAMES=()
FAILURES=0

for i in $(seq 0 $((EVAL_COUNT - 1))); do
  # Extract eval fields
  EVAL_ID=$(jq -r ".[$i].id" "$EVALS_JSON")
  EVAL_NAME=$(jq -r ".[$i].name" "$EVALS_JSON")
  EVAL_PROMPT=$(jq -r ".[$i].prompt" "$EVALS_JSON")

  # Fallback: use id if name is null/empty
  if [[ -z "$EVAL_NAME" || "$EVAL_NAME" == "null" ]]; then
    EVAL_NAME="eval-${EVAL_ID}"
  fi

  EVAL_DIR="${ITER_DIR}/eval-${EVAL_NAME}"
  mkdir -p "${EVAL_DIR}/with_skill" "${EVAL_DIR}/without_skill"

  # Copy eval metadata
  jq ".[$i]" "$EVALS_JSON" > "${EVAL_DIR}/eval_metadata.json"

  echo "[${EVAL_NAME}] Starting parallel runs..."

  # --- With skill (background) ---
  (
    run_claude "${EVAL_DIR}/with_skill" "$EVAL_PROMPT" "${SKILL_DIR}"
  ) &
  PIDS+=($!)
  EVAL_NAMES+=("${EVAL_NAME}/with_skill")

  # --- Without skill / baseline (background) ---
  (
    run_claude "${EVAL_DIR}/without_skill" "$EVAL_PROMPT" ""
  ) &
  PIDS+=($!)
  EVAL_NAMES+=("${EVAL_NAME}/without_skill")
done

##############################################################################
# Wait for all processes and report
##############################################################################

echo ""
echo "Waiting for ${#PIDS[@]} runs to complete..."
echo ""

for idx in "${!PIDS[@]}"; do
  pid="${PIDS[$idx]}"
  name="${EVAL_NAMES[$idx]}"
  if wait "$pid"; then
    echo "  [DONE] ${name}"
  else
    echo "  [FAIL] ${name} (exit code: $?)"
    FAILURES=$((FAILURES + 1))
  fi
done

echo ""
echo "=== Results ==="
echo "  Completed: $((${#PIDS[@]} - FAILURES))/${#PIDS[@]}"
if [[ $FAILURES -gt 0 ]]; then
  echo "  Failures:  ${FAILURES}"
fi
echo "  Output:    ${ITER_DIR}"
echo ""

# Output the iteration directory path (for programmatic consumption)
echo "${ITER_DIR}"

exit $FAILURES
