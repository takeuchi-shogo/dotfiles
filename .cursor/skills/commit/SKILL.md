---
name: commit
description: 変更を分析し conventional commit + 絵文字プレフィックスでコミットする。コミット前に lint/test の通過を確認する。
---

# Commit Skill

## When to Use

- コード変更をコミットする時
- 適切なコミットメッセージを生成したい時

## 型の正本（コピーしない）

件名・本文の型は **`$pr-issue-style`**（`.agents/skills/pr-issue-style/templates/commit-message.txt`）に従う。

- 命令形・末尾句点なし・実在のシンボル名を入れる
- 本文は subject の言い換えにしない（why だけ）
- `git commit`（`-m` なし）なら `commit.template` が同じひな形を開く

この repo の絵文字 + conventional (`✨ feat:` 等）は **残す**（型の Conventional Commits 行と両立）。

## Workflow

1. `git diff --staged` で staged の変更を確認。なければ `git status` で unstaged を表示
2. 変更の性質を判定:
   - `✨ feat:` — 新機能
   - `🐛 fix:` — バグ修正
   - `📝 docs:` — ドキュメント
   - `♻️ refactor:` — リファクタリング
   - `🔧 chore:` — 雑務
   - `🧪 test:` — テスト
   - `🎨 style:` — フォーマット
   - `⚡ perf:` — パフォーマンス
3. lint/test を実行して通過を確認
4. コミットメッセージを生成:
   - 1行目: `emoji type(scope): summary` (72文字以内・命令形・末尾句点なし)
   - 空行
   - 本文: なぜこの変更が必要か（what ではなく why）。subject を繰り返さない
5. `git commit` を実行

## Rules

- `--no-verify` 禁止
- 機密ファイル（.env, credentials 等）をコミットしない
- 1コミット = 1目的（狭いコミットを優先。巨大な1本にしない）
