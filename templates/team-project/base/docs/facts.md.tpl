# Project Facts — {{PROJECT_NAME}}

> 変わらない事実を index する。仕様変更時は「履歴を残して update」(削除しない)。
> **このファイルは session 再開時に最初に読むべき context**。

## Environments

| 名前 | URL | 用途 | 所有 |
|------|-----|------|------|
| Production | {{PROD_URL}} | 本番稼働 | {{INFRA_OWNER}} |
| Staging | {{STAGING_URL}} | QA / リリース前検証 | {{INFRA_OWNER}} |
| Local | http://localhost:{{LOCAL_PORT}} | 開発 | 各自 |

## API Endpoints (主要)

**Base URL**: `{{API_BASE_URL}}`

| Method | Path | 用途 | Auth |
|--------|------|------|------|
| POST | `/auth/login` | ログイン | Public |
| GET | `/users/me` | 自分のユーザー情報 | Bearer |
| POST | `/{{RESOURCE}}` | {{RESOURCE}} 作成 | Bearer |

> 全 endpoint 一覧: `{{API_SPEC_PATH}}` (OpenAPI / Proto) を参照

## Database Schema (主要)

**DBMS**: {{DBMS}} ({{DB_VERSION}})
**接続文字列**: `DATABASE_URL` 環境変数 (secret、`.env` 参照)

### 主要テーブル

```
users (id: UUID PK, email: unique, created_at, ...)
sessions (id: UUID PK, user_id: FK, token_hash, expires_at)
{{RESOURCE}} (...)
```

> 全 schema: `{{SCHEMA_PATH}}` (Prisma / Atlas / migration files)

## External Services

| Service | 用途 | Secret Key 名 |
|---------|------|-------------|
| {{AUTH_PROVIDER}} | 認証 | `AUTH_*` |
| {{PAYMENT_PROVIDER}} | 決済 | `{{PAYMENT_PREFIX}}_*` |
| {{EMAIL_PROVIDER}} | メール送信 | `{{EMAIL_PREFIX}}_*` |
| {{ANALYTICS_PROVIDER}} | アナリティクス | `{{ANALYTICS_PREFIX}}_*` |

## Environment Variables (必須)

```
# 必須 — 値はすべて `<REPLACE>` placeholder。実値は secret manager で配信
DATABASE_URL=<REPLACE: postgres connection URL>
{{AUTH_PROVIDER}}_SECRET=<REPLACE>          # 例: FIREBASE_SERVICE_ACCOUNT_JSON / CLERK_SECRET_KEY / AUTH0_CLIENT_SECRET
{{PAYMENT_PROVIDER}}_SECRET=<REPLACE>        # 例: STRIPE_SECRET_KEY

# オプション
LOG_LEVEL=info
```

> `{{AUTH_PROVIDER}}` / `{{PAYMENT_PROVIDER}}` は SDK/サービスごとに実際の env 変数名が違う (Firebase / Clerk / Auth0 / Stripe 等)。variant ファイルを参照するか、採用サービスの公式 docs で正しい変数名に置換する。

> コピー元: `.env.example`
> セット方法: {{DEPLOY_ENV_MECHANISM}} (AWS Secrets Manager / GCP Secret Manager / Vercel Env / 等)

## Directory Conventions

```
{{REPO_ROOT}}/
├── {{FRONTEND_DIR}}/      (Frontend — {{FE_OWNER}})
├── {{BACKEND_DIR}}/       (Backend — {{BE_OWNER}})
├── {{INFRA_DIR}}/         (Infra / IaC — {{INFRA_OWNER}})
├── {{DB_MIGRATIONS_DIR}}/ (DB migrations — {{DB_OWNER}})
├── docs/                  (facts.md, decisions/, zones/, security/)
└── .github/               (CODEOWNERS, workflows)
```

## Release Cadence

- 本番 deploy: {{RELEASE_FREQUENCY}}
- Feature freeze: {{FREEZE_POLICY}}
- Hotfix 手順: `docs/runbooks/hotfix.md` を参照 (存在する場合)

## Update Rules

- **値の変更は diff が見えるように**: 旧値を取り消し線ではなくコメントで残す
- **大きな構造変更**: ADR を起票してから facts.md を更新
- **secret 値自体はここに書かない**: 変数名のみ

---

**Last Updated**: {{DATE}} / **By**: {{UPDATER}}
