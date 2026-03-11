# Claude Config Changes

`.config/claude/` を変えるときの playbook。

## Read First

- `AGENTS.md`
- `.config/claude/CLAUDE.md`
- `.config/claude/references/workflow-guide.md`
- `PLANS.md`
- `docs/agent-harness-contract.md`

## Typical Scope

- `.config/claude/CLAUDE.md`
- `.config/claude/settings.json`
- `.config/claude/scripts/`
- `.config/claude/skills/`
- `.config/claude/commands/`

## Standard Steps

1. hook / skill / command / reference のどこを変えるか先に切り分ける
2. workflow guide と設定の整合を確認する
3. hook を足すなら timeout、失敗時の挙動、対象 matcher を明示する
4. skill や command を足すなら、参照先 script / reference も揃える
5. symlink される設定なら home 側公開も確認する

## Minimum Validation

- `task validate-configs`
- `task validate-symlinks`

## Watchouts

- Claude 固有 hook 保証を repo 共通 contract に混ぜない
- `git commit --no-verify` を許さない
- completion gate、checkpoint、session save/load の前提を壊さない
