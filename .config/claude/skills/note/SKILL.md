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
2. Bash で `note-to-vault.sh` を実行する:

```bash
~/.config/claude/scripts/runtime/note-to-vault.sh '引数テキスト'
```

3. 保存先パスをユーザーに報告する
