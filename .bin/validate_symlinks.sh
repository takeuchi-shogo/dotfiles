#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 - <<'PY'
import pathlib
import sys

root = pathlib.Path.cwd()
home = pathlib.Path.home()

sys.path.insert(0, str(root / "scripts"))
from lib import skill_platforms  # noqa: E402

# Static (non-skill) symlinks managed by .bin/symlink.sh.
managed_links = [
    (home / ".hammerspoon", root / ".hammerspoon", ".hammerspoon"),
    (home / ".config/aerospace/aerospace.toml", root / ".config/aerospace/aerospace.toml", ".config/aerospace/aerospace.toml"),
    (home / ".config/rtk/config.toml", root / ".config/rtk/config.toml", ".config/rtk/config.toml"),
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
]

# Skill symlinks derived from SKILL.md frontmatter `platforms:` declarations.
# This is the same source of truth used by .bin/symlink.sh.
for skill in skill_platforms.list_skills_needing("claude", "codex"):
    target = root / ".config/claude/skills" / skill
    managed_links.append((home / ".codex/skills" / skill, target, f".codex/skills/{skill}"))
    managed_links.append((home / ".agents/skills" / skill, target, f".agents/skills/{skill}"))

for skill in skill_platforms.list_skills_needing("agents", "codex"):
    target = root / ".agents/skills" / skill
    managed_links.append((home / ".codex/skills" / skill, target, f".codex/skills/{skill}"))
    managed_links.append((home / ".agents/skills" / skill, target, f".agents/skills/{skill}"))

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
