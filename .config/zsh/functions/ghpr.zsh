# ghpr: gh pr create に PR 本文ひな形を載せる
#
# 正本: ~/.agents/skills/pr-issue-style/templates/
#   ghpr small   … 見出しなし 3 文（pr-body-small.md）
#   ghpr medium  … Why / What changed / …（pr-body-medium.md）
# 以降の引数は gh pr create にそのまま渡す。
#
# 例:
#   ghpr small --title "[zsh] Add ghpr helper" --draft
#   ghpr medium --fill

_ghpr_style_root() {
  local candidates=(
    "${HOME}/.agents/skills/pr-issue-style"
    "${HOME}/.codex/skills/pr-issue-style"
    "${HOME}/dotfiles/.agents/skills/pr-issue-style"
  )
  # この repo を直接開いているとき用（symlink 前でも動く）
  local here
  here="$(git rev-parse --show-toplevel 2>/dev/null)"
  if [[ -n "$here" ]]; then
    candidates+=("${here}/.agents/skills/pr-issue-style")
  fi

  local dir
  for dir in "${candidates[@]}"; do
    if [[ -d "$dir/templates" ]]; then
      echo "$dir"
      return 0
    fi
  done
  return 1
}

ghpr() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || -z "${1:-}" ]]; then
    cat >&2 <<'EOF'
usage: ghpr <small|medium> [gh pr create の追加引数...]

  small   templates/pr-body-small.md を --body-file に渡す
  medium  templates/pr-body-medium.md を --body-file に渡す

追加引数に --body / --body-file が既にある場合はそのまま gh に渡し、ひな形は付けない。
EOF
    return 1
  fi

  local size="$1"
  shift

  local template_name
  case "$size" in
    small|s) template_name="pr-body-small.md" ;;
    medium|med|m|large|l) template_name="pr-body-medium.md" ;;
    *)
      echo "ghpr: unknown size '$size' (expected small|medium)" >&2
      return 1
      ;;
  esac

  # 呼び出し側が本文を既に指定しているなら上書きしない
  local arg
  for arg in "$@"; do
    case "$arg" in
      --body|--body-file|--body=*)
        command gh pr create "$@"
        return $?
        ;;
    esac
  done

  local root template
  root="$(_ghpr_style_root)" || {
    echo "ghpr: pr-issue-style skill が見つかりません（nix:switch / symlink を確認）" >&2
    return 1
  }
  template="${root}/templates/${template_name}"
  if [[ ! -f "$template" ]]; then
    echo "ghpr: template missing: $template" >&2
    return 1
  fi

  command gh pr create --body-file "$template" "$@"
}

# 短別名
alias ghpr-small='ghpr small'
alias ghpr-medium='ghpr medium'
