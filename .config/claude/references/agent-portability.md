---
status: reference
last_reviewed: 2026-04-23
---

# Agent 定義ポータビリティガイド

## 目的

特定ベンダー（Anthropic Managed Agents, OpenAI, etc.）にロックインされない Agent 定義の管理方法。
Build to Delete 原則に基づき、いつでも別基盤に移行可能な状態を維持する。

## ポータビリティ戦略

### 1. Canonical Definition（正規定義）をローカルに持つ

```
.config/claude/agents/*.md        ← 正規定義（ローカル git 管理）
    ↓ エクスポート
Managed Agents API                ← デプロイ先（クラウド）
    ↓ エクスポート
OpenAI Agents API                 ← 代替デプロイ先
```

**原則**: 正規定義は常にローカルの git リポジトリに。クラウドはデプロイ先。

### 2. Vendor-Neutral なフィールドセット

以下のフィールドはベンダー間で共通性が高い:

| フィールド | 互換性 | 注意 |
|-----------|--------|------|
| name | 高 | kebab-case で統一 |
| model | 中 | ベンダーごとにモデル名が異なる → マッピングテーブルが必要 |
| system_prompt | 高 | ほぼそのまま移行可能 |
| tools | 低 | ツール名・スキーマがベンダー固有 |
| mcp_servers | 中 | MCP 対応ベンダーなら互換 |

### 3. Decision Journal 連携

Agent 設計の決定を `references/decision-journal.md` に記録:

- なぜこの model を選んだか
- なぜこの tools 構成にしたか
- なぜこの system_prompt の構造にしたか

→ 移行時に「なぜそうなっているか」が再現可能

### 4. エクスポート/インポート形式

#### 推奨: YAML Canonical Format

```yaml
# agents/reviewer.canonical.yaml
meta:
  name: reviewer
  version: "1.0"
  created: 2026-04-09
  description: "Code review specialist"

spec:
  model_preference: "mid-tier"  # vendor-neutral: low/mid/high/top
  system_prompt: |
    You are a code reviewer...
  tools_required:
    - category: "code_execution"
    - category: "file_system"
    - category: "web_search"
  max_tokens: 16384

vendor_overrides:
  anthropic:
    model: "claude-sonnet-4-6"
    tools: ["bash_20250124", "text_editor_20250124"]
  openai:
    model: "gpt-5.5"
    tools: ["code_interpreter"]
```

### 5. 移行チェックリスト

移行時に確認する項目:

- [ ] 全 Agent の canonical 定義が git にあるか
- [ ] system_prompt にベンダー固有の指示が混入していないか
- [ ] tools のマッピングテーブルが最新か
- [ ] Decision Journal の該当エントリが揃っているか
- [ ] テスト: 移行先で同等の品質が出るか（A/B テスト）

## 現時点のアクション

1. **新規エージェント作成時**: canonical YAML を先に書き、そこから各ベンダー形式に変換
2. **既存エージェント**: 変更時に順次 canonical 化（一括変換はしない）
3. **Decision Journal**: Agent 設計決定は必ず記録

## 関連ドキュメント

- `references/agent-config-standard.md` — Agent Config 標準化
- `references/managed-agents-hybrid.md` — Hybrid Architecture 全体像
- `references/decision-journal.md` — 設計決定ジャーナル
