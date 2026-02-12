#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | python3 "$SCRIPT_DIR/scripts/context-monitor.py" 2>/dev/null || echo "[Claude] 📁 ${PWD##*/}"
