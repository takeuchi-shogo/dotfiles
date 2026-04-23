---
status: reference
last_reviewed: 2026-04-23
---

# Doc Status Schema

`docs/research/`, `docs/plans/`, `.config/claude/references/` の全 `.md` ファイルに付与する frontmatter スキーマ。

**目的**: search-result sprawl の抑制。agent が grep/semantic search で拾うドキュメントを `active | reference | archive` で分類し、古い or 棚上げされた知見を静かに足を引っ張らせない。

## Frontmatter スキーマ

```yaml
---
status: active | reference | archive   # 必須
last_reviewed: YYYY-MM-DD                # 必須
# 以下は既存と互換の任意フィールド
source: "URL または記事タイトル"         # research のみ
date: YYYY-MM-DD                         # 作成日（既存）
analysis: "path/to/related.md"           # plans で analysis との紐付け
superseded_by: "path/to/new.md"          # archive 時のみ
---
```

## ステータス定義

| status | 意味 | 運用 |
|---|---|---|
| `active` | 今も運用されている方針・現行プラン | 通常参照対象 |
| `reference` | 骨子・定義・長期参照資料（陳腐化しない） | 通常参照対象、更新は低頻度 |
| `archive` | 過去に統合済み／方針変更で無効化／完了済み | 検索から除外推奨、歴史的参照のみ |

## 判定ルール（`doc-status-audit.py --fix` 自動推定）

優先順位で上から判定:

1. **archive**: `docs/plans/archive/` 配下、または `docs/plans/done/` 配下
2. **active**: `MEMORY.md`, `CLAUDE.md`, `~/.claude/CLAUDE.md`, `_index.md` から stem マッチで参照されている
3. **reference**: 最終更新が 90 日超 + 参照あり（active 条件不一致）、または references/ 配下の骨子 doc
4. **archive**: 最終更新が 90 日超 + 参照なし
5. **active**: 最終更新が 90 日以内（フォールバック）

誤判定時は手動で frontmatter を修正可能。スクリプトは **提案のみ**（`--fix` でも frontmatter への追加のみ、他フィールド保持）。

## Pruning と archive 連携

- `archive` 付与から 30 日観察 → `/improve` Garden で削除候補として提示
- `docs/playbooks/stale-doc-retirement.md` の 6-step に従って移行
- `references/improve-policy.md` Rule 51/52 の dead-weight-scan と合流

## 既存 frontmatter との互換

既に `source:`, `date:`, `analysis:` 等がある場合は **追加のみ** 行う。`--fix` は:
- frontmatter なし → 新規付与
- frontmatter あり + status 未設定 → status + last_reviewed のみ追加
- frontmatter あり + status あり → 何もしない（既存尊重）

## 運用頻度

- 月次 `/improve` 実行時に `doc-status-audit.py --dry-run` を回して新規未設定ファイルを検出
- 新規 `docs/research/YYYY-MM-DD-*.md` 作成時は手動で `status: active` + `last_reviewed` を付与
