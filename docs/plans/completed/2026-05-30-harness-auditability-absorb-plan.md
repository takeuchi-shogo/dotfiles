---
title: harness auditability 強化 (claude-code-harness absorb)
date: 2026-05-30
status: completed
completed: 2026-05-30
source: docs/research/2026-05-30-claude-code-harness-absorb-analysis.md
size: L (4 tasks: S + S-M + S + M)
theme: 「codegen ではなく auditability」— 既存状態を legible にする
---

> **完了 (2026-05-30, /rpi)**: 全 4 タスク実装・検証済。Codex Review Gate (codex-reviewer + code-reviewer) 共に PASS (ブロッカー 0)。
> 実装: `.config/claude/references/{retired-concepts,hook-failure-policy,deny-rules-catalog}.md` 新規 + `scripts/lifecycle/doctor-stale.sh` 新規 + `doc-garden-check.py` 退役検出 + `Taskfile.yml` `doctor:stale`。
> Research 補正: 正本のパス `scripts/lifecycle/doc-garden-check.py` は実際 `.config/claude/scripts/lifecycle/`。`/improve` の「廃止 vs 実体現存」矛盾を確認 → registry に status=曖昧 で記録。確定退役 seed は live 参照 0 の `gleam-practice`/`moonbit-practice` (2026-05-10 削除) を採用。

# Plan: harness auditability 強化

claude-code-harness (競合プラグイン) の設計を鏡に、Phase 2.5 (Codex+Gemini) で Gap が
「config codegen ではなく auditability」に収束した 4 件を実装する。#2 codegen は over-engineering で drop 済。

## Task 1 (#6, P1/S): retired-concepts registry + doc-garden-check 連携

- **新規**: `.config/claude/references/retired-concepts.md`
  - 列: `id / retired-date / replacement / rationale / status (確定/曖昧)`
  - 初期エントリ: `/improve` command (2026-05-03 retire、ただし improve skill 存在の曖昧性を status=曖昧 で記録)、autoevolve-core legacy 等
- **Edit**: `scripts/lifecycle/doc-garden-check.py`
  - 新規/変更ファイル中の retired-concepts.md 語彙への参照を検出して warn (Negative Constraints パターン)
  - fail_closed=False (advisory) で既存 doc-garden の挙動を踏襲
- **受入**: 退役語彙を含むファイルを変更すると warn が出る。既存 historical doc (docs/research/*) は除外対象に。

## Task 2 (#5, P2/S-M): doctor:stale inventory モード

- **Edit**: `Taskfile.yml` に `doctor:stale` task 追加 (doctor の defer に組み込み or 独立)
- **新規 (必要なら)**: `scripts/lifecycle/doctor-stale.sh`
  - inventory 対象: `~/.claude/plugins/data/codex-openai-codex/state/*` の orphaned job、stale cache、古い backup path
  - **削除しない**。--report のみ。件数 + パス一覧を出力
- **受入**: `task doctor:stale` が orphaned state を列挙し、削除は一切しない。

## Task 3 (#4, P3/S): fail-open/closed 一覧 + 選択原則

- **新規**: `.config/claude/references/hook-failure-policy.md`
  - `hook_utils.run_hook(fail_closed=...)` を呼ぶ全 hook を grep でカタログ化 (hook 名 / fail_closed 値 / 分類)
  - 選択原則を codify: 「security/policy hook = fail_closed=True、advisory hook = fail_closed=False」
- **受入**: どの hook が fail-open かが 1 ファイルで分かる。code と一覧の不整合がない。

## Task 4 (#3, P4/M): deny rules カタログ

- **新規**: `.config/claude/references/deny-rules-catalog.md`
  - settings.json の deny 102 / ask 0 / allow 71 を `id / tier / pattern / rationale` でカタログ化
  - settings.json 自体は single source として不変。本ファイルは auditability 用の読み物
- **受入**: deny rule の意図が tier 別に追える。settings.json とパターン数が一致。

## 非実装 (記録のみ)

- #2 config codegen: over-engineering (projen/KCL 系の team-scale 価値、単一ユーザーに deadlock リスク)
- #7 release evidence: versioned plugin を ship しない個人 repo に N/A
- #1 Go hook runtime: Python 編集容易性が個人 repo では勝つ (N/A)

## 検証

- 各タスク後: `task validate-configs`, `task validate-symlinks`
- Task 1/3: doc-garden-check の既存テストが通ること
- Codex Review Gate (S 規模以上の変更)
