# 外部 API 連携 Archetype

> repair-routing.md からの修復先。このドメインで繰り返しミスが発生した場合に参照・更新する。

## 定義

- **スコープ**: 外部 HTTP API・gRPC・メッセージキュー・SaaS SDK を呼び出すクライアント実装
- **典型的なファイルパス例**: `client/`, `*_client*.go`, `api/external*/`, `integration/`, `infra/http/`

## 既知の落とし穴

| 落とし穴 | 症状 | 関連 FM | 防止策 |
|---------|------|---------|--------|
| タイムアウト未設定 | `http.DefaultClient` 使用でハング | FM-009 | `http.Client{Timeout: ...}` を明示。Go のデフォルト Client はタイムアウトなし |
| リトライ欠如（指数バックオフなし） | 一時的な 5xx で即失敗 | FM-002 | `retryablehttp` や独自バックオフで最大3回リトライ |
| レート制限の無視 | 429 を受けても即リトライしてアカウント停止 | FM-009 | `Retry-After` ヘッダーを尊重し、リトライ間隔を制御する |
| 部分失敗の無視 | バッチ API の一部エラーを見落とす | FM-002 | バッチレスポンスの各要素のステータスを個別に確認する |
| エラー分類の欠如 | 429/503 を 400 と同じく fatal 扱い | FM-002 | retryable（5xx, 429, network）と fatal（4xx）を明確に分類 |

## 不変条件

- すべての外部 HTTP 呼び出しにタイムアウトを設定する（デフォルト Client 禁止）
- リトライは指数バックオフ + ジッターで実装する
- circuit breaker を導入し、連続失敗時に早期遮断する
- エラーは retryable / fatal に分類し、fatal は即座に上位へ伝播する
- `context.WithTimeout` で呼び出し全体の上限も設ける

## テスト戦略

| テスト種別 | 目的 | 優先度 |
|-----------|------|--------|
| モックサーバーテスト | 正常系・各エラーコードのレスポンスをシミュレート | Critical |
| タイムアウトテスト | 規定時間内にキャンセルされることを確認 | High |
| リトライ動作テスト | 5xx でリトライし、最終的に成功/失敗することを確認 | High |
| レート制限テスト | 429 受信後に適切なウェイトを入れることを確認 | Medium |

## Change Surface 連携

- **対応する Change Surface**: 「外部 API 連携」(High)
- **推奨 preflight**: edge-case-hunter（タイムアウト・リトライ・エラーハンドリングの網羅）
- `change-surface-preflight.md` の `client/`, `*_client*`, `api/external*`, `integration/` パターンに該当
