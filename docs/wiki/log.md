# Wiki Operations Log

> Append-only record of wiki operations. Each entry follows the format:
> `## [YYYY-MM-DD] operation | Title`
>
> Operations: `ingest` (absorb), `compile` (compile-wiki), `update` (compile-wiki update),
> `lint` (compile-wiki lint), `query` (compile-wiki query), `index` (compile-wiki index)

<!-- Parseable with: grep "^## \[" docs/wiki/log.md | tail -10 -->

## [2026-04-07] ingest | Self-Optimizing Multi-Agent Systems for Deep Research

- ソース: https://arxiv.org/abs/2604.02988 (Câmara+ 2026, ECIR Workshop)
- 判定: Gap 2個, Partial 2個, Already 2個 (強化可能), N/A 1個
- 取り込み: /research Aggregate 品質基準, improve Rule 44 カテゴリ別ルーブリック, evolve --pareto モード, Phase 4 メタプロンプト自己改善

## [2026-04-07] ingest | meta-agent: Continual Learning for Agents + The Great Convergence

- ソース: https://github.com/canvas-org/meta-agent + The Great Convergence blog
- 判定: Gap 3個, Partial 1個, Already 6個 (うち強化可能3個), N/A 1個
- 取り込み: improve-policy に Rule 40-43 追加（anti-overfit, skill化優先, per-trace critique方向性, holdout gate方向性）、Rule 20 修正（single-change デフォルト化）、continuous-learning に trace-based rule extraction パス追加

## [2026-04-07] ingest | AIエージェントのHITL評価を深化させる

- ソース: https://tech.layerx.co.jp/entry/2026/04/01/150000
- 判定: Gap 3個, Partial 1個, Already 3個, N/A 1個
- 取り込み: 非対称損失の原則追記、カテゴリ別リスク重み付け、HITLパターン分類、FP追跡ループ設計

## [2026-04-07] ingest | The Anatomy of an Agent Harness

- ソース: "The Anatomy of an Agent Harness" by @akshay_pachaar
- 判定: Gap 2個, Partial 1個, Already 13個 (うち強化可能3個), N/A 2個
- 取り込み: FM に recoveryType 4分類追加、harness-simplification-checklist 新規作成、context-compaction-policy に Observation Masking 参照追記、/audit に Tool Usage Audit 追加

## [2026-04-06] ingest | ハーネスエンジニアリング入門 — 8ヶ月の実践記録

- ソース: https://zenn.dev/takuyanagai0213/articles/harness-engineering-intro-8months
- 判定: Gap 0個, Partial 0個, Already 8個 (うち強化可能2個), N/A 1個
- 取り込み: skill-audit に Usage Tier Classification (Weekly/Monthly/Unused 3段階) 追加、reviewer-ma/mu に署名スタイル追加
- 変更ファイル: skill-audit/SKILL.md, agents/reviewer-ma.md, agents/reviewer-mu.md, analysis report

## [2026-04-06] ingest | ASI-Evolve: AI Accelerates AI

- ソース: https://arxiv.org/abs/2603.29640
- 判定: Gap 3個, Partial 2個, Already 4個 (うち強化可能4個), N/A 3個
- 取り込み: Embedding索引付き認知基盤, UCB1バンディット探索, 候補プール管理, 多段階スケールアップ基準, 適応的計算予算配分, runs/構造化拡充, per-experimentマイクロ分析, 提案事前類似性フィルタ, 昇格知識インデックス

## [2026-04-06] ingest | SSD Self-Distillation 差分統合（alphaxiv overview）

- ソース: https://arxiv.org/abs/2604.01193 (alphaxiv 構造化レポート)
- 判定: Gap 2個, Partial 1個, Already 2個 (うち強化可能2個) — 前回統合 (2026-04-05) の差分
- 取り込み: 難易度→探索度軸+Lock/Fork分類(situation-strategy-map), Scaffolding>Model定量根拠(CLAUDE.md), 品質フィルタ緩和ガイドライン(trajectory-learning), 多様性保持定量根拠(best-of-n-guide)

## [2026-04-06] ingest | MTI: Model Temperament Profiling for AI Agents

- ソース: https://arxiv.org/abs/2604.02145
- 判定: Gap 2個, Partial 1個, Already 3個 (うち強化可能2個), N/A 2個
- 取り込み: C-R パラドックス+RLHF軸別影響+Core-Shell変動(cross-model-insights), 能力≠気質注記(model-expertise-map), Sycophancy 2ファセット(agency-safety-framework)

## [2026-04-05] ingest | Dorsey "World Intelligence" 実装体験記

- ソース: How to practically deploy Jack Dorsey's 'world intelligence' today (Single Grain)
- 判定: Gap 1個, Partial 3個, Already 5個 (うち強化可能2個), N/A 1個
- 取り込み: エージェント統合棚卸し(skill-audit), 競合解決パターン(references), DRI学習抽出(feature-tracker), 成果追跡ループ+実験バリデーション(improve)

## [2026-04-05] ingest | rohitg00/agentmemory Repo Analysis

- ソース: https://github.com/rohitg00/agentmemory
- 判定: Gap 1, Partial 2, Already 3, N/A 3
- 取り込み: Ebbinghaus decay メモリ拡張、cascading staleness 伝播、importance-based eviction、矛盾自動スキャン

## [2026-04-05] update | Parallel Agent Worktrees Orchestration → wiki

- 対象: 1 レポート（2026-04-05-parallel-agent-worktrees-orchestration-analysis.md）
- 結果: 新規概念記事 1 件（parallel-agent-orchestration.md）、既存記事更新 2 件（multi-agent-architecture.md, context-management.md）、INDEX.md 更新
- 新規概念: Awareness Summary、Pre-Merge Conflict Detection、Worktree as Runtime Environment、Narrow Context Principle

## [2026-04-05] ingest | Parallel Agent Worktrees Orchestration

- ソース: https://dev.to/mexiter/claude-code-parallel-agent-driven-worktrees-orchestration-5bf0
- 判定: Gap 2, Partial 2, Already 2, N/A 0
- 取り込み: Awareness Summary プロトコル、Pre-Merge Conflict Detection、並列タスクリスト UX、Worktree=ランタイム環境原則、fork_context 最小入力セット
- 結論: agentmemory 自体は導入しない（16K LOC の外部依存、Build to Delete 原則に反する）。アルゴリズムのみ軽量に移植

## [2026-04-05] ingest | Karpathy "LLM Wiki" Gist

- ソース: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 判定: Gap 1, Partial 2, Already 6, N/A 0
- 取り込み: log.md 導入、query サブコマンド追加、Q&A フィードバック強化、概念間矛盾検出確認
- 変更ファイル: docs/wiki/log.md (new), compile-wiki/SKILL.md, absorb/SKILL.md, knowledge-pipeline.md, analysis report

## [2026-04-05] ingest | Apple SSD — Self-Distillation for Code Generation

- ソース: https://arxiv.org/abs/2604.01193 + https://github.com/apple/ml-ssd
- 判定: Gap 0, Partial 1, Already 3 (うち強化可能3個), N/A 2
- 取り込み: 未検証トレース学習指針、VS 不採用候補記録、best-of-n 敗者パターン活用、難易度→探索度軸
- 変更ファイル: trajectory-learning.md, verbalized-sampling-guide.md, best-of-n-guide.md, analysis report
