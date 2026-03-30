#!/usr/bin/env bash
# CLAUDE.md をテンプレートコンポーネントから結合生成する
# Usage: bash build-claude.sh [--check]
#   --check: 差分確認のみ（書き込みしない）
set -euo pipefail

TEMPLATE_DIR="${HOME}/dotfiles/.config/claude/templates/claude-md"
OUTPUT="${HOME}/dotfiles/.config/claude/CLAUDE.md"
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

# コンポーネント存在確認
components=(header.md rules.md workflow.md principles.md dotfiles.md)
for c in "${components[@]}"; do
  if [[ ! -f "${TEMPLATE_DIR}/${c}" ]]; then
    echo "ERROR: ${TEMPLATE_DIR}/${c} not found" >&2
    exit 1
  fi
done

# 結合（セクション間に --- セパレータ）
{
  cat "${TEMPLATE_DIR}/header.md"
  echo ""
  cat "${TEMPLATE_DIR}/rules.md"
  echo ""
  echo "---"
  echo ""
  cat "${TEMPLATE_DIR}/workflow.md"
  echo ""
  echo "---"
  echo ""
  cat "${TEMPLATE_DIR}/principles.md"
  echo ""
  echo "---"
  echo ""
  cat "${TEMPLATE_DIR}/dotfiles.md"
} > "$TMPFILE"

# 差分チェック
if diff -q "$OUTPUT" "$TMPFILE" > /dev/null 2>&1; then
  echo "CLAUDE.md is up to date (no changes)"
  exit 0
fi

# --check モード
if [[ "${1:-}" == "--check" ]]; then
  echo "CLAUDE.md has differences:"
  diff --unified "$OUTPUT" "$TMPFILE" || true
  exit 1
fi

# バックアップして上書き
cp "$OUTPUT" "${OUTPUT}.bak"
cp "$TMPFILE" "$OUTPUT"
echo "CLAUDE.md rebuilt from templates (backup: CLAUDE.md.bak)"
