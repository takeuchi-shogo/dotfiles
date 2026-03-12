# セキュリティ & パフォーマンス詳細ガイド

## セキュリティ: 多層防御モデル

### Layer 1: トランスポートセキュリティ

- HTTPS 必須
- 適切なタイムアウト設定（リクエスト・レスポンス両方）
- CORS の許可オリジンを明示的に指定

### Layer 2: 需要制御（Demand Control）

#### Trusted Documents / Persisted Queries（最も効果的）

```
# Automatic Persisted Queries (APQ) フロー:
1. クライアント: ハッシュのみ送信
2. サーバー: ハッシュで検索 → 見つからない → "PersistedQueryNotFound"
3. クライアント: ハッシュ + クエリ文字列を送信
4. サーバー: 保存 + 実行
5. 以降: ハッシュのみで実行

# Trusted Documents（ファーストパーティ限定）:
- ビルド時にクエリを抽出 → ハッシュマップを生成
- サーバーはホワイトリストにないクエリを拒否
- 任意クエリの実行を完全に防止
```

**メリット:**
- ネットワーク転送量の大幅削減
- 任意クエリの実行を防止（セキュリティ）
- GET リクエスト + CDN キャッシュが可能に

#### ページネーション強制

```graphql
type Query {
  # first/last に最大値を設定
  users(first: Int = 20, after: String): UserConnection!
}

# リゾルバ側で上限を強制
function resolveUsers(_, args) {
  const first = Math.min(args.first || 20, 100); // 最大 100
  // ...
}
```

#### Depth Limiting（深度制限）

```graphql
# 攻撃例: 再帰的ネストで指数関数的にデータ量を増加
query {
  hero {
    friends {       # depth 1
      friends {     # depth 2
        friends {   # depth 3
          friends { # depth 4 — ここでブロック
            name
          }
        }
      }
    }
  }
}

# 推奨: 最大深度 7-10 程度
```

#### Breadth Limiting（幅制限）

```graphql
# 攻撃例: エイリアスで同一フィールドを大量に展開
query {
  a1: user(id: "1") { name }
  a2: user(id: "2") { name }
  # ... 10,000 個のエイリアス
}

# 対策: ルートフィールド数に上限を設定
```

#### Batch Limiting

```graphql
# 攻撃例: 1リクエストに大量のオペレーションを含める
[
  { "query": "{ user(id: \"1\") { name } }" },
  { "query": "{ user(id: \"2\") { name } }" },
  # ... 数千のオペレーション
]

# 対策: バッチサイズに上限を設定（例: 最大 10）
```

### Layer 3: コスト制御

#### Query Complexity Analysis

```graphql
# フィールドにコスト重みを割り当て
type Query {
  users(first: Int): UserConnection!
    @cost(weight: 1)                    # 基本コスト
}

type User {
  name: String!    @cost(weight: 0)     # スカラー: 低コスト
  posts: [Post!]!  @cost(weight: 5)     # リスト: 高コスト
  avatar: Image!   @cost(weight: 10)    # 外部サービス: 高コスト
}

# リスト引数による乗算
# users(first: 50) の posts フィールド → 50 × 5 = 250 ポイント
```

**コスト計算の考慮事項:**
- スカラーフィールド: 0-1
- DB クエリが必要なフィールド: 1-5
- 外部サービス呼び出し: 5-20
- リスト: 基本コスト × 要素数（first/last 引数で乗算）
- ネスト: 親のコスト × 子のコスト

参照仕様: [IBM GraphQL Cost Spec Draft](https://ibm.github.io/graphql-specs/cost-spec.html)

#### コストベースの Rate Limiting（推奨）

```
# 単純なクエリ数ベース（非推奨）
100 queries / minute

# コストベース（推奨 — GitHub API v4 方式）
5,000 points / hour
- 各クエリのコストをポイントとして消費
- 軽いクエリは 1 ポイント、重いクエリは数百ポイント
- レスポンスヘッダーで残りポイントを通知
```

### Layer 4: 入力検証

```graphql
# カスタムスカラーで入力を制限
scalar Email      # メールアドレス形式を検証
scalar URL        # URL 形式を検証
scalar DateTime   # ISO 8601 形式を検証
scalar PositiveInt # 正の整数のみ

# Input の max length
input CreateCommentInput {
  body: String!    # リゾルバ側で長さ制限を強制
  postId: ID!
}
```

**リゾルバでのサニタイズ:**
- XSS: HTML タグのエスケープ / サニタイズ
- SQL Injection: パラメータ化クエリ（ORM 使用時は自動）
- 文字列長制限: 入力フィールドに最大長を設定

### Layer 5: 情報漏洩防止

```javascript
// 本番環境でイントロスペクションを無効化
const server = new ApolloServer({
  introspection: process.env.NODE_ENV !== 'production',
});

// エラーメッセージのマスク
formatError(error) {
  if (error.extensions?.code === 'INTERNAL_SERVER_ERROR') {
    return { message: 'Internal server error' }; // 詳細を隠す
  }
  return error;
}
```

**注意**: イントロスペクション無効化だけでは不十分（フィールド名の推測で情報漏洩の可能性）。多層防御の一部として位置づける。

---

## パフォーマンス最適化

### N+1 問題と DataLoader

#### 問題の構造

```
query { users { posts { comments { author { name } } } } }

実行フロー（DataLoader なし）:
1. users を 1 回の DB クエリで取得 (N ユーザー)
2. 各ユーザーの posts を N 回クエリ
3. 各ポストの comments を M 回クエリ
4. 各コメントの author を L 回クエリ
→ 合計: 1 + N + N*M + N*M*L 回のクエリ
```

#### DataLoader パターン

```javascript
import DataLoader from 'dataloader';

// バッチ関数: キーの配列を受け取り、同じ順序で結果を返す
const userLoader = new DataLoader(async (userIds) => {
  const users = await db.query(
    'SELECT * FROM users WHERE id IN (?)', [userIds]
  );
  // 入力キーと同じ順序で返す（見つからない場合は Error）
  const userMap = new Map(users.map(u => [u.id, u]));
  return userIds.map(id =>
    userMap.get(id) || new Error(`User ${id} not found`)
  );
});

// リゾルバでの使用
const resolvers = {
  Comment: {
    author: (comment, _, context) => {
      return context.loaders.userLoader.load(comment.authorId);
    }
  }
};

// リクエストスコープで DataLoader を生成
function createContext(req) {
  return {
    user: req.user,
    loaders: {
      userLoader: new DataLoader(batchGetUsers),
      postLoader: new DataLoader(batchGetPosts),
    }
  };
}
```

#### DataLoader のルール

| ルール | 理由 |
|--------|------|
| リクエストごとに新規インスタンス | キャッシュの分離（他ユーザーのデータが漏れない） |
| バッチ関数は入力と同じ長さ・順序で返す | DataLoader の内部マッピングが壊れる |
| 個別エラーは Error オブジェクトとして返す | 1件の失敗でバッチ全体を失敗させない |
| `.load()` は常に Promise を返す | 非同期バッチングの仕組み |

### HTTP キャッシュ戦略

#### GET + Persisted Queries

```
# HTTP キャッシュを活用するフロー
GET /graphql?extensions={"persistedQuery":{"sha256Hash":"abc123"}}

# CDN / ブラウザが通常の HTTP キャッシュを適用可能
Cache-Control: public, max-age=300
```

#### フィールドレベルキャッシュ

```graphql
type Query {
  """頻繁に変わらないカテゴリ一覧"""
  categories: [Category!]! @cacheControl(maxAge: 3600)

  """ユーザー固有のデータ"""
  me: User! @cacheControl(maxAge: 0, scope: PRIVATE)
}

type Product {
  id: ID!
  name: String! @cacheControl(maxAge: 86400)  # 1日
  stock: Int!   @cacheControl(maxAge: 0)       # リアルタイム
}
```

**レスポンス全体の maxAge** = 全フィールドの中で最小の maxAge

#### クライアントサイドキャッシュ

- **正規化キャッシュ**: Apollo Client / Relay が `__typename` + `id` でオブジェクトを正規化
- **グローバルユニーク ID が必須**: Node Interface パターンの採用を推奨
- **キャッシュ無効化**: Mutation の戻り値で更新されたオブジェクトを返す → 自動的にキャッシュ更新

### レスポンス最適化

#### 圧縮

```javascript
// Express の例
app.use(compression()); // GZIP/Brotli
```

#### @defer / @stream（段階的レスポンス）

```graphql
query {
  product(id: "1") {
    name
    price
    ... @defer {
      reviews {       # 重いフィールドを後から送信
        rating
        comment
      }
    }
  }
}
```

- クライアントは初期レスポンスを先に描画
- 重いフィールドは後から到着
- ユーザー体感速度の改善

### 監視と計測

```javascript
// OpenTelemetry でリゾルバの実行時間を計測
const plugin = {
  requestDidStart() {
    return {
      executionDidStart() {
        return {
          willResolveField({ info }) {
            const start = performance.now();
            return () => {
              const duration = performance.now() - start;
              if (duration > 100) { // 100ms 超のリゾルバを記録
                logger.warn(`Slow resolver: ${info.parentType}.${info.fieldName}: ${duration}ms`);
              }
            };
          }
        };
      }
    };
  }
};
```

**監視すべきメトリクス:**
- リゾルバの実行時間（P50, P95, P99）
- クエリの複雑度分布
- エラー率（Request Error vs Field Error）
- DataLoader のバッチサイズ・ヒット率
