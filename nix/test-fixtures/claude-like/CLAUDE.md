# Phase 0+A fixture: claude-like root file

このファイルは D6 (`mkOutOfStoreSymlink`) の活線編集検証用のダミーです。
Phase B2 着手前に `nix/test-fixtures/claude-like/` ごと削除します。

検証観点:
- 編集 → `darwin-rebuild switch` を経由せず `~/.config/zsh-test-nix/CLAUDE.md` に即反映
- symlink の target が `/nix/store` ではなく本 repo を指していること
live-edit-1777029632
