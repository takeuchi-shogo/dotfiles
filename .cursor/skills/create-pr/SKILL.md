---
name: create-pr
description: ブランチの全コミットを分析し、タイトル・本文・テストプランを自動生成して PR を作成する。
---

# Create PR Skill

## When to Use

- 機能実装が完了し PR を作成する時
- ブランチの変更をまとめてレビューに出す時

## Workflow

1. 状態確認:
   - `git status` で未コミットの変更がないか確認
   - `git log main..HEAD --oneline` で全コミットを把握
   - `git diff main..HEAD --stat` で変更ファイル一覧
2. PR 情報を生成:
   - **タイトル**: 70文字以内、変更の目的を簡潔に
   - **Summary**: 1-3 bullet points で主要な変更を説明
   - **Test Plan**: テスト手順のチェックリスト
3. リモートにプッシュ（必要なら）: `git push -u origin HEAD`
4. PR 作成:
   ```
   gh pr create --title "title" --body "## Summary
   - Change 1

   ## Test Plan
   - [ ] Test step 1"
   ```
5. PR URL を返す
