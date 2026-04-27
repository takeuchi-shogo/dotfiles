# Spec: Claude Hooks → Codex Migration

**Date**: 2026-04-27
**Source**: [absorb analysis](../research/2026-04-27-codex-claude-parity-absorb-analysis.md) — G13
**Status**: deferred (large scope)
**Workflow**: spec → /epd (別セッション、L 規模)

## Context

Claude Code 側の hook configuration:
- `~/.claude/settings.json` の `hooks` セクション: 43 hook 設定 (PreToolUse 9, PostToolUse 22, SessionStart 5, Stop 1, Notification 1, UserPromptSubmit 2, PreCompact 1, PostCompact 1, SubagentStop 1)
- 主要実装: Rust binary `~/dotfiles/tools/claude-hooks/target/release/claude-hooks` に subcommand (`post-edit`, `post-bash` 等)
- Python scripts: `~/dotfiles/scripts/{policy,lifecycle,runtime,learner,lib}/` 配下に多数

Codex hooks framework (v0.124.0 stable) は **shell command + JSON I/O** ベース。Python script は実行可能だが Claude-specific path/env を Codex 規約に書き換え必要。

## Why deferred

1. **Rust binary の port が必要**: `claude-hooks` は Claude 専用パス前提。Codex 用にビルドし直すか、subcommand を直接 shell command として呼ぶ書き換えが必要
2. **Python scripts の path 依存**: `~/.claude/settings.json` 読み取り、`~/.claude/scripts/lib/hook_utils.py` import 等が Claude 前提
3. **Event 名の差異**: Claude `PostToolUse` matcher (e.g., `Edit|Write`) → Codex の matcher は同じ regex だが、tool 名が一部異なる (Claude `Edit` ↔ Codex `apply_patch`)
4. **44 hook の意義評価**: 全 port は YAGNI。Codex 文脈で意味のある hook を選別

## Migration Strategy (Phased)

### Phase 1: Pilot (3 hook)
1 つは既に G1 で配備済 (PostToolUse apply_patch lint warning)。次の候補:
- **PostToolUse apply_patch** で `protect-linter-config` の Codex 版 (lint 設定の変更を block)
- **SessionStart** で workspace context 読み込み (Codex memories と統合)
- **PreToolUse Bash** で危険コマンド検出 (`rm -rf`, `git push --force` 等)

### Phase 2: Top 10 (本セッション後の別 plan)
価値マトリックスで上位 10 を選定。候補:

| Claude hook | Codex 移植価値 | 理由 |
|-------------|--------------|------|
| `protect-linter-config` | 高 | リンター設定保護は Codex でも有効 |
| `golden-check` | 高 | golden principle 違反検出 |
| `error-to-codex` | N/A | Codex 自身なので不要 |
| `suggest-gemini` | 中 | Gemini 委譲ヒント |
| `completion-gate` | 中 | 完了前検証 (Codex の `verification-before-completion` skill と統合) |
| `mcp-audit` | 高 | MCP tool filtering |
| `golden-cleanup` | 中 | golden 原則違反スキャン |
| `file-proliferation-guard` | 中 | ファイル増殖防止 |
| `output-offload` | 低 | 大量出力オフロード (Codex は handles separately) |
| `claudemd-size-check` | N/A | AGENTS.md 用に書き換え必要 |

### Phase 3: Full migration (実施しない可能性大)
43 hook 全 port は実行コスト高。Phase 2 完了後、本当に必要かを再評価。

## Acceptance Criteria

### Phase 1
- [ ] 3 hook が `~/.codex/config.toml [hooks]` に配備
- [ ] `codex exec` で各 event 起動時に hook が発火することを log 確認
- [ ] hook が誤発火しないこと (matcher が厳密)
- [ ] ロールバック手順: `codex_hooks = false` で全 hook 無効化できる

### Phase 2
- [ ] top 10 hook を選定し採用判断
- [ ] 各 hook で `codex_hooks` 起動時クラッシュ (#19199) 回避を確認

## Risks

- **#19199 系のクラッシュ**: hook 追加で起動失敗 → 1 つずつ追加して確認
- **既存 Claude harness との干渉**: Codex hook で Claude 用 path を上書きしない
- **Python venv path**: hook script の `python3` が想定 venv を使うか確認
- **infinite loop**: hook が hook 自身を triggering する可能性 (matcher 設計で回避)

## Implementation Sketch (Phase 1)

```toml
# ~/.codex/config.toml
[features]
codex_hooks = true

# 1. Linter config protection
[[hooks.PreToolUse]]
matcher = "apply_patch"

[[hooks.PreToolUse.hooks]]
type = "command"
command = "/Users/takeuchishougo/dotfiles/.codex/hooks/protect-linter-config-codex.sh"
timeout = 5
statusMessage = "Checking linter config integrity"

# 2. Session start context load
[[hooks.SessionStart]]
matcher = "startup|resume"

[[hooks.SessionStart.hooks]]
type = "command"
command = "/Users/takeuchishougo/dotfiles/.codex/hooks/session-context-codex.sh"
timeout = 10

# 3. Dangerous command guard
[[hooks.PreToolUse]]
matcher = "shell|Bash"

[[hooks.PreToolUse.hooks]]
type = "command"
command = "/Users/takeuchishougo/dotfiles/.codex/hooks/dangerous-command-guard.sh"
timeout = 3
```

各 script は stdin で JSON を受け取り、exit 2 で block、exit 0 で allow。

## Recommendation

**別セッションで `/epd`** → Phase 1 (3 hook pilot) を spike → 効果測定 → Phase 2 (top 10) を別 plan 化。Phase 3 は YAGNI 判定で skip 可能性大。

## Out of Scope

- 全 43 hook の機械的 port (Pruning-First 違反)
- Rust binary `claude-hooks` の Codex 用ビルド (overhead 大)
- Claude 側 hook の削除 (Codex 移植は **並存**、Claude 側は維持)
