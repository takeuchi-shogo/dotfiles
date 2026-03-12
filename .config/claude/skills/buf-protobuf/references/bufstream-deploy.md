# Bufstream デプロイメントガイド

## デプロイメント概要

### 前提条件

| コンポーネント | 要件 |
|--------------|------|
| メタデータストア | PostgreSQL 14+ / etcd 3.5+ / Spanner |
| オブジェクトストレージ | S3 / GCS / Azure Blob |
| ネットワーク | Kafka クライアントからブローカーへの TCP 接続 |
| 認証（任意） | SASL / mTLS 証明書 |

---

## Docker デプロイ

### 最小構成（ローカル開発）

```bash
# バイナリダウンロード
curl -sSL -o bufstream \
  "https://buf.build/dl/bufstream/latest/bufstream-$(uname -s)-$(uname -m)" && \
  chmod +x bufstream

# インメモリモードで起動
./bufstream serve

# ローカルスキーマ付きで起動
./bufstream serve --schema .
```

### Docker + PostgreSQL + MinIO

```yaml
# bufstream.yaml
version: v1beta1
cluster: local-dev
data:
  s3:
    bucket: bufstream
    region: us-east-1
    endpoint: http://minio:9000
    force_path_style: true
metadata:
  postgres:
    string: postgresql://bufstream:password@postgres:5432/bufstream
kafka:
  listeners:
    - listen_address: 0.0.0.0:9092
```

### クラウド別 Docker 設定

**AWS (S3 + PostgreSQL)**:
```yaml
version: v1beta1
data:
  s3:
    bucket: my-bufstream-bucket
    region: ap-northeast-1
metadata:
  postgres:
    string: postgresql://user:pass@rds-host:5432/bufstream
```

**GCP (GCS + PostgreSQL)**:
```yaml
version: v1beta1
data:
  gcs: gs://my-bufstream-bucket/prefix/
metadata:
  postgres:
    string: postgresql://user:pass@cloud-sql-host:5432/bufstream
```

**Azure (Blob + PostgreSQL)**:
```yaml
version: v1beta1
data:
  azure: https://myaccount.blob.core.windows.net/bufstream/prefix
metadata:
  postgres:
    string: postgresql://user:pass@azure-pg-host:5432/bufstream
```

---

## Kubernetes (Helm) デプロイ

### 基本手順

```bash
# 1. values ファイルを作成
cat > bufstream-values.yaml << 'EOF'
cluster: bufstream-prod
storage:
  use: s3
  s3:
    bucket: bufstream-data
    region: ap-northeast-1
metadata:
  use: postgres
  postgres:
    dsn: postgresql://user:pass@pg-host:5432/bufstream
schemaRegistry:
  bsr:
    host: buf.build
EOF

# 2. Helm でインストール
helm install bufstream oci://buf.build/helm/bufstream \
  -f bufstream-values.yaml

# 3. アップグレード
helm upgrade bufstream oci://buf.build/helm/bufstream \
  -f bufstream-values.yaml
```

### AWS EKS

```yaml
# bufstream-values.yaml
cluster: bufstream-eks
storage:
  use: s3
  s3:
    bucket: bufstream-data
    region: ap-northeast-1
    # EKS Pod Identity を使用（推奨）
    # forcePathStyle: false
metadata:
  use: postgres
  postgres:
    dsn: postgresql://user:pass@rds-endpoint:5432/bufstream
discoverZoneFromNode: true
```

**IAM ポリシー（S3 アクセス）**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bufstream-data",
        "arn:aws:s3:::bufstream-data/*"
      ]
    }
  ]
}
```

### GCP GKE

```yaml
# bufstream-values.yaml
cluster: bufstream-gke
storage:
  use: gcs
  gcs:
    bucket: gs://bufstream-data/
metadata:
  use: postgres  # or spanner
  postgres:
    dsn: postgresql://user:pass@cloud-sql-proxy:5432/bufstream
  # spanner:
  #   database: projects/proj/instances/inst/databases/bufstream
discoverZoneFromNode: true
```

### Azure AKS

```yaml
# bufstream-values.yaml
cluster: bufstream-aks
storage:
  use: azure
  azure:
    uri: https://account.blob.core.windows.net/bufstream/
metadata:
  use: postgres
  postgres:
    dsn: postgresql://user:pass@azure-pg:5432/bufstream
```

---

## 認証設定

### SASL PLAIN

```yaml
# bufstream.yaml
kafka:
  listeners:
    - listen_address: 0.0.0.0:9092
      authentication:
        sasl:
          plain:
            users:
              - username: producer
                password:
                  env_var: PRODUCER_PASSWORD
              - username: consumer
                password:
                  env_var: CONSUMER_PASSWORD
```

### SASL OAUTHBEARER

```yaml
kafka:
  listeners:
    - listen_address: 0.0.0.0:9092
      authentication:
        sasl:
          oauthbearer:
            jwks_url: https://auth.example.com/.well-known/jwks.json
```

### mTLS

```yaml
kafka:
  listeners:
    - listen_address: 0.0.0.0:9092
      tls:
        cert_chain:
          path: /certs/server.crt
        private_key:
          path: /certs/server.key
        client_ca:
          path: /certs/ca.crt
      authentication:
        mtls:
          principal_source: SUBJECT_COMMON_NAME
```

**Helm 設定**:
```yaml
mtls:
  principalSource: SUBJECT_COMMON_NAME
  # ANONYMOUS | SUBJECT_COMMON_NAME | SAN_DNS | SAN_URI
```

---

## クラスター推奨事項

### インスタンスサイジング

| ワークロード | 推奨インスタンス | ブローカー数 |
|-------------|----------------|-------------|
| 開発/テスト | 2 vCPU, 4GB RAM | 1 |
| 小規模本番 | 4 vCPU, 8GB RAM | 3 |
| 中規模本番 | 8 vCPU, 16GB RAM | 3-5 |
| 大規模本番 | 16+ vCPU, 32GB+ RAM | 5+ |

### メタデータストア選定

| ストア | 推奨場面 |
|--------|---------|
| PostgreSQL | 汎用（最もよくテストされている） |
| etcd | 低レイテンシ要件、既存 etcd インフラ |
| Spanner | GCP、グローバル分散要件 |

### ネットワーク設計

- ブローカーとオブジェクトストレージは同一リージョンに配置
- `advertise_address` をクライアントが到達可能なアドレスに設定
- Kubernetes 内部では Service 経由、外部からは LoadBalancer/Ingress 経由

---

## サードパーティ統合

| ツール | 用途 | 互換性 |
|--------|------|--------|
| AKHQ | Web UI でトピック管理 | 完全互換 |
| Redpanda Console | Web UI でクラスター監視 | 完全互換 |
| Kpow | エンタープライズ監視 | 完全互換 |
| kafkactl | CLI でトピック操作 | 完全互換 |
| Tigris | オブジェクトストレージ代替 | S3 互換 |
| MinIO | ローカル S3 代替 | S3 互換 |

---

## Iceberg デモ環境（Docker Compose）

Bufstream + MinIO + PostgreSQL + Iceberg REST Catalog + Spark + Jupyter の
一体型デモ環境:

```bash
git clone https://github.com/bufbuild/bufstream-demo.git
cd bufstream-demo

# Iceberg デモ環境を起動
docker compose -f iceberg/docker-compose.yaml up

# テストデータ生成
go run ./cmd/bufstream-demo-produce --topic orders

# Iceberg テーブルの同期
docker exec bufstream /usr/local/bin/bufstream admin clean topics

# Jupyter で SQL クエリ
# http://localhost:8888/notebooks/notebooks/bufstream-quickstart.ipynb
```
