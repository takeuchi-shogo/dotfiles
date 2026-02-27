---
name: search-first
description: "Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Use when starting a new feature, adding a dependency, or before creating a new utility."
---

# /search-first — 実装前に検索する

既存の解決策を探してからコードを書くワークフロー。

## Trigger

以下の場合にこのスキルを使う:
- 新機能の実装を開始するとき
- 依存パッケージやインテグレーションを追加するとき
- 「X の機能を追加して」と言われ、コードを書こうとしているとき
- 新しいユーティリティ、ヘルパー、抽象化を作ろうとしているとき

## Workflow

```
1. NEED ANALYSIS（何が必要か）
   → 必要な機能を定義、言語/フレームワークの制約を特定

2. PARALLEL SEARCH（並列検索）
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ npm/PyPI/ │ │  既存の   │ │ GitHub/ │
   │ go pkg   │ │ スキル/MCP│ │   Web    │
   └──────────┘ └──────────┘ └──────────┘

3. EVALUATE（評価）
   → 機能適合度、メンテナンス状況、ライセンス、依存数

4. DECIDE（判断）
   ┌─────────┐  ┌──────────┐  ┌─────────┐
   │ そのまま │  │ ラップ/  │  │ 自作   │
   │  採用   │  │  拡張    │  │  実装   │
   └─────────┘  └──────────┘  └─────────┘

5. IMPLEMENT（実装）
   → パッケージインストール / MCP設定 / 最小限のカスタムコード
```

## Decision Matrix

| シグナル | アクション |
|---------|-----------|
| 完全一致、メンテ良好、MIT/Apache | **Adopt** — そのまま採用 |
| 部分一致、良い基盤 | **Extend** — 採用 + 薄いラッパー |
| 各候補が要件の一部しかカバーしない | **Compose** — 2-3個の小さなパッケージを組み合わせて完全カバー |
| 適切なものなし | **Build** — 自作。ただし調査結果を踏まえて |

## Quick Mode（インライン）

ユーティリティや機能を書く前に、頭の中でチェック:

1. よくある問題か？ → npm/PyPI/go pkg を検索
2. MCP サーバーがあるか？ → `settings.json` と MCP マーケットプレイスを確認
3. 既存のスキルがあるか？ → `~/.claude/skills/` を確認
4. GitHub テンプレートがあるか？ → GitHub を検索

## Full Mode（エージェント委譲）

非自明な機能の場合、汎用サブエージェント（Explore または general-purpose）に委譲する:

```
Task ツールで以下を指示:
  subagent_type: "Explore" (調査のみ) or "general-purpose" (調査+実装)

  プロンプト例:
  以下の機能について既存のツールを調査してください:
  機能: [DESCRIPTION]
  言語/フレームワーク: [LANG]
  制約: [ANY]

  検索対象: npm/PyPI/go pkg, MCP サーバー, Claude Code スキル, GitHub
  返却: 構造化された比較と推奨
```

## 技術スタック別の検索ショートカット

### TypeScript / Next.js
- バリデーション → `zod`, `valibot`
- HTTP クライアント → `ky`, `got`
- テスト → `vitest`, `jest`, `playwright`
- フォーマット → `prettier`, `biome`

### Go
- HTTP → `net/http`, `chi`, `echo`
- バリデーション → `validator`, `ozzo-validation`
- テスト → `testify`, `gomock`
- CLI → `cobra`, `urfave/cli`

### 共通
- Lint → `eslint`, `golangci-lint`, `ruff`
- Pre-commit → `husky`, `lint-staged`, `pre-commit`
- ドキュメント処理 → `unstructured`, `pdfplumber`

## Anti-Patterns

- **いきなりコードを書く**: 既存の解決策を確認せずにユーティリティを作成
- **MCP を無視する**: MCP サーバーが既に機能を提供しているか確認しない
- **過度なラッピング**: ライブラリを厚くラップしすぎて利点を失う
- **依存膨張**: 1つの小さな機能のために巨大なパッケージをインストール

## Examples

### Example 1: 「デッドリンクチェックを追加」
```
必要: Markdown ファイルのリンク切れチェック
検索: npm "markdown dead link checker"
発見: textlint-rule-no-dead-link (スコア: 9/10)
判断: ADOPT — npm install textlint-rule-no-dead-link
結果: カスタムコード 0行、実戦検証済みのソリューション
```

### Example 2: 「設定ファイルバリデータを追加」
```
必要: プロジェクト設定ファイルのスキーマ検証
検索: npm "config linter schema", "json schema validator cli"
発見: ajv-cli (スコア: 8/10)
判断: ADOPT + EXTEND — ajv-cli + プロジェクト固有スキーマ
結果: 1パッケージ + 1スキーマファイル、カスタムバリデーションロジック不要
```
