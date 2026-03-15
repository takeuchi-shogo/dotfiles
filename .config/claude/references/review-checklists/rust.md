# Rust Review Checklist

Rust 固有のレビュー観点。`code-reviewer` が `.rs` の変更をレビューする際に参照する。
Effective Rust に基づく。

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

- `must:` `unwrap()` を見つけたら指摘（テストコード内は OK）
- `?` 演算子、`unwrap_or`, `map`, `and_then` を使う
- `Option`/`Result` の変換メソッドを活用する（明示的 `match` より優先）

## RS-3. パターンマッチ網羅性

- `must:` `_` ワイルドカードが新バリアント追加時にバグを隠さないか
- `#[non_exhaustive]` の適切な使用

## RS-4. Clippy 準拠

- `clippy::pedantic` レベルの主要な lint
- 冗長なクロージャ、不要な `return`、`to_string()` vs `to_owned()`

## RS-5. 標準トレイトの実装

- `must:` `Debug` がデータ型に derive されているか（機密情報を含む場合は除く）
- `PartialEq` を実装するなら `Eq` も実装する（float フィールドがない限り）
- `Hash` を実装するなら `Eq` と整合させる
- `HashMap`/`HashSet` のキーに使う型に `Eq + Hash` があるか
- `Display` はユーザー向け出力が必要な型に手動実装する
- トレイト境界は最小限にし、`where` 句で整理する

## RS-6. Iterator 活用

- `for` + `push` → `.map().collect()`
- `.filter().map()` → `.filter_map()`
- 手書きループを標準イテレータメソッドに置き換えられないか

## RS-7. unsafe 最小化

- `must:` `unsafe` には `// SAFETY:` コメントを必須
- 安全な API で `unsafe` を隠蔽する

## RS-8. Derive macro

- `Debug` はほぼ全ての型に付ける
- `serde::Serialize`/`Deserialize` はデータ型に付ける
- `Copy` は小さな値型のみ — 大きな型は明示的 `clone()` を強制する

## RS-9. Newtype パターン

プリミティブ型の混同を防ぐ。`UserId(u64)` + `From`/`Into` 実装。

## RS-10. async Rust (tokio)

- `must:` blocking 操作は `tokio::task::spawn_blocking` を使っているか
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

## RS-14. Drop / RAII パターン

- リソース管理（ファイル、接続、ロック）に `Drop` を実装しているか
- `Drop` を実装する型は `Copy` を derive できないことを理解しているか

## RS-15. ジェネリクス vs トレイトオブジェクト

- `must:` トレイトオブジェクト（`dyn Trait`）が本当に必要か — ジェネリクスをデフォルトにする
- 異種コレクション（`Vec<Box<dyn Shape>>`）が必要な場合のみ `dyn` を使う
- トレイトがオブジェクト安全か確認する

## RS-16. 可視性の最小化

- `must:` 不要に `pub` になっているアイテムがないか
- クレート内部のヘルパーには `pub(crate)` を使う
- `pub` → private は破壊的変更（major バージョン必要）

## RS-17. ワイルドカード import 禁止

- `must:` `use foo::*` を使っていないか（プレリュードを除く）
- 名前衝突と可読性の低下を防ぐ

## RS-18. ドキュメントコメント

- `must:` 公開アイテムに `///` ドキュメントコメントがあるか
- `# Examples` セクションにコード例を含める（doc テストとして実行される）
- `#![warn(missing_docs)]` の有効化を検討する

## RS-19. テスト網羅性

- ユニットテストに加えて統合テスト（`tests/`）があるか
- doc テスト（`///` 内のコード例）が動作するか
- プロパティベーステスト（`proptest`/`quickcheck`）を検討する

## RS-20. セマンティックバージョニング

- `must:` 公開 API の破壊的変更が major バージョンと整合しているか
- `#[non_exhaustive]` で enum/struct の将来の拡張を許可しているか
- 依存クレートの型が公開 API に露出する場合は `pub use` で再エクスポートする
