# Wiki Operations Log

> Append-only record of wiki operations. Each entry follows the format:
> `## [YYYY-MM-DD] operation | Title`
>
> Operations: `ingest` (absorb), `compile` (compile-wiki), `update` (compile-wiki update),
> `lint` (compile-wiki lint), `query` (compile-wiki query), `index` (compile-wiki index)

<!-- Parseable with: grep "^## \[" docs/wiki/log.md | tail -10 -->

## [2026-04-07] ingest | AlphaEvolve: Gemini-powered coding agent for algorithm design

- ソース: AlphaEvolve (Google DeepMind, 2025-05) — 公式ブログ + arXiv:2506.13131
- 判定: Gap 2個 (島モデル, 差分パッチ生成), Partial 1個 (プロンプト組立エンジン), Already強化 4個 (モデルルーティング, 進化ループ, 自動評価関数, 候補DB)
- 取り込み: 全7項目。Layer 0: 二層評価アーキテクチャ + 候補DBメタデータ拡充。Layer 1: Tournament Mode拡張 + 差分パッチ生成。Layer 2: Context Assembly体系化 + 島モデル導入。Layer 3: 探索/深化トークン予算分離
- ドメイン適合性注記: 手法の直接移植ではなく設計パターンの翻案（決定的評価×数百世代→確率的評価×最大5世代）
- プラン: docs/plans/2026-04-07-alphaevolve-integration.md

## [2026-04-07] ingest | RACA: Research Assistant Coding Agent for Ph.D. Students

- ソース: ブログ記事 "RACA: Research Assistant Coding Agent for Ph.D. Students"
- 判定: Partial 4個 (Canary Job, Red-team自動起動, Observability, Task Archetype), Already強化 4個 (Repair Routing, Stage Transition, Conductor統合, gaming-detector), N/A 2個 (HPC, Single Workspace)
- 取り込み: 全8項目。Wave 1: 変更面ベース自動preflight, 高リスク変更Red-team自動トリガー, Repair Routing Table。Wave 2: Backend Task Archetype Templates, Stage Transition結線, Observability信号接続。Wave 3: Conductor統合, gaming-detector拡張
- リフレーム: "Knowledge over Code" → "Knowledge with Code", "Dataset Skills" → "Backend Task Archetype Templates", "Research Dashboard" → "Observability Dashboard"
- プラン: docs/plans/2026-04-07-raca-integration.md

## [2026-04-07] ingest | LLM Knowledge Bases Full Guide (Karpathy method)

- ソース: How to create your own LLM knowledge bases today (full course)
- 判定: Gap 1個 (Wiki→Schema昇格パス), Partial 2個 (定期自動コンパイル, Wiki→QA生成), Already強化 4個 (Filing Loop実効化, Lint auto-fix, INDEX強化, frontmatter強化), N/A 1個 (QMD)
- 取り込み: compile-wiki に promote/lint--fix/generate-data サブコマンド追加、query Filing Loop をデフォルト提案に変更、INDEX に source_count/related_concepts 追加、frontmatter に confidence/last_validated 追加、auto-morning-briefing.sh に wiki auto-update 接続

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

## [2026-04-07] ingest | Skills can use subagents, Subagents can use skills

- ソース: X post on Claude Code agent design (Skills ↔ Subagents composition patterns)
- 判定: Gap 1個, Partial 1個, Already 1個 (強化不要)
- 取り込み: workflow-guide.md に Skill ↔ Subagent 合成パターンの判断基準テーブルを追加

## [2026-04-07] ingest | The Anatomy of an Agent Harness (Round 2 再分析)

- ソース: "The Anatomy of an Agent Harness" by @akshay_pachaar
- 判定: 新規 Gap 2個, Partial 1個, 強化 1個（Round 1 の見落とし分）
- 取り込み: ACON compaction 優先順位テーブル、ツール数閾値+エラー複合則を resource-bounds に追加、workflow-guide ステップ追加時のコスト評価参照、Co-evolution ツール定義安定性セクション

## [2026-04-07] ingest | The Anatomy of an Agent Harness (Round 1)

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

## [2026-04-07] ingest | SDLC品質分散 — コードレビュー依存からの脱却

- ソース: https://mtx2s.hatenablog.com/entry/2026/04/06/061511
- 判定: Gap 0, Partial 3, Already 17 (うち強化可能 4), N/A 6
- 取り込み: completion-gate パターン分類、AST 構造チェッカー、review 多モデル検証、タスク分解ガイド、ライセンスチェック
- 変更ファイル: completion-gate.py, structure-check.py, settings.json, task-decomposition-guide.md, security-reviewer.md, analysis report
