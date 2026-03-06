---
paths:
  - "**/*.go"
  - "**/go.mod"
---

# Go Rules

## Error Handling

ALWAYS handle errors explicitly:
- Check `if err != nil` for every error return — never assign to `_`
- Wrap errors with context: `fmt.Errorf("failed to create user: %w", err)`
- Use `errors.Is()` / `errors.As()` for comparison — never `==`
- Define sentinel errors as package-level `var ErrNotFound = errors.New(...)`

## Nil & Zero Values

- Prefer `var s []T` (nil slice) for "no data yet" — it marshals to `null`
- Use `make([]T, 0)` when you need an empty JSON array `[]`
- Always check for nil maps before writing: `if m == nil { m = make(...) }`

## Naming Conventions

### 基本ルール
- MixedCaps only — no underscores in exported names
- Package names: short, lowercase, single word (e.g. `user`, `http`)
- Receiver names: 1-2 letter abbreviation of type (e.g. `s` for `Server`)
- Interfaces: single-method interfaces use `-er` suffix (`Reader`, `Writer`)

### 「what」を表現する（「when/who/how」ではない）
- `onMessageReceived` ✗ → `storeReceivedMessage` ✓
- `handleError` ✗ → `logAndReturnError` ✓
- 関数名は「呼び出し側で読んだとき何が起きるか分かる」名前にする

### 単位・型情報を名前に含める
- `timeout` ✗ → `timeoutSec` or `timeoutMillis` ✓
- `width` ✗ → `widthPx` ✓
- `i, j, k` ✗ → `userIdx`, `row`, `col` ✓（ループ変数が1行で閉じない場合）

### Newtype パターンで型安全を確保
- `type UserID int64`, `type ArticleID int64` で取り違えを防ぐ
- iota で enum を定義し、string フラグの暗黙的な値域を排除する

### 否定を避ける
- `isEnabled` ✓, `isDisabled` △, `isNotDisabled` ✗
- 条件分岐で二重否定を生まないようにする

## context.Context

- Always pass as the first parameter: `func Foo(ctx context.Context, ...)`
- Propagate context through the call chain — never use `context.Background()` mid-chain
- Set timeouts for external calls: `ctx, cancel := context.WithTimeout(ctx, 5*time.Second)`
- Always `defer cancel()` after creating a cancellable context

## Concurrency

- Every goroutine must have a clear exit path — prevent goroutine leaks
- Use `errgroup` for concurrent operations with error propagation
- Prefer channels for communication, mutexes for state protection
- `defer mu.Unlock()` immediately after `mu.Lock()`

## Function Design

### Early Return の徹底
- アンハッピーパスを先にガード節で追い出す — Go のイディオムそのもの
- ハッピーパスはインデントなしでフラットに書く

### Command-Query Separation
- Query（値を返す）: 副作用なし。呼び出し回数で結果が変わらない
- Command（状態を変える）: 戻り値は error のみ（Go 慣用の例外あり）
- `Queue.Poll()` のような de facto standard は許容

### Split by object, not condition
- switch を1つの関数内で繰り返すのでなく、対象（背景色、アイコン等）ごとの関数に分割
- 新しいケースを追加したとき、全 switch を探す必要がない設計にする

### Definition-Based Programming
- ネスト・メソッドチェーンを名前付き変数で分割する
- 上から下に読めるコード: `userModel := repo.QueryUser(id)` → `result := presenter.Update(userModel)`

## Testing

- Use table-driven tests with `t.Run()` for subtests
- Name test cases descriptively: `{name: "returns error when user not found"}`
- Use `t.Helper()` in test helper functions
- Use `t.Parallel()` where safe for faster execution
