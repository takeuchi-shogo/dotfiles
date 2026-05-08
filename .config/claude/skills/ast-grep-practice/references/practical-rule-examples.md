# ast-grep Practical Rule Examples

`/ast-grep-practice` skill の Practical rule examples セクションを切り出した詳細カタログ。
SKILL.md からは summary table のみ参照され、ここで完全な YAML snippet を保持する。

---

## TypeScript: forbid `as any` casts (detection only, no fix)

```yaml
id: no-as-any
language: TypeScript
severity: error
rule:
  pattern: $EXPR as any
message: as any disables the type system. Go through as unknown or a type guard.
note: |
  Why no auto-fix: mechanically replacing `as any` → `as unknown` changes type
  inference results and introduces new compile errors at call sites. Detection-only,
  migrate manually.
```

When matching a type assertion like `as any`, `$EXPR as any` works on the `as_expression` node. `$EXPR` matches the whole left-hand side, so it matches both `JSON.parse(raw) as any` and `(value as any)`.

## TypeScript: rewrite a deprecated API

```yaml
id: migrate-old-api
language: TypeScript
severity: error
rule:
  pattern: oldClient.fetch($URL, $OPTS)
fix: newClient.request($URL, $OPTS)
message: oldClient.fetch is deprecated. Migrate to newClient.request.
```

## Forbid a specific import

```yaml
id: no-lodash-import
language: TypeScript
severity: warning
rule:
  pattern: import $_ from 'lodash'
message: Do not import lodash wholesale. Use lodash/xxx.
fix: import $_ from 'lodash/xxx' // TODO: fix the correct path
```

## TypeScript: forbid direct fetch inside React components

```yaml
id: no-fetch-in-component
language: TypeScript
severity: warning
rule:
  pattern: fetch($$$ARGS)
  inside:
    any:
      - kind: function_declaration
        has:
          field: return_type
          pattern: JSX.Element
      - kind: arrow_function
        inside:
          kind: variable_declarator
          regex: '^[A-Z]'
    stopBy: end
message: Do not fetch directly inside a component. Use hooks or a server action.
```

## Rust: forbid unwrap()

```yaml
id: no-unwrap
language: Rust
severity: warning
rule:
  pattern: $EXPR.unwrap()
  not:
    inside:
      kind: function_item
      regex: '#\[test\]'
      stopBy: end
message: Do not use unwrap() outside tests. Use ? or expect().
note: unwrap() panics, so avoid it in production code.
```

## Rust: flag unsafe blocks

```yaml
id: flag-unsafe-block
language: Rust
severity: warning
rule:
  kind: unsafe_block
message: unsafe block. Explain the safety rationale in a comment.
```

## Rust: migrate println! to log macros

```yaml
id: no-println-in-lib
language: Rust
severity: warning
rule:
  pattern: println!($$$ARGS)
  not:
    inside:
      kind: function_item
      regex: 'fn main'
      stopBy: end
message: Do not use println! in library code. Use log::info! etc.
fix: log::info!($$$ARGS)
files:
  - "src/lib.rs"
  - "src/**/mod.rs"
  - "src/**/*.rs"
ignores:
  - "src/main.rs"
  - "src/bin/**"
```

## Go: detect ignored errors

```yaml
id: no-ignored-error
language: Go
severity: error
rule:
  kind: short_var_declaration
  has:
    kind: identifier
    regex: '^_$'
    field: left
  has:
    kind: call_expression
    field: right
    stopBy: end
message: Do not ignore errors with _. Handle them appropriately.
```

## Go: prevent forgetting defer Close()

```yaml
id: defer-close-after-open
language: Go
severity: warning
rule:
  kind: short_var_declaration
  has:
    pattern: os.Open($PATH)
    field: right
    stopBy: end
  not:
    precedes:
      pattern: defer $_.Close()
      stopBy:
        kind: return_statement
message: Add defer Close() immediately after os.Open.
```

## Python: forbid bare except

```yaml
id: no-bare-except
language: Python
severity: warning
rule:
  kind: except_clause
  not:
    has:
      kind: identifier
      stopBy: neighbor
message: Do not use bare except. Specify the exception type.
```

## Python: migrate print() to a logger

```yaml
id: no-print-in-src
language: Python
severity: warning
rule:
  pattern: print($$$ARGS)
  not:
    inside:
      kind: function_definition
      regex: 'def main'
      stopBy: end
message: Use logger instead of print().
fix: logger.info($$$ARGS)
files:
  - "src/**"
```
