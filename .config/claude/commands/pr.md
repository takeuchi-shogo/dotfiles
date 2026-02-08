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

1. 現在のブランチのコミット履歴と差分を分析
2. コミット内容に基づいて PR タイトルと本文を自動生成
3. base branch はデフォルトで `main`、引数で変更可（例: `/pr develop`）
4. リモートにプッシュされていなければ `git push -u` を実行
5. `gh pr create` で PR を作成

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
