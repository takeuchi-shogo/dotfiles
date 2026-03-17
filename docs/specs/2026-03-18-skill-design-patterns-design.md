# Skill Design Patterns Integration

> **Status**: Reviewed
> **Date**: 2026-03-18
> **Source**: "5 Agent Skill design patterns every ADK developer should know" (Saboo_Shubham_, lavinigam)

## Goal

スキルシステムに設計パターン分類を導入し、新スキルの品質向上と既存スキルの可視化を実現する。

## Decisions

- **Approach A (Reference-First)** を採用: reference が single source of truth
- **品質軸の優先順位**: 構造 → 合成可能性 → トリガー精度
- **スコープ**: reference + skill-creator 改善 + 全スキル metadata 付与。構造リファクタリングは別タスク
- **skill-audit 改善は別タスク**に分離

## 5 Skill Design Patterns

| Pattern | Purpose | Key Structure |
|---------|---------|---------------|
| **Tool Wrapper** | ライブラリ/フレームワークの規約をオンデマンドでロード | キーワードトリガー → references/ ロード → 規約適用 |
| **Generator** | 定型出力をテンプレートから生成 | テンプレート + スタイルガイド → 変数収集 → テンプレート充填 |
| **Reviewer** | チェックリストに基づいてコードを評価 | チェックリストロード → 項目ごとに検査 → severity 分類 → スコア |
| **Inversion** | エージェントがユーザーにインタビューしてから行動 | フェーズ分け → 質問 → ゲート条件 → 合成 |
| **Pipeline** | 厳密な順序の多段ワークフロー | 番号付きステップ → 各ステップにゲート条件 → 失敗時中断 |

## Deliverables

### 1. `references/skill-patterns.md` (新規)

5パターンの定義ドキュメント。以下を含む:

**各パターンの定義** (Purpose, When to use, Key structure, Required elements, Gate conditions, Composability)

**Decision Tree**:
```
スキルの主目的は？
├─ 知識を適用 → Tool Wrapper
├─ 定型出力を生成 → Generator
├─ コードを評価 → Reviewer
├─ 要件を収集してから行動 → Inversion
└─ 複数ステップを順序保証 → Pipeline
```

**合成パターン**:
- Inversion + Generator: 要件収集 → テンプレート出力 (例: /spec, /timekeeper)
- Pipeline + Reviewer: 多段処理の最終ステップで品質チェック (例: /epd)
- Tool Wrapper + Reviewer: 規約ロード → 規約に基づくレビュー (例: /review + review-checklists/)

**構造品質チェックリスト** (パターン別の必須要素):

| Pattern | Required Elements |
|---------|-------------------|
| Tool Wrapper | references/ 内のドキュメント、キーワードトリガー |
| Generator | テンプレート (assets/ or inline)、出力フォーマット定義 |
| Reviewer | references/ 内のチェックリスト、severity 分類 |
| Inversion | フェーズ分け、ゲート条件 ("DO NOT proceed until...") |
| Pipeline | 番号付きステップ、各ステップのゲート条件、失敗時の挙動 |

### 2. `skill-creator/SKILL.md` 改修

**Stage 1.5 — Pattern Selection** を Capture Intent の直後に追加:

1. `references/skill-patterns.md` の Decision Tree をロード
2. Stage 1 の回答から最適パターンを推奨
3. ユーザーに確認（合成パターンも提案）
4. 選択されたパターンの必須要素チェックリストを以降のステージに引き継ぐ

**Stage 4 (Write SKILL.md) への影響**:
- frontmatter に `metadata.pattern` を自動追加
- 選択パターンの必須要素をスキャフォールド (Pipeline なら `## Step N —` テンプレート等)
- 合成パターンは `metadata.pattern: inversion+generator` と表記

**Stage 6 (Test) への影響**:
- パターンの必須要素が実際に存在するかを検証に追加

**frontmatter 追加フィールド**:
```yaml
metadata:
  pattern: pipeline            # tool-wrapper | generator | reviewer | inversion | pipeline
  composable-with: [reviewer]  # 組み合わせ可能なパターン
```

**変更対象**: skill-creator の SKILL.md 内の指示テキスト + planning-guide.md のみ。スクリプト変更なし。

### 3. 全スキル metadata 付与

全スキルの SKILL.md frontmatter に `metadata.pattern` を追加（本体ロジック変更なし）。

**分類マッピング**:

| Skill | Pattern |
|-------|---------|
| check-health | reviewer |
| search-first | pipeline |
| review | reviewer |
| verification-before-completion | pipeline+reviewer |
| continuous-learning | pipeline |
| spec | inversion+generator |
| spike | pipeline |
| validate | reviewer |
| codex-review | reviewer |
| codex | tool-wrapper |
| gemini | tool-wrapper |
| research | pipeline |
| epd | pipeline |
| interviewing-issues | inversion |
| react-best-practices | tool-wrapper |
| react-expert | tool-wrapper |
| senior-frontend | tool-wrapper |
| senior-backend | tool-wrapper |
| senior-architect | tool-wrapper |
| graphql-expert | tool-wrapper |
| buf-protobuf | tool-wrapper |
| frontend-design | generator |
| ui-ux-pro-max | tool-wrapper+generator |
| autonomous | pipeline |
| improve | pipeline |
| skill-creator | pipeline+inversion |
| skill-audit | reviewer |
| eureka | generator |
| daily-report | generator |
| timekeeper | inversion+generator |
| digest | generator |
| edge-case-analysis | reviewer |
| github-pr | pipeline |
| create-pr-wait | pipeline |
| webapp-testing | tool-wrapper |
| init-project | pipeline+inversion |
| setup-background-agents | generator |
| ai-workflow-audit | reviewer |
| web-design-guidelines | reviewer |
| vercel-composition-patterns | tool-wrapper |
| absorb | pipeline |
| debate | pipeline |
| security-review | reviewer |
| obsidian-content | generator |
| obsidian-knowledge | tool-wrapper |
| obsidian-vault-setup | generator |
| fix-issue | pipeline |
| rpi | pipeline |
| checkpoint | generator |

> **Note**: 上記マッピングに含まれないスキル（Personal Ops 系等）は、実装時に Decision Tree に基づいて分類する。

### 4. `skill-inventory.md` 更新

既存の5ティア分類テーブルの各行に `Pattern` 列を追加。

## Out of Scope

- 既存スキルの構造リファクタリング (別タスク — metadata から改善優先度を判断可能になる)
- skill-audit へのパターン品質チェック追加 (別タスク)
- `/improve --evolve` へのパターン情報統合 (別タスク)

## Acceptance Criteria

1. `references/skill-patterns.md` が存在し、5パターン + Decision Tree + 合成例 + 品質チェックリストを含む
2. `skill-creator/SKILL.md` に Pattern Selection ステージが追加されている
3. 全スキル (30+) の frontmatter に `metadata.pattern` が付与されている
4. `skill-inventory.md` にパターン列が追加されている
5. 既存スキルの本体ロジックは変更されていない
