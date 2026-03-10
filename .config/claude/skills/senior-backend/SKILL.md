---
name: senior-backend
description: >
  バックエンドAPI設計・DB選定・セキュリティの意思決定ガイド。REST vs GraphQL、RDB vs NoSQL、
  認証方式の選定を支援。Use when designing APIs, optimizing databases, or planning backend
  security architecture. Do NOT use for frontend component design (use senior-frontend)
  or system-level architecture decisions (use senior-architect).
allowed-tools: "Read, Grep, Glob"
---

# Senior Backend — 設計意思決定ガイド

バックエンド設計に関する判断を支援するガイド。実装コードではなく「何を選ぶか」に特化。

## デシジョンツリー

### 1. REST vs GraphQL

```
クライアントが1種類     → REST（シンプル）
複数クライアント + 異なるデータ要件 → GraphQL
内部サービス間          → gRPC（型安全 + 高速）
公開API                 → REST（標準的で広く理解される）
```

| 判断基準 | REST | GraphQL |
|----------|------|---------|
| 学習コスト | 低い | 中〜高い |
| オーバーフェッチ | 発生しやすい | クライアントが指定 |
| キャッシュ | HTTP キャッシュが自然 | 専用レイヤー必要 |
| リアルタイム | WebSocket 別途 | Subscription 組込み |
| ファイルアップロード | 標準的 | multipart spec 必要 |
| エコシステム | 成熟 | 成長中 |

### 2. データベース選定

| 要件 | 推奨 |
|------|------|
| 複雑なリレーション・トランザクション | PostgreSQL |
| 柔軟なスキーマ・ドキュメント型 | MongoDB |
| 高速 Key-Value アクセス | Redis |
| 大規模な水平スケーリング | DynamoDB / Cassandra |
| 全文検索 | Elasticsearch |
| 時系列データ | TimescaleDB / InfluxDB |

**迷ったら PostgreSQL** — 最も汎用的で JSONB でドキュメント型も対応可能。

### 3. 認証方式選定

| 条件 | JWT | Session | OAuth 2.0 |
|------|-----|---------|-----------|
| SPA / モバイル | ◎ | ○ | ◎ |
| SSR (Next.js等) | ○ | ◎ | ◎ |
| サードパーティ連携 | × | × | ◎ |
| マイクロサービス | ◎ | × | ○ |
| シンプルな要件 | ○ | ◎ | 過剰 |

**JWT の注意**: リフレッシュトークンのローテーション必須、ログアウト時の無効化戦略が必要。

### 4. API バージョニング

| 方式 | 長所 | 短所 | 推奨場面 |
|------|------|------|----------|
| URL (/v1/) | 明確、キャッシュ容易 | URL 増加 | 公開API |
| Header | URL がクリーン | 発見しにくい | 内部API |
| Query (?v=1) | 簡単 | キャッシュに影響 | 非推奨 |

## パフォーマンスチェックリスト

- [ ] **コネクションプール**: DB接続の適切なプールサイズ設定
- [ ] **N+1 防止**: DataLoader / JOIN / バッチクエリ
- [ ] **インデックス**: EXPLAIN でクエリプランを確認
- [ ] **キャッシュ**: 読み取り頻度の高いデータに TTL 付きキャッシュ
- [ ] **ページネーション**: 大量データは cursor-based を推奨
- [ ] **非同期化**: メール送信・画像処理等はキューに逃がす
- [ ] **レート制限**: 公開エンドポイントに必須
- [ ] **タイムアウト**: 外部サービス呼び出しに必ず設定

## セキュリティチェックリスト

- [ ] **入力バリデーション**: zod / joi でスキーマ検証（境界で検証）
- [ ] **パラメータ化クエリ**: SQL インジェクション防止
- [ ] **CORS**: 許可オリジンを明示的に指定
- [ ] **レート制限**: ブルートフォース防止
- [ ] **ログ**: 認証失敗・権限エラーを記録（PII は除外）
- [ ] **シークレット管理**: 環境変数 or シークレットマネージャー

## エラーレスポンス設計

RFC 7807 Problem Details 形式を標準とする:

```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User with ID 123 was not found",
  "instance": "/users/123"
}
```

詳細なパターン集は `references/api-design-guide.md` を参照。
