---
source: docs/research/2026-03-23-minimax-skills-analysis.md
date: 2026-03-23
status: in-progress
scale: L
---

# MiniMax-AI/skills パターン統合プラン

## 概要

MiniMax-AI/skills から抽出した4つのパターンを現在のスキル体系に統合する。
全59スキルへの一括適用ではなく、パイロットスキル（5個）で検証後に展開する。

## Task 1: Anti-Patterns を ❌/✅ 対比表に進化

**現状**: 箇条書きリスト（「○○しない」の羅列）
**目標**: 番号付き ❌/✅ テーブルで Bad → Good を対比表示

### Before (現在)

```markdown
## Anti-Patterns

- spike のコードを本番に持ち込む
- spec なしで Build に進む
```

### After (目標)

```markdown
## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | spike のコードを本番に持ち込む | Phase 4 で正式実装する |
| 2 | spec なしで Build に進む | 最低限 acceptance criteria を定義する |
```

### パイロット対象（5スキル）

1. `epd/SKILL.md` — パイプライン型の代表
2. `spec/SKILL.md` — 生成型の代表
3. `validate/SKILL.md` — 検証型の代表
4. `review/SKILL.md` — レビュー型の代表（Anti-Patterns があれば）
5. `spike/SKILL.md` — パイプライン型の第2例

### 展開基準

パイロット5スキルの変換完了後、ユーザー確認を経て残りのスキルに展開。
`skill-creator` の skill-writing-principles にもテーブル形式をデフォルトとして追記。

---

## Task 2: Metadata 拡張

**現状**: `name` と `metadata.pattern` のみ
**目標**: `version`, `category`, `sources` を追加

### After (目標)

```yaml
metadata:
  pattern: pipeline
  version: 1.0.0
  category: workflow
  sources:
    - "Harrison Chase: Builder or Reviewer"
```

### category 体系（案）

| category | 対象スキル例 |
|----------|-------------|
| workflow | epd, spike, rpi, autonomous |
| quality | review, validate, verification-before-completion |
| generation | spec, frontend-design, autocover |
| research | research, absorb, debate, gemini |
| operations | morning, daily-report, weekly-review, timekeeper |
| tooling | codex, codex-review, webapp-testing |
| architecture | senior-architect, senior-backend, senior-frontend |
| knowledge | obsidian-*, digest, eureka, continuous-learning |
| security | careful, freeze, security-review |
| meta | skill-creator, skill-audit, ai-workflow-audit, improve |

### パイロット対象

Task 1 と同じ5スキル。Anti-Patterns テーブル化と同時に metadata も拡張する。

### 展開基準

パイロット後、`skill-creator` テンプレートに category/version/sources を追加し、
新規スキル作成時にデフォルトで含まれるようにする。既存スキルは段階的に追加。

---

## Task 3: Decision Table 強化

**現状**: review, search-first に判断テーブルあり。他のスキルは散文で判断を説明。
**目標**: 判断分岐が存在するスキルに Decision Table を追加

### 追加候補スキル

| スキル | 追加する Decision Table | 理由 |
|--------|----------------------|------|
| `epd` | spike vs rpi vs epd の使い分け | ユーザーが迷いやすい分岐点 |
| `research` | research vs gemini vs debate の使い分け | 3つのリサーチ系スキルの境界が曖昧 |
| `senior-architect` | monolith vs microservices 判断基準 | アーキテクチャ決定の中核 |
| `absorb` | 取り込み規模に応じた実行方法 | Phase 5 の Handoff 判断 |

### テーブル形式

```markdown
## Decision: いつ spike vs rpi vs epd を使うか

| 状況 | 推奨 | 理由 |
|------|------|------|
| 仕様が曖昧、実現可能性が不明 | `/spike` | 最小実装で検証 |
| 仕様は明確、複雑度が中程度 | `/rpi` | Research→Plan→Implement |
| 仕様が曖昧 + 大規模 | `/epd` | Spec→Spike→Validate→Build→Review |
```

### パイロット対象

`epd` と `research` の2スキル。他は効果を確認後に追加。

---

## Task 4: マルチ言語コード例

**現状**: JS/TS のみ
**目標**: 開発系スキルで同一パターンを複数言語で提示

### 対象と方針

このタスクは **選択的に適用** する。全スキルへの展開は不要。

| スキル | 追加言語 | 理由 |
|--------|---------|------|
| `senior-backend` | Go, Python | バックエンド開発はマルチ言語 |
| `senior-architect` | Go, Python | アーキテクチャパターンは言語非依存 |
| `graphql-expert` | Go, Python | GraphQL は複数言語で使われる |

### 制約

- 既に十分なコード例があるスキル（react-best-practices 等）には追加しない
- フロントエンド系スキルは JS/TS のみで十分
- コード例は references/ に配置し、SKILL.md のサイズ肥大を防ぐ

---

## 実行順序

```
Task 1 + Task 2（パイロット5スキル）
  ↓ ユーザー確認
Task 3（Decision Table 2スキル）
  ↓ ユーザー確認
Task 1 + Task 2 展開（残りスキル）
Task 4（マルチ言語、選択的）
  ↓
skill-creator テンプレート更新
```

## 依存関係

- Task 1 と Task 2 は同時実行可能（同じファイルを編集）
- Task 3 は独立
- Task 4 は独立だが優先度最低
- 全タスク完了後に `skill-creator/references/skill-writing-principles.md` を更新

## リスク

| リスク | 軽減策 |
|--------|--------|
| Anti-Patterns テーブル化で情報が欠落 | Before/After を diff で確認 |
| Metadata 追加でフロントマター肥大 | 必須は pattern/version/category のみ。sources はオプショナル |
| Decision Table が古くなる | skill-audit で定期チェック |
| マルチ言語例の保守コスト | references/ に分離し、更新頻度を下げる |
