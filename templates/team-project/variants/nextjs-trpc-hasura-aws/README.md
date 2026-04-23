# Variant: Next.js + tRPC + Hasura + AWS

副業系スタック向けの concrete example。base をコピー後、この variant の中身を上書きすると placeholder の多くが埋まった状態で始められる。

## 想定スタック

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui |
| API Layer | tRPC v11 (Next.js Route Handlers 上) |
| Data Layer | Hasura GraphQL Engine (PostgreSQL 直結) |
| Database | PostgreSQL (RDS or Supabase) |
| Infra | AWS (Amplify / Vercel / ECS for Hasura, RDS, S3) |
| CI/CD | GitHub Actions |
| 認証 | Clerk / Auth0 / NextAuth.js |
| 監視 | AWS CloudWatch + Sentry |

## 典型的なディレクトリ構成

```
<repo>/
├── apps/
│   └── web/                  # Next.js (tRPC router を内包)
│       ├── src/server/trpc/  # tRPC routers
│       └── src/app/api/trpc/ # Route Handler
├── hasura/
│   ├── metadata/             # Hasura metadata (declarative)
│   └── migrations/           # Hasura migration
├── infra/
│   └── terraform/aws/        # RDS, ECS, S3, CloudFront
├── docs/
└── .github/
    ├── CODEOWNERS
    └── workflows/
```

## 同梱ファイル

- `facts.md` — tRPC router / Hasura endpoint / AWS リソース
- `docs/decisions/0001-tech-stack.md` — スタック選定 ADR (なぜ Hasura + tRPC 両立か)
- `.github/CODEOWNERS` — Zone 別 reviewer

## 適用手順

```bash
cp -R /path/to/dotfiles/templates/team-project/base/* /path/to/your-project/
cp -R /path/to/dotfiles/templates/team-project/variants/nextjs-trpc-hasura-aws/* /path/to/your-project/
cd /path/to/your-project && find . -name '*.tpl' -exec sh -c 'mv "$0" "${0%.tpl}"' {} \;
# placeholder 置換
```

## tRPC と Hasura の役割分担 (この variant の前提)

- **Hasura**: CRUD の 80% を自動生成 (Row-Level Security で権限統制)
- **tRPC**: ビジネスロジック・外部 API 呼び出し・決済・認証フロー等の「手書きコード」
- **Frontend**: Hasura は codegen で生成した GraphQL client、tRPC は `@trpc/client` で型共有

両方を使うことで boilerplate を減らしつつ、複雑なユースケースを逃がす設計。
