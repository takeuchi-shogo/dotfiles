---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.go"
  - "**/*.py"
  - "**/*.rs"
---

# Error Handling

## Principles

1. **Handle errors explicitly** — Never silently swallow errors
2. **Fail fast** — Detect errors early, report them immediately
3. **Structured logging** — Use structured formats for server-side errors
4. **User-friendly messages** — Generic messages for users, detailed logs for developers
5. **Recovery when possible** — Graceful degradation over hard failures

## Patterns

### DO
- Return typed errors (not strings)
- Log error context (what operation failed, with what input)
- Use error boundaries in React (ErrorBoundary components)
- Validate inputs at system boundaries
- Use `try/catch` only when you can meaningfully handle the error

### DON'T
- Catch and ignore errors (`catch (e) {}`)
- Log sensitive data in error messages
- Expose stack traces to users
- Use `catch` as control flow
- Swallow errors with `|| true` unless intentional and documented

### Few-shot Examples

```typescript
// NG: 握り潰し
try { await saveUser(data); } catch (e) {}

// OK: ログ + rethrow（userId のみ — data 全体はログしない）
try { await saveUser(data); } catch (e) {
  logger.error("saveUser failed", { userId: data.id, error: e });
  throw e;
}
```

```typescript
// NG: 曖昧メッセージ
throw new Error("Error occurred");

// OK: 入力値 + 操作 + 原因を含む
throw new Error(`Failed to update user ${userId}: email validation failed - ${detail}`);
```

## Language-Specific

### TypeScript
```typescript
// Use Result pattern or throw typed errors
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
```

### Go
```go
// Always check error returns
if err != nil {
    return fmt.Errorf("operation failed: %w", err)
}
```
