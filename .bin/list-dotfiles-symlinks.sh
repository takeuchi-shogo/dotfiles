#!/usr/bin/env bash
# list-dotfiles-symlinks.sh — dry-run dump of symlinks symlink.sh would create.
#
# Phase B2.0 deliverable. Used to produce a deterministic baseline for diffing
# home-manager migration output (B2.1-B2.3) against the pre-migration state.
#
# Output format: one line per symlink, "<link_path>\t<target_path>",
#                sorted lexicographically.
#
# Usage:
#   ./.bin/list-dotfiles-symlinks.sh > /tmp/symlinks-baseline.txt
#   diff <(./.bin/list-dotfiles-symlinks.sh) <(actual-state-dump.sh)
#
# Mirrors `.bin/symlink.sh` logic without performing any filesystem mutation.
set -euo pipefail

DOTFILES_DIR="${DOTFILES_DIR:-$HOME/dotfiles}"

if [[ ! -d "$DOTFILES_DIR" ]]; then
  echo "Error: $DOTFILES_DIR not found." >&2
  exit 1
fi

cd "$DOTFILES_DIR"

# --- mirrors SYMLINK_EXCLUDE_FILES from .bin/symlink.sh -----------------------
EXCLUDE=(
  "^README\.md$"
  "^PLANS\.md$"
  "^Taskfile\.yml$"
  "^\.mcp\.json$"
  "^\.claudeignore$"
  "^\.agent/"
  "^\.kiro/"
  "^\.playwright-mcp/"
  "^\.pytest_cache/"
  "^\.research/"
  "^\.ruff_cache/"
  "^\.skill-eval/"
  "^\.venv/"
  "^breakthroughs/"
  "^skills-lock\.json$"
  "^vm/"
  "^images/"
  "^docs/"
  "^bin/"
  "^tests/"
  "^tmp/"
  "\.zsh_history$"
  "git-templates"
  "\.zcompdump.*"
  "^\.config/jgit/config$"
  "^\.config/raycast/extensions/"
  "^\.serena/"
  "^sample-dotfiles/"
  "^\.hammerspoon/"
  "^\.config/zsh/"
  "^\.config/claude/"
  "^\.claude/"
  "^\.context/"
  "^\.agents/"
  "^\.codex/"
  "^\.gemini/"
  "^\.cursor/"
)

is_excluded() {
  local f="$1" p
  for p in "${EXCLUDE[@]}"; do
    [[ "$f" =~ $p ]] && return 0
  done
  return 1
}

emit() {
  local link="$1" target="$2"
  printf '%s\t%s\n' "$link" "$target"
}

# --- block 1: DIRECTORY_SYMLINKS -----------------------------------------------
DIRECTORY_SYMLINKS=(
  ".hammerspoon"
  ".config/zsh"
)
for d in "${DIRECTORY_SYMLINKS[@]}"; do
  emit "$HOME/$d" "$DOTFILES_DIR/$d"
done

# --- block 2: Claude (.config/claude → ~/.claude) ------------------------------
CLAUDE_FILES=(CLAUDE.md settings.json settings.local.json statusline.sh)
CLAUDE_DIRS=(agents channels commands scripts skills)
for f in "${CLAUDE_FILES[@]}"; do
  [[ -f "$DOTFILES_DIR/.config/claude/$f" ]] && emit "$HOME/.claude/$f" "$DOTFILES_DIR/.config/claude/$f"
done
for d in "${CLAUDE_DIRS[@]}"; do
  [[ -d "$DOTFILES_DIR/.config/claude/$d" ]] && emit "$HOME/.claude/$d" "$DOTFILES_DIR/.config/claude/$d"
done

# --- block 3: Codex (.codex → ~/.codex) ----------------------------------------
CODEX_FILES=(config.toml AGENTS.md)
for f in "${CODEX_FILES[@]}"; do
  [[ -f "$DOTFILES_DIR/.codex/$f" ]] && emit "$HOME/.codex/$f" "$DOTFILES_DIR/.codex/$f"
done

# --- block 4: Gemini (.gemini → ~/.gemini) -------------------------------------
GEMINI_FILES=(GEMINI.md)
for f in "${GEMINI_FILES[@]}"; do
  [[ -f "$DOTFILES_DIR/.gemini/$f" ]] && emit "$HOME/.gemini/$f" "$DOTFILES_DIR/.gemini/$f"
done

# --- block 5: Cursor (.cursor → ~/.cursor) -------------------------------------
CURSOR_FILES=(hooks.json)
CURSOR_DIRS=(rules skills agents commands hooks)
for f in "${CURSOR_FILES[@]}"; do
  [[ -f "$DOTFILES_DIR/.cursor/$f" ]] && emit "$HOME/.cursor/$f" "$DOTFILES_DIR/.cursor/$f"
done
for d in "${CURSOR_DIRS[@]}"; do
  [[ -d "$DOTFILES_DIR/.cursor/$d" ]] && emit "$HOME/.cursor/$d" "$DOTFILES_DIR/.cursor/$d"
done

# --- block 6: skill-sharing (Python helper) ------------------------------------
SKILL_HELPER="$DOTFILES_DIR/scripts/lib/skill_platforms.py"
if [[ -f "$SKILL_HELPER" ]] && command -v python3 >/dev/null 2>&1; then
  while IFS= read -r skill; do
    [[ -z "$skill" ]] && continue
    target="$DOTFILES_DIR/.config/claude/skills/$skill"
    [[ -d "$target" ]] || continue
    emit "$HOME/.codex/skills/$skill"  "$target"
    emit "$HOME/.agents/skills/$skill" "$target"
  done < <(python3 "$SKILL_HELPER" --source claude --needs codex 2>/dev/null || true)

  while IFS= read -r skill; do
    [[ -z "$skill" ]] && continue
    target="$DOTFILES_DIR/.agents/skills/$skill"
    [[ -d "$target" ]] || continue
    emit "$HOME/.codex/skills/$skill"  "$target"
    emit "$HOME/.agents/skills/$skill" "$target"
  done < <(python3 "$SKILL_HELPER" --source agents --needs codex 2>/dev/null || true)
fi

# --- block 7: find-walk with 37-pattern exclude --------------------------------
while IFS= read -r f; do
  is_excluded "$f" && continue
  emit "$HOME/$f" "$DOTFILES_DIR/$f"
done < <(/usr/bin/find . \( -type f -o -type l \) ! -path '*.git/*' ! -name '.DS_Store' | /usr/bin/sed 's|^\./||')
