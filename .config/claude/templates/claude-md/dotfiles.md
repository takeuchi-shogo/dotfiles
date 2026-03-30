<important if="you are working with file paths, symlinks, or directory structure">

## dotfiles 固有の注意

- このリポジトリは symlink で `~/.config`, `~/.claude` 等にリンクしている
- `~/.claude/` 配下の設定の実体は `dotfiles/.config/claude/`
- `~/.config/` 配下の設定の実体は `dotfiles/.config/`
- エージェントのメモリスコープは3種: `user`（汎用）、`project`（プロジェクト固有レビューア）、`local`（機密）
- 実運用の playbook は `docs/playbooks/` を参照する

</important>
