---
description: >
  コンテキスト圧縮を生き延びる絶対不変ルール。
  長時間セッションでも毎回再注入され、消失しない。
paths:
  - "**/*"
---

# Core Invariants

これらは全ファイル触発で再注入される。圧縮で消えない最後の砦。
違反が実際にバグ・品質低下・hook 崩壊を引き起こした実績のあるルールのみ。

1. **`git commit --no-verify` 禁止** — hook 体系が全て無効化される。例外なし。
   verify: Grep("--no-verify", path=".config/claude/") → 0 matches

2. **lint config は変更しない** — `.eslintrc*`, `biome.json`, `.prettierrc*` 等は保護対象。設定ではなくコードを直す。
   verify: git diff で lint config ファイルが含まれていない

3. **レビュー中は Edit/Write 禁止** — diff が汚れ、レビュー結果が無意味になる。レビューは read-only で完了させる。
   verify: レビューエージェント実行中に Edit/Write が呼ばれていない

4. **MEMORY.md にはポインタのみ** — 詳細を書くと 200行上限に即到達。1エントリ1行、詳細は個別ファイルに。
   verify: Grep("^- ", path="MEMORY.md") の各行が 150文字以下

5. **symlink 実体パスを間違えない** — `~/.claude/` の実体は `dotfiles/.config/claude/`。直接 `~/.claude/` を編集すると symlink が壊れる。
   verify: 編集対象パスが dotfiles/ 配下であること
