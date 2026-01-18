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
  "^\.config/zsh/"  # ディレクトリ全体でシンボリックリンクするため除外
)

# ディレクトリ全体をシンボリックリンクするリスト
ZSH_SYMLINK_DIRECTORIES=(
  ".config/zsh"
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
