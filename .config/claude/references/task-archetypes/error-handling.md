---
status: reference
last_reviewed: 2026-04-23
---

# エラーハンドリング Archetype

> repair-routing.md からの修復先。このドメインで繰り返しミスが発生した場合に参照・更新する。

## 定義

- **スコープ**: エラーの生成・ラップ・伝播・ログ・ユーザー向けレスポンス変換に関わる処理
- **典型的なファイルパス例**: `error/`, `*_error*.go`, `errors/`, `middleware/error*.go`, `handler/response.go`

## 既知の落とし穴

| 落とし穴 | 症状 | 関連 FM | 防止策 |
|---------|------|---------|--------|
| エラー握り潰し（空 catch/`_`） | 失敗が無音で進行し、後続処理が不正なデータを使う | FM-002 | エラーは必ずラップして伝播するか、明示的にログを残す |
| `panic`/`recover` の乱用 | 非致命的エラーで goroutine がクラッシュ | FM-002 | `panic` は「プログラムが継続不可能な状態」のみに限定する |
| generic error message | `"internal error"` のみでデバッグ不可 | FM-002 | 開発者向けエラーには元のエラーと操作コンテキストを含める |
| ユーザー向けメッセージへの内部情報露出 | スタックトレース・DB スキーマがレスポンスに含まれる | FM-010 | ユーザー向けと開発者向けのエラー表現を分離する |
| `defer` 内のエラー無視 | `rows.Close()` 等のエラーが捨てられる | FM-002 | `defer` 内でもエラーを named return または変数で捕捉する |

## 不変条件

- エラーは `fmt.Errorf("操作名: %w", err)` でコンテキストを付けてラップする
- `errors.Is` / `errors.As` で sentinel error と custom error type を判別する
- ユーザー向けメッセージには内部実装を含めない（エラーコードやメッセージIDで対応）
- ログには `request_id`・`user_id`・`operation` 等のコンテキストを必ず含める
- `_` によるエラー無視は原則禁止。無視する場合はコメントで理由を明記する

## テスト戦略

| テスト種別 | 目的 | 優先度 |
|-----------|------|--------|
| エラーパス網羅テスト | 各エラー条件（nil, EOF, 権限エラー等）で適切に伝播することを確認 | Critical |
| エラーラップテスト | `errors.Is`/`errors.As` で元のエラーを辿れることを確認 | High |
| エラーメッセージ検証 | ユーザー向けレスポンスに内部情報が含まれないことを確認 | High |
| `defer` cleanup テスト | `defer` 内のエラーが適切に処理されることを確認 | Medium |

## Change Surface 連携

- **対応する Change Surface**: 「エラーハンドリング」(Medium)
- **推奨 preflight**: silent-failure-hunter（エラー握り潰し・ログ欠落・伝播漏れの検出）
- `change-surface-preflight.md` の `error/`, `*_error*`, `panic*`, `recover*` パターンに該当
