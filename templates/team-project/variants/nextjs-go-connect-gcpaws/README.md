# Variant: Next.js + Go + Connect RPC + GCP/AWS

本業系スタック向けの concrete example。base をコピー後、この variant の中身を上書きすると placeholder の多くが埋まった状態で始められる。

## 想定スタック

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind |
| Backend | Go 1.22 + Connect RPC (buf) + sqlc or GORM |
| Database | PostgreSQL 15 (Cloud SQL / RDS) |
| Infra | GCP (Cloud Run, Cloud SQL) + AWS (S3, CloudFront, Route53) |
| CI/CD | GitHub Actions |
| 認証 | Firebase Auth or Auth0 |
| 監視 | Cloud Logging + Cloud Monitoring + Sentry |

## 典型的なディレクトリ構成

```
<repo>/
├── apps/
│   ├── web/                  # Next.js
│   └── api/                  # Go Connect RPC
├── proto/                    # Protocol Buffers 定義
├── infra/
│   ├── terraform/            # Terraform (GCP + AWS)
│   └── k8s/                  # (optional) Kubernetes manifests
├── migrations/               # DB migration (sqlc-compatible or goose)
├── docs/
└── .github/
    ├── CODEOWNERS
    └── workflows/
```

## 同梱ファイル

- `facts.md` — API endpoint / DB schema / GCP-AWS 両リソースの index
- `docs/decisions/0001-tech-stack.md` — スタック選定 ADR
- `.github/CODEOWNERS` — Zone 別 reviewer

## 適用手順

```bash
# 1. base を project にコピー
cp -R /path/to/dotfiles/templates/team-project/base/* /path/to/your-project/

# 2. この variant の中身を上書き
cp -R /path/to/dotfiles/templates/team-project/variants/nextjs-go-connect-gcpaws/* /path/to/your-project/

# 3. .tpl 拡張子を外す
cd /path/to/your-project && find . -name '*.tpl' -exec sh -c 'mv "$0" "${0%.tpl}"' {} \;

# 4. 残りの placeholder (owner 名等) を置換
```

Owner 名・具体的な URL は project ごとに異なるので、`{{*_OWNER_GH}}` / `{{PROJECT_NAME}}` / `{{PROD_URL}}` 等は手動で置換する。
