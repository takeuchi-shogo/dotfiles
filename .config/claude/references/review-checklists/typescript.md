# TypeScript Review Checklist

TypeScript/JavaScript 固有のレビュー観点。`code-reviewer` が `.ts/.tsx/.js/.jsx` の変更をレビューする際に参照する。

## 命名規約

- `camelCase` for variables/functions, `PascalCase` for types/components
- Boolean は `is`/`has`/`should` プレフィックス
- イベントハンドラは `handle` + 動詞（`handleClick`）、props は `on` + 動詞（`onClick`）

## TS-1. 型の厳密さ — `any` 禁止

`any` は型安全性を完全に破壊する。代わりに `unknown` を使い、型ガードで絞り込む。

- `must:` `any` を見つけたら必ず指摘
- `as any` によるキャストも同様
- やむを得ない場合は `// eslint-disable-next-line` + 理由コメントを要求

## TS-2. Discriminated Union

Union 型には判別プロパティ（`type`/`kind`）を持たせ、switch 文で網羅性を保証する。

## TS-3. Utility Types の活用

`Partial`, `Pick`, `Omit`, `Record`, `Readonly<T>` で型の重複を防ぐ。手書きで部分型を再定義していたら指摘。

## TS-4. 型推論バランス

- 変数の初期化: 推論に任せてよい
- 関数の戻り値: 公開 API は明示、内部関数は省略可

## TS-5. Branded Types

プリミティブ型の混同を防ぐ。`type UserId = string & { readonly __brand: 'UserId' }`

## TS-6. Nullish 処理

`??`/`?.` を適切に使う。`||` で falsy 値（`0`, `""`, `false`）を意図せず除外していないか。

## TS-7. Import 整理 — `import type`

型のみの import には `import type` を使う。バンドルサイズ最適化に直結。

## TS-8. Async/Await パターン

- `await` の不要な直列化を検出（`Promise.all` で並列化できるケース）
- `async` 関数内で `.then()/.catch()` を混在させない

## TS-9. Immutability — `readonly` / `as const`

- 配列パラメータ: `readonly T[]`
- 定数オブジェクト: `as const` assertion
- `Readonly<T>` で immutability を型レベルで保証

## TS-10. Zod スキーマバリデーション

外部入力（API レスポンス、フォーム、環境変数）には Zod でバリデーション。`z.infer<typeof schema>` で二重定義を回避。

## TS-11. React 固有パターン

- `must:` リスト要素の `key` に index を使っていないか
- hooks のルール違反（条件分岐内/ループ内での使用）
- コンポーネントの props が 5 個超で分割検討
- `useEffect` の依存配列が正しいか

## TS-12. Exhaustive Switch — `satisfies never`

Discriminated union の switch 文には `default: { const _exhaustive: never = action; }` を入れる。

## TS-13. Node.js エラーハンドリング

- `must:` `process.on('unhandledRejection')` のハンドラ設定
- `must:` Express/Hono 等のエラーミドルウェアの存在
- async ルートハンドラのエラーキャッチ

## TS-14. ミドルウェア・DI 設計

- ミドルウェア順序: 認証 → バリデーション → ビジネスロジック
- ルートハンドラが薄いか（ビジネスロジックはサービス層に委譲）

## TS-15. 環境変数・設定の型安全性

`process.env.XXX` を直接使わず、起動時に Zod/envalid でバリデーション。機密情報がログに出力されていないか。
