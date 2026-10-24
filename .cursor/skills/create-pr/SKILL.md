---
name: create-pr
description: ブランチの全コミットを分析し、タイトル・本文・テストプランを自動生成して PR を作成する。
---

# Create PR Skill

## When to Use

- 機能実装が完了し PR を作成する時
- ブランチの変更をまとめてレビューに出す時

## 型の正本（コピーしない）

PR タイトル・本文・分け方は **`$pr-issue-style`**（`.agents/skills/pr-issue-style/`）に従う。

- 読む: `.agents/skills/pr-issue-style/SKILL.md`
- 小さい PR: `templates/pr-body-small.md`（見出しなし・3文）
- 中〜大 PR: `templates/pr-body-medium.md`（Why / What changed / Scope / Blast Radius / Verification）
- タイトル: `templates/pr-title.md` / 分け方: `templates/pr-split.md`

旧フォーマット（Summary / Test Plan）は使わない。Verification に実際に動かしたコマンドと結果を書く。

## Workflow

1. 状態確認:
   - `git status` で未コミットの変更がないか確認
   - `git log main..HEAD --oneline` で全コミットを把握
   - `git diff main..HEAD --stat` で変更ファイル一覧
2. 規模判定と本文生成:
   - **タイトル**: `pr-title.md` に従う（50字目安・命令形・末尾句点なし）
   - **小さい**: `pr-body-small.md` の3文
   - **中〜大**: `pr-body-medium.md`（空見出しは削る・40行以内）
3. リモートにプッシュ（必要なら）: `git push -u origin HEAD`
4. PR 作成（本文は型に合わせる）。素のシェルなら `ghpr small` / `ghpr medium` も可:
   ```
   gh pr create --title "title" --body-file path/to/filled-body.md
   ```
5. PR URL を返す
