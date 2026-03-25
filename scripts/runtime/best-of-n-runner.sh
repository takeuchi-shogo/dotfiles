#!/bin/bash
# best-of-n-runner.sh — Run N parallel Claude sessions on separate worktrees,
# compare results, and select the best one.
#
# Usage: best-of-n-runner.sh -n <count> -p "<prompt>" [--auto|--interactive] [--keep-all]
# See: references/best-of-n-guide.md
set -euo pipefail

# ── 1. Defaults & Constants ──────────────────────────────────────
N=3
MODE="auto"
KEEP_ALL=0
PROJECT_DIR=""
PROMPT=""
MAX_N=8
RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
LOG_DIR="${HOME}/.claude/logs"
RESULTS_DIR=""
WORKTREE_DIRS=()
PIDS=()
BEST_WORKTREE=""

# ── 2. Argument parsing ─────────────────────────────────────────
usage() {
    cat <<EOF
Usage: $(basename "$0") -p <prompt> [-n <count>] [--auto|--interactive] [--keep-all] [-d <dir>]

Options:
  -n, --count NUM       Number of parallel runs (default: 3, max: 8)
  -p, --prompt TEXT      Prompt to execute (required)
  -d, --dir DIR          Project directory (default: current dir)
  --auto                 Auto-select best result (default)
  --interactive          Show comparison table, let user choose
  --keep-all             Don't clean up worktrees after completion
  -h, --help             Show this help
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--count)    N="$2"; shift 2 ;;
        -p|--prompt)   PROMPT="$2"; shift 2 ;;
        -d|--dir)      PROJECT_DIR="$2"; shift 2 ;;
        --auto)        MODE="auto"; shift ;;
        --interactive) MODE="interactive"; shift ;;
        --keep-all)    KEEP_ALL=1; shift ;;
        -h|--help)     usage ;;
        *)             echo "Unknown option: $1" >&2; usage ;;
    esac
done

if [[ -z "$PROMPT" ]]; then
    echo "Error: --prompt is required" >&2
    usage
fi

if (( N < 1 || N > MAX_N )); then
    echo "Error: --count must be between 1 and $MAX_N" >&2
    exit 1
fi

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR"

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "Error: $PROJECT_DIR is not a git repository" >&2
    exit 1
fi

if ! command -v claude &>/dev/null; then
    echo "Error: claude CLI not found" >&2
    exit 1
fi

# ── 3. Logging setup ────────────────────────────────────────────
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/best-of-n-${RUN_ID}.log"
RESULTS_DIR="${HOME}/.claude/logs/bon-results-${RUN_ID}"
mkdir -p "$RESULTS_DIR"

log() {
    echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

log "Best-of-N started: N=$N, mode=$MODE, project=$PROJECT_DIR"
log "Prompt: $PROMPT"

# ── 4. Cleanup trap ─────────────────────────────────────────────
cleanup() {
    local exit_code=$?
    # Kill remaining child processes
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    log "Cleanup started (exit_code=$exit_code)"

    for wt in "${WORKTREE_DIRS[@]}"; do
        if [[ "$KEEP_ALL" == "1" ]]; then
            log "Keeping worktree: $wt"
            continue
        fi
        if [[ -n "${BEST_WORKTREE:-}" && "$wt" == "$BEST_WORKTREE" ]]; then
            log "Keeping best worktree: $wt"
            continue
        fi
        if [[ -d "$wt" ]]; then
            log "Removing worktree: $wt"
            git worktree remove --force "$wt" 2>&1 || log "WARN: failed to remove $wt"
        fi
    done

    git worktree prune 2>/dev/null || true
    log "Cleanup completed"
}
trap cleanup EXIT SIGTERM SIGINT

# ── 5. Create N worktrees ───────────────────────────────────────
WORKTREE_BASE="${PROJECT_DIR}/.claude/worktrees"
mkdir -p "$WORKTREE_BASE"

LOCK_FILES=("package-lock.json" "yarn.lock" "pnpm-lock.yaml" "go.sum" "Cargo.lock")

for i in $(seq 1 "$N"); do
    wt_dir="${WORKTREE_BASE}/bon-${RUN_ID}-${i}"
    log "Creating worktree $i: $wt_dir"

    git worktree add "$wt_dir" HEAD --detach --quiet

    # Per-worktree state directories
    wt_state_dir="${wt_dir}/.bon-state/session-state"
    wt_data_dir="${wt_dir}/.bon-state/agent-memory"
    mkdir -p "$wt_state_dir" "$wt_data_dir"

    # Copy-on-create from global session-state
    if [[ -d "${HOME}/.claude/session-state" ]]; then
        cp -R "${HOME}/.claude/session-state/"* "$wt_state_dir/" 2>/dev/null || true
    fi

    # Lock files read-only
    for lockfile in "${LOCK_FILES[@]}"; do
        if [[ -f "${wt_dir}/${lockfile}" ]]; then
            chmod a-w "${wt_dir}/${lockfile}"
        fi
    done

    WORKTREE_DIRS+=("$wt_dir")
done

log "Created $N worktrees"

# ── 6. Launch N parallel Claude sessions ────────────────────────
for i in $(seq 1 "$N"); do
    wt_dir="${WORKTREE_DIRS[$((i-1))]}"
    run_log="${RESULTS_DIR}/run-${i}.log"
    run_exit="${RESULTS_DIR}/run-${i}.exitcode"

    (
        set +e
        cd "$wt_dir" || { echo 1 > "$run_exit"; exit 1; }
        CLAUDE_SESSION_STATE_DIR="${wt_dir}/.bon-state/session-state" \
        AUTOEVOLVE_DATA_DIR="${wt_dir}/.bon-state/agent-memory" \
        claude -p "$PROMPT" \
            > "${RESULTS_DIR}/run-${i}.out" 2>"$run_log"
        echo $? > "$run_exit"
    ) &
    PIDS+=($!)
    log "Launched run $i (PID: ${PIDS[$((i-1))]})"
done

log "All $N runs launched, waiting for completion..."

# ── 7. Wait & collect results ───────────────────────────────────
EXIT_CODES=()
for i in $(seq 1 "$N"); do
    pid="${PIDS[$((i-1))]}"
    wait "$pid" 2>/dev/null || true

    run_exit="${RESULTS_DIR}/run-${i}.exitcode"
    if [[ -f "$run_exit" ]]; then
        EXIT_CODES+=("$(cat "$run_exit")")
    else
        EXIT_CODES+=(1)
    fi
    log "Run $i completed (exit: ${EXIT_CODES[$((i-1))]})"
done

# ── 8. Evaluate runs ────────────────────────────────────────────
# Score weights
W_EXIT=40
W_TEST=40
W_DIFF=20

evaluate_run() {
    local idx="$1"
    local wt_dir="${WORKTREE_DIRS[$((idx-1))]}"
    local exit_code="${EXIT_CODES[$((idx-1))]}"
    local run_log="${RESULTS_DIR}/run-${idx}.log"
    local run_out="${RESULTS_DIR}/run-${idx}.out"

    # Exit code score
    local exit_score=0
    if [[ "$exit_code" == "0" ]]; then
        exit_score=100
    fi

    # Test pass rate (best-effort grep)
    local test_score=0
    local passed=0 failed=0
    local files=("$run_log" "$run_out")

    for f in "${files[@]}"; do
        if [[ -f "$f" ]]; then
            # Go: ok/FAIL patterns
            local go_pass go_fail
            go_pass=$(grep -c '^ok ' "$f" 2>/dev/null || echo 0)
            go_fail=$(grep -c '^FAIL' "$f" 2>/dev/null || echo 0)
            passed=$((passed + go_pass))
            failed=$((failed + go_fail))

            # JS/Python: X passed, Y failed
            local js_pass js_fail
            js_pass=$(grep -oE '[0-9]+ pass' "$f" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
            js_fail=$(grep -oE '[0-9]+ fail' "$f" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
            passed=$((passed + ${js_pass:-0}))
            failed=$((failed + ${js_fail:-0}))
        fi
    done

    if (( passed + failed > 0 )); then
        test_score=$(( passed * 100 / (passed + failed) ))
    fi

    # Diff size (smaller = better)
    local diff_lines=0
    if [[ -d "$wt_dir" ]]; then
        diff_lines=$(cd "$wt_dir" && git diff --stat HEAD 2>/dev/null | tail -1 | grep -oE '[0-9]+' | head -1 || echo 0)
        diff_lines="${diff_lines:-0}"
    fi

    echo "${exit_score}:${test_score}:${diff_lines}"
}

# Collect scores
SCORES=()
DIFF_SIZES=()
for i in $(seq 1 "$N"); do
    result=$(evaluate_run "$i")
    SCORES+=("$result")

    diff_size=$(echo "$result" | cut -d: -f3)
    DIFF_SIZES+=("$diff_size")
done

# Find max diff for normalization
max_diff=1
for d in "${DIFF_SIZES[@]}"; do
    if (( d > max_diff )); then
        max_diff=$d
    fi
done

# Calculate weighted scores
WEIGHTED_SCORES=()
for i in $(seq 1 "$N"); do
    IFS=: read -r exit_s test_s diff_s <<< "${SCORES[$((i-1))]}"
    diff_s="${diff_s:-0}"

    # Normalize diff: smaller is better (invert)
    diff_score=100
    if (( max_diff > 0 && diff_s > 0 )); then
        diff_score=$(( (max_diff - diff_s) * 100 / max_diff ))
    fi

    total=$(( exit_s * W_EXIT / 100 + test_s * W_TEST / 100 + diff_score * W_DIFF / 100 ))
    WEIGHTED_SCORES+=("$total")
    log "Run $i: exit=$exit_s test=$test_s diff=$diff_s → weighted=$total"
done

# ── 9. Select best ──────────────────────────────────────────────
best_idx=1
best_score="${WEIGHTED_SCORES[0]}"

for i in $(seq 2 "$N"); do
    score="${WEIGHTED_SCORES[$((i-1))]}"
    if (( score > best_score )); then
        best_score=$score
        best_idx=$i
    fi
done

# Check if all failed
all_failed=1
for ec in "${EXIT_CODES[@]}"; do
    if [[ "$ec" == "0" ]]; then
        all_failed=0
        break
    fi
done

if [[ "$MODE" == "interactive" ]]; then
    echo ""
    echo "┌─────────────────────────────────────────────┐"
    echo "│         Best-of-N Results (N=$N)              │"
    echo "├─────┬──────┬──────┬──────┬─────────┬────────┤"
    echo "│ Run │ Exit │ Test │ Diff │ Score   │ Status │"
    echo "├─────┼──────┼──────┼──────┼─────────┼────────┤"
    for i in $(seq 1 "$N"); do
        IFS=: read -r e t d <<< "${SCORES[$((i-1))]}"
        ws="${WEIGHTED_SCORES[$((i-1))]}"
        status=""
        if (( i == best_idx )); then status="* BEST"; fi
        printf "│ %3d │ %4s │ %4s │ %4s │ %5s/100│ %-6s │\n" \
            "$i" "$e" "$t" "${d:-0}" "$ws" "$status"
    done
    echo "└─────┴──────┴──────┴──────┴─────────┴────────┘"
    echo ""

    if (( all_failed == 0 )); then
        read -r -p "Select run to keep [${best_idx}]: " choice
        if [[ -n "$choice" && "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= N )); then
            best_idx=$choice
        fi
    fi
fi

BEST_WORKTREE="${WORKTREE_DIRS[$((best_idx-1))]}"
log "Selected run $best_idx (score: $best_score, worktree: $BEST_WORKTREE)"

# ── 10. Report & notify ─────────────────────────────────────────
if (( all_failed )); then
    log "WARNING: All $N runs failed. Keeping all worktrees for inspection."
    KEEP_ALL=1
    if command -v cmux-notify.sh &>/dev/null; then
        cmux-notify.sh "Best-of-N Failed" "All $N runs failed — check logs" hero || true
    fi
    echo "All $N runs failed. Worktrees preserved for inspection." >&2
    echo "Logs: $RESULTS_DIR" >&2
    exit 1
else
    if command -v cmux-notify.sh &>/dev/null; then
        cmux-notify.sh "Best-of-N Complete" "Run $best_idx selected (score: $best_score/100)" hero || true
    fi
    echo "Best run: $best_idx (score: $best_score/100)"
    echo "Worktree: $BEST_WORKTREE"
    echo "Logs: $RESULTS_DIR"
fi
