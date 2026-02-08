---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
argument-hint: [message] | --amend | --no-verify
description: Create well-formatted commits with conventional commit format and emoji
---

# Smart Git Commit

Create well-formatted commit: $ARGUMENTS

## Current Repository State

- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Staged changes: !`git diff --cached --stat`
- Unstaged changes: !`git diff --stat`
- Recent commits: !`git log --oneline -5`

## What This Command Does

1. プロジェクトに lint/test コマンドがあれば実行して品質を確認
2. `git status` でステージ済みファイルを確認
3. ステージ済みファイルが0件なら、変更・新規ファイルを `git add`
4. `git diff` で変更内容を分析
5. 複数の論理的変更がある場合、コミット分割を提案
6. 絵文字付き conventional commit 形式でコミットメッセージを作成

## Conventional Commit Format

`<emoji> <type>: <description>` — 1行目は72文字以内、現在形・命令形で記述。

### 頻出絵文字

| Emoji | Type | 用途 |
|-------|------|------|
| ✨ | feat | 新機能 |
| 🐛 | fix | バグ修正 |
| 📝 | docs | ドキュメント |
| 💄 | style | フォーマット・スタイル |
| ♻️ | refactor | リファクタリング |
| ⚡️ | perf | パフォーマンス改善 |
| ✅ | test | テスト追加・修正 |
| 🔧 | chore | ツール・設定変更 |
| 🚀 | ci | CI/CD 改善 |
| ⏪️ | revert | 変更の取り消し |
| 🔒️ | fix | セキュリティ修正 |
| 🔥 | fix | コード・ファイル削除 |
| 💥 | feat | 破壊的変更 |
| 🏷️ | feat | 型定義の追加・更新 |
| 🚑️ | fix | クリティカルな修正 |

## Guidelines for Splitting Commits

以下に該当する場合、コミットの分割を提案する:

1. **異なる関心事**: コードベースの無関係な部分への変更
2. **異なる変更タイプ**: feat, fix, refactor 等の混在
3. **ファイルパターン**: ソースコードとドキュメント等、異なる種類のファイル

## Examples

Good commit messages:
- ✨ feat: add user authentication system
- 🐛 fix: resolve memory leak in rendering process
- 📝 docs: update API documentation with new endpoints
- ♻️ refactor: simplify error handling logic in parser

Splitting example:
- First: ✨ feat: add new type definitions
- Second: 📝 docs: update documentation for new features
- Third: ✅ test: add unit tests for new features
