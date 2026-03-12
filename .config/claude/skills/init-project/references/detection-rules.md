# 検出ルール

init-project スキルの Phase 1（Detect）で使用するプロジェクト分析・規模判定ロジック。

---

## シグナルテーブル

| シグナル | 検出コマンド | S (1pt) | M (2pt) | L (3pt) | 重み |
|---|---|---|---|---|---|
| ファイル数 | `find . -type f -not -path './.git/*' -not -path './node_modules/*' -not -path './vendor/*' -not -path './.venv/*' \| wc -l` | < 20 | 20-200 | 200+ | 1.0 |
| 言語数 | `ls -1 package.json pyproject.toml go.mod Cargo.toml Gemfile mix.exs 2>/dev/null \| wc -l` | 1 | 2 | 3+ | 1.5 |
| CI/CD | `ls -1 .github/workflows/*.yml .gitlab-ci.yml Jenkinsfile 2>/dev/null \| wc -l` | 0 | 1 | 2+ | 2.0 |
| Contributors | `git shortlog -sn --no-merges 2>/dev/null \| wc -l` | 1 | 2-5 | 6+ | 1.5 |
| フレームワーク | package.json / go.mod / Cargo.toml 内の依存検出 | なし or 1 | 1-2 | 3+ | 1.0 |
| テスト | config ファイル + テストファイル数 | なし | あり | あり+E2E | 1.5 |
| docs/ | `ls -d docs/ 2>/dev/null` | なし | 部分的 | 充実 | 0.5 |
| リスキーモジュール | find でパターンマッチ | 0 | 1 | 2+ | 2.0 |

## スコアリングロジック

```
score = Σ(signal_score × weight) / Σ(weight)

閾値:
  score ≤ 1.5  → S（Minimal）
  1.5 < score ≤ 2.3 → M（Standard）
  score > 2.3  → L（Production）
```

### 強制ルール（閾値を上書き）

- CI あり **AND** リスキーモジュール 2+ → **L に引き上げ**
- ファイル数 200+ **AND** テストあり → **最低 M**
- Contributors 6+ → **最低 M**

---

## リスキーモジュール検出

| パターン | ドメイン |
|---|---|
| `auth/`, `authentication/`, `authorization/` | 認証・認可 |
| `billing/`, `payment/`, `stripe/` | 課金・決済 |
| `migration/`, `migrations/` | DB マイグレーション |
| `infra/`, `infrastructure/`, `terraform/`, `pulumi/` | インフラ |
| `security/`, `crypto/` | セキュリティ |
| `persistence/`, `database/`, `db/` | データ永続化 |

```bash
find . -maxdepth 3 -type d \( \
  -name 'auth' -o -name 'authentication' -o -name 'authorization' \
  -o -name 'billing' -o -name 'payment' -o -name 'stripe' \
  -o -name 'migration' -o -name 'migrations' \
  -o -name 'infra' -o -name 'infrastructure' -o -name 'terraform' -o -name 'pulumi' \
  -o -name 'security' -o -name 'crypto' \
  -o -name 'persistence' -o -name 'database' -o -name 'db' \
\) -not -path './.git/*' -not -path './node_modules/*' -not -path './vendor/*' -not -path './.venv/*'
```

---

## 既存 Claude Code 構造の検出

| チェック | コマンド | 意味 |
|---|---|---|
| CLAUDE.md | `test -f CLAUDE.md` | 初期化済み |
| .claude/ | `test -d .claude` | 設定あり |
| .claudeignore | `test -f .claudeignore` | 部分セットアップ |
| settings.json | `test -f .claude/settings.json` | hooks 設定あり |
| skills/ | `ls .claude/skills/ 2>/dev/null` | スキルあり |
| rules/ | `ls .claude/rules/ 2>/dev/null` | ルールあり |

既存構造が検出された場合 → `--upgrade` フローに切り替え提案。

---

## 判定結果フォーマット

```
🔍 プロジェクト分析結果:
  - 言語: TypeScript, Go
  - フレームワーク: Next.js 15, Echo
  - CI: GitHub Actions (3 workflows)
  - テスト: Vitest, Go testing, Playwright
  - Contributors: 4
  - リスキーモジュール: src/auth/, src/billing/
  - スコア: 2.6 / 3.0

📊 推奨レベル: L（Production）
   理由: CI + リスキーモジュール 2件（強制ルール適用）

(1) L で進める
(2) M に下げる（hooks/agents/background agents を省略）
(3) S に下げる（CLAUDE.md + .claudeignore のみ）
(4) --dry-run で生成物を確認
```
