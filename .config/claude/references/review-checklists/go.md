# Go Review Checklist

Go 固有のレビュー観点。`code-reviewer` が `.go` の変更をレビューする際に参照する。
Go Code Review Comments・Effective Go に基づく。

## 命名規約

- アクロニム: `ID`, `URL`, `API`, `HTTP` は全大文字（`userId` → `userID`）
- `MixedCaps` / `mixedCaps`（アンダースコア不使用）
- exported 名はパッケージ名で修飾される — 冗長にしない（`http.Server` not `http.HTTPServer`）
- レシーバ名は1-2文字（`s`, `db`, `svc`）で、同じ型の全メソッドで一貫させる
- Getter に `Get` プレフィックスを付けない（`Owner()` not `GetOwner()`）

## GO-1. Effective Go 準拠

- 早期リターン（happy path は左寄せ）
- named return values は defer やドキュメント目的でのみ
- naked return は小さな関数のみ
- cf. https://go.dev/doc/effective_go

## GO-2. nil slice vs 空 slice

- `must:` `make([]T, 0)` や `[]T{}` を nil に置き換えられないか確認
- JSON: `nil` → `null`, `[]T{}` → `[]`（API レスポンスに関わる場合は注意）

## GO-3. エラーハンドリング — `%w` ラップ

- `must:` エラーを握り潰していないか
- `must:` `%v` ではなく `%w`（`errors.Is`/`errors.As` で判定可能に）
- エラーメッセージは小文字で始め、句読点を付けない

## GO-4. Goroutine リーク検出

- `must:` channel 送信がブロックし続ける可能性がないか
- `must:` context キャンセルで goroutine が停止するか
- `errgroup` でライフサイクル管理
- 同期関数を非同期関数より優先しているか

## GO-5. Interface 最小化

- 使用者側で定義し、1-2メソッドの小さい interface を好む
- "Accept interfaces, return structs"
- モック目的だけで interface を実装側に定義していないか

## GO-6. Table-driven tests

- `[]struct{ name string; ... }` + `t.Run(tc.name, ...)`
- テストヘルパーには `t.Helper()` を呼ぶ
- 安全な場合は `t.Parallel()` を使う
- 失敗メッセージに入力・実際の値・期待値を含める: `Foo(%q) = %d; want %d`

## GO-7. Context 伝播

- `must:` `context.Background()` を深い層で直接使っていないか
- `must:` context をストラクトに保存していないか
- キャンセル可能な context は `defer cancel()` しているか

## GO-8. defer 安全性

- ループ内の defer はリソースリーク注意
- defer 内のエラーも処理: `defer func() { err = f.Close() }()`

## GO-9. Generics 活用

- 同じロジックを複数の型で書いている場合に検討
- 過剰なジェネリクスは避ける

## GO-10. 標準ライブラリの活用（Go 1.21+）

- `slices.Contains`, `slices.SortFunc` 等 — 手書きループを標準ライブラリに
- `maps.Clone`, `maps.Keys`, `maps.Values` 等 — map 操作も標準ライブラリに
- `log/slog` — 構造化ログを検討

## GO-11. Struct embedding

- is-a でなく has-a ならフィールドにする
- `sync.Mutex` の埋め込みは避ける（メソッドが export される）

## GO-12. make の capacity

- `make([]T, 0, len(source))` は source 全件が入る場合のみ有用
- フィルタリング後のサイズ不明なら capacity 指定不要

## GO-13. レシーバ型の選択（Value vs Pointer）

- `must:` レシーバを変更するメソッドが value レシーバになっていないか
- `must:` `sync.Mutex` を含む struct が value レシーバになっていないか
- 同じ型で pointer と value レシーバを混ぜていないか
- 迷ったら pointer レシーバを使う

## GO-14. Import 整理

- 標準ライブラリと外部パッケージを空行で区切っているか
- 不要な import リネームがないか（名前衝突時のみ許容）
- `import _` が `package main` またはテスト以外で使われていないか

## GO-15. 暗号論的乱数

- `must:` 鍵・トークン・シークレットの生成に `math/rand` を使っていないか
- `crypto/rand` を使う

## GO-16. 値渡し vs ポインタ渡し

- バイト数節約のためだけにポインタを渡していないか
- `*string`, `*io.Reader` 等の固定サイズ型を不要にポインタにしていないか

## GO-17. Example テストとベンチマーク

- 新しいパッケージには `func ExampleFoo()` を検討
- パフォーマンスが重要な箇所には `func BenchmarkFoo(b *testing.B)` を検討
