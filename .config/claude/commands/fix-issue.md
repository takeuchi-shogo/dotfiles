---
allowed-tools: Bash(gh issue *), Bash(gh pr *), Bash(gh repo view *), Bash(git *), Bash(npm test *), Bash(go test *), Bash(pnpm test *), Bash(bun test *)
argument-hint: <issue-number> [--repo owner/repo]
description: GitHub Issue を起点にした自動修正ワークフロー
---

# Fix GitHub Issue

Fix issue: $ARGUMENTS

## Issue Details

- Repository: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown"`
- Current branch: !`git branch --show-current`
- Default branch: !`gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main"`

## Workflow

### 1. Issue 取得

`gh issue view <issue-number>` で Issue の内容を取得する。
`--repo` が指定されていればそのリポジトリの Issue を取得する。

### 2. 関連ファイル特定

Issue のタイトル・本文からキーワードを抽出し、Grep/Glob で関連ファイルを特定する。
- エラーメッセージがあればコード内を検索
- ファイルパスが言及されていればそのファイルを確認
- 機能名・コンポーネント名から関連コードを探す

### 3. ブランチ作成

`fix/issue-<N>` 形式の新しいブランチを作成する:
```
git switch -c fix/issue-<N>
```

### 4. 修正計画

Plan Mode に入って修正計画を立てる:
- 根本原因の特定
- 修正方針の決定
- 影響範囲の確認

### 5. 実装

計画に従って最小限の修正を実装する。
- 既存パターンに従う
- テストがあればテストも修正・追加

### 6. テスト実行

プロジェクトのテストコマンドを実行して検証する:
- `package.json` の test スクリプト
- Go プロジェクトなら `go test ./...`
- テストがなければスキップ（その旨を伝える）

### 7. コミット

`/commit` の規約に従ってコミットする:
- メッセージに Issue 番号を含める（例: `🐛 fix: resolve rendering issue (#447)`）
- fix/feat 等の適切な type を選択

### 8. PR 作成

`/pull-request` の規約に従って PR を作成する:
- PR 本文に `Fixes #<N>` を含めて Issue を自動クローズ
- `--repo` が指定されていれば `gh pr create --repo owner/repo` を使用する
- 修正内容の要約を記述

## Important

- Issue が見つからない場合はエラーを報告して終了
- 修正が複雑すぎる場合は計画段階でユーザーに相談
- セキュリティ関連の Issue は特に慎重に対応
