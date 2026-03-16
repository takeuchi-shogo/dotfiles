# half-clone

Auto-compact 時の情報損失を緩和するバックアップスクリプト。

## 概要

Claude Code の会話ファイル（`.jsonl`）の後半 50% を `~/dotfiles/tmp/half-clone-backup.jsonl` に保存する。
PreCompact hook チェーンから呼ばれ、圧縮前に会話コンテキストのスナップショットを残す。

## 仕様

- 最新の `.jsonl` 会話ファイルを `~/.claude/` 配下から検索
- メッセージ総数の後半 50% を抽出して保存
- 3 世代ローテーション（`.1`, `.2`, `.3`）
- 会話ファイル未検出 or 4 行未満の場合は graceful exit（exit 0）
