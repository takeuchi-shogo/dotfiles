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

## Security Response Protocol

If security issue found:

1. STOP immediately
2. Use **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review codebase for similar issues
