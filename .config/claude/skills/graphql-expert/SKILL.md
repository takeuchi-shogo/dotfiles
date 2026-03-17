---
name: graphql-expert
description: >
  GraphQL API の設計・実装・レビューを支援するエキスパートガイド。スキーマ設計、Mutation パターン、
  ページネーション、エラーハンドリング、セキュリティ、パフォーマンス最適化を網羅。
  Use when designing GraphQL schemas, implementing resolvers, reviewing GraphQL code,
  or optimizing GraphQL API performance. Do NOT use for REST API design (use senior-backend)
  or general system architecture (use senior-architect).
allowed-tools: "Read, Grep, Glob, Bash"
metadata:
  pattern: tool-wrapper
---

# GraphQL Expert — 設計・実装・レビューガイド

GraphQL API に関する設計判断、実装パターン、コードレビューを支援する。
公式仕様 + Production Ready GraphQL のベストプラクティスに基づく。

## アクション判定

```
ユーザーの要求を判定:

スキーマ設計・型設計の相談        → design アクション
GraphQL コードの実装              → implement アクション
GraphQL コードのレビュー          → review アクション
パフォーマンス・セキュリティ改善  → optimize アクション
```

---

## design アクション — スキーマ設計

### 設計原則

1. **クエリ駆動設計**: クライアントが実行するクエリを想像してからスキーマを構築する
2. **DB スキーマを反映しない**: ビジネスドメインをグラフとしてモデリングする
3. **バージョンレス進化**: `/v1/` `/v2/` ではなく `@deprecated` + 新フィールド追加
4. **Nullable がデフォルト**: Non-null (`!`) は保証が必要な場合のみ（失敗時エラーが親に伝播）
5. **全フィールドに description**: スキーマがそのまま API ドキュメントになる

### 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| フィールド | camelCase | `firstName`, `createdAt` |
| 型名 | PascalCase | `UserProfile`, `OrderItem` |
| Enum 値 | SCREAMING_SNAKE_CASE | `ACTIVE`, `IN_PROGRESS` |
| Boolean | `is`/`has`/`can` プレフィックス | `isActive`, `hasPermission` |
| Mutation | 動詞 + 名詞（目的別） | `createOrder`, `deactivateAccount` |
| Input | `{Mutation名}Input` | `CreateOrderInput` |
| Payload | `{Mutation名}Payload` | `CreateOrderPayload` |

### 型選択デシジョンツリー

```
共通フィールドがある複数型？
├── Yes → Interface
│   例: interface Node { id: ID! }
└── No  → 共通点のない異種型のグループ？
    ├── Yes → Union
    │   例: union SearchResult = Product | Article | User
    └── No  → Object Type
```

### Mutation 設計パターン（必須）

```graphql
# Input Type: 引数をグループ化
input CreateOrderInput {
  items: [OrderItemInput!]!
  shippingAddress: AddressInput!
  clientMutationId: String      # Relay 互換
}

# Payload Type: 結果 + ビジネスエラー
type CreateOrderPayload {
  order: Order                   # 成功時のデータ
  userErrors: [UserError!]!      # ビジネスロジックエラー
}

# UserError: 型安全なエラー表現
type UserError {
  field: [String!]!              # エラー箇所のパス
  message: String!               # 人間向けメッセージ
  code: CreateOrderErrorCode!    # マシンリーダブルコード
}
```

**アンチパターン**: 汎用 `updateUser(id: ID!, data: JSON!)` — 目的別 mutation を設計すること。

### Pagination 判断

```
要素数が少なく固定的（タグ、カテゴリ等）
├── Yes → Simple List: [Tag!]!
└── No  → Connection パターン（Relay 準拠）
```

Connection パターンの詳細 → `references/schema-design-patterns.md`

### Nullability 判断

```
このフィールドが null を返す可能性は？
├── DB障害、非同期失敗、認可拒否で null になりうる → nullable（デフォルト）
└── 絶対に null にならないと保証できる → Non-null (!)
    ※ Non-null フィールドがエラーを起こすと親フィールドまで null が伝播する
```

---

## implement アクション — 実装パターン

### リゾルバの 4 引数

```javascript
function resolver(obj, args, context, info) {
  // obj:     親オブジェクト（ルートリゾルバでは undefined）
  // args:    フィールド引数
  // context: 共有コンテキスト（ユーザー、DB、DataLoader 等）
  // info:    フィールド固有情報・スキーマ詳細
}
```

### 認可パターン（必須）

**認証はミドルウェア（GraphQL 処理前）、認可はビジネスロジック層（リゾルバから委譲）**

```javascript
// NG: リゾルバに認可ロジックを直書き
function resolvePostBody(obj, args, context) {
  if (context.user?.id === obj.authorId) return obj.body;
  return null;
}

// OK: ビジネスロジック層に委譲
function resolvePostBody(obj, args, context) {
  return postService.getBody({ user: context.user, post: obj });
}
```

### DataLoader（N+1 対策）

```javascript
// リクエストスコープで DataLoader を生成
function createLoaders() {
  return {
    userLoader: new DataLoader(async (ids) => {
      const users = await db.users.findByIds(ids);
      // 入力キーの順序と同じ順序で返す
      return ids.map(id => users.find(u => u.id === id) || new Error(`User ${id} not found`));
    }),
  };
}

// context に注入
const context = { loaders: createLoaders(), user: req.user };
```

**DataLoader の原則:**
- リクエストごとに新規インスタンス（キャッシュ分離）
- バッチ関数は入力キーと同じ順序・同じ長さで返す
- 個別エラーは `Error` オブジェクトとして返す（全体を失敗させない）

### 3 層エラーモデル

| 層 | 場所 | 用途 | 例 |
|----|------|------|-----|
| Transport | HTTP レベル | ネットワーク障害 | 500, タイムアウト |
| Request | トップレベル `errors` | 構文/バリデーション/認証 | フィールド未定義、認証失敗 |
| Business | Mutation Payload 内 `userErrors` | ビジネスロジック | 在庫不足、メール重複 |

```json
// Request Error（開発者向け）
{
  "errors": [{
    "message": "Field 'name' not found on type 'User'",
    "extensions": { "code": "GRAPHQL_VALIDATION_FAILED" }
  }]
}

// Business Error（エンドユーザー向け — Payload 内）
{
  "data": {
    "createOrder": {
      "order": null,
      "userErrors": [{
        "field": ["items", "0", "quantity"],
        "message": "在庫が不足しています",
        "code": "INSUFFICIENT_STOCK"
      }]
    }
  }
}
```

### Subscription 使い分け

```
頻繁かつ漸進的な変更（チャット、通知）   → Subscription（WebSocket / SSE）
低頻度の更新                              → ポーリング or プッシュ通知
ユーザーアクション起点                    → クエリ再取得（refetch）
```

---

## review アクション — コードレビュー

以下のチェックリストに基づいてレビューする。
詳細は `references/` を参照。

### スキーマ設計チェック

- [ ] フィールド名は camelCase、型名は PascalCase、Enum は SCREAMING_SNAKE_CASE
- [ ] 全型・全フィールドに description（`"""..."""`）がある
- [ ] Mutation は Input/Payload パターンに従っている
- [ ] Payload に `userErrors: [UserError!]!` がある
- [ ] 大きなリストには Connection パターンを使用
- [ ] Nullable/Non-null の判断が適切（デフォルト nullable）
- [ ] DB スキーマの直接反映ではなくドメインモデルになっている
- [ ] 汎用 CRUD ではなく目的別 mutation になっている
- [ ] `@deprecated(reason: "...")` で廃止予定フィールドが管理されている

### 実装チェック

- [ ] 認可ロジックがビジネスロジック層に委譲されている（リゾルバ直書きでない）
- [ ] DataLoader でバッチング（N+1 対策）されている
- [ ] DataLoader はリクエストスコープで生成されている
- [ ] エラーが 3 層モデルに従っている
- [ ] Mutation リゾルバが変更後のエンティティを返している
- [ ] 変数を使用（文字列補間でクエリ構築していない）
- [ ] オペレーション名が全クエリに付いている

### セキュリティチェック

- [ ] Query depth limit が設定されている
- [ ] Query complexity / cost analysis が設定されている
- [ ] コストベースの rate limiting がある
- [ ] 本番で introspection が無効化されている
- [ ] エラーメッセージが内部情報を漏洩していない
- [ ] 入力のサニタイズ・バリデーションがある
- [ ] ファーストパーティなら Trusted Documents / Persisted Queries を検討

### パフォーマンスチェック

- [ ] N+1 クエリが発生していない（DataLoader 使用）
- [ ] 大量データに適切なページネーションがある
- [ ] GET + Persisted Queries で HTTP/CDN キャッシュ活用
- [ ] グローバルユニーク ID を公開（クライアントキャッシュ用）
- [ ] GZIP/Brotli 圧縮が有効
- [ ] OpenTelemetry 等でリゾルバパフォーマンス監視

---

## optimize アクション — パフォーマンス・セキュリティ最適化

詳細は `references/security-performance.md` を参照。

### パフォーマンス最適化の優先順位

```
1. N+1 問題の解決（DataLoader）           ← 最も効果大
2. ページネーション（Connection パターン）
3. Persisted Queries + HTTP キャッシュ
4. Query Complexity 制限
5. レスポンス圧縮（GZIP/Brotli）
6. @defer / @stream（段階的レスポンス）
```

### セキュリティ多層防御

```
1. HTTPS + タイムアウト                    ← トランスポート層
2. Trusted Documents / Persisted Queries  ← 需要制御
3. Depth / Breadth / Batch Limiting       ← 構造制限
4. Query Complexity Analysis              ← コスト制限
5. Rate Limiting（コストベース推奨）       ← 流量制限
6. Input Validation + Sanitization        ← 入力検証
7. Introspection 無効化 + Error Masking   ← 情報漏洩防止
```

---

## Federation 判断

```
複数チームが独立して API を開発？
├── Yes → Federation 検討
│   ├── DDD に基づくサービス境界が明確 → Federation 導入
│   └── 境界が曖昧 → まずモノリスで開始、後で分割
└── No  → モノリシック GraphQL API
    ※ Facebook 自身も 2012 年以降モノリシック API を使い続けている
```

---

## 関連スキルとの使い分け

| 判断 | 使うスキル |
|------|-----------|
| REST vs GraphQL の選定 | `senior-backend` |
| システム全体のアーキテクチャ | `senior-architect` |
| GraphQL スキーマ・リゾルバの設計/実装/レビュー | **このスキル** |
| React クライアントからの GraphQL 利用 | `react-best-practices` |
