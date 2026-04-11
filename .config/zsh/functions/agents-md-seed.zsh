# agents-md-seed: ghq get 後に CLAUDE.md を自動 seed
# Source: nyosegawa/agents-md-generator の知見を dotfiles 向けに適応

# --- Helper ---
_agents_md_seed() {
  local target_dir="$1"

  # Skip: empty repo (< 3 items excluding .git)
  local item_count
  item_count=$(find "$target_dir" -maxdepth 1 -not -name '.git' -not -name '.' 2>/dev/null | wc -l | tr -d ' ')
  [[ "$item_count" -lt 3 ]] && return 0

  # Skip: CLAUDE.md or AGENTS.md already exists
  [[ -f "$target_dir/CLAUDE.md" || -f "$target_dir/AGENTS.md" ]] && return 0

  cat > "$target_dir/CLAUDE.md" << 'TEMPLATE'
<!-- Do not restructure or delete sections. Update individual values in-place when they change. -->
# Project Guide

## Build & Test
[TBD: Add build/test commands after exploring the project]

## Working Rules
- [TBD: Add project-specific conventions]

## Key Paths
- [TBD: Add important file paths and entry points]
TEMPLATE

  echo "\033[32m✅ Seeded CLAUDE.md in ${target_dir}\033[0m (run /init-project for full setup)"
}

# --- ghq wrapper ---
ghq() {
  local subcmd="$1"
  command ghq "$@"
  local ret=$?

  if [[ $ret -eq 0 && "$subcmd" == "get" ]]; then
    local repo_id=""
    for arg in "${@:2}"; do
      [[ "$arg" != -* ]] && repo_id="$arg" && break
    done
    if [[ -n "$repo_id" ]]; then
      local repo_name="${repo_id##*/}"
      repo_name="${repo_name%.git}"
      local repo_path
      repo_path=$(command ghq list -p | grep "/${repo_name}\$" | head -1)
      [[ -d "$repo_path" ]] && _agents_md_seed "$repo_path"
    fi
  fi

  return $ret
}
