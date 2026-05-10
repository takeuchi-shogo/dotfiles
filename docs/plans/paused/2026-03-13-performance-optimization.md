---
status: active
last_reviewed: 2026-04-23
---

# Performance Optimization Plan

## Goal
品質を落とさず、サブエージェントとhookの応答速度を最適化する

## Phase 1: Agent Model Changes (即時)
- [ ] codex-debugger: sonnet → haiku (CLIラッパー)
- [ ] codex-reviewer: sonnet → haiku (CLIラッパー)
- [ ] gemini-explore: sonnet → haiku (CLIラッパー)
- [ ] db-reader: sonnet → haiku (制約ベースゲートキーパー)
- [ ] doc-gardener: sonnet → haiku (パターンベース)
- [ ] security-reviewer: sonnet → opus (高リスク分析)

## Phase 2: Rust Hook Binary
14個の Python/JS hook を 1 つの Rust バイナリに統合。

### サブコマンド構成
```
claude-hooks post-bash      # 5 hooks → 1 (output-offload, error-to-codex, post-test, plan-lifecycle, review-feedback)
claude-hooks post-edit      # 4 hooks → 1 (auto-format, suggest-compact, golden-check, checkpoint)
claude-hooks pre-edit       # 2 hooks → 1 (protect-linter, search-first)
claude-hooks pre-bash       # 1 hook (git add -A block)
claude-hooks pre-search     # 1 hook (search-first for read tools)
claude-hooks pre-websearch  # 1 hook (suggest-gemini)
claude-hooks user-prompt    # 1 hook (agent-router)
```

### 期待効果
- PostToolUse/Bash: 5プロセス(~500ms) → 1プロセス(~3ms)
- PostToolUse/Edit: 4プロセス(~400ms) → 1プロセス(~3ms) + formatter実行時間
- PreToolUse: 2プロセス(~200ms) → 1プロセス(~2ms)
- 合計: 1ツール呼び出しあたり ~300-650ms 短縮

## Phase 3: settings.json 更新
- 旧hookエントリを新バイナリに差し替え
- 旧スクリプトはバックアップとして残す
