# Wiki Operations Log

> Append-only record of wiki operations. Each entry follows the format:
> `## [YYYY-MM-DD] operation | Title`
>
> Operations: `ingest` (absorb), `compile` (compile-wiki), `update` (compile-wiki update),
> `lint` (compile-wiki lint), `query` (compile-wiki query), `index` (compile-wiki index)

<!-- Parseable with: grep "^## \[" docs/wiki/log.md | tail -10 -->

## [2026-04-11] ingest | Multi-agent coordination patterns (Anthropic)

- ソース: https://claude.com/blog/multi-agent-coordination-patterns
- 判定: Gap 1 (Sequential Protocol 移行判断), Partial 6 (Generator-Verifier/Agent Teams weak/Message Bus 前提ズレ/Shared State/Context Accumulation/Information Bottleneck), Already 4 (うち強化可能 3: Orchestrator-Subagent context budget, Pattern Selection 5-view, Reward Hacking)
- 取り込み: Wave 1 (5-Pattern 統合ビュー新設 + Coordinator Context Budget + Sequential Protocol 移行判断基準), Wave 2 (Reward Hacking 検知 + Agent Teams 実ランタイム + Shared State 制約明示) — 計 6 タスク L 規模、新セッションで `/rpi` 実行予定
- 分析レポート: docs/research/2026-04-11-multi-agent-coordination-patterns-analysis.md
- 統合プラン: docs/plans/2026-04-11-multi-agent-coordination-patterns-integration.md
- Phase 2.5 メモ: Codex プロセス途中終了 (task-registry.jsonl 実体未発見のみ取得)、Gemini で代替批評完了

## [2026-04-11] ingest | The New Software: CLI, Skills & Vertical Models

- ソース: Agent Experience 時代の SaaS 戦略論
- 判定: Gap 2 (online cascade, model debt register) / Partial 2 / Already 3 / N/A 2
- 取り込み:
  - cascade-routing.md (新規 references)
  - model-debt-register.md (新規 references)
  - agent-invocation-logger.py に cascade marker parser をパッチ
  - deterministic-task-contract-plan.md (M plan 化、未実装)
- Codex 批評で Claude バイアス 4 点補正 (cover 過大評価、Pitfall 重複、Harvey 誤読、deterministic Already 甘い)
- 詳細: docs/research/2026-04-11-new-software-cli-skills-vertical-models-analysis.md

## [2026-04-11] ingest | pepabo 失敗学習ループ記事

- ソース: https://zenn.dev/pepabo/articles/claude-code-failure-learning-loop (あたに, GMOペパボ)
- 判定: Partial 4 / Already 1 / N/A 1 / Gap 0（当初 Gap 1 判定だったが Codex 批評で N/A に修正）
- 取り込み:
  - MEMORY.md 棚卸し + docs/research/_index.md 分離
  - continuous-learning に「記録しない基準」DNR-1〜7 追加
  - improve-policy を Pruning-First 思想に書き換え (verify 行付き)
  - promote-patterns.py を evidence-based 昇格 (2+ scopes OR 3+ occurrences, 30日 stale dismiss)
  - dead-weight-scan-protocol に容量上限トリガー追加
- 除外: 項目2 失敗フィールド追加 (over-engineering), 項目5 EUC-JP guard (repo に該当ファイルなし)
- 最大の学び: Codex 批評で「記事の核心は3層構造ではなく『記録しない基準』と『まず1件だけの導入容易性』」と指摘。既存セットアップの「研究知見を吸収する力が強すぎる」バイアスが可視化された

## [2026-04-10] ingest | Claude Code from Source (全18章リバースエンジニアリング)

- ソース: https://claude-code-from-source.com/ — 2000ファイル/~150-200K LoC のモノリスを 36 エージェント×6時間で復元した18章解説書
- 判定: Already 9個, Already(強化可能) 4個, Partial 15個, Gap 4個, N/A 28個 (全60キーワード)
- 取り込み (Tier 1): Memory staleness 運用ポリシー + 4型分類境界判定ルール (`memory-safety-policy.md`) / Coordinator "Never delegate understanding" 4-phase (`agent-orchestration-map.md`) / Hook snapshot security 対応表 新規 (`hook-snapshot-security.md`)
- 取り込み (Tier 2): 6 built-in agents の全体像 (`wiki/concepts/claude-code-architecture.md`) / 2^N problem 警告 原則9 (`skill-writing-principles.md`) / Derivability Test 具体禁止リスト (`compact-instructions.md`) / Sub-agent bubble permission mode (`subagent-delegation-guide.md`)
- 記録のみ (Tier 3): 16項目を包括研究ノートに集約
- 却下/降格: Fork agents byte-identical (Gemini: 実効25-50%/OS差異リスク/ROI negative → 採用非推奨), 4-layer context compression (過度に複雑), KAIROS mode (AutoEvolve で類似カバー済み), Generator Loop 1730行 monolith (dotfiles 責務外)
- Codex/Gemini 批評: Codex は 14 分タイムアウトで cancel (task-mnsmuwyq-sifv6r), Gemini のみで Phase 3 に進行。Gemini は file-based memory + self-describing tools + hook-based architecture を「最も堅牢」、Fork agents + Query.ts monolith + KAIROS を「最も脆弱」と判定
- 分析: [2026-04-10-claude-code-from-source-analysis.md](../research/2026-04-10-claude-code-from-source-analysis.md) (包括研究ノート), [2026-04-10-claude-code-from-source-integration-report.md](../research/2026-04-10-claude-code-from-source-integration-report.md) (/absorb レポート)

## [2026-04-10] ingest | How to Build a Full AI Stack Using Only Claude in 2026 (cyrilXBT)

- ソース: cyrilXBT blog post "How to Build a Full AI Stack Using Only Claude in 2026 (Full Course)"
- 判定: Already 3個 (L1,L3,L4), Partial 2個 (L2,L5), N/A 1個 (L6)
- 取り込み: Stop hook に `sync-memory-to-vault.sh` を追加（L5 核心未回収の閉ループ化）。Dry-run で 18 ファイルのバックログ検出が hook 欠落の物証
- 却下: P1 (Research→Draft→QC playbook — 既存 skills で実質カバー), P3 (反論メモ — 情報密度不足), L6 (スコープ外)
- Codex/Gemini 批評: 「記事の本質は単一ツール信仰でなく、定時実行／成果物固定／QC を挟む設計」「このセットアップは既に記事の先を行っている」
- 分析: [2026-04-10-claude-full-ai-stack-2026-analysis.md](../research/2026-04-10-claude-full-ai-stack-2026-analysis.md)

## [2026-04-10] ingest | NotebookLM Extend Sessions (blog)

- ソース: "I want to extend my Claude sessions (full guide)" (Teng Ling の notebooklm-py 言及)
- 判定: Gap 1個 (採用), Partial 3個, N/A 2個 (defer 付き), 新規 Gap 1個 (データ分類ゲート)
- 取り込み: skill-writing-guide に DBS rubric (Direction/Blueprints/Solutions) チェックリスト追加。Atomic Skill の Self-containment と連携
- 却下: notebooklm-py CLI 導入, Master Brain 方式, /wrap-up 独立スキル (非公式 API の production harness リスク + 既存 /checkpoint + continuous-learning + Obsidian で充足)
- Codex セカンドオピニオン: 「採用は 1 つだけ、DBS rubric のみ」の勧告に従う
- 分析: [2026-04-10-notebooklm-claude-extend-sessions-analysis.md](../research/2026-04-10-notebooklm-claude-extend-sessions-analysis.md)

## [2026-04-10] ingest | The Art of Building Verifiers for Computer Use Agents

- ソース: https://arxiv.org/abs/2604.06240 (Microsoft Research)
- 判定: Gap 2個, Partial 1個, Already(強化可能) 4個, Already(強化不要) 1個
- 取り込み: 全7項目 — controllability帰属, scoring uncontrollable case, 動的ルーブリック生成, Two-pass verification, 動的関連性スコアリング概念, AutoEvolve構造レビュー+alignment tipping対策
- プラン: `docs/plans/2026-04-10-universal-verifier-integration.md`

## [2026-04-10] ingest | Scaling Coding Agents via Atomic Skills

- ソース: [arXiv:2604.05013](https://arxiv.org/abs/2604.05013)
- 判定: Gap 0個, Partial 4個, Already 0個, N/A 3個 (うち proxy 可 2個)
- 取り込み: Independent Evaluability 明示化, Capability マッピング表, Deterministic Metrics 方針, AutoEvolve Multi-Skill Regression Check

## [2026-04-09] ingest | Launching Claude Managed Agents

- ソース: Anthropic Blog — Launching Claude Managed Agents
- 判定: Gap 1個, Partial 2個, Already 2個(強化可能), N/A 1個
- 取り込み: Hybrid Architecture リファレンス, CLAUDE.md ルーティング更新, Agent Config 標準化, Scheduling 移行検討, ポータビリティガイド

## [2026-04-09] ingest | 30 Claude Prompts, Workflows & Automations

- ソース: "30 Claude Prompts, Workflows & Automations I Use Every Single Day" (@eng_khairallah1)
- 判定: Gap 1個, Partial 6個, Already 10個, Already(強化可能) 3個, N/A 5個
- 取り込み: /decision スキル作成, /weekly-review 強化(DELIBERATELY SKIPPING + 80/20), /morning 強化(Blocked), /output-mode learning 段階化, /profile-drip スキルギャップ, /obsidian-content Self-Correction + Voice Guide + Repurpose + Thread体系化

## [2026-04-08] ingest | CORAL: Autonomous Multi-Agent Evolution

- ソース: arXiv:2604.01658 (MIT, NUS, Stanford 他)
- 判定: Gap 1個, Partial 3個, Already 5個 (うち強化可能 2個), N/A 1個
- 取り込み: Consolidate heartbeat導入、attempts構造formalization、蒸留品質因果検証(Wave2)
- プラン: Wave 1実装完了、Wave 2-3は `docs/research/2026-04-08-coral-autonomous-multi-agent-evolution-analysis.md`

## [2026-04-08] ingest | Environment-Driven Reinforcement Learning

- ソース: Baseten Blog — Environment-Driven Reinforcement Learning
- 判定: Gap 0個, Partial 1個, Already 7個 (うち強化可能 5個), N/A 0個
- 取り込み: Environment-as-User パターン明文化、RL→AutoEvolve接続、Checkpoint→Replay拡張、Recording Proxyストリーミング化、AutoEvolve自動化
- プラン: `docs/plans/2026-04-08-environment-driven-rl-integration.md`

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

## [2026-04-08] ingest | ASI-Evolve: AI Accelerates AI

- ソース: https://arxiv.org/abs/2603.29640
- 判定: Gap 1個, Partial 1個, Already(強化可能) 5個, Already(強化不要) 4個
- 取り込み: 全6件採用 — P0: proposals.jsonl lineage拡張 + micro-analyzer, P1: proposal-level dedup, P2: knowledge-index + retrieval, P3: 3段ゲート評価, P4: UCB1
- プラン: `docs/plans/2026-04-08-asi-evolve-autoevolve-integration.md`

## [2026-04-08] ingest | CC Harness Blueprint

- ソース: "How I built harness for my agent using Claude Code leaks" (Medium記事)
- 判定: Gap 0個, Partial 7個, Already 7個 (強化不要), N/A 4個
- 取り込み: マイクロループ規律, コンテキスト注入ポリシー, Context Collapse, Progressive Trust, CC内部Retry/Budgeting参照, UI Trust原則

## [2026-04-09] ingest | Better Harness: Eval-Driven Hill-Climbing

- ソース: "Better Harness: A Recipe for Harness Hill-Climbing with Evals" (LangChain/Z.ai)
- 判定: Gap 1個, Partial 2個, Already 4個(うち強化可能4), Already 強化不要 3個, N/A 1個
- 取り込み: 全7項目 — 実行型 Regression, Holdout split, Eval spring cleaning, External import, Baseline run, Version diff, パイプライン図
- プラン: docs/plans/2026-04-09-better-harness-integration.md（L規模, 8タスク3Wave）

## [2026-04-09] ingest | 12 Things Claude Can Do for You

- ソース: "12 things Claude can do for you that you've never tried" (@sharbel)
- 判定: Gap 1個, Partial 4個, Already 6個 (うち強化可能 2個), N/A 1個
- 取り込み: 全項目。Wave 1: rewrite skill + /think decision + /digest summarize。Wave 2: /challenge persona + /think roleplay + /checkpoint brief。Wave 3: voice guide + data analysis patterns
- プラン: `docs/plans/2026-04-09-12-claude-patterns-integration.md`

## [2026-04-09] ingest | Skill Evaluation & Self-Improving Loop

- ソース: 外部記事テキスト（URL なし）
- 判定: Gap 2個, Partial 4個, Already(強化可能) 4個, N/A 0個
- 取り込み: Wave 1 実装済み（per-skill score attribution + スケール統一）、Wave 2-3 は docs/plans/2026-04-09-skill-eval-improvement-plan.md

## [2026-04-09] ingest | Obsidian + Claude Code is the new meta

- ソース: "Obsidian + Claude Code is the new meta" (Noah, Sovereign Creator OS)
- 判定: Gap 1個, Partial 1個, Already 6個 (うち強化可能1), N/A 1個
- 取り込み: T1 Vault自動メンテナンス, T2 双方向整合性チェック, T3 Bases統合(低優先)

## [2026-04-10] ingest | Submodular Optimization for Diverse Query Generation in DeepResearch

- ソース: https://jina.ai/news/submodular-optimization-for-diverse-query-generation-in-deepresearch/
- 判定: Critical Gap 1個, Gap 2個, Partial 1個, 低優先 1個, Already(強化可能) 2個
- 取り込み: 全項目選択。計測基盤→選択層→Aggregate強化→2段階パイプライン→λ制御の順で統合予定
- プラン: `docs/plans/2026-04-10-submodular-diversity-integration.md`

## [2026-04-10] ingest | The Advisor Strategy

- ソース: https://claude.com/blog/the-advisor-strategy
- 判定: Gap 1個, Partial 2個, Already 3個 (うち強化可能 3個), N/A 1個
- 取り込み: Advisor パターンリファレンス新規作成、委譲ガイドに中間相談プロトコル (Pattern 4) 追加、benchmark-dimensions に Advisor-Mode 評価軸追加

## [2026-04-10] ingest | UI Quality 3-Layers (SKILL.md 品質3層定義)

- ソース: UIデザインスタジオ記事「Claude Code の SKILL.md に品質3層定義を書いたら 40 画面のデザインが破綻しなくなった」
- 判定: Gap 4 (K1/K3/K5/K7), Partial 2 (K2/K6), N/A 1 (K4)
- 取り込み: K5 (SKILL.md 検証基準埋め込み) + K1 縮約版 (Must/Important/Optional 義務差) をパイロット先行
- 変更: skill-writing-guide.md (Pre-generation Contract Pattern), rpi.md (Phase 1/2/3 Must Contract)
- 分析レポート: docs/research/2026-04-10-ui-quality-3layers-article-analysis.md
- Codex 批評で L3「感動品質」を排除、固定比率も採用せず義務差ベースに変換

## [2026-04-11] ingest | 仕様通り動くの先へ。Claude Codeで「使える」を検証する

- **ソース**: gotalab555 (Speaker Deck)
- **判定**: Gap 1 (M3 UX差分閉ループ), Already 2 (M1, M4), N/A 2 (M2残4, M5), 強化 1 (GP-012)
- **取り込み**: GP-012 Wire Before You Decorate、Task 7 (ui-observer UX Diff Scoring) 実装、Task 8 (/validate UX Score Gate) 実装、Universal Verifier プラン Wave 2 に合流

## [2026-04-11] ingest | PostHog Agent-First Rules

- ソース: The golden rules of agent-first product engineering (Jina Yoon, posthog.com)
- 判定: Gap 1 (wrapper-vs-raw), Already 強化可能 3 (subagent/improve/skill-writing), 強化不要 1 (universal context)
- 取り込み: wrapper-vs-raw-boundary.md 新規 + Capability Restriction Policy + Friction→Eval Loop + Onboarding-not-manuals
- 不採用: Weekly traces hour (Codex 批評), 既存 skills rewrite (dead weight)
- レポート: docs/research/2026-04-11-posthog-agent-first-rules-analysis.md

## [2026-04-11] ingest | Skills for Claude Code — The Ultimate Guide from an Anthropic Engineer

- ソース: Medium 記事 (Anthropic engineer, URL 特定不可)
- 判定: Gap 1 (BP5 config.json), Partial 6 (Gotchas 浸透率 25%, 9-type taxonomy=Documented/Not operationalized, Product Verification, BP9 hooks 乖離, BP6 description 棚卸し, BP7 memory, skill sharing), N/A 1 (Infra Ops), Already 強化不要 5 (DBS/Onboarding/Scripts/Usage measurement/Iterative dev)
- 取り込み: T1 skill-writing-principles に Setup Config & Persistent State 標準スキーマ + skill_name validation/containment check, T2 skill-audit に Gotchas Coverage Scan + lessons-learned 昇格経路, T3 skill-archetypes に Tool Wrapper 5a Product Verification 派生型 (repo 固有 oracle + credential 分離 + HAR sanitize + 7日 retention)
- 不採用: 9-type 全面 metadata 化, Infra Ops 専用 skill, marketplace 重装備化, BP9 hooks 全面再設計 (Codex 推奨)
- 批評: Codex が当初 90% 判定 → 実質 60-70% に修正。Gotchas 23/92 実態など [verified] 指摘多数。security-reviewer 3 Medium 指摘 (path traversal / Evidence PII / credential) も反映済み
- Gemini 空振り (別調査に分岐)
- レポート: docs/research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md

## [2026-04-11] ingest | caveman + genshijin brevity

- ソース: https://github.com/JuliusBrussee/caveman (Julius Brussee, 15.6k stars) + https://zenn.dev/mikana0918/articles/7ad57493a04f88 (mikana0918, Zenn)
- 判定: Gap 3個 (日本語 brevity, Drop リスト型, 強度グラデーション), Partial 2個 (3-arm 評価, token delta 記録), Already 3個 (SessionStart + state file, 自動リバート, Verbosity Guard), N/A → Conditional 1個 (入力圧縮), N/A 2個 (npx 配布, 5x API 利用)
- 取り込み: A1+A2 (concise.md 日本語+Drop+例外), A3 (skill-audit 3-arm オプション), Gap#3 縮小版 (minimal 3段階強度), A4 縮小版 (Verbosity Guard 参照リンクのみ), brevity-benchmark.py 新規
- 見送り: 入力圧縮 caveman-compress, 5段階 (3段階に縮小), Verbosity Guard 全面適用 (Codex 警告により縮小)
- 批評: Codex で「MoA verbosity guard (構造レベル) と Drop リスト (語彙レベル) は別物で新規性あり」「5段階は過剰」「日英混在時の技術説明曖昧化が真の副作用」「A4 全面適用は検証報告まで痩せる」を受けた修正を反映
- 実測検証: 未実行 (brevity-benchmark.py は実装済みだが実行は明示トリガー待ち、tiktoken インストール要)
- レポート: [2026-04-11-caveman-genshijin-brevity-analysis.md](../research/2026-04-11-caveman-genshijin-brevity-analysis.md)

## [2026-04-12] ingest | Garry Tan: Thin Harness, Fat Skills (10 Design Principles)

- ソース: Garry Tan "Ten Design Principles of Agentic AI Skills Design"
- 判定: Gap 0, Partial 3 (#1 Parameterized Skill / #7 Narrow Tools / #10 Invocation Pattern), Already 6, 強化可能 2 (#2 Invert Test / #5 Negative Routing)
- 取り込み:
  - skill-invocation-patterns.md 新設 (事例集: improve/absorb/research/モデルルーティング)
  - skill-writing-principles.md 原則 1 に Invert Test 追加
  - skill-conflict-resolution.md 新設 (negative routing + 衝突優先度 + 規模ガード)
- 批評反映: Codex 指摘で #1 frontmatter parameters 仕様化を却下 (形式主義リスク)、#5 Resolver を強化可能に昇格。Gemini 総評で 70% 既実装 → 取り込み最小限
- レポート: `docs/research/2026-04-12-tan-thin-harness-fat-skills-analysis.md`

## [2026-04-12] re-absorb | caveman / genshijin brevity (mikana0918 Zenn 記事)

- ソース: https://zenn.dev/mikana0918/articles/7ad57493a04f88
- 種別: 既存統合の再検証 (Phase 2.5 まで再分析)
- 判定: Gap 1個 (J: benchmark validation), Partial 3個 (B/D/E), Already強化可能 8個, 新規要素 4個 (M/N/O/P)
- 取り込み: concise.md 拡充 (Drop リスト・語形短縮・2層分離・ultra gate 強化)、output-modes.md 同期、brevity-benchmark.py バグ修正
- Codex 批評: ultra 強化で verification/review gate の情報損失リスク → gate 出力は ultra 禁止に
- Gemini 補完: Anchored Summarization (State/Constraint 圧縮禁止)、cascade failure 対策

## [2026-04-12] ingest | Andrej Karpathy Skills

- ソース: https://github.com/forrestchang/andrej-karpathy-skills
- 判定: Gap 0個, Partial 4個, Already 3個(うち強化可能1個), N/A 0個
- 取り込み: 多解釈列挙プロトコル、スコープ外3層禁止、抽象化アンチパターン、TDD 事前宣言強化
- Codex 批評: instruction層のみの分析は盲点あり — hook/gateの暗黙カバーを考慮すべき。真のギャップは#1と#5

## [2026-04-14] ingest | Build Agents that never forget (Cognee / Akshay Pachaar)

- ソース: テキスト貼り付け (`@akshay_pachaar` Substack / Blog)
- 判定: Gap 0, Partial 4 (T4 entity dedup / T6 代名詞解決 / T9 multihop traversal / T8 lost-in-middle 境界条件), Already 強化 4 (T2 implicit relationships / **T5 usage-based edge weight ★ 最優先** / T7 境界条件 docs / T8 compression 担保), N/A 2 (T3 vector/graph DB / T1 4 分類メモリ階層)
- Codex + Gemini 合意: vector/graph DB 導入は個人 dotfiles に過剰。既存 markdown + jsonl + hooks の拡張で対応
- 取り込み: 7 タスク (A-G) L 規模統合プラン
  - `docs/research/2026-04-14-cognee-agent-memory-analysis.md`（分析レポート）
  - `docs/plans/2026-04-14-agent-memory-enhancement-plan.md`（統合プラン、`/rpi` 実行用）
- Phase 3 Triage: ユーザー「全部」選択
- Gemini 補完: 分析麻痺リスク(タイムボックス必要)、Surgical Changesの断片化リスク、SDD台頭
