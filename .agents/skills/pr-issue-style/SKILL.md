---
name: pr-issue-style
description: >
  PR・Issue・コミット・レビューコメントの共通の型（Lauren Tan / pstack 由来）。
  Triggers: 'PR 書く', 'Issue 書く', 'PR 本文', 'create PR', 'gh pr create',
  'コミットメッセージの型', 'レビューコメントの型'.
  Do NOT use for: 実装そのもの、CI 修正、コードレビュー本体（use /review）。
platforms: [agents, codex]
---

# PR・Issue の型

ツール非依存の正本。Cursor / Claude Code / Codex / 素の `git`・`gh` は **ここを参照する**（文言をコピーしない）。

出典の要約と数値メモは `references/source-notes.md`。穴埋め用の文言は `templates/`。

## いつ読むか

- PR タイトル・本文を書くとき
- Issue（上流バグ報告 / TODO リスト）を書くとき
- コミット件名を整えるとき
- レビューコメントや Issue への定型返信を書くとき

## 使い方（エージェント）

1. 変更規模を判定する: **小さい**（〜100行・意図が1つ）か **中〜大**か。
2. 該当テンプレートを読む（コピーせず、パスを開く）:
   - 小さい PR 本文 → `templates/pr-body-small.md`
   - 中〜大 PR 本文 → `templates/pr-body-medium.md`
   - タイトル / 分け方 → `templates/pr-title.md` / `templates/pr-split.md`
   - Revert → `templates/revert.md`
   - 上流バグ Issue → `templates/issue-bug.md`
   - TODO Issue → `templates/issue-todo.md`
   - 定型返信 → `templates/issue-replies.md`
   - レビュー → `templates/review-comments.md`
   - コミット件名の型 → `templates/commit-message.txt`
3. 空の見出しは削る。ログ・SHA一覧・表は貼らずリンクにする。40行以内を目安にする。

## 使い方（人間・素の git / gh）

- コミット: `git commit`（`-m` なし）で `commit.template` が開く（`.config/git/config` → 本 skill の `templates/commit-message.txt`）。
- PR: zsh の `ghpr small` / `ghpr medium`（`.config/zsh/functions/ghpr.zsh`）で本文ひな形を渡して `gh pr create` する。

## 既存ルールとの優先順位

この型を **PR/Issue 本文とタイトルの正本** とする。衝突時の扱い:

| 既存 | 残すもの | 型が上書きするもの |
|------|----------|-------------------|
| Cursor `create-pr` / Claude `/pull-request` の Summary・Test plan | Pre-PR チェック、draft 判定、既存 PR 検出 | 本文見出し → Why / What changed / Scope / Blast Radius / Verification（小は見出しなし3文） |
| Cursor `commit` / Claude `/commit` の conventional + 絵文字 | 絵文字プレフィックス、contextual action lines、`--no-verify` 禁止、1コミット1目的 | 件名は命令形・末尾句点なし・実在シンボル名。本文は subject の言い換えにしない |
| Claude `create-issue` の背景/要件型 | 機能要望の構造化フロー | 上流バグ報告は `templates/issue-bug.md` を使う |

## Anti-patterns

- ✗ この skill の文言を他 skill に全文コピーする → ✓ パス参照だけにする
- ✗ 巨大な1本の PR にリネーム・整形・機能を混ぜる → ✓ 狭い PR に分ける（`templates/pr-split.md`）
- ✗ Verification に「テスト済み」だけ書く → ✓ 実行したコマンドと結果を残す
