#!/bin/sh
# Common Codex CLI patterns
# Usage: codex-helper.sh <command> [args]
set -e
CMD="${1:-help}"
shift 2>/dev/null || true

case "$CMD" in
  analyze)
    codex exec "$*" --reasoning-effort high
    ;;
  review)
    codex exec "Review the following code changes for quality and correctness: $*" --reasoning-effort xhigh
    ;;
  refactor)
    codex exec "Refactor: $*" -w workspace-write --reasoning-effort high
    ;;
  help|*)
    echo "Usage: codex-helper.sh <analyze|review|refactor> [prompt]"
    ;;
esac
