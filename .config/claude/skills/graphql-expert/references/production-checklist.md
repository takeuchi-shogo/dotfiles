# GraphQL 本番投入チェックリスト

## スキーマ設計

- [ ] **クエリ駆動設計**: DB スキーマではなくクライアントのユースケースに基づいて設計されている
- [ ] **命名規則の一貫性**: フィールド=camelCase、型=PascalCase、Enum=SCREAMING_SNAKE_CASE
- [ ] **全型・全フィールドに description** (`"""..."""`) が付いている
- [ ] **Mutation は Input/Payload パターン**: `XxxInput` → `XxxPayload` 構造
- [ ] **Payload に userErrors**: `userErrors: [UserError!]!` でビジネスエラーを返す
- [ ] **目的別 Mutation**: 汎用 CRUD ではなくドメインアクション（`changeEmail`, `deactivateAccount`）
- [ ] **Connection パターン**: 増加するリストには Relay 準拠のページネーション
- [ ] **Nullable がデフォルト**: Non-null は保証できる場合のみ
- [ ] **Node Interface**: グローバルユニーク ID で `node(id: ID!): Node` を提供
- [ ] **Interface vs Union**: 共通フィールドの有無で適切に選択
- [ ] **@deprecated 管理**: 廃止予定フィールドに `reason` 付きで設定

## エラーハンドリング

- [ ] **3 層エラーモデル**:
  - Transport: HTTP レベル（ネットワーク障害）
  - Request: トップレベル `errors`（構文/バリデーション/認証）
  - Business: Payload 内 `userErrors`（ビジネスロジック）
- [ ] **extensions.code**: トップレベルエラーにマシンリーダブルなコードを付与
- [ ] **UserError に code enum**: Mutation ごとのエラーコード enum
- [ ] **エラーメッセージマスク**: 本番で内部エラーの詳細を隠蔽
- [ ] **部分レスポンス対応**: クライアントが `data` と `errors` の共存を処理できる

## パフォーマンス

- [ ] **DataLoader**: N+1 問題を解決するバッチング・キャッシングレイヤー
- [ ] **DataLoader はリクエストスコープ**: 毎リクエストで新規インスタンス生成
- [ ] **ページネーション上限**: `first`/`last` に最大値を設定（例: 100）
- [ ] **Persisted Queries**: クエリハッシュでネットワーク転送量を削減
- [ ] **HTTP キャッシュ**: GET + Persisted Queries で CDN キャッシュ活用
- [ ] **レスポンス圧縮**: GZIP または Brotli を有効化
- [ ] **リゾルバ監視**: OpenTelemetry 等でリゾルバの実行時間を計測
- [ ] **Slow query 検出**: 閾値超えのクエリをログ記録

## セキュリティ

- [ ] **HTTPS**: 全通信を暗号化
- [ ] **認証はミドルウェア**: GraphQL レイヤーの外で処理
- [ ] **認可はビジネスロジック層**: リゾルバに直書きしない
- [ ] **Query Depth Limit**: ネストの深さに上限設定（推奨: 7-10）
- [ ] **Query Breadth Limit**: ルートフィールド数に上限設定
- [ ] **Batch Limit**: 1リクエストのオペレーション数に上限設定
- [ ] **Query Complexity Analysis**: フィールドにコスト重みを割り当て、閾値超過を拒否
- [ ] **Rate Limiting**: コストベースの流量制限（GitHub v4 方式推奨）
- [ ] **Introspection 制御**: 本番環境で無効化 or アクセス制限
- [ ] **Input Validation**: カスタムスカラー + リゾルバでの長さ/値の制限
- [ ] **入力サニタイズ**: XSS, SQL Injection 対策
- [ ] **Trusted Documents**: ファーストパーティなら事前承認クエリのホワイトリスト化

## スキーマ進化 & CI/CD

- [ ] **バージョンレス API**: `/v1/` `/v2/` ではなく additive changes + @deprecated
- [ ] **Breaking Change 検出**: `graphql-inspector` 等で CI 自動チェック
- [ ] **フィールド使用率トラッキング**: 廃止判断の材料を収集
- [ ] **Deprecation フロー**: @deprecated 設定 → 使用率監視 → 0% で削除
- [ ] **スキーマ Snapshot Test**: SDL のスナップショットで意図しない変更を検出

## テスト戦略

- [ ] **Unit Test**: リゾルバの個別ロジック（DataLoader/DB はモック）
- [ ] **Integration Test**: `graphql(schema, query)` で実スキーマに対するテスト
- [ ] **Contract Test**: CI でスキーマの破壊的変更を自動検出
- [ ] **E2E Test**: HTTP リクエスト + 認証フローを含む全体テスト
- [ ] **スキーマ品質チェック**:
  - 全型が到達可能（orphaned types がない）
  - 命名規則の遵守
  - description の網羅性

## HTTP サービング

- [ ] **単一エンドポイント**: `/graphql`
- [ ] **POST**: 全オペレーション対応（`Content-Type: application/json`）
- [ ] **GET**: クエリのみ（mutation 不可）、HTTP キャッシュ活用
- [ ] **Content-Type**: レスポンスに `application/graphql-response+json`
- [ ] **ステータスコード**: data が non-null なら `2xx`、バリデーションエラーは `400`
- [ ] **オペレーション名必須**: デバッグ・ログ・監視のため全クエリに名前

## Federation（マイクロサービス構成の場合）

- [ ] **サービス境界**: DDD に基づく明確なドメイン分割
- [ ] **@key ディレクティブ**: エンティティの解決方法を定義
- [ ] **ゲートウェイ**: クエリプランニング + ルーティングの設定
- [ ] **独立デプロイ**: 各サブグラフが独立してデプロイ・テスト可能
- [ ] **スキーマ合成チェック**: 合成エラーを CI で検出

---

## アンチパターン早見表

| アンチパターン | 問題 | 正しいアプローチ |
|---------------|------|----------------|
| DB テーブルを型に 1:1 マッピング | 内部実装の漏洩 | クライアントのユースケースで設計 |
| 汎用 `updateUser(data: JSON!)` | 型安全性の喪失 | 目的別 mutation (`changeEmail`) |
| リゾルバに認可ロジック直書き | ロジックの散在 | ビジネスロジック層に委譲 |
| 全フィールド Non-null | エラー時にリクエスト全体が失敗 | Nullable をデフォルトに |
| Offset ページネーション | 大規模データで性能劣化 | Cursor-based Connection パターン |
| 文字列補間でクエリ構築 | インジェクションリスク | 変数 ($var) を使用 |
| バージョニング (/v1/, /v2/) | URL 増加、管理コスト | additive changes + @deprecated |
| DataLoader なしのネスト解決 | N+1 クエリ | DataLoader でバッチング |
| エラーを全て トップレベル errors で返す | 型安全でないエラー処理 | 3層エラーモデル |
| 本番で Introspection 有効 | スキーマ情報漏洩 | 無効化 + 多層防御 |
| REST 思考で resource 中心設計 | GraphQL の利点を活かせない | Graph 思考でドメインモデリング |
| 最初から完全なドメインモデル | 過剰設計 | 漸進的に 1 シナリオずつ構築 |
