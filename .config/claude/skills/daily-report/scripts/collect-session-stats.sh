#!/bin/sh
# Collect session statistics for daily report generation
# Usage: collect-session-stats.sh [YYYY-MM-DD]
# Output: JSON summary of the day's development activity

set -e

DATE="${1:-$(date +%Y-%m-%d)}"

echo "{"
echo "  \"date\": \"$DATE\","

# Git commits for the day
COMMITS=$(git log --since="$DATE 00:00:00" --until="$DATE 23:59:59" --oneline 2>/dev/null | wc -l | tr -d ' ')
echo "  \"commits\": $COMMITS,"

# Files changed
FILES_CHANGED=$(git log --since="$DATE 00:00:00" --until="$DATE 23:59:59" --name-only --pretty=format: 2>/dev/null | sort -u | grep -c . || echo 0)
echo "  \"files_changed\": $FILES_CHANGED,"

# Lines added/removed
STATS=$(git log --since="$DATE 00:00:00" --until="$DATE 23:59:59" --shortstat --pretty=format: 2>/dev/null | awk '
  /insertion/ { ins += $4 }
  /deletion/  { del += $6 }
  END { printf "%d %d", ins+0, del+0 }
')
INSERTIONS=$(echo "$STATS" | cut -d' ' -f1)
DELETIONS=$(echo "$STATS" | cut -d' ' -f2)
echo "  \"insertions\": $INSERTIONS,"
echo "  \"deletions\": $DELETIONS,"

# Current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "  \"branch\": \"$BRANCH\""

echo "}"
