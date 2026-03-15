---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript Rules

Effective TypeScript (2nd Ed.)・TypeScript 公式ドキュメントに基づく。

## 型システムの基礎

### 構造的型付けを理解する（ET Item 4）

TypeScript は構造的型付け（ダックタイピング）。名前ではなく形で互換性を判定する:

```typescript
interface Point { x: number; y: number }
const obj = { x: 1, y: 2, z: 3 };
const p: Point = obj; // OK — 余分なプロパティがあっても構造が合えば通る
```

ただし、オブジェクトリテラルを直接代入する場合のみ「余剰プロパティチェック」が働く。

### 型は値の集合として考える（ET Item 7）

- `never` = 空集合（どの値も属さない）
- リテラル型 = 単一要素の集合
- `string | number` = 和集合
- `A & B` = 交差集合（両方のプロパティを持つ）
- `unknown` = 全体集合

## 厳格な型付け

### `any` 禁止

- `any` は型安全性を完全に破壊する — 代わりに `unknown` を使い、型ガードで絞り込む
- `as any` によるキャストも同様に禁止
- やむを得ない場合は `// eslint-disable-next-line` + 理由コメントを要求
- `any` より精密な代替を使う: `unknown`, `object`, `Record<string, unknown>`, `unknown[]`（ET Item 44）

```typescript
// NG
function parse(data: any) { return data.name; }

// OK
function parse(data: unknown): string {
  if (typeof data === "object" && data !== null && "name" in data) {
    return (data as { name: string }).name;
  }
  throw new Error("Invalid data");
}
```

### Object Wrapper Types を使わない（ET Item 10）

```typescript
// NG: ラッパー型
const s: String = "hello";
const n: Number = 42;
const b: Boolean = true;

// OK: プリミティブ型
const s: string = "hello";
const n: number = 42;
const b: boolean = true;
```

### `as` キャストを最小化する

- 型アサーションより型ナローイングやジェネリクスを優先する
- 安全でない型アサーションは型安全な関数の中に隠す（ET Item 45）:

```typescript
// 内部で as を使うが、関数シグネチャは安全
function safeGet<T>(map: Map<string, unknown>, key: string, guard: (v: unknown) => v is T): T | undefined {
  const val = map.get(key);
  return val !== undefined && guard(val) ? val : undefined;
}
```

### tsconfig 推奨設定

`strict: true` は必須。加えて以下を推奨（TypeScript 5.9 のデフォルトに準拠）:

```jsonc
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,    // インデックスアクセスに undefined を含める
    "exactOptionalPropertyTypes": true,   // optional と undefined を区別
    "verbatimModuleSyntax": true,         // import type の強制
    "isolatedModules": true,             // バンドラー互換性
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

## 型推論

### 推論に任せ、不要な型注釈を書かない（ET Item 18）

```typescript
// 冗長: コンパイラが推論できる
const x: number = 10;
const arr: string[] = ["a", "b"];

// OK: 推論に任せる
const x = 10;
const arr = ["a", "b"];
```

ただし、公開 API の関数戻り値は明示する（意図の文書化 + エラー発生位置の改善）。

### オブジェクトは一括で作成する（ET Item 21）

```typescript
// NG: 段階的に構築すると型エラー
const pt = {};
pt.x = 1;  // Error: Property 'x' does not exist on type '{}'

// OK: 一括作成
const pt: Point = { x: 1, y: 2 };

// スプレッドで段階的に組み立てる場合
const pt = { ...base, x: 1 };
```

## 型設計

### Discriminated Union

タグ付きユニオンで型安全な分岐を行う。string/boolean による条件分岐より優先する:

```typescript
type Result<T> =
  | { status: "ok"; data: T }
  | { status: "error"; error: Error };
```

`noUncheckedIndexedAccess` を有効にし、全てのバリアントを網羅する。

### `satisfies` 演算子

値が型に適合することを検証しつつ、推論された狭い型を保持する:

```typescript
const config = {
  port: 3000,
  host: "localhost",
} satisfies ServerConfig;
// config.port は number ではなく 3000 として推論される
```

### Null をペリメータに押し出す（ET Item 33）

```typescript
// NG: null が型全体に散らばる
interface User { name: string | null; email: string | null }

// OK: null をペリメータに
interface User { name: string; email: string }
function getUser(id: string): User | null { ... }
```

### 受け入れは寛容に、出力は厳格に（ET Item 30）

関数の入力には広い型（`Iterable`, `ArrayLike`, `readonly T[]`）を受け入れ、出力には具体的な型を返す。

### Optional プロパティを制限する（ET Item 37）

optional プロパティが多いと組み合わせ爆発を起こす。必須と optional を別の型に分離するか、discriminated union で表現する。

### 不正確より不精密を選ぶ（ET Item 40）

型が実態と矛盾するくらいなら、精度を落としても正確な型を使う。嘘をつく型は `any` より有害。

### 不要な型パラメータを避ける（ET Item 51）

```typescript
// NG: T が戻り値でしか使われず、呼び出し側の推論に頼れない
function parse<T>(input: string): T { ... }

// OK: unknown を返し、呼び出し側で narrowing
function parse(input: string): unknown { ... }
```

## Utility Types

- `Pick<T, K>` / `Omit<T, K>` で既存型から部分型を導出する
- `Partial<T>` を更新ペイロードに、`Required<T>` を作成ペイロードに使う
- `Record<K, V>` を辞書型に使う（`{ [key: string]: V }` より推奨）
- `Readonly<T>` / `ReadonlyArray<T>` で関数パラメータの不変性を保証する
- `as const` でリテラルタプル、enum 代替オブジェクト、設定値を定義する

## Branded Types（公称型）

プリミティブ型の混同を防ぐ:

```typescript
type UserId = string & { readonly __brand: "UserId" };
type ArticleId = string & { readonly __brand: "ArticleId" };

function getUser(id: UserId): User { ... }
// getUser(articleId) → コンパイルエラー
```

## Import

- 型のみの import には `import type` を使う — バンドルサイズ最適化に直結
- `verbatimModuleSyntax: true` で強制する

```typescript
import type { User } from "./types";
import { getUser } from "./api";
```

## Nullish 処理

- `??`（nullish coalescing）を使う — `||` は `0`, `""`, `false` を意図せず除外する
- `?.`（optional chaining）で安全にプロパティアクセスする
- `null` と `undefined` を区別するなら `exactOptionalPropertyTypes: true` を設定する

## エラーハンドリング

- 外部入力（API レスポンス、フォーム、環境変数）には Zod でバリデーションする
- `z.infer<typeof schema>` で型の二重定義を回避する
- Result パターンを検討する:

```typescript
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
```

## ドキュメント

### TSDoc（ET Item 68）

公開 API には TSDoc コメントを書く。型情報を散文で繰り返さない（ET Item 31）:

```typescript
// NG: 型情報を繰り返している
/** @param name ユーザー名（string型） @returns User オブジェクト */

// OK: 型に書けないことだけ書く
/** ユーザーをIDで検索する。見つからない場合は null を返す。 */
function getUser(id: UserId): User | null { ... }
```

## テスト

- 型のテストを書く（ET Item 55） — `expectTypeOf`（vitest）や `tsd` で型リグレッションを検出する
- 型チェックとユニットテストの保証範囲は異なる（ET Item 77）— 両方必要

## 依存関係

- `@types/*` パッケージは `devDependencies` に置く（ET Item 65）
- TypeScript 本体も `devDependencies` に置く
