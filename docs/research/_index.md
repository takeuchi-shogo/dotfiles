# Research Index — 外部知見統合索引

> MEMORY.md から外出しした索引。実装はコードベースに反映済み。
> このファイルは /improve や /absorb が「過去に何を統合したか」を参照する時のためのインデックス。
> **MEMORY.md 本体は常時コンテキスト**、このファイルは **on-demand 参照** 用途で分離。

更新方針: `/absorb` で新規統合が完了したら、該当カテゴリに1行追記する（MEMORY.md は更新しない）。

---

## 統合済み（60+記事/論文）

### ハーネス理論

- NLAH, Meta-Harness, AutoHarness(2件), Harness Wars/Books
- Skill Loop Wiring, Ralph Loop, AutoAgent(self-optimizing)
- Subconscious Agent — Ideation-Debate + backlog + per-run artifacts
- Harness Startup (Aicon)
- Better Harness — eval hill-climbing: regression + holdout + staleness + 4強化
- Skill Eval Loop — Wave1実装済み: per-skill score attribution + スケール統一、Wave2-3: `docs/plans/2026-04-09-skill-eval-improvement-plan.md`
- Managed Agents — Hybrid Architecture + Agent Config標準化 + Scheduling移行 + ポータビリティ → `references/managed-agents-*.md`
- **Tan: Thin Harness, Fat Skills 10原則 (2026-04-12)** — Codex 批評で #1 Parameterized Skill は frontmatter 仕様化却下 (thin harness 形式主義リスク) + #5 Resolver を過小評価から昇格 (negative routing 不足)。採用: `skill-invocation-patterns.md` 新設 (improve/absorb/research 事例集) + `skill-writing-principles.md` 原則 1 に Invert Test 追加 + `skill-conflict-resolution.md` 新設 (衝突時優先度・読まない条件・規模ガード)。Gemini 総評「70% 既実装」— 原則 8 自己スコアリングが OK Learning Loop に相当 → `docs/research/2026-04-12-tan-thin-harness-fat-skills-analysis.md`

### エージェント設計

- Self-Organizing LLM, AgentFixer, Agent Traps, Agent Teams
- Multi-Agent Autoresearch
- Emotion Concepts — functional emotions → desperation / sycophancy 因果
- Advisor Strategy — ボトムアップ escalation + Pattern 4追加 + response types + advisor-mode 評価軸 → `references/advisor-strategy.md`
- MoE Explained (Shekhar 2026-04-11) — analogical mapping → subagent-delegation-guide "Minimum Routing Granularity" 新設 [思考ステップ最小粒度 + Contextual Fragmentation / Gradient Blackout / Latency Cascade] + skill-audit Dominant tier [40%+ Expert Collapse検出] + Agent Consolidation Scan Orthogonality [出力種別×ドメイン2軸] → `docs/research/2026-04-11-moe-article-analysis.md`
- MoA paper integration (Wang et al. ICLR 2025 + Li et al. 2025-02, 2026-04-11) — /debate TTFT guard + /review Step4 rule16 Synthesis Output Verbosity Constraint + review-consensus-policy §5に MoA failure modes補足 + model-expertise-map Cross-Model vs Same-Model Race [Cross-MoA第一選択]; 既存 /debate / review / research は既に MoA 実装済みで新規 primitive 不要 → `ba3ce35`
- Routing Observability Plan (Codex批評起点, 2026-04-11) — 3-wave [measure → attribute → close loop] + AC-5に Codex 再批評 gate → `docs/plans/2026-04-11-routing-observability-closed-loop.md`
- **Multi-Agent Coordination Patterns (Cara Phillips 他, Anthropic 2026-04-10)** — 5 パターン統合ビュー [Generator-Verifier / Orchestrator-Subagent / Agent Teams / Message Bus / Shared State] に対する Gap/Partial/Already 11 項目分析。Gap: Sequential Protocol 移行判断基準 (Dochkina 2026 で 14% 向上実測)。強化: Coordinator Context Budget 明記 + Reward Hacking 検知ルール + 5-Pattern 統合ビュー新設。Codex 途中終了 → Gemini 代替批評で補完。Message Bus は hooks fan-out との前提ズレ、Agent Teams は task-registry.jsonl 実ランタイム未発見 (Codex 指摘) → `docs/research/2026-04-11-multi-agent-coordination-patterns-analysis.md`
- **New Software: CLI/Skills/Vertical Models** (2026-04-11) — Codex 批評で Partial→Gap 格上げ。cascade-routing.md + agent-invocation-logger.py パッチで online cascade の観測基盤追加 / model-debt-register.md で Harvey 示唆「moat は蒸発する」への削除条件管理 / Deterministic task contract (M) は `docs/plans/2026-04-11-deterministic-task-contract-plan.md` に格下げ。SaaS 原義の 8 割は N/A、効いたのは online cascade と model debt register の 2 点 → `docs/research/2026-04-11-new-software-cli-skills-vertical-models-analysis.md`

### Claude Code 内部

- アーキテクチャ, 7層メモリ, Memory Internals, Skill Chaining, Codex Plugin
- Harnessing Intelligence (dead weight scan)
- Harness Blueprint — 4層フレームワーク + 18手法 → 7項目統合
- `claude_code_internal_architecture.md`（agent-memory）
- **Claude Code from Source 全18章** (2026-04-10):
  - Tier1: staleness policy + 4型分類境界ルール + Coordinator "Never delegate understanding" + hook snapshot security 新規
  - Tier2: 6 built-in agents + 2^N warning + Derivability Test 禁止リスト + bubble mode
  - Tier3: 16項目研究ノート集約
  - Fork agents / KAIROS / 4-layer compression は Gemini 批評で脆弱判定 → 採用非推奨
  - → `docs/research/2026-04-10-claude-code-from-source-analysis.md`

### レビュー・品質

- Spec&Verify, SlopCodeBench, code-review-graph, cc-skills-golang
- Dual-Audience CLI, Pocock 5 Skills (prd-to-issues + improve-codebase-architecture 統合)
- Atomic Skills — 原子スキル3原則 → skill-writing-guide + Capability Coverage表 + Deterministic Metrics方針 + Multi-Skill Regression Check
- NotebookLM Extend Sessions — DBS rubric → skill-writing-guide 追加; 非公式API / Master Brain 採用却下 → `docs/research/2026-04-10-notebooklm-claude-extend-sessions-analysis.md`
- UI Quality 3-Layers — K5+K1縮約版パイロット: skill-writing-guide Pre-generation Contract 追加 + /rpi Must/Important Contract 埋め込み、3回使用後 rollback 判定 → `docs/research/2026-04-10-ui-quality-3layers-article-analysis.md`
- PostHog Agent-First 5 Rules (2026-04-11) — wrapper-vs-raw-boundary.md 新規 + subagent-delegation-guide Capability Restriction 追加 + improve-policy Friction → Eval Loop 追加 + skill-writing-guide Onboarding-not-manuals + Skill Audit Policy 追加; weekly traces hour / 既存 skills rewrite は Codex 批評により不採用 → `docs/research/2026-04-11-posthog-agent-first-rules-analysis.md`
- Spec-Driven Usable Validation (gotalab555 2026-04-11) — golden-principles GP-012 "Wire Before You Decorate" 追加 + Universal Verifier Wave2に UX差分閉ループ Task7-8 合流; M1/M4/M5 は既存でカバー済み・Credo 4/5原則は重複却下 → `docs/research/2026-04-11-spec-driven-usable-validation-analysis.md`
- Skills for CC Ultimate Guide (Anthropic engineer 2026-04-11) — skill-writing-principles に Setup Config + skill-data namespace + path validation + containment check / skill-audit に Gotchas Coverage Scan [23/92] + lessons-learned 昇格経路 / skill-archetypes に Tool Wrapper 5a Product Verification 派生型 [repo固有 oracle + credential分離 + HAR sanitize + 7日 retention] 追加; 9-type全面 metadata 化 / Infra Ops 専用 / marketplace 政策は却下; Codex 批評で当初90%判定 → 実質60-70%に修正 → `docs/research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md`
- **pepabo 失敗学習ループ (2026-04-11)** — MEMORY.md 60+記事索引を _index.md に分離 + continuous-learning 「記録しない基準」DNR-1〜7 + improve-policy "Pruning-First" philosophy shift + promote-patterns.py 昇格基準厳格化 (7日経過→2回以上再発) → `docs/research/2026-04-11-pepabo-failure-learning-loop-analysis.md`
- **caveman + genshijin brevity (2026-04-11)** — concise.md に日本語 brevity ルール+Drop リスト+例外条項追加 / output-modes.md minimal に3段階強度 (lite/standard/ultra) + MoA verbosity guard 参照リンク / skill-audit Step 3 に 3-arm 評価 (terse-control) オプション追加 / brevity-benchmark.py 新規 (主張3「日本語12pt追加削減」の実測用、未実行) ; 入力圧縮 caveman-compress は見送り (Conditional) → `docs/research/2026-04-11-caveman-genshijin-brevity-analysis.md`

### プロンプト・ワークフロー

- 30 Claude Prompts — Self-Correction + Voice Guide + DELIBERATELY SKIPPING + 80/20 → 9タスク統合完了
- 12 Claude Patterns — rewrite skill + think decision/roleplay + digest summarize + challenge persona + checkpoint brief + 参照2件
- CC Automation Guide — spike Feasibilityラベル + cron拡充
- Paper Analysis Prompts — 9プロンプト → /paper-analysisスキル統合、安全機構: 原典照合 + チャンキング + Sycophancy防止

### セキュリティ

- VeriGrey, Vibe Code, Verbalized Sampling

### 初期統合（03-08〜03-29）

33記事。カテゴリ別詳細は各メモリファイル参照。

---

## 未統合・進行中

- 3層プロンプトインジェクション対策 — `docs/plans/2026-03-25-3-layer-injection-defense-integration.md`
- 未着手プラン: Compounding Agent, MEMO, Stripe Minions, Spark — `docs/plans/2026-03-19〜20-*.md`
- Obsidian Agent Memory — Vault同期等4タスク
- Hyperagents (DGM-H) — 5タスク3Wave — `docs/plans/2026-03-29-hyperagents-integration.md`
- Agent Memory Quality Guide — lessons-learned + decision-journal
- Workflow Optimization Survey — グラフメトリクス計測は将来
- PAI — 7タスク3Wave — `docs/plans/2026-03-30-pai-integration.md`
- AlphaLab — 負の知識Playbook, Convergence検出, Error Rate Supervisor, Multi-Model Race, Data-Driven Adapter — `docs/plans/2026-04-04-alphalab-integration.md`
- Environment-Driven RL (Baseten) — RL↔ハーネス対応表、rl_advantage→AutoEvolve接続、Checkpoint→Replay、5タスク3Wave — `docs/plans/2026-04-08-environment-driven-rl-integration.md`
- CORAL (自律マルチエージェント進化) — Wave1実装済み (Consolidate heartbeat + attempts formalization)、Wave2-3未着手 — `docs/research/2026-04-08-coral-autonomous-multi-agent-evolution-analysis.md`
- 12 Claude Patterns — rewrite skill新規 + 既存6スキル拡張 + 参照2件、8タスク3Wave — `docs/plans/2026-04-09-12-claude-patterns-integration.md`
- Great Convergence (市場分析) — 「存在≠機能」の視点。cycle time実測 + Context活用度監査 + anti-Goodhart + Playwright + Outcome、5タスク3Wave — `docs/plans/2026-04-09-great-convergence-integration.md`
- Obsidian+CC Meta (Noah) — Vault自動メンテ + 双方向整合性 + Bases統合、3タスク2Wave — `docs/plans/2026-04-09-obsidian-claude-integration-enhancement.md`
- Submodular Diversity — 生成後多様性選択層 + 計測基盤 + /research Aggregate強化、7タスク3Wave — `docs/plans/2026-04-10-submodular-diversity-integration.md`
- Universal Verifier (CUA検証) — controllability帰属 + 動的ルーブリック + Two-pass verification + scoring uncontrollable + AutoEvolve構造レビュー、6タスク3Wave — `docs/plans/2026-04-10-universal-verifier-integration.md`
- その他: Ultimate Guide, OTel, AI System Design, MiniMax 等 — `docs/research/` 配下の analysis.md 参照

---

## メンテナンス

- **ロード条件**: このファイルは常時ロードしない。`/absorb` のギャップ分析時、`/improve` の Garden フェーズ時、または過去統合の参照が必要な時に明示的に読む
- **上限**: 200行を目安。超えたら古い「初期統合」セクションを `_index_archive.md` に退避
- **連動**: MEMORY.md には `外部知見索引 → docs/research/_index.md` の1行のみ残す
