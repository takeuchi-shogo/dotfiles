---
status: active
last_reviewed: 2026-04-23
---

# /init-project スキル設計

**Date**: 2026-03-12
**Status**: Approved

## コンセプト

プロジェクトを分析し、最適な Claude Code 構造を段階的に構築するオーケストレータスキル。
Pandey "Anatomy of a Claude Code Project" の5層構造を基盤に、既存ファクトリ群に委譲する薄いオーケストレーション層。

## 意思決定ログ

| 決定 | 選択 | 理由 |
|---|---|---|
| スコープ | 自己+他者、成熟度スケール | 構造は普遍。適用レベルで調整 |
| レベル分け | 3段階(S/M/L) + 自動検出 | 既存ワークフロー規模テーブルと一致 |
| アーキテクチャ | オーケストレータ（ファクトリ委譲） | GP-001 共有ユーティリティ優先、DRY |
| 名前 | `/init-project` | 高レベルの初期化を表現 |

## アーキテクチャ

```
/init-project
    │
    ├─ Phase 1: Detect (自己完結)
    │   プロジェクト分析 → 規模判定(S/M/L) → ユーザー確認
    │
    ├─ Phase 2: Generate (ファクトリ委譲)
    │   ├─ constitution-factory  → CLAUDE.md + .claudeignore
    │   ├─ context-factory       → architecture.md, ADR, Local CLAUDE.md
    │   └─ setup-background-agents → CI基盤 (L のみ)
    │
    └─ Phase 3: Verify (自己完結)
        生成物の整合性チェック + 次ステップの提案
```

## 自動検出シグナル

| シグナル | S | M | L |
|---|---|---|---|
| ファイル数 | < 20 | 20-200 | 200+ |
| 言語数 | 1 | 1-2 | 2+ |
| CI/CD 有無 | なし | あり | あり |
| チーム規模（contributors） | 1 | 2-5 | 5+ |
| フレームワーク | なし or 1 | 1-2 | 2+ |
| テストの有無 | なし | あり | あり + E2E |
| docs/ の有無 | なし | 部分的 | あり |
| リスキーモジュール数 | 0 | 0-1 | 2+ |

強制ルール: CI あり + リスキーモジュール 2+ → L に引き上げ

## レベル別出力

### S（Minimal）

```
CLAUDE.md              ← constitution-factory
.claudeignore          ← constitution-factory
```

### M（Standard）

```
CLAUDE.md              ← constitution-factory
.claudeignore          ← constitution-factory
.claude/rules/{lang}.md ← 検出言語に応じて
docs/architecture.md   ← context-factory
references/workflow-guide.md ← constitution-factory
```

### L（Production）

```
CLAUDE.md              ← constitution-factory
.claudeignore          ← constitution-factory
.claude/rules/common/{security,testing}.md
.claude/rules/{lang}.md
.claude/settings.json  ← hooks 設定
docs/architecture.md   ← context-factory
docs/decisions/001-template.md ← context-factory (ADR)
references/workflow-guide.md ← constitution-factory
src/{risky}/CLAUDE.md  ← context-factory (検出時のみ)
.github/workflows/     ← setup-background-agents
```

## リスキーモジュール検出パターン

- `auth/`, `authentication/`, `authorization/`
- `billing/`, `payment/`, `stripe/`
- `migration/`, `migrations/`
- `infra/`, `infrastructure/`, `terraform/`, `pulumi/`
- `security/`, `crypto/`
- `persistence/`, `database/`, `db/`

## 既存プロジェクト適応

1. 既存 CLAUDE.md を読み取り、5層の Gap Analysis を実行
2. 欠けている層のみ追加提案（上書きしない）
3. `--upgrade` で S→M、M→L の段階的昇格

## 検証（Phase 3）

- CLAUDE.md が 100 行以内
- .claudeignore が技術スタックと一致
- references/ 内リンクが CLAUDE.md から参照されている
- Local CLAUDE.md がモジュールの実際の内容を反映
