#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$HOME/dotfiles"

SYMLINK_EXCLUDE_FILES=(
  "^README\.md$"
  "^Taskfile\.yml$"
  "^vm/"
  "^images/"
  "^docs/"
  "^bin/"
  "\.zsh_history$"
  "git-templates"
  "\.zcompdump.*"
  "^\.config/jgit/config$"
  "^\.config/raycast/extensions/"
  "^\.serena/"
  "^sample-dotfiles/"
  "^\.config/zsh/"    # ディレクトリ全体でシンボリックリンクするため除外
  "^\.config/claude/" # ~/.claude/ へカスタムシンボリックリンクするため除外
  "^\.claude/"        # プロジェクトローカルの設定は除外
  "^\.codex/"         # ~/.codex/ へカスタムシンボリックリンクするため除外
)

# ディレクトリ全体をシンボリックリンクするリスト
ZSH_SYMLINK_DIRECTORIES=(
  ".config/zsh"
)

# Claude設定: .config/claude/ -> ~/.claude/ へのシンボリックリンク
CLAUDE_SYMLINK_FILES=(
  "CLAUDE.md"
  "settings.json"
  "settings.local.json"
  "statusline.sh"
)
CLAUDE_SYMLINK_DIRECTORIES=(
  "agents"
  "commands"
  "scripts"
  "skills"
)

# Codex設定: .codex/ -> ~/.codex/ へのシンボリックリンク
CODEX_SYMLINK_FILES=(
  "config.toml"
  "AGENTS.md"
)
CODEX_SYMLINK_DIRECTORIES=()

# Codex スキル: Claude スキルを ~/.codex/skills/ に共有
# ~/.codex/skills/.system/ を壊さないよう個別にシンボリックリンク
CODEX_SHARED_SKILLS=(
  "senior-architect"
  "senior-backend"
  "senior-frontend"
  "react-best-practices"
  "frontend-design"
)

is_excluded() {
  local file="$1"
  local pattern
  for pattern in "${SYMLINK_EXCLUDE_FILES[@]}"; do
    if [[ "$file" =~ $pattern ]]; then
      return 0
    fi
  done
  return 1
}

create_symlink() {
  local file="$1"
  local target="$DOTFILES_DIR/$file"
  local link="$HOME/$file"
  local link_dir
  link_dir="$(dirname "$link")"

  # ディレクトリを作成
  if ! mkdir -p "$link_dir"; then
    echo "Failed to create directory: $link_dir" >&2
    return 1
  fi

  # 既存ファイルのチェック（シンボリックリンクでない場合は警告）
  if [ -f "$link" ] && [ ! -L "$link" ]; then
    echo "Warning: $link exists and is not a symlink. Skipping." >&2
    return 1
  fi

  # シンボリックリンクの作成
  if [ -L "$link" ]; then
    # 既に正しいターゲットを指している場合はスキップ
    if [ "$(readlink "$link")" = "$target" ]; then
      return 0
    fi
    ln -sfv "$target" "$link"
  else
    ln -sv "$target" "$link"
  fi
}

create_directory_symlink() {
  local dir="$1"
  local target="$DOTFILES_DIR/$dir"
  local link="$HOME/$dir"
  local link_parent
  link_parent="$(dirname "$link")"

  # 親ディレクトリを作成
  mkdir -p "$link_parent"

  # 既存ディレクトリの処理
  if [ -d "$link" ] && [ ! -L "$link" ]; then
    echo "Warning: $link exists and is not a symlink. Removing..." >&2
    rm -rf "$link"
  fi

  # シンボリックリンクの作成
  if [ -L "$link" ]; then
    if [ "$(readlink "$link")" = "$target" ]; then
      return 0
    fi
    ln -sfvn "$target" "$link"
  else
    ln -sv "$target" "$link"
  fi
}

# Claude設定用のシンボリックリンク作成 (.config/claude/ -> ~/.claude/)
create_claude_symlinks() {
  local src_dir="$DOTFILES_DIR/.config/claude"
  local dest_dir="$HOME/.claude"

  # ~/.claude ディレクトリが存在しない場合は作成
  mkdir -p "$dest_dir"

  # ファイルのシンボリックリンク
  for file in "${CLAUDE_SYMLINK_FILES[@]}"; do
    local target="$src_dir/$file"
    local link="$dest_dir/$file"

    if [ ! -f "$target" ]; then
      echo "Warning: $target not found. Skipping." >&2
      continue
    fi

    if [ -f "$link" ] && [ ! -L "$link" ]; then
      echo "Backing up $link to ${link}.backup"
      mv "$link" "${link}.backup"
    fi

    if [ -L "$link" ]; then
      if [ "$(readlink "$link")" = "$target" ]; then
        continue
      fi
      ln -sfv "$target" "$link"
    else
      ln -sv "$target" "$link"
    fi
  done

  # ディレクトリのシンボリックリンク
  for dir in "${CLAUDE_SYMLINK_DIRECTORIES[@]}"; do
    local target="$src_dir/$dir"
    local link="$dest_dir/$dir"

    if [ ! -d "$target" ]; then
      echo "Warning: $target not found. Skipping." >&2
      continue
    fi

    if [ -d "$link" ] && [ ! -L "$link" ]; then
      echo "Warning: $link exists and is not a symlink. Removing..." >&2
      rm -rf "$link"
    fi

    if [ -L "$link" ]; then
      if [ "$(readlink "$link")" = "$target" ]; then
        continue
      fi
      ln -sfvn "$target" "$link"
    else
      ln -sv "$target" "$link"
    fi
  done
}

# Codex設定用のシンボリックリンク作成 (.codex/ -> ~/.codex/)
create_codex_symlinks() {
  local src_dir="$DOTFILES_DIR/.codex"
  local dest_dir="$HOME/.codex"

  # ~/.codex ディレクトリが存在しない場合は作成
  mkdir -p "$dest_dir"

  # ファイルのシンボリックリンク
  for file in "${CODEX_SYMLINK_FILES[@]}"; do
    local target="$src_dir/$file"
    local link="$dest_dir/$file"

    if [ ! -f "$target" ]; then
      echo "Warning: $target not found. Skipping." >&2
      continue
    fi

    if [ -f "$link" ] && [ ! -L "$link" ]; then
      echo "Backing up $link to ${link}.backup"
      mv "$link" "${link}.backup"
    fi

    if [ -L "$link" ]; then
      if [ "$(readlink "$link")" = "$target" ]; then
        continue
      fi
      ln -sfv "$target" "$link"
    else
      ln -sv "$target" "$link"
    fi
  done

  # ディレクトリのシンボリックリンク
  for dir in "${CODEX_SYMLINK_DIRECTORIES[@]}"; do
    local target="$src_dir/$dir"
    local link="$dest_dir/$dir"

    if [ ! -d "$target" ]; then
      echo "Warning: $target not found. Skipping." >&2
      continue
    fi

    if [ -d "$link" ] && [ ! -L "$link" ]; then
      echo "Warning: $link exists and is not a symlink. Removing..." >&2
      rm -rf "$link"
    fi

    if [ -L "$link" ]; then
      if [ "$(readlink "$link")" = "$target" ]; then
        continue
      fi
      ln -sfvn "$target" "$link"
    else
      ln -sv "$target" "$link"
    fi
  done

  # Claude スキルを Codex スキルとして共有（個別シンボリックリンク）
  local claude_skills_dir="$DOTFILES_DIR/.config/claude/skills"
  local codex_skills_dir="$dest_dir/skills"
  mkdir -p "$codex_skills_dir"

  for skill in "${CODEX_SHARED_SKILLS[@]}"; do
    local target="$claude_skills_dir/$skill"
    local link="$codex_skills_dir/$skill"

    if [ ! -d "$target" ]; then
      echo "Warning: Claude skill $target not found. Skipping." >&2
      continue
    fi

    if [ -d "$link" ] && [ ! -L "$link" ]; then
      echo "Warning: $link exists and is not a symlink. Skipping." >&2
      continue
    fi

    if [ -L "$link" ]; then
      if [ "$(readlink "$link")" = "$target" ]; then
        continue
      fi
      ln -sfvn "$target" "$link"
    else
      ln -sv "$target" "$link"
    fi
  done
}

main() {
  if ! cd "$DOTFILES_DIR"; then
    echo "Error: $DOTFILES_DIR not found." >&2
    exit 1
  fi

  echo "Processing dotfiles in $DOTFILES_DIR..."

  # ディレクトリ全体のシンボリックリンクを作成
  echo "Creating directory symlinks..."
  for dir in "${ZSH_SYMLINK_DIRECTORIES[@]}"; do
    create_directory_symlink "$dir" || true
  done

  # Claude設定のシンボリックリンクを作成
  echo "Creating Claude config symlinks..."
  create_claude_symlinks || true

  # Codex設定のシンボリックリンクを作成
  echo "Creating Codex config symlinks..."
  create_codex_symlinks || true

  # すべてのファイルとシンボリックリンクを処理（macOS互換）
  echo "Creating file symlinks..."
  while IFS= read -r file; do
    if is_excluded "$file"; then
      continue
    fi
    create_symlink "$file" || true  # エラーが発生しても続行
  done < <(find . \( -type f -o -type l \) ! -path '*.git/*' ! -name '.DS_Store' | sed 's|^\./||')

  echo "Complete! 🚀"
}

main "$@"
