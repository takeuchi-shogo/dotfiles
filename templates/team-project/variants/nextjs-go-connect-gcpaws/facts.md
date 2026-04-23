# Project Facts — {{PROJECT_NAME}}

> Next.js + Go + Connect RPC + GCP/AWS 向け concrete example。
> `{{PROJECT_NAME}}` 等の placeholder は project 固有値に置換する。

## Environments

| 名前 | URL | Runtime | 所有 |
|------|-----|---------|------|
| Production | {{PROD_URL}} | Cloud Run (asia-northeast1) | {{INFRA_OWNER}} |
| Staging | {{STAGING_URL}} | Cloud Run (asia-northeast1) | {{INFRA_OWNER}} |
| Local | http://localhost:3000 (web) / http://localhost:8080 (api) | docker compose | 各自 |

## API Endpoints (Connect RPC)

**Protocol**: Connect RPC (buf) over HTTPS
**Base URL**: `{{API_BASE_URL}}` (例: `https://api.{{DOMAIN}}`)
**Proto 定義**: `proto/` ディレクトリ (buf.yaml で管理)

| Service | Method | Auth | 概要 |
|---------|--------|------|------|
| `AuthService` | `Login` | Public | ログイン → JWT + refresh token |
| `AuthService` | `RefreshToken` | Refresh Token | アクセストークン更新 |
| `UserService` | `GetMe` | Bearer | 自分の情報 |
| `{{RESOURCE}}Service` | `Create{{RESOURCE}}` | Bearer | {{RESOURCE}} 作成 |

> 全サービス一覧: `buf.build/{{BUF_ORG}}/{{BUF_REPO}}` または `proto/` を参照
> TypeScript SDK 生成: `buf generate` → `apps/web/src/gen/`
> Go SDK: `buf generate` → `apps/api/gen/`

## Database Schema

**DBMS**: PostgreSQL 15 (Cloud SQL for PostgreSQL)
**接続**: Cloud SQL Auth Proxy (local) / Unix socket (Cloud Run)
**Migration**: `goose` または `atlas` (`migrations/` 配下)
**Query**: `sqlc` で type-safe コード生成

### 主要テーブル

```sql
-- users
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
email       TEXT UNIQUE NOT NULL
created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()

-- sessions (refresh token 用)
id           UUID PRIMARY KEY
user_id      UUID REFERENCES users(id) ON DELETE CASCADE
token_hash   TEXT NOT NULL
expires_at   TIMESTAMPTZ NOT NULL

-- {{RESOURCE}}
id           UUID PRIMARY KEY
user_id      UUID REFERENCES users(id)
...
```

> 全 schema: `migrations/*.sql` を参照 / sqlc 生成コード: `apps/api/gen/sqlc/`

## External Services

| Service | 用途 | Secret |
|---------|------|--------|
| Firebase Auth (or Auth0) | 認証 | `FIREBASE_SERVICE_ACCOUNT_JSON` |
| Stripe | 決済 | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` |
| SendGrid | メール | `SENDGRID_API_KEY` |
| Sentry | エラー監視 | `SENTRY_DSN` (FE + BE 別) |
| Cloud Logging | ログ集約 | — (GCP IAM) |

## Environment Variables

```
# 必須 (backend) — 値はすべて `<REPLACE>` placeholder。実値は Secret Manager で配信
DATABASE_URL=<REPLACE: postgres connection URL>
JWT_SIGNING_KEY=<REPLACE: 256-bit random hex, e.g. `openssl rand -hex 32`>
FIREBASE_SERVICE_ACCOUNT_JSON=<REPLACE: path to service account JSON or raw JSON>
STRIPE_SECRET_KEY=<REPLACE: Stripe live secret (starts with sk_live_)>
STRIPE_WEBHOOK_SECRET=<REPLACE: Stripe webhook signing secret (starts with whsec_)>

# 必須 (frontend)
NEXT_PUBLIC_API_URL=https://api.{{DOMAIN}}
NEXT_PUBLIC_FIREBASE_CONFIG=<REPLACE: Firebase config JSON>
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=<REPLACE: Stripe publishable key (starts with pk_live_)>
NEXT_PUBLIC_SENTRY_DSN=<REPLACE: Sentry DSN URL>

# オプション
LOG_LEVEL=info
```

> Local: `.env.local` (gitignore 済み)
> Production: GCP Secret Manager (`gcloud secrets`) で配信

## AWS リソース (補助)

| Resource | 用途 |
|----------|------|
| S3 (`s3://{{BUCKET_NAME}}`) | 画像 / アップロード |
| CloudFront | S3 CDN + custom domain |
| Route53 | DNS |
| SES (optional) | SendGrid のバックアップ |

> Terraform: `infra/terraform/aws/`

## GCP リソース (主軸)

| Resource | 用途 |
|----------|------|
| Cloud Run (`{{API_SERVICE_NAME}}`) | Go backend |
| Cloud Run (`{{WEB_SERVICE_NAME}}`) | Next.js (optional, Vercel でも可) |
| Cloud SQL (PostgreSQL) | 主 DB |
| Secret Manager | secrets |
| Cloud Logging | log sink |
| Cloud Monitoring | メトリクス & アラート |

> Terraform: `infra/terraform/gcp/`

## CI/CD

- **PR チェック**: `.github/workflows/ci.yml`
  - `pnpm typecheck && pnpm test` (frontend)
  - `go test ./... && go vet ./...` (backend)
  - `buf lint && buf breaking` (proto)
  - `terraform fmt -check && tflint` (infra)
- **Deploy**: `.github/workflows/deploy-{staging,production}.yml`
  - Cloud Run に `gcloud run deploy`
  - Vercel に `vercel --prod` (frontend を Vercel にする場合)

## Directory Conventions

```
<repo>/
├── apps/
│   ├── web/                   # Next.js — @{{FE_OWNER_GH}}
│   └── api/                   # Go Connect RPC — @{{BE_OWNER_GH}}
├── proto/                     # .proto + buf.yaml
├── infra/terraform/{aws,gcp}/ # @{{INFRA_OWNER_GH}}
├── migrations/                # DB — @{{DB_OWNER_GH}}
├── docs/                      # facts.md, decisions/, zones/, security/
└── .github/                   # CODEOWNERS, workflows
```

## Release Cadence

- Staging: 毎 PR merge で自動 deploy
- Production: 平日 10-16 時のみ手動 approval で deploy (金曜夕方 + 休前日禁止)
- Hotfix: `hotfix/*` branch → 直接 production (2 名承認必須)

---

**Last Updated**: {{DATE}} / **By**: {{UPDATER}}
