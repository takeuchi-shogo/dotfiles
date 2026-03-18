# デプロイメントガイド + オブザーバビリティ

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
