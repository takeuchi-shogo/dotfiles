---
paths:
  - "**/*.rs"
  - "**/Cargo.toml"
---

# Rust Rules

## Ownership & Borrowing

- Prefer borrowing (`&T`, `&mut T`) over cloning — `clone()` is a code smell
- Use `&str` for function parameters, `String` for owned storage
- Keep lifetimes simple — elision covers most cases, annotate only when required
- Avoid `Rc`/`Arc` unless shared ownership is genuinely needed

## Error Handling

- Use `Result<T, E>` for recoverable errors — never `panic!` in library code
- Define domain errors with `thiserror`: `#[derive(Error, Debug)]`
- Use `anyhow::Result` in application code, `thiserror` in library code
- Propagate with `?` — avoid manual `match` on `Result` when context isn't needed
- Add context: `foo().context("failed to load config")?`

## Pattern Matching

- Prefer `match` over chains of `if let` — exhaustive matching catches missed variants
- Use `_` wildcard sparingly — explicit variants catch future additions at compile time
- Destructure in match arms: `Some(User { name, .. }) =>`

## Type System

- Use newtypes to enforce invariants: `struct UserId(u64)` over bare `u64`
- Prefer enums over boolean flags: `enum Visibility { Public, Private }`
- Derive traits generously: `#[derive(Debug, Clone, PartialEq, Eq, Hash)]`
- Use `impl Into<T>` / `AsRef<T>` for flexible function parameters

## Concurrency

- Prefer `tokio` channels over shared state with `Mutex`
- Use `Arc<Mutex<T>>` only when channel-based design doesn't fit
- Mark async functions explicitly — avoid blocking calls inside async contexts
- Use `tokio::spawn` with proper error handling, not fire-and-forget

## Idiomatic Patterns

- Use iterators over manual loops: `.iter().filter().map().collect()`
- Prefer `if let` / `let else` for single-variant matching
- Use `Default` trait: `#[derive(Default)]` and `..Default::default()`
- Clippy is law — `#![warn(clippy::all, clippy::pedantic)]`
