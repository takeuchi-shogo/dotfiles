---
name: fix-issue
allowed-tools: Bash(gh issue *), Bash(gh pr *), Bash(gh repo view *), Bash(git *), Bash(npm test *), Bash(go test *), Bash(pnpm test *), Bash(bun test *)
argument-hint: <issue-number> [--repo owner/repo]
description: >
  GitHub Issue を起点にした自動修正ワークフロー。Issue の内容を読み取り、修正を実装してテストする。
  Triggers: 'fix-issue', 'Issue 修正', 'fix #', 'Issue を直して', 'bug fix from issue'.
  Do NOT use for: Issue 作成（use /create-issue）、Issue の明確化（use /interviewing-issues）、手動実装（use /rpi）。
origin: self
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

### 4. Reproduce First

**修正計画の前に、まず再現すること。** 「attestation is scarce」原則 — 再現できないバグを修正してはいけない。

- 失敗ケースを最小単位で再現する手順を確立する（コマンド・入力・環境）
- 可能なら failing test を先に書く（TDD: red → green）
- 再現ログ・スタックトレース・出力を Issue または作業メモに記録する
- 「再現できた」を確認してから次へ進む

**再現できない場合は修正に進まない**:
- 環境差・タイミング・前提条件のいずれが原因か切り分ける
- Issue 起票者に追加情報を求める、または stop して re-scope する
- 「動いてしまった」修正は attestation がないので merge 不可

### 5. 修正計画

Plan Mode に入って修正計画を立てる:
- 根本原因の特定（Step 4 の再現結果から導く）
- 修正方針の決定
- 影響範囲の確認

### 6. 実装

計画に従って最小限の修正を実装する。
- 既存パターンに従う
- テストがあればテストも修正・追加

### 7. テスト実行

プロジェクトのテストコマンドを実行して検証する:
- `package.json` の test スクリプト
- Go プロジェクトなら `go test ./...`
- Step 4 で書いた failing test が green になることを確認
- テストがなければスキップ（その旨を伝える）

### 8. コミット

`/commit` の規約に従ってコミットする:
- メッセージに Issue 番号を含める（例: `🐛 fix: resolve rendering issue (#447)`）
- fix/feat 等の適切な type を選択

### 9. PR 作成

`/pull-request` の規約に従って PR を作成する:
- PR 本文に `Fixes #<N>` を含めて Issue を自動クローズ
- `--repo` が指定されていれば `gh pr create --repo owner/repo` を使用する
- 修正内容の要約を記述

## Important

- Issue が見つからない場合はエラーを報告して終了
- 修正が複雑すぎる場合は計画段階でユーザーに相談
- セキュリティ関連の Issue は特に慎重に対応
- **再現できなければ修正しない**: Step 4 で再現できない場合は stop し、re-scope または起票者へ確認。"動いてしまった" 修正は attestation がないため merge 不可
