# Reviewer Routing Reference

レビューアーの詳細仕様。SKILL.md の Step 3 (Dispatch) で参照する。

## コアレビューアー（常時起動候補）

### code-reviewer

- **subagent_type**: `code-reviewer`
- **観点**: コード品質、バグ検出、CLAUDE.md 準拠、設計パターン
- **起動条件**: 50行以上の変更で常に起動
- **信頼度スコア**: 80以上の指摘のみ報告

### 言語固有チェックリスト（code-reviewer に注入）

言語専門の観点は独立エージェントではなく、`code-reviewer` のプロンプトにチェックリストを注入して適用する。

| 対象拡張子                   | 参照ファイル                                 | 専門観点                                           |
| ---------------------------- | -------------------------------------------- | -------------------------------------------------- |
| `.ts`, `.tsx`, `.js`, `.jsx` | `references/review-checklists/typescript.md` | 型安全性、React パターン、Node.js サーバーサイド   |
| `.go`                        | `references/review-checklists/go.md`         | Effective Go、エラーハンドリング、並行処理パターン |
| `.py`                        | `references/review-checklists/python.md`     | 型ヒント、Pythonic イディオム、例外設計            |
| `.rs`                        | `references/review-checklists/rust.md`       | 所有権、ライフタイム、Result/Option、unsafe 最小化 |

- **注入方法**: code-reviewer のプロンプトに該当チェックリストの内容を Read して含める
- **複数言語**: 変更ファイルに複数言語が含まれる場合、該当する全チェックリストを注入

### codex-reviewer

- **subagent_type**: `codex-reviewer`
- **観点**: Codex (gpt-5.4) による深い推論ベースのセカンドオピニオン
- **起動条件**: 50行以上の変更（code-reviewer と同時起動）
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

### nil-path-reviewer

- **subagent_type**: `general-purpose`（専用エージェントではなく汎用エージェントに専用プロンプトを渡す）
- **観点**: nil/zero パスの安全性、ポインタ dereference の防御、暗黙の前提の検出
- **トリガー**: diff の追加/変更行に以下が含まれる場合:
  - Go: ポインタ型フィールド (`*`), `nil`, `.Get()`, `option.Option`, `option.Some`, `option.None`
  - TypeScript: `undefined`, `null`, optional chaining (`?.`), non-null assertion (`!.`)
- **プロンプト**: 以下を含めること:

  ```
  コード変更に含まれるポインタ型・Option 型・nullable フィールドについて、
  以下の観点でレビューしてください:

  1. nil/undefined になりうるフィールドが dereference される箇所に防御があるか
  2. 下流の関数に nil が渡された場合に panic/crash しないか（データフロー追跡）
  3. 「呼び出し側が nil を渡さないはず」という暗黙の前提がないか
  4. Option 型の .Get() が ok チェックなしで使われていないか
  5. テストで nil/zero ケースがカバーされているか

  重要度の高い指摘のみ報告してください。
  ```

- **重要度**: CRITICAL（nil dereference で panic 可能）, HIGH（暗黙の前提に依存）, MEDIUM（テスト欠落）

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

## 信頼度スコアリング

全レビューアーは各指摘に **confidence score (0-100)** を付与する。

### スコア基準

| スコア | 基準                                              |
| ------ | ------------------------------------------------- |
| 90-100 | 確実にバグ/セキュリティ問題。コードパスで再現可能 |
| 80-89  | 高確率で問題。エッジケースや暗黙の前提に基づく    |
| 60-79  | 中程度。パターン的に問題になりやすいが確証なし    |
| 40-59  | 低確度。スタイルや好みの範囲                      |
| 0-39   | 推測レベル。根拠が薄い                            |

### フィルタリングルール

以下の指摘は **自動除外** する（レポートに含めない）:

1. **confidence < 80** の指摘
2. **既存コードの問題**（diff の追加行以外への指摘）
3. **linter/formatter が検出すべき問題**（インデント、セミコロン等）
4. **純粋なスタイル nitpick**（命名規則の好み等、CLAUDE.md に明記がない限り）

### プロンプトへの追記

各レビューアーへのプロンプトに以下を追加:

```
各指摘には confidence score (0-100) を付与してください。
80未満の指摘は報告不要です。
既存コード（diff の追加行以外）への指摘は除外してください。
linter/formatter が検出すべき問題は除外してください。

フォーマット例:
- [95] `file.ts:42` — NullPointerException の可能性。`user` が undefined の場合に crash
- [82] `api.go:128` — エラーが握り潰されている。`err` を返すべき
```
