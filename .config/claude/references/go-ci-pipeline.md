---
status: reference
last_reviewed: 2026-04-23
---

# Go CI Pipeline Guide

GitHub Actions での Go プロジェクト CI/CD パイプライン設定ガイド。

## Quick Reference

| Stage | Tool | Purpose |
|-------|------|---------|
| Test | `go test -race` | Unit + race detection |
| Coverage | `codecov/codecov-action` | カバレッジ報告 |
| Lint | `golangci-lint` | 包括的リンティング |
| Vet | `go vet` | 組み込み静的解析 |
| SAST | `gosec`, `CodeQL`, `Bearer` | セキュリティ静的解析 |
| Vuln scan | `govulncheck` | 既知脆弱性検出 |
| Docker | `docker/build-push-action` | マルチプラットフォームイメージ |
| Deps | Dependabot / Renovate | 依存関係自動更新 |
| Release | GoReleaser | バイナリリリース自動化 |

## Testing

### 必須テストフラグ

```yaml
- run: go test -race -shuffle=on -coverprofile=coverage.out ./...
```

| フラグ | 目的 |
|--------|------|
| `-race` | データ競合検出（CI 必須） |
| `-shuffle=on` | テスト順序依存の検出 |
| `-coverprofile` | カバレッジデータ生成 |
| `-count=1` | テストキャッシュ無効化（integration test 用） |

### Go Version Matrix

`go.mod` の `go` ディレクティブに基づいてマトリクスを設定:

```
go 1.24 → matrix: ["1.24", "1.25", "1.26", "stable"]
go 1.25 → matrix: ["1.25", "1.26", "stable"]
go 1.26 → matrix: ["1.26", "stable"]
```

- `fail-fast: false` で1バージョンの失敗が他をキャンセルしないようにする

### Tidy Check

```yaml
- run: go mod tidy && git diff --exit-code
```

## Linting

golangci-lint は CI で必須:

```yaml
- uses: golangci/golangci-lint-action@v6
  with:
    version: latest
```

## Security

### 必須: govulncheck

実際のコードパスで呼ばれる脆弱性のみ報告（汎用 CVE スキャナより精度が高い）:

```yaml
- run: go install golang.org/x/vuln/cmd/govulncheck@latest
- run: govulncheck ./...
```

### 推奨: CodeQL

```yaml
- uses: github/codeql-action/init@v3
  with:
    languages: go
    queries: security-extended
```

| Query Suite | 内容 |
|-------------|------|
| default | 標準セキュリティクエリ |
| security-extended | 追加セキュリティ（やや低精度） |
| security-and-quality | セキュリティ + 保守性 |

## Dependency Management

| 機能 | Dependabot | Renovate |
|------|-----------|----------|
| `go mod tidy` 自動実行 | ❌ | ✅ (`gomodTidy`) |
| ネイティブ automerge | ❌ (別 workflow 要) | ✅ |
| グループ化柔軟性 | 基本的 | 高い |
| Regex manager | ❌ | ✅ (Dockerfile, Makefile) |
| Monorepo 対応 | 基本的 | ✅ (go.work 対応) |

## Release: GoReleaser

| プロジェクト | 設定 |
|-------------|------|
| CLI/Program | クロスコンパイル + アーカイブ + Docker |
| Library | changelog のみ（ビルドスキップ） |
| Monorepo | 複数バイナリ (`cmd/api/`, `cmd/worker/`) |

```yaml
# release.yml (tag push 時のみ)
on:
  push:
    tags: ["v*"]
```

## Docker

- QEMU + Buildx でマルチプラットフォーム (`linux/amd64,linux/arm64`)
- PR では `push: false`（ビルドのみ、push しない）
- Provenance + SBOM 生成
- Trivy でコンテナイメージスキャン

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `-race` なし | 常に `go test -race` |
| `-shuffle=on` なし | テスト順序依存を検出 |
| integration test キャッシュ | `-count=1` でキャッシュ無効化 |
| `go mod tidy` 未チェック | `go mod tidy && git diff --exit-code` |
| `fail-fast: false` なし | 1版の失敗で他をキャンセルしない |
| Action バージョン未固定 | `@vN` を使用（`@master` 禁止） |
| `permissions` ブロックなし | job ごとに最小権限を設定 |
| govulncheck 未実行 | CI 必須 |

## Repository Security Checklist

- [ ] Branch protection: main に直接 push 禁止
- [ ] Required status checks: test, lint, security
- [ ] Required approvals: 1+ reviewer
- [ ] Workflow permissions: Read-only by default
- [ ] Secrets: DOCKERHUB_TOKEN 等は Repository secrets に
- [ ] Dependabot or Renovate 有効化
