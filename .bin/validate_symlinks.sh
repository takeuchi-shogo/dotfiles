#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 - <<'PY'
import pathlib
import sys

root = pathlib.Path.cwd()
home = pathlib.Path.home()

managed_links = [
    (home / ".config/aerospace/aerospace.toml", root / ".config/aerospace/aerospace.toml", ".config/aerospace/aerospace.toml"),
    (home / ".config/karabiner/karabiner.json", root / ".config/karabiner/karabiner.json", ".config/karabiner/karabiner.json"),
    (home / ".config/nvim", root / ".config/nvim", ".config/nvim"),
    (home / ".config/sheldon/plugins.toml", root / ".config/sheldon/plugins.toml", ".config/sheldon/plugins.toml"),
    (home / ".config/sketchybar/init.lua", root / ".config/sketchybar/init.lua", ".config/sketchybar/init.lua"),
    (home / ".config/starship.toml", root / ".config/starship.toml", ".config/starship.toml"),
    (home / ".config/wezterm/wezterm.lua", root / ".config/wezterm/wezterm.lua", ".config/wezterm/wezterm.lua"),
    (home / ".config/zsh", root / ".config/zsh", ".config/zsh"),
    (home / ".claude/CLAUDE.md", root / ".config/claude/CLAUDE.md", ".claude/CLAUDE.md"),
    (home / ".claude/settings.json", root / ".config/claude/settings.json", ".claude/settings.json"),
    (home / ".claude/settings.local.json", root / ".config/claude/settings.local.json", ".claude/settings.local.json"),
    (home / ".claude/statusline.sh", root / ".config/claude/statusline.sh", ".claude/statusline.sh"),
    (home / ".claude/agents", root / ".config/claude/agents", ".claude/agents"),
    (home / ".claude/commands", root / ".config/claude/commands", ".claude/commands"),
    (home / ".claude/scripts", root / ".config/claude/scripts", ".claude/scripts"),
    (home / ".claude/skills", root / ".config/claude/skills", ".claude/skills"),
    (home / ".codex/AGENTS.md", root / ".codex/AGENTS.md", ".codex/AGENTS.md"),
    (home / ".codex/config.toml", root / ".codex/config.toml", ".codex/config.toml"),
    (home / ".codex/skills/frontend-design", root / ".config/claude/skills/frontend-design", ".codex/skills/frontend-design"),
    (home / ".codex/skills/react-best-practices", root / ".config/claude/skills/react-best-practices", ".codex/skills/react-best-practices"),
    (home / ".codex/skills/senior-architect", root / ".config/claude/skills/senior-architect", ".codex/skills/senior-architect"),
    (home / ".codex/skills/senior-backend", root / ".config/claude/skills/senior-backend", ".codex/skills/senior-backend"),
    (home / ".codex/skills/senior-frontend", root / ".config/claude/skills/senior-frontend", ".codex/skills/senior-frontend"),
    (home / ".codex/skills/codex-search-first", root / ".agents/skills/codex-search-first", ".codex/skills/codex-search-first"),
    (home / ".codex/skills/codex-verification-before-completion", root / ".agents/skills/codex-verification-before-completion", ".codex/skills/codex-verification-before-completion"),
    (home / ".codex/skills/dotfiles-config-validation", root / ".agents/skills/dotfiles-config-validation", ".codex/skills/dotfiles-config-validation"),
    (home / ".codex/skills/codex-checkpoint-resume", root / ".agents/skills/codex-checkpoint-resume", ".codex/skills/codex-checkpoint-resume"),
    (home / ".codex/skills/codex-memory-capture", root / ".agents/skills/codex-memory-capture", ".codex/skills/codex-memory-capture"),
    (home / ".codex/skills/codex-session-hygiene", root / ".agents/skills/codex-session-hygiene", ".codex/skills/codex-session-hygiene"),
    (home / ".agents/skills/frontend-design", root / ".config/claude/skills/frontend-design", ".agents/skills/frontend-design"),
    (home / ".agents/skills/react-best-practices", root / ".config/claude/skills/react-best-practices", ".agents/skills/react-best-practices"),
    (home / ".agents/skills/senior-architect", root / ".config/claude/skills/senior-architect", ".agents/skills/senior-architect"),
    (home / ".agents/skills/senior-backend", root / ".config/claude/skills/senior-backend", ".agents/skills/senior-backend"),
    (home / ".agents/skills/senior-frontend", root / ".config/claude/skills/senior-frontend", ".agents/skills/senior-frontend"),
    (home / ".agents/skills/codex-search-first", root / ".agents/skills/codex-search-first", ".agents/skills/codex-search-first"),
    (home / ".agents/skills/codex-verification-before-completion", root / ".agents/skills/codex-verification-before-completion", ".agents/skills/codex-verification-before-completion"),
    (home / ".agents/skills/dotfiles-config-validation", root / ".agents/skills/dotfiles-config-validation", ".agents/skills/dotfiles-config-validation"),
    (home / ".agents/skills/codex-checkpoint-resume", root / ".agents/skills/codex-checkpoint-resume", ".agents/skills/codex-checkpoint-resume"),
    (home / ".agents/skills/codex-memory-capture", root / ".agents/skills/codex-memory-capture", ".agents/skills/codex-memory-capture"),
    (home / ".agents/skills/codex-session-hygiene", root / ".agents/skills/codex-session-hygiene", ".agents/skills/codex-session-hygiene"),
]

errors = []

for link_path, target_path, label in managed_links:
    if not target_path.exists():
        errors.append(f"missing target  {label}: {target_path}")
        continue
    if not link_path.is_symlink():
        errors.append(f"missing symlink  {label}: {link_path}")
        continue
    if link_path.resolve() != target_path.resolve():
        errors.append(f"wrong target  {label}: {link_path} -> {link_path.resolve()} (expected {target_path})")

if errors:
    for error in errors:
        print(error)
    sys.exit(1)

for _, _, label in managed_links:
    print(f"ok  {label}")
PY
