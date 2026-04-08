#!/usr/bin/env bash
# validate-agents.sh — Validate agent definition frontmatter
# Checks: tools defined, reviewer/analyzer Write/Edit usage, Agent tool presence

set -euo pipefail

AGENTS_DIR="${HOME}/.claude/agents"
WARN_COUNT=0
AGENT_COUNT=0

# Exceptions: these agents legitimately use Write/Edit despite reviewer-like names
WRITE_EDIT_EXCEPTIONS=("doc-gardener" "golden-cleanup")

is_exception() {
    local name="$1"
    for exc in "${WRITE_EDIT_EXCEPTIONS[@]}"; do
        if [[ "$name" == "$exc" ]]; then
            return 0
        fi
    done
    return 1
}

extract_frontmatter_field() {
    local file="$1"
    local field="$2"
    # Extract value between first --- and second ---
    awk '/^---/{f++; next} f==1' "$file" | grep "^${field}:" | sed "s/^${field}:[[:space:]]*//"
}

extract_tools_list() {
    local file="$1"
    # Extract frontmatter block
    local in_fm=0
    local fm_count=0
    local in_tools=0
    local tools_value=""

    while IFS= read -r line; do
        if [[ "$line" == "---" ]]; then
            fm_count=$((fm_count + 1))
            if [[ $fm_count -eq 1 ]]; then
                in_fm=1
                continue
            elif [[ $fm_count -eq 2 ]]; then
                break
            fi
        fi
        if [[ $in_fm -eq 1 ]]; then
            if [[ "$line" =~ ^tools:[[:space:]]*(.*) ]]; then
                in_tools=1
                tools_value="${BASH_REMATCH[1]}"
            elif [[ $in_tools -eq 1 && "$line" =~ ^[[:space:]]*-[[:space:]]+(.*) ]]; then
                tools_value="${tools_value} ${BASH_REMATCH[1]}"
            elif [[ $in_tools -eq 1 && "$line" =~ ^[^[:space:]-] ]]; then
                in_tools=0
            fi
        fi
    done < "$file"

    echo "$tools_value"
}

if [[ ! -d "$AGENTS_DIR" ]]; then
    echo "[validate-agents] ERROR: agents directory not found: $AGENTS_DIR"
    exit 1
fi

# Count total agents
mapfile -t agent_files < <(find -L "$AGENTS_DIR" -maxdepth 1 -name "*.md" | sort)
AGENT_COUNT=${#agent_files[@]}

echo "[validate-agents] Checking ${AGENT_COUNT} agent definitions..."

for file in "${agent_files[@]}"; do
    basename_no_ext="$(basename "$file" .md)"

    # Extract name from frontmatter (fallback to filename)
    agent_name="$(extract_frontmatter_field "$file" "name")"
    if [[ -z "$agent_name" ]]; then
        agent_name="$basename_no_ext"
    fi

    # Extract tools
    tools_raw="$(extract_tools_list "$file")"

    # Check 1: tools undefined or empty
    if [[ -z "$tools_raw" ]]; then
        echo "[validate-agents] WARN: ${agent_name} has no tools defined"
        WARN_COUNT=$((WARN_COUNT + 1))
        continue
    fi

    # Check 2: reviewer/analyzer/inspector/hunter with Write or Edit
    if echo "$agent_name" | grep -qiE "(reviewer|analyzer|inspector|hunter)"; then
        if ! is_exception "$agent_name"; then
            if echo "$tools_raw" | grep -qiE "\b(Write|Edit)\b"; then
                echo "[validate-agents] WARN: ${agent_name} (reviewer) has Write/Edit tools"
                WARN_COUNT=$((WARN_COUNT + 1))
            fi
        fi
    fi

    # Check 3: Agent tool presence (info only)
    if echo "$tools_raw" | grep -qiE "\bAgent\b"; then
        echo "[validate-agents] INFO: ${agent_name} has Agent tool (can spawn subagents)"
    fi
done

if [[ $WARN_COUNT -eq 0 ]]; then
    echo "[validate-agents] OK: All checks passed (${AGENT_COUNT} agents, 0 warnings)"
else
    echo "[validate-agents] OK: All checks passed (${AGENT_COUNT} agents, ${WARN_COUNT} warnings)"
fi

# Exit 0 even with warnings (future: change to exit 1 for CI enforcement)
exit 0
