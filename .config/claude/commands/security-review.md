---
allowed-tools: Bash(git diff *), Bash(git log *), Bash(git status *), Bash(npm audit *), Bash(govulncheck *)
description: Run OWASP Top 10 security review on recent code changes
---

# Security Review

セキュリティ観点でコード変更をレビュー: $ARGUMENTS

## Current Repository State

- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Staged changes: !`git diff --cached --stat`
- Unstaged changes: !`git diff --stat`

## What This Command Does

1. 引数なし: unstaged + staged の変更をセキュリティレビュー
2. ブランチ名指定: 現在のブランチとの diff をセキュリティレビュー
3. コミットハッシュ指定: 特定コミットの変更をセキュリティレビュー
4. `git diff` で変更内容を取得し、OWASP Top 10 チェックリストで評価

## Security Checklist

### OWASP Top 10 Check

1. **Injection** — SQL/コマンド/LDAP インジェクション
   - パラメタライズドクエリを使用しているか
   - ユーザー入力が直接 SQL/シェルコマンドに含まれていないか

2. **Broken Authentication** — 認証の不備
   - パスワードが適切にハッシュ化されているか（bcrypt/argon2）
   - JWT/セッションが安全に管理されているか

3. **Sensitive Data Exposure** — 機密データの露出
   - ハードコードされたシークレット（API キー、パスワード、トークン）がないか
   - ログに機密情報が出力されていないか
   - エラーメッセージに内部情報が含まれていないか

4. **XML External Entities (XXE)** — XXE 脆弱性
   - XML パーサーが安全に構成されているか

5. **Broken Access Control** — アクセス制御の不備
   - すべてのエンドポイントで認証・認可チェックがあるか
   - CORS が適切に設定されているか

6. **Security Misconfiguration** — セキュリティ設定の不備
   - 本番環境でデバッグモードが無効か
   - セキュリティヘッダーが設定されているか

7. **Cross-Site Scripting (XSS)** — XSS 脆弱性
   - ユーザー入力が適切にエスケープされているか
   - `dangerouslySetInnerHTML` に未サニタイズ入力がないか

8. **Insecure Deserialization** — 安全でないデシリアライゼーション
   - ユーザー入力のデシリアライズが安全か

9. **Known Vulnerabilities** — 既知の脆弱性
   - 依存パッケージに既知の脆弱性がないか

10. **Insufficient Logging** — 不十分なログ
    - セキュリティイベントが適切にログされているか

### Secret Detection

以下のパターンを検索:
- `password`, `secret`, `api_key`, `token` を含む文字列リテラル
- Base64 エンコードされた資格情報
- AWS/GCP/Azure のキーパターン
- プライベートキー（`-----BEGIN`）

### Input Validation

- ユーザー入力にバリデーションスキーマ（zod, pydantic 等）が適用されているか
- ファイルアップロードにサイズ・タイプ制限があるか
- ホワイトリスト方式のバリデーションか（ブラックリストではなく）

## Output Format

深刻度別に分類して表示:

```
🔴 CRITICAL: [説明]
  ファイル:行番号 — 問題の詳細と修正案

🟠 HIGH: [説明]
  ファイル:行番号 — 問題の詳細と修正案

🟡 MEDIUM: [説明]
  ファイル:行番号 — 改善提案

🟢 LOW: [説明]
  ファイル:行番号 — 推奨事項
```

CRITICAL/HIGH が見つかった場合は、コミット前に修正を強く推奨する。
問題がなければ "Security Review: PASSED" と表示。
