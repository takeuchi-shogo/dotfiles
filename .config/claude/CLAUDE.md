# Claude Code グローバル設定

## IMPORTANT ルール
- サブエージェント・スキルを積極的に活用する（単独で完結させず、専門エージェントに委譲）
- コード変更後は必ず `code-reviewer` エージェントでレビューを実行
- 日本語で応答する

## コミット規則
- conventional commit + 絵文字プレフィックス（例: ✨ feat:, 🐛 fix:, 📝 docs:, ♻️ refactor:, 🔧 chore:）
- `/commit` コマンドを使用

## dotfiles 固有の注意
- このリポジトリは symlink で `~/.config`, `~/.claude` 等にリンクしている
- `~/.claude/` 配下の設定の実体は `dotfiles/.config/claude/`
- `~/.config/` 配下の設定の実体は `dotfiles/.config/`
