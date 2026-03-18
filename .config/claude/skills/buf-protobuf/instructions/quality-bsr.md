# 品質ゲート + BSR 統合

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
