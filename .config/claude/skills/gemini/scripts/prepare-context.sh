#!/bin/sh
# Prepare codebase snapshot for Gemini 1M context
# Usage: prepare-context.sh [dir] [output]
set -e
DIR="${1:-.}"
OUT="${2:-/tmp/gemini-context.txt}"

echo "# Codebase Snapshot: $(basename "$(cd "$DIR" && pwd)")" > "$OUT"
echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUT"
echo "" >> "$OUT"

find "$DIR" -type f \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  -not -path '*/vendor/*' \
  -not -path '*/__pycache__/*' \
  -not -name '*.min.*' \
  -not -name '*.map' \
  -not -name '*.lock' \
  \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.py' -o -name '*.go' \
     -o -name '*.rs' -o -name '*.md' -o -name '*.yaml' -o -name '*.yml' \
     -o -name '*.json' -o -name '*.toml' -o -name '*.sh' \) \
  | sort | while read -r f; do
    echo "--- $f ---" >> "$OUT"
    cat "$f" >> "$OUT"
    echo "" >> "$OUT"
done

SIZE=$(wc -c < "$OUT" | tr -d ' ')
echo "Context prepared: $OUT ($SIZE bytes)"
