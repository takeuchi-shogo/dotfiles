# Bufstream 設定リファレンス

## bufstream.yaml 完全リファレンス

### トップレベルキー

| キー | 型 | 必須 | 説明 |
|------|-----|------|------|
| `version` | string | Yes | `v1beta1` |
| `cluster` | string | Yes | クラスター名。同一クラスターのブローカーは同じ値 |
| `zone` | string | No | データセンター/AZ。未指定時は自動検出 |
| `recovery_timestamp` | string | No | メタデータバックアップ復元時のタイムスタンプ |

### metadata（メタデータストア）

いずれか1つを選択:

```yaml
# PostgreSQL
metadata:
  postgres:
    string: postgresql://user:pass@host:5432/dbname
    # または Cloud SQL
    cloud_sql:
      instance: project:region:instance
      database: bufstream
      user: bufstream

# etcd
metadata:
  etcd:
    addresses:
      - etcd-0:2379
      - etcd-1:2379
      - etcd-2:2379

# Spanner (GCP)
metadata:
  spanner:
    database: projects/my-project/instances/my-instance/databases/bufstream
```

### data（オブジェクトストレージ）

未指定時: metadata 設定があればローカル FS (`$HOME/.local/share/bufstream`)、なければインメモリ。

```yaml
# S3
data:
  s3:
    bucket: my-bucket
    region: ap-northeast-1
    endpoint: http://minio:9000      # MinIO 等のカスタムエンドポイント
    force_path_style: true           # パスス タイル URL を使用
    access_key_id: AKIAIOSFODNN      # 明示的な認証情報（省略時は IAM ロール）
    secret_access_key: wJalrXUtn

# GCS
data:
  gcs: gs://my-bucket/prefix/

# Azure Blob
data:
  azure: https://myaccount.blob.core.windows.net/mycontainer/prefix
```

### kafka（リスナー設定）

```yaml
kafka:
  listeners:
    - name: internal
      listen_address: 0.0.0.0:9092
      advertise_address: bufstream.example.com:9092
      tls:
        cert_chain:
          path: /certs/server.crt
        private_key:
          path: /certs/server.key
        client_ca:
          path: /certs/ca.crt
      authentication:
        sasl:
          plain:
            users:
              - username: producer
                password:
                  env_var: PRODUCER_PASSWORD
          # or scram / oauthbearer
        mtls:
          principal_source: SUBJECT_COMMON_NAME
          # ANONYMOUS, SUBJECT_COMMON_NAME, SAN_DNS, SAN_URI

  authorization:
    super_users:
      - admin@example.com
    allow_everyone_if_no_acl_found: false
```

### schema_registry（スキーマプロバイダー）

```yaml
schema_registry:
  bsr:
    host: buf.build           # またはプライベート BSR ホスト
    token:
      env_var: BUF_TOKEN      # 認証トークン
    tls:
      insecure: false
```

### iceberg（Iceberg カタログ）

```yaml
iceberg:
  # REST カタログ
  - name: rest-catalog
    rest:
      url: https://iceberg-rest.example.com
      uri_prefix: /api/v1
      warehouse: my-warehouse
      tls:
        insecure: false
      authentication:
        bearer:
          token:
            env_var: ICEBERG_TOKEN

  # AWS Glue Data Catalog
  - name: glue-catalog
    aws_glue_data_catalog:
      account_id: "123456789012"
      region: ap-northeast-1

  # BigQuery Metastore
  - name: bq-catalog
    bigquery_metastore:
      project: my-gcp-project
      location: asia-northeast1
```

### observability（オブザーバビリティ）

```yaml
debug:
  listen_address: 0.0.0.0:9090  # /metrics, /debug/pprof

logging:
  level: info  # debug | info | warn | error

metrics:
  otlp:
    type: http  # http | grpc
    url: http://otel-collector:4318
  include_labels:
    - key: environment
      values: [production, staging]

traces:
  otlp:
    type: http
    url: http://otel-collector:4318
    trace_ratio: 0.1
```

### admin（管理インターフェース）

```yaml
admin:
  listen_address: 0.0.0.0:9089
  tls:
    cert_chain:
      path: /certs/admin.crt
    private_key:
      path: /certs/admin.key
```

### Data Source フォーマット

設定値は以下の形式で指定可能:

```yaml
# インライン文字列
token: my-token

# ファイルパス
token:
  path: /secrets/token

# 環境変数
token:
  env_var: BUF_TOKEN

# Base64 エンコード
cert:
  encoding: base64
  path: /secrets/cert.b64
```

---

## トピックパラメータ一覧

### スキーマ関連

| パラメータ | 説明 |
|-----------|------|
| `buf.registry.value.schema.module` | BSR モジュール名（BSR 使用時に必須） |
| `buf.registry.value.schema.message` | 完全修飾メッセージ名（常に必須） |

### 検証関連

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `bufstream.validate.mode` | `reject` / `dlq` | 検証モード |
| `bufstream.validate.dlq.topic` | string | DLQ トピック名（デフォルト: `{topic}.dlq`） |

### Iceberg アーカイブ関連

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `bufstream.archive.kind` | `ICEBERG` | アーカイブ種別 |
| `bufstream.archive.iceberg.catalog` | string | カタログ名 |
| `bufstream.archive.iceberg.table` | string | `namespace.table` 形式 |
| `bufstream.archive.parquet.granularity` | `MONTHLY` / `DAILY` / `HOURLY` | パーティション粒度 |

### データ保持

| パラメータ | デフォルト | 説明 |
|-----------|----------|------|
| `retention.ms` | 7日 | データ保持期間（負値で無期限） |
| `retention.bytes` | -1 | データ保持サイズ上限 |

---

## Helm values.yaml リファレンス

```yaml
nameOverride: ""
namespaceOverride: ""
namespaceCreate: false
imagePullSecrets: []
cluster: bufstream
zone: ""
discoverZoneFromNode: false

# ストレージ
storage:
  use: s3  # s3 | gcs | azure
  s3:
    bucket: bufstream-data
    region: ap-northeast-1
    forcePathStyle: false
    endpoint: ""

# メタデータ
metadata:
  use: postgres  # postgres | etcd | spanner
  postgres:
    dsn: postgresql://user:pass@host:5432/bufstream

# スキーマレジストリ
schemaRegistry:
  bsr:
    host: buf.build

# Kafka
kafka:
  authorization:
    superUsers:
      - admin@example.com
    allowEveryoneIfNoAclFound: false

# Iceberg
iceberg:
  catalogs:
    my-catalog:
      use: rest  # rest | awsGlue | bigQuery
      rest:
        url: https://iceberg-rest.example.com

# mTLS
mtls:
  principalSource: ""  # ANONYMOUS | SUBJECT_COMMON_NAME | SAN_DNS | SAN_URI
```

---

## CLI コマンドリファレンス

### bufstream serve

```bash
bufstream serve [flags]
  -c, --config string    設定ファイルパス（デフォルト: bufstream.yaml）
  --schema string        ローカルスキーマディレクトリ（開発用）
```

### bufstream kafka topic

```bash
bufstream kafka topic create <name> --partitions <n>
bufstream kafka topic delete <name>
bufstream kafka topic list
bufstream kafka topic describe <name>
```

### bufstream kafka config topic

```bash
bufstream kafka config topic set --topic <name> --name <key> --value <val>
bufstream kafka config topic get --topic <name> --name <key>
bufstream kafka config topic list --topic <name>
```

### bufstream admin

```bash
bufstream admin clean topics    # Iceberg カタログの同期
bufstream admin status          # ブローカーステータス
```

### bufstream migrate

```bash
bufstream migrate    # メタデータストアのマイグレーション
```
