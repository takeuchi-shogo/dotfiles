---
status: reference
last_reviewed: 2026-04-23
---

# Agent Config 標準化リファレンス

## 現状: 分散定義

| 基盤 | 形式 | パス | 含まれる情報 |
|------|------|------|-------------|
| Codex | TOML | `.codex/agents/*.toml` | name, model, sandbox_mode, approval_policy, instructions |
| Claude Code | Markdown | `.config/claude/agents/*.md` | name, description, role instructions |
| Blueprints | YAML | `references/blueprints/*.yaml` | workflow DAG, tools scope, failure policy |

## Managed Agents の Agent 定義

Managed Agents API では Agent を以下の統合形式で定義:

```yaml
# 概念的な形式（API は JSON だが YAML で管理し CLI でデプロイ）
name: "reviewer"
model: "claude-sonnet-4-6"
system_prompt: |
  You are a code reviewer...
tools:
  - computer_20250124
  - text_editor_20250124
  - bash_20250124
skills:
  - id: "skill_abc123"
mcp_servers:
  - name: "github"
    url: "https://..."
max_tokens: 16384
```

## 対応表

| Managed Agents フィールド | Codex TOML | Claude Code agents/*.md | 統合方針 |
|--------------------------|------------|------------------------|----------|
| name | name | YAML frontmatter name | そのまま |
| model | model | （暗黙: 親セッション継承） | 明示化推奨 |
| system_prompt | developer_instructions | Markdown 本文 | フォーマット変換 |
| tools | sandbox_mode で暗黙制御 | （制限なし） | スコープ明示化 |
| skills | — | — | 将来対応 |
| mcp_servers | — | — | 将来対応 |
| max_tokens | — | — | 将来対応 |

## 統合ビジョン

### 短期（現在のセットアップ内）

1. **agents/*.md に YAML frontmatter を標準化**: name, model, tools_scope を必須フィールドに
2. **Codex TOML との命名規約統一**: kebab-case で統一
3. **Blueprints との連携**: agents/*.md から Blueprint ノードを参照可能に

### 中期（Managed Agents 導入時）

1. **エクスポートスクリプト**: agents/*.md → Managed Agents API 形式の変換ツール
2. **CLI for setup, SDK for runtime** パターンの採用
3. **Agent Template の git 管理**: YAML 形式で agents/ 配下にバージョン管理

### 長期

1. **双方向同期**: ローカル定義 ↔ Managed Agents API
2. **統一 Agent Registry**: ローカルとクラウドのエージェントを一元管理

## 注意事項

- 統合は段階的に進める。既存の agents/*.md を一括変換しない
- まず新規エージェントから YAML frontmatter を標準化
- 既存エージェントは変更時に順次対応

## 関連ドキュメント

- `references/managed-agents-hybrid.md` — Hybrid Architecture 全体像
- `references/agent-portability.md` — ベンダーロックイン回避
- `.codex/agents/` — 現在の Codex エージェント定義
- `.config/claude/agents/` — 現在の Claude Code エージェント定義
