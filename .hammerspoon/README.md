# Hammerspoon

朝 TODO と日報の未実施を `wake / unlock` ベースで強めに促すための Hammerspoon 設定。

## 何をするか

- 今日の daily note を自動で作成または補完する
- `systemDidWake` と `screensDidUnlock` で未実施を判定する
- 未記入なら Obsidian の当日ノートを開く
- menubar に `TODO`, `EOD`, `DAY` の状態を出す
- 15 分ごとに再確認する

## 保存先

優先順は以下。

1. `OBSIDIAN_VAULT_PATH/07-Daily/YYYY-MM-DD.md`
2. `~/Documents/Obsidian Vault/07-Daily/YYYY-MM-DD.md`
3. `~/daily-notes/YYYY-MM-DD.md`

## セットアップ

1. `task symlink`
2. Hammerspoon を起動
3. Hammerspoon で `~/.hammerspoon/init.lua` を reload
4. 必要なら macOS の通知権限を許可
5. 必要なら Hammerspoon の `Launch at login` を有効化

## daily template

テンプレートは `~/dotfiles/docs/templates/daily.md` を使う。
未実施判定は `daily-enforcer:*` の marker と、marker 内の実際の記入有無で行う。
