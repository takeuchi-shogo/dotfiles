# Bufstream — 概要・アーキテクチャ・設定・トピック + セマンティック検証 + Iceberg 統合 + Kafka 互換性

## 概要

Bufstream は **データレイクハウス時代のための Kafka 互換メッセージキュー**。
Apache Kafka の 1/8 のコストで運用でき、以下の特徴を持つ:

- **スキーマ駆動**: ブローカーがスキーマを理解し、データ品質を自動強制
- **Iceberg 直接書き込み**: ETL パイプライン不要でデータレイクに直結
- **リーダーレス**: アクティブ-アクティブアーキテクチャ
- **オブジェクトストレージ**: S3/GCS/Azure Blob をデータストアに使用
- **完全セルフホスト**: AWS, GCP, Azure, オンプレミス対応
- **Jepsen 検証済み**: 正確性が独立検証されている

## アーキテクチャ

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

## クイックスタート

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

## bufstream.yaml 基本構成

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

## トピック設定

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
