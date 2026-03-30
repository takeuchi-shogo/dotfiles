# Go Project Layout Guide

プロジェクトの規模と種類に合わせて構造をサイズ調整する。100行の CLI に DI レイヤーは不要。

## Project Type

| Type | 用途 | 主要ディレクトリ |
|------|------|----------------|
| CLI Tool | コマンドラインアプリ | `cmd/{name}/`, `internal/`, optional `pkg/` |
| Library | 再利用可能なコード | `pkg/{name}/`, `internal/` |
| Service | HTTP API, マイクロサービス | `cmd/{service}/`, `internal/`, `api/`, `web/` |
| Monorepo | 複数関連パッケージ | `go.work`, separate modules |
| Workspace | ローカル複数モジュール開発 | `go.work`, replace directives |

## Module Naming

- `go.mod` はリポジトリ URL と一致: `github.com/username/project-name`
- lowercase only、ハイフン区切り: `user-auth`（`userAuth` や `user_auth` ではない）
- 意味のある名前: 目的を明確に表現する

```go
// Good
module github.com/jdoe/payment-processor

// Bad
module myproject
module github.com/jdoe/MyProject
```

## Directory Rules

| ディレクトリ | 役割 | ルール |
|-------------|------|--------|
| `cmd/` | エントリポイント | main パッケージ。フラグ解析→依存注入→`Run()` のみ |
| `internal/` | 非公開コード | 外部パッケージからインポート不可 |
| `pkg/` | 公開ライブラリ | 外部消費者にも有用な場合のみ |
| `api/` | API 定義 | OpenAPI spec, proto files |
| `web/` | Web アセット | テンプレート、静的ファイル |
| `testdata/` | テストフィクスチャ | Go build に含まれない |

### 禁止パッケージ名

`util`, `common`, `misc`, `helpers`, `shared` — 具体的な名前を付ける

## 12-Factor App（サービス向け）

- [ ] 設定は環境変数から取得
- [ ] ログは stdout に出力
- [ ] プロセスはステートレス
- [ ] グレースフルシャットダウン対応
- [ ] バッキングサービスはアタッチドリソースとして扱う
- [ ] 管理タスクは `cmd/migrate/` 等のワンオフコマンド

## Essential Files

| ファイル | 用途 |
|---------|------|
| `Makefile` | ビルド自動化 |
| `.gitignore` | `/vendor/`, バイナリ, `.env` |
| `.golangci.yml` | リンター設定 |
| `README.md` | プロジェクト説明 |

## Go Workspaces

複数モジュールのローカル開発時:

```bash
go work init
go work use ./module-a ./module-b
```

- `go.work` はリポジトリルートに配置
- CI では `GOWORK=off` で個別モジュールをテスト可能
- `go.work.sum` はコミットする

## Initialization Checklist

- [ ] アーキテクチャ選択（clean / hexagonal / DDD / flat）
- [ ] DI アプローチ選択（manual / wire / dig+fx / なし）
- [ ] プロジェクトタイプ決定（CLI / Library / Service / Monorepo）
- [ ] 構造をスコープに合わせてサイズ調整
- [ ] `go mod init github.com/user/project-name`
- [ ] `cmd/{name}/main.go` 作成
- [ ] `internal/` 作成
- [ ] `gofmt -s -w .`
- [ ] `.gitignore` 追加

## Anti-Patterns

| NG | 理由 |
|----|------|
| cmd/ に ビジネスロジック | main は薄く保つ。internal/ に移動 |
| pkg/ の乱用 | 外部公開不要なら internal/ |
| 深すぎるネスト (4階層超) | パッケージをフラットに保つ |
| 循環依存 | interface で依存を逆転させる |
| 1パッケージに全部入れ | 責務で分割する（ただし分けすぎない） |
