---
title: コンテキストエンジニアリング
topics: [claude-code, memory]
sources: [2026-03-24-ace-agentic-context-engineering-analysis.md, 2026-03-19-important-if-conditional-tags-analysis.md, 2026-03-25-context-and-impact-analysis.md, 2026-03-18-evaluating-agentsmd-analysis.md]
updated: 2026-04-04
---

# コンテキストエンジニアリング

## 概要

コンテキストエンジニアリングとは、LLM に渡す情報（system prompt・指示・メモリ）の構造・配置・更新手法を設計する技術領域である。ACE 論文（ICLR 2026）は、コンテキストをモノリシックなテキストとして一括書き換えするアプローチが「Context Collapse」（18,282 tokens が 122 tokens に崩壊してベースラインを下回る）を引き起こすことを示した。一方、AGENTS.md の実証評価（ETH Zurich）は、LLM が生成したコンテキストファイルは性能を -0.5〜-2% 低下させるのに対し、人間が記述した指示は +4% の改善をもたらすことを明らかにしており、コンテキストの質と構造が定量的な性能差を生む。

## 主要な知見

- **Brevity Bias の危険性**: コンテキスト最適化手法がドメイン固有の戦略やエッジケースを「簡潔さ」のために削ぎ落とす問題。ACE はインクリメンタルデルタ更新でこれを回避する
- **Incremental Delta Updates**: コンテキストを bullet 単位で管理し、helpfulness/harmfulness カウンタ付きの一意IDで追跡。全体リライトではなく差分更新で Context Collapse を防ぐ
- **`<important if>` 条件タグ**: 条件が現在のタスクにマッチする場合のみ Claude がそのセクションを重視するタグ。ファイルが長くなるほど個別セクションが「任意」扱いされる問題への対処
- **指示バジェット**: 約 150〜200 指示で遵守率が均一に劣化する。system prompt で既に約 50 消費済みのため実質的な余裕は限られる
- **hooks は deterministic、CLAUDE.md は advisory**: 確実に実行すべきルールは hook 化すべきであり、CLAUDE.md は判断ガイダンスとして機能する
- **5層コンテキスト収集**: L0（永続メモリ）→ L1（Grep/Glob）→ L2a（コールグラフ）→ L2b（Wikiliink グラフ）→ L3（セマンティック検索）の段階的収集が盲目的コード変更を防ぐ
- **Temporal Decay**: `exp(-0.1 × days)` でコンテキストの鮮度を自動管理（7日で 49.7%、30日で 5% に減衰）
- **コードベース概要は無効**: AGENTS.md にファイルツリーを含めても関連ファイルへの到達ステップ数に有意差がない（ETH Zurich 実証）
- **既存ドキュメントとの冗長排除**: docs が存在する場合、LLM 生成 CLAUDE.md は開発者記述を -2.7% 下回る。Documentation = Infrastructure 原則が重要

## 実践的な適用

dotfiles の CLAUDE.md は `<important if>` 条件タグを 6 セクションに適用し、関連タスクのときのみ該当指示が活性化する設計になっている。Progressive Disclosure（CLAUDE.md → references/ → rules/）でコンテキスト密度を制御し、詳細は分離ファイルに委譲する。hook 体系（completion-gate、golden-check など）が deterministic なルールを担い、CLAUDE.md は advisory な指示のみを持つ明確な役割分担がある。ACE の Incremental Delta Updates に相当する実装として、メモリファイルを bullet 単位で管理し、MEMORY.md を要約＋パス参照のみに保つ方針を採っている。Temporal Decay は現在 Gap として認識されており、手動での「古い→削除」からスコアベースの自動減衰への移行が課題である。

## 関連概念

- [agent-memory](agent-memory.md) — エージェントのメモリ層とコンテキストの永続化
- [context-management](context-management.md) — コンテキスト圧縮とウィンドウ管理
- [claude-code-architecture](claude-code-architecture.md) — Claude Code のシステム構造とコンテキストフロー

## ソース

- [ACE: Agentic Context Engineering Analysis](../../research/2026-03-24-ace-agentic-context-engineering-analysis.md) — ICLR 2026 採録。Brevity Bias・Context Collapse の定義とインクリメンタルデルタ更新手法
- [Important-If Conditional Tags Analysis](../../research/2026-03-19-important-if-conditional-tags-analysis.md) — `<important if>` タグによる指示遵守率向上と指示バジェットの制約
- [Context and Impact Analysis](../../research/2026-03-25-context-and-impact-analysis.md) — 5層コンテキスト収集・Temporal Decay・Ensemble Quality Gate を含む包括的パイプライン
- [Evaluating AGENTS.md Analysis](../../research/2026-03-18-evaluating-agentsmd-analysis.md) — ETH Zurich による大規模実証。LLM 生成 vs 人間記述のコンテキストファイル性能比較
- [Harnesses Are Everything (2026-04)](../../research/2026-04-19-harness-everything-absorb-analysis.md) — **instruction budget の真の総量** = CLAUDE.md 本文 + hook 注入 + description + MCP tool 定義。Stanford "Lost in the Middle" 研究が裏付け: 2000 トークン超で指示遵守率 20-30% 低下。**Progressive Disclosure** (lean .md → references → rules) で常時露出を最小化し、dumb zone を回避する。
