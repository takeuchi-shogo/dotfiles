# Go Review Checklist

Go 固有のレビュー観点。`code-reviewer` が `.go` の変更をレビューする際に参照する。

## 命名規約

- アクロニム: `ID`, `URL`, `API`, `HTTP` は全大文字（`userId` → `userID`）
- `MixedCaps` / `mixedCaps`（アンダースコア不使用）
- exported 名はパッケージ名で修飾される — 冗長にしない（`http.Server` not `http.HTTPServer`）
- レシーバ名は1-2文字（`s`, `db`, `svc`）

## GO-1. Effective Go 準拠

- 早期リターン（happy path は左寄せ）
- named return values は defer やドキュメント目的でのみ
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

## GO-5. Interface 最小化

- 使用者側で定義し、1-2メソッドの小さい interface を好む
- "Accept interfaces, return structs"

## GO-6. Table-driven tests

- `[]struct{ name string; ... }` + `t.Run(tc.name, ...)`
- テストヘルパーには `t.Helper()` を呼ぶ

## GO-7. Context 伝播

- `must:` `context.Background()` を深い層で直接使っていないか
- `must:` context をストラクトに保存していないか

## GO-8. defer 安全性

- ループ内の defer はリソースリーク注意
- defer 内のエラーも処理: `defer func() { err = f.Close() }()`

## GO-9. Generics 活用

- 同じロジックを複数の型で書いている場合に検討
- 過剰なジェネリクスは避ける

## GO-10. slices/maps パッケージ

Go 1.21+ の `slices.Contains`, `slices.SortFunc` 等。手書きループを標準ライブラリに。

## GO-11. Struct embedding

- is-a でなく has-a ならフィールドにする
- `sync.Mutex` の埋め込みは避ける（メソッドが export される）

## GO-12. make の capacity

- `make([]T, 0, len(source))` は source 全件が入る場合のみ有用
- フィルタリング後のサイズ不明なら capacity 指定不要
