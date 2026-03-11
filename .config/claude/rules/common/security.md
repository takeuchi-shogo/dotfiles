# Security Guidelines

## Mandatory Security Checks

Before ANY commit:

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized HTML)
- [ ] Authentication/authorization verified
- [ ] CSRF protection for state-changing endpoints
- [ ] Error messages don't leak sensitive data
- [ ] No sensitive data in logs

## Secret Management

- NEVER hardcode secrets in source code
- PREFER secret managers (direnv + 参照パス, AWS Secrets Manager, Vault) over `.env` files
- `.env` ファイルは AI エージェントから読取可能 — 技術的に遮断できない場合は短命トークンで被害を限定
- Validate that required secrets are present at startup
- Rotate any secrets that may have been exposed
- Check `.gitignore` includes `.env*` files

## AI Agent Era: 漏洩前提の設計

- **禁止命令は防御にならない**: LLM はプロンプトインジェクションで迂回される（アーキテクチャ上の制約）
- **短命トークン**: 有効期限 1 時間以内、IP 制限、最小権限スコープの 3 点セット
- **`.claudeignore`**: 補助的防御層として `.env`, `*.pem`, `*.key` 等を遮断（ただし完全ではない）
- **コード検査**: AI 生成コードに `print(os.environ)` 等の情報漏洩パターンがないか確認

## Claude Code Ecosystem Security

脅威 DB: `references/claude-code-threats.md`

### MCP サーバー導入ルール

- 信頼できないソースの MCP サーバーを許可しない（GitHub 100+ stars、アクティブメンテナンス、公式推奨を基準）
- バージョンは exact で固定（`^` や `~` 禁止）、更新時は差分レビュー必須
- 既知 CVE に該当する MCP サーバーは使用停止（脅威 DB §1 参照）

### 外部リポジトリの .claude/ フォルダ

- `git clone` した外部リポジトリの `.claude/` は信頼しない — agents, hooks, settings.json, CLAUDE.md を検査してから使用
- `allowed-tools: ["Bash"]` の無制限許可、外部 URL への送信パターン（`curl`, `wget`）、難読化（`eval`, `base64 -d`）を検出対象とする

### スキル導入時の注意

- 外部スキルは導入前にコードを確認（Snyk 調査: スキルの 36.82% にセキュリティ欠陥）
- 環境変数の外部送信、動的コード実行、機密ディレクトリへのアクセスがないか確認

## Security Response Protocol

If security issue found:

1. STOP immediately
2. Use **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review codebase for similar issues
