# Team Project Base Template

新規 team project に Claude Code harness を導入するための最小構成。
dotfiles 個人 harness の蓄積から、team 運用に必要な要素だけ抽出した。

## 構成

```
base/
├── CLAUDE.md.tpl                          — team 向け Claude Code 契約
├── docs/
│   ├── facts.md.tpl                       — API / DB / 環境の事実 index
│   ├── zones/OWNERSHIP.md.tpl             — Zone 所有権マトリクス
│   ├── decisions/0000-template.md         — ADR テンプレート
│   └── security/auth-payment-policy.md.tpl — 認証・決済の 2-sign-off policy
├── .github/CODEOWNERS.tpl                  — Zone ownership を GitHub 機構化
└── README.md                               — 本ファイル
```

## Quick Start

新規 team project に適用する場合:

```bash
# 1. コピー
cp -R /path/to/dotfiles/templates/team-project/base/* /path/to/your-project/
cd /path/to/your-project/

# 2. .tpl 拡張子を外す
find . -name '*.tpl' -exec sh -c 'mv "$0" "${0%.tpl}"' {} \;

# 3. placeholder 置換 (ripgrep + sd / sed 等で)
rg -l '\{\{PROJECT_NAME\}\}' | xargs sd '\{\{PROJECT_NAME\}\}' 'MyApp'
rg -l '\{\{FE_OWNER_GH\}\}'  | xargs sd '\{\{FE_OWNER_GH\}\}'  'alice'
# ... 以下続く
```

既存 project に差分適用する場合: 親ディレクトリの `../APPLY.md` を参照。

## Placeholder 一覧

主要なもの (詳細は各ファイルを grep):

| Placeholder | 例 |
|-------------|------|
| `{{PROJECT_NAME}}` | MyApp |
| `{{TECH_STACK}}` | Next.js 14 + Go 1.22 + Connect RPC + PostgreSQL |
| `{{FE_OWNER}}` / `{{FE_OWNER_GH}}` | Alice / @alice |
| `{{FE_PATHS}}` | `/frontend/**` or `/apps/web/**` |
| `{{FE_VERIFY_CMD}}` | `pnpm typecheck && pnpm test` |
| `{{BE_OWNER}}` / `{{BE_OWNER_GH}}` | Bob / @bob |
| `{{BE_PATHS}}` | `/backend/**` or `/apps/api/**` |
| `{{BE_VERIFY_CMD}}` | `go test ./...` |
| `{{DB_MIGRATIONS_DIR}}` | `backend/migrations/` |
| `{{AUTH_PATHS}}` | `/backend/auth/**`, `/frontend/auth/**` |
| `{{PAYMENT_PATHS}}` | `/backend/billing/**` |

全 placeholder を grep する方法:

```bash
rg -o '\{\{[A-Z_]+\}\}' -h . | sort -u
```

## Customization Policy

- **必須**: CLAUDE.md / OWNERSHIP.md / CODEOWNERS
- **強く推奨**: facts.md / ADR template
- **必要なら**: auth-payment-policy (認証・決済を扱う project のみ)

不要なファイルは削除して構わない。Zone も 4 個すべて使う必要はない (例: infra が別 team なら Infra zone 削除)。

## Variants (技術スタック別 concrete example)

base は placeholder のままだが、技術スタック別に具体例を埋めた variant がある:

- `../variants/nextjs-go-connect-gcpaws/` — 本業系 (Next.js + Go + Connect RPC + GCP/AWS)
- `../variants/nextjs-trpc-hasura-aws/` — 副業系 (Next.js + tRPC + Hasura + AWS)

variant を先にコピーしてから編集する方が書き始めの痛みが少ない。

## 関連

- 個人 harness と team 仕組みの翻訳マップ: `~/.claude/references/team-harness-patterns.md`
- 初期化自動化: `/init-project --team` skill
- このテンプレートの設計根拠: `docs/plans/completed/2026-04-23-team-harness-template-plan.md` (dotfiles 内)
