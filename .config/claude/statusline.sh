#!/bin/bash
# SCRIPT_DIR を symlink 解決して dotfiles 実体パスを取得
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

# context monitor output
CONTEXT=$(cat | python3 "$SCRIPT_DIR/scripts/context-monitor.py" 2>/dev/null || echo "")

# harness stats (find -L for symlink traversal)
REF_COUNT=$(find -L "$SCRIPT_DIR/references" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
MEM_COUNT=$(find -L "$CLAUDE_DIR/projects" -path '*/memory/*.md' ! -name 'MEMORY.md' 2>/dev/null | wc -l | tr -d ' ')
SKILL_COUNT=$(find -L "$CLAUDE_DIR/skills" -maxdepth 2 -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')

STATS="📚${REF_COUNT} 🧠${MEM_COUNT} ⚡${SKILL_COUNT}"

if [ -n "$CONTEXT" ]; then
  echo "${CONTEXT} | ${STATS}"
else
  echo "📁 ${PWD##*/} | ${STATS}"
fi
