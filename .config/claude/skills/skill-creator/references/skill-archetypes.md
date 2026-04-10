# Skill Archetypes — 新スキル作成時の型選択ガイド

## 判断フロー

```
スキルの主な役割は？
├─ 操作をブロック/確認する → Guard
├─ 複数ステップを順序実行する → Pipeline
├─ ファイルを生成する → Generator
├─ 知識を提供し判断を支援する → Knowledge Base
└─ 外部CLIツールをラップする → Tool Wrapper
```

## Archetype 定義

### 1. Guard（ガード型）
**役割**: 操作インターセプト、安全担保
**構造**: SKILL.md のみ
**例**: freeze, careful, verification-before-completion

### 2. Pipeline（パイプライン型）
**役割**: 複数フェーズの順序実行 + ゲート
**必須**: templates/ (出力フォーマット)
**推奨**: references/ (フェーズ別ガイド)
**任意**: scripts/ (自動化)
**例**: review, research, improve, absorb

### 3. Generator（ジェネレータ型）
**役割**: 構造化ファイル生成
**必須**: templates/ (出力テンプレート)
**任意**: scripts/ (データ収集), data/ (ドメインコンテンツ)
**例**: daily-report, eureka, spec, digest

### 4. Knowledge Base（知識ベース型）
**役割**: ドメイン知識の構造化、意思決定支援
**必須**: references/ (パターンカタログ)
**任意**: data/ (判断マトリクス), scripts/ (検証ツール)
**例**: senior-frontend, edge-case-analysis, react-best-practices

### 5. Tool Wrapper（ツールラッパー型）
**役割**: 外部CLIツールの最適な使い方を教える
**推奨**: scripts/ (ヘルパー), references/ (CLIリファレンス)
**任意**: examples/ (実行可能サンプル)
**例**: codex, gemini, webapp-testing

#### 5a. Tool Wrapper の派生型: Product Verification

「対象 repo/product 固有の acceptance oracle を持つ検証スキル」は、汎用 Tool Wrapper とは別物として扱う。
Anthropic "Skills for Claude Code" (2026-04) が「Product Verification スキルは 1 週間エンジニア専任の価値」と評価する型に相当。

**役割**: 単なる CLI 起動ではなく、**その repo でしか成立しない合否基準**を実行可能な形で提供する

**Tool Wrapper との違い:**

| 次元 | 汎用 Tool Wrapper | Product Verification 派生型 |
|------|------------------|---------------------------|
| 対象 | あらゆる repo で再利用可能 | 1 つの repo/product に特化 |
| 合否基準 | ユーザー判断 | スキル内に明示（DOM selector, URL, レスポンス contract 等） |
| エビデンス | なし（実行ログのみ） | 必須（screenshot, HAR, log diff, API snapshot） |
| メンテ頻度 | ツール更新時 | product 変更のたび |

**必須要素:**

- `scripts/run.sh` — エントリポイント。1コマンドで verify が走ること
- `scripts/assertions/` — repo 固有の oracle（例: `checkout-flow.spec.ts`, `signup-api.http`）
- `evidence/` — スクリーンショット・HAR・レスポンスログの出力先（`.gitignore` で実体は除外、テンプレのみ git 管理）
- `references/product-invariants.md` — 「この product で絶対に変わらない契約」を明文化（例: 「/checkout は必ず 200 を返す」「ログイン後の /dashboard に 3 秒以内に到達」）
- **Credential 分離**: seed user の認証情報・API key は `config.json` / `.spec.ts` / `.http` に**絶対に hardcode しない**。`~/.config/{skill}/secrets.env` or keychain に格納し、oracle からは `process.env.SEED_USER_TOKEN` のように env 参照のみ。配置は skill-writing-principles.md の Setup Config 規約に従う
- **Evidence sanitize**: screenshot/HAR は本番 cookie・Authorization header・PII を含むため、保存前に scrub 関数を通す。HAR は `--exclude-headers=authorization,cookie,set-cookie` 相当で sanitize、screenshot は PII マスク関数を通してから書き出す
- **Retention policy**: `evidence/` は直近 7 日のみ保持。`scripts/run.sh` 末尾で `find evidence -mtime +7 -delete` 相当のローテーションを必ず組み込む

**スキル内に書くべきこと:**

1. **Scope**: どの repo / どの環境を対象にしているか明示
2. **Preconditions**: 起動前に必要な state（seed user、DB snapshot、env var）
3. **Oracle**: 合否を判定する具体的基準（コードで書ける形）
4. **Evidence collection**: 失敗時のスクショ/ログ保存場所
5. **Rollback hint**: 失敗したらどの layer（UI / API / DB）を疑うか

**例 (想定):**

```
.config/claude/skills/verify-checkout/
├── SKILL.md                        # scope, preconditions, rollback hint
├── config.json                     # target_env, seed_user 等（Setup Config パターン）
├── scripts/
│   ├── run.sh                      # entrypoint
│   └── assertions/
│       ├── checkout-flow.spec.ts   # Playwright
│       └── payment-api.http        # API contract
├── references/
│   └── product-invariants.md       # "checkout は必ず 200 を返す"
└── evidence/
    └── .gitkeep                    # 実体は gitignore
```

**NG パターン:**

- 汎用 `webapp-testing` / `validate` を Product Verification と同一視する（別物）
- repo 固有 oracle をスキル外（プロジェクト test dir）に置く → スキルとして再現不能になる
- evidence を git 管理する（容量爆発）
- **1 つの Verification スキルで複数 product をカバーする**（スキルを分割せよ）

**いつ作るか:**

- 同じ repo の E2E 検証を 2 回以上手動で再現している
- 「この product のこの flow は壊れちゃいけない」という明確な契約がある
- 失敗時に evidence（スクショ/HAR）が次のデバッグで必要

## 新スキル作成時の手順

1. 上記判断フローで archetype を選択
2. archetype の「必須」ディレクトリを作成
3. SKILL.md に `## Skill Assets` セクションで参照ポインタを記載
4. 「任意」は実際に必要になってから追加 (YAGNI)
5. Tool Wrapper を選んだ場合、汎用 wrapper か Product Verification 派生かを判断し、後者なら 5a の必須要素を必ず揃える
