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

## agent に設定を書かせたときの 3 点確認

`task validate-configs` は構文と参照整合を見るだけで、**その設定が実際に効いているか**は見ない。
agent に config を書かせた変更では、以下の 3 点が揃って初めて完了とする。

1. **diff** — 何がどう変わったかを提示する
2. **形式互換** — 現在インストールされている CLI のバージョンがその書式を受け付けるか確認する
3. **有効性** — 書いた設定が実際にランタイムに載っているかを、CLI を 1 回動かして確認する

3 が抜けると「書いたが読まれていない設定」が静かに残る。
実例: `.codex/agents/*.toml` の 12 個は 5 ヶ月間 `~/.codex/` へ配備されず、
配備しても現行 CLI には選択手段が無かった (`rules/codex-delegation.md`「名前付き custom agent は作らない」参照)。
1 と 2 だけは当時も満たしていた。
