---
allowed-tools: Bash(git diff *), Bash(git log *), Bash(git status *), Bash(gh repo view *)
argument-hint: "[mode: elegant|grill|prove]"
description: 直前の変更を分析し、エレガント版の再設計・厳しいレビュー・差分実証を行う
---

# Challenge Mode

Mode: $ARGUMENTS

## Recent Changes

- Last commit diff: !`git diff HEAD~1 --stat 2>/dev/null || echo "No previous commit"`
- Unstaged changes: !`git diff --stat`
- Staged changes: !`git diff --cached --stat`

## Modes

### `elegant` (デフォルト — 引数なしの場合もこのモード)

**「全部理解した上で、スクラップして洗練版を作り直せ」**

1. 直前の変更（`git diff HEAD~1` または unstaged diff）を完全に読み込む
2. 変更の意図・目的を要約する
3. 以下の観点で分析:
   - 不要な複雑さはないか
   - より直接的な解法はないか
   - 既存のライブラリ・パターンで代替できないか
   - エッジケースの見落としはないか
4. **改善版の設計**を提案する（コードは書かない）
5. ユーザーが承認したら実装に移る

### `grill`

**「この変更を防御してみろ」**

直前の変更に対して厳しいレビュー質問をする:

1. 変更内容を読み込む
2. 以下の観点で質問を生成:
   - なぜこのアプローチを選んだのか？代替案は検討したか？
   - この変更が壊しうるシナリオは？
   - パフォーマンスへの影響は？
   - 半年後のメンテナビリティは？
   - テストは十分か？境界値は？
3. 5-7個の質問をユーザーに投げかける
4. ユーザーの回答に基づいてフォローアップ

### `prove`

**「main との差分を実証しろ」**

1. `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` でデフォルトブランチを取得し、`git diff <default-branch>...HEAD` で差分を取得
2. 変更前後の動作の違いを具体的に列挙:
   - 入力 X に対して、Before: Y → After: Z
   - 新しいエラーハンドリング
   - パフォーマンス特性の変化
3. テストがあれば実行して結果を示す
4. テストがなければ、検証すべきシナリオを提案

## Important

- このコマンドは読み取り・分析のみ。コードの変更はユーザーの明示的な承認後に行う
- `elegant` モードで改善版を実装する場合は、ユーザーの許可を得てから
- 変更がない場合（clean working tree + HEAD commit なし）はその旨を伝えて終了
