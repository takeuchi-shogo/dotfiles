---
status: reference
last_reviewed: 2026-04-23
---

# Agent Config 標準化リファレンス

## 現状: 分散定義

| 基盤 | 形式 | パス | 含まれる情報 |
|------|------|------|-------------|
| Claude Code | Markdown | `.config/claude/agents/*.md` | name, description, role instructions |
| Blueprints | YAML | `references/blueprints/*.yaml` | workflow DAG, tools scope, failure policy |

## Managed Agents の Agent 定義

Managed Agents API では Agent を以下の統合形式で定義:

```yaml
# 概念的な形式（API は JSON だが YAML で管理し CLI でデプロイ）
name: "reviewer"
model: "claude-sonnet-5"
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

Codex にはファイルベースの agent 定義形式が無い (`spawn_agent` は `task_name` / `message` /
`fork_turns` のみ)。対応表は Managed Agents と Claude Code の 2 者で取る。

| Managed Agents フィールド | Claude Code agents/*.md | 統合方針 |
|--------------------------|------------------------|----------|
| name | YAML frontmatter name | そのまま |
| model | （暗黙: 親セッション継承） | 明示化推奨 |
| system_prompt | Markdown 本文 | フォーマット変換 |
| tools | （制限なし） | スコープ明示化 |
| skills | — | Managed Agents native 対応済 (2026-06、shared/private wiring 可)。ローカル agents/*.md 側は未標準化 |
| mcp_servers | — | Managed Agents native 対応済 (2026-06、shared/private wiring 可)。ローカル agents/*.md 側は未標準化 |
| max_tokens | — | 将来対応 |

## 統合ビジョン

### 短期（現在のセットアップ内）

1. **agents/*.md に YAML frontmatter を標準化**: name, model, tools_scope を必須フィールドに
2. **Blueprints との連携**: agents/*.md から Blueprint ノードを参照可能に

### 中期（Managed Agents 導入時）

1. **エクスポートスクリプト**: agents/*.md → Managed Agents API 形式の変換ツール
   - **自前実装は不要 (2026-06)**: `agentlift` (MIT, github.com/phuryn/agentlift) が `.managed-agents/` folder から Anthropic Managed Agents / Google Vertex Agent Engine / OpenAI Agents SDK への cross-provider compiler (deploy/export/audit) を提供。将来 managed deploy 時はまずこれを評価する。ローカル `.config/claude/agents/*.md` は触らず別レイヤーとして共存する設計
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
- `.config/claude/agents/` — 現在の Claude Code エージェント定義
