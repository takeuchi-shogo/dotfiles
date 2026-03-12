---
name: buf-protobuf
description: >
  Buf エコシステム（Buf CLI, BSR, Bufstream）を活用した Protocol Buffers 開発の包括ガイド。
  Protobuf スキーマ設計、コード生成、リンティング、破壊的変更検出、Bufstream（Kafka互換メッセージキュー）の
  構築・デプロイ・設定を支援。Use when working with .proto files, buf.yaml, buf.gen.yaml,
  bufstream.yaml, Kafka streaming with schema enforcement, Protobuf code generation,
  gRPC/ConnectRPC API design, or Buf Schema Registry integration.
  Triggers: 'protobuf', 'proto file', 'buf lint', 'buf generate', 'buf breaking',
  'bufstream', 'BSR', 'schema registry', 'Kafka replacement', 'gRPC schema',
  'protovalidate', 'Iceberg integration', 'proto validation'.
  Do NOT use for general Kafka administration without Buf/Protobuf context —
  use senior-backend instead.
---

# Buf Protobuf — エコシステム包括ガイド

Buf エコシステムを使った Protocol Buffers 開発のすべてを支援するスキル。
スキーマ設計からストリーミング基盤まで、3つのレイヤーをカバーする。

## エコシステム概要

```
┌─────────────────────────────────────────────────────┐
│                   Buf Ecosystem                      │
├──────────┬──────────────────┬────────────────────────┤
│ Buf CLI  │ Buf Schema       │ Bufstream              │
│          │ Registry (BSR)   │                        │
│ ローカル │ スキーマの中央   │ Kafka互換メッセージ    │
│ 開発     │ 管理・配布       │ キュー + データ        │
│ ツール   │                  │ レイクハウス            │
├──────────┴──────────────────┴────────────────────────┤
│ Protovalidate: フィールドレベルのセマンティック検証   │
│ ConnectRPC: ブラウザ互換 RPC フレームワーク          │
└─────────────────────────────────────────────────────┘
```

## タスクルーティング

| ユーザーの意図 | 参照セクション |
|---------------|---------------|
| .proto ファイルの設計・ベストプラクティス | [スキーマ設計](#スキーマ設計) |
| buf.yaml / buf.gen.yaml の設定 | [Buf CLI 設定](#buf-cli-設定) |
| コード生成（Go, TypeScript 等） | [コード生成](#コード生成) |
| リンティング・破壊的変更検出 | [品質ゲート](#品質ゲート) |
| BSR へのモジュール公開・依存管理 | [BSR 統合](#bsr-統合) |
| Bufstream の構築・デプロイ | [Bufstream](#bufstream) + `references/bufstream-deploy.md` |
| セマンティック検証の設定 | [セマンティック検証](#セマンティック検証) |
| Iceberg テーブル連携 | [Iceberg 統合](#iceberg-統合) + `references/bufstream-config.md` |
| Kafka 互換性・クライアント設定 | [Kafka 互換性](#kafka-互換性) |

---

## スキーマ設計

### Protobuf ベストプラクティス

**パッケージ命名**: `{organization}.{domain}.{version}` 形式を使う。

```protobuf
syntax = "proto3";
package acme.payment.v1;
```

**バージョニング戦略**: パッケージ名にバージョンを含める（v1, v2）。
既存のメッセージのフィールドを削除・型変更せず、新バージョンのパッケージを作る。

**フィールド設計のルール**:

| ルール | 理由 |
|--------|------|
| フィールド番号は削除しない | ワイヤフォーマットの互換性 |
| `reserved` で廃止番号を明示 | 将来の再利用事故を防止 |
| `optional` を意図的に使う | ゼロ値とフィールド未設定を区別 |
| `repeated` は空リストがデフォルト | nil チェック不要 |
| enum の 0 番は `UNSPECIFIED` にする | デフォルト値の意味を明確に |

```protobuf
enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_CONFIRMED = 2;
  ORDER_STATUS_SHIPPED = 3;
}

message Order {
  string order_id = 1;
  OrderStatus status = 2;
  repeated LineItem items = 3;
  reserved 4, 5;  // 廃止済みフィールド
  reserved "old_field_name";
}
```

### Protovalidate によるフィールド検証

Protovalidate を使うとスキーマ内に検証ルールを直接定義でき、
Bufstream のブローカーサイド検証や各言語のランタイム検証で活用できる。

```protobuf
syntax = "proto3";
package invoice.v1;

import "buf/validate/validate.proto";

message Invoice {
  string invoice_id = 1 [(buf.validate.field).string.uuid = true];
  string email = 2 [(buf.validate.field).string.email = true];
  uint32 quantity = 3 [
    (buf.validate.field).uint32.gt = 0,
    (buf.validate.field).uint32.lte = 10000
  ];
  repeated LineItem line_items = 4
    [(buf.validate.field).repeated.min_items = 1];
}

// CEL 式によるクロスフィールド検証
message DateRange {
  option (buf.validate.message).cel = {
    id: "end_after_start",
    message: "end_date must be after start_date",
    expression: "this.end_date > this.start_date"
  };
  google.protobuf.Timestamp start_date = 1;
  google.protobuf.Timestamp end_date = 2;
}
```

**主な検証ルール**:

| 型 | ルール例 | 説明 |
|----|---------|------|
| string | `.string.uuid = true` | UUID 形式 |
| string | `.string.email = true` | メールアドレス形式 |
| string | `.string.min_len = 1` | 最小文字数 |
| uint32 | `.uint32.gt = 0` | 0 より大きい |
| uint32 | `.uint32.gte = 0, .lte = 150` | 範囲指定 |
| repeated | `.repeated.min_items = 1` | 最低1要素 |
| field | `.required = true` | 必須フィールド |
| message | `.cel = {expression: "..."}` | CEL 式 |

---

## Buf CLI 設定

### buf.yaml（ワークスペース定義）

```yaml
version: v2
modules:
  - path: proto
deps:
  - buf.build/bufbuild/protovalidate
lint:
  use:
    - STANDARD
breaking:
  use:
    - FILE
```

### buf.gen.yaml（コード生成定義）

```yaml
version: v2
managed:
  enabled: true
  override:
    - file_option: go_package_prefix
      value: github.com/myorg/myproject/gen
plugins:
  # Go
  - remote: buf.build/protocolbuffers/go
    out: gen/go
    opt: paths=source_relative
  # ConnectRPC (Go)
  - remote: buf.build/connectrpc/go
    out: gen/go
    opt: paths=source_relative
  # TypeScript (ConnectRPC)
  - remote: buf.build/connectrpc/es
    out: gen/ts
inputs:
  - directory: proto
```

### 主要コマンド

| コマンド | 用途 |
|---------|------|
| `buf build` | Protobuf のコンパイル・検証 |
| `buf lint` | スタイル・ベストプラクティスの検証 |
| `buf breaking --against .git#branch=main` | 破壊的変更の検出 |
| `buf generate` | コードスタブの生成 |
| `buf format -w` | .proto ファイルの自動フォーマット |
| `buf push` | BSR へのモジュール公開 |
| `buf dep update` | 依存関係の更新 |
| `buf curl` | RPC エンドポイントのテスト |
| `buf convert` | バイナリ ↔ JSON 変換 |

---

## コード生成

### Managed Mode

`managed: enabled: true` で、各言語のオプション（`go_package`, `java_package` 等）を
.proto ファイルに書く必要がなくなる。buf.gen.yaml で一元管理する。

**override の使い方**:

```yaml
managed:
  enabled: true
  override:
    # Go パッケージプレフィックス
    - file_option: go_package_prefix
      value: github.com/myorg/myproject/gen
    # Java パッケージプレフィックス
    - file_option: java_package_prefix
      value: com.myorg.myproject
    # 特定モジュールの除外
    - file_option: go_package_prefix
      module: buf.build/googleapis/googleapis
      value: google.golang.org/genproto
```

### リモートプラグイン vs ローカルプラグイン

| 方式 | 利点 | 欠点 |
|------|------|------|
| リモート (`remote:`) | インストール不要、BSR 管理 | ネットワーク依存 |
| ローカル (`local:`) | オフライン動作、カスタムプラグイン | PATH に要配置 |

```yaml
plugins:
  # リモート（BSR ホスト）
  - remote: buf.build/protocolbuffers/go
    out: gen/go
  # ローカル（protoc プラグイン）
  - local: protoc-gen-go
    out: gen/go
```

---

## 品質ゲート

### リンティング (`buf lint`)

`STANDARD` カテゴリで最も一般的なルールを適用。カスタマイズ可能:

```yaml
lint:
  use:
    - STANDARD
  except:
    - ENUM_VALUE_PREFIX  # 特定ルールの除外
  enum_zero_value_suffix: _UNSPECIFIED
  service_suffix: Service
```

### 破壊的変更検出 (`buf breaking`)

CI/CD パイプラインに組み込んで API の後方互換性を自動検証:

```bash
# main ブランチとの比較
buf breaking --against .git#branch=main

# BSR の最新版との比較
buf breaking --against buf.build/myorg/mymodule

# サブディレクトリ指定
buf breaking proto --against ".git#branch=main,subdir=proto"
```

**検出ルールカテゴリ**:

| カテゴリ | 検出対象 |
|---------|---------|
| `FILE` | ファイル単位の変更（最も厳しい） |
| `PACKAGE` | パッケージ単位の変更 |
| `WIRE` | ワイヤフォーマットの互換性 |
| `WIRE_JSON` | JSON シリアライゼーション互換性 |

### CI/CD 統合例

```yaml
# GitHub Actions
- name: Buf Lint
  run: buf lint
- name: Buf Breaking
  run: buf breaking --against "https://github.com/${{ github.repository }}.git#branch=main"
```

---

## BSR 統合

### 認証

```bash
buf registry login buf.build
# トークンは ~/.netrc に保存される
```

### モジュール公開

```bash
buf push
```

BSR に公開すると以下が自動的に利用可能になる:
- **ドキュメント**: 自動生成されるAPIリファレンス
- **生成SDK**: Go, npm, Python, Maven, Cargo, Swift
- **依存解決**: 他のモジュールからの `deps` 参照
- **破壊的変更ポリシー**: レジストリレベルでの強制

### 依存管理

```yaml
# buf.yaml
deps:
  - buf.build/bufbuild/protovalidate
  - buf.build/googleapis/googleapis
```

```bash
buf dep update  # buf.lock を更新
```

---

## Bufstream

### 概要

Bufstream は **データレイクハウス時代のための Kafka 互換メッセージキュー**。
Apache Kafka の 1/8 のコストで運用でき、以下の特徴を持つ:

- **スキーマ駆動**: ブローカーがスキーマを理解し、データ品質を自動強制
- **Iceberg 直接書き込み**: ETL パイプライン不要でデータレイクに直結
- **リーダーレス**: アクティブ-アクティブアーキテクチャ
- **オブジェクトストレージ**: S3/GCS/Azure Blob をデータストアに使用
- **完全セルフホスト**: AWS, GCP, Azure, オンプレミス対応
- **Jepsen 検証済み**: 正確性が独立検証されている

### アーキテクチャ

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Producer    │     │  Consumer   │     │  Kafka CLI  │
│  (Kafka API) │     │  (Kafka API)│     │  / AKHQ     │
└──────┬───────┘     └──────┬──────┘     └──────┬──────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────┐
│              Bufstream Brokers (Leaderless)          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Schema   │  │  Semantic    │  │  Iceberg      │  │
│  │ Provider │  │  Validation  │  │  Archiver     │  │
│  └──────────┘  └──────────────┘  └───────────────┘  │
└──────┬──────────────┬──────────────────┬────────────┘
       │              │                  │
       ▼              ▼                  ▼
┌──────────┐   ┌──────────┐      ┌──────────────┐
│ Object   │   │ Metadata │      │ Iceberg      │
│ Storage  │   │ Store    │      │ Catalog      │
│ (S3/GCS) │   │ (PG/etcd)│      │ (REST/Glue)  │
└──────────┘   └──────────┘      └──────────────┘
```

### クイックスタート

```bash
# ダウンロード
curl -sSL -o bufstream \
  "https://buf.build/dl/bufstream/latest/bufstream-$(uname -s)-$(uname -m)" && \
  chmod +x bufstream

# ローカルモードで起動（localhost:9092）
./bufstream serve

# スキーマ付きで起動（ローカル .proto ファイルを参照）
./bufstream serve --schema .
```

### bufstream.yaml 基本構成

```yaml
version: v1beta1

cluster: my-cluster

# メタデータストア
metadata:
  postgres:
    string: postgresql://user:pass@host:5432/bufstream

# データストレージ
data:
  s3:
    bucket: my-bufstream-data
    region: ap-northeast-1

# スキーマレジストリ
schema_registry:
  bsr:
    host: buf.build

# Kafka リスナー
kafka:
  listeners:
    - listen_address: 0.0.0.0:9092

# オブザーバビリティ
logging:
  level: info
metrics:
  otlp:
    type: http
    url: http://otel-collector:4318
```

詳細な設定リファレンスは `references/bufstream-config.md` を参照。

### トピック設定

```bash
# トピック作成
bufstream kafka topic create orders --partitions 6

# スキーマの紐付け（BSR）
bufstream kafka config topic set --topic orders \
  --name buf.registry.value.schema.module \
  --value buf.build/myorg/mymodule
bufstream kafka config topic set --topic orders \
  --name buf.registry.value.schema.message \
  --value myorg.orders.v1.Order

# スキーマの紐付け（ローカル開発）
bufstream kafka config topic set --topic orders \
  --name buf.registry.value.schema.message \
  --value myorg.orders.v1.Order
```

---

## セマンティック検証

ブローカーサイドで Protovalidate ルールを強制し、不正データをトピックに入れない。

### 検証モード

| モード | 動作 | ユースケース |
|--------|------|-------------|
| `reject` | 不正バッチを拒否、プロデューサーにエラー返却 | 厳密なデータ品質要件 |
| `dlq` | 不正メッセージを DLQ トピックに転送 | プロデューサーを止めたくない場合 |

```bash
# reject モード
bufstream kafka config topic set --topic orders \
  --name bufstream.validate.mode --value reject

# DLQ モード
bufstream kafka config topic set --topic orders \
  --name bufstream.validate.mode --value dlq

# DLQ トピック名のカスタマイズ（デフォルト: {topic}.dlq）
bufstream kafka config topic set --topic orders \
  --name bufstream.validate.dlq.topic --value orders-invalid
```

---

## Iceberg 統合

Kafka トピックのデータを Apache Iceberg テーブルとして直接書き出し、
ETL パイプラインを排除する。

### 設定手順

1. スキーマプロバイダーを設定（BSR or ローカル）
2. bufstream.yaml にカタログを追加
3. トピックパラメータを設定

```yaml
# bufstream.yaml — カタログ設定
iceberg:
  - name: my-catalog
    rest:
      url: https://iceberg-rest.example.com
  # AWS Glue
  - name: glue-catalog
    aws_glue_data_catalog: {}
  # BigQuery
  - name: bq-catalog
    bigquery_metastore: {}
```

```bash
# トピックに Iceberg アーカイブを設定
bufstream kafka config topic set --topic orders \
  --name bufstream.archive.kind --value ICEBERG
bufstream kafka config topic set --topic orders \
  --name bufstream.archive.iceberg.catalog --value my-catalog
bufstream kafka config topic set --topic orders \
  --name bufstream.archive.iceberg.table --value warehouse.orders

# パーティション粒度（MONTHLY / DAILY / HOURLY）
bufstream kafka config topic set --topic orders \
  --name bufstream.archive.parquet.granularity --value DAILY
```

詳細な設定は `references/bufstream-config.md` を参照。

---

## Kafka 互換性

Bufstream は標準 Kafka クライアント（librdkafka, kafka-go, sarama 等）と互換。
既存ツール（AKHQ, Redpanda Console, Kpow, kafkactl）もそのまま使える。

### クライアント設定のポイント

- `bootstrap.servers`: Bufstream ブローカーのアドレス
- 標準的な Kafka producer/consumer API がそのまま動作
- ACL ベースの認可をサポート（SASL/mTLS 認証と組み合わせ）

### 認証方式

| 方式 | 説明 |
|------|------|
| SASL PLAIN | ユーザー名/パスワード |
| SASL SCRAM | チャレンジ-レスポンス |
| SASL OAUTHBEARER | OAuth 2.0 トークン |
| mTLS | クライアント証明書認証 |

### ACL 設定例（Helm）

```yaml
kafka:
  authorization:
    superUsers:
      - admin@example.com
    allowEveryoneIfNoAclFound: false
```

---

## デプロイメントガイド

### デプロイ先の選定

| 環境 | メタデータ | オブジェクトストレージ |
|------|-----------|---------------------|
| ローカル | インメモリ | ローカルFS |
| Docker | PostgreSQL | S3/GCS/Azure |
| AWS (EKS) | PostgreSQL / etcd | S3 |
| GCP (GKE) | PostgreSQL / Spanner / etcd | GCS |
| Azure (AKS) | PostgreSQL / etcd | Azure Blob |

### Docker デプロイ

```yaml
# bufstream.yaml
version: v1beta1
data:
  s3:
    bucket: my-bucket
    region: ap-northeast-1
    endpoint: http://minio:9000
    force_path_style: true
metadata:
  postgres:
    string: postgresql://user:pass@postgres:5432/bufstream
```

### Helm デプロイ（Kubernetes）

```yaml
# bufstream-values.yaml
cluster: bufstream-prod
storage:
  use: s3
  s3:
    bucket: bufstream-data
    region: ap-northeast-1
schemaRegistry:
  bsr:
    host: buf.build
kafka:
  authorization:
    superUsers:
      - admin@example.com
```

```bash
helm install bufstream oci://buf.build/helm/bufstream \
  -f bufstream-values.yaml
```

詳細なクラウド別デプロイ手順は `references/bufstream-deploy.md` を参照。

---

## オブザーバビリティ

### メトリクス

```yaml
# Prometheus エクスポート
debug:
  listen_address: 0.0.0.0:9090
# /metrics エンドポイントで公開

# OTLP エクスポート
metrics:
  otlp:
    type: http  # or grpc
    url: http://otel-collector:4318
```

### ログ

```yaml
logging:
  level: info  # debug | info | warn | error
# JSON 形式で stderr に出力
```

### トレーシング

```yaml
traces:
  otlp:
    type: http
    url: http://otel-collector:4318
    trace_ratio: 0.1  # サンプリングレート
```

---

## デシジョンツリー

### Kafka vs Bufstream

```
データレイクハウスが主要な消費先?
  └─ Yes → Bufstream（Iceberg 直接統合で ETL 不要）
  └─ No
     ├─ コスト最適化が優先?
     │   └─ Yes → Bufstream（S3 ベースで 1/8 コスト）
     │   └─ No → Kafka（成熟したエコシステム）
     ├─ スキーマ強制をブローカーで行いたい?
     │   └─ Yes → Bufstream（ネイティブ対応）
     │   └─ No → Kafka + Schema Registry
     └─ 既存 Kafka クライアント資産がある?
         └─ Yes → Bufstream（互換性あり、移行コスト低い）
```

### gRPC vs ConnectRPC vs REST

```
ブラウザクライアントが必要?
  └─ Yes → ConnectRPC（HTTP/1.1 + JSON 対応）
  └─ No
     ├─ 高性能サービス間通信?
     │   └─ gRPC（HTTP/2 ストリーミング）
     └─ パブリック API?
         └─ REST + Protobuf スキーマ（Vanguard で変換可）
```

---

## よくあるトラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| `buf lint` でパッケージ名エラー | パッケージ名がディレクトリ構造と不一致 | `package` をファイルパスに合わせる |
| `buf breaking` で大量エラー | `--against` の比較先が古すぎる | 直近のリリースタグと比較 |
| `buf generate` でプラグインエラー | リモートプラグインのバージョン不整合 | `buf dep update` で依存更新 |
| Bufstream が起動しない | metadata 接続エラー | PostgreSQL/etcd の接続文字列を確認 |
| 検証が効かない | スキーマプロバイダー未設定 | `schema_registry` + トピック設定を確認 |
| Iceberg テーブルが空 | `bufstream admin clean topics` 未実行 | アーカイブのフラッシュを実行 |
