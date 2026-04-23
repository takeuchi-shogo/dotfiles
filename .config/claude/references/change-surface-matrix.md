---
status: active
last_reviewed: 2026-04-23
---

# Change Surface Matrix

harness 関連ファイルを変更する際に、併せて確認すべきファイルと最低限の検証コマンド。

| 変更対象 | 併せて見る | 最低検証 |
|----------|-----------|---------|
| `CLAUDE.md`, `settings.json`, `scripts/`, `skills/` | `PLANS.md`, `references/workflow-guide.md`, `docs/agent-harness-contract.md` | `task validate-configs`, `task validate-symlinks` |
| `commands/` | 対応する skill / script / workflow guide | 関連 skill / script の構文確認 |
| `agents/`, `references/` | `references/workflow-guide.md` の Agent Routing Table、関連スキル定義 | 参照整合性の目視確認（エージェント名・ファイルパスの一致） |
| `.bin/symlink.sh`, `.bin/validate_symlinks.sh` | Claude 側 symlink 対象、`Taskfile.yml` | `task symlink`, `task validate-symlinks` |
