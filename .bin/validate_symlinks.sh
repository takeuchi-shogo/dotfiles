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

# Static (non-skill) symlinks managed by home-manager (nix/home/default.nix `home.file`).
# Phase B2.4 (2026-04-26): symlink.sh は削除済み、home-manager が真実源。
# 順序・ブロック分けは nix/home/default.nix のコメントと一致させること。
managed_links = [
    # block 1: directory-level symlinks
    (home / ".hammerspoon", root / ".hammerspoon", ".hammerspoon"),
    (home / ".config/zsh", root / ".config/zsh", ".config/zsh"),

    # block 2: Claude (.config/claude → ~/.claude)
    (home / ".claude/CLAUDE.md", root / ".config/claude/CLAUDE.md", ".claude/CLAUDE.md"),
    (home / ".claude/settings.json", root / ".config/claude/settings.json", ".claude/settings.json"),
    (home / ".claude/settings.local.json", root / ".config/claude/settings.local.json", ".claude/settings.local.json"),
    (home / ".claude/statusline.sh", root / ".config/claude/statusline.sh", ".claude/statusline.sh"),
    (home / ".claude/agents", root / ".config/claude/agents", ".claude/agents"),
    (home / ".claude/commands", root / ".config/claude/commands", ".claude/commands"),
    (home / ".claude/scripts", root / ".config/claude/scripts", ".claude/scripts"),
    (home / ".claude/skills", root / ".config/claude/skills", ".claude/skills"),

    # block 3: Codex
    (home / ".codex/config.toml", root / ".codex/config.toml", ".codex/config.toml"),
    (home / ".codex/AGENTS.md", root / ".codex/AGENTS.md", ".codex/AGENTS.md"),

    # block 4: Gemini
    (home / ".gemini/GEMINI.md", root / ".gemini/GEMINI.md", ".gemini/GEMINI.md"),

    # block 5: Cursor
    (home / ".cursor/hooks.json", root / ".cursor/hooks.json", ".cursor/hooks.json"),
    (home / ".cursor/rules", root / ".cursor/rules", ".cursor/rules"),
    (home / ".cursor/skills", root / ".cursor/skills", ".cursor/skills"),
    (home / ".cursor/agents", root / ".cursor/agents", ".cursor/agents"),
    (home / ".cursor/commands", root / ".cursor/commands", ".cursor/commands"),
    (home / ".cursor/hooks", root / ".cursor/hooks", ".cursor/hooks"),

    # B2.3: top-level dotfiles
    (home / ".cursorignore", root / ".cursorignore", ".cursorignore"),
    (home / ".tmux.conf", root / ".tmux.conf", ".tmux.conf"),
    (home / ".worktreeinclude", root / ".worktreeinclude", ".worktreeinclude"),
    (home / ".zshrc", root / ".zshrc", ".zshrc"),

    # B2.3: root config files at ~
    (home / "AGENTS.md", root / "AGENTS.md", "AGENTS.md"),
    (home / "Brewfile", root / "Brewfile", "Brewfile"),
    (home / "lefthook.yml", root / "lefthook.yml", "lefthook.yml"),
    (home / "llms.txt", root / "llms.txt", "llms.txt"),
    (home / "ruff.toml", root / "ruff.toml", "ruff.toml"),

    # B2.3: .config/<tool> dir-level symlinks
    (home / ".config/aerospace", root / ".config/aerospace", ".config/aerospace"),
    (home / ".config/borders", root / ".config/borders", ".config/borders"),
    (home / ".config/gh", root / ".config/gh", ".config/gh"),
    (home / ".config/ghostty", root / ".config/ghostty", ".config/ghostty"),
    (home / ".config/git", root / ".config/git", ".config/git"),
    (home / ".config/karabiner", root / ".config/karabiner", ".config/karabiner"),
    (home / ".config/lazygit", root / ".config/lazygit", ".config/lazygit"),
    (home / ".config/nvim", root / ".config/nvim", ".config/nvim"),
    (home / ".config/sheldon", root / ".config/sheldon", ".config/sheldon"),
    (home / ".config/sketchybar", root / ".config/sketchybar", ".config/sketchybar"),
    (home / ".config/wezterm", root / ".config/wezterm", ".config/wezterm"),
    (home / ".config/zed", root / ".config/zed", ".config/zed"),

    # B2.3: .config single-files
    (home / ".config/starship.toml", root / ".config/starship.toml", ".config/starship.toml"),
    (home / ".config/rtk/config.toml", root / ".config/rtk/config.toml", ".config/rtk/config.toml"),
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
