# Setup Requirements

`scripts/lifecycle/doctor.sh` (= `task doctor`) が参照する minimum version / install 経路の **single source of truth**。

詳細仕様: `docs/specs/2026-05-13-setup-doctor.md`

## 分類

- **required** (不在 = `FAIL`): bootstrap が走らない / Taskfile が動かない
- **recommended** (不在 = `WARN`): 体験は劣化するが致命的ではない
- **bootstrap-gated** (`task nix:bootstrap` 後に出現する想定なので未実行マシンでは `SKIP`)

## Table

形式は **bash-parseable な行指向**: doctor.sh が `awk` で `$1 $2 $3` を読む。コメント行 (`#` 始まり) と空行は無視。

各行: `<tier> <name> <min_version_or_-> <probe_command>`

- `tier` = `required` / `recommended` / `bootstrap_gated`
- `min_version` = semver 文字列、不要なら `-`
- `probe_command` = stdout からバージョン文字列を取り出す shell command。`{bin}` placeholder は `name` に置換

```setup-requirements
# tier            name             min       probe_command
required          rtk              0.39.0    {bin} --version | awk '{print $2}'
required          jq               1.6       {bin} --version | sed 's/^jq-//'
required          gh               2.0       {bin} --version | head -1 | awk '{print $3}'
required          task             3.0       {bin} --version | tr -d 'v'
required          git              2.30      {bin} --version | awk '{print $3}'
required          brew             4.0       {bin} --version | head -1 | awk '{print $2}'

recommended       sheldon          -         -
recommended       direnv           -         -
recommended       mise             -         -
recommended       starship         -         -
recommended       claude           -         {bin} --version | awk '{print $1}'

bootstrap_gated   darwin-rebuild   -         test -x /run/current-system/sw/bin/darwin-rebuild
```

## 更新方針

- rtk のように commit 由来で minimum version を引き上げたい時はこのファイルを編集する (single source)
- 新規 binary 追加は **`required` のハードルを慎重に**: 不在で bootstrap 全停止するため、recommended から始めて運用実績を貯める
- minimum version の権威ソース:
  - rtk: upstream release notes
  - jq / gh / git: brew formula のデフォルト
  - task: go-task release tag
  - claude: npm `@anthropic-ai/claude-code` の package.json
