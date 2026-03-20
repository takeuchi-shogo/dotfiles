# Codex Config Changes

`.codex/` や `.agents/skills/` を変えるときの playbook。

## Read First

- `AGENTS.md`
- `.codex/AGENTS.md`
- `PLANS.md`
- `docs/agent-harness-contract.md`
- `docs/guides/codex-long-horizon-workflow.md`
- `docs/playbooks/codex-subagent-usage.md`
- Apps / connectors を触る場合は `docs/playbooks/codex-apps-pilot.md`

## Typical Scope

- `.codex/config.toml`
- `.codex/AGENTS.md`
- `.codex/rules/*.rules`
- `.agents/skills/`
- Apps / connectors を使う場合の feature flag と app config
- `.bin/symlink.sh`
- `.bin/validate_symlinks.sh`

## Standard Steps

1. goal、scope、validation を plan に書く
2. 既存 skill / profile / MCP / memory を確認する
3. custom agent / playbook / skill のどこを変えるか先に切り分ける
4. approval friction を durable 化したい場合は `.codex/rules/*.rules` を検討し、自然言語 guidance は `AGENTS.md` に残す
5. 変更面に応じて `.codex/` と `.agents/skills/` の両方を更新する
6. rules を追加・変更したら `codex execpolicy check --pretty --rules <file> -- <command>` で代表例を確認する
7. skill を追加したら `~/.codex/skills/` と `~/.agents/skills/` の公開対象も更新する
8. validation を実行する

## Minimum Validation

- `task validate-configs`
- `task symlink`
- `task validate-symlinks`
- docs を変えた場合は `task validate-readmes`

## Watchouts

- `personality` と task ごとの output control を混ぜない
- Claude 固有 hook を Codex 側へ持ち込まない
- 新しい skill を追加したのに `~/.codex/skills/` と `~/.agents/skills/` の公開を忘れない
- subagent の詳細テンプレートは `docs/playbooks/codex-subagent-usage.md` へ寄せ、`.codex/AGENTS.md` は短い運用ルールに留める
- `Rules` は experimental 前提で扱い、初回は read-only / low-risk prefix だけに絞る
- Apps / connectors は常時有効化の前に one-off pilot を優先する
