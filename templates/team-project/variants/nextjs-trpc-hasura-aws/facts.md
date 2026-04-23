# Project Facts — {{PROJECT_NAME}}

> Next.js + tRPC + Hasura + AWS 向け concrete example。

## Environments

| 名前 | URL | Runtime | 所有 |
|------|-----|---------|------|
| Production | {{PROD_URL}} | Vercel (web) + ECS Fargate (Hasura) | {{INFRA_OWNER}} |
| Staging | {{STAGING_URL}} | Vercel Preview + ECS staging | {{INFRA_OWNER}} |
| Local | http://localhost:3000 (web) / http://localhost:8080 (hasura) | docker compose | 各自 |

## API Layers

### tRPC (`/api/trpc/*`)

**Base URL**: `{{PROD_URL}}/api/trpc`
**Source**: `apps/web/src/server/trpc/`
**型共有**: `@trpc/client` で FE 側に型が自動伝播

| Router | 用途 | Auth |
|--------|------|------|
| `auth` | ログイン・サインアップ・パスワードリセット | Public / User |
| `billing` | Stripe 連携 (サブスク、Webhook 処理) | User |
| `{{RESOURCE}}` | Hasura でカバーできない複雑処理 | User |

### Hasura GraphQL (`{{HASURA_URL}}/v1/graphql`)

**Endpoint**: `{{HASURA_URL}}/v1/graphql` (HTTPS, production)
**Admin Console**: `{{HASURA_URL}}/console` (IP 制限推奨)
**メタデータ**: `hasura/metadata/` (declarative、git 管理)
**Migration**: `hasura/migrations/` (`hasura migrate apply`)
**権限**: Role-Based (`user`, `admin`, `anonymous`) + Row-Level Security
**型生成**: `graphql-codegen` で TS 型と React hooks を生成 → `apps/web/src/gen/graphql/`

## Database Schema

**DBMS**: PostgreSQL 15 (Amazon RDS)
**接続**: Hasura 経由 (direct DB アクセスは migration/admin のみ)
**Migration**: Hasura migrations が正 (`hasura migrate create/apply`)

### 主要テーブル

```sql
-- users (Clerk user_id を外部キーに)
id               UUID PRIMARY KEY DEFAULT gen_random_uuid()
clerk_user_id    TEXT UNIQUE NOT NULL     -- Clerk の user.id
email            TEXT UNIQUE NOT NULL
created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()

-- subscriptions (Stripe subscription と 1:1)
id                     UUID PRIMARY KEY
user_id                UUID REFERENCES users(id)
stripe_subscription_id TEXT UNIQUE NOT NULL
status                 TEXT NOT NULL   -- active / past_due / canceled
```

> Hasura の Relationship / Permission 設定は `hasura/metadata/databases/default/tables/*.yaml`

## External Services

| Service | 用途 | Secret |
|---------|------|--------|
| Clerk | 認証 | `CLERK_SECRET_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` |
| Stripe | 決済 | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` |
| Resend / SES | メール | `RESEND_API_KEY` |
| Sentry | エラー監視 | `SENTRY_DSN` |

## Environment Variables

```
# 必須 (Next.js) — 値はすべて `<REPLACE>` placeholder。実値は SSM Parameter Store 等で配信
DATABASE_URL=<REPLACE: postgres connection URL, migration 用>
HASURA_GRAPHQL_ADMIN_SECRET=<REPLACE: 256-bit random hex, `openssl rand -hex 32`>
NEXT_PUBLIC_HASURA_URL={{HASURA_URL}}
CLERK_SECRET_KEY=<REPLACE: Clerk secret key (starts with sk_live_)>
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<REPLACE: Clerk publishable key (starts with pk_live_)>
STRIPE_SECRET_KEY=<REPLACE: Stripe secret (starts with sk_live_)>
STRIPE_WEBHOOK_SECRET=<REPLACE: Stripe webhook secret (starts with whsec_)>

# 必須 (Hasura - ECS task definition)
HASURA_GRAPHQL_DATABASE_URL=<REPLACE: postgres connection URL>
HASURA_GRAPHQL_ADMIN_SECRET=<REPLACE: same as Next.js 側>
HASURA_GRAPHQL_JWT_SECRET=<REPLACE: JSON {"type":"HS256","key":"<256-bit hex>"} for Clerk JWT 検証>
HASURA_GRAPHQL_ENABLE_CONSOLE=false      # production では false

# オプション
LOG_LEVEL=info
```

## AWS リソース

| Resource | 用途 |
|----------|------|
| RDS (PostgreSQL) | 主 DB |
| ECS Fargate (Hasura) | Hasura GraphQL Engine |
| ALB | ECS へのロードバランサ |
| S3 (`s3://{{BUCKET_NAME}}`) | 画像 / アップロード |
| CloudFront | S3 CDN |
| Route53 | DNS |
| SSM Parameter Store | secrets (ECS task 経由で注入) |

> Terraform: `infra/terraform/aws/`
> Frontend は Vercel に委譲 (AWS に置かない)

## CI/CD

- **PR チェック**: `.github/workflows/ci.yml`
  - `pnpm typecheck && pnpm test` (Next.js)
  - Hasura metadata diff (`hasura metadata diff`)
  - `terraform fmt -check && tflint` (infra)
- **Deploy**:
  - Frontend: Vercel (PR で preview, main で production)
  - Hasura: `.github/workflows/deploy-hasura.yml` で ECS task 更新 + `hasura migrate apply` + `hasura metadata apply`
  - Infra: Terraform Cloud or `terraform apply` を CI から

## Directory Conventions

```
<repo>/
├── apps/
│   └── web/                   # Next.js + tRPC — @{{FE_OWNER_GH}} (+ tRPC は @{{BE_OWNER_GH}})
│       └── src/server/trpc/   # tRPC routers (backend logic)
├── hasura/
│   ├── metadata/              # @{{DB_OWNER_GH}} + @{{BE_OWNER_GH}}
│   └── migrations/            # @{{DB_OWNER_GH}}
├── infra/terraform/aws/       # @{{INFRA_OWNER_GH}}
├── docs/
└── .github/
```

## Release Cadence

- Staging: `develop` branch → Vercel preview + ECS staging
- Production: `main` merge で自動 deploy (Vercel は instantly, Hasura は 5-10 分)
- Hasura migration は **backward-compatible** を原則、breaking change は ADR 起票

---

**Last Updated**: {{DATE}} / **By**: {{UPDATER}}
