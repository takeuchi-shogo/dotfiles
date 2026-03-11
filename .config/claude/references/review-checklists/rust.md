# Rust Review Checklist

Rust 固有のレビュー観点。`code-reviewer` が `.rs` の変更をレビューする際に参照する。

## 命名規約

- 関数・変数・モジュール: `snake_case`
- 型・トレイト: `PascalCase`
- 定数・static: `SCREAMING_SNAKE_CASE`
- ライフタイム: 短い小文字（`'a`, `'ctx`）

## RS-1. 所有権とライフタイム — 不要な `.clone()` 検出

- `must:` 不要な `.clone()` がないか（借用で済むケース）
- `must:` `String` を受け取る関数が `&str` で済まないか
- `Cow<'_, str>` で所有/借用を柔軟にする

## RS-2. Result/Option — `unwrap()` 禁止

- `must:` `unwrap()` を見つけたら必ず指摘（テストコード内は OK）
- `?` 演算子、`unwrap_or`, `map`, `and_then` を使う

## RS-3. パターンマッチ網羅性

- `must:` `_` ワイルドカードが新バリアント追加時にバグを隠さないか
- `#[non_exhaustive]` の適切な使用

## RS-4. Clippy 準拠

- `clippy::pedantic` レベルの主要な lint
- 冗長なクロージャ、不要な `return`、`to_string()` vs `to_owned()`

## RS-5. Trait 設計

- 標準トレイトの実装（`Display`, `Debug`, `Default`, `From`/`Into`）
- トレイト境界は最小限、`where` 句で整理

## RS-6. Iterator 活用

- `for` + `push` → `.map().collect()`
- `.filter().map()` → `.filter_map()`

## RS-7. unsafe 最小化

- `must:` `unsafe` には `// SAFETY:` コメントを必須
- 安全な API で `unsafe` を隠蔽する

## RS-8. Derive macro

- `Debug` はほぼ全ての型に付ける
- `serde::Serialize`/`Deserialize` for data types

## RS-9. Newtype パターン

プリミティブ型の混同を防ぐ。`UserId(u64)` + `From`/`Into` 実装。

## RS-10. async Rust (tokio)

- `must:` blocking 操作は `tokio::task::spawn_blocking`
- `tokio::select!` のキャンセル安全性
- `Arc<Mutex<T>>` vs `tokio::sync::Mutex<T>` の使い分け

## RS-11. メモリ効率 — `Box`/`Rc`/`Arc`

- `Box<T>`: 単一所有者、`Rc<T>`: 単一スレッド共有、`Arc<T>`: スレッド間共有
- 不要なヒープ割り当てを避ける

## RS-12. Module 構成

- 2018 edition 以降は `foo.rs` + `foo/` が推奨
- `pub use` で公開 API を整理
- テスト: `#[cfg(test)] mod tests`

## RS-13. Builder パターン

3個以上のオプショナルフィールドで Builder を検討。`derive_builder` クレート活用。
