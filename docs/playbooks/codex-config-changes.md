# Codex Config Changes

`.codex/` や `.agents/skills/` を変えるときの playbook。

## Read First

- `AGENTS.md`
- `.codex/AGENTS.md`
- `PLANS.md`
- `docs/agent-harness-contract.md`
- `docs/guides/codex-long-horizon-workflow.md`

## Typical Scope

- `.codex/config.toml`
- `.codex/AGENTS.md`
- `.agents/skills/`
- `.bin/symlink.sh`
- `.bin/validate_symlinks.sh`

## Standard Steps

1. goal、scope、validation を plan に書く
2. 既存 skill / profile / MCP / memory を確認する
3. 変更面に応じて `.codex/` と `.agents/skills/` の両方を更新する
4. skill を追加したら symlink 公開対象も更新する
5. validation を実行する

## Minimum Validation

- `task validate-configs`
- `task symlink`
- `task validate-symlinks`

## Watchouts

- `personality` と task ごとの output control を混ぜない
- Claude 固有 hook を Codex 側へ持ち込まない
- 新しい skill を追加したのに `~/.codex/skills/` 公開を忘れない
