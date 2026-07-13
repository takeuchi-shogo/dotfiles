---
name: note
description: "セッション中の知見を Obsidian Vault の Inbox に即時保存する。Triggers: '/note 内容'. Do NOT use for: ナレッジ整理 (use obsidian-knowledge)."
origin: self
metadata:
  pattern: action
argument-hint: "<保存したい内容>"
---

# Note to Vault

セッション中に残したい知見・メモを Obsidian Vault の 00-Inbox/ に即座に書き出す。

## 処理手順

1. 引数テキストを受け取る
2. **分類 (未整理テキストのみ)**: テキストが複数の論点を含む・思いつきの羅列である場合、保存前に以下の見出しで整形する。該当のないカテゴリは省略。短い単一メモはそのまま (整形しない):
   - `## 事実` — 観察した事実・確認済みのこと
   - `## 解釈` — 自分/セッションの解釈
   - `## 未検証の仮説` — まだ確かめていない推測
   - `## アイデア` — 次にやる・作る候補
   - `## 矛盾・違和感` — 前後で食い違う点、引っかかり
3. Bash で `note-to-vault.sh` を実行する:

```bash
~/.config/claude/scripts/runtime/note-to-vault.sh '整形済みテキスト'
```

4. 保存先パスと (分類した場合は) カテゴリ内訳をユーザーに報告する。分類はあくまで保存時の整形であり、自動でどこかへ昇格・転記しない
