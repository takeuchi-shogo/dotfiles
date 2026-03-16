#!/bin/bash
set -euo pipefail

echo "=== SafeClaw Container ==="
echo "Node.js: $(node --version)"
echo "npm:     $(npm --version)"
echo "Claude:  $(claude --version 2>/dev/null || echo 'not available')"
echo "gh:      $(gh --version 2>/dev/null | head -1)"
echo "=========================="

# If arguments are passed, execute them directly (for docker exec use)
if [ $# -gt 0 ]; then
    exec "$@"
fi

# Default: start tmux with claude --dangerously-skip-permissions
exec tmux new-session -s claude "claude --dangerously-skip-permissions"
