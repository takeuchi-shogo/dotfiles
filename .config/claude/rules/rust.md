---
paths:
  - "**/*.rs"
  - "**/Cargo.toml"
---

# Rust Rules

Effective Rust・Rust API Guidelines に基づく。

## 所有権と借用

- 借用（`&T`, `&mut T`）をクローンより優先する — `clone()` はコードスメル
- 関数パラメータには `&str` を使い、所有が必要な場合のみ `String` を受け取る
- ライフタイムはシンプルに保つ — 省略規則がほとんどのケースをカバーする
- `Rc`/`Arc` は共有所有権が本当に必要な場合のみ使う
- `Cow<'_, str>` で所有/借用を柔軟に扱う

## エラーハンドリング

- 回復可能なエラーには `Result<T, E>` を使う — ライブラリコードで `panic!` しない
- ドメインエラーは `thiserror` で定義: `#[derive(Error, Debug)]`
- アプリケーションコードでは `anyhow::Result`、ライブラリでは `thiserror`
- `?` 演算子で伝播する — コンテキストが不要なら手動 `match` を避ける
- コンテキストを追加する: `foo().context("failed to load config")?`
- `Option`/`Result` の変換メソッドを活用する（ET Item 3）— `map`, `and_then`, `unwrap_or_else` 等

## パターンマッチ

- `if let` チェーンより `match` を優先する — 網羅的マッチングがバリアント漏れをコンパイル時に検出する
- `_` ワイルドカードは控えめに使う — 明示的なバリアントが将来の追加を検出する
- match アームで分解する: `Some(User { name, .. }) =>`
- 単一バリアントには `if let` / `let else` を使う

## 型システム

### Newtype パターン（ET Item 6）

不変条件を強制する: `struct UserId(u64)` — 素の `u64` より安全

### enum を boolean フラグより優先する

```rust
// NG
fn set_visibility(visible: bool) { ... }

// OK
enum Visibility { Public, Private }
fn set_visibility(v: Visibility) { ... }
```

### 型変換（ET Item 5）

- `From`/`Into`: 無損失変換。`From<T>` を実装すれば `Into` は自動導出
- `TryFrom`/`TryInto`: 失敗しうる変換
- `AsRef<T>`/`AsMut<T>`: 安価な参照変換
- 関数パラメータには `impl Into<T>` / `impl AsRef<T>` で柔軟性を持たせる

### Builder パターン（ET Item 7）

3個以上のオプショナルフィールドがある型で Builder を検討する。`derive_builder` クレート活用。

## 標準トレイトの活用（ET Item 10）

### derive すべきトレイト

| トレイト | ガイドライン |
|---|---|
| `Debug` | ほぼ全ての型に付ける（機密情報を含む場合は除く） |
| `Clone` | 全フィールドが Clone なら derive する。RAII 型やユニークリソースには付けない |
| `Copy` | 小さな値型のみ。大きな型は明示的 `clone()` を強制する |
| `PartialEq` + `Eq` | ユーザー定義型では両方実装する（float フィールドがない限り） |
| `Hash` | `HashMap`/`HashSet` のキーに使う型に必須。`Eq` と整合させる |
| `Default` | ゼロ引数コンストラクタ。`..Default::default()` で struct 更新構文に使える |
| `serde::Serialize`/`Deserialize` | データ型に付ける |

### 手動実装すべきトレイト

- `Display`: ユーザー向けテキスト出力（derive 不可）
- `Error`: `Display + Debug` を要求。`thiserror` で導出
- `From`/`Into`: 型変換
- `Drop`: RAII パターン（リソースクリーンアップ）
- `Iterator`: カスタムイテレータ

### マーカートレイト

- `Send`: スレッド間転送可能（コンパイラ自動実装）
- `Sync`: 複数スレッドから参照安全（コンパイラ自動実装）

## ジェネリクス vs トレイトオブジェクト（ET Item 12）

**ジェネリクスを優先する**（デフォルト）:
- 複数のトレイト境界が必要な場合
- パフォーマンスが重要な場合（単相化で直接呼び出し）
- コンパイル時に型情報を保持したい場合

**トレイトオブジェクト（`dyn Trait`）を使う場合**:
- 異種コレクション（`Vec<Box<dyn Shape>>`）
- バイナリサイズやコンパイル時間を削減したい場合
- 型消去が必要な場合

トレイトオブジェクトにはオブジェクト安全性が必要 — メソッドがジェネリックだったり `Self` を返したりできない。

## Drop トレイト / RAII パターン（ET Item 11）

スコープ終了時の自動クリーンアップに `Drop` を実装する:

```rust
impl Drop for TempFile {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.path);
    }
}
```

- ファイル、ネットワーク接続、ロック等のリソース管理に使う
- `Drop` を実装する型は `Copy` を derive できない

## 並行処理

- `tokio` チャネルを `Mutex` による共有状態より優先する
- `Arc<Mutex<T>>` はチャネルベース設計が適さない場合のみ使う
- async 関数内でブロッキング呼び出しをしない — `tokio::task::spawn_blocking` を使う
- `tokio::spawn` にはエラーハンドリングを付ける（fire-and-forget しない）
- 共有状態の並行処理には注意する（ET Item 17）— データ競合はコンパイラが防ぐが、論理的な競合は防げない

## 可視性の最小化（ET Item 22）

- デフォルトは private — 必要な場合のみ `pub` にする
- クレート内部のヘルパーには `pub(crate)` を使う
- private → public は minor バージョンで可能だが、逆は major バージョンが必要
- 公開 API の表面積を小さく保つ

## Import（ET Item 23）

- ワイルドカード import（`use foo::*`）を避ける — 名前衝突と可読性の低下を招く
- プレリュード（`use std::io::prelude::*`）は標準ライブラリの慣習に従う場合のみ OK
- `pub use` で公開 API を整理し、内部構造を隠す（ET Item 24）

## ドキュメント（ET Item 27）

- 公開アイテムには `///` ドキュメントコメントを書く
- モジュールには `//!` を使う
- `# Examples` セクションにコード例を含める — rustdoc がテストとして実行する
- `cargo doc --open` で確認する
- `#![warn(missing_docs)]` で未文書の公開アイテムを検出する

## テスト（ET Item 30）

- ユニットテスト以外も書く:
  - **Doc テスト**: `///` 内のコード例は `cargo test` で自動実行される
  - **統合テスト**: `tests/` ディレクトリに外部から API を検証するテストを置く
  - **プロパティベーステスト**: `proptest` / `quickcheck` で境界値を自動探索する
- `#[cfg(test)] mod tests` でユニットテストを分離する

## ツール

- `cargo fmt` でフォーマットを統一する
- `cargo clippy` に従う — `#![warn(clippy::all, clippy::pedantic)]`
- `cargo test` を CI で実行する
- リフレクション（`Any` 型、`TypeId`）を避ける（ET Item 19）— 型安全性を損なう
- 過度な最適化を避ける（ET Item 20）— まずプロファイルを取る

## マクロ（ET Item 28）

- マクロは控えめに使う — コンパイルエラーが分かりにくくなる
- `derive` マクロは積極的に活用する
- 宣言マクロ（`macro_rules!`）はボイラープレート削減に有用だが、複雑なロジックには関数やジェネリクスを優先する

## セマンティックバージョニング（ET Item 21）

- 公開 API の破壊的変更は major バージョンで行う
- `pub` アイテムの追加は minor バージョン
- バグ修正は patch バージョン
- `#[non_exhaustive]` で enum/struct の将来の拡張を許可する
