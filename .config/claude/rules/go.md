---
paths:
  - "**/*.go"
  - "**/go.mod"
---

# Go Rules

Go Code Review Comments・Effective Go・Learn Go with Tests に基づく。

## エラーハンドリング

- `if err != nil` を全てのエラー戻り値に対してチェックする — `_` への代入禁止
- コンテキスト付きでラップする: `fmt.Errorf("failed to create user: %w", err)`
- 比較には `errors.Is()` / `errors.As()` を使う — `==` 禁止
- センチネルエラーはパッケージレベルの `var ErrNotFound = errors.New(...)` で定義する
- エラーメッセージは小文字で始め、句読点を付けない（ログ中で他のメッセージと結合されるため）

```go
// OK: 小文字、句読点なし
fmt.Errorf("something bad")

// NG: 大文字、句読点あり
fmt.Errorf("Something bad.")
```

## Nil とゼロ値

- `var s []T`（nil slice）を「データなし」に使う — JSON では `null` にマーシャルされる
- 空の JSON 配列 `[]` が必要な場合のみ `make([]T, 0)` を使う
- map への書き込み前に nil チェックする: `if m == nil { m = make(...) }`

## 命名規約

### 基本ルール

- MixedCaps のみ — exported 名にアンダースコアを使わない
- パッケージ名: 短い小文字の単語（例: `user`, `http`）。`util`, `common`, `misc` は避ける
- パッケージ名から識別子の冗長性を排除する（`chubby.File` であって `chubby.ChubbyFile` ではない）
- アクロニム: `ID`, `URL`, `API`, `HTTP` は全大文字（`userId` → `userID`）
- interface: 単一メソッドなら `-er` サフィックス（`Reader`, `Writer`, `Formatter`）

### レシーバ名

- 型名の1-2文字の略語を使う（`s` for `Server`, `cl` for `Client`）
- `me`, `this`, `self` は使わない — Go ではレシーバはただのパラメータ
- 同じ型の全メソッドで一貫させる（あるメソッドで `c`、別で `cl` としない）

### レシーバ型（Value vs Pointer）の選択

**pointer レシーバ**を使う場合:
- メソッドがレシーバを変更する
- `sync.Mutex` などの同期フィールドを含む（コピー防止）
- 大きな struct や array（効率のため）

**value レシーバ**を使う場合:
- map, func, chan 型（pointer を使わない）
- スライスでメソッドがリスライス・再割り当てしない
- `time.Time` のような小さな値型
- ミュータブルなフィールドやポインタを含まない

**迷ったら pointer レシーバを使う。同じ型で pointer と value を混ぜない。**

### Getter の命名

- `GetOwner()` ではなく `Owner()` — Go では Get プレフィックスを付けない
- setter は `SetOwner()` で OK

### 変数名のスコープルール

宣言からの距離に応じて名前の長さを決める（Go Code Review Comments 公式ルール）:
- レシーバ: 1-2文字（`s`, `cl`）
- ループインデックス: 1文字 OK（`i`, `j`）
- 短いスコープの変数: 短い名前 OK（`r` for reader, `c` for count）
- パッケージレベル・広いスコープ: 説明的な名前が必要

```go
// OK: 短いスコープなら短い名前
for i, v := range items { ... }

// OK: 広いスコープなら説明的に
var defaultUserTimeout time.Duration
```

### 型で意味を表現する

Go の型システムを活かし、名前に単位を埋め込まない:

```go
// Go 慣用: 型で単位を表現（標準ライブラリ全体で使用）
func Dial(addr string, timeout time.Duration) (Conn, error)

// 非慣用: 名前に単位を埋め込む（C スタイル）
func Dial(addr string, timeoutMs int64) (Conn, error)
```

型で区別できない場合は Newtype パターンを使う:
- `type UserID int64`, `type ArticleID int64` で取り違えを防ぐ
- iota で enum を定義し、string フラグの暗黙的な値域を排除する

### 「何をするか」を表現する

- `onMessageReceived` ✗ → `storeReceivedMessage` ✓
- `handleError` ✗ → `logAndReturnError` ✓
- 関数名は「呼び出し側で読んだとき何が起きるか分かる」名前にする

### 否定を避ける

- `isEnabled` ✓, `isDisabled` △, `isNotDisabled` ✗
- 条件分岐で二重否定を生まないようにする

## Import

- 標準ライブラリを第1グループ、外部パッケージを第2グループに分け、空行で区切る
- `goimports` を使って自動整理する
- リネームは名前衝突時のみ — パッケージ名が良ければリネーム不要
- `import _`（副作用のみ）は `package main` またはテストでのみ使う
- `import .` はほぼ使わない（循環依存のテストなど限定的なケースのみ）

```go
import (
    "fmt"
    "os"

    "github.com/foo/bar"
    "rsc.io/goversion/version"
)
```

## context.Context

- 第1引数として渡す: `func Foo(ctx context.Context, ...)`
- コールチェーン全体で伝播する — 途中で `context.Background()` を使わない
- 外部呼び出しにはタイムアウトを設定: `ctx, cancel := context.WithTimeout(ctx, 5*time.Second)`
- キャンセル可能なコンテキスト作成後は `defer cancel()` する
- struct のフィールドに context を保存しない（引数として渡す）

## 並行処理

- 全ての goroutine に明確な終了パスを持たせる — goroutine リークを防ぐ
- 並行操作でのエラー伝播には `errgroup` を使う
- 通信にはチャネル、状態保護にはミューテックスを使う
- `mu.Lock()` の直後に `defer mu.Unlock()` する
- 同期関数を非同期関数より優先する — 呼び出し側が必要なら goroutine で呼べばよい

## 関数設計

### Early Return の徹底

アンハッピーパスを先にガード節で追い出し、ハッピーパスをフラットに保つ:

```go
// OK: エラーを先に処理、正常パスはフラット
x, err := f()
if err != nil {
    return err
}
// x を使う処理（インデントなし）

// NG: else に正常パスを書く
if err != nil {
    // エラー処理
} else {
    // 正常パス（不要なインデント）
}
```

### Named Result と Naked Return

- named result は同じ型のパラメータ2-3個の意味を区別する場合、または defer で変更する場合に使う
- naked return は数行の小さな関数でのみ許容。中規模以上の関数では明示的に return する

### 値渡し vs ポインタ渡し

- バイト数節約のためだけにポインタを渡さない
- `*string`, `*io.Reader` は固定サイズなので直接渡す
- 関数内で `*x` としてしか参照しないなら、引数をポインタにすべきではない

### Command-Query Separation

- Query（値を返す）: 副作用なし。呼び出し回数で結果が変わらない
- Command（状態を変える）: 戻り値は error のみ（Go 慣用の `(value, error)` は例外）

## セキュリティ

### 暗号論的乱数

鍵やトークンの生成には `math/rand` を使わない。`crypto/rand` を使う:

```go
import "crypto/rand"

// Go 1.24+
func Key() string {
    return rand.Text()
}

// Go 1.23 以前
func Key() string {
    buf := make([]byte, 32)
    _, err := rand.Read(buf)
    if err != nil {
        panic(err) // システムエントロピー枯渇は回復不能
    }
    return hex.EncodeToString(buf)
}
```

## テスト

- table-driven tests を `t.Run()` で構造化する
- テストケース名は説明的に: `{name: "ユーザーが見つからない場合にエラーを返す"}`
- テストヘルパーには `t.Helper()` を呼ぶ
- 安全な場合は `t.Parallel()` で並列実行する
- テスト失敗メッセージには入力・実際の値・期待値を全て含める:

```go
if got != tt.want {
    t.Errorf("Foo(%q) = %d; want %d", tt.in, got, tt.want)
}
```

- `func ExampleFoo()` でドキュメントと実行可能テストを兼ねる
- パフォーマンスが重要な箇所には `func BenchmarkFoo(b *testing.B)` を書く

## モダン Go（1.21+）

- `slices.Contains`, `slices.SortFunc`, `maps.Clone`, `maps.Keys` 等の標準ライブラリを手書きループより優先する
- Go 1.22+ ではループ変数がイテレーションごとにスコープされる（goroutine 内での変数キャプチャ問題が解消）
- `log/slog` で構造化ログを検討する（`log.Printf` の代替）
- Go 1.23+ の range-over-func でカスタムイテレータを定義できる
