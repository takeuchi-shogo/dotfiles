---
status: reference
last_reviewed: 2026-04-23
---

# TypeScript Review Checklist

TypeScript/JavaScript 固有のレビュー観点。`code-reviewer` が `.ts/.tsx/.js/.jsx` の変更をレビューする際に参照する。
Effective TypeScript (2nd Ed.) に基づく。

## 命名規約

- `camelCase` で変数/関数、`PascalCase` で型/コンポーネント
- Boolean は `is`/`has`/`should` プレフィックス
- イベントハンドラは `handle` + 動詞（`handleClick`）、props は `on` + 動詞（`onClick`）

## TS-1. 型の厳密さ — `any` 禁止

- `must:` `any` を見つけたら指摘 — `unknown` を使い型ガードで絞り込む
- `must:` `as any` によるキャストも同様
- より精密な代替を推奨: `unknown`, `object`, `Record<string, unknown>`, `unknown[]`
- やむを得ない場合は理由コメントを要求

## TS-2. Discriminated Union

- Union 型には判別プロパティ（`type`/`kind`/`status`）を持たせる
- switch 文で網羅性を保証する（`satisfies never` パターン）

## TS-3. Utility Types の活用

- `Partial`, `Pick`, `Omit`, `Record`, `Readonly<T>` で型の重複を防ぐ
- 手書きで部分型を再定義していたら指摘

## TS-4. 型推論バランス

- 変数の初期化: 推論に任せてよい（不要な型注釈を書かない）
- 関数の戻り値: 公開 API は明示、内部関数は省略可
- `must:` コンパイラが推論できる箇所に冗長な型注釈を書いていないか

## TS-5. Branded Types

- プリミティブ型の混同を防ぐ: `type UserId = string & { readonly __brand: 'UserId' }`
- ID 系の値を素の `string` や `number` で扱っていたら検討

## TS-6. Nullish 処理

- `??`/`?.` を適切に使う
- `must:` `||` で falsy 値（`0`, `""`, `false`）を意図せず除外していないか

## TS-7. Import 整理 — `import type`

- 型のみの import には `import type` を使う — バンドルサイズ最適化に直結
- `verbatimModuleSyntax: true` で強制する

## TS-8. Async/Await パターン

- `must:` `await` の不要な直列化を検出（`Promise.all` で並列化できるケース）
- `async` 関数内で `.then()/.catch()` を混在させない

## TS-9. Immutability — `readonly` / `as const`

- 配列パラメータ: `readonly T[]` または `ReadonlyArray<T>`
- 定数オブジェクト: `as const`
- `Readonly<T>` で immutability を型レベルで保証

## TS-10. Zod スキーマバリデーション

- 外部入力（API レスポンス、フォーム、環境変数）には Zod でバリデーション
- `z.infer<typeof schema>` で二重定義を回避

## TS-11. React 固有パターン

- `must:` リスト要素の `key` に index を使っていないか
- hooks のルール違反（条件分岐内/ループ内での使用）
- コンポーネントの props が 5 個超で分割検討
- `must:` `useEffect` を直接使っていないか — `useMountEffect` のみ許可
  - 派生状態の同期 → インライン計算に置き換え
  - データフェッチ → `useQuery` / `useSWR` 等に置き換え
  - ユーザーアクション → イベントハンドラで直接処理
  - props 変更でリセット → `key` でリマウント
  - マウント時の外部同期のみ `useMountEffect(effect: () => void | (() => void))` を使用

## TS-12. Exhaustive Switch — `satisfies never`

- Discriminated union の switch 文に `default: { const _exhaustive: never = action; }` を入れる

## TS-13. Node.js エラーハンドリング

- `must:` `process.on('unhandledRejection')` のハンドラ設定
- `must:` Express/Hono 等のエラーミドルウェアの存在
- async ルートハンドラのエラーキャッチ

## TS-14. ミドルウェア・DI 設計

- ミドルウェア順序: 認証 → バリデーション → ビジネスロジック
- ルートハンドラが薄いか（ビジネスロジックはサービス層に委譲）

## TS-15. 環境変数・設定の型安全性

- `process.env.XXX` を直接使わず、起動時に Zod/envalid でバリデーション
- 機密情報がログに出力されていないか

## TS-16. Object Wrapper Types 禁止

- `must:` `String`, `Number`, `Boolean`, `Object` を型注釈に使っていないか
- プリミティブ型 `string`, `number`, `boolean`, `object` を使う

## TS-17. Null ペリメータ設計

- `must:` 型のフィールドに `| null` が散在していないか
- null はペリメータ（関数の戻り値等）に押し出し、内部の型は非 null にする

## TS-18. `satisfies` 演算子の活用

- 型検証と推論の保持を両立したい場合に `satisfies` を使う
- `as const satisfies Config` パターンで設定値を安全に定義する

## TS-19. tsconfig 推奨設定

新規プロジェクトでは以下が有効か確認:
- `noUncheckedIndexedAccess: true` — インデックスアクセスに `| undefined` を含める
- `exactOptionalPropertyTypes: true` — optional と `undefined` を区別
- `verbatimModuleSyntax: true` — `import type` の強制
- `isolatedModules: true` — バンドラー互換性

## TS-20. 型テスト

- 共有ユーティリティ型やライブラリの型には `expectTypeOf`（vitest）や `tsd` でテストを書く
- 型のリグレッションを CI で検出する

## TS-21. `@types` の配置

- `@types/*` と TypeScript 本体は `devDependencies` に置く
- `dependencies` に含まれていたら指摘

## TS-22. TSDoc

- 公開 API には TSDoc コメントを書く
- 型情報を散文で繰り返さない（型に書けないことだけ書く）

## TS-23. Optional プロパティの制限

- optional プロパティが多い型（5個超）は設計の見直しを検討
- 必須と optional を別の型に分離するか、discriminated union で表現する
