---
name: ai-workflow-audit
description: >
  Audit and upgrade a repo's AI operating model. Use when improving Claude Code or
  Codex workflows, deciding what belongs in skills vs memory vs scripts, or carrying
  reusable AI practices across repos.
  Triggers: 'AI ワークフロー', 'workflow audit', 'スキル整理', 'skills vs memory', 'AI 運用改善', 'AI practices'.
  Do NOT use for: コードベース監査（use /audit）、スキル個別の改善（use /skill-creator）、ドキュメント鮮度チェック（use /check-health）。
origin: self
allowed-tools: "Read, Bash, Grep, Glob, Agent"
metadata:
  pattern: reviewer
disable-model-invocation: true
---

# AI Workflow Audit

`docs/guides/ai-workflow-audit.md` を前提に、属人的な AI 利用を再利用可能な workflow に変える。

## Trigger

以下の状況で使う:

- Claude Code / Codex の運用を強化したい
- 同じ調査、同じ指示、同じ修正が繰り返される
- skill、memory、script、hook、MCP のどれに落とすべきか迷う
- 他の repo に知見を共有できる形へ整理したい

## Workflow

### 1. Inventory

まず次を確認する:

- `AGENTS.md`
- `Taskfile.yml` と validation script
- `.mcp.json`
- `.agents/skills/`
- `.codex/`
- `.config/claude/`
- 変更対象に近い README / guide

非自明なら Agent を使い、Codex 側と Claude 側の inventory を並列で集める。

### 2. Audit

以下の lens で gap を見る:

- **discovery**: 実装前調査が workflow 化されているか
- **orchestration**: model、tool、MCP、task の接続が設計されているか
- **verification**: 完了前の証拠確認があるか
- **memory and continuity**: checkpoint と durable memory が整理されているか
- **portability**: repo 固有ルールと cross-repo ルールが分かれているか
- **packaging**: 繰り返し手順が skill / script / hook に昇格されているか

### 3. Promote

昇格先は次で決める:

- session 限定の状態 → checkpoint
- repo 固有の安定ルール → `AGENTS.md` または repo-local skill
- 複数 repo で再利用する判断基準 → global skill または durable memory
- 毎回必須の手順 → task / script / hook
- 外部情報取得経路 → MCP / tool config

### 4. Implement

最小変更で実装する:

- 既存 skill を extend できるなら新規作成しない
- docs で足りるなら script を増やさない
- 実行保証が必要なら docs だけで済ませない

### 5. Verify

`verification-before-completion` を使い、変更面に最も近い validation を実行する。

## Output Format

```md
## AI Workflow Audit
- Goal:
- Current friction:
- Chosen lens:
- Promotion target:
- Planned change:
- Validation:
```

## Anti-Patterns

- 便利そうという理由だけで新しい tool や script を増やす
- prompt を skill や template に固定せず、毎回その場で書き直す
- repo 固有ルールを global memory に混ぜる
- docs に書いただけで運用が定着すると期待する

## Skill Assets

- `references/audit-checklist.md` — Checklist covering Skills, Agents, Hooks, Memory, and Configuration audit criteria
