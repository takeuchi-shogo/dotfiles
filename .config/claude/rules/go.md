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

- MixedCaps only — no underscores in exported names
- Package names: short, lowercase, single word (e.g. `user`, `http`)
- Receiver names: 1-2 letter abbreviation of type (e.g. `s` for `Server`)
- Interfaces: single-method interfaces use `-er` suffix (`Reader`, `Writer`)

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

## Testing

- Use table-driven tests with `t.Run()` for subtests
- Name test cases descriptively: `{name: "returns error when user not found"}`
- Use `t.Helper()` in test helper functions
- Use `t.Parallel()` where safe for faster execution
