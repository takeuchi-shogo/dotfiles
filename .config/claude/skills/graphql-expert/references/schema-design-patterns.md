# スキーマ設計パターン集

## Connection パターン（Relay 準拠ページネーション）

### 完全な型定義

```graphql
type Query {
  """注文一覧を取得する。カーソルベースのページネーション対応。"""
  orders(
    "先頭から取得する件数"
    first: Int
    "このカーソル以降のデータを取得"
    after: String
    "末尾から取得する件数"
    last: Int
    "このカーソル以前のデータを取得"
    before: String
    "フィルタ条件"
    filter: OrderFilterInput
  ): OrderConnection!
}

type OrderConnection {
  """接続内のエッジ一覧"""
  edges: [OrderEdge!]!
  """ページネーション情報"""
  pageInfo: PageInfo!
  """フィルタ条件に一致する総件数"""
  totalCount: Int
}

type OrderEdge {
  """このエッジのカーソル（不透明な文字列）"""
  cursor: String!
  """エッジが指すノード"""
  node: Order!
}

type PageInfo {
  """次のページが存在するか"""
  hasNextPage: Boolean!
  """前のページが存在するか"""
  hasPreviousPage: Boolean!
  """最初のエッジのカーソル"""
  startCursor: String
  """最後のエッジのカーソル"""
  endCursor: String
}
```

### 設計ルール

- カーソルは**不透明な文字列**にする（Base64 エンコードが一般的）
- `first/after`（前方走査）と `last/before`（後方走査）の両方をサポート
- Edge にリレーション固有のメタデータを持たせられる（例: `role` in `TeamMemberEdge`）
- `totalCount` はオプション（大規模データでは計算コストが高い）

### Edge メタデータの例

```graphql
type TeamMemberEdge {
  cursor: String!
  node: User!
  """チームにおけるこのメンバーの役割"""
  role: TeamRole!
  """チームに参加した日時"""
  joinedAt: DateTime!
}
```

### Simple List vs Connection の判断

| 条件 | パターン |
|------|---------|
| 要素数 ≤ 20 で増加しない | `[Tag!]!`（Simple List） |
| 要素数が増加する / 100 以上 | Connection パターン |
| Edge にメタデータが必要 | Connection パターン |
| ソート・フィルタが必要 | Connection パターン |

---

## Global Object Identification（Node Interface）

### パターン

```graphql
"""グローバルにユニークな ID で識別可能なオブジェクト"""
interface Node {
  """グローバルにユニークな識別子"""
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
  email: String!
}

type Query {
  """任意の Node を ID で取得"""
  node(id: ID!): Node
  """複数の Node を一括取得"""
  nodes(ids: [ID!]!): [Node]!
}
```

### ID 生成戦略

| 方式 | 例 | メリット | デメリット |
|------|-----|---------|----------|
| Base64(型名:ID) | `VXNlcjoxMjM=` | 型情報を含む、不透明 | デコード可能 |
| UUID | `550e8400-...` | グローバル一意 | 型情報なし |
| 型プレフィックス | `user_123` | 可読性 | 一貫性の維持が必要 |

**推奨**: Base64 エンコード — クライアントに ID の構造を意識させない。

### キャッシュとの関係

- グローバルユニーク ID を公開 → Apollo Client / Relay が正規化キャッシュを構築
- `__typename` + `id` がキャッシュキーになる
- REST の URL ベースキャッシュの代替として機能

---

## Mutation 設計パターン

### 基本構造

```graphql
# 1. Input Type: 引数をグループ化
input CreateProductInput {
  """商品名"""
  name: String!
  """商品説明"""
  description: String
  """価格（セント単位）"""
  priceInCents: Int!
  """カテゴリ ID"""
  categoryId: ID!
}

# 2. Payload Type: 結果 + エラー
type CreateProductPayload {
  """作成された商品（エラー時は null）"""
  product: Product
  """ビジネスロジックエラーのリスト"""
  userErrors: [UserError!]!
}

# 3. UserError: 型安全なエラー
type UserError {
  """エラーが発生した入力フィールドのパス"""
  field: [String!]!
  """人間が読めるエラーメッセージ"""
  message: String!
  """マシンリーダブルなエラーコード"""
  code: CreateProductErrorCode!
}

enum CreateProductErrorCode {
  """商品名が既に使われている"""
  NAME_TAKEN
  """カテゴリが存在しない"""
  CATEGORY_NOT_FOUND
  """価格が不正"""
  INVALID_PRICE
}

# 4. Mutation 定義
type Mutation {
  """新しい商品を作成する"""
  createProduct(input: CreateProductInput!): CreateProductPayload!
}
```

### 目的別 Mutation（推奨）

```graphql
# NG: 汎用的すぎる CRUD
type Mutation {
  updateUser(id: ID!, data: UpdateUserInput!): User!
}

# OK: 目的別に分割
type Mutation {
  """ユーザーのメールアドレスを変更する"""
  changeEmail(input: ChangeEmailInput!): ChangeEmailPayload!
  """ユーザーアカウントを無効化する"""
  deactivateAccount(input: DeactivateAccountInput!): DeactivateAccountPayload!
  """プロフィール画像を更新する"""
  updateAvatar(input: UpdateAvatarInput!): UpdateAvatarPayload!
}
```

### バッチ Mutation

```graphql
# 大量操作が予見される場合
type Mutation {
  """複数商品を一括削除する"""
  deleteProducts(input: DeleteProductsInput!): DeleteProductsPayload!
}

input DeleteProductsInput {
  ids: [ID!]!
}

type DeleteProductsPayload {
  """削除に成功した商品 ID"""
  deletedIds: [ID!]!
  """個別の削除エラー"""
  userErrors: [DeleteProductError!]!
}
```

---

## Interface vs Union

### Interface: 共通フィールドがある場合

```graphql
"""割引可能なアイテム"""
interface Discountable {
  """現在の価格"""
  price: Money!
  """適用可能な割引率"""
  discountPercentage: Float
}

type Product implements Discountable {
  id: ID!
  name: String!
  price: Money!
  discountPercentage: Float
}

type Service implements Discountable {
  id: ID!
  title: String!
  price: Money!
  discountPercentage: Float
  durationMinutes: Int!
}
```

### Union: 共通フィールドがない場合

```graphql
"""検索結果（異種型の集合）"""
union SearchResult = Product | Article | User

type Query {
  search(query: String!): [SearchResult!]!
}

# クエリ時はインラインフラグメントで型ごとに分岐
# query {
#   search(query: "GraphQL") {
#     ... on Product { name, price }
#     ... on Article { title, author }
#     ... on User { username }
#   }
# }
```

### 判断基準

| 基準 | Interface | Union |
|------|-----------|-------|
| 共通フィールドがある | Yes | No |
| 多態的な振る舞いが必要 | Yes | No |
| 全く異なる型をグループ化 | No | Yes |
| フィールドの実装を強制したい | Yes | No |

---

## Nullability 設計ガイド

### デフォルト nullable の理由

GraphQL では全フィールドがデフォルトで nullable。これは意図的な設計：

1. **DB 障害時**: そのフィールドだけ `null` にし、リクエスト全体は成功させる
2. **非同期処理失敗**: 部分的なデータでも返す
3. **フィールドレベル認可**: 権限不足のフィールドだけ `null`
4. **スキーマ進化**: 後から nullable → non-null は安全だが、逆は破壊的変更

### Non-null エラーの伝播

```
Non-null フィールドが null を返す
→ エラーが親フィールドに伝播（バブルアップ）
→ 親も Non-null なら さらに伝播
→ 最終的に data 全体が null になる可能性
```

### 判断チェック

```
このフィールドは:
├── 外部サービスに依存する            → nullable
├── 認可で制限される可能性がある      → nullable
├── 将来 null になりうる              → nullable
├── データベースの NOT NULL カラム     → Non-null 候補
├── 計算値で必ず算出できる            → Non-null 候補
└── ID フィールド                     → Non-null (!)
```

---

## スキーマ進化戦略

### 安全な変更（非破壊的）

- 新しい型の追加
- 新しいフィールドの追加
- 新しい Enum 値の追加（ただしクライアントが `default` ケースを持つ前提）
- 新しい引数の追加（nullable / デフォルト値付き）

### 破壊的変更の回避

```graphql
# Step 1: 新フィールドを追加し、旧フィールドを deprecated に
type User {
  name: String! @deprecated(reason: "Use 'firstName' and 'lastName' instead")
  firstName: String!
  lastName: String!
}

# Step 2: 使用率を監視（Apollo Studio, graphql-inspector 等）
# Step 3: 使用率が 0 になったら旧フィールドを削除
```

### CI/CD でのスキーマチェック

- `graphql-inspector` でスキーマ差分を検出
- Breaking changes を CI で自動ブロック
- フィールド使用状況をトラッキングし、deprecation → 削除の判断材料に
