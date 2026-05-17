# worktree: cmux + Claude Code 並列開発用の git worktree 操作 wrapper
#
# 配置: <repo>/.claude/worktrees/<name>/  (claude -w のデフォルト)
#
# 提供 function:
#   wt-new <name> [--no-claude]  - worktree 作成 (デフォルトで claude 起動)
#   wt-ls                        - worktree 一覧 (path / branch / status)
#   wt-rm <name>                 - worktree + branch 削除 (merge 済チェック付き)
#   wt-cd <name>                 - worktree directory に cd (補完対応)
#
# Refs: GitHub Issue #48

_wt_root() {
  git rev-parse --show-toplevel 2>/dev/null
}

_wt_dir() {
  local root
  root=$(_wt_root) || return 1
  echo "$root/.claude/worktrees"
}

_wt_names() {
  local dir
  dir=$(_wt_dir) || return 1
  [[ -d "$dir" ]] || return 0
  print -l "$dir"/*(N:t)
}

# 入力検証: worktree 名は英数字 / ハイフン / アンダースコア / ドット / プラスのみ許可
# path injection (../, /, NUL 等) を防止
_wt_validate_name() {
  if [[ -z "$1" ]]; then
    echo "wt: name is required" >&2
    return 1
  fi
  if ! [[ "$1" =~ ^[a-zA-Z0-9_+.-]+$ ]]; then
    echo "wt: invalid name '$1' (allowed: [a-zA-Z0-9_+.-])" >&2
    return 1
  fi
}

# repo の default branch (origin/HEAD → init.defaultBranch → main → master の順)
_wt_default_branch() {
  local root="$1"
  local b
  b=$(git -C "$root" symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|^refs/remotes/origin/||')
  [[ -z "$b" ]] && b=$(git -C "$root" config init.defaultBranch 2>/dev/null)
  [[ -z "$b" ]] && git -C "$root" show-ref --verify --quiet refs/heads/main && b=main
  [[ -z "$b" ]] && b=master
  echo "$b"
}

wt-new() {
  if [[ -z "$1" || "$1" == "-h" || "$1" == "--help" ]]; then
    echo "usage: wt-new <name> [--no-claude]" >&2
    return 1
  fi
  local name="$1"
  local no_claude="${2:-}"
  _wt_validate_name "$name" || return 1
  local root
  root=$(_wt_root) || { echo "wt-new: not a git repository" >&2; return 1; }

  local wt_path="$root/.claude/worktrees/$name"
  if [[ -d "$wt_path" ]]; then
    echo "wt-new: worktree already exists: $wt_path" >&2
    return 1
  fi

  if [[ "$no_claude" == "--no-claude" ]]; then
    git -C "$root" worktree add "$wt_path" -b "worktree-$name"
  else
    # claude -w は内部で worktree を作る (cwd 必須、name のみ渡す)
    claude -w "$name"
  fi
}

wt-ls() {
  local root
  root=$(_wt_root) || { echo "wt-ls: not a git repository" >&2; return 1; }
  printf "%-50s %-40s %s\n" "PATH" "BRANCH" "STATUS"
  # zsh の予約変数を避ける: `path` (=PATH array)、`status` (=$? read-only)
  local line wp branch st
  git -C "$root" worktree list --porcelain | while IFS= read -r line; do
    case "$line" in
      "worktree "*) wp="${line#worktree }" ;;
      "branch "*)   branch="${line#branch refs/heads/}" ;;
      "detached")   branch="(detached)" ;;
      "")
        if [[ -n "$wp" ]]; then
          if [[ -n "$(git -C "$wp" status --porcelain 2>/dev/null | head -1)" ]]; then
            st="dirty"
          else
            st="clean"
          fi
          printf "%-50s %-40s %s\n" "$wp" "$branch" "$st"
          wp=""; branch=""
        fi
        ;;
    esac
  done
}

wt-rm() {
  if [[ -z "$1" || "$1" == "-h" || "$1" == "--help" ]]; then
    echo "usage: wt-rm <name>" >&2
    return 1
  fi
  local name="$1"
  _wt_validate_name "$name" || return 1
  local root
  root=$(_wt_root) || { echo "wt-rm: not a git repository" >&2; return 1; }
  local wt_path="$root/.claude/worktrees/$name"
  [[ -d "$wt_path" ]] || { echo "wt-rm: worktree not found: $wt_path" >&2; return 1; }

  # 現在のディレクトリが削除対象 (or その配下) の場合は拒否
  # realpath で symlink を解決して prefix match の誤爆 (foo vs foobar) を回避
  local wt_real pwd_real
  wt_real=$(cd "$wt_path" 2>/dev/null && pwd -P) || wt_real="$wt_path"
  pwd_real=$(pwd -P)
  case "$pwd_real" in
    "$wt_real"|"$wt_real"/*)
      echo "wt-rm: cannot remove the worktree you are currently in. cd elsewhere first." >&2
      return 1
      ;;
  esac

  local branch
  branch=$(git -C "$wt_path" rev-parse --abbrev-ref HEAD 2>/dev/null)

  local default_branch
  default_branch=$(_wt_default_branch "$root")

  # merge 状態確認: branch が default_branch の ancestor なら merged
  if [[ "$branch" != "$default_branch" ]] && \
     ! git -C "$root" merge-base --is-ancestor "$branch" "$default_branch" 2>/dev/null; then
    echo "wt-rm: branch '$branch' is NOT merged into $default_branch"
    read -q "REPLY?Delete anyway? [y/N] " || { echo; return 1; }
    echo
  fi

  git -C "$root" worktree remove "$wt_path" && {
    git -C "$root" branch -D "$branch" 2>/dev/null || \
      echo "wt-rm: kept branch '$branch' (delete manually if needed)"
  }
}

wt-cd() {
  if [[ -z "$1" || "$1" == "-h" || "$1" == "--help" ]]; then
    echo "usage: wt-cd <name>" >&2
    return 1
  fi
  _wt_validate_name "$1" || return 1
  local dir
  dir=$(_wt_dir) || { echo "wt-cd: not a git repository" >&2; return 1; }
  local wt_path="$dir/$1"
  [[ -d "$wt_path" ]] || { echo "wt-cd: worktree not found: $wt_path" >&2; return 1; }
  cd "$wt_path" || return 1
}

# 補完: wt-cd / wt-rm に worktree 名を提示
_wt_complete() {
  local -a names
  names=(${(f)"$(_wt_names)"})
  _describe 'worktree' names
}
compdef _wt_complete wt-cd wt-rm 2>/dev/null
