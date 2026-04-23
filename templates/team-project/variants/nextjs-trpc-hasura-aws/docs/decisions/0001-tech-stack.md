# ADR-0001: Tech Stack Selection (Next.js + tRPC + Hasura + AWS)

- **Status**: Accepted
- **Date**: {{YYYY-MM-DD}}
- **Deciders**: @{{DECIDER_1}}, @{{DECIDER_2}}

## Context

- 小〜中規模の SaaS (数千 MAU 想定、急成長の可能性あり)
- 少人数 (1-3 名) での開発 → boilerplate 削減と型安全の両立が必須
- 既存 AWS アカウント資産を活用
- Backend を独立 service に分けるほど複雑ではない (モノリシック Next.js が適切)

## Decision

以下のスタックを採用する:

- **Frontend + API Layer**: Next.js 14 (App Router) + tRPC v11 (Route Handlers 上)
- **Data Layer**: Hasura GraphQL Engine (PostgreSQL 直結、Role-Based Permission)
- **DB**: PostgreSQL 15 (Amazon RDS)
- **Infra**: AWS (ECS Fargate for Hasura, RDS, S3) + Vercel (Next.js)
- **Auth**: Clerk (JWT を Hasura に渡して RLS)

### tRPC と Hasura の役割分担

- **Hasura**: CRUD の 80% (list/get/insert/update/delete + Row-Level Security)
- **tRPC**: ビジネスロジック・Stripe 連携・外部 API 呼び出し・Webhook 処理

## Rationale

- **tRPC**: TS-only で型共有が zero-config。gRPC より軽量
- **Hasura**: CRUD の boilerplate を自動生成、権限を declarative に管理。少人数でも API を爆速構築
- **併用**: 単純 CRUD は Hasura、複雑ロジックは tRPC。両者を merge せず独立運用 (tRPC から Hasura を呼ぶことはしない、責務を分離)
- **Clerk**: 認証 UI / メール認証 / MFA を 0 から書かずに済む
- **Vercel + AWS**: Next.js は Vercel の SSR 最適化を享受、Hasura は AWS で VPC 内 RDS に直結

## Alternatives Considered

| 選択肢 | Pros | Cons | 却下理由 |
|-------|------|------|---------|
| Prisma (Hasura なし) | TS-only でスタック統一 | 権限統治が難しい、RLS を自前で | Hasura の declarative 権限が魅力 |
| Supabase (Hasura 代替) | 認証・ストレージ込み | ベンダーロックイン、既存 AWS 資産と並行運用が煩雑 | 既存 AWS を活かしたい |
| NestJS + PostgreSQL | 構造化されたバックエンド | Next.js + tRPC より boilerplate 多い | 小人数には重い |
| Firebase Firestore | 速い構築 | NoSQL で後から relational 要件が辛い | PostgreSQL を選びたい |
| Go backend (Connect RPC) | 性能・並行性 | 少人数では TS-only の方が開発速い | 本業 variant と差別化 |

## Consequences

- **Positive**:
  - CRUD API を書く手間が激減 (Hasura 自動生成)
  - tRPC で FE/BE 型共有が無料
  - Vercel + Clerk + Stripe の組み合わせで「書かない」を最大化
- **Negative**:
  - 2 つの API 層 (tRPC + Hasura) を維持する複雑性
  - Hasura の権限設定を間違えるとデータ漏洩 → 慎重な review 必要
  - ECS Fargate の cold start (5-10 秒) で Hasura 起動に時間
- **Mitigation**:
  - Hasura permission は metadata migration + CI で diff 検出
  - ECS minimum task = 1 で常時稼働 (cold start 回避、cost 受容)
  - tRPC と Hasura の使い分けを CLAUDE.md で明文化

## Validation / Exit Criteria

- **成功指標**:
  - CRUD API 追加が Hasura metadata 編集のみで完了
  - tRPC endpoint 追加の工数 30 分以内 (型共有・認証ミドルウェアが揃っている)
- **撤退条件**:
  - Hasura の権限複雑性が手に負えなくなる → Prisma + 自前 API に移行検討
  - ECS cost が Cloud Run / Cloud Functions の 2x を超える → PaaS 移行検討

## Related

- tRPC: https://trpc.io
- Hasura: https://hasura.io/docs
- Clerk: https://clerk.com/docs
- Hasura JWT with Clerk: https://clerk.com/docs/integrations/databases/hasura

---

**Update History**:
- {{YYYY-MM-DD}}: Accepted (initial stack selection)
