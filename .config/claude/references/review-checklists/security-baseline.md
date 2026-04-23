---
status: reference
last_reviewed: 2026-04-23
---

# Security Baseline チェックリスト

AI-DLC SECURITY-01〜15 ベース。`security-reviewer` のプロンプトに注入して使用。
既存の `rules/common/security.md` を補完する追加チェック項目。

---

## OWASP 2025 対応チェック

### SECURITY-04: HTTP セキュリティヘッダー

- [ ] `Strict-Transport-Security` (HSTS) が設定されているか
- [ ] `Content-Security-Policy` (CSP) が設定されているか
- [ ] `X-Content-Type-Options: nosniff` が設定されているか
- [ ] `X-Frame-Options` または CSP frame-ancestors が設定されているか
- [ ] `Referrer-Policy` が適切に設定されているか

### SECURITY-09: セキュリティ硬化・設定ミス防止（A02:2025）

- [ ] デフォルト資格情報が変更されているか
- [ ] 本番環境でデバッグモード/スタックトレースが無効か
- [ ] 不要な HTTP メソッド（TRACE, OPTIONS）が無効化されているか
- [ ] ディレクトリリスティングが無効化されているか
- [ ] サーバーバージョン情報がレスポンスヘッダーから削除されているか

### SECURITY-11: セキュアデザイン原則（A06:2025）

- [ ] 信頼境界が明確に定義されているか（フロントエンド/バックエンド/DB）
- [ ] ビジネスロジックに対するレート制限があるか
- [ ] 重要な操作（削除、権限変更）に確認ステップがあるか
- [ ] フェイルセーフデフォルト: 明示的な許可がない限りアクセス拒否か

### SECURITY-13: ソフトウェア・データ整合性（A08:2025）

- [ ] CI/CD パイプラインで未検証のコードが実行されないか
- [ ] デシリアライゼーションに型チェック/スキーマ検証があるか
- [ ] パッケージの署名/チェックサム検証が有効か
- [ ] 自動アップデート機能にデジタル署名の検証があるか

---

## 適用ルール

- Web アプリケーション開発時に security-reviewer のプロンプトに注入
- Blocking: CRITICAL/HIGH の指摘は修正必須
- Non-Blocking: MEDIUM/LOW は推奨事項として報告
