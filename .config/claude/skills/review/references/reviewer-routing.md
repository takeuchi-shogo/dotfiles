# Reviewer Routing Reference

レビューアーの詳細仕様。SKILL.md の Step 3 (Dispatch) で参照する。

## コアレビューアー（常時起動候補）

### code-reviewer

- **subagent_type**: `code-reviewer`
- **観点**: コード品質、バグ検出、CLAUDE.md 準拠、設計パターン
- **起動条件**: 50行以上の変更で常に起動
- **信頼度スコア**: 80以上の指摘のみ報告

### 言語専門レビューアー

| subagent_type      | 対象拡張子                   | 専門観点                                           |
| ------------------ | ---------------------------- | -------------------------------------------------- |
| `code-reviewer-ts` | `.ts`, `.tsx`, `.js`, `.jsx` | 型安全性、React パターン、Node.js サーバーサイド   |
| `code-reviewer-go` | `.go`                        | Effective Go、エラーハンドリング、並行処理パターン |
| `code-reviewer-py` | `.py`                        | 型ヒント、Pythonic イディオム、例外設計            |
| `code-reviewer-rs` | `.rs`                        | 所有権、ライフタイム、Result/Option、unsafe 最小化 |

- **起動条件**: 50行以上の変更で、該当拡張子のファイルが含まれる場合
- **複数言語**: 変更ファイルに複数言語が含まれる場合、該当する全レビューアーを起動

### codex-reviewer

- **subagent_type**: `codex-reviewer`
- **観点**: Codex (gpt-5.4) による深い推論ベースのセカンドオピニオン
- **起動条件**: 100行以上の変更
- **特記**: `/codex-review` スキルとは別。こちらは Agent として並列起動される

### code-reviewer-ma / code-reviewer-mu

- **subagent_type**: `code-reviewer-ma`（簡潔・直接的）/ `code-reviewer-mu`（丁寧・教育的）
- **観点**: 異なるレビュースタイルによる多角的評価
- **起動条件**: 200行以上の変更
- **使い分け**: 200行前後は ma or mu のどちらか1つ、200行超は両方

## スペシャリストレビューアー（コンテンツベースで追加）

### silent-failure-hunter

- **subagent_type**: `silent-failure-hunter`
- **観点**: サイレント障害、エラー握り潰し、不適切な fallback
- **トリガー**: diff に `catch`, `recover`, `fallback`, `retry`, `on.*[Ee]rror`, `try {` が含まれる
- **重要度**: CRITICAL（silent failure）, HIGH（poor messages）, MEDIUM（missing context）

### type-design-analyzer

- **subagent_type**: `type-design-analyzer`
- **観点**: 型のカプセル化、不変条件の表現、型安全性
- **トリガー**: diff の追加行に `type `, `interface `, `struct `, `enum ` が含まれる
- **評価軸**: カプセル化(1-10), 不変条件表現(1-10), 有用性(1-10), 強制力(1-10)

### pr-test-analyzer

- **subagent_type**: `pr-test-analyzer`
- **観点**: テストカバレッジの質、エッジケースの網羅性
- **トリガー**: `_test.go`, `.test.ts`, `.spec.ts`, `__tests__/` のファイルが変更されている
- **評価**: 行カバレッジではなく振る舞いカバレッジを重視

### comment-analyzer

- **subagent_type**: `comment-analyzer`
- **観点**: コメント・ドキュメントの正確性、完全性、長期保守性
- **トリガー**: `/** */`, `///`, `# ` 等のコメントブロックが10行以上追加されている
- **検出対象**: コメント腐敗、WHY の欠落、不正確な記述

## Agent プロンプトテンプレート

各レビューアーへ渡すプロンプトの基本構造:

```
以下のコード変更をレビューしてください。

## 変更対象
{git diff --name-only の結果}

## 差分
{git diff の結果}

## プロジェクト規約
{CLAUDE.md の内容（存在する場合）}

重要度の高い指摘のみ報告してください。
ファイルパス:行番号 の形式で具体的な場所を示してください。
```
