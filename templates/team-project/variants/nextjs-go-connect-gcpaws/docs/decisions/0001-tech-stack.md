# ADR-0001: Tech Stack Selection (Next.js + Go + Connect RPC + GCP/AWS)

- **Status**: Accepted
- **Date**: {{YYYY-MM-DD}}
- **Deciders**: @{{DECIDER_1}}, @{{DECIDER_2}}

## Context

- 数万〜数十万 MAU を想定する SaaS
- 型安全な API 契約とコード生成パイプラインを重視
- 既存チームが TypeScript + Go に習熟
- GCP が主 (チームの運用経験)、S3 / CDN は AWS を継続利用

## Decision

以下のスタックを採用する:

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind
- **Backend**: Go 1.22 + Connect RPC (buf ecosystem)
- **DB**: PostgreSQL 15 on Cloud SQL (GCP)
- **API Contract**: Protocol Buffers (`proto/` + buf.yaml) → TypeScript / Go SDK 自動生成
- **Primary Cloud**: GCP (Cloud Run, Cloud SQL, Secret Manager)
- **CDN / Storage**: AWS (S3, CloudFront, Route53)

## Rationale

- **Connect RPC**: gRPC-Web の代替。HTTP/1.1 互換で debugging が楽、ブラウザから直接叩ける。buf の linting/breaking change 検出が強力
- **Go**: Cloud Run の cold start が速い、並行処理が書きやすい、チームが書ける
- **Next.js App Router**: Server Components で SSR 性能確保、Streaming 対応
- **Cloud Run**: K8s 管理コストを払わず autoscaling を得る
- **GCP + AWS 併用**: 既存資産 (S3 バケット・Route53 ゾーン) を活かしつつ、新規は GCP に寄せる

## Alternatives Considered

| 選択肢 | Pros | Cons | 却下理由 |
|-------|------|------|---------|
| gRPC (pure) | 成熟 | ブラウザから直接叩くのが面倒 (gRPC-Web 必要) | Connect RPC の方が DX が良い |
| GraphQL (Apollo) | 柔軟 | N+1 問題、スキーマ統治が難しい | proto の breaking change 検出の方が手堅い |
| tRPC | TS-only で型共有が楽 | Go backend と混在不可 | backend を Go にする前提で不可 |
| Python (FastAPI) | 学習コスト低 | 並行性能・cold start で Go に劣る | パフォーマンス優先 |
| AWS Fargate / ECS | 既存 AWS 資産活用 | GCP Cloud Run より cold start 遅い + 運用複雑 | Cloud Run の操作性 |

## Consequences

- **Positive**:
  - API 契約が proto で一元化され、FE/BE のズレが起きにくい
  - Cloud Run で 0 台までスケールダウン → コスト効率
  - 型生成パイプラインで boilerplate が減る
- **Negative**:
  - buf + protoc のセットアップが初学者には敷居高い
  - GCP + AWS 両方の請求・権限管理コスト
  - Connect RPC はエコシステムが gRPC より小さい (ライブラリ選択肢が少ない)
- **Mitigation**:
  - buf CLI のインストール手順を `docs/runbooks/dev-setup.md` に明記
  - Terraform state を 2 つ分ける (gcp/, aws/) + Makefile で抽象化
  - Connect RPC の不足分は `net/http` 直書きで補う (interceptor 等)

## Validation / Exit Criteria

- **成功指標**:
  - API 追加時の FE/BE 連携工数が proto 変更 → 自動生成で済む
  - Cloud Run の cold start p95 < 500ms
- **撤退条件**:
  - Connect RPC ライブラリが 12 ヶ月以上 stale になる → gRPC or REST に検討
  - GCP の cost が想定の 2x → アーキテクチャ見直し ADR

## Related

- buf: https://buf.build
- Connect RPC: https://connectrpc.com
- Next.js App Router: https://nextjs.org/docs/app

---

**Update History**:
- {{YYYY-MM-DD}}: Accepted (initial stack selection)
