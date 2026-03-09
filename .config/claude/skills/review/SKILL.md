---
name: review
description: コード変更のレビューを実行。変更規模に応じてレビューアーを自動選択・並列起動し、結果を統合する。コード変更後の Review 段階で使用、または /review で手動起動。
allowed-tools: Read, Bash, Grep, Glob, Agent
---

# Code Review Orchestrator

コード変更に対して、適切なレビューアーを自動選択・並列起動し、結果を統合するオーケストレーター。

## Workflow

```
1. Pre-analysis  → git diff で変更を分析
2. Scaling       → 行数・内容からレビュアー構成を決定
3. Dispatch      → Agent ツールで1メッセージに並列起動
4. Synthesis     → 結果を統合し templates/review-output.md 形式で出力
```

## Step 1: Pre-analysis

```bash
git diff --stat HEAD
git diff --name-only HEAD
```

以下を特定する:

- **変更行数**: insertions + deletions の合計
- **言語**: 変更ファイルの拡張子
- **コンテンツシグナル**: diff 内容からスペシャリストの必要性を判定

## Step 2: Scaling Decision

### レビュアー構成（行数ベース）

| 変更規模 | 構成                                                                                              |
| -------- | ------------------------------------------------------------------------------------------------- |
| ~10行    | レビュー省略（Verify のみ）                                                                       |
| ~50行    | `code-reviewer` + 言語専門（2並列）                                                               |
| ~100行   | `code-reviewer` + 言語専門 + `codex-reviewer`（3並列）                                            |
| ~200行   | `code-reviewer` + 言語専門 + `codex-reviewer` + `code-reviewer-ma` or `code-reviewer-mu`（4並列） |
| 200行超  | `code-reviewer` + 言語専門 + `codex-reviewer` + `ma` + `mu`（5並列）+ スペシャリスト              |

### 言語専門レビューアー（拡張子で自動選択）

| 拡張子              | レビューアー                 |
| ------------------- | ---------------------------- |
| `.ts/.tsx/.js/.jsx` | `code-reviewer-ts`           |
| `.go`               | `code-reviewer-go`           |
| `.py`               | `code-reviewer-py`           |
| `.rs`               | `code-reviewer-rs`           |
| 複数言語混在        | 該当する全レビューアーを起動 |

### コンテンツベースのスペシャリスト自動検出

行数に関係なく、diff の内容にマッチするスペシャリストを追加する。
ただし **50行以上の変更** でのみ適用（10行以下はレビュー自体を省略）。

| diff 内のシグナル    | スペシャリスト          | 検出パターン                                                    |
| -------------------- | ----------------------- | --------------------------------------------------------------- |
| エラーハンドリング   | `silent-failure-hunter` | `catch`, `recover`, `fallback`, `retry`, `on.*error`, `try {`   |
| 新しい型定義         | `type-design-analyzer`  | `type `, `interface `, `struct `, `enum ` の追加行              |
| テスト変更           | `pr-test-analyzer`      | `_test.go`, `.test.ts`, `.spec.ts`, `__tests__/` のファイル変更 |
| コメント大量変更     | `comment-analyzer`      | `/** */`, `///`, `# ` のブロック追加（10行以上）                |
| nil/ポインタ操作     | `nil-path-reviewer`     | `*`, `nil`, `Option`, `.Get()`, ポインタ型フィールドの追加/変更 |

## Step 3: Dispatch

**Agent ツールで1メッセージに全レビューアーを並列起動する。**

各エージェントへのプロンプトには以下を含める:

- レビュー対象の git diff
- 変更ファイルのパス一覧
- プロジェクトの CLAUDE.md（存在する場合）

詳細なルーティング情報は `references/reviewer-routing.md` を参照。

## Step 4: Synthesis

全レビューアーの結果を `templates/review-output.md` のフォーマットに従って統合する。

統合ルール:

1. **重複排除**: 同じファイル・行への指摘が複数ある場合、最も具体的なものを残す
2. **重要度順**: Critical → Important → Suggestion の順に整理
3. **アクション明示**: 各指摘に対して「修正必須」「検討推奨」「参考」を付与
4. **判定**: 全体として修正が必要かどうかを明示する

## Anti-Patterns

- レビューアーを直接 Skill ツールで起動する（Agent ツールで並列起動すること）
- 行数だけでスペシャリストを判断する（コンテンツシグナルも見ること）
- レビュー結果をそのまま列挙する（統合・重複排除すること）
- 10行以下の変更に対してフルレビューを実行する
