#!/bin/bash
# patrol-agent.sh — Periodic patrol of Claude headless sessions
# Detects stalled headless sessions (claude -p) and sends notifications.
#
# Triggered by: launchd (com.claude.patrol-agent.plist) every 5 minutes
#
# Install:
#   cp scripts/runtime/com.claude.patrol-agent.plist ~/Library/LaunchAgents/
#   launchctl load ~/Library/LaunchAgents/com.claude.patrol-agent.plist
#
# Usage:
#   patrol-agent.sh              # Normal patrol
#   patrol-agent.sh --dry-run    # Detect without notifying
#   patrol-agent.sh --verbose    # Print to stdout + log

set -euo pipefail

# --- Constants ---
STALL_THRESHOLD_MINUTES="${PATROL_STALL_THRESHOLD:-60}"
HEARTBEAT_FILE="${HOME}/.claude/patrol-heartbeat"
LOG_DIR="${HOME}/.claude/logs"
LOG_FILE="${LOG_DIR}/patrol-agent.log"
MAX_LOG_LINES=1000
NOTIFY_SCRIPT="${HOME}/.claude/scripts/runtime/cmux-notify.sh"

# --- CLI flags ---
DRY_RUN=0
VERBOSE=0
for arg in "$@"; do
    case "$arg" in
        --dry-run)  DRY_RUN=1 ;;
        --verbose)  VERBOSE=1 ;;
    esac
done

# --- Counters ---
NOTIFICATION_FAILURES=0
SESSIONS_CHECKED=0
STALLED_DETECTED=0

# --- Logging ---
log() {
    local msg="[$(date -Iseconds)] $*"
    echo "$msg" >> "$LOG_FILE"
    if (( VERBOSE )); then
        echo "$msg"
    fi
}

rotate_log() {
    if [[ -f "$LOG_FILE" ]] && (( $(wc -l < "$LOG_FILE") > MAX_LOG_LINES )); then
        tail -n "$MAX_LOG_LINES" "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
}

# --- etime parser ---
# Parses ps etime format: [[DD-]HH:]MM:SS → minutes
etime_to_minutes() {
    local etime="$1"
    local days=0 hours=0 mins=0

    if [[ "$etime" == *-* ]]; then
        days="${etime%%-*}"
        etime="${etime#*-}"
    fi

    # Split by ':' — formats: SS, MM:SS, HH:MM:SS
    IFS=: read -ra parts <<< "$etime"
    local n=${#parts[@]}
    local secs=0
    if (( n == 3 )); then
        hours="${parts[0]}"
        mins="${parts[1]}"
        secs="${parts[2]}"
    elif (( n == 2 )); then
        mins="${parts[0]}"
        secs="${parts[1]}"
    elif (( n == 1 )); then
        secs="${parts[0]}"
    fi

    echo $(( days * 1440 + hours * 60 + mins + secs / 60 ))
}

# --- Notification (cascade, no || true) ---
notify() {
    local title="$1" body="$2" sound="${3:-glass}"

    if (( DRY_RUN )); then
        log "DRY-RUN: would notify [$title] $body"
        return 0
    fi

    # Attempt 1: cmux-notify.sh
    if [[ -x "$NOTIFY_SCRIPT" ]]; then
        if "$NOTIFY_SCRIPT" "$title" "$body" "$sound"; then
            log "Notified via cmux-notify.sh"
            return 0
        else
            log "WARN: cmux-notify.sh failed (exit: $?)"
        fi
    fi

    # Attempt 2: osascript fallback (sanitize for AppleScript)
    local safe_body safe_title
    safe_body=$(printf '%s' "$body" | sed 's/[\"\\]/\\&/g')
    safe_title=$(printf '%s' "$title" | sed 's/[\"\\]/\\&/g')
    if osascript -e "display notification \"$safe_body\" with title \"$safe_title\"" 2>>"$LOG_FILE"; then
        log "Notified via osascript fallback"
        return 0
    fi
    log "WARN: osascript notification failed"

    # Attempt 3: log-only (last resort)
    log "ERROR: All notification methods failed. Message: [$title] $body"
    NOTIFICATION_FAILURES=$((NOTIFICATION_FAILURES + 1))
    return 1
}

# --- Session detection ---
detect_stalled_sessions() {
    local stalled=()

    # Get claude PIDs (may be empty)
    local pids
    pids=$(pgrep -f "claude" 2>/dev/null || true)
    if [[ -z "$pids" ]]; then
        return
    fi

    while IFS= read -r pid; do
        [[ -z "$pid" ]] && continue

        # Get process info
        local info
        info=$(ps -o etime=,pcpu=,args= -p "$pid" 2>/dev/null) || continue
        [[ -z "$info" ]] && continue

        local etime pcpu args
        etime=$(echo "$info" | awk '{print $1}')
        pcpu=$(echo "$info" | awk '{print $2}')
        args=$(echo "$info" | awk '{$1=$2=""; print $0}' | sed 's/^ *//')

        # Skip non-headless sessions (no -p flag)
        if ! echo "$args" | grep -qE '(^| )-p( |$)'; then
            continue
        fi

        # Skip patrol-agent itself and other short-lived processes
        if echo "$args" | grep -q 'patrol-agent'; then
            continue
        fi

        SESSIONS_CHECKED=$((SESSIONS_CHECKED + 1))

        # Parse elapsed time
        local minutes
        minutes=$(etime_to_minutes "$etime")

        # Stall condition: running > threshold AND near-zero CPU
        if (( minutes > STALL_THRESHOLD_MINUTES )); then
            if awk "BEGIN {exit !($pcpu < 0.5)}"; then
                stalled+=("PID=${pid} running=${minutes}m cpu=${pcpu}%")
                log "Stalled: PID=${pid} etime=${etime} cpu=${pcpu}% cmd=${args:0:80}"
            fi
        fi
    done <<< "$pids"

    STALLED_DETECTED=${#stalled[@]}
    if (( STALLED_DETECTED > 0 )); then
        printf '%s\n' "${stalled[@]}"
    fi
}

# --- Heartbeat ---
update_heartbeat() {
    local now
    now=$(date -Iseconds)

    # Read existing run_count
    local prev_count=0
    local prev_consecutive_failures=0
    if [[ -f "$HEARTBEAT_FILE" ]]; then
        if command -v jq &>/dev/null; then
            prev_count=$(jq -r '.run_count // 0' "$HEARTBEAT_FILE" 2>/dev/null || echo 0)
            prev_consecutive_failures=$(jq -r '.consecutive_failures // 0' "$HEARTBEAT_FILE" 2>/dev/null || echo 0)
        else
            log "WARN: jq not found, heartbeat counters will not accumulate"
        fi
    fi

    local new_count=$((prev_count + 1))
    local consecutive_failures
    if (( NOTIFICATION_FAILURES > 0 )); then
        consecutive_failures=$((prev_consecutive_failures + 1))
    else
        consecutive_failures=0
    fi

    local last_success="$now"
    if (( NOTIFICATION_FAILURES > 0 && STALLED_DETECTED > 0 )); then
        # Notification failed for stalled session — don't update last_success
        if [[ -f "$HEARTBEAT_FILE" ]] && command -v jq &>/dev/null; then
            last_success=$(jq -r '.last_success // ""' "$HEARTBEAT_FILE" 2>/dev/null || echo "$now")
        fi
    fi

    local tmp="${HEARTBEAT_FILE}.tmp"
    cat > "$tmp" <<EOF
{
  "last_run": "${now}",
  "last_success": "${last_success}",
  "run_count": ${new_count},
  "consecutive_failures": ${consecutive_failures},
  "sessions_checked": ${SESSIONS_CHECKED},
  "stalled_detected": ${STALLED_DETECTED},
  "notification_failures": ${NOTIFICATION_FAILURES},
  "version": 1
}
EOF
    mv "$tmp" "$HEARTBEAT_FILE"
}

# --- Main ---
main() {
    mkdir -p "$LOG_DIR"
    rotate_log
    log "Patrol started (threshold=${STALL_THRESHOLD_MINUTES}m dry_run=${DRY_RUN})"

    # Detect stalled sessions
    local stalled_list
    stalled_list=$(detect_stalled_sessions)

    if [[ -n "$stalled_list" ]]; then
        log "Stalled sessions: ${STALLED_DETECTED}"
        local body
        body=$(printf "Stalled: %d session(s)\n%s" "$STALLED_DETECTED" "$stalled_list")
        if ! notify "Patrol: Stalled Session" "$body" glass; then
            log "WARN: stalled session notification failed, continuing"
        fi
    fi

    # Update heartbeat (always, even if no stalls found)
    update_heartbeat
    log "Patrol complete: checked=${SESSIONS_CHECKED} stalled=${STALLED_DETECTED} notify_failures=${NOTIFICATION_FAILURES}"
}

main "$@"
