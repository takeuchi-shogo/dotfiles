# Hammerspoon Daily Enforcer Plan

## Goal
- wake / unlock をトリガーに、朝 TODO と日報の未実施を強めに促す Hammerspoon 設定を dotfiles に追加する

## Scope
- 追加: `.hammerspoon/` 配下の Hammerspoon 設定
- 変更: `docs/templates/daily.md`
- 変更: `README.md`, `Brewfile`
- 変更: `.bin/symlink.sh`, `.bin/validate_configs.sh`, `.bin/validate_symlinks.sh`
- 変更しない: Claude / Codex harness 本体、既存 skill の振る舞い

## Constraints
- スリープ復帰中心の運用に効くこと
- 既存の dotfiles symlink 管理に自然に乗ること
- 未実施判定は機械的に安定して行えること
- validation は変更面に近い最小コマンドに絞ること

## Validation
- `task validate-configs`
- `task validate-symlinks`
- `task validate-readmes`

## Steps
1. daily テンプレートと保存先の方針を決める
2. Hammerspoon 設定を実装する
3. symlink / validation / README / Brewfile を更新する
4. validation を実行して差分を確認する

## Progress
- [x] Step 1
- [x] Step 2
- [x] Step 3
- [x] Step 4

## Surprises & Discoveries
- repo には Hammerspoon 設定がまだ無く、`~/.hammerspoon` を新規 managed surface として追加する必要がある
- `docs/templates/daily.md` は現状どこからも参照されておらず、machine-readable marker を入れても影響範囲は限定的
- `task symlink` は sandbox 下だと既存の home 配下 symlink 対象で大量の permission noise が出るため、今回必要な `~/.hammerspoon` は個別 symlink 作成で反映した
- `task validate-readmes` は既存の `everything-cc/` 配下 broken local links で失敗し、今回の `README.md` / `.hammerspoon/README.md` のリンク自体は個別確認で問題なかった

## Decision Log
- `.config/hammerspoon` ではなく `~/.hammerspoon` に合わせて repo 直下 `.hammerspoon/` を採用する
- Obsidian Vault があればそこを優先し、無ければ `~/daily-notes/` をフォールバック保存先にする

## Outcome
- `.hammerspoon/` に daily enforcer を追加し、wake / unlock + 定期 timer で朝 TODO / 日報の未実施を判定できるようにした
- `docs/templates/daily.md` を machine-readable に拡張し、自動作成・補完のテンプレートとして使えるようにした
- `.hammerspoon` の symlink / validation / install surface を dotfiles 側に追加した
