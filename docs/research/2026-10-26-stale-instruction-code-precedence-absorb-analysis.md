---
title: "Stale instruction files vs existing code (arXiv:2610.30571)"
date: 2026-10-26
source:
  - https://arxiv.org/html/2610.30571
  - https://x.com/ai_database/status/2114184481951330365
status: integrated
family: agentic-instruction-following
adopted: 1
---

# Stale instruction × code precedence — 採否

## Source Summary

**主張**: コーディングエージェントは CLAUDE.md / AGENTS.md が既存コードと食い違っても、指示ファイル側に従う。ユーザー指示ファイルに「ドキュメントと既存コードが食い違ったらコードに従い、食い違いを最終返答で挙げる」1文を足すと、コード準拠へ大きく寄る。

**論文で確認した数値**（arXiv HTML abstract / §5）:
- 文なし: 選択肢の 90.1% が古い指示ファイルに一致、既存コード一致は 4.2%
- 文あり: 既存コード一致が 4.2% → 91.4%
- テスト通過率: 89.4% → 100%（文ありでは全 160 run 通過）

**紹介投稿**: @ai_database (2026-10-25) が同趣旨の日本語訳と論文要旨を紹介。

## 既存との照合

| 既存 | 判定 |
|---|---|
| instruction DRY（指示同士の重複・矛盾の一本化） | 別論点。docs↔code 優先は未記載 |
| `convention-pinning.md`（既存コードから慣習を読む） | 近接だが、指示ファイルとの食い違い時の優先と最終報告義務はない |

→ 同趣旨の1文は未存在。**採用 1**。

## 採用

ユーザー承認（2026-10-26 10:44 JST、提案1）どおり、次の2箇所（CLAUDE.md は生成元経由）に1文を追加した。

1. `.config/claude/templates/claude-md/principles.md` → `build-claude.sh` で `.config/claude/CLAUDE.md` の instruction DRY 項へ反映
2. `.codex/AGENTS.md` Editing Defaults の対応行

追加文: 「ドキュメント（指示ファイル）と既存コードが食い違ったら既存コードに従い、見つけた食い違いを最後の報告で挙げる」
