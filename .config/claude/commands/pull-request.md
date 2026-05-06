---
allowed-tools: Bash(gh pr *), Bash(git log *), Bash(git diff *), Bash(git branch *), Bash(git push *)
argument-hint: [base-branch]
description: Create a Pull Request with auto-generated title and body
---

# Smart Pull Request

Create a Pull Request: $ARGUMENTS

## Current Repository State

- Current branch: !`git branch --show-current`
- Remote tracking: !`git status -sb | head -1`
- Recent commits: !`git log --oneline -10`
- Changed files vs main: !`git diff main...HEAD --stat 2>/dev/null || git diff master...HEAD --stat`

## What This Command Does

1. **Pre-PR Chain Check** — 既存 PR / template / draft 判定（下記 Step 0）
2. 現在のブランチのコミット履歴と差分を分析
3. コミット内容に基づいて PR タイトルと本文を自動生成
4. base branch はデフォルトで `main`、引数で変更可（例: `/pr develop`）
5. リモートにプッシュされていなければ `git push -u` を実行
6. `gh pr create` で PR を作成

## Step 0: Pre-PR Chain Check

> 出典: Warp `oz-skills/create-pull-request` (2026-05-06 absorb)。`gh pr create` 直前に実行する 4 点チェック。

PR を作成する前に **必ず** 以下を確認する。失敗時は対応コマンドへ誘導する。

### 0-1. 既存 PR の検出

```bash
# 同じブランチの open PR がないか確認
gh pr view --json number,url,state 2>/dev/null
```

- 既に open な PR がある → `gh pr edit` で本文/タイトルを更新する案内に切り替え（重複 PR は作らない）
- closed / merged な過去 PR は新規作成 OK だが、ユーザに「過去 PR #N があった」と通知

### 0-2. PR template の検出と反映

```bash
# テンプレート存在確認
ls .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE/*.md 2>/dev/null
```

- 存在する → テンプレートの構造を **必ず本文に反映**（独自フォーマットで上書きしない）
- 複数 template がある → ユーザに choice を提示（`AskUserQuestion`）

### 0-3. Pre-PR skill chain（必要に応じて推奨）

PR 作成前に以下のいずれかが未実行と判断したら **実行を提案**（強制ではない）:

| 状況 | 推奨スキル | 判断根拠 |
|------|----------|---------|
| 直近コミットでコード変更あり、レビュー未実施 | `/review` | git diff `main...HEAD` で 50 行超の変更 |
| CI 設定変更を含む | `/gh-fix-ci` 事前確認 + `references/ci-fix-policy.md` 一読 | `.github/workflows/` に diff |
| テストが不足 | `test-engineer` agent / 既存 test framework | source diff に対して test diff が著しく少ない |
| breaking change の可能性 | `/spec` または migration note 追記 | export 削除、API signature 変更 |

ユーザが「すぐに作りたい」と明示した場合はスキップして次に進む。

### 0-4. Draft 判定

以下のいずれかに該当する → `--draft` フラグを **強く推奨**:

- WIP commit が含まれる（`wip:`, `tmp:`, `[WIP]` 等）
- 自己レビュー未完了
- CI が green でない（`gh pr checks` 結果）
- TODO / FIXME コメントが diff に含まれる

判断後 `gh pr create [--draft]` を実行する。

## PR Format

### タイトル
- 70文字以内
- 変更の要約を簡潔に記述

### 本文
```markdown
## Summary
- 変更の概要を箇条書き（1-3項目）

## Test plan
- [ ] テスト項目のチェックリスト
```

## Guidelines

- コミットが1つの場合: コミットメッセージをベースにタイトル生成
- コミットが複数の場合: 全コミットを総合してタイトル生成
- Draft PR が適切な場合は `--draft` フラグを提案
- PR 作成後は URL を表示
