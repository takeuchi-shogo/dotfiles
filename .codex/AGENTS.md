# Global Codex Instructions

## Language
- 日本語で応答する（コード・技術用語は英語のまま）

## Coding Conventions
- Conventional Commit + 絵文字プレフィックス（✨ feat:, 🐛 fix:, 📝 docs:, ♻️ refactor:, 🔧 chore:）
- 変数名・関数名は既存コードベースの命名規則に従う
- 不要なコメントやドキュメントを追加しない

## Workflow
- コード変更時は最小限の変更に留める
- テストがあるプロジェクトでは変更後にテストを実行
- セキュリティ脆弱性（XSS, SQL Injection 等）を導入しない
- エラーハンドリングはシステム境界（ユーザー入力、外部 API）のみ

## Tools
- パッケージマネージャは既存プロジェクトの設定に従う（pnpm, npm, bun 等）
- フォーマッタ・リンターが設定されていればコミット前に実行
