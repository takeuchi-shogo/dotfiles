# High-Risk Change Patterns

> 高リスク変更のパターン定義。PostToolUse hook (`change-surface-advisor.py`) が参照し、
> edge-case-hunter / silent-failure-hunter の自動起動をアドバイスする。

## リスクレベル定義

| レベル | 意味 | アクション |
|--------|------|-----------|
| **Critical** | データ損失・セキュリティ侵害の可能性 | red-team brief 必須を強く推奨 |
| **High** | 機能障害・パフォーマンス劣化の可能性 | edge-case-hunter 推奨 |
| **Medium** | silent failure の可能性 | silent-failure-hunter 推奨 |

## パターン一覧

### Critical

| パターン | ファイル例 | リスク | 推奨エージェント |
|---------|-----------|--------|----------------|
| 認証ロジック変更 | `auth.go`, `middleware/jwt.go` | 認可バイパス | edge-case-hunter + security-reviewer |
| DB スキーマ変更 | `*.sql`, `migration/*.go` | データ損失、後方互換性破壊 | migration-guard |
| Hook・Policy 変更 | `scripts/policy/*.py`, `settings.json` | ハーネス無効化 | harness contract 準拠確認 |
| 暗号・署名処理 | `crypto*`, `sign*`, `hash*` | セキュリティ脆弱性 | security-reviewer |

### High

| パターン | ファイル例 | リスク | 推奨エージェント |
|---------|-----------|--------|----------------|
| 外部 API クライアント | `*_client.go`, `api/external*` | タイムアウト、リトライ不備 | edge-case-hunter |
| 並行処理 | `*worker*`, `*channel*`, `sync*` | デッドロック、race condition | edge-case-hunter |
| キャッシュロジック | `cache*`, `*_cache*` | 一貫性違反、stale data | edge-case-hunter |
| Rate limiting | `rate*`, `throttle*`, `limiter*` | DoS 耐性 | edge-case-hunter |

### Medium

| パターン | ファイル例 | リスク | 推奨エージェント |
|---------|-----------|--------|----------------|
| 設定・環境変数 | `config*`, `.env*` | デフォルト値の安全性 | silent-failure-hunter |
| エラーハンドリング | `error*`, `*_error*` | エラー握り潰し | silent-failure-hunter |
| ログ・計装 | `logger*`, `telemetry*` | 観測可能性の欠落 | silent-failure-hunter |
| バリデーション | `valid*`, `sanitiz*` | 入力検証の抜け穴 | edge-case-hunter |
