---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript Rules

## Strict Typing

- NEVER use `any` — use `unknown` and narrow with type guards
- Minimize `as` casts — prefer type narrowing or generics
- Leverage type inference — don't annotate when the compiler can infer
- Enable `strict: true` in tsconfig — no exceptions

```typescript
// BAD: any loses all type safety
function parse(data: any) { return data.name; }

// GOOD: unknown forces safe narrowing
function parse(data: unknown): string {
  if (typeof data === "object" && data !== null && "name" in data) {
    return (data as { name: string }).name;
  }
  throw new Error("Invalid data");
}
```

## Discriminated Unions

- Use tagged unions for type-safe branching over string/boolean checks
- Always handle all variants — enable `noUncheckedIndexedAccess`

```typescript
type Result<T> =
  | { status: "ok"; data: T }
  | { status: "error"; error: Error };
```

## satisfies Operator

- Use `satisfies` to validate a value matches a type while preserving inference
- Prefer over `as const` + type annotation when you need both safety and narrowing

```typescript
const config = {
  port: 3000,
  host: "localhost",
} satisfies ServerConfig;
```

## Utility Types

- Use `Pick<T, K>` / `Omit<T, K>` to derive focused types from existing ones
- Use `Partial<T>` for update payloads — `Required<T>` for creation payloads
- Use `Record<K, V>` for dictionaries instead of `{ [key: string]: V }`
- Prefer `Readonly<T>` for function parameters that should not be mutated

## Const & Readonly

- Use `as const` for literal tuples, enums-as-objects, and config values
- Mark arrays and objects as `readonly` when mutation is not intended
- Prefer `ReadonlyArray<T>` in function signatures accepting arrays
