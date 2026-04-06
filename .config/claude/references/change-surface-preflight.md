# Change Surface Preflight Map

> 変更対象の種別（change surface）に応じた事前検証ルール。
> PostToolUse hook (`change-surface-advisor.py`) が参照し、適切な preflight をアドバイスする。

## Change Surface → Preflight マッピング

| Change Surface | ファイルパターン例 | Preflight アクション | 重要度 |
|---------------|-------------------|---------------------|--------|
| **認証・認可** | `auth/`, `middleware/auth`, `*_auth*`, `permission*`, `rbac*` | `/edge-case-analysis` + セキュリティレビュー推奨 | Critical |
| **DB Migration** | `migration/`, `*_migrate*`, `schema*`, `*.sql` | migration-guard エージェント起動推奨 | Critical |
| **外部 API 連携** | `client/`, `*_client*`, `api/external*`, `integration/` | edge-case-hunter（タイムアウト・リトライ・エラーハンドリング） | High |
| **並行処理** | `*_worker*`, `*goroutine*`, `*channel*`, `*mutex*`, `sync*` | edge-case-hunter（デッドロック・race condition） | High |
| **設定・環境変数** | `config/`, `.env*`, `*config*` | silent-failure-hunter（設定漏れ・デフォルト値の安全性） | Medium |
| **エラーハンドリング** | `error/`, `*_error*`, `panic*`, `recover*` | silent-failure-hunter | Medium |
| **テスト** | `*_test.go`, `*_test.ts`, `*.spec.*` | テスト対象のカバレッジ確認 | Low |
| **ドキュメント** | `*.md`, `docs/` | `/check-health` で参照整合性チェック | Low |
| **Hook・スクリプト** | `scripts/`, `settings.json`, `hooks/` | harness contract 準拠確認 | Critical |

## Preflight の実行タイミング

- **自動**: PostToolUse hook がファイルパスを検出し、アドバイスメッセージを注入
- **判断**: Claude がアドバイスを受けて、適切なタイミングで実行（毎回ではなく区切りで）
- **手動**: ユーザーが `/edge-case-analysis` や `/security-review` を直接起動

## 設計原則

- Preflight は **アドバイス**であり、ブロッカーではない（開発速度を落とさない）
- Critical な change surface では、アドバイスをより強く表示
- 同じ change surface への連続編集では、最初の1回だけアドバイス
