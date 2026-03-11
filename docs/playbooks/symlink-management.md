# Symlink Management

home 側へ公開する managed symlink を変更するときの playbook。

## Read First

- `AGENTS.md`
- `Taskfile.yml`
- `.bin/symlink.sh`
- `.bin/validate_symlinks.sh`

## Typical Scope

- 新しい managed file / directory の追加
- 除外パターンの更新
- `~/.claude/` と `~/.codex/` への個別公開
- project-local skill の公開対象更新

## Standard Steps

1. 追加したい path が generic symlink か custom symlink かを決める
2. exclude pattern が必要か確認する
3. `.bin/symlink.sh` と `.bin/validate_symlinks.sh` をセットで更新する
4. home 側へ不要 artifact を漏らさないか確認する

## Minimum Validation

- `task symlink`
- `task validate-symlinks`

## Watchouts

- `.agents/skills/` は generic に home へ出さず、`~/.codex/skills/` へ個別公開する
- cache、test artifact、temporary file を home に展開しない
- 既存の非 symlink ファイルは上書きせず warning 扱いにする
