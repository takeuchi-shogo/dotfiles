# Codex Model Selection Guide

| Model | Best For | Reasoning | Speed |
|-------|---------|-----------|-------|
| gpt-5.4 (default) | 汎用分析・リファクタリング | High | Standard |
| gpt-5.2-max | 深い推論、複雑な設計 | Max | Slow |
| gpt-5.2 | バランス型 | High | Standard |
| gpt-5.2-mini | 単純タスク、コスト節約 | Medium | Fast |

## Sandbox Mode Guide

| Mode | Use Case |
|------|----------|
| plan (default) | Read-only 分析、レビュー |
| workspace-write | コード編集、リファクタリング |

## Common Patterns

- **分析**: `codex exec "Analyze X" --reasoning-effort high`
- **リファクタリング**: `codex exec "Refactor X" -w workspace-write`
- **レビュー**: `codex exec "Review diff" --reasoning-effort xhigh`
