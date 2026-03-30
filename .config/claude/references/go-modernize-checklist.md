# Go Modernize Checklist

Go 1.21〜1.26 のバージョン別移行ガイド。`go.mod` の `go` ディレクティブを確認し、対象バージョンの項目を適用する。

## バージョン別主要変更点

| Version | Release | 主要変更 |
|---------|---------|---------|
| Go 1.21 | 2023-08 | `min`/`max` builtin、`slices`/`maps` パッケージ、`log/slog`、`sync.OnceValue`/`OnceFunc` |
| Go 1.22 | 2024-02 | ループ変数スコープ修正、`range` over int、`math/rand/v2`、`cmp.Or`、`reflect.PointerTo` |
| Go 1.23 | 2024-08 | イテレータ（`iter` パッケージ）、`slices.SortedFunc`、`unique` パッケージ |
| Go 1.24 | 2025-02 | `os.Root`（パス走査防止）、`t.Context()`、`b.Loop()`、`go.mod` tool directives、crypto 移行 |
| Go 1.25 | 2025-08 | `sync.WaitGroup.Go`、`testing/synctest.Test`、`encoding/json/v2`（experimental） |
| Go 1.26 | 2026-02 | `go fix` 刷新（modernize linter 統合）、`ReverseProxy.Rewrite`、OAEP 推奨 |

## Deprecated Packages

| Deprecated | Replacement | Since |
|---|---|---|
| `math/rand` | `math/rand/v2` | Go 1.22 |
| `crypto/elliptic` (大部分) | `crypto/ecdh` | Go 1.21 |
| `reflect.SliceHeader`, `StringHeader` | `unsafe.Slice`, `unsafe.String` | Go 1.21 |
| `reflect.PtrTo` | `reflect.PointerTo` | Go 1.22 |
| `runtime.GOROOT()` | `go env GOROOT` | Go 1.24 |
| `runtime.SetFinalizer` | `runtime.AddCleanup` | Go 1.24 |
| `crypto/cipher.NewOFB`, `NewCFB*` | AEAD modes or `NewCTR` | Go 1.24 |
| `golang.org/x/crypto/sha3` | `crypto/sha3` | Go 1.24 |
| `golang.org/x/crypto/hkdf` | `crypto/hkdf` | Go 1.24 |
| `golang.org/x/crypto/pbkdf2` | `crypto/pbkdf2` | Go 1.24 |
| `testing/synctest.Run` | `testing/synctest.Test` | Go 1.25 |
| `crypto.EncryptPKCS1v15` | OAEP encryption | Go 1.26 |
| `httputil.ReverseProxy.Director` | `ReverseProxy.Rewrite` | Go 1.26 |

## Migration Priority

### High（安全性・正確性）

- [ ] ループ変数シャドウコピーの削除（Go 1.22+ でスコープ修正済み）
- [ ] `math/rand` → `math/rand/v2`、`rand.Seed` 呼び出し削除
- [ ] `os.Root` でユーザー入力ファイルパスを保護（Go 1.24+）
- [ ] `govulncheck` を実行し既知脆弱性を検出
- [ ] `errors.Is`/`errors.As` を使用（直接比較しない）
- [ ] deprecated crypto パッケージの移行（Go 1.24+）

### Medium（可読性・保守性）

- [ ] `interface{}` → `any`
- [ ] `min`/`max` builtin を使用
- [ ] `range` over int（`for i := range n`）
- [ ] `slices`/`maps` パッケージ活用
- [ ] `cmp.Or` でデフォルト値設定
- [ ] `sync.OnceValue`/`sync.OnceFunc` 活用
- [ ] `sync.WaitGroup.Go` 活用（Go 1.25+）
- [ ] テストで `t.Context()` 使用（Go 1.24+）
- [ ] ベンチマークで `b.Loop()` 使用（Go 1.24+）

### Lower（段階的改善）

- [ ] `log/slog` への移行検討
- [ ] イテレータの適用（Go 1.23+）
- [ ] `sort.Slice` → `slices.SortFunc`
- [ ] `strings.SplitSeq` 等のイテレータ版（Go 1.24+）
- [ ] `go.mod` tool directives でツール依存管理（Go 1.24+）
- [ ] PGO（Profile-Guided Optimization）有効化
- [ ] golangci-lint v2 + modernize linter 導入

## modernize linter

golangci-lint v2.6.0+ で `modernize` linter が利用可能。`golang.org/x/tools/go/analysis/passes/modernize` 由来。

```yaml
# .golangci.yml
linters:
  enable:
    - modernize
```

```bash
# 実行
golangci-lint run --enable modernize ./...

# Go 1.26+ の go fix でも利用可能
go fix -fix=modernize ./...
```

## 移行手順

1. `go.mod` の Go バージョンを確認
2. [go.dev/dl/](https://go.dev/dl/) で最新版を確認、アップグレード検討
3. `govulncheck ./...` で脆弱性チェック
4. High priority 項目から順に適用
5. `golangci-lint run --enable modernize` で残りを検出
6. CI に modernize チェックを追加
