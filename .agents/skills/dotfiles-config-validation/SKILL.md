---
name: dotfiles-config-validation
description: Validation guide for this dotfiles repository. Use when editing shell, window manager, Claude, Codex, README, or symlink-managed files in this repo and you need the smallest relevant validation command.
---

# Dotfiles Config Validation

この repo では、変更範囲に最も近い validation だけを実行する。

## Command Map

- `task validate-configs`
  - shell script、TOML、JSON、Lua、各種 config の構文や基本整合性
- `task validate-readmes`
  - `README.md` やドキュメント内リンク
- `task validate-symlinks`
  - `~/.claude`、`~/.codex`、`~/.config` への managed symlink
- `task validate`
  - 上記 3 つをまとめて確認したいとき

## Selection Rules

- `.codex/` を触ったら `task validate-symlinks`
- `.config/claude/` を触ったら `task validate-symlinks` を最低限含める
- tool 別 README 変更だけなら `task validate-readmes`
- shell / script / config 変更なら `task validate-configs`
- 迷ったら `Taskfile.yml` と `.bin/validate_*.sh` を読んで最小コマンドを選ぶ

## Before Editing

- 変更対象の README を先に読む
- 既存 symlink 管理対象かを確認する
- validation が重い場合でも、無関係な全体チェックは避ける

## Anti-Patterns

- small change なのに毎回 `task validate` を走らせる
- symlink 管理を変えたのに `task validate-symlinks` を省略する
- tool 固有 README を読まずに設定を変更する
