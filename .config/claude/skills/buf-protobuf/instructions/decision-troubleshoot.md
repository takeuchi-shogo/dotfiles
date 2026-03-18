# デシジョンツリー + トラブルシューティング

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

## よくあるトラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| `buf lint` でパッケージ名エラー | パッケージ名がディレクトリ構造と不一致 | `package` をファイルパスに合わせる |
| `buf breaking` で大量エラー | `--against` の比較先が古すぎる | 直近のリリースタグと比較 |
| `buf generate` でプラグインエラー | リモートプラグインのバージョン不整合 | `buf dep update` で依存更新 |
| Bufstream が起動しない | metadata 接続エラー | PostgreSQL/etcd の接続文字列を確認 |
| 検証が効かない | スキーマプロバイダー未設定 | `schema_registry` + トピック設定を確認 |
| Iceberg テーブルが空 | `bufstream admin clean topics` 未実行 | アーカイブのフラッシュを実行 |
