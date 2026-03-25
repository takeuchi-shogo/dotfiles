#!/usr/bin/env bash
# CLAUDE.md line count guard (lefthook pre-commit)
# Warning only — does NOT block commit
set -euo pipefail

LIMIT=150
CLAUDEMD=".config/claude/CLAUDE.md"

# Only check if CLAUDE.md is in staged files
if ! git diff --cached --name-only | grep -q "^${CLAUDEMD}$"; then
  exit 0
fi

LINES=$(wc -l < "$CLAUDEMD" | tr -d ' ')
if [ "$LINES" -gt "$LIMIT" ]; then
  echo "⚠️  [check-claudemd-lines] CLAUDE.md is ${LINES} lines (limit: ${LIMIT})"
  echo "   Progressive Disclosure に従い、詳細は references/ に分離してください"
fi
exit 0
