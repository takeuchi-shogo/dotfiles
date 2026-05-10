---
status: active
last_reviewed: 2026-04-23
---

# Plans Index

`docs/plans/` 配下の active / archive 状況を一覧化する索引。
詳細な研究背景は `docs/research/_index.md` を参照。

## 運用方針

- 新規 plan は `docs/plans/active/YYYY-MM-DD-<topic>-plan.md` に作成
- 完了したら frontmatter `status` を `archive` に変更し、本索引から削除候補に
- archive 後 30 日経過観察 → `/improve` Garden で削除提案
- 詳細手順: [`docs/playbooks/stale-doc-retirement.md`](../playbooks/stale-doc-retirement.md)

## active

`docs/plans/active/` 配下の現行プラン（status: active）。新規追加時はここに 1 行追記。
実在する相対パスのみ記載すること。

| Plan | パス | 概要 |
|---|---|---|
| 2026-04-23-agents-md-absorb-plan | `active/2026-04-23-agents-md-absorb-plan.md` | AGENTS.md patterns absorb 7 タスク統合 |
| 2026-04-21-harness-pipeline-absorb-plan | `active/2026-04-21-harness-pipeline-absorb-plan.md` | Harness Pipeline (BAN article) absorb |
| 2026-04-20-karpathy-absorb-plan | `active/2026-04-20-karpathy-absorb-plan.md` | Karpathy Skills absorb |
| 2026-04-19-harness-everything-absorb-plan | `active/2026-04-19-harness-everything-absorb-plan.md` | Harnesses Are Everything absorb |
| 2026-04-19-autogenesis-integration-plan | `active/2026-04-19-autogenesis-integration-plan.md` | Autogenesis 統合 |

> 最新 10-15 件を維持。完全な一覧は `ls docs/plans/active/` で参照。

## completed (完了済み)

`docs/plans/completed/` 配下に移動された完了プラン。検索除外推奨。
`ls docs/plans/completed/` で全件参照可能。

## paused (保留)

`docs/plans/paused/` 配下。再開判断待ちの plan。

## legacy (active 外、docs/plans/ 直下)

古い plan が `docs/plans/` 直下に残存している（Obsidian/Context Design/Hermes/CREAO/Empirical Prompt Tuning 等）。`ls docs/plans/*.md` で確認可。段階的に active/completed/paused に再配置予定。

## メンテナンス

- 月次 `/improve` Garden フェーズで `doc-status-audit.py --dry-run` を実行し、status: active のプランで完了済みのものを archive へ移行提案
- 索引上限の目安: 15 件。超過時は古いものから archive へ
