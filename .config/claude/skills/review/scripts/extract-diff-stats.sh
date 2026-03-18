#!/bin/sh
# Extract structured diff statistics for review scaling decisions
# Usage: extract-diff-stats.sh [ref]
# Output: JSON with line counts, file counts, and language breakdown

set -e

REF="${1:-HEAD}"

# Total insertions/deletions
STAT=$(git diff --shortstat "$REF" 2>/dev/null || echo "0 files changed")
FILES=$(echo "$STAT" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo 0)
INSERTIONS=$(echo "$STAT" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)
DELETIONS=$(echo "$STAT" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)
TOTAL=$((INSERTIONS + DELETIONS))

# Language breakdown
LANGS=$(git diff --name-only "$REF" 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -5)
LANG_JSON=$(echo "$LANGS" | awk '{printf "{\"ext\":\".%s\",\"files\":%d},", $2, $1}' | sed 's/,$//')

cat <<ENDJSON
{
  "ref": "$REF",
  "files_changed": $FILES,
  "insertions": $INSERTIONS,
  "deletions": $DELETIONS,
  "total_lines": $TOTAL,
  "languages": [$LANG_JSON],
  "scale": "$(
    if [ "$TOTAL" -le 10 ]; then echo "skip"
    elif [ "$TOTAL" -le 30 ]; then echo "basic"
    elif [ "$TOTAL" -le 50 ]; then echo "standard"
    elif [ "$TOTAL" -le 200 ]; then echo "thorough"
    else echo "comprehensive"
    fi
  )"
}
ENDJSON
