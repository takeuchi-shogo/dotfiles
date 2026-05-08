---
status: active
last_reviewed: 2026-04-23
---

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
- **30 Claude Code Sub-Agents I Actually Use in 2026 (2026-05-02)** — anonymous 著者の subagent カタログ記事 (business team agent 多数含む 30 個 / 9 カテゴリ)。**採用 4 件** (Pruning-First 譲歩、deep-dive で novel pattern 発見): T2 migration-guard.md に forward+reverse BLOCK rule + Postgres-specific hard blockers (>1M rows non-concurrent index 等) / T3 edge-case-analysis に 15 軸補足チェックリスト (empty/max/off-by-one/network/i18n/timezone/DST/leap year/currency/partial failures/retries/stale cache 等) / T5 agent-design-lessons.md に Self-Rejection Rule Pattern セクション (spec-writer の vanity metric reject、edge-cases の null check 単独 reject、decision-log の options なし reject 等の novel design pattern を 1st-class artifact 化) / メタ Subagent Count Ceiling セクション (Gemini grounding: 50+ subagent で品質 9/10→5/10 劣化 + token cost spike、dotfiles 既存 33 個で警戒ライン残り 17 個)。棄却 26 件: code-reviewer (COMPLETION CONTRACT + 5 次元スコア + Critic Evasion 耐性 + Dynamic Rubric Generation で十分) / counterargument (/debate は multi-model orchestration で設計思想完全に異なる、新規 subagent 追加は router 劣化リスク) / decision-log (/decision に「撤回条件」既存で revisit-condition カバー済) / daily-plan (/timekeeper の対話型コーチング Q1-Q7 vs structured 4-task で設計思想衝突) / business team 15 個 (Sales/Marketing/CS/Ops/Finance は個人 dotfiles で out_of_scope、Gemini #2 UNFOUND: solo engineer 用 ROI 独立検証なし)。Codex (codex-rescue) 最終推奨「採用 1 件 (T3 のみ)」、Gemini grounding 「single-purpose CONFIRMED + 50+ degradation CONFIRMED」。ユーザー「本当に抜け、漏れ、手抜きない？」指摘で 4 軸 deep-dive 実行 (Difficulty path / Model 配分 / Rejection rules pattern / Single-purpose 違反検出) → Self-Rejection Rule pattern を Gap として発見、4 件採用に増加。教訓: 個別 subagent コピーは router 劣化リスク (33→63 で性能崩壊)、メタ原則 codify (Self-Rejection Rule + Subagent Count Ceiling) の方が ROI 高い、既存 subagent 数の自覚 (現状 33 個) が新規追加判断に必須 → `docs/research/2026-05-02-30-subagents-2026-absorb-analysis.md`
- **Cursor Continually Improving Agent Harness (2026-04-30)** — Cursor 公式 (Heule & Katz) の継続改善実践 6 章 + 11 手法。直近 5 本目の harness-engineering 記事吸収で **採用 0 件** (Pruning-First 完徹)。N/A 7 件 (大量ユーザー前提 #2/#3/#4/#6、IDE 固有 #1、checkpoint 代替 #10、明示棄却済 #6) + Already 強化不要 4 件 (#5 failure-taxonomy 21 FM で吸収 / #7 R-002 役割分離 / #9 cross-model-insights 2026-03-25 既記載 / #11 31 agents)。Codex stdout 失敗→Opus 直接ファイル精読で 4 件を強化可能→強化不要に格下げ。Gemini の表層的推奨 3 件 (Tool error taxonomy / LM-based satisfaction / Context Rot) も実ファイル精読で全棄却。教訓: 累積 5 本目で採用率 6→3→1→4→0 の飽和 / Watch 行 mechanism (R-NNN) を使う選択肢はあったがユーザー判断で 0 件採用 → `docs/research/2026-04-30-cursor-harness-absorb-analysis.md`

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
- **google/skills + ADK 2.0 5 Patterns (2026-04-24)** — google/skills 13 GCP skill (alloydb/bigquery/cloud-run/cloud-sql/firebase/gemini-api/gke + recipe×3 + waf×3) を skills-lock.json 統合 (本業 GCP 利用、commit 6f0b877)。ADK 2.0 5 patterns (Hybrid Graph/Coordinator-Specialist/Skill Composition/Cross-Language Pipeline/Sandboxed Executor) は全 Already 判定: blueprint-pattern.md + triage-router + skill-invocation-patterns + cmux-ecosystem + hook 防御層で実装済、強化不要。gh CLI v2.90+ 不在で手動 clone フォールバック、name mismatch 1 件 (networking-observability) は recipe 接頭辞付与で解消 → `docs/research/2026-04-24-google-skills-adk2-absorb-analysis.md`

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
- **SKILL.md 15min Guide (Nyk @nyk_builderz, 2026-04-26)** — community blogger による初級7セクションガイドの分析。90 skills + skill-creator + skill-audit + writing-skills + cwd-routing-matrix の成熟度に対し全項目 Already (allowed-tools 100% / Triggers+Do NOT use 100% / DBS 三層 / 6 pattern 分類)。Codex 批評で 1) 「100% description coverage ≠ 品質」、2) paths field の N/A by design 判定は妥当 (skill=intent / rules=file constraint レイヤリング維持)、3) build-first は Pruning-First と逆向き、と整合確認。Gemini 補完で著者・Telegram channel・superpowers/gstack repo 実在確認、「15分」は過大宣伝。ユーザー判断で取り込み不要 (唯一の微強化候補 skill-audit examples discoverability も skip) → `docs/research/2026-04-26-skill-md-15min-guide-absorb-analysis.md`
- **Codex/Claude Parity (X post 4 tips, 2026-04-27)** — "Optimize Codex just like Claude Code" の 4 ステップ (AGENTS.md / config.toml / Skills / Hooks) absorb。**初回分析の手抜き** をユーザー指摘で発覚 → 11 項目周辺見落とし検出 → feedback memory 化 (`feedback_absorb_thoroughness.md`)。Codex CLI v0.124.0 で `codex_hooks stable` 確認 (record `[[hooks.PostToolUse]]` + `[[hooks.PostToolUse.hooks]]` 二層 PascalCase + `[features].codex_hooks=true` 必須、既知バグ #19199 注意)。実装: G1 hooks pilot / G7 MCP sync (Claude側に deepwiki+openaiDeveloperDocs 追加) / G6 agents 5 移植 (edge_case_hunter / silent_failure_hunter / comment_analyzer / migration_guard / cross_file_reviewer、既存 reviewer/security_auditor との重複回避) / G2 dependency-auditor port / G3 hook-debugger Codex 版 / G9 stable features AGENTS.md 追記。Codex 公式に user-defined slash commands 機能なし確認 → G5 spec stub に降格 (commands の多くは Codex skill として並存) / G8 plugin selection spec / G13 hooks 全 port spec 別セッション。petekp/claude-code-setup・ariccb/sync-claude-skills-to-codex は Nix で代替済 + bulk sync は Pruning-First 違反で棄却。プラン: `docs/plans/active/2026-04-27-codex-parity-plan.md` → `docs/research/2026-04-27-codex-claude-parity-absorb-analysis.md`

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
- **Hermes personal analyst (2026-04-14)** — 10手法中 Already 強化不要 5 / N/A 2 / Already 強化可能 2 / Gap 小 1。auto-morning-briefing.sh に Hacker News + arXiv + RSS 統合 + mcp-skill-hint.py (PostToolUse hook) 新規追加; 月次コストダッシュボードは spike PASS (Claude/Codex JSONL で feasible、Gemini は blind) で別 plan 化; `auto-morning-briefing.sh` 発見により #2 判定を Pass 2 で N/A → Already 強化可能に補正; Scaffolding > Model は Gemini で "Scaffolding over Scaling" 論文裏付け → `docs/research/2026-04-14-hermes-personal-analyst-analysis.md`
- **Hermes Fleet Shared Memory (2026-04-17)** — Qdrant+Ollama+mem0+Stop hook による自己ホスト共有メモリ構成の分析。既存資産（Stop hook→session-learner、OTel redactor）と大幅重複、即導入不要と判定。Codex 批評で #3 mem0 Partial 昇格・#7 Local fallback Gap 格上げ。4 タスク取り込み: Track A (secret 監査→redactor 統合) + Track B (schema 策定→semantic search 実験、撤退条件付き) → `docs/research/2026-04-17-hermes-fleet-shared-memory-analysis.md`、プラン: `docs/plans/2026-04-17-hermes-absorb-plan.md`
- **Context Design 5層 (i3design, 2026-04-17)** — 5層コンテキストデザイン（System/Memory/History/Input/Output）の分析。10タスク P1-P4 採用: Connector drift 検出 + Telemetry 品質スコア + cwd-aware profile + Hook 陳腐化 Guard + MCP 非依存性 + 金額予算表示 + skill-local lock 他。ステータス: integrated → `docs/research/2026-04-17-context-design-absorb-analysis.md`、プラン: `docs/plans/2026-04-17-context-design-absorb-plan.md`

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
- WebFetch Haiku 要約 (sherry/Zenn 2026-05-04) — WebFetch は内部 Haiku 要約あり、3 条件 (markdown対応/trusted domain/<100k chars) 外はサイレント truncate。8/8 採用 (web-fetch-policy.md + telemetry hook + 委譲契約改訂 + absorb gate 化 + security 接続)。L 規模 14 ファイル → `docs/plans/2026-05-06-webfetch-policy-plan.md`、レポート: `docs/research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md`
- Warp oz-skills 15 skill (2026-05-07) — Warp ADE ベンダー MIT 配布。新 skill 追加せず 6 件すべて rubric 移植 (Pruning-First): ci-fix-policy.md / check-health Step 3.8 / design-reviewer WCAG / pull-request Pre-PR Chain / scheduling-decision-table.md / agent-browser-server-lifecycle.md。レポート: `docs/research/2026-05-07-warp-oz-skills-absorb-analysis.md`
- Cyril Obsidian Vault Smarter (cyrilXBT 2026-05-08) — newsletter プロモバイアス、reference only 分類 (主張 8 件棄却)。Codex 批評で副次採用 3 タスク (S 規模): /think 信念矛盾照合 step / auto-morning-briefing.sh + Hammerspoon の Daily path 07-Daily 統一 (ca82145) / thinking-context-template に Reading 欄。レポート: `docs/research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md`

---

## メンテナンス

- **ロード条件**: このファイルは常時ロードしない。`/absorb` のギャップ分析時、`/improve` の Garden フェーズ時、または過去統合の参照が必要な時に明示的に読む
- **上限**: 200行を目安。超えたら古い「初期統合」セクションを `_index_archive.md` に退避
- **連動**: MEMORY.md には `外部知見索引 → docs/research/_index.md` の1行のみ残す
