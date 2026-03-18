# Buf CLI 設定 + コード生成

## buf.yaml（ワークスペース定義）

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

## buf.gen.yaml（コード生成定義）

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

## 主要コマンド

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
