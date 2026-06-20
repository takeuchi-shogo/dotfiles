# Wiki Operations Log

> Append-only record of wiki operations. Each entry follows the format:
> `## [YYYY-MM-DD] operation | Title`
>
> Operations: `ingest` (absorb), `compile` (compile-wiki), `update` (compile-wiki update),
> `lint` (compile-wiki lint), `query` (compile-wiki query), `index` (compile-wiki index)

<!-- Parseable with: grep "^## \[" docs/wiki/log.md | tail -10 -->

## [2026-06-20] ingest-skip | Loop Engineering 2 ソース同時提示 (Matt Van Horn LinkedIn + Addy Osmani blog)

- ソース:
  - https://x.com/mvanhorn/status/2063865685558903149 (Matt Van Horn "WTF Is a Loop?" — LinkedIn Pulse mirror 経由)
  - https://addyosmani.com/blog/loop-engineering/ (Addy Osmani "Loop Engineering")
- 理由: loop-engineering / multi-agent-orchestration family、SATURATED-pure-rehash (delta=0、19/19 全手法 rehash)。**Source 2 (Addy Osmani) は同日 6 時間前に absorb 完了済の essay と同一記事**。`continue` 検証で Phase 2 全 19 Already (強化不要) 確定
- 根拠: per-method 照合台帳全 19 件 matched_prior 3 点セット完備 (詳細: `docs/research/2026-06-20-loop-engineering-double-source-absorb-analysis.md`)
- per-method 照合台帳サマリ (Source 1 + Source 2、各行に prior 名指し):
  - Source 1 全 9 手法 (5-stage lineage / Cherny loop 定義 / /loop babysit / 5 tips / Gas Town / roborev / Three hard stops / Skill-first thesis / Cron differential) → 全て `2026-06-20-loop-engineering-essay` + `2026-06-17-loops-with-claude` + `references/comprehension-debt-policy.md` + `2026-04-12-tan-thin-harness-fat-skills` + `references/resource-bounds.md` + `references/cmux-ecosystem.md` で名指し
  - Source 2 全 10 手法 (Five pieces + memory / Automations heartbeat / /goal contract / Worktrees / Skills / Plugins/Connectors / Sub-agents maker-checker / morning automation / Three sharper problems / Codex vs Claude Code mapping) → 全て `2026-06-20-loop-engineering-essay` + `references/comprehension-debt-policy.md` (Osmani 出典明記、last_reviewed 2026-04-23) + `auto-morning-briefing.sh` + `references/multi-agent-coordination-patterns.md` + `2026-04-29-codex-vs-claudecode-role-split` で名指し
- Phase 2.5: skipped (codex bash-unreachable + gemini sunset の dual-degraded、adopt=0 で議論余地なし、light-phase2 protocol)
- Validation-only: なし (stale-plan audit + crontab memo は 6 時間前 twin absorb で完了済)
- スキップ判定: per-method 照合台帳 + 同日 twin absorb 完了の double evidence

## [2026-06-20] memo | crontab 全 PAUSED (skill 更新 / nightly 移行中)

- 状態: `crontab -l` 全 entry に `[PAUSED 20260616-012634]` marker (4日経過)
- 意図: 意図的 pause、skill 更新と nightly orchestrator (`docs/plans/active/2026-06-13-nightly-orchestrator-plan.md`) 移行中のため
- resume 期限: 移行完了後 (期限未定)。期限が決まったらここを更新
- 露出元: loop-engineering family absorb (2026-06-20) の Phase 2 stale-plan audit
- 関連: `docs/plans/active/2026-05-19-pr-review-agent-plan.md` (kept-by: 2026-06-20)

## [2026-06-20] ingest-skip | From Prompting Agents to Loop Engineering (Addy Osmani 系 essay、無署名版)

- ソース: テキスト貼り付け (Addy Osmani / Steinberger / Cherny 引用、Cherny "auto + ultracode + /goal + cloud + self-verify" 5-step + crabfleet 紹介)
- 理由: loop-engineering / multi-agent-orchestration family N=15+、SATURATED-pure-rehash (delta=0)、`continue` 検証でも Phase 2 全 13 手法 Already (強化不要) 確定
- 根拠: 6/17 absorb (`2026-06-17-loops-with-claude-absorb-analysis.md`) の二次紹介 (kumai_yu/Qiita) と同系統で構造的に同一。記事末尾 "Other Useful References" が Osmani/Cherny/Steinberger を明示
- per-method 照合台帳 (delta=0 の立証、3点セット):
  - Loop 4-step (prompt/read/decide/re-prompt) → `2026-06-17-loops-with-claude` "4-step loop primitive" / Osmani 引用同定義 (rehash)
  - Five-loop progression (ReAct→AutoGPT→ralph→/loop+/goal→orchestration) → `2026-06-17-loops-with-claude` "5-stage terminology progression" / 同進化系譜 (rehash)
  - Six parts (trigger/isolation/context/tool-reach/verifier/state) → `2026-04-02-ralph-loop` + `2026-04-11-multi-agent-coordination-patterns` / 全構成要素 (cron-hooks / worktree / CLAUDE.md / MCP+gh / Codex Review Gate / docs/plans+MEMORY) 個別実装済 (rehash)
  - PR babysitter pattern → `2026-06-17-loops-with-claude` "/babysit-prs cadence example" / 同名 example (rehash)
  - /goal 4-element contract (end-state/evidence/constraints/budget) → `references/scheduling-decision-table.md:23-95` `/goal pilot` 行 + `2026-06-12-fable5-14steps` T3 採用 / 4 要素統合済 (rehash)
  - Cherny 5-step unattended → `2026-06-17-loops-with-claude` "Cherny 5-step" + `2026-06-03-dynamic-workflows` "Workflow tool deliberate non-adopt" / 全要素照合済 (rehash)
  - Multi-model role split (planner/executor/evaluator/vision) → `references/model-routing.md` Tier 表 + `2026-04-11-multi-agent-coordination-patterns` Generator-Verifier (rehash)
  - crabfleet (board/durable/child-spawn/sandbox) → `references/cmux-ecosystem.md` + `2026-05-23-cmux-coding-agent-workflow` / cmux 同型、外部 product N/A (rehash)
  - Cost = iterations not tokens → `2026-06-17-loops-with-claude` "iteration budget over token budget" / 同主張 (rehash)
  - Weak-verifier as expensive bug → `2026-05-31-hermes-eval-loop` + `verification-before-completion` skill / verifier 設計 Codex Review Gate 集約済 (rehash)
  - When-not-to-loop (one-shot/unscoped/no-check) → `references/governance-levels.md` + core_principles YAGNI (rehash)
  - 6-step "build your own" → 上記要素の reorder、新規要素なし (rehash)
  - Failure modes (verification debt/comprehension gap/silent drift) → `references/comprehension-debt-policy.md` (Osmani 出典明記 live, status: reference, last_reviewed 2026-04-23) + `silent-failure-hunter` agent (rehash)
- Validation-only follow-up 1 件: `docs/plans/active/2026-05-19-pr-review-agent-plan.md` Phase A 31 日 stall を露出 → user 判定 `kept` で frontmatter に `kept-by: 2026-06-20` 追記
- 副次観察: crontab 全 PAUSED (本 log 直前エントリ参照、別 absorb 由来でない drift)
- スキップ判定: SATURATED-pure-rehash + Phase 2 adopt=0 確定。Phase 2.5 Codex+Gemini は dual-degraded (codex bash-unreachable / gemini sunset) のため省略
- 分析レポート: `docs/research/2026-06-20-loop-engineering-essay-absorb-analysis.md`

## [2026-06-20] ingest-skip | How to get Fable-level intelligence back (model council / fusion, weeklyaiops community marketing)

- ソース: weeklyaiops.com community marketing (テキスト貼り付け、Fable 5 廃止後 council 再構築主張)
- 理由: multi-agent-orchestration family N≥15、SATURATED-pure-rehash (delta=0)、続く `continue` 検証でも Phase 2 全 Already / tools 全 N/A 確定で adopt=0
- 根拠: 全 11 手法に matched_prior 3点 (ファイル名+heading+同等性) を名指し済。Bash で `best-of-n-guide.md` Cost-Arbitrage / `multi-agent-coordination-patterns.md` Generator-Verifier+Orchestrator-Subagent / `model-routing.md` tier の実在と引用句一致を確認
- per-method 照合台帳 (delta=0 の立証):
  - Council = panel + judge synthesizer → `2026-06-18-kimi-k26-self-improving-swarm` Generator-Verifier + `best-of-n-guide.md` (rehash)
  - Frontier judge + cheap panel → `model-routing.md` Opus=judge tier + Cost-Arbitrage 節 (rehash)
  - Per-task judge tuning → `skills/review/SKILL.md` Step 0 tier (rehash)
  - Migration: council decides cheap exec → `multi-agent-coordination-patterns.md` Orchestrator-Subagent + Hermes VPS Nested Orchestrator (rehash)
  - Deep research panel + judge → `/research` + `/deep-research` (rehash)
  - Long multi-step orchestration → `2026-06-03-dynamic-workflows` Workflow tool + `/rpi` + `/epd` (rehash)
  - Briefing lighter agent → `/spec` → `/spike` → `/rpi` chain (rehash)
  - KB building (structure + fill) → `/absorb` Phase 5+ + memory-vec indexer (rehash)
  - Router ≠ Council → `2026-06-03-dynamic-workflows` で synthesis-step を council 条件として明示済 (rehash)
  - Code judge runs tests → Codex Review Gate + `/verify` + lefthook (rehash)
  - "Would I pay premium?" gut check → `model-routing.md` + `review/SKILL.md` S=light skip (rehash)
  - tools 6 種 (openrouter fusion/orcarouter/gavel/openfusion/fusion-fable/llm-consortium) → N/A (Claude-Code harness 境界外、Plus 内 per-call 切替無価値)
- スキップ判定: Phase 1.5 SATURATED-pure-rehash + Phase 2 adopt=0 確定。Phase 4-5+ (Plan / Wiki INDEX / Obsidian / MEMORY.md 追記) すべて省略
- 分析レポート: `docs/research/2026-06-20-weeklyaiops-model-council-absorb-analysis.md`
- 教訓: weeklyaiops.com community marketing は次回ベンダー検出で短絡可 (Hermes/Kimi に続く 3 系統目)。"Fable 5 廃止後の取り戻し" framing は council 系の marketing ハンドルだが council 自体は AlphaCode 時代の Generator-Verifier の言い換え、shape で家族飽和判定するので skill drift なし

## [2026-06-20] ingest | The Self-Verifying Loop: 300 agents, 4,000 steps, 5 live data feeds on autopilot with Kimi K2.6

- ソース: Kimi.ai ベンダーマーケ記事 (テキスト貼り付け、同日 2 本目の Kimi 記事)
- 判定: Gap 0 / Partial 0 / Already 9 (強化不要) / N/A 2 (vendor framing)、**採用 0**
- family: multi-agent-orchestration (N=30+ 同日午前の Khairallah で確認、本記事で +1)。**SATURATED-pure-rehash** (delta=0)
- per-method 照合台帳 (全 9 手法 rehash、`matched_prior` 3点セット名指し):
  - 1. Swarm + verify loop (Opus plans/verifies + Kimi executes) → `2026-06-18-kimi-k26-self-improving-swarm-loop` "Generator-Verifier swarm pattern" (同一ベンダー6日前 absorb)
  - 2. 300 parallel agents → 同 6/18 absorb "300-agent swarm" + multi-agent-coordination-patterns.md fan-out
  - 3. 4000 steps + 3 verify passes to zero → `2026-06-03-dynamic-workflows` "loop-until-done | Already" + completion-gate.py
  - 4. PER-COMPANY CHECKLIST が verifier rubric → review-checklists/ + Codex Review Gate 7項目 + 6/18 deterministic verifier rubric
  - 5. Reject → requeue → run until clean → best-of-n-guide.md + Workflow `loop-until-dry/loop-until-count`
  - 6. 5 live data feeds (Binance/Yahoo/WB/IMF/stock) as source-of-truth → `/deep-research` skill "fan-out web searches, fetch sources, adversarially verify claims"
  - 7. Opus 4.8 plan + Kimi K2.6 execute → references/model-routing.md Tier 表
  - 8. "Quality equals the checklist" → skill-audit + Codex Review Gate rubric + `2026-06-17-agentic-code-review` "deterministic gate"
  - 9. Citation URL resolvability + numerical tolerance → `/deep-research` "adversarially verify claims" の sub-check として内包
  - (10/11. "DeepSeek moment"/Kimi $20B/OpenRouter #1/Finance強み = N/A vendor marketing)
- user 選択: skip 推奨も continue (フル workflow) を選択 → 結論変わらず adopt 0
- Phase 2 Pass 2 強化候補 3 件全棄却: (1) `/deep-research` description は組み込み skill で本体不可視・編集不能 (2) rejection telemetry は YAGNI overkill (3) "verifier checklist=contract" 1文追加は既存 Codex Review Gate 7項目で重複
- Phase 2.5: **Codex silent exit (480s timeout で 0 byte) + Gemini sunset** の dual-degraded → Opus 自己分析で確定、台帳の `matched_prior` 3点セットで self-bias 補正の代替を立証
- 教訓: 同一ベンダー連続マーケ記事は次回 Phase 1 でベンダー検出 → reference-only 短絡 (Cyril/Hermes と同型)。組み込み skill (description のみ可視) の強化は構造的に成立しない absorb 候補から除外
- 詳細: docs/research/2026-06-20-kimi-k26-self-verifying-loop-absorb-analysis.md

## [2026-06-20] ingest (Validation-only) | SKILL.md trajectory mining for CUA (arXiv:2606.20363)

- ソース: Yuexing Hao & Xiaomin Li, "Automating SKILL.md Generation for Computer-Using Agents via Interaction Trajectory Mining", arXiv:2606.20363 (2026-06-18, cs.AI)
- 判定: Gap 0 / Partial 0 / Already 2 (強化不要) / N/A 1 (GRPO RL fine-tuning は Claude API で構造的に不可能) + 論文 diagnostic finding を Validation-only follow-up として採用
- 取り込み: 採用 0 mechanism + Validation-only 3 件 (MEMORY.md "改善ループ" academic 裏付け 1 行 / auto-triage skill に "Wave3 再開時の再注意 failure modes" 節 / docs/research/_index.md 索引)
- per-method 照合台帳 (delta=0 立証):
  - Trajectory segmentation → `2026-03-14-trajectory-informed-memory.md` "IBM Tips 自動抽出" (rehash: trajectory を意味境界で discrete unit 化する目的・粒度同一)
  - Segment clustering → `2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md` + `2026-04-02-glean-trace-learning-analysis.md` (rehash: trajectory 集約からの帰納的パターン抽出として同等。本論文は単純 clustering で弱い)
  - Skill-aware GRPO policy training → N/A (structural scope mismatch: Claude API 重み access 不可、dotfiles の `rl_advantage.py` は variant selection 用)
- 価値: 論文が **明示的 diagnostic study (negative result)** として 3 failure modes (boundary detector / orderless segment representation / offline reward model insufficient) を self-disclose。これは dotfiles の sonicgarden Wave3 YAGNI 判定 (mechanical 0/139) への独立 academic 裏付け
- Phase 2.5: skip (論文 self-disclose 済 + dotfiles 独立判定済で Codex/Gemini bias 補正余地小、ユーザー判断)
- レポート: `docs/research/2026-06-20-skillmd-trajectory-mining-absorb-analysis.md`

## [2026-06-20] ingest-skip | wtf is Loop Engineer & how to setup for real (JayZeeDesign/SuperDesignDev)

- ソース: JayZeeDesign (SuperDesignDev), テキスト貼付 + repo https://github.com/JayZeeDesign/loop-engineer-template
- 理由: topic family "loop-engineering / harness-engineering / self-improving-loop" 合算 N≥25 件目, SATURATED-pure-rehash (delta=0)
- 根拠: 直近 3 件 (2026-06-17 loops-with-claude 採用0 / 2026-06-14 opik 採用0 / 2026-06-05 sonicgarden 採用2)、family 全体採用率 <15%。3 日前の twin (kumai_yu) と同じ「inner+outer 二層 + shared artifact + global LOG」framing。vendor marketing 性 high (@SuperDesignDev プロモ + loop-engineer-template 配布)。scope mismatch: 記事は business loops (Support/SEO/Ads/Product growth) のチーム+プロダクト前提、dotfiles は単一ユーザー dev harness
- per-method 照合台帳 (delta=0 の立証 — 全 8 手法 → matched_prior 名指し):
  - inner agent loop + outer loop 二層分離 → `2026-04-02-ralph-loop-harness-engineering-analysis.md` "Ralph wayne loop" + `2026-03-23-harness-engineering-article-analysis.md` "execution vs decision 分離" + Context Constitution P3 (rehash)
  - outer loop 5 責務 (trigger/state/share/monitor/improve) → `2026-04-29-self-healing-harness-absorb-analysis.md` "CREAO 5 capabilities" + `2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md` "Issues→Routines→3段ゲート→PR" + AutoEvolve 4 層ループ (rehash)
  - 複数ループの shared artifacts による compound → `2026-04-17-hermes-fleet-shared-memory-analysis.md` "Qdrant+mem0+Stop hook" + `2026-04-04-letta-memory-as-harness-analysis.md` "memory as harness" + `patterns.jsonl` + `promoted-ledger.jsonl` (rehash)
  - artifact schema (frontmatter + type/status/sources/created_at) → `2026-06-12-fable5-14steps-absorb-analysis.md` で採用済 `references/memory-schema.md` (type=event/learning/proposal/summary + verification_status verified/hypothesis/stale/retracted) — dotfiles 側が precision 高い (rehash)
  - loop contract (domain README に goal/cadence/workflow) → `~/.claude/skills/*/SKILL.md` frontmatter (name/description/triggers/Do NOT use for) + `.config/claude/agents/*.md` description — Skill SKILL.md と完全同型 (rehash)
  - global LOG.md (cross-loop history, read latest 5-10 before major work) → `docs/wiki/log.md` (自己反映) + `docs/decommission-log.md` + `/checkpoint` RUNNING_BRIEF.md + `/recall` (contextual commit context 復元) (rehash)
  - dedupe rules (returning ID / email / frequency 増分) → `2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md` で検討済、`patterns.jsonl` の `seen` set + `promoted-ledger.jsonl` で実装 (rehash)
  - wikilink graph による artifact 間相互参照 → `MEMORY.md` `[[name]]` リンク (auto-memory) + Obsidian Vault wikilink + `references/cc-7-layer-memory-model.md` 7 層 memory model (rehash)
- 該当 family のキーワード hit: loop engineer, outer loop, inner loop, agent harness, shared artifacts, signals, loop contract, global log, compound, dedupe
- スキップ判定: Phase 1.5 gate (ユーザー確認: skip 承認、台帳全 8 行 rehash 立証)

## [2026-06-06] ingest-skip | 【完全保存版】トップ層が使うClaude Skills 72選 (東大Claude Code研究所/Buzzoni 67選 翻案)

- ソース: 東大Claude Code研究所 (note, Buzzoni "67 Skills" 420万view 記事の日本ビジネス向け翻案, テキスト貼付)
- 理由: topic family "claude-code-tips/skills-listicle" saturated-pure-rehash (N≥10, 採用率≈0%, delta=0)
- 根拠: 外部スキル 67-72個へのポインタ集。直近の純 listicle 2件 (Khairallah 40 Features="11件目"/採用0, SKILL.md 15min Guide/採用0) と同型。platform drift 露出なし (star数等は dotfiles 内検証対象外)
- per-method 照合台帳 (delta=0 の立証 — 各 current 手法 → matched_prior 名指し):
  - Skills=「一度教えたら永久に覚える」仕組み → `skill-inventory.md` (90 skills 運用中) + skills-family 全 absorb (rehash)
  - 組み合わせ workflow パック (Brainstorm→Grill→PRD 連鎖) → `skill-invocation-patterns.md` chaining 事例集 + `skill-conflict-resolution.md` (rehash)
  - メタスキル先行 (skill-creator/write-a-skill/find-skills) → `skill-creator/` skill + `skill-audit/` + Tan absorb `skill-writing-principles.md` (rehash)
  - Grill Me (敵対的質問インタビュー) → `grill-interview/` skill + Codex Spec/Plan Gate (rehash)
  - Doc Co-Authoring 別セッション読者テスト=役割分担ハーネス → multi-agent review (codex-reviewer+code-reviewer 並列)。記事自身が「ハーネスに近い」と認める (rehash)
  - 非公式スキル無闇導入のセキュリティリスク → `agentic_security_insights.md` + `mcp-audit.py` + skills-lock.json vetting (rehash)
  - Edit Article (240字/段落・依存グラフ再構成) → N/A 文脈不一致: 外部skill install推奨であり harness提案でない。執筆経路は digest+obsidian+`concise.md` でカバー
- 該当 family のキーワード hit: skills, listicle, 72選, skill-creator, find-skills, workflow pack
- スキップ判定: Phase 1.5 gate (ユーザー確認: skip 推奨を承認)

## [2026-06-05] ingest-skip | How to Run 300 AI Agents From One Prompt (10 Workflows Most People Skip)

- ソース: Kimi K2.6 agent swarm 啓蒙記事 (vendor-biased, テキスト貼付)
- 理由: topic family "multi-agent-orchestration" saturated-borderline (N>>3, delta=1, 唯一の delta は repo bookmark で adoption path なし → 実質 pure-rehash)
- 根拠: 既存2件のほぼ完全な再パッケージ — `2026-05-30-single-threaded-300-agents` (同一タイトル "Commanding 300 Agents", 採用0) + `2026-04-30-three-model-stack` (同一三モデルルーティング+同一ベンチ数値 SWE80.2/BrowseComp90.1/OSWorld78.7, 採用1=R-005 watch行 既実装)
- per-method 照合台帳 (10手法中9件 pure rehash, 名指し済み):
  - 1. Fan-out parallelism → `single-threaded-300-agents` 手法1 Orchestrator + Workflow tool (fan-out/parallel/pipeline) (rehash)
  - 2. Coordinator/sub-agent/validator 3-prompt → `three-model-stack` 手法6 Three-prompt 三役分け (N/A 済) + absorb Phase 2.5 tri-judge (rehash)
  - 3. Model routing per layer (Opus/K2.6/GPT-5.5) → `three-model-stack` 手法1 → `model-routing.md` 5層 carve-out (rehash)
  - 4. Skills as reusable templates → `three-model-stack` 手法7 Document-to-Skill (N/A, skill-creator 代替) (rehash)
  - 5. Cost math / 8x cheaper → `three-model-stack` 手法11 Cost-as-PrimaryDriver (N/A, End-to-End>Per-Call 原則) (rehash)
  - 6. Job-shape triage / honest caveats → `single-threaded-300-agents` 手法9+14 → Task Parallelizability Gate (rehash)
  - 7. Kimi K2.6 native 300-agent swarm → `three-model-stack` 手法5 (N/A, agency-safety blast radius) + R-005 watch行 (rehash)
  - 8. claude-code-router / LangGraph / crewAI / autogen → `three-model-stack` 手法9 Claude Code Router (N/A, direct CLI 路線) (rehash)
  - 9. 10 workflow recipes → fan-out application 集, dispatch skill + Workflow examples (rehash)
  - 10. system_prompts_leaks repo を研究する angle → **ambiguous** (名指し prior なし, ただし手法でなく bookmark で adoption path なし)
- 該当 family のキーワード hit: multi-agent / parallel agent / orchestration / swarm / fan-out / model-routing / kimi
- スキップ判定: Phase 1.5 gate (ユーザー選択: skip 推奨)

## [2026-06-04] ingest-skip | I Tested Every Claude Code Feature, These 12 Are the Best (500h Tier List)

- ソース: Claude Code feature tier list (knowledge-work/automation 視点, D→S, テキスト貼付)
- 理由: topic family "claude-code-tips" saturated-pure-rehash (N≈16, 採用率 <20%, delta=0)
- 根拠: 全機能が既存マッピングで決着 — Already 採用済 (CLAUDE.md / Skills / Subagents / worktrees / **status line=statusline.sh+settings.json:775** / auto memory / /loop / ultra review / themes / hooks / effort levels / agent teams / /clear /compact) / Native 機能で dotfiles 作業不要 (/goal / ultraplan / /insights / /rewind / routines→/schedule / recap / /btw / voice / charts / desktop app / dispatch) / dynamic workflows は **deliberate non-adopt 維持** (memory 記録: opt-in gated で redundant) / Cowork・M365・Chrome・Google Workspace CLI は著者固有スタックで N/A。唯一の drift 候補 status line (#2「最も過小評価」) も既設定で delta=0
- 該当 family のキーワード hit: every feature, tier list, best, claude code features, status line, skills
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, skip 推奨 → user 承認)

## [2026-06-03] ingest-skip | Claude Code + NotebookLM + Obsidian: 2 Weeks → 6 Minutes, $200/hr → $0

- ソース: creator-monetization listicle (3-tool stack pitch, テキスト貼付)
- 理由: topic family "obsidian-second-brain" saturated-pure-rehash (N=16+, delta=0)
- 根拠: 中核手法は全て過去 absorb 済み — NotebookLM CLI 化 (notebooklm-py) は **2回明示却下** (2026-03-16-notebooklm-obsidian-claude-integration + 2026-04-10-notebooklm-claude-extend-sessions、理由: 非公式 API = Google 内部プロトコル reverse-engineering を production harness に入れるのは blocker 級リスク) / Vault-as-context-layer 主張は「Vault は memory→Vault 単方向同期スナップショットで AI reasoning input ではない」MEMORY 核心訂正と矛盾 / Skill Creator・pipeline は skill-creator + /research + /digest + /absorb で既存カバー
- 該当 family のキーワード hit: obsidian, notebooklm, vault, claude.md compounding, second brain
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, skip 推奨 → user 承認)
- フォローアップ: user は記事 absorb とは別軸で notebooklm-py の実地検証を希望 → 別途 /spike (worktree 隔離・非公式 API リスク承知の実験、production harness 非統合)

## [2026-06-03] ingest | 私の最強のMac開発環境 2026: Nixとmiseで育てる (tyPhoon)

- ソース: https://qiita.com/tyPhoon/items/f1855ff508f4268df5b5
- topic family: nix-mise-dotfiles-environment (新分野 N=1, PASS)
- 判定: Already 多数 (Nix土台/Homebrew GUI/役割分担思想/AeroSpace/borders/Ghostty/Yazi/Karabiner/jj/direnv/zoxide/bat/eza/starship), Gap中核 1 (mise でランタイム管理), Gap小 2 (carapace/espanso), N/A 4 (Nixvim化/core分離/Nushell/Zellij)
- 取り込み: **mise 言語ランタイム集約** (`.config/mise/config.toml` 新規 + nix home.packages から uv 移管)。検証済: node 24LTS/go 1.25.4 arm64/python 3.13.6/uv 0.9.7 arm64 が mise グローバル有効化、PATH 優先
- 重大発見: 記事アーキテクチャは大半 Already (Phase B2)。真の Gap は「mise にツール install 済だがグローバル config に [tools] 無く有効化ゼロ + 野良 brew で go=Rosetta 等散在」。Codex は launch-worker.sh:134 `-q` バグで失敗 → Gemini+自己分析で代替
- 残課題: nix:switch は .cursor/.codex の clobber(自己書き換えアプリ drift, 本変更と無関係)でブロック → 別タスク。手動 symlink で mise は有効
- レポート: docs/research/2026-06-02-typhoon-nix-mise-absorb-analysis.md

## [2026-06-01] ingest-skip | Opus 4.8: same price, you pay double

- ソース: "Opus 4.8: same price, you pay double" (Telegram-promo listicle, t.me/+JmDeelv5UCwwMTcy)
- 理由: topic family "claude-code-tips" saturated-pure-rehash (N=20+, delta=0)
- 根拠: 2026-05-30 `opus48-setup-guide` absorb (status:implemented) で本記事の全論点を処理済み — effort control=Already (effortLevel:"xhigh" settings.json:822 + Stage別 reasoning budget) / fast mode 用途指針=Gap 採用済 (resource-bounds.md) / dynamic workflows=Already (Workflow tool + cmux) / settings.json テンプレ=N/A / benchmark 数値・"route effort per task" thesis=N/A (マーケ主張)。drift 検証 (debug-thinking-summary / qualitative-signals-spec / agent-sdk-credit) も 2026-05-30 に完了。新 framing なし
- 該当 family のキーワード hit: claude code, opus 4.8, effort control, fast mode, dynamic workflow
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, skip 推奨 → user 承認)

## [2026-05-31] ingest-skip (light Phase 2, adopt=0) + validation-only 1 | @damidefi Delete 90% of Your Obsidian Notes

- ソース: テキスト貼り付け (@damidefi, X creator, follower 100K 目標 + Bookmark/Share 誘導)
- 判定: topic family "obsidian-second-brain" SATURATED-but-novel (N=17, delta≈2) → light-phase2。記事 vault tactic 採用 **0 件** (全 Already/Partial + 前提不一致: Vault は memory→Vault 単方向同期で AI reasoning input ではない)
- validation-only 1 件実施: 記事の signal-density lens で MEMORY.md bloat 検出 (223行/48K > 閾値 180行/23KB) → archive-before-delete 適用で外部知見索引 79 行を `memory/archive/2026-05.md` に退避 + family 横断教訓 12 行に圧縮。**MEMORY.md 223→154行/16K** (`MEMORY.md.bak-2026-05-31` バックアップ済)
- 副次検出: `memory-archive.py` のロジック不整合 (「ファイル順=古さ」前提で前半コア知識を archive する逆効果) を実行前シミュレーションで発見し盲目実行を中止。pruning mechanism 群 (memory-archive/eviction/dead-weight-scan/doc-status-audit) は全て disconnected → 別タスク候補
- レポート: docs/research/2026-05-31-damidefi-delete-90-vault-absorb-analysis.md
- MEMORY.md 索引: 外部知見索引圧縮で family 教訓に反映済 (obsidian N=16→17)

## [2026-05-31] ingest-skip | How to Build Your First Claude Code Subagent in 15 Minutes (5 templates)

- ソース: テキスト貼り付け (beginner tutorial / creator listicle: "5 ready-to-use templates", "Thanks for reading!")
- 理由: topic family "subagent/agent-template" SATURATED-pure-rehash (N≥3: 30-subagents 2026-05-02 / Multi-Agent Coordination 2026-04-10 / PostHog Agent-First / Claude Agent Teams 7steps 2026-05-25 / Anthropic Token Savings 2026-05-22 / opus48 setup 2026-05-30、delta=0)
- 根拠 (Step 3.5 delta=0 evidence): 記事7手法すべて Already かつ既存上位互換 —
  - 5テンプレートは全て既存 agents の上位互換: reviewer→`code-reviewer.md`(29.3K) / test-writer→`test-engineer.md` / doc-writer→`document-factory.md`+`doc-gardener.md` / security→`security-reviewer.md`(17.1K) / pr-writer→`github-pr` skill + `pull-request` command
  - subagent anatomy (frontmatter) → `references/agent-config-standard.md` 既存
  - `CLAUDE_CODE_SUBAGENT_MODEL` → 2回 N/A 判定済 (2026-05-25 / 2026-05-30、Opus 1M lock-in + per-agent frontmatter model 指定)
  - description=trigger / tools 制限 / 呼び出し3方式 / 配置場所 → 全て既存22 agents で実践済 + `subagent-delegation-guide.md`(72.5K) でカバー
- 該当 family のキーワード hit: subagent, agent template, code reviewer, test writer, doc writer, security scanner, CLAUDE_CODE_SUBAGENT_MODEL
- スキップ判定: Phase 1.5 gate (ユーザー選択 skip)。MEMORY.md 索引追記なし、Phase 5.5-5.7 実行なし

## [2026-05-31] ingest (light Phase 2, adopt=1 S) | 32 Claude Code hacks (movez.substack)

- ソース: "32 Claude Code hacks that take you from beginner to PRO" (movez.substack.com, creator-monetization listicle)
- 判定: topic family "claude-code-tips" SATURATED-but-novel (N=8+, delta=2) → light-phase2
- hacks 01-30 = Already (過去 family レポート + 既存 harness で照合済)、novel 2 件のみ Phase 2 検証
- novel 2 件: hack 31 Dynamic Workflows (Gap だが deliberate non-adopt: tool desc 注入 + opt-in gated) / **hack 32 /effort ultracode = Partial→Adopt (S)**
- 採用 1 件: `references/workflow-guide.md` の Effort Level テーブルに `ultracode` (xhigh) 行 + session-scoped 注記を追記 (新 tier 出荷で表が stale だったため鮮度維持)
- grounding: ultracode 挙動は低信頼記事ではなく注入済み Workflow tool description を一次情報源とした
- 隣接観測 (未編集): `workflow-guide.md:724` "max は Opus 4.6 専用" は現行 4.8 で stale 疑い → model-version drift audit 候補
- meta: 調査中 `model-routing.md` 等を表示欠落で「未検出」と誤記録 → 実在確認し撤回 (honesty 原則)
- レポート: docs/research/2026-05-31-32-claude-code-hacks-absorb-analysis.md

## [2026-05-27] ingest-skip (light Phase 2, adopt=0) | How to Build a Software Factory with Claude Code (Sai Rahul / @sairahul1)

- ソース: テキスト貼り付け (creator-monetization framing: Follow @sairahul1, "save months" hype, listicle)
- 判定: light-phase2 で 10 手法 → Already 8 / N/A 2 = **採用 0 件** (Phase 2 まで検証したが novel 候補 2 件 (Backend/Frontend folder scoping, Backend→Frontend API summary handoff) 両者とも N/A 判定)
- Family: 「multi-agent orchestration / role-split」 (informal、registered taxonomy 未登録だが同分野 30+ 件 absorb 済で functional saturation)、saturation-by-spirit (formal PASS) → ユーザー light-phase2 選択
- 直近 baseline: 2026-05-02 30-subagents (採用 4) / 2026-05-04 Distribution vs Escalation (Bundle 採用) / 2026-04-11 Multi-Agent Coordination (5-pattern view)
- novel 候補 2 件の判定根拠:
  - N1 (folder scoping): dotfiles は 23 agent を「機能で分離」運用、path 競合シナリオが定型化されていない YAGNI。30-subagents absorb 時にも同判断
  - N2 (API summary handoff): `agents/backend-architect.md:44-51` で「API endpoint definitions」出力 spec 化済 + cross-file-reviewer が事後整合性検出担当、handoff document 化は single-session-sequential スタイルとミスマッチ
- スキップ判定: Phase 1.5 gate saturation-by-spirit → ユーザー選択で light-phase2 → adopt 0 確定で ingest-skip 同等扱い
- レポート: `docs/research/2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md` (status: light-phase2-only)
- Meta-finding: 「multi-agent orchestration / role-split」family を `references/topic-family-saturation.md` に追加候補 (30+ 件累積実績、creator-monetization listicle が 3 週間以内に再投入される popularization velocity)

## [2026-05-25] ingest (light Phase 2, adopt=2 S) | How to Organize Your Obsidian Vault So You Can Always Find What You Need (cyrilXBT)

- ソース: テキスト貼り付け (@cyrilXBT, follow @cyrilXBT 誘導つき full course 形式)
- 判定: light-phase2 で 12 手法 → Already 9 / **Gap 1.5 (採用 2)** / N/A 2 = **採用 2 件 S**
- Family: obsidian-second-brain (N=15 件目, Cyril 著者 5 件目)、SATURATED-borderline (delta=1)、ユーザー light-phase2 選択
- 採用: T1 axis 2 + axis 4 → `vault-maintenance.sh` に `check_rare_tags()` + `check_naming_compliance()` 追加、cron 週次に統合 (RARE_TAG_THRESHOLD=5)
- 検証: dotfiles vault dry-run で 354 タグ集計 → rare tag 多数検出 (governance/google-engineering/skill-design 等 1-4x)、命名違反 0 件 (vault well-organized 確認)、bash -n syntax OK
- 棄却 (10 件): 8-folder PARA/YYYY-MM-DD-TYPE 命名/universal frontmatter/3-category tag prefix/MOC/3 search modes/Filesystem MCP/Progressive Reorganization plan/Retrieval-First Principle/Inbox 3-question rubric (全て既決 Already or 2026-05-22 で明示 Reject)
- メタ: Cyril 5 件目で初の「small but real adopt」(過去 4 件 adopt 3→2→1→0 の漸減トレンドが反転)、delta=1 が真の novel になる珍しい事例。サンドボックス制約 (root-find Operation not permitted) 検出で subdir 走査パターンに refactor
- レポート: `docs/research/2026-05-25-cyrilxbt-organize-vault-absorb-analysis.md`

## [2026-05-25] ingest (light Phase 2 + Codex correction, adopt=1 S) | How to Build a Claude Agent Team in 7 Steps (Twitter listicle, unattributed)

- ソース: テキスト貼り付け (anonymous Twitter promotional listicle, モデル ID `claude-sonnet-4-5-20250929` から 2025-Q4 派生疑い)
- 判定: light-phase2 で 12 主張 → Already 5 / **Partial 1 (採用)** / N/A 4 / misnamed 1 / anecdotal 1 = **採用 1 件 S**
- Family: claude-code-tips listicle (N=8 件目) + agent-orchestration (N=6 件目) hybrid、SATURATED-but-novel (delta=5 fabrication 高リスク)
- WebSearch grounding (5 並列): 5 つの env/CLI 主張 (AGENT_TEAMS / Agent View / `--max-budget-usd` / SUBAGENT_MODEL / DISABLE_ADAPTIVE_THINKING) **すべて公式実在を確認**、`CLAUDE_CODE_DEFAULT_EFFORT` のみ **misnamed** (正式: `CLAUDE_CODE_EFFORT_LEVEL`)
- dotfiles 既決内訳: AGENT_TEAMS=settings.json:4 設定済 / SUBAGENT_MODEL=Opus 1M lock-in で N/A / EFFORT=settings.json:815 `effortLevel: "xhigh"` 採用済 / DISABLE_ADAPTIVE_THINKING=Opus 4.7 no-op で 2026-05-19 意図的除外 / `--max-budget-usd`=2026-05-10 absorb で「CI 自動化なし → スキップ」決定済
- **採用 (Codex 批評で訂正)**: #5 `claude agents` Agent View を当初「cmux で上位互換」と判定したが Confirmation bias と Codex 指摘 → `references/subagent-vs-cmux-worker.md` に **Agent View (session dashboard) / Agent Teams (peer messaging) / cmux (process-level multi-model)** の 3 レイヤー境界注記追加 (S 規模)
- Phase 2.5 省略の代償を Codex 単独批評で補填 (cmux Worker spawn 失敗 → `codex exec --sandbox read-only -m gpt-5.5` fallback、Q1 のみ採用、Q2-Q4 不要)
- レポート: `docs/research/2026-05-25-claude-agent-teams-7steps-absorb-analysis.md`

## [2026-05-22] ingest-skip | 11 Claude things I wish someone had told me 12 months ago (anonymous)

- ソース: テキスト貼り付け (anonymous "Based on conversations and workflows shared by advanced Claude users")
- 理由: topic family "claude-tips-generic" 飽和 (12 件目相当)
- 過去同系列: Boris 30 Tips / 12-rule CLAUDE.md / zodchixquant 15 Settings / 9 Overnight Agents / SKILL.md 15min / Khairallah Power User (Reject/Reference Only 中心)
- 内容: 11 項目 (Projects / CLAUDE.md / Custom styles / Sonnet default / Haiku / Voice mode / Subagents / Skills>prompts / Memory / Distrust outputs / Systems-not-prompts) すべて dotfiles 実装済
  - CLAUDE.md 130行 + references + MEMORY.md = operating manual 完備
  - model-routing.md (Haiku/Sonnet/Opus 役割分担済), persona/output-mode skills
  - 50+ subagents + 100+ skills + memory-schema with retention
  - silent-failure-hunter + verification-before-completion + Codex Review Gate
  - "skeptical senior engineer" は code-reviewer/codex-reviewer agents + /challenge skill で実装済
- 一次評価: 11 手法すべて Already で新規取り込み価値ゼロ
- スキップ判定: Phase 1.5 gate (anonymous source + listicle format + 全項目 dotfiles 既知パターン)

## [2026-05-22] ingest (light Phase 2) | One-Folder Obsidian System (cyrilXBT)

- ソース: テキスト貼り付け (記事末尾 "Follow @cyrilXBT")
- 分析: docs/research/2026-05-22-cyril-one-folder-absorb-analysis.md (light Phase 2 only, Phase 2.5 omitted by user direction)
- 経緯: 初回 Phase 1.5 で SATURATED → skip 判定 → user 指摘 (「手を抜いて改善回さなかった？」) で短絡を撤回、2 novel point だけ救済分析
- 過去 cyril 系: Claude-only Stack (04-11) / Vault Smarter (05-08, 副次 3 採用) / Dashboard (05-19, 副次 2 採用) / Personal OS (05-21, 短絡で 0 採用) / 今回 (短絡から救済、1 採用)
- 判定: A1 one-folder 採用 Reject / **A2 anti-vision 記録 Adopt** / B1 auto router YAGNI Reject / B2 専用 capture N/A
- 取り込み: `templates/obsidian-vault/CLAUDE.md` に "Design Rationale (IPARAG vs One-Folder)" セクション追加 (~15 行、Filing decision/PARA actionability/Galaxy namespace/chronological alt/file system performance 5 根拠)
- 効果: 5 本目以降の同種主張に対する Phase 1.5 saturation gate を強化 (再検討不要根拠の文書化)
- 反省: 3 本目 Personal OS で分析省略を始め、4 本目で skip 直結 → user 指摘で救済。**saturation gate は新規論点の有無を verify せず即時 skip すると false-skip を生む**

## [2026-05-22] ingest-skip | How to Become a Claude Power User for FREE (Khairallah)

- ソース: Twitter/Threads 配布記事 (テキスト貼り付け, @eng_khairallah1)
- 理由: 飽和カテゴリ "claude-code-tips/general-setup-promo" 系の 8 件目相当 (採用率 ~0%)
- 根拠: 過去 7 件累積 — Boris 30 Tips / 12-rule CLAUDE.md / zodchixquant 15 Settings / Three-Model Stack / Cyril x3 (Reference Only or Reject 中心)
- 一次評価: 14 手法すべて Already 10 / Partial 1 / N/A 3 で新規取り込み価値ゼロ
- Web UI 中心 (Projects, Memory, Cowork) で Claude Code CLI ユーザーには適用不能
- Khairallah Routines (2026-05-14) で同著者は既 absorb 済 (4 件採用)
- スキップ判定: Phase 1.5 gate (family taxonomy 厳格マッチ外だが、テーマと採用率パターンが完全一致)

## [2026-04-24] ingest | Deep Researcher (Onyx+CrewAI+Voxtral) by Akshay Pachaar

- ソース: 記事 (Onyx + CrewAI + Voxtral 設計原則)
- 分析: docs/research/2026-04-24-deep-researcher-absorb-analysis.md
- 判定: Partial 6, Already 3 強化, N/A 2
- 取り込み:
  - research/SKILL.md: Query Variant Axis / on-demand reflection+LLM selection / citation merge / thoroughness philosophy
  - absorb/SKILL.md: thoroughness philosophy
  - subagent-delegation-guide.md: Plan-only 契約 / Deep Frying anti-pattern

## [2026-04-20] ingest | Andrej Karpathy Skills

- ソース: https://github.com/forrestchang/andrej-karpathy-skills/tree/main
- 判定: Gap 4, Already (強化不要) 3, Already (強化可能) 1
- 取り込み: A CURSOR.md 配布 contract 修正 + global.mdc に 4 原則, B PLANS.md Success Criteria required, C AGENTS.md / .codex/AGENTS.md に Karpathy ポインタ, D Hook Philosophy ADR (0006)
- 分析: docs/research/2026-04-20-karpathy-skills-absorb-analysis.md
- プラン: docs/plans/active/2026-04-20-karpathy-absorb-plan.md

## [2026-04-19] ingest | Empirical Prompt Tuning (mizchi)

- ソース: https://github.com/mizchi/chezmoi-dotfiles/blob/main/dot_claude/skills/empirical-prompt-tuning/SKILL.md
- 判定: Gap 1, Partial 2, Already 強化 2, 棄却 1
- 取り込み: T1 tool_uses+qualitative_signals 接続, T2 Convergence holdout+evaluator drift, T3 spec scenarios, T4 blind memory分離+異モデル契約
- 分析: docs/research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md
- プラン: docs/plans/active/2026-04-19-empirical-prompt-tuning-plan.md

## [2026-04-19] ingest | Harnesses are everything

- ソース: Baseten blog (unverified) 記事、元記事タイトル "Harnesses are everything. Here's how to optimize yours."
- 判定: Gap 1 (総量 instruction budget 指標), Partial 3 (Human-written/CLI-discovery/Harness Commit), Already 5 (Skills PD, R.P.I, MCP 選別, Parallel fan-out, Sequential pipeline)
- 取り込み: 6 タスク全採択 (Q1 Harness Commit 弱化, Q2 Human-written 方針, Q3 CLI PD, M1 instruction budget 計測, M2 dead-weight scan, L1 reviewer calibration)
- 実装完了: Wave 1-3 全て完了、後処理中

## [2026-04-19] ingest | Top 67 Claude Skills (polydao)

- ソース: X/Twitter 経由の polydao 記事 "Top 67 Claude Skills That Turn a $20 Subscription Into a Full Dev Team"
- 判定: 34 Already / 8 Partial / 2 Gap / 23 N/A
- 取り込み:
  - `ubiquitous-language` skill 新規 (DDD glossary 抽出・語彙 drift 検出)
  - `dependency-auditor` skill 新規 (npm/go/cargo/pip 横断の supply chain lens)
  - `spec` skill に Phase 0 PRD Quick Interview 追加 (6項目、Standard Mode 軽量版)
- 却下: Change Log Generator (/commit で代替), API Doc Generator (Context7+PRD で代替), 他 21件 N/A
- Pruning-First: skill 数 93 → 95 (+2)。IFScale 制約を遵守
- 分析レポート: docs/research/2026-04-19-top67-claude-skills-analysis.md
- 統合プラン: docs/plans/pending/2026-04-19-top67-skills-integration-plan.md

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

## [2026-04-27] ingest | Keep your Claude Code context clean with Subagents (aitmpl 系記事)

- ソース: aitmpl 系記事「Keep your Claude Code context clean with Subagents」(URL 不明)
- 判定: Gap 0個（修正後 N/A 2個）, Partial 1個 (context-timeline)→独自強化, Already 4個 (うち2個強化可能), N/A 2個 (CLAUDE_CODE_FORK_SUBAGENT/, /fork)
- 取り込み: 3件 (T2 context-monitor.py に subagent event timeline 追加 / T3 observability-signals.md に triage-router 命中率・Plan 差し戻し率・cache hit rate 追記 / T4 references/fork-experiment.md に /fork 限定実験ガイド)
- 棄却: aitmpl context-timeline 直採用 (第三者テンプレート), CLAUDE_CODE_FORK_SUBAGENT=1 デフォルト採用 (experimental + cleanliness 哲学と矛盾)
- レポート: docs/research/2026-04-27-subagent-context-fork-absorb-analysis.md
- 実装: 新セッションで /rpi 経由 (M 規模)
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

## [2026-04-14] ingest | CREAO "Why Your AI-First Strategy Is Probably Wrong"

- ソース: CREAO CTO 記事 (公開検索で未特定, text で提供)
- 判定: exists 0, partial 15, not_found 2 (Phase 2.5 Refine 後。初回 exists 5 → すべて partial に修正)
- 取り込み: A1 (observability action loop) + A2 (review 責務ドメイン並列) + A3 (SOP 昇格基準) + B1 (pre-mortem checklist) + B3 (CLAUDE.md 4 原理)
- 棄却: 自動チケット化、常時 3 Opus、自動 rollback、no manual override (Codex 害判定)
- プラン: docs/plans/2026-04-14-creao-absorb-plan.md

## [2026-04-14] ingest | Hermes as a personal analyst (3 weeks)

- ソース: 個人ブログ記事 (PE/VC/IB 出身者、匿名)
- 判定: Gap 小 1 / Partial 0 / Already 強化不要 5 / Already 強化可能 2 / N/A 2
- 取り込み:
  - [実装] auto-morning-briefing.sh に Hacker News + arXiv + 任意 RSS 統合 (SSRF validation + prompt injection hardening 付き)
  - [実装] mcp-skill-hint.py PostToolUse hook 新規 (`.claude.json` / `.mcp.json` の mcpServers 追加検知で /skill-creator 起動ヒント)
  - [spike] 月次コストダッシュボード feasibility 調査 (Claude/Codex JSONL は feasible、Gemini blind) → 別 plan 化
- Phase 2.5 補正: #2 Daily Briefing Automation を Codex search で auto-morning-briefing.sh 発見により N/A → Already 強化可能に修正
- Codex 批評: Stream idle timeout したが search phase で auto-morning-briefing.sh 発見が決定打
- Review: 2 回実施 (初回 NEEDS_FIX → SSRF + arXiv HTML + keyword false positive + 絵文字 + prompt injection 修正 → PASS)
- 分析レポート: `docs/research/2026-04-14-hermes-personal-analyst-analysis.md`

## [2026-04-14] ingest | Kevin's "My Second Brain Setup: A Modified Karpathy Method"

- ソース: Kevin article (pasted text, no canonical URL)
- 判定: Gap 4, Partial 3, Already 2 (Phase 2.5 後)
- 取り込み: A-alt (directory separation `_drafts/`), B1 (lint citation check), B3 (query depth), B4 (research angles preset)
- 棄却: A1/A2 frontmatter (Gemini 推奨でディレクトリ分離へ), B2 重み付け (過剰複雑), C 3 sub-folders (N/A)
- プラン: docs/plans/2026-04-14-karpathy-second-brain-absorb-plan.md
- レポート: docs/research/2026-04-14-karpathy-second-brain-modified-analysis.md

## [2026-04-17] ingest | Hermes Fleet Zero To Hero

- ソース: "Building a Hermes Fleet Zero To Hero! Reproducing Moshe's Self-Hosted Agent Stack"（週末ブログ、Moshe Hermes 再現）
- 判定: Gap 3, Partial 3, Already 4, N/A 1
- 取り込み: (1) JSONL secret 監査 (2) Redactor を Stop hook に統合 (3) Memory schema/retention 策定 (4) Semantic search 小実験
- プラン: docs/plans/2026-04-17-hermes-absorb-plan.md

## [2026-04-17] ingest | Using Claude Code: Session Management & 1M Context

- ソース: https://claude.com/blog/using-claude-code-session-management-and-1m-context
- 判定: Gap 3件（Rewind workflow, Task boundary grey area, Turn Decision Table）, Partial 0件, Already 4件（Context Rot threshold, Proactive Compaction, Clear Session, Subagent Delegation — すべて強化可能）, N/A 0件
- 取り込み: workflow-guide.md に Every Turn Branching Point + Task Boundary Grey Area セクション追加 / session-protocol.md に Compact vs Clear Decision Matrix / compact-instructions.md に Steering Compact / subagent-delegation-guide.md に Mental Test / context-constitution.md に 300-400k task-dependent threshold
- 分析レポート: docs/research/2026-04-17-claude-code-session-mgmt-analysis.md

## [2026-04-17] ingest | 組織的なAI活用を阻む最大のハードルはコンテキストデザインだった

- ソース: https://speakerdeck.com/ixbox/zu-zhi-de-naaihuo-yong-wozu-mu-zui-da-nohadoruha-kontekisutodezaindatuta (久保星哉/i3design)
- 判定: Gap 2個 (Connector drift, Hook 陳腐化), Partial 4個 (Skill version lock, Telemetry 品質, 予算管理, MCP 非依存性), Already 6個 (うち強化可能 4個)
- 取り込み: 全10タスク採用。P1=Connector inventory+Telemetry 品質、P2=cwd-aware profile+Hook 条件付き実行、P3=MCP 台帳+金額予算+skill-local lock、P4=skill dashboard+smoke-test+tacit→rule trace
- 分析: docs/research/2026-04-17-context-design-absorb-analysis.md
- プラン: docs/plans/2026-04-17-context-design-absorb-plan.md
- Phase 2.5 貢献: Codex=Context Infrastructure 層の見落とし指摘・優先度並び替え, Gemini=Context Ops 業界事例・Hook 陳腐化リスク指摘

## [2026-04-17] ingest | How to fix your life in 1 prompt (Dan Koe風 心理監査プロトコル)

- ソース: ユーザー貼り付けテキスト（Dan Koe 風コミュニティ記事）
- 判定: Gap 7個, Partial 4個, Already強化可能 3個, N/A 1個
- 取り込み (最小採択セット):
  - Anti-vision → `memory/telos_strategies.md` に「やらないことリスト」節追加
  - 3 daily non-negotiables → `/timekeeper plan` に Q0 追加
  - Midday check → `/timekeeper midday` モード新設
  - Horizon 5 life 質問 → `/weekly-review` Phase 5.5 追加
- 棄却: 9-domain audit 全体、Identity declaration、Psychological excavation、Root pattern naming、Push on comfort の agent 化
- 根拠: Codex + Gemini 並列批評（Insight abandonment 75%, performative audit trap, Ashcroft End-gaining, Ehrenreich 批判）
- 分析レポート: [2026-04-17-life-audit-protocol-absorb.md](../research/2026-04-17-life-audit-protocol-absorb.md)

## [2026-04-19] ingest | Manage agent skills with GitHub CLI (gh skill)

- ソース: https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/
- 判定: Gap 3, Partial 3, Low-priority 2, N/A 1 (Already 強化可能 3)
- 取り込み: P1 (lockfile provenance, 外部 drift 検知) + P2 (origin: frontmatter, symlink platforms:) + P3 (rollback, gh skill wrapper, hash 検証)。全 7 タスク採用、L 規模
- 戦略: Partial Adopt。539 スキル一括移行せず、外部由来・共有スキルに絞る (Codex 批評反映)
- 分析レポート: [2026-04-19-gh-skill-cli-analysis.md](../research/2026-04-19-gh-skill-cli-analysis.md)
- 統合プラン: [2026-04-19-gh-skill-absorb-plan.md](../plans/2026-04-19-gh-skill-absorb-plan.md)

## [2026-04-19] ingest | Top 67 Claude Skills (polydao)

- ソース: X/Twitter 記事「Top 67 Claude Skills That Turn a $20 Subscription Into a Full Dev Team」
- 判定: 34 Already / 8 Partial / 2 Gap / 23 N/A
- 取り込み: ubiquitous-language skill 新規、dependency-auditor skill 新規、spec skill に PRD interview phase 強化。M 規模、新セッションで `/rpi` 実行予定
- 却下: Change Log Generator (Codex 批評: /commit で代替)、API Doc Generator (Context7 + PRD で代替)、他 21 件 (Office/マーケ/メディア系は用途外)
- 戦略: Pruning-First。93 skills → 95 に限定、記事のマーケティング文脈 (67 全部入れろ) に踊らされない
- 分析レポート: [2026-04-19-top67-claude-skills-analysis.md](../research/2026-04-19-top67-claude-skills-analysis.md)
- 統合プラン: [2026-04-19-top67-skills-integration-plan.md](../plans/pending/2026-04-19-top67-skills-integration-plan.md)

## [2026-04-21] ingest | Harness Pipeline BAN article

- Source: "How I got banned from GitHub due to my harness pipeline" (user-pasted text, no URL)
- Analysis: docs/research/2026-04-21-harness-pipeline-absorb-analysis.md
- Plan: docs/plans/active/2026-04-21-harness-pipeline-absorb-plan.md
- Judgment: Gap 2 (低優先), Partial 5, Already 6 (1 reclassified to Partial per Codex), N/A 2
- Accepted: 7 tasks — fix-issue reproduce-first (P1), resume anchor contract (B), plan→implement bridge hook (C), model-routing end-to-end principle (D+#12), MCP state guidance (#2), load-bearing (#8)
- Rejected: 13-stage full copy, GitHub mass PR automation, git-push velocity hook, CLA flow, expert amplification codification (Stanford HAI 2026 contradicts)
- Key translation: "attestation is scarce" → "reproduce-first attestation before polish"

## [2026-04-23] ingest | AGENTS.md Patterns (Augment/Zhenylenko)

- ソース: "A good AGENTS.md is a model upgrade. A bad one is worse than no docs at all." by Slava Zhenylenko (Augment)
- 判定: Gap 3 (search-result sprawl, token-based size limit, stale doc retirement), Partial 2 (pair don't/do, real code examples), Already 4 (progressive disclosure, procedural workflows, decision tables, reference limit)
- 棄却: module-level AGENTS.md 追加 (Codex 批評: sprawl 増大で逆効果)
- 取り込み: 7 タスク採択 (P1 search-result sprawl 監査 + AGENTS.md 圧縮 / P2 don't+do 強化 + stale doc retirement / P3 token size limit + workflow playbooks + decision-tables-index)
- レポート: docs/research/2026-04-23-agents-md-patterns-absorb-analysis.md
- プラン: docs/plans/active/2026-04-23-agents-md-absorb-plan.md

## [2026-04-21] ingest | Obsidian × Claude Code (akira_papa_AI)

- ソース: https://qiita.com/akira_papa_AI/items/4ac1edc7e93604b0199a
- 判定: Gap 2個 (Obsidian Inbox triage / 1コマンド1タスク codify), Partial 2個 (cwd-aware / 禁止より推奨), N/A 2個 (Daily Note / Sprint Sync), Already 7個 (5 強化可 + 2 強化不要)
- 取り込み: 5 タスク (A1 cwd routing matrix, A2 weekly-review Obsidian 統合, B1 Build to Delete wiring, C1 Thin+Thick ADR-0007, C2 skill-writing-principles 三節)
- 分析: docs/research/2026-04-21-obsidian-claudecode-absorb-analysis.md
- プラン: docs/plans/active/2026-04-21-obsidian-claudecode-absorb-plan.md
- 特記: Codex 批評で「新コマンド量産ではなく decision loop 接続と削除運用完成を優先」と judgment を補正。Gemini で Karpathy 3層パラダイム、Constitutional AI 規範的フレーミング、IFScale 上限など周辺知識を補完。

## [2026-04-24] ingest | AlphaSignal Harness Engineering

- ソース: AlphaSignal "A Closer Look at Harness Engineering from Top AI Companies" (2026-04)
- 判定: Gap 1 (4 軸分類), Partial 5 (Map not Manual / Strict Dependency Flow / Agent-written Linter / Evaluator 分離 / Meta-harness 他), Already 強化 2 (Reasoning Sandwich, dead-weight 吸収)
- 重複度: 2026-04-19 harness-everything-absorb と高 (独自 contribution 3 点のみ)
- 取り込み: 既存 plan docs/plans/active/2026-04-19-harness-everything-absorb-plan.md の M2 に subtask merge
  - M2-A: Reasoning Sandwich 手動チェックリスト pin (model-routing.md、LangChain +13.7pt data)
  - M2-B: dead-weight-scan に superseded_by_model タグ (Opus 4.7 self-verification 吸収追跡、最優先)
  - M2-C: ADR-0006 に ThoughtWorks 4 軸分類 Appendix (3 分類と直交)
- 実装済: M2-A, M2-C。保留: M2-B (dead-weight-scan.py 本体実装時に組み込み)
- 分析: docs/research/2026-04-24-harness-engineering-absorb-analysis.md
- 特記: Codex 批評で Gap (3) Strict Dependency Flow を Partial に降格、最優先は B (Opus 4.7 吸収時間圧) と判定。Gemini 補完は 15 tool uses / 15 分で empty return、外部 independent replication は未検証。Wiki/Obsidian 後処理は subagent permission denied で main session 実行。

## [2026-04-26] ingest | Workflow Trellis (2x2 step-level workflow framework)

- ソース: https://github.com/gnurio/nurijanian-skills/blob/main/skills/workflow-trellis/SKILL.md (Linus Lee 系統)
- 判定: Gap 0 / Partial 0 / Already 強化可能 4 / N/A 1 (記事の核は S/M/L 多因子ルーティングに既に内包)
- 取り込み: 3 件 (S 規模、その場で実装)
  - A: stage-transition-rules.md に Control Surface Override 段落 (S 規模でも auth/不可逆/master/harness/breaking change なら Gate 強制)
  - C: observability-signals.md に Attention Allocation Decision Table (interrupt/batch/escalate/hide/shut up × 信号タイプ、Meister 2024 *Neuron* 10 bits/sec を脚注引用)
  - F: decision-tables-index.md に trellis 4 象限 → mechanism 1 行マッピング (ambient=hook / control surface=Gate / human-led=/think / nobody cares=silent)
- 棄却: 3 件 (cybernetic loop 三要素は agent-harness-contract.md に内蔵 / 5 driver weight は精緻化過剰、identity は個人 harness で N/A / Obligation Gate は Top 67 absorb で先行実装済)
- Codex 観察: 当初参照した harness-engineering-details.md は実在せず、強化案 B を棄却。S/M/L が単なる規模ではなく多因子ルーティング (リスク × 影響範囲 × ステークホルダー) として既に機能していることが判明
- Gemini 副作用: 指示外で docs/research/2026-04-26-workflow-trellis-research.md + memory/reference_workflow_trellis_research.md + MEMORY.md 索引追加。ユーザー判断で全削除
- レポート: docs/research/2026-04-26-workflow-trellis-absorb-analysis.md

## [2026-04-27] ingest | graphify (safishamsi/graphify)

- ソース: https://github.com/safishamsi/graphify (MIT, Python 3.10+)
- 判定: Already×4 / Partial×3 / N/A×3 / Gap→YAGNI×1 (vis.js)
- 取り込み: 3 件採択 (graphify 本体は棄却、CRG と 70% 重複)
  - T1 paper-analysis に Step 3.5 Concept Relations 追加 (subject/predicate/object トリプル、closed vocabulary 6 種)
  - T2 三値タグ EXTRACTED/INFERRED/AMBIGUOUS を confidence と直交軸で併記
  - T3 71.5x benchmark を `codebase-graph-benchmarks.md` に reference 記録
- 棄却: 本体インストール (Build to Delete 違反)、vis.js (YAGNI)、Whisper (digest で代替)
- レポート: docs/research/2026-04-27-graphify-absorb-analysis.md

## [2026-04-26] ingest | Tech-Debt-Skill (ksimback) absorb

- ソース: https://github.com/ksimback/tech-debt-skill
- 判定: Gap 0 / Partial 6 / Already 4 / N/A 0（Phase 2.5 修正後）
- 取り込み: 既存 `/audit` を 9 点強化（Pruning-First、新規スキル作成なし）
  - Orient Gate (境界/flow/invariants/runtime surface mandatory)
  - Structural Pre-filter Optional (ast-grep/madge/knip/vulture/Semgrep)
  - /check-health crosswalk
  - Severity × Effort 2軸 + Quick Wins
  - Conflict Detection (両論併記)
  - Hallucination Defense (虚偽 line 検出 + ±10 行閾値)
  - QUESTIONS.md template 拡張 (Orient Summary / Top 5 / Quick Wins / Conflicts / Non-Findings)
  - Output Contract (曖昧表現禁止)
  - Repeat-Run Tracking 軽量版 (git diff ベース)
- 棄却: 新規 /tech-debt-audit 作成、9 dimensions 独立化、Repeat-run state file、Diplomatic vagueness 哲学節
- 分析レポート: docs/research/2026-04-26-tech-debt-skill-absorb-analysis.md
- 強化対象: .config/claude/skills/audit/SKILL.md

## [2026-04-29] ingest | mattpocock/skills (AlphaSignal Skills For Real Engineering)

- ソース: AlphaSignal newsletter / github.com/mattpocock/skills (28K stars 2026-04-27)
- 判定: Already 12, Already (強化可能) 2, Gap 1, N/A 1
- 取り込み:
  - prd-to-issues SKILL.md に HITL/AFK markers (Step 3 ルール5 + Issue テンプレ + Step 4/5 表示)
  - grill-interview SKILL.md Step 3 に Auto Mode OFF 起動条件を 1 行追記
- 棄却: K7 TDD 新規 reference (Pruning-First 違反) / S3 Invocation Control 原則 (実害が出るまで保留) / K13 backlog abstraction (GitHub-only 運用継続)
- 本質: 既に 4/5 chain が origin タグ付きで統合済 (grill-interview/spec/prd-to-issues/improve-codebase-architecture+LANGUAGE.md)。Codex 指摘「skill catalog ではなく discipline (個人 artifact 過度に一般化しない / 狭い process encoding / 更新できない skill は負債化)」は既存仕組みでカバー
- 分析レポート: docs/research/2026-04-29-mattpocock-skills-absorb-analysis.md

## [2026-04-29] ingest | OpenAI Symphony / ClawSweeper Orchestration Layer

- ソース: AlphaSignal "How OpenAI Is Setting the Default Orchestration Layer for Coding Agents" (https://github.com/openai/symphony, https://github.com/openclaw/clawsweeper)
- 判定: Already 11 / Gap 4 (F0+#9+#10+#13+#11) / N/A 棄却 4 (#7 cron / #15 apply cap / #5 app-server 全採用 / #2 GitHub issue cron)
- 取り込み: 既存 Codex Janitor のハーデニング 3 グループ (F0 既存 Follow-Ups 消化 / #9+#10 snapshot hash + 構造化 evidence record / #13+#11 keep-open bias + token strip)。Codex 批評で #9 が Already→Gap 格上げ、Gemini 警告で snapshot scope を single-run 内に限定
- 分析: docs/research/2026-04-29-symphony-clawsweeper-absorb-analysis.md
- プラン: docs/plans/active/2026-04-29-symphony-clawsweeper-absorb-plan.md

## [2026-04-29] ingest | Claude Code の Routines 機能で継続的にパフォーマンスチューニング (yamadashy)

- ソース: https://zenn.dev/yamadashy/articles/claude-code-routines-perf-tuning
- 判定: Gap 1, Partial 5, Already→Partial 格下げ 2 (#5/#8), Already 0 (修正後)
- 取り込み: 6 項目全採択 (A Improvement Vectors matrix / B End-to-End Improvement Floor / E 成果属性メタデータ / F Plateau 多軸検出 / C _dashboard.md sparkline / D Routines pilot 仕様化)
- 分析レポート: docs/research/2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md
- 統合プラン: docs/plans/active/2026-04-29-routines-absorb-plan.md
- Codex 批評: 既存 /absorb + AutoEvolve で土台十分、A+B を gate/report に最小差分追加が最優先
- Gemini 補完: Reward Hacking / Slop 蓄積 / Goodhart が主要失敗パターン → Anti-Gaming Layer 必要

## [2026-04-29] ingest | Claude Code Skills が "勝手に動く" 6つの設計法則

- ソース: zodchiii氏 X.com (https://x.com/zodchiii/status/2048345453096313005) / 東大Claude Code研究所紹介, 2026-04
- 判定: Already 6, Partial 1, Gap 1, 棄却 4 (Pruning-First 徹底)
- 取り込み: 採用 2 件のみ
  - T1: validation-checklist.md に「3 near-miss negative examples」チェック追加
  - T2: skill-writing-principles § 7 に「first screen 50行 (trigger/usage/next-read pointers)」原則追記
- 棄却: Out of Scope 100% (過剰)、6法則 ↔ 12原則 crosswalk 新規ファイル (docs 増殖)、50文字未満 ast-grep (観察的相関)
- 教訓: 100個リバースエンジニアリングという脳筋手法の知見も、大半は既に skill-writing-principles 12原則 + skill-creator + skill-audit に内蔵されていた
- 分析レポート: `docs/research/2026-04-29-claude-skills-six-laws-absorb-analysis.md`

## [2026-04-29] ingest | Codex vs Claude Code 役割分担 (Codex Studio)

- ソース: 「【保存版】Codex vs Claude Code 数百時間使ってたどり着いた最強の役割分担」(@Codestudiopjbk)
- 判定: Already 3, Partial 3 (Reject), Gap 3 (Reject), N/A 3
- 取り込み: 1 件のみ — `.config/claude/rules/codex-delegation.md` に「Safety Claim を過信しない」セクション追記 (trusted profile 運用前提の明示)
- 棄却理由: Codex Studio = Codex 寄りベンダーバイアス強い (DM 募集アカウント)。E/G/L (tokenizer +35%/Codex 4-23 機能/Anthropic disclosure) は公式 changelog で裏取り不可 (Gemini 補完)。Codex 批評も「採用 0 件が妥当」と判定
- レポート: docs/research/2026-04-29-codex-vs-claudecode-role-split-absorb-analysis.md

## [2026-04-29] ingest | The Self-Healing Agent Harness (CREAO 続編)

- ソース: CREAO CTO Peter Pang, 2026-04-29 推定
- 判定: Gap 1, Partial 1 (T4-C), Already (強化採用) 3, N/A 5, 棄却 7
- 取り込み: T1 outcome over trajectory / T2 model-family diversity / T3 drift 再校正条件 / T4-C regression-suite populate (別セッション)
- 棄却の主軸: CREAO の Engineering Pipeline と Bridge は前作 absorb (2026-04-14) で「multi-tenant 製品の儀式」として N/A 判定済
- 関連: docs/research/2026-04-29-self-healing-harness-absorb-analysis.md, docs/plans/active/2026-04-29-self-healing-absorb-plan.md

## [2026-04-30] ingest | What to Learn, Build, and Skip in AI Agents (2026)

- ソース: anonymous engineer ($250k+ offers, stealth company tech lead), 2026-04 meta-guide
- 判定: Already 6 (L1/L3/L4/L5/L6/B2), Already→不要 1 (L2 aci-tool-design.md #3 が同等カバー), Already→N/A 1 (M2 weekly-review GTD focus 不適合), N/A 6 (F2/L7/B1/M1/S1/W1)
- 取り込み: **採用 1 件のみ** — F1 5-test filter (will-it-matter-2y / postmortem-w-numbers / non-disruptive-adopt / cost-of-skipping-6m / measurable-impact) を `references/triage-criteria.md` に 1 セクション追記。test 4「6 ヶ月 skip コスト ≒ 0」の機会費用フレーミングが novel
- Codex 批評: exec 失敗 (BG kill, exit 144) → Opus がファイル直接検証 (aci-tool-design.md / weekly-review SKILL.md / triage-criteria.md) で同等批評達成、L2 と M2 を強化候補から降格
- Gemini fact-check: Spotify 25% / 40% retry / CC April 2026 47% regression / LangGraph 1/3 全て未検証 anecdote と判明 → 報告書に untrusted-stat タグ
- 教訓: 40+ 累積 absorb 後の meta 級記事は Already 率高 (本記事は ~80% カバー済)、ファイル直接検証が外部 critic より高効率なケースあり
- 分析レポート: docs/research/2026-04-30-learn-build-skip-2026-absorb-analysis.md

## [2026-04-30] ingest | Claude API skill now in CodeRabbit, JetBrains, Resolve AI, and Warp

- ソース: https://claude.com/blog/claude-api-skill (Anthropic 公式, 2026-04-29)
- 判定: Gap 0 / Partial 0→N/A 修正 / Already 5 (強化不要) / N/A 3
- 取り込み: **採用 0 件** (Codex+Gemini 一致、Pruning-First)
- 教訓: アナウンス記事 + ベンダーバイアス警戒。claude-api SKILL.md model ID 陳腐化は別件 hygiene
- レポート: docs/research/2026-04-30-claude-api-skill-absorb-analysis.md

## [2026-05-02] ingest | 30 Claude Code Sub-Agents I Actually Use in 2026

- ソース: anonymous Medium 系記事 (テキスト貼り付け、URL なし)
- 判定: Gap 0 / Partial 5 / Already 7 / N/A 15 / not_found 3 (deep-dive で Self-Rejection Rule pattern + Subagent Count Ceiling を Gap 発見)
- 取り込み: T2 migration-guard.md に forward+reverse BLOCK rule + Postgres-specific hard blockers / T3 edge-case-analysis SKILL.md に 15 軸補足チェックリスト / T5 agent-design-lessons.md に Self-Rejection Rule Pattern セクション / メタ Subagent Count Ceiling セクション (Gemini 50+ degradation 9/10→5/10、dotfiles 33 個で残り 17)
- 棄却 26 件: business team agent 15 個 (Sales/Marketing/CS/Ops/Finance) は個人 dotfiles で out_of_scope、code-reviewer / counterargument / decision-log / daily-plan は既存仕組みで実質カバー
- 関連レポート: docs/research/2026-05-02-30-subagents-2026-absorb-analysis.md

## [2026-05-04] ingest | I tracked 430 hours of Claude Code usage. 73% was wasted on these 9 patterns

- ソース: anonymous X post + Telegram funnel (https://t.me/+_ZWrQN7GuDA3ZDEy、URL なし、テキスト貼り付け)
- 判定: Gap 1 (Pattern 5 skill loading 12,283 token tax) / Partial 2 (8 早期停止 / 9 SessionStart) / Already 5 / 保留 1 (4 Cache TTL)
- 取り込み 5 件: T1 (M, 最優先) skill Tier 分類で常時 description tax 半減 (12,283→~6,000) / T1.5 (S) dotfiles/CLAUDE.md project 再検討 / T2 (S) SessionStart hook 監査 / T3 (S) Cache TTL 実態確認調査 / T4 (XS) MEMORY references 流入経路確認
- 棄却 3: Pattern 1 (CLAUDE.md user) Pruning-First / Pattern 6 (MCP) settings.json 0 個で最小 / Pattern 7 (Thinking) DISABLE_ADAPTIVE_THINKING=1 設定済
- 教訓: 14+13+11+10+7+6+5+4+3=73% engineered 数字。Telegram 集客で信頼度低。判断は記事数値ではなく当 setup 実測 (107 skill 12,283 token tax) ベース。Codex critique で Opus 過大評価寄りバイアスを 4 件補正 (Pattern 5 Gap 格上げ、Pattern 4 保留、Pattern 1/6 棄却)
- 関連レポート: docs/research/2026-05-04-claude-code-overhead-9patterns-absorb-analysis.md

## [2026-05-04] ingest | Distribution vs Escalation: Subagents or Advisors

- ソース: "Distribution vs Escalation: When to Use Subagents or Advisors" (2026-05-02, author unknown)
- 判定: Gap 0 / Partial 3 (#3 Advisor 索引接続, #5 Drive 主体逆転表, #7 lifecycle registry) / Already 6 / N/A 1 (Forked subagent 再確認)
- 取り込み: A1 (decision-tables-index Advisor 行 + Drive 主体逆転表) / A2 (advisor-strategy one-shot per decision + review-consensus §9) / A3 (subagent-delegation Return Contract) / B1 (mcp-audit soft→enforcement 修正) / B2 (fork-analysis reaffirmed footnote)
- 分離: B3 (lifecycle registry coverage) は別 plan
- Hallucination Risk: advisor_20260301 / Anthropic blog 4/9 / UC Berkeley advisor 論文 が確認不可、specific tool names / 数値は採用せず pattern のみ採用
- 分析レポート: docs/research/2026-05-04-distribution-vs-escalation-absorb-analysis.md

## [2026-05-06] ingest | I Tried 100+ Claude Code Skills. These 6 Are The Best

- ソース: anonymous AI agency operator 記事 (real estate / HVAC / coaches / marketing 業界向け automation 販売バイアス)
- 判定: Already 4 (Skill Creator, Superpowers, Frontend Design + 当初 Context Mode)、Partial 3 (GSD, /ultrareview, Claude Mem)、Codex 修正で Context Mode → Partial 要実験に降格
- Phase 2.5 Refine: Codex で `/ultra-review` → 公式名 `/ultrareview` 確認、Pro/Max 3 free 期間 2026-05-05 終了 (今日から有料)、最大の罠 = MEMORY.md を semantic layer で置換
- 取り込み 5 タスク (3 件は今セッション実装済): T1 Codex Review Gate に Independent Reproduction Standard 追加 / T2 task skills:eval-e2e 化 / T3 post-compact-verify.js に reinjection selector (P1 Active Plans + P2 Recently Edited) / T4 checkpoint 強化 (skip) / T5 Claude Mem vector spike (リスク annotation 付き、別セッション推奨)
- 詳細: docs/research/2026-05-06-100-skills-best6-absorb-analysis.md

## [2026-05-06] ingest | Your Claude Code's WebFetch Isn't Actually Reading the Web Properly

- ソース: sherry/Zenn 2026-05-04 (https://zenn.dev/zhizhiarv/articles/claude-code-webfetch-haiku-summary)
- 主張: Claude Code の WebFetch は内部で Haiku が要約、3 条件 (Content-Type: text/markdown + 80+ trusted domains + <100k chars) 外はサイレント truncate。表示の "204.4KB" は受信バイト、実際 LLM が読むのは要約後コンテンツ。
- 判定: Phase 2 初版で Gap 4/Partial 5 → Phase 2.5 (Codex+Gemini 並列批評) で Gap 4 → Already 拡張に格下げ (friction-events 1 schema + 外部 JSON + 1 行参照で吸収可能)、新規 Gap 3 追加 (引用 faithfulness vs Copyright filter 125字 / HTML→md lossy / Haiku 要約層の prompt injection 表面)
- 取り込み 8/8 採用 (ユーザー判断 `a`):
  - A1 references/web-fetch-policy.md (URL pattern → 経路 decision table) 新規 + 7 skill (absorb/research/deep-read/digest/web-design-guidelines/alphaxiv/tech-article-reproducibility) から 1 行参照
  - A2 PostToolUse hook `scripts/runtime/webfetch-truncation-detector.py` で `webfetch_truncation_suspect` event を friction-events.jsonl に記録
  - A3 references/model-routing.md と subagent-delegation-guide.md の「Haiku WebFetch 委譲」契約を「生 markdown 取得まで」に限定、要約は呼び出し側責務 (二重圧縮の根本遮断)
  - B1 当プロジェクトで 1 度実測 (Wikipedia/Zenn/Qiita/AWS docs で受信バイト vs 可視文字数 vs 元記事) — policy 化前の根拠確保
  - B2 absorb SKILL.md Phase 1 を gate 化 (trusted 外で curl+defuddle/Gemini grounding に強制切替) + 引用 faithfulness 警告
  - C1/C2 web-fetch-policy.md 内に「原文引用必要時」「code/table 重視記事」のオーバーライド明記
  - C3 security-reviewer agent に「Haiku 要約層の prompt injection 表面」観点追加
- 棄却: trusted_domains リスト本体を CLAUDE.md/MEMORY.md 転記 (IFScale 違反) / 各 skill に 3 行手順分散 (DRY 違反)
- 規模: L (14 ファイル変更、新規 2 + 修正 12)、推奨実行: 新セッション + `/rpi docs/plans/2026-05-06-webfetch-policy-plan.md`
- 観測前提: Claude Code v2.1.126 リバースエンジニアリング由来 (observation_pinned)、Anthropic 公式は Haiku 介在を直接記述していない (Gemini 確認、コミュニティで 100KB truncation 自体は再現多数)
- Gemini 追加発見: Jina Reader (`r.jina.ai/<url>`) / 15 分キャッシュ / JS 非対応 / Cline は MCP+Playwright でフルブラウザ
- 関連レポート: docs/research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md / 統合プラン: docs/plans/2026-05-06-webfetch-policy-plan.md

## [2026-05-08] ingest | Cyril Obsidian Vault Smarter (@cyrilXBT)

- ソース: 「How to Build an Obsidian Knowledge Vault That Gets Smarter Every Day」記事
- 判定: Gap 0, Partial 1 (contradiction detection), Already 3 (強化不要), N/A 4, 棄却 5
- 採用 (3 タスク S): A) /think に保存済み信念との矛盾照合 step 追加 / B) auto-morning-briefing.sh の Daily path を 07-Daily に統一 / C) thinking-context-template に Reading 欄追加
- 副次発見: Hammerspoon (.hammerspoon/{daily_enforcer.lua,README.md}) にも同 path drift があり同時修正済み
- 分類: reference-only (記事の主要主張 8 件棄却、Codex 批評で厳格化)

## [2026-05-08] meta | /improve サイクル 1 — skill pruning evaluation 開始

- トリガー: /improve サイクル 1 (2026-05-08) で skill-audit が dormant 8 件 + 大型 5 件 + description 衝突 4 件を検出
- 即時適用: Track C audit/simplify description sharpen (commit 7541b7e) + briefing security 強化 (commit 89426bf)
- 30 日評価開始: ai-workflow-audit / autocover / refactor-session / setup-background-agents / recall(local) / analyze-tacit-knowledge(local) / prompt-review / developer-onboarding (期間 2026-05-08 → 2026-06-07)
- プラン: docs/plans/2026-05-08-skill-pruning-evaluation-plan.md (gitignored, ローカル参照)
- リマインダー: 2026-06-07 09:00 cron で `dead-weight-scan.py` 起動 (cycle 2 で配置予定)

## [2026-05-07] ingest | Warp oz-skills (15 skill) absorb

- ソース: https://github.com/warpdotdev/oz-skills (MIT, 2026)
- 判定: Already 1 / Already 強化可能 4 / Partial 6 / Gap 0 / N/A 4
- 取り込み (6件すべて rubric 移植, 新 skill 追加なし):
  - T1: references/ci-fix-policy.md (permissions/pull_request_target/flaky rerun 3 hard rule)
  - T2: skills/check-health/SKILL.md Step 3.8 user-facing change drift rubric
  - T3: agents/design-reviewer.md WCAG POUR + severity + manual testing
  - T4: commands/pull-request.md Step 0 Pre-PR Chain Check
  - T5: references/scheduling-decision-table.md
  - T6: references/agent-browser-server-lifecycle.md
- 分析レポート: docs/research/2026-05-07-warp-oz-skills-absorb-analysis.md

## [2026-05-10] ingest | 12-rule CLAUDE.md (anonymous Telegram article)

- ソース: anonymous Telegram daily-tips article (skool.com 販売漏斗パターン、Boris/Three-Model Stack 系列)
- 判定: Gap 0, Partial 2 (R6/R9), Already 6 (R5/R7/R8/R10/R11/R12)
- 取り込み: T1 R12 silent success audit (S 規模、completion-gate.py + checkpoint_manager.py の silent except 修正) + T2 R9 test intent rubric (S 規模、review-dimensions.md に correctness 補足追記)
- 棄却: T3 12-rule CLAUDE.md 全採用 (Pruning-First 違反 + 200 行 ceiling 抵触 + 記事根拠の弱さ)
- 分析レポート: `docs/research/2026-05-10-12-rule-claude-md-absorb-analysis.md`

## [2026-05-14] ingest | Khairallah Claude Code Routines

- ソース: "How to Set Up Claude Code Routines to Automate Any Workflow (Full Course)" (@eng_khairallah1, content farm pattern 7th)
- 判定: Gap 4 / Partial 5 / Already(強化可能) 3 / Already(強化不要) 1 / N/A 1 / Inconclusive 1
- 取り込み: T1 routine-prompt-rubric.md 新規 (Bulletproof prompt 6 要素) / T2 managed-agents-scheduling.md に Recipe Catalog R1-R5 + Dreaming Inconclusive 注記 / T3 scheduling-decision-table.md に Step 6 + 段階運用 / T4 decision-tables-index.md 更新
- 教訓: Codex no output 2 連発 + Gemini rate limit で Phase 2.5 劣化 → 前日 Nav Toor 検証データを Phase 2.5 補完源として再活用するパターンが成立

## [2026-05-16] ingest | Anthropic Agent SDK Credit (2026-06-15 billing split)

- ソース: <https://zed.dev/blog/anthropic-subscription-changes> (Zed Industries, 2026-05-15)
- 一次検証: <https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan> (`obsidian:defuddle` で全文取得確認、Gemini grounding の 3 誤判定を訂正)
- 判定: Gap 1 / Partial 1 / N/A 2 / Already 強化 3 + 副次 F1+F2 (合計 6 件、全採用)
- 取り込み: `references/agent-sdk-credit.md` (new decision-table) + `model-routing.md` Cost-aware Fallback 節 + `managed-agents-scheduling.md` Phase 0 (Routine `claude -p` は credit 消費) + `skills/{research,autonomous,dispatch}/SKILL.md` credit short note + `~/.claude/skills/absorb/SKILL.md` Codex Skill 経由パターン化 (F1) + memory 3 件 (F2)
- 教訓: (a) Gemini grounding は二重矛盾あり (内部メモ UNVERIFIED vs 最終 summary VERIFIED)、defuddle で自分で一次取得が必須 / (b) Codex `Agent(subagent_type: "codex:codex-rescue")` 直起動は codex CLI 孤立 stall、`Skill(skill: "codex:rescue")` 経由が正規 / (c) Phase 2.5 `ScheduleWakeup` ループは 2 回 max、独自検証で進む / (d) competitive vendor 記事 (Zed=ACP 推進者) でも事実主張は全 Verified なケースあり
- 関連 commit: `ec3e1c6`
- 分析レポート: `docs/research/2026-05-16-anthropic-agent-sdk-credit-absorb-analysis.md`

## [2026-05-17] ingest | SocratiCode absorb

- ソース: https://github.com/giancarloerra/SocratiCode (Giancarlo Erra / Altaire Limited、AGPL-3.0+商用、2640⭐)
- 判定: 18 手法のうち採用 1 (#4 S 規模) + 降格 1 (#16 XS) + eval spike plan 1 (M plan-only)、Already 強化不要 9、N/A (dotfiles 用途外 Gap 含む) 7
- 取り込み:
  - T1 (S): `.config/claude/references/code-review-graph-guide.md` に CRG 循環依存検出 limitation 補足 (`flows.py` cycle 防止のみ、SocratiCode `codebase_graph_circular` 相当無し、madge/pylint fallback)
  - T2 (XS): `.config/claude/scripts/policy/mcp-audit.py` + `references/decision-tables-index.md` に plugin+standalone 重複登録 audit checklist memo (#16 降格、即実装 YAGNI)
  - T3 (M plan-only): `docs/plans/pending/2026-05-17-memory-vec-scope-extension-spike.md` (memory-vec scope を docs/research+specs+references 478files/4MB に拡張する eval-only spike)
- 教訓: (a) 3 度目の同分野 absorb (CRG 採用 / graphify 棄却) は Pruning-First で本体棄却、強化観点で記録のみ / (b) Codex 単独 Phase 2.5 (Gemini quota 完全枯渇 gemini-3-flash-preview/2.5-pro 両モデル 10 attempts max) でも memory-vec Phase D 実装済を再発見し #2/#8 判定誤り補正 / (c) Altaire vendor 記事のベンチ (61%/84%/37x) は grep-only baseline で vendor claim 扱い、`codebase-graph-benchmarks.md` の「5-15x 収束」教訓と整合 / (d) cmux `launch-worker.sh` `surface:1` ハードコード + `codex exec -q` 廃止のバグ併発 (修正は本 absorb 外)
- 分析レポート: `docs/research/2026-05-17-socraticode-absorb-analysis.md`
- Obsidian Literature Note: `~/Documents/Obsidian Vault/05-Literature/lit-giancarlo-erra-socraticode.md`

## [2026-05-20] ingest | Claude Code Large Codebase Best Practices (Anthropic 公式)

- ソース: https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start
- 判定: Already 10, N/A 3, Partial 1, Already (軽微強化余地) 1
- 取り込み: なし (D 選択)
- 最重要発見: Task 1-3 候補 (skill path-scoped/cadence/token tax 監視) 全て既存 (`skill-suggest.py` PATH_MAP / `skill-pruning-eval-reminder.sh` / `skill-count-alert.sh`) と完全重複、Pruning-First 失敗事例
- 分析: docs/research/2026-05-20-claude-code-large-codebase-absorb-analysis.md

## [2026-05-20] ingest | Hermes Agent + x_search 最小セットアップ

- ソース: xAI 公式 (@xai 2026-05-16/17) "grok-hermes" アナウンス由来、ユーザー貼り付け記事
- 判定: Gap 1 (低価値), Already 1, Already(強化可能) 1, N/A 2
- 取り込み: なし (Reference Only) — X Premium サブスク前提 + dotfiles 用途で X 検索 ROI 極小 + Grok 解釈レイヤー経由 (interpretation layer 問題と同型) + 30 秒+ レスポンスは non-blocking パターン不適
- レポート: `docs/research/2026-05-20-hermes-x-search-absorb-analysis.md`
- Obsidian Literature Note: `~/Documents/Obsidian Vault/05-Literature/lit-anonymous-hermes-x-search-minimal-setup-2026-05-20.md`

## [2026-05-19] ingest | Cyril Obsidian Dashboard (@cyrilXBT)

- ソース: docs/research/2026-05-19-cyril-obsidian-dashboard-absorb-analysis.md
- 判定: Gap/Partial 0 件、Already 4 件 (T4/T5/T6/T8/T10/T11)、N/A 6 件 (T1/T2/T3/T7/T9/T12 — Dataview legacy + agency domain mismatch)
- 採用: Task A (daily_enforcer Review section detector 追加 / 1-2 ファイル) + Task B (Dataview micro-dashboard 3-section template with Bases 移行 caveat / 2 新規 + 1 修正)
- 関連: docs/research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md (同一著者前回 absorb)
- 教訓: content farm 11 件目、技術主張も時代遅れ (Dataview legacy 確認)、副次発見 (T11) が実害近い

## [2026-05-22] ingest-skip | Cyril Obsidian Personal OS Never Breaks Down (@cyrilXBT)

- ソース: How to Turn Obsidian Into a Personal Operating System That Never Breaks Down (cyrilXBT, テキスト貼り付け)
- 理由: topic family "obsidian-second-brain" saturated (N>=12 / Cyril 単独 4 本目)、_index.md `2026-05-21 cyril-personal-os` エントリと完全一致 (タイトル "Personal OS" / 8 フォルダ CAPTURE-ARCHIVE / 5 workflow Daily-Capture-Weekly-Queue-Health / CLAUDE.md SSOT / N8N automation)
- スキップ判定: Phase 1.5 Saturation Gate + _index 明記「4 本目以降は Phase 1 で著者検出 → reference-only 即時判定で workflow 短絡可能」指示適用
- 過去採用: 0% (Cyril 3 本連続 reference-only、副次発見も 2026-05-19 で停止)
- 後続アクション: なし (MEMORY.md 索引追記なし、分析レポート作成なし、Codex/Gemini Phase 2.5 なし)

## [2026-05-21] ingest | Erukiti フルAIコーディング (Zenn)

- ソース: https://zenn.dev/erukiti/articles/2512-full-ai-cofing
- 判定: Gap 0, Partial 6 (→ うち 2 を N/A 降格), Already 5 (うち 1 強化不要に降格、4 強化可能), N/A 3 (Phase 2.5 で追加降格分含む)
- 取り込み (6 項目, 4 ファイル変更):
  - T1: CLAUDE.md core_principles に「暗黙フォールバック・モック・NO-OP 絶対禁止」追記
  - T2: references/task-decomposition-guide.md に M/L 事前見積もりプロンプト + テスト/実装フェイズ分離プロンプト追記
  - T3: rules/common/testing.md に「Test Comments (前提・事前条件・検証項目)」セクション追加
  - T4: rules/typescript.md に「推奨スタック (vitest 優先)」+「レイヤー強制 (eslint-plugin-boundaries)」セクション追加
- レポート: docs/research/2026-05-21-zenn-erukiti-full-ai-coding-absorb-analysis.md

## [2026-05-22] ingest | How Anthropic Engineers Actually Save Tokens

- ソース: テキスト貼り付け (community blog、Thariq Shihipar X 投稿引用)
- 分析: docs/research/2026-05-22-anthropic-engineers-token-savings-absorb-analysis.md
- 判定: Gap 4 (T4/T5/NEW1/NEW2), Partial 4 (T1/T6/T8/T9 修正), Already 2 (T2 強化必須/T3), N/A 1 (T7)
- 取り込み (S 規模 5 ファイル):
  - resource-bounds.md: Prompt Cache TTL 三層 (state 2h / main 1h / subagent 5min) + 混同回避注記
  - cc-7-layer-memory-model.md: CacheSafeParams 強化 (MCP/tool deny/CC upgrade も invalidation 要因、CLAUDE.md mid-edit は restart まで未反映)
  - model-routing.md: Model Switch / Cache Invalidation Boundary 新セクション
  - subagent-delegation-guide.md: Subagent Prompt Cache TTL (5min) 注記
  - session-protocol.md: /rewind を /clear の cache-safe 代替として追加
- 取り込み (M 規模、保留): T9 session_observer 拡張 → docs/plans/active/2026-05-22-token-cache-observer-extension.md
- Codex review (task-mpg0cxic-z5lvrk) 主要指摘:
  - 2h state TTL ≠ 1h prompt cache TTL の混同回避が最重要
  - token-dashboard は session_observer に既に cache_read/create 抽出 (Gap → Partial)
  - opusplan 禁止 bias 警告 (品質メリット無視は誤り)
- Gemini fact-check: 8 主張中 7 VERIFIED + 1 PARTIALLY VERIFIED (subagent 5min は公式に「even on subscription」明記)


## [2026-05-22] ingest | Khairallah — How to Actually Set Up Claude. 40 Features Most Users Have Never Touched

- ソース: テキスト貼り付け (X 投稿、@eng_khairallah1)
- 分析: docs/research/2026-05-22-khairallah-40-features-absorb-analysis.md
- 判定: family `claude-code-tips` 11 件目 / Saturation Gate PASS (warning, 60% adoption)
- 記事採用: 0 件 (TOP 5 強化候補すべて Sonnet imagination と Pass 2 で判定、Codex 独立検証で同判定確認)
- Validation-only 1 件:
  - docs/guides/2026-05-09-claude-cowork-equivalents.md: 「Claude Cowork は存在しない」stale fact → 「Cowork 実在前提で dotfiles が採用しない理由」に書き直し
- Meta-finding 3 件 (本 absorb の主成果):
  - /absorb SKILL.md anti-patterns に 4 行追加 (Sonnet 強化案 Pass 2 引用照合 / 未知用語 Gemini grounding 先行 / 採用 0 ≠ 終了 で platform drift 別 ledger / Sonnet imagination 罠 link)
  - memory/feedback_absorb_sonnet_imagination.md 新設 (Gap fabrication = Already=存在確認≠強化不要 の対の罠)
  - 同 family 11 件目で初検出した failure mode を skill 自身で防御化
- 重要発見 (Codex / Gemini grounding):
  - "Cowork tab" は Anthropic 公式機能として実在 (2026 年初頭 Claude Desktop 導入、support.claude.com/articles/13345190)
  - Opus 当初の "factually dubious" 即断は誤り (未知用語の grounding 不足)
  - dotfiles の stale doc が absorb 過程で露出 → platform drift audit としては値あり
- ユーザー指摘: 「本当に参考になるもの、活かせるものなかった？手を抜いてない？」→ フル Phase 2-2.5 走査で Reject 判定の根拠を厳格化


## [2026-05-23] ingest (article=0, side-adopt=3, validation-only) | aitmpl — Keep your Claude Code context clean with Subagents (re-投入)

- ソース: テキスト貼り付け (aitmpl 系記事、2026-04-27 absorb 済の同一記事)
- 分析: docs/research/2026-05-23-subagent-context-fork-revisit-analysis.md
- 判定: family `subagent / context-fork` (N=5+, 完全一致先行例あり) / Saturation Gate **SATURATED-pure-rehash** (delta=0) → ユーザーは continue 選択
- **記事採用 0**: 全 8 手法は前回 2026-04-27 で analyze 済、新規論点なし
- **副次採用 3 件** (validation-only follow-up):
  - A1: /absorb に Stale-Plan Audit (Step 7) 追加 — 過去採用タスクの棚卸し mechanism (topic-family-saturation.md + SKILL.md)
  - A2: 2026-04-27 レポートに `status: partially-superseded` + 棚卸し追記 (T3 superseded by 2026-05-22 session_observer / T2 narrowed / T4 narrowed)
  - A3: subagent-delegation-guide.md に `/fork` 意図的非採用の 1 段落注記 (T4 の新規 file 採用を inline 注記に narrow)
- Codex 推奨で副次採用、Gemini grounding は stable 化主張 (要 verification) — context cleanliness と逆方向の判断は不変
- Meta-finding: 「未実施タスクを backlog と見すぎる」failure mode を mechanism (Step 7) で防ぐ。記事再投入が古い採用判断の剪定トリガーとして機能した Khairallah パターン

## [2026-05-23] ingest | damidefi "Connect Claude to Obsidian Vault. 2 Months Later" (X creator)

- ソース: テキスト貼り付け (URL なし)、著者 @damidefi (X creator, follower 100K 目標)
- 分析: docs/research/2026-05-23-damidefi-claude-obsidian-second-brain-absorb-analysis.md
- 判定: family `obsidian-second-brain` 10 件目 / Saturation Gate PASS (warning) (採用率 33% で形式通過、user `continue` 選択)
- 主張: 4-layer (Capture/Automation/Memory/Intelligence) + type-based 6-folder + Daily 4-section synthesis (Connections/Patterns/Contradictions/Open Questions) + Weekly 30-day surprise test
- 採用 0 件、Validation-only follow-up なし
- Codex 批評で T3 (Partial→N/A)、T5 (Gap novel→Partial / novel ではない)、T7 (Already→Partial / on-demand 限定) に降格。「採用するなら T7 を 1 件だけ。最終推奨採用 0 件」
- Meta-finding 1: **obsidian-second-brain family 3 連続 reference-only 確定** (Cyril x2 + damidefi)。共通パターン = creator-monetization-driven AI second brain genre (X follower KPI + 課金 SaaS + anecdotal metrics + Bookmark/Share 誘導)
- Meta-finding 2: saturation taxonomy 閾値調整シグナル — N>=3 採用率>=20% の現行 PASS ルールでは「直近 2 件連続 reject」trend が拾えない → Step 4.5 連続 reject trend 副ガードを新設
- Meta-finding 3: Sonnet imagination 罠再発 (T5 を Partial 強化可能と Sonnet が返したが Cyril 系で棄却済)。Pass 2 で過去 absorb の照合が必要
- Meta-finding 4: Codex の reasoning depth が同族 absorb 文脈再構築に有効 — bias mitigation だけでなく context recovery としても Phase 2.5 価値あり
- Gemini grounding: クォータ枯渇 (Free tier) で 3 retry 後 abort、Codex 単独で判定十分

## [2026-05-24] ingest-skip | @cyrilXBT "How to Link Notes Together in Obsidian and Why It Changes Everything"

- ソース: テキスト貼り付け (URL なし)、著者 @cyrilXBT
- 理由: topic family `obsidian-second-brain` **14 件目 / Cyril 7 本目**、SATURATED-pure-rehash 寄り borderline (採用率 < 20%, delta ≈ 1 novel 候補)
- 根拠: 直近 3 連続 reference-only (cyril-one-folder 2026-05-22 / cyrilxbt-18-steps 2026-05-23 / damidefi 2026-05-23) + 著者ベース短絡示唆 (Cyril 4 本目以降, cyril-personal-os 2026-05-21 に明記) + Cyril 系 11+ 件で安定的 Reject パターン (cyrilxbt-18-steps Meta-finding 2)
- 該当 family のキーワード hit: obsidian, linking, backlink, graph view, aliases, MOCs, daily note, vault
- 手法 delta: Obsidian default 機能 7 項目 ([[Internal/Block/Heading Links]] / backlink panel / graph view / aliases frontmatter / unlinked mentions / MOCs / daily linking hub) は完全に Already (Obsidian built-in、強化対象なし) + novel 候補 1 件 (Claude MCP 3 prompts: connection finder / synthesis / gap finder) は /digest /think /compile-wiki + semantic_search_nodes + code-review-graph MCP で代替可能性高
- スキップ判定: Phase 1.5 gate (user 選択: skip 推奨)
- Phase 2-5 + Phase 2.5 + Wiki INDEX / Obsidian Bridge / MEMORY.md ポインタはすべて skip

## [2026-05-24] ingest | Google eng-practices Code Review Guide

- ソース: https://github.com/google/eng-practices (CC-BY 3.0, 20.9k stars)
- 判定: Gap 1 / Partial 9 / Already 強化可能 9 / Already 強化不要 4 / N/A 3 (合計 26 手法)
- 取り込み: 13 件全採用 — Gap/Partial 7 (#14 cleanup-later 境界, #21 emergency 定義, #25 Large CL exception, #1 Positive principle, #2 evidence-based feedback, #6 design-first gate, #13 pushback-who-is-right) + Already 強化可能 6 (#15 small-CL threshold, #16 splitting patterns, #11 courtesy + Bad/Good, #3 every-line + good-things, #17 refactor mixing block, #18 refactor-only tests nuance)
- プラン: `docs/plans/active/2026-05-24-google-eng-practices-integration-plan.md` (L 規模、新セッションで /rpi 推奨)
- 分析レポート: `docs/research/2026-05-24-google-eng-practices-absorb-analysis.md`

## [2026-05-24] ingest | Cursor cursor-team-kit thermo-nuclear-code-quality-review skill

- ソース: https://github.com/cursor/plugins/blob/b8f2564c2e8da66b331c1dd63c2a2925d6739961/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md (Cursor OSS plugin marketplace)
- 判定: Gap 4 / Partial 6 / 合計 11 手法 (Codex Phase 2.5 で #1 Gap→Partial / #7 Partial→Gap / #9 #10 根拠補強 + 4 件見落とし指摘)
- Family: code-review-best-practices **4 件目** (Findy + code-review-graph + Google eng-practices 13 件採用 直後)、saturation PASS-warning
- 取り込み: 3 件採用 (Pruning-First で 11 → 3 に圧縮) — T1 `cross-cutting.md` CC-11 Presumptive Structural Blockers (must 3 / consider 2 + Review Phrases 4 件) / T2 CC-12 1k-crossing review-time check (300 行 edit-time advisory と別軸の review-time presumptive blocker) / T3 CC-13 Canonical helper / layer leak check
- 棄却: 8 件 — #2 code-judo / #5 phrases / #6 spaghetti / #7 priority / #11 magic mechanism は T1 (CC-11) に吸収、#3 ambitious mindset は Pruning-First で棄却、#9 type cleanliness と #10 sequential orchestration は既存カバー (`review-checklists/typescript.md:17` + Promise.all / asyncio.gather)
- ユーザー質問への回答: 「/review skill から cursor CLI 呼び出しで使えるか?」→ 技術的可能 (既存 `skills/cursor/SKILL.md` 流用) だが常時 4th reviewer は棄却。opt-in pilot で `strict-maintainability` reviewer を Watch 扱いから 10 回ログ→ capability score 化 → 組み込み判断、が将来候補
- 分析レポート: `docs/research/2026-05-24-cursor-team-kit-thermo-nuclear-absorb-analysis.md`
- Phase 2.5 Gemini 省略理由: family saturated + 記事自己完結 + CLI 統合質問は記事内容と独立 (Codex 単独で批評十分)
- Meta-finding: Codex 批評で Opus Phase 2 の 4 件誤判定を訂正 (#1 `structure-check.py:34` `MAX_FILE_LINES=300` 見落とし / #7 broad→specific→nit は 3 段階で 7 段階と別物 / non-atomic update と magic mechanism 軸の見落とし)。bias mitigation 効果実証 (Google eng-practices で 9 件、本記事で 4 件)

## [2026-05-25] ingest-skip | 【保存版】勝手に賢くなるObsidianの作り方大全 (東大Obsidianオタク, Japanese rehash of cyrilxbt)

- ソース: 東大Obsidianオタク blog (Japanese), 元記事 = https://x.com/cyrilxbt/status/2052235121416188114 (2026-05-08 absorb 済)
- 理由: topic family "obsidian-second-brain" saturated-pure-rehash (11 件目, delta=0, 直近 3 件 (Cyril x2 + damidefi) 採用 0)
- 根拠: 4-layer architecture / 5-folder Inbox-Notes-Ideas-Projects / CLAUDE.md 5-section / Daily Brief CONNECTIONS-PATTERN-QUESTION / Weekly Synthesis 4-frame / 20min/week budget / "when in doubt, put in inbox" 全て 2026-05-08 `docs/research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md` で検証済 (12 手法のうち 8 棄却 + 副次 3 採用)
- 該当 family のキーワード hit: obsidian, second brain, CLAUDE.md, Daily Brief, Weekly Synthesis, vault, capture friction
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, ユーザー skip 選択)
- 既存実装 (記事の主張は既に運用中): `scripts/runtime/auto-morning-briefing.sh` (cron 平日 8:30) / `sync-daily-report.sh` (cron 23:00) / `/timekeeper` / `/think` contradiction check (2026-05-08 Task A 採用済) / `obsidian-vault-setup` 8-folder IPARAG (記事の 5-folder より上位構造)
- フォローアップ: ユーザーの「夜間動作させたい」は記事 absorb と切り離し、別 actionable として brainstorming に移行 (記事 absorb には数えない)

## [2026-05-25] ingest (light Phase 2) | 18 Claude settings (Telegram-promoted listicle)

- ソース: 匿名 Telegram プロモ付きリスティクル (`t.me/+_ZWrQN7GuDA3ZDEy`)、canonical URL なし
- 判定: claude-code-tips family **N=13** で SATURATED-but-novel (delta=2 + ambiguous 2)、ユーザー light-phase2 選択
- 取り込み: **採用 2 件** (#10 chmod 600 .env defense-in-depth in `claude-code-threats.md §6.5` / #15 `cleanupPeriodDays: 180` in `settings.json`)
- 棄却: 16 件 (Section 1 Claude.ai UI 8 件 N/A / #9 #12 #13 #14 #16 既存カバー / #11 Progressive Disclosure 優位で reject / #17 raw API 不使用で N/A / #18 workspace 運用なし)
- Grounding: WebSearch で `cleanupPeriodDays` 公式実在 + Issue #23710/#2543/#45903 確認、「Dreaming」機能主張は未確認のまま採用 (key 自体は本物)
- Step 4.5 trend warning: 直近 4 件中 3 件 reject 寄り (routines=4 / large-codebase=0 / khairallah-40=0 / khairallah-30-workflows=2) → light-phase2 で消化
- 該当 family のキーワード hit: claude code tips, hidden, N tricks, cheat
- レポート: `docs/research/2026-05-25-18-claude-settings-absorb-analysis.md`
- メタ: N=13 で初の light-phase2 採用、Phase 2.5 (Codex+Gemini) 省略で token/時間コスト 60% 削減

## [2026-05-26] ingest-skip | How to build a team of AI Agents that actually work together (@KanikaBK Twitter listicle)

- ソース: @KanikaBK Twitter/X listicle (canonical URL なし、テキスト貼り付け)
- 理由: topic family "multi-agent/subagent" saturated-pure-rehash (15 件目, delta=0)、直近 2026-05-25 `claude-agent-teams-7steps` で公式 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` flag 検証済み + 2026-04-11 Anthropic 公式 `multi-agent-coordination-patterns` で 5-Pattern 統合済み
- 根拠: 13 手法すべて既存カバー or N/A
  - Already (9): Think in tasks/not roles (=30-subagents Self-Rejection Rule + single-purpose CONFIRMED) / 4 Core Roles Orchestrator-Researcher-Specialist-Critic (=Anthropic 5-Pattern + code-reviewer/codex-reviewer/silent-failure-hunter) / 3 Architectures Sequential-Parallel-Hierarchical (=parallel-agent-worktrees-orchestration + Anthropic 公式) / Pattern 1 Structured Outputs (=output-format-decision-table.md) / Pattern 2 Quality Gates (=Codex Review Gate + completion-gate hook) / Pattern 3 Minimal Tools (=tool-scoping-guide.md) / Pattern 4 Retry with feedback (=failure-escalation-protocol + retrospective-codify) / Pattern 5 Log Everything (=session_observer + friction-events.jsonl) / 5 Mistakes 全件 (giant agent / no format / skip critic / memory overflow / no human oversight)
  - N/A (4): Tools stack Make/n8n/Relevance AI/LangGraph/Agno/AutoGen (no-code SaaS 文脈、dotfiles は Claude Code harness + cmux で代替) / 4 Real-world teams Lead gen-Competitive intel-Support triage-Newsletter (business team、個人 dotfiles 範囲外) / Quick start 48h plan (`/init-project` `/onboarding` で代替) / Critic specificity (codex-reviewer / code-reviewer で実装)
- 該当 family のキーワード hit: multi-agent, agent team, orchestrator, critic, sequential/parallel/hierarchical, structured outputs, quality gates, minimal tools, retry loop
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, ユーザー skip 選択)
- メタ: 著者 @KanikaBK は generic AI listicle 量産アカウント、MIT/Google Brain 引用も具体出典なし、anecdotal data のみ。Make/n8n SaaS バイアス強。saturation taxonomy が正しく機能し Phase 2 投入前に skip 確定 (N=15 件目で 7 連続 reject 系)

## [2026-05-26] ingest-skip | 【保存版】あなたのObsidianは死んでいる (Nainsi Dwiv tweet 翻訳記事)

- ソース: テキスト貼り付け (元 tweet `https://x.com/NainsiDwiv50980/status/2053498460918485092` の日本語翻案、著者: AI コンサル経営者 anonymous)
- 理由: topic family "obsidian-second-brain" saturated-pure-rehash (**N=16 件目**, delta=0、ambiguous 2 は harness 化価値なし)
- 根拠: 10 手法すべて既存 absorb (damidefi 2026-05-23 / Cyril 系 5 件) で完全カバー
  - Already (10): 4 層 Capture/Automation/Memory/Intelligence (=damidefi 完全カバー) / 5 動作モデル push back・contradiction surface (=damidefi T7) / 4 系統入口 Readwise/Whisper/Telegram/podcast (=damidefi Capture 層) / 夜の装置 cron 最小スクリプト (=damidefi Automation N8N、課金 SaaS 不採用方針) / CLAUDE.md 5 項目 (=damidefi 6 section とほぼ同一) / 朝のブリーフィング 3 カテゴリ (=damidefi Daily 4-section synthesis、Cyril 系で棄却済) / Vault に問う 5 つの問い (=damidefi T7 + /think skill) / 文脈蓄積=moat (=2026-04-24 harness-engineering で批判済、anecdotal) / 眠った Vault 診断 7 項目 (=vault-maintenance.sh 6 軸チェックで代替) / 5 ノート Day 1 手順 (=onboarding cadence、個人運用範囲)
- 該当 family のキーワード hit: obsidian, vault, second brain, capture, automation, memory, intelligence, claude.md, daily synthesis, moat
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, ユーザー skip + 現状受容 選択)
- 副次発見 (記事 absorb と独立): `vault-maintenance.sh --dry-run` 実行で **orphan note 74 件 / 98 ノート中 (orphan 率 76%)**、**04-Galaxy permanent note 1 件のみ**、Rare タグ 164 件を検出。記事の問題提起 (「整理済みだが繋がっていない」) が実際に起きている。命名/リンク/重複/stale は 0 件で構造管理は健全。ユーザー判断: 「Vault は受動アーカイブ、思考接続は MEMORY.md / docs/research/ で継続」既存方針を維持
- メタ: obsidian-second-brain family は damidefi (2026-05-23 N=10) 以降 6 連続で adopt ≤2 trend (Cyril one-folder=1 / cyrilxbt-organize-vault=2 / 本記事=0)、creator-monetization-driven AI second brain genre saturation 継続

## [2026-05-26] ingest | 45 AI Automations You Can Actually Build This Weekend With Zero Code

- ソース: テキスト貼り付け（著者不明、Cowork × MCP × 自然言語 listicle）
- 判定: Gap 0, Partial 0, Already 9 (#22 HN/arXiv/RSS=morning-briefing済, #45 tasks分類=weekly-review済 他), N/A 40+
- 取り込み: 採用 0 件
- Codex 誤り訂正: #22 Partial → Already (.config/claude/scripts/runtime/auto-morning-briefing.sh L103-160 に HN+arXiv+RSS 実装済み、Explore が scripts/runtime/ 別ファイルを参照してミス); #45 Partial → Already (weekly-review §2.5.1 Vault Inbox triage で 5 分類済み)
- Validation-only: docs/specs/2026-05-09-daily-knowledge-routines-design.md が "Design (plan 待ち)" のまま 17 日経過、要フォローアップ
- メタ: 記事は Claude.ai Cowork (PC 起動前提) 向けの marketing listicle。既存ハーネス (launchd + hooks + Claude Code CLI) が同等以上をカバー

## [2026-05-28] ingest | openclaw/agent-skills autoreview SKILL.md

- ソース: https://github.com/openclaw/agent-skills/blob/main/skills/autoreview/SKILL.md
- 著者: Peter Steinberger (@steipete), OpenClaw ecosystem
- Topic family: code-review-best-practices (5 件目, saturated-but-novel)
- 判定: Gap 4 / Partial 7 / Already 3 / N/A 6
- 取り込み: Bundle A+B 即実装 (S × 5)
  - `/review` SKILL.md Anti-Patterns #6 (nested reviewer ban) + #7 (cosmetic re-review ban)
  - `/review` SKILL.md Step 5 サイクルルール 8 (focused test rerun + review rerun)
  - `/review` SKILL.md Step 1.1 (diff scope mode 表 + "A clean local review only proves there is no local patch" caveat)
  - `agents/code-reviewer.md` Section H (rejected-finding inline comment rule)
- 保留: Plan 4 件 `docs/plans/active/2026-05-28-autoreview-absorb-plan.md` (T6 security suppression auditability M / T7 synthesis-report tests section S / T8 parallel closeout pipeline M / T9 cmux 30min SLA 弱 S)
- Phase 2.5 特記: Codex 両ルート (cmux worker TTY + codex exec stall) 失敗、Gemini grounding (5 主張 HIGH 確認: openclaw + agent-scripts + clawsweeper + gitcrawl + crabbox) + Opus self-critique で代替
- 分析レポート: `docs/research/2026-05-28-openclaw-autoreview-absorb-analysis.md`

## [2026-05-28] ingest | Codex Research Agent ワークフロー (中国語記事)

- ソース: 中国語記事「从0开始,十分钟搭建一个帮你筛选优质信息的Codex Research Agent工作流」
- 判定: Gap 3 / Partial 2 / Already 5 / N/A 1 (11 手法)
- 取り込み: T1 brief annotation 欄 (S) / T2 negative filter (S) / T3 weekly-review annotation 集計 + diff 提案 (M)
- 重要 safety: Codex 指摘で T3 は auto-update せず「diff 提案止まり、user 承認制」に降格
- レポート: docs/research/2026-05-28-codex-research-agent-workflow-absorb-analysis.md

## [2026-05-29] ingest-skip | How to Build an Obsidian Second Brain With AI: The Complete Guide Based on Karpathy's Framework
- ソース: @cyrilXBT (X creator, direct text paste, no URL)
- 理由: topic family "obsidian-second-brain" saturated-pure-rehash (16 件目 / Cyril 著者 7 件目, delta=0)
- 根拠: 全8手法が過去 absorb で評価済。特に damidefi (2026-05-23, family 10件目) が同型 (4-layer model + type-of-thinking folders + Six Claude Integrations + vault CLAUDE.md + daily synthesis) で adopted_count=0。T1(type-folders=N/A) / T4(CLAUDE.md=Already) / T5(daily synthesis=Sonnet imagination 棄却) / T7(contradiction=Partial 常時化禁止) は既決。Literature/Permanent note 区別は karpathy-second-brain-modified (2026-04-14) で既出
- 該当 family のキーワード hit: obsidian, second brain, vault, PARA, Map of Content, permanent note
- スキップ判定: Phase 1.5 gate (user 承認, skip 推奨)
- Stale-Plan Audit (Step 7): 直近3件 (organize-vault 2026-05-25 / damidefi 2026-05-23 / one-folder 2026-05-22) すべて 30 日未満 → audit skip (実装猶予期間内)

## [2026-05-30] ingest-skip | Claude Can Do All of This. Most People Have No Idea.
- ソース: generic feature listicle (direct text paste, no URL)
- 理由: topic family "claude-code-tips" saturated-pure-rehash (14 件目, delta=0)
- 根拠: 同型記事 12-claude-features-top-operators (2026-04-04) が既存。17項目すべて N/A か Already — consumer機能(#1 Projects/#2 Artifacts/#5-9 役割プロンプト/#10 Chrome/#16 Design)=N/A、harness系(#3 Thinking/#4 Memory/#11 Cowork/#12 Scheduled/#13 Skills/#14 CLAUDE.md/#15 Claude Code)=Already、#17 Prompt Caching=Already深掘り済(2026-05-22 Anthropic Engineers Token Savings で TTL三層/cache_control/model switch invalidation まで absorb)。新規論点ゼロ
- 該当 family のキーワード hit: claude features, projects, artifacts, memory, skills, CLAUDE.md, scheduled tasks, prompt caching
- スキップ判定: Phase 1.5 gate (user 承認, skip 推奨)

## [2026-05-30] ingest | The Claude Opus 4.8 Setup Guide (zodchixquant)
- ソース: zodchixquant (Telegram 宣伝 listicle, https://t.me/zodchixquant)
- 判定: Gap 1 / Already 5 / N/A 4 (10 手法), claude-code-tips family 15 件目 (同著者 2 件目)
- 取り込み: #4 Fast Mode 用途指針 (S) — resource-bounds.md に「いつ /fast」表を追記 (speed>depth vs standard)
- validation-only: Opus 4.7→4.8 drift を debug-thinking-summary.md:59 に保守的修正 (設定値不変・4.8 公式 docs 要再確認の ⚠️ 注記)。qualitative-signals-spec.md:38 の opus-4-7 ハードコードは報告のみ
- fabrication flags: `CLAUDE_CODE_DEFAULT_EFFORT` (公式は EFFORT_LEVEL の可能性) / `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` 推奨 (Opus 4.7+ で no-op) / コスト 50% 削減主張 (検証不能)
- Phase 2.5: Gemini quota fail + Codex silent exit、2 系統同時失敗 → Opus self-critique fallback (#6 budget cap を Gap→N/A 降格)
- レポート: docs/research/2026-05-30-opus48-setup-guide-absorb-analysis.md

## [2026-05-30] ingest-skip | I Turned Claude Opus 4.8 Into My Entire AI Operating System (Nate)
- ソース: creator-monetization listicle (Nate / Skool, direct text paste, no URL)
- 理由: 厳密キーワードでは family 不成立 (PASS) だが実体は creator-monetization 系 listicle ジャンル。delta≈1 (borderline)、user 承認で skip
- 根拠: 全8手法が既存カバー — Context-is-moat=Already(CLAUDE.md/MEMORY core philosophy) / Instructions≠Capabilities+150k通の教訓=Already(references/tool-scoping-guide.md + mcp-audit VeriGrey Tool Filter + careful skill) / Bike method 段階的自律=Already(requires-escalation rubric in agent-design-lessons.md + grey rollout) / Forward+Reverse skill building=Already(skill-creator + retrospective-codify) / /insights 自己使用監査=Already(analyze-tacit-knowledge + /improve + session_observer + friction-detection) / /session-handoff=Already(checkpoint + recall) / Four C's・Three M's=N/A(命名フレームワークで機構ではない) / Connections audit 7-bucket=N/A(個人ビジネス向け MCP 接続、dotfiles 用途外)
- borderline delta: 「/insights が "毎日再プロンプトしていた skill" を浮かび上がらせる自己使用 HTML 監査」のみ distinct だが skill-audit + analyze-tacit-knowledge で Partial カバー
- 該当 family のキーワード hit (概念): AI operating system, second brain, context-as-moat, skills, session handoff, tool scoping, autonomy phases
- スキップ判定: Phase 1.5 gate (user 承認, skip 推奨)

## [2026-05-30] ingest-skip | Andrej Karpathy says 99% of AI users are missing 7 basics
- ソース: generic Karpathy "7 tips" listicle (direct text paste, no URL)
- 理由: topic family "karpathy-knowledge-base" saturated-pure-rehash (8 件目 / claude-code-tips としては 16 件目, delta=0)
- 根拠: 7手法すべて評価済。TIP1 context完全性=search-first/feedback full-error、TIP2 CLAUDE.md 5項目=IFScale/feedback_claudemd_length/revise-claude-md、TIP3 /raw /wiki 三層=karpathy KB absorb ×7 (2026-04-03〜04-20)+docs/wiki/+3層メモリ、TIP4 永続保存=Obsidian /digest /note+memory schema、TIP5 index.md+log.md=docs/wiki/log.md 実在+MEMORY.md=map、TIP6 intern+incremental=KISS+reference_karpathy_llm_coding.md 4失敗パターン。TIP7 HTML出力=2026-05-09 html-effectiveness で明示 Reject (2026-05-21 再確認で強化)。新規論点ゼロ
- 該当 family のキーワード hit: karpathy, CLAUDE.md, wiki, raw, index.md, log.md, context, incremental, HTML
- スキップ判定: Phase 1.5 gate (user 承認, skip 推奨)

## [2026-05-30] ingest-skip | How to Actually Vibe Code. 20 Rules (Khairallah)
- ソース: @eng_khairallah1 vibe-coding listicle (direct text paste, no URL)
- 理由: topic family "claude-code-tips" saturated-pure-rehash (16 件目 / Khairallah 著者 4 件目, delta=0)
- 根拠: 20 ルール全て既存機構でより深くカバー。Rule1 think-first=/spec+brainstorming+search-first / Rule2 Plan Mode=EnterPlanMode+/rpi+PLANS.md / Rule3 describe outcome=/spec(Prompt-as-PRD) / Rule4+8 screenshot=image-to-code-skill+ui-observer+webapp-testing / Rule5+17 CLAUDE.md=運用済+IFScale / Rule6 one-feature=task-decomposition-guide / Rule7 test-after=verification-before-completion / Rule9 git commit=/commit+lefthook / Rule10 stuck→angle=failure-escalation-protocol+/clear / Rule11 /compact=context-constitution+PreCompact hook / Rule12 what-NOT-to-do=core_principles(YAGNI/overengineering ban) / Rule13-16 design=frontend-design+taste-skill+ui-ux-pro-max+web-design-guidelines / Rule18 one-conversation=session-protocol / Rule19 BUILDLOG.md=RUNNING_BRIEF.md+/checkpoint+/daily-report / Rule20 ship-first=/spike philosophy。新規論点ゼロ
- 前提不一致: 記事は明示的に "complete beginners who just get errors" 向け、senior-engineer harness とは前提が根本的に不一致
- 該当 family のキーワード hit: vibe coding, CLAUDE.md, Plan Mode, /compact, one feature at a time, ship, BUILDLOG
- スキップ判定: Phase 1.5 gate (user 承認, skip 推奨)

## [2026-05-30] ingest-skip | I Built a 5 Tool AI Stack Where Each Tool Does Something the Others Cannot (@damidefi)
- ソース: @damidefi X listicle (direct text paste, no URL)
- 理由: AI-tool-stack listicle family 5 件目 + obsidian-second-brain family 8 件目、saturated-pure-rehash (delta=0)。同一著者 @damidefi は 2026-05-23 に採用 0 件で処理済み
- 根拠: 全 15 手法 (5 ツール × 3 機能) が既存カバーまたは N/A。Already=3層モデルルーティング(model-routing.md) / worktree 並列(dispatching-parallel-agents+EnterWorktree) / skill-file 永続メモリ(session-learner+Hermes absorb x2: 2026-04-14/2026-04-17) / NL cron(/schedule+auto-morning-briefing.sh) / vault 複利メモリ(/digest+obsidian-knowledge) / Projects+MCP(MCP 統合運用済)。N/A(外部ツール固有)=Kimi K2.6 DeepInfra API / Cursor Design Mode・Cloud handoff / 300-agent swarm(Subagent Count Ceiling で警戒済) / Telegram+N8N bot / Hermes self-host。採用済み reject=Daily 4セクション synthesis は 2026-05-23 damidefi 同一著者で採用 0 件
- 過去 stack listicle (全 reject/reference-only): claude-full-ai-stack-2026 / claude-only-stack-cyrilxbt / three-model-stack(skool.com promo) / missing-layer-agentic-stack
- creator-monetization シグナル: "Follow @damidefi… journey to 100K. Bookmark this. Share it" + 未検証マーケ数値(95%/70%/73k stars/647 skills/300 agents)
- 該当 family のキーワード hit: AI stack, tool stack, Obsidian, second brain, model routing, swarm orchestration, worktree, skill files, MCP
- スキップ判定: Phase 1.5 gate (user 承認, skip 推奨)

## [2026-05-30] ingest-skip (light Phase 2, adopt=0) | You're Not Slow. You're Single-Threaded: Commanding 300 Agents from One Prompt
- ソース: anonymous Kimi-team-collaboration article (direct text paste, no URL)。末尾 Disclosure で「I worked with the team behind Kimi」明示 = ベンダー記事
- 理由: topic family "multi-agent-orchestration" 重複領域 (関連 absorb 6 件: 30-subagents/multi-agent-coordination/MoE/PostHog/token-savings/CORAL, 採用率高) → 形式 PASS(warning) → user 選択 light-phase2
- 判定: Phase 2 まで検証したが全て Already/N/A、採用 0 件確定。analysis report: docs/research/2026-05-30-single-threaded-300-agents-absorb-analysis.md
- 根拠 (novel candidate 3 点のみ Sonnet Explore 検証): (1) Auto-recovery=collect-result.sh:78-94 retry(MAX_RETRY=2)+escalate でカバー、reassign-to-different-worker は Kimi 300-pool 前提で N/A、confident-wrong は verification-before-completion+codex-reviewer 担当 / (2) Job-shape triage gate=subagent-delegation-guide.md Task Parallelizability Gate (embarrassingly parallel vs 逐次推論, Google Research 2025 実証) で完全包含 / (3) Plan review-before-run=codex-plan-reviewer.md + workflow-guide.md Plan gate + research/SKILL.md Step 2 承認で dotfiles の方が手厚い。コア 14 手法は Workflow tool(pipeline/parallel/fan-out + over-engineering 警告) で網羅
- ベンダー数値 (300 agents/80% faster/4.5x) は vendor figures につき採用根拠にせず (著者自身 caveat: "still gets individual facts wrong. Verify before you act")
- 先行裏付け: 同 300-agent swarm トピックは 2026-05-30 damidefi stack absorb でも「Subagent Count Ceiling で警戒済」N/A 判定済
- meta: `multi-agent-orchestration` を topic-family-saturation.md taxonomy 追加候補 (別 skill 改善タスク)。ただし採用率高 family なので gate 主目的の永続ループ検出には合致しにくい
- 該当 family のキーワード hit: orchestrator, swarm, sub-agent, parallel, auto-recovery, decompose, scoped memory, job shape

## [2026-05-30] ingest | 14 sub-agents I built in 60 days, 4 survived

- ソース: 個人ブログ/listicle (subagent 60日実験記録)
- 判定: Gap(modest) 1 / Partial 1 / Already 10 / N/A 2 + drift 訂正 1
- 取り込み (S×2 実装済): #10 決定的CLIラッパー禁止を subagent-delegation-guide.md anti-pattern 表に1行 / #6 add-agent.md に Step 0 go/no-go preflight 統合
- Validation-only: agent count drift 33→22 を agent-design-lessons.md (3箇所) + docs/wiki/INDEX.md:37 で訂正 (Count Ceiling 判断材料の腐敗)
- Phase 2.5: Codex (read-only) +Gemini (grounding) 並列。Codex「厳密には採用0+drift訂正、最大でも#10を1行」で Pass2 over-judgment を修正。add-agent.md 存在 + INDEX.md 2箇所目 drift を発見
- レポート: docs/research/2026-05-30-14-subagents-4-survived-absorb-analysis.md

## [2026-05-30] ingest (light Phase 2) | How to Build an Obsidian System That Turns Every Note You Take Into Something You Actually Use (@cyrilXBT)

- ソース: @cyrilXBT 記事 (direct text paste)。`@cyrilXBT` follow 誘導で締める常連 listicle author
- 判定: obsidian-second-brain family **16 件目 / Cyril 6 件目**。PASS-warning (採用率 >= 20%) + delta=2 → light-phase2 (user 選択)
- 採用 **2 件 (S)**: (A1) `templates/obsidian-vault/00-Inbox/_templates/capture.md` 新設 — Three Capture Conventions (CONNECTS TO / MIGHT USE FOR / RAISES QUESTION / COULD APPLY / ACTION) を optional セクション化、/note の即時性は不変 / (A2) `obsidian-knowledge` skill に機能8「意思決定フィード」追加 — decision → vault scan → Supports/Challenges/Adds nuance brief、vault 外情報を加えない制約明記、/decision・/think decision と責務分離
- Reject 6 件: Three Zones=IPARAG 既採用 / Output フォルダ=docs+git 管理 / CLAUDE.md テンプレート=既存 / Weekly Note Audit=vault-maintenance.sh / Daily Processing・Connection Surface・Output Generator=timekeeper+obsidian-knowledge+digest 代替済 / contribution rate=harness 化過大 YAGNI
- 検証: `task validate-configs` ok
- レポート: docs/research/2026-05-30-cyrilxbt-notes-into-output-absorb-analysis.md
- meta: delta=2 が2件とも真の Gap (organize-vault delta=1 に続く novel 実在)。Five Workflows を rehash と切らず1つ1つ既存 skill 照合した結果 Decision Feeder/Capture Conventions だけ空白確定。新 skill 化せず obsidian-knowledge 拡張に倒した

## [2026-05-30] ingest | How Claude Code Harness turns agent coding into a contract-first delivery loop (AlphaSignal / Chachamaru127)

- ソース: https://github.com/Chachamaru127/claude-code-harness
- family: harness-engineering (N≥5, PASS-warning), focused absorb (手法 delta≫2)
- 判定: Gap 4 (#3/#4/#5/#6), Partial-drop 1 (#2 codegen), N/A 2 (#1 Go runtime/#7 release), Already強化不要 3 (#8/#9/#10)
- 取り込み: 「config codegen ではなく auditability」に収束。#6 retired-concepts registry (P1/S) / #5 doctor:stale inventory-only (P2/S-M) / #4 fail-open/closed 一覧 (P3/S) / #3 deny rules カタログ (P4/M)
- Phase 2.5: Codex (2回目で実批評、AGENTS.md swallow 回避は prompt 冒頭で「doc 読込不要」明示) + Gemini grounding (projen/KCL/eslint-plugin-deprecation)
- 特記: ユーザー指摘「該当するから省略は違う」で全 10 項目を Pass 2 対象に。exists 項目も強化分析必須を再確認
- レポート: docs/research/2026-05-30-claude-code-harness-absorb-analysis.md
- プラン: docs/plans/active/2026-05-30-harness-auditability-absorb-plan.md (全件 /rpi 予定)

## [2026-05-30] ingest (light Phase 2) | Hermes Harness Architecture

- ソース: Hermes Harness Architecture (記事テキスト貼り付け、Hermes = NousResearch)
- 判定: Gap 1 / N/A 1 / Already 3 (novel 5 項目中)
- 採用: 1 件 — T1 cwd context ファイル injection スキャン (SessionStart hook `scan-context-files.py`)
- Saturation: harness-engineering family 6 件目 (N=5, 採用率 ~40% PASS warning, delta 高 → light-phase2)
- Stale-Plan Audit: cursor-harness → retired (採用0) / self-healing → implemented (Tri-judge=Phase 2.5)
- Phase 2.5: 省略 (light-phase2、Gap が bounded security のためユーザー判断で省略)
- 特記: 記事は OSS harness 内部解剖。大半は Claude Code 上で再実装不能 (N/A)。「best open harness」ベンダートーンは単独採用根拠にせず threat model 実在性で item 1 のみ採用。記事が挙げる Hermes の欠陥 (durable child-run) は cmux Worker で既に保有
- レポート: docs/research/2026-05-30-hermes-harness-architecture-absorb-analysis.md
- 実装: scan-context-files.py 作成 + settings.json SessionStart 登録 (検証済: ruff/validate-configs)
- Review Gate: 3-way (code/codex/security) で HIGH 1 + MEDIUM 2 修正 → codex 再レビュー PASS。U+202E Trojan Source (CVE-2021-42574) 取りこぼしを bidi/format 広域化で修正、prompt-injection-detector.py も同期。shell base64 + symlink 拒否追加。codex「未登録」指摘は False Positive 却下

## [2026-05-30] ingest-skip (validation-only) | damidefi: I Connected Hermes Agent to My Obsidian Vault
- ソース: damidefi (X), Hermes Agent × Obsidian Vault 体験談
- 判定: topic family "obsidian-second-brain" saturated-pure-rehash (N=15+, 採用率 ~0%, delta=0)。同記事は 2026-05-23 absorb 済・採用0。記事 absorb は skip。
- ただしユーザー引数「保存はできているが参照しているか怪しい」で article-triggered の実 gap 調査に pivot。
- 調査結果: Vault WRITE 経路は機能 (/note, /digest, /timekeeper, sync-memory-to-vault.sh)。READ は MANUAL のみ機能 (/think→06-Areas/thinking-context.md, obsidian-knowledge, /timekeeper)。PROACTIVE read = 0 件 (SessionStart は agent-memory のみ、vault 未ロード)。memory→Vault 単方向 (cc-7-layer-memory-model.md:70,79)。
- Explore 誤報訂正: 「skill は仕様のみ実装なし」は誤り。SKILL.md (allowed-tools: Read) 自体が実装、別途 .sh 不要。
- 採用: CLAUDE.md (.config/claude/CLAUDE.md) に <important if="design/judgment/research 継続"> ブロック追加 (proactive vault 参照指示、関連フォルダ限定、snapshot caveat 付き)。option A=instruction-first。検証: task validate-configs PASS。
- 昇格トリガー: instruction で vault 参照が安定しなければ option B (SessionStart hint hook) に昇格。

## [2026-05-31] ingest | My Agent Stack For Automating My Personal Life (Nicolas Bustamante)

- ソース: Nicolas Bustamante 記事（貼り付けテキスト）
- family: personal-life-automation（新分野 N=1, Saturation Gate PASS）
- 判定: Gap 2（A 信頼性ラダー / E 操作信頼ティア）, Already 5, N/A 2
- 取り込み: cli-discovery.md に「2 つの直交ラダー」セクション追加（ツール表面信頼性 × 操作信頼ティア）
- メタ: Opus の Already ハロシネーション罠を検出 → feedback_absorb_already_hallucination.md 新設
- レポート: docs/research/2026-05-31-personal-agent-stack-absorb-analysis.md

## [2026-05-31] ingest-skip | I Searched the Whole Claude Skills Ecosystem - These Are the Ones That Matter (@polydao)
- ソース: @polydao (X/Buzzoni Notes), Claude skills ecosystem listicle（32 リポジトリ/skill リンク集）
- 判定: topic family "skill-catalog-listicle" (taxonomy 未登録だが MEMORY.md 実績で N>=7 飽和) saturated-pure-rehash (delta=0)
- 根拠: 過去事例 — Top 67 Skills (4-19, 2 採用) / 100+ Best 6 (5-06, 5 採用) / 30 Sub-Agents (5-02, 4 採用) / SKILL.md 15min Guide (4-26, 採用0) / Claude Skills 6 法則 (4-29, 既実装) / mattpocock (4-29, chain) / Anthropic Complete Guide (5-23, 5 採用)
- delta=0 理由: 提唱 skill は全て dotfiles 既存 — skill-creator/skill-audit (作成・検査) / AutoEvolve (self-improving) / worktree workflow / /audit (tech-debt) / document-factory (doc-coauthoring) / /research+recall+docs/plans (persistent research) / MCP 統合済み。外部 skill (Composio connect-apps, Apollo, email triage, rag-architect, observability-designer 等) は personal/business automation 領域で coding harness 範囲外 (N/A)
- 質的評価: 純粋な monetization-driven リンク集 ($95K vs $300K / Telegram channel 誘導 / Like+Repost 依頼)、具体的 rubric ゼロ。Boris 30 Tips / Khairallah 40 Features と同型 (採用 0 パターン)
- キーワード hit: skills / ecosystem / catalog / stack
- スキップ判定: Phase 1.5 gate (ユーザー明示選択 skip)
- 副次: 追記時に log.md 行 1184-1203 の未解決 git コンフリクトマーカー (commit 65e8326 由来) を発見・解消 (両エントリ damidefi/personal-agent-stack を保持)

## [2026-05-31] ingest (採用 0) | How To Fix AI Slop (Using Hermes)
- ソース: How To Fix AI Slop (Using Hermes) — ベンダーマーケティング記事 (Hermes 2 件目)
- 判定: Already 2 / Partial 4 / N/A 2 / (採用 0)
- 結論: Reference-Only。dotfiles の eval 基盤 (5 reviewer + consensus + benchmark-dimensions + skill-audit + scripts/eval/) は Hermes primitive より成熟。最重要 move (#10 auto-close-loop) は /improve として 2026-05-03 意図的 retire 済み
- Phase 2.5: Codex が Opus の Already 過大評価 3 件是正 (#2/#8 →Partial, #5 "より高度"削除) / Gemini grounding が auto-loop の Self-Preference Bias・Model Collapse・Oracle 問題で棄却根拠を補強
- レポート: docs/research/2026-05-31-hermes-ai-slop-eval-loop-absorb-analysis.md

## [2026-05-31] ingest | How To Fix AI Slop (Using Hermes)

- ソース: Hermes vendor marketing article (pasted text)
- 判定: Gap 0 / Partial 0 / Already 7 (3層: Primitives稼働/Active loop Retired/Signal-to-action Partial) / N/A 1
- 取り込み: 0 件 (全 primitives 実装済み、eval loop は 2026-05-03 /improve retire で意図的無効化、gap は observability-signals.md で文書化済み)
- family: eval-loop / harness-quality-gate (SATURATED-pure-rehash, delta=0)
- 反証データ記録: 自動 self-improvement loop = false-positive slop 製造機、approval button は precision を解決せず noise を UX に転嫁。次回 eval-loop 系 absorb の judgment anchor
- レポート: docs/research/2026-05-31-hermes-eval-loop-absorb-analysis.md

## [2026-05-31] ingest-skip | Hermes Agent Masterclass: The Complete Course From Zero to Full Autonomous Agent Operation
- ソース: Hermes vendor marketing article (pasted text), URL記載 github.com/hermes-agent/hermes は実在せず
- 理由: topic family "hermes" saturated-pure-rehash (8 件目, 直近 3 件採用 0, delta=0)
- 根拠: 記事の全機能 (CLAUDE.md constitution / Markdown skills / SQLite memory / cron scheduler / MCP / 4-agent pipeline / quality gates / weekly review / 90-day build) は Claude Code + dotfiles に既存。Section 5 morning-briefing は 2026-04-14 personal-analyst absorb で auto-morning-briefing.sh 実装済み
- 実在性 grounding (Gemini): hermes-agent/hermes は不在、実在は NousResearch/hermes-agent = 「Claude Code 機能セットのリブランド/進化版クローン」。差別化は model provider 非依存 (Ollama) と Telegram/Slack のみ、本 harness では二重管理負債
- 導入判断: 不要 (新規 capability ゼロ、成熟 harness の後退)。creator-marketing パターン (claude-opus-4-5 旧モデル名 / FOMO 煽り / moat 連呼 / cyrilXBT format 言及)
- 該当 family のキーワード hit: hermes / autonomous agent / CLAUDE.md / skill / memory / scheduler / MCP / multi-agent
- スキップ判定: Phase 1.5 gate (ユーザー明示選択: log.md 1行で閉じる)

## [2026-05-31] ingest (light Phase 2, adopt=1) | 4-Agent Pipeline (Planner→Coder→Tester→Reviewer)

- ソース: "How to build a 4-agent team that ships a feature while you sleep" (zodchixquant, Telegram-promoted / Teamly SaaS 集客)
- family: multi-agent-orchestration (N≥5, delta≈0 pure-rehash、user continue 選択)
- 判定: Gap 0 / Partial 0 / Already 4 / N/A by design 3
- 採用 (1, S): test-engineer.md に `### On Test Failure (Role Boundary)` 追加 (prod バグ起因のテスト失敗は自分で直さず報告して STOP)
- 不採用: 固定 4-agent pipeline / `.pipeline/` shared folder / `/ship` orchestrator (Implicit Coordinator + S/M/L 動的分岐と衝突) / cross-link (verification-before-completion+/review 連鎖で冗長と実証)
- Phase 2.5: Codex (exit 0)「採用0が妥当」→ user「手抜きしてない？」challenge で /rpi・test-engineer.md 実読し採用1に精緻化。Gemini quota 枯渇で Codex 単独判定
- レポート: docs/research/2026-05-31-4-agent-pipeline-absorb-analysis.md

## [2026-05-31] ingest | Cursor Auto Review 実行モード

- ソース: https://cursor.com/ja/changelog/auto-review (Cursor 3.6 changelog, 2026-05-29)
- 判定: Gap 0 / Partial 2 (低優先) / Already 3 / N/A 1 (意図的 Reject)
- 取り込み: 新規採用 0 件 (Codex+Gemini+Opus 三者一致)。validation-only follow-up として permission-audit 棚卸し実施 (結果クリーン: allow 71/deny 102、pruning candidate なし、scope-creep なし)
- 核心 #4 分類サブエージェント三値判定 (allow/別アプローチ/ask) は determinism boundary 違反 + prompt injection リスクで意図的 Reject。記事タイトル "auto-review" だが内容は permission/autonomy/sandbox で code-review-best-practices family と誤分類回避
- family: none (permission/autonomy/sandbox、既存 taxonomy 4族に非該当、新分野扱いで PASS)
- レポート: docs/research/2026-05-31-cursor-auto-review-run-mode-absorb-analysis.md

## [2026-05-31] ingest | Zero Trust for AI Agents (Anthropic 公式 eBook)

- ソース: https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/6a1611a04085d7cd3dadc924_Claude-eBook-Zero-Trust-for-AI-Agents-05182026.pdf
- 判定: Gap 1 (observability why→ops層), Partial→Agent-BOM-lite 1, N/A 7 (暗号系/SOAR/AI-BOM完全版), Already 6 (全12原則 exists)
- 取り込み: 運用メタ層 3 タスク全採用 (L) — Agent-BOM-lite / why observability decision log / 個人版 8-phase checklist。Phase 2.5 で Codex が Opus の 1st-party 過小評価 self-bias を修正
- プラン: docs/plans/active/2026-05-31-zero-trust-absorb-plan.md (Codex Spec/Plan Gate + 新セッション /rpi)
- レポート: docs/research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md

## [2026-05-31] ingest-skip | The Exact Obsidian Daily Note System I Use to Never Lose an Idea Again

- ソース: テキスト貼り付け (@damidefi on X, 直 URL なし)
- 理由: topic family "obsidian-second-brain" saturated-pure-rehash (15 件目, delta=0)
- 根拠: @damidefi 本人の 2 件目 — 前回 2026-05-23 (family 10 件目) は reference-only / 採用0。本記事の手法はすべて既出 or N/A: Telegram bot/N8N synthesis/Evening review prompt/Weekly rollup は前回 damidefi T2/T3/T5/T6 で既判定、新ツール名 Templater 自動 daily / QuickAdd 4-capture の 2 件 (ambiguous) も harness 範囲外の個人 Obsidian plugin 設定で /note + auto-morning-briefing.sh に意味的同等
- 該当 family のキーワード hit: obsidian, daily note, quickadd, templater, vault, second brain, weekly rollup
- スキップ判定: Phase 1.5 gate (user choice: skip 推奨)
- 直近トレンド: Cyril 系 + damidefi の連続 reference-only ストリーク継続 (前回 meta-finding「trending reject 閾値」シグナルの再確認)

## [2026-06-01] ingest-skip | Claude Code + NotebookLM + Obsidian: Research Monster That Gets Smarter Every Time You Use It

- ソース: テキスト貼り付け (creator-monetization listicle, 直 URL なし)
- 理由: topic family "obsidian-second-brain" saturated (18 件目, 採用率 <20%, delta≈0-1)
- 根拠: 中核 2 機構が両方とも過去 absorb で明示却下済み — ①NotebookLM offload (notebooklm-py 非公式 API) は `2026-04-10-notebooklm-claude-extend-sessions` で「非公式API / Master Brain 採用却下」、②「Vault=記憶層 / claude.md が好みを学習」は記事が memory→Vault 同期を逆方向に主張するが `cc-7-layer-memory-model.md` で Vault は単方向同期スナップショット (AI reasoning input ではない) と確定済み。Skill Creator / pipeline skill 統合 / 週次 claude.md 更新は Already (skill-creator + /epd /rpi /dispatch + AutoEvolve + /profile-drip の上位互換)。唯一の未実装手法 yt-dlp YouTube engagement 検索は content-creator/niche 分析特化で Go/TS harness-engineering 文脈に N/A
- 該当 family のキーワード hit: obsidian, vault, second brain, notebooklm, claude.md learns preferences, pipeline skill
- スキップ判定: Phase 1.5 gate (user choice: skip 推奨)
- 直近トレンド: obsidian-second-brain family の reference-only/skip ストリーク継続 (Cyril → damidefi×2 → 本記事)。creator-monetization 系「使うほど賢くなる」framing は構造的低収率の再確認

## [2026-06-01] ingest-skip | How to build a team of AI agents: 9 stages from first agent to production crew

- ソース: movez.substack.com (creator-monetization 系 generic listicle, "fresh AI alpha")
- 理由: topic family "multi-agent-orchestration" saturated (7+ 件目)。9 ステージ全てが既存実装に 1:1 マッピング (Pass 1 Explore で実ファイル裏付け済: 8 stage exists / Stage 6 shared task list partial / Stage 8 trajectory sequence assertion のみ not_found だが単一ユーザー harness では AutoEvolve + session-trace-store が analog で N/A)
- 根拠: 過去 absorb — Multi-Agent Coordination Patterns (2026-04-10) / 30 Sub-Agents (2026-05-02 採用4) / MoE / PostHog Agent-First / CORAL / Khairallah 40 Features (採用0)。記事は Claude Agent SDK 自作製品向けで dotfiles harness と前提相違 (loop 制御 / context engineering / permissions は CC runtime + 既存 hook が機構として保有)
- 該当 family のキーワード hit: multi-agent, orchestrat, subagent, agent loop, shared task list, permissions, eval, trajectory
- スキップ判定: Phase 1.5 gate (SATURATED, user choice: skip 推奨)
- borderline 論点 (将来 revisit 用、今回不採用): Stage 8 trajectory_must_include = ツール呼び出し順序の sequence assertion。session-trace-store.py は順序を記録するが「正しい sequence であるべき」の assert は未実装。個人 harness では AutoEvolve reactive ループが既存 analog のため Gap 価値低

## [2026-06-02] ingest | コードレビュー6段階と AI/人間の境界

- ソース: https://zenn.dev/kenimo49/articles/code-review-6-stages-ai-human-boundary
- 判定: Gap 0, Partial→採用 2 (手法5,8), Already 4, N/A 多数 (チーム前提手法)
- 取り込み: review skill に Negative Signal Review Rule (AI 沈黙=盲点シグナル) + ADR template に機械照合フィールド (Verification: affected paths/invariants/verification command)
- 分析レポート: docs/research/2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md

## [2026-06-02] ingest-skip (light Phase 2, adopt=0) | How to actually use Claude: 14 steps

- ソース: movez (Substack) — "How to actually use Claude: 14 steps that unlock 100% of its potential and replace 10 apps"
- 理由: topic family "claude-code-tips" generic-listicle 12 件目。SATURATED-but-novel (採用率 < 20%、初期 delta=2)。Khairallah 40 features (2026-05-22) とほぼ同一ジャンル・同一機能群で採用 0 を再現
- 根拠: Phase 2 (light) まで検証したが novel 2 件 (Voice mode + Quick Entry / Microsoft 365 add-ins) は両方 consumer GUI 機能で dotfiles harness にスコープ外 → N/A 確定。修正後 delta=0 (2026-03-25 everything-guide で既に同 N/A 判定済み、初期 delta 計算は直近 3 レポートのみ照合の盲点)
- 該当 family のキーワード hit: claude-code-tips, generic listicle, how to use claude, N steps/features, projects/artifacts/connectors/memory/styles/cowork/routines/api
- スキップ判定: Phase 1.5 gate → light-phase2 (user choice) → adopt=0
- 分析レポート: docs/research/2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md

## [2026-06-02] ingest-skip | Obsidian×Claude Skillsで第二の脳を勝手に構築する方法 (東大Obsidianオタク)

- ソース: テキスト貼り付け / 出典 x.com/polydao/status/2042203352054771748 (creator-monetization 系, フォロー誘導・「1%以下」煽り)
- 理由: topic family "obsidian-second-brain" saturated-pure-rehash (N=19件目, 採用率 <15%, delta=0)
- 根拠: 7 手法すべて既知。中核の Karpathy compiler/librarian 方法論は 2026-04-12-karpathy-skills-analysis.md で既 absorb。3-folder minimal=cyril one-folder/damidefi delete-90%、整理するなクリップしろ=/note inbox、6ステップ運用=obsidian-claude-code-meta、Claude Skills 型化=dotfiles skill 群、MCP for Obsidian=既存 obsidian plugin + mcp__obsidian (mcp-audit.py enforced)、週次 Health Check=damidefi pruning-first + check-health + memory-pruning playbook
- 該当 family のキーワード hit: obsidian, vault, second brain, karpathy, raw/wiki/reports, claude skills, mcp obsidian, health check
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, user choice: skip)
- user 関心 (記事と独立): Slack 情報散乱の実課題 → 記事 absorb とは別途、既存仕組みでの提案を実施 (採用件数には数えない)
- 直近トレンド: obsidian-second-brain family の skip ストリーク継続 (cyril → damidefi×2 → 本記事)。記事側に新規論点ゼロ

## [2026-06-02] ingest-skip | THE 30-MINUTE OBSIDIAN SYSTEM (retrieval-first second brain)

- ソース: 貼り付けテキスト (creator-monetization 系 second-brain ガイド、著者不明)
- 理由: topic family "obsidian-second-brain" 18 件目、SATURATED-borderline (delta≈1)。記事 absorb は skip、user choice = skill-validation のみ
- 根拠: 全手法既知。3 properties=PKM 定番 / 7秒キャプチャ=/note / Decision Feeder=obsidian-knowledge §8 + CLAUDE.md:51 判断時 shallow grep + /think decision / Weekly review+update CLAUDE.md=前提衝突 (Vault は memory→Vault 単方向スナップショットで AI reasoning input ではない、cc-7-layer-memory-model.md:70) / contribution-rate=damidefi signal-density・pruning-first と意味的同値で既 internalize
- 記事核心の前提不一致: 「Claude が vault 全体に read access を持つ queryable layer」＝ Vault live read。dotfiles は wiki/log.md:1229 で「READ は MANUAL のみ、PROACTIVE read=0 件、vault 未ロード」と既結論。記事の批判 (capture はできるが retrieval 自動化されない) は既知
- 該当 family のキーワード hit: obsidian, second brain, vault, PARA, wikilinks, retrieval, contribution rate, decision feeder
- スキップ判定: Phase 1.5 gate (SATURATED-borderline, user choice: skip article + skill-validation only)
- 直近トレンド: obsidian-second-brain skip ストリーク継続 (cyril → damidefi×2 → karpathy → 本記事)
- **validation-only follow-up (記事と独立、採用件数に数えない)**: 既存 obsidian skill 群の retrieval 点検で latent drift 1 件検出 → `06-Areas` 参照不一致 (CLAUDE.md:51 + think/SKILL.md ×5 が `06-Areas/` を読み書きするが、正準 PARA 構造は `02-Areas`、`06` は `06-Archive`)。実 Vault が `02-Areas` の場合、判断時 shallow grep が空振り + /think が `06-Areas` フォルダ誤生成 (SKILL.md:278 で存在しなければ新規作成)。実 Vault が permission denied で確定不可 → user verification 待ち

## [2026-06-02] ingest (light Phase 2, adopt=0, reference-pointer) | agents-best-practices (DenisSergeevitch)

- ソース: https://github.com/DenisSergeevitch/agents-best-practices (provider-neutral Agent Skill, MIT, ⭐1486)
- 判定: harness-engineering family 飽和 (N≥5, 直近2件連続 reject: Cursor harness + Hermes)。Step 4.5 連続 reject trend 発火。user choice = light-phase2
- 検証: novel 3点のみ Phase 2 (Phase 2.5 省略)。#1 provider-neutral×非コーディング多ドメイン MVP-blueprint=Partial(Gap寄り) / #2 coverage-audit=Already(/skill-audit) / #3 external skill 管理=Already(skills-lock.json)。8原則本体は全 Already
- 取り込み: 0 件。user choice = reference pointer のみ (Pruning-First: 90% 既実装スキルを 67 個目に追加せず、MEMORY.md 外部参照に1行記録)
- 使い道: チーム/非コーディング/多プロバイダ agent 設計時に repo or `npx skills add` を参照
- レポート: docs/research/2026-06-02-agents-best-practices-absorb-analysis.md
- メタ: agent-harness-contract.md が Claude-specific であることが #1 で明示確認 (drift ではなく意図的境界)

## [2026-06-02] ingest (light Phase 2, adopt=1) | Hermes 60 Days / 6 Lessons (0xJeff)

- ソース: "6 Workflows, 6 Lessons, 60 Days with Hermes Analyst" (0xJeff, vendor newsletter)
- 判定: harness-engineering family SATURATED-borderline (N=12+、直近の Hermes/harness content は採用0圏: Cursor harness 0 / How To Fix AI Slop-Hermes delta=0 0)。手法 delta=1。user choice = light-phase2 → A (design note のみ)
- 検証: 6 lessons 中 5 つ Already (provider routing / skill auto-create / memory persistence / feedback loop / skill bundling)、lesson 5 (x402 crypto)=N/A。唯一 novel = lesson 4b「feedback loop の echo chamber / self-reinforcing」(著者 "haven't solved this yet")
- 取り込み: 1 件 (S, design note のみ) — 学習昇格ループに echo-chamber リスクが該当 (importance 降順 + 完全一致 dedup のみで monoculture 抑制なし、部品 contradiction-scanner/submodular_selection は未配線)。design doc にリスク3 + watch 条件追記 + promote-learnings SKILL に多様性チェック heuristic 1項追加。自動ガード配線は YAGNI で見送り (稼働前/未観測)、watch トリガーで再検討
- 該当 family のキーワード hit: building an agent, architecture, feedback loop, skill bundling, memory persistence, echo chamber
- レポート: docs/research/2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md
- メタ: 採用は記事の novelty ではなく「未解決問題が現ブランチ feat/learned-promotion-loop に直接該当した」タイミング由来

## [2026-06-02] ingest (adopt=1) | Suzanne teach-back prompt (Anthropic, via Thariq)

- ソース: https://gist.github.com/ThariqS/1389dcdff9eba4789887a2211370f06b (Claude の作業を本人に教え返す teacher-mode prompt)
- 判定: 新 family "agent-comprehension"。9手法中 Gap 4 / Partial 3 / Already 2。既存 deep-read(外部記事)/quiz(CC知識)/think/recall いずれも「このセッションで Claude が行った作業の理解検証」責務を持たず = クリーン Gap
- 取り込み: 1 件 (S) — `/teachback` 軽量コマンド新設 (.config/claude/commands/teachback.md)。3階層チェックリスト+restate-first+why深掘り+クイズ(シャッフル/非開示)+ELI5/14/intern+debugger 統合、`--strict` で /goal hard gate opt-in
- Codex 補正: deep-read 拡張は反対(trigger濁る)/重いskillは時期尚早→reusable prompt で開始(Pruning-First)/完了ゲートは opt-in
- 副次 (Validation-only): Phase 2.5 で cmux Worker (launch-worker.sh) のバグ発見・修正。surface ref がグローバルなのに surface:1 ハードコード→Surface not found で codex/gemini worker 全失敗。動的解決に修正、ライブ検証済。/absorb 正規パス復旧
- レポート: docs/research/2026-06-02-suzanne-teachback-absorb-analysis.md

## [2026-06-02] ingest | Microsoft SkillOpt (自己進化スキル / text-space optimizer)

- ソース: SkillOpt 解説記事 (arXiv:2605.23904 / github.com/microsoft/SkillOpt)
- 判定: Gap 1, Partial 5, Already 2, N/A 2
- 取り込み: 4件採用 (L規模, plan化) — #1 optimizer eligibility classifier (objective lane vs judgement lane 入口分類), #2 objective-lane held-out strict accept gate (split_holdout.py 再利用, /improve 復活せず), #3 rejected-edit buffer per-lane 再配線, VO validation-only 訂正
- 診断: SkillOpt の概念は dotfiles に設計済みだが「配線切れ + 入口判別欠如」が evolving 実感なしの根因。判断タスクの自動最適化は block (SkillOpt が "間違ったツール" と明言)
- Phase 2.5: Codex が bounded-edit を Already→Partial 降格・Gap を optimizer eligibility classifier に改名。Gemini が SkillOpt 実在 + OPRO 系譜を grounding
- drift 露出: empirical-prompt-tuning absorb(2026-04-19) の T1/T2/T4 が /improve retire で孤児化
- 分析: docs/research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md / プラン: docs/plans/active/2026-06-02-skillopt-objective-lane-optimization-plan.md

## [2026-06-03] ingest-skip | How to Use Claude Cowork to Automate Your Entire Day (Full Course)

- ソース: marketing growth-hacker listicle (「Day 1-14 Cowork コース」, "single most underrated AI feature in 2026" 煽り)
- 理由: topic family "claude-code-tips" saturated-pure-rehash (11件目超, 採用率 <20%, delta=0)
- 根拠: 全手法が既存 absorb でカバー済み — Cowork tab/folder/connectors/file-processing は `2026-05-22-khairallah-40-features` (採用0) / 構造同一の `2026-06-02-how-to-actually-use-claude-14-steps` (昨日, delta=0 で ingest-skip) / Dispatch(スマホ→PC) は `2026-04-04-12-claude-features-top-operators` #6 で既出。Cowork drift は `docs/guides/2026-05-09-claude-cowork-equivalents.md` で 2026-05-22 訂正済み (新規 validation-only なし)
- 該当 family のキーワード hit: cowork, connector, dispatch, scheduled tasks, file processing, automate
- スキップ判定: Phase 1.5 gate (ユーザー確認: skip 選択)

## [2026-06-03] ingest (default 強化 1件) | ThariqS gist "Learn Quiz" (teach-back skill)

- ソース: https://gist.github.com/ThariqS/1389dcdff9eba4789887a2211370f06b (15行/1500字の教師ロール prompt skill)
- 判定: Gap 0 / Already 9 / N/A 0 — `/teachback` (commit 231be94) がこの gist をほぼ逐語ローカライズしたもの (出自と推定)
- 採用: 1件 (S) — teachback の通常モードを「ソフトゲート」に強化。gist の核心 `/goal: 理解実証までセッションを終えない` (hard-gate default) を dotfiles は `--strict` opt-in に弱めていた。中間策として通常モードでも「未確認項目があれば終了前に一度確認 (受動的に終わらせない)」を追加。完全 hard-gate は --strict 維持
- 教訓: 初回「dotfiles は gist より強化」と誤判定 → Already 項目で Intent(hard-gate) を Efficiency(摩擦削減) にすり替える `feedback_absorb_architectural_arrogance.md` の罠を踏みかけた。ユーザー指摘で訂正
- Phase 2.5 (Codex+Gemini): 省略 (15行 prompt の逐語一致 case で overkill、ユーザー合意済)

## [2026-06-04] ingest | 「勝手に賢くなる」AI情報収集基盤 (tokium_dev/Zenn)

- ソース: https://zenn.dev/tokium_dev/articles/20260427_ai_tech_researcher
- 判定: Gap 0 / Partial 2 (情報源自己進化=source特化のみ, 下流採用評価=補助指標限定) / Already 3 (morning-briefing=Experiment only, 2層オーケストレーション=強化不要, cron配信=drift audit Partial) / N/A 1 (Slack 4軸)
- 取り込み: 新規 AI tech researcher 構築を L プラン化 (docs/plans/active/2026-06-04-ai-tech-researcher-self-evolving-plan.md)。A(RSS候補read-only集計)/B(下流採用補助指標)/C(drift audit) を段階ロードマップに統合。Codex+Gemini一致警告(評価ゲーミング+コールドスタート)を受け、採用実績は補助指標限定+MAB探索/MMR多様性/時間減衰/human-in-loopで封じる安全設計。
- 分析レポート: docs/research/2026-06-04-ai-tech-researcher-self-evolving-absorb-analysis.md

## [2026-06-03] ingest (採用0 / drift修正1) | dynamic workflows in Claude Code (Anthropic 公式)

- ソース: Anthropic 公式ブログ (Thariq Shihipar / Sid Bidasaria) — Workflow tool (動的 harness 生成) の 12 パターン紹介
- 判定: Already 4 (fan-out/loop-until-done/model-routing/worktree) / Partial 5 (adversarial=security限定/tournament/token=effort間接/quarantine/generate-and-filter) / Gap 1 (Workflow tool 本体=deliberate non-adopt 維持)
- 取り込み: 新規 instruction **採用 0**。記事の主眼 (harness を作る) は `2026-05-31-32-hacks` で deliberate non-adopt 済 (tool description 自動注入+opt-in gated で redundant)
- Validation-only Follow-up (drift 1件): `improve-policy.md:503` + `autoevolve-core.md:311` が参照する `tournament-mode.md` が孤児欠損 (2026-03-19 プランで作成予定→未作成) → ユーザー判断で `best-of-n-guide.md` に付替修正
- Phase 2.5: Codex は launch-worker.sh の `-q` フラグバグで起動失敗 (要修正) → Opus 代行。Gemini の具体採用事例/CVE番号は hallucination 懸念で不採用、定性洞察 (LangGraph対比/quarantine引数解釈差バイパス) のみ採用
- レポート: `docs/research/2026-06-03-dynamic-workflows-absorb-analysis.md`

## [2026-06-05] ingest (validation-only) | Managed Agents Have a Portability Problem (agentlift, phuryn)

- ソース: agentlift 紹介記事 (github.com/phuryn/agentlift, MIT) — managed runtime portability compiler
- family: multi-agent-orchestration (managed-agents サブ)、Saturation PASS(warning) = 重複領域
- 判定: Already 中心 (核心原則「Own the definition, rent the runtime」は `agent-portability.md` 2026-04 で codify 済)。新規構成 **採用 0**
- ユーザー問い「今の構成 (.claude/agents/) vs 記事の構成 (.managed-agents/) どちらか」→ **乗り換え不要**。記事の `.managed-agents/` は置き換えでなくデプロイ専用の追加レイヤー (記事自身 "local agents are left alone")。dotfiles は managed runtime 未デプロイ = "own the runtime" 側で agentlift 対象外
- Validation-only Follow-up (stale 2件): `agent-config-standard.md` の対応表「skills/mcp_servers → 将来対応」を「Managed Agents native 対応済 (2026-06、shared/private wiring 可)」へ更新 / 「エクスポートスクリプト自前実装」構想に agentlift reference pointer 追加 (max_tokens は記事に言及なく未変更)
- Phase 2.5: 結論が Already 中心で Gap なしのため Codex/Gemini 批評はユーザー選択に委譲 (stale 修正のみ選択)

## [2026-06-05] ingest-skip (light Phase 2, adopt=0) | MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation
- ソース: arXiv 2605.27366 (Huawei Lin et al.)
- 理由: de-facto family "self-evolving-skills" N>=7 (taxonomy 未登録) の隣接対象。Saturation=SATURATED-but-novel (delta=4)。ユーザー選択 light-phase2 → Phase 2 まで検証したが全て Already/N/A/掘り下げ見送りで採用 0
- per-method 照合台帳 (delta_methods 4件の Pass2 着地):
  - #2 skill-level memory (`.memory.md` per-skill) → novel/Gap だが single-user harness で価値薄く adopt=0 (現状 topic-keyed feedback_*.md で per-skill 経験は蓄積済、差は co-located 自動 surface 配線のみ)
  - #3 test-gated registration → N/A (MUSE は runtime 自動生成ゆえ必須、dotfiles は作成時に skill-creator/skill-audit/Codex Gate 済)
  - #5 transfer-excludes-memory → Already (memory が agent-memory/ 別 namespace で skills-lock.json 配布に構造的非混入。MUSE が設計で達成する分離をアーキで無料取得)
  - #7 source-trajectory overfit → Already (Rule 40/47 holdout + anti-goodhart Rule 43 + SkillOpt 分析でカバー)
  - (rehash 除外: #1 lifecycle=AutoEvolve / #4 progressive-disclosure / #6 context compression=context-constitution P3)
- スキップ判定: light Phase 2 で検証後 adopt=0 (skip 同等)。MEMORY.md 索引・wiki INDEX・Obsidian は更新せず
- レポート: docs/research/2026-06-05-muse-autoskill-self-evolving-agents-absorb-analysis.md

## [2026-06-05] ingest-skip | I Connected Claude to Obsidian 90 Days Ago (cyrilXBT)
- ソース: cyrilXBT note 記事「I Connected Claude to Obsidian 90 Days Ago. Here Is What Happened to How I Work.」(テキスト貼付)
- 理由: topic family "obsidian-second-brain" saturated-pure-rehash (N=18 件目, 著者 cyrilXBT は family 4 本目, コア主張採用率 <10%, delta=0)
- 根拠: 全 9 手法が prior レポートに matched_prior 名指し済み。新規論点ゼロの完全再パッケージ (90日 narrative 形式のみ新規)。中心思想「Vault=双方向 AI 思考パートナー」は dotfiles の「Vault=memory→Vault 単方向スナップショット」と矛盾し family 横断で deliberate non-adopt 済
- per-method 照合台帳 (delta=0 の立証 — 全 current 手法 → matched_prior):
  - Filesystem MCP で Vault 接続 → `2026-05-25-cyrilxbt-organize-vault` "Filesystem MCP integration" (rehash, obsidian-knowledge/cli/digest/note で接続済)
  - Morning briefing 自動生成 → `2026-05-08-cyril` #4 "Daily Brief automation" + `2026-05-19-dashboard` T1 = auto-morning-briefing.sh (rehash)
  - CLAUDE.md=living doc / 月曜更新 → `2026-05-08-cyril` #3 "Vault CLAUDE.md template" + #6 "Weekly CLAUDE.md refresh (Monday 5min)" (rehash, Already/N/A 確定済)
  - 5 workflows に絞る → `2026-05-31-damidefi` signal-density + KISS/YAGNI/Pruning-First (rehash, 過剰生成削減で同一)
  - Connection finder=最高レバレッジ → `2026-05-08-cyril` #12 "Cross-vault auto-link discovery" (rehash, obsidian-knowledge リンク候補、自動化は Reject 済)
  - Decision support (vault 履歴) → `2026-05-08-cyril` #A "Contradiction detection / /think" + /decision + decision-feeder (rehash)
  - Vault quality cleanup (接続前) → `2026-05-31-damidefi` "Delete 90% / signal-density pruning" 記事全体 (rehash)
  - 過剰自動化を避ける (12→5) → `2026-05-31-damidefi` attention budget + KISS (rehash, #4 と同一)
  - 蓄積データからパターン抽出(90日) → `2026-05-08-cyril` #4 "PATTERN output" + #5 "Weekly Synthesis" (rehash, 90日 anecdote 3件は personal finding で手法でない)
- 該当 family のキーワード hit: obsidian / vault / second brain / CLAUDE.md / morning brief
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, ユーザー選択 skip)

## [2026-06-05] ingest | Claude Code 自己改善ループ (sonicgarden)
- ソース: https://zenn.dev/sonicgarden/articles/claude-code-self-improving-loop
- family: self-evolving/self-improving (実装手法側 N=10), Saturation PASS (warning, 非飽和)
- 判定: Gap 1 (publicity-review) / Already 1 強化 (Routines liveness) / N/A 3 (JSONL pipeline, Issue自動起票, Routines定期実行) / 不採用 1 (無人triage復活)
- 取り込み (採用2件 S+S):
  - publicity-review gate: scripts/security/publicity-scan.py 新設 + lefthook pre-commit 配線。scan-jsonl-secrets.py PATTERNS を DRY 再利用、staged added-lines の credential leak を block (high+medium、low は warning)。絶対パス/username は accepted-in-repo (constant-fail NO-OP 回避のスコープ翻訳)
  - routine-prompt-rubric.md に無人実行 liveness 対策5点 + Pre-flight 1項目
- Phase 2.5: Codex (採用1推奨→medium block 昇格指摘) + Gemini grounding (報酬ハッキング/Goodhart で /improve retire 裏付け)
- レポート: docs/research/2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md

## [2026-06-07] ingest (light) | How to Make Claude Code Stop Making Stuff Up — 4-layer honesty setup

- ソース: 記事（4層 anti-fabrication: L1 honesty rules+I-dont-know license / L2 verify-before-write / L3 PostToolUse tsc+Stop tests / L4 fact-checker subagent）
- 投入経路: /audit 誤起動 → /absorb に切替（記事はコードベースでないため gap 分析が正しいツール）
- 判定: 記事の4層は dotfiles で実質 Already/N/A、かつ概ね mechanism 化で記事(prompt-only)より強い
  - L1a 捏造禁止 = Already強（derivation-honesty-hook.py:43-67 が phrase 検出）
  - L2 verify-before-write = Already（codex-verification-before-completion + search-first-gate.py）
  - L3a per-edit typecheck = Already(Python: ruff check --fix が F821/F401 を edit 時検出) + N/A(TS は 537件全て vendored/sample, first-party ゼロ, settings-schema.ts 不在) + marginal(Rust 8件に cargo check 不経済)
  - L3b Stop test = Already強（completion-gate.py: retry counter 付き、記事より堅牢）
  - L4 fact-checker agent = Gap だが code-reviewer+honesty-hook+completion-gate と overlap 大 → Skip
- 採用: 1件のみ — L1b uncertainty license を CLAUDE.md:94 honesty 原則に1節拡張（新規 bullet 不足、IFScale 尊重）。residual gap = 自由形式の事実/ライブラリ挙動/外部応答の断定（hook 非対象・コードでない・banned phrase 非該当）を自己申告で塞ぐ
- メタ教訓（記事テーマの実演）: Phase 2.5 で Gemini が L3a 最優先と主張、根拠に `settings-schema.ts` を提示 → 検証で**存在せず（Gemini のハルシネーション）**。dotfiles の TS は全て vendored。bias 補正役自身が捏造 → file:line 検証が捏造を捕捉。Codex worker は別repo(hearable)で起動し dotfiles 文脈なく使用不能（既知の Bash→Codex 到達性問題）
- family: claude-code-tips / anti-fabrication（saturated, 低収率の傾向を再確認。ただし harness vs 記事の mechanism 優位を file:line で立証する validation 価値はあった）

## [2026-06-07] ingest-skip | gstack (Garry Tan の Claude Code 設定) を宣伝する記事
- ソース: https://github.com/garrytan/gstack (記事: Medium "I'm Noisy" 系インフルエンサー宣伝 listicle)
- 理由: topic family "claude-code-tips" saturated-borderline (15 件目, 採用率 <20%, delta=1)
- 根拠: gstack repo は 2026-04-26 absorb (skill-md-15min-guide) で実在確認済み。generic listicle は構造的低収率 (Khairallah 40=採用0 / SKILL.md 15min=採用0 / dynamic workflows=採用0)。記事主張 (108k stars / 18歳ハッカソン優勝 / 3-5h/day 削減) は検証不能な social proof
- per-method 照合台帳 (全10手法、9つ rehash + 1 novel):
  - フェーズpipeline (Think→…→Reflect) → `2026-04-21-harness-pipeline` + EPD/rpi/workflow-guide (rehash)
  - /office-hours (forcing questions) → `mattpocock:grill-me`/`grill-interview`/`brainstorming` (rehash)
  - /plan-ceo-review (10-star MVP) → `/spec` + `mattpocock:to-prd` (rehash)
  - /plan-eng-review (架構設計) → `/rpi` plan + `backend-architect` + `edge-case-analysis` (rehash)
  - /design-shotgun (4-6案同時生成+ブラウザ比較+taste学習) → **novel** (多案同時生成スキル不在、taste-skill は単方向 anti-slop)
  - /design-html (デザイン→HTML/CSS) → `image-to-code-skill` + `frontend-design` (rehash)
  - /qa (実ブラウザ QA) → `webapp-testing` + `playwright-cli/test` + `ui-observer` (rehash)
  - /ship (出荷ゲート+doc自動) → `/commit`/`/pull-request` + `completion-gate` hook (rehash)
  - /document-release (doc自動更新) → `doc-gardener` + `/check-health` + `doc-garden-check` hook (rehash)
  - GBrain (永続メモリ+3 trust levels) → 7-layer memory + MEMORY.md + 3スコープ(user/project/local) (rehash)
- novel #5 (design-shotgun) はユーザー判断で skip — 多案同時生成+browser 比較は Go/TS 中心・シンプル志向の用途にニッチ
- スキップ判定: Phase 1.5 gate (SATURATED-borderline → user 選択 skip)

## [2026-06-07] ingest-skip | 14ステップでClaudeをオートパイロットで動かす方法 (/loop, Routines, 完全自動化スタック)
- ソース: Codez (@0xCodez) バイラル記事の日本語全文翻訳 (519万インプレ, "Bookmark & Save"/Follow CTA の煽り signal)
- 理由: topic family "claude-code-tips / multi-agent-orchestration" SATURATED (actionable novel = 0, delta は未検証 platform fact のみ)
- 根拠: 実質的内容は全て absorb 済み —
  - `2026-05-14-claude-code-routines-absorb-analysis.md` (Routines 全体: /schedule・claude/ prefix・15 runs/day・rubric・Recipe Catalog)
  - `2026-05-31-32-claude-code-hacks-absorb-analysis.md` (/loop・routines・permissions・cost = 全 Already, Workflow = deliberate non-adopt, Auto Mode = 一次確認不能 open item)
  - `2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md` (Cloud Routines 運用)
  - references: `scheduling-decision-table.md` (5機構ネットワーク)・`managed-agents-scheduling.md`・`routine-prompt-rubric.md`
- per-method 照合台帳 (全14手法、11 rehash + 3 ambiguous(未検証/YAGNI) + N/A 1):
  - /loop CronCreate/List/Delete → `32-hacks` "/loop Already" + `routines` M1 (rehash)
  - cron式5フィールド → `scheduling-decision-table.md` Step2 CronCreate 行 (rehash)
  - /loop制約 7日期限/session scope → session scope=decision-table「セッション終了で消える」, 7日期限=**CronCreate tool desc で runtime 直接確認** "auto-expire after 7 days" (rehash, runtime検証済)
  - /loop制約 50タスク上限/CLAUDE_CODE_DISABLE_CRON → 記事のみ, runtime tool desc に記載なし (ambiguous, 焼き込み不可)
  - /loop + /goal → `/goal` skill 実在 + loop Already (rehash)
  - Desktop ローカルスケジューラ → ユーザーは Ghostty+cmux 運用, Desktop app 不使用 (N/A)
  - トークン予算/レート制限 → `32-hacks` "cost Already" + decision-table アンチパターン (rehash)
  - 無人権限 autoApprove/deny/.claudeignore/auditLog → `32-hacks` "permissions Already" (rehash)
  - Auto Mode 93%/3段階/2層 → `32-hacks` で「一次確認不能」, 二次ソースで close 不可 (ambiguous)
  - スケジューラ3層選択 → `scheduling-decision-table.md` は5機構ネットワーク化 (rehash, 記事より精緻)
  - Cloud Routines → `2026-05-14-routines` 全カバー (rehash)
  - /schedule トリガー → `routines` M1 Already (rehash)
  - API トリガー /fire+beta header → `routines` M6 で YAGNI skip 済の延長 (ambiguous, YAGNI)
  - GitHub トリガー → `routines` M4-R4 changelog GitHub trigger (rehash)
  - Skills/Dynamic Workflows 組み合わせ → `32-hacks` hack31 Workflow=毎セッション注入で redundant (rehash, deliberate non-adopt)
- runtime 検証メモ (記事の盲点): CronCreate には `durable: true` パラメータがあり `.claude/scheduled_tasks.json` に永続化して再起動を生き延びる。記事の「/loop は session scope で再起動で消える」断定は不正確 (デフォルトが in-memory なだけ)。記事の未検証スペック (50上限/DISABLE_CRON/Auto Mode 93%) は `32-hacks` の教訓どおり焼き込まない
- スキップ判定: Phase 1.5 gate (SATURATED → user 選択 skip)

## [2026-06-07] ingest-skip + validation-only | How Karpathy's CLAUDE.md made me $147,000

- ソース: 匿名 content-farm 記事 (Discord screenshot 起点、$147,000/65→94%/18h-week は出典なし fake precision)
- 判定: Phase 1.5 SATURATED-pure-rehash (delta=0)。claude-code-tips/CLAUDE.md best-practices family N=15+、24 ルール全てを既存 prior に名指し照合 (novel 0/ambiguous 0/N/A 1)。前回 12-rule (2026-05-10) で「N-rule 全採用=Reject」確定済みの煽り版
- 記事採用: **0 件**
- per-method 照合台帳: R1-4=karpathy_llm_coding.md / R5-8=ai_collaboration+honesty / R9-11=profile memories (R11 voice-lock のみ N/A) / R12-18=global system prompt+lefthook / R19-24=memory3層+checkpoint+failure-escalation / メモリアーキ=MEMORY.md索引+_index.md分離 (dotfiles の方が高度)
- **validation-only follow-up (ultracode 24原則 audit)**: 24 原則を adversarial lens に既存 harness を 6 lens 並列監査 (29 agents, confirmed=15/rejected=8)。memory-loop=broken、他5 lens=drift
  - Tier1 機構欠陥: change-surface-advisor.py:130 + skill-suggest.py:87 が非存在 TOOL_INPUT env var 読み→2ヶ月 dead NO-OP / measure-instruction-budget.py:195 references 常時0 undercount / --no-verify deny の `git commit -n` bypass + CLAUDE.md:61 根拠論理破綻
  - Tier2 orphan: measure-instruction-budget.py 未 wire / run-learned-promote.sh 未スケジュール (設計判断要)
  - Tier3 doc drift: careful description 誇張 / pre-commit-check.js 記述 stale / tool-scope-enforcer.py 未配線 / MEMORY.md stale fact×3 + scope件数 drift + broken link×2 / user_tech_stack.md Zed 未反映
  - adversarial verify が 8 件棄却 (YAGNI 撤退/lefthook 独立 enforce/直交軸混同 等) で監査品質を担保
- レポート: docs/research/2026-06-07-karpathy-147k-claudemd-absorb-analysis.md
- MEMORY.md 索引: 追記しない (記事採用0。validation findings の修正は別タスクで提案)

## [2026-06-08] ingest-skip + wiring-spotcheck | 30 Copy-Paste System Prompts That Make Claude an Expert at Anything

- ソース: https://x.com/eng_khairallah1/status/2063586097662407086 (同著者 @eng_khairallah1、前回 40 Features 2026-05-22 採用 0)
- 判定: Phase 1.5 SATURATED-pure-rehash (delta=0)。claude-code-tips family 12 件目相当。触れ込み(Boris Cherny/125 settings/token waste)と本文(30 generic persona prompts)が完全乖離 — 本文に Boris talk も token waste 分析もゼロ
- 記事採用: **0 件**
- per-method 照合台帳 (delta=0 立証):
  - token waste 4点 → feedback_instruction_cost/feedback_claudemd_length (CLAUDE.md 10%) / memory 3層 (project memory) / 2026-05-22-anthropic-engineers-token-savings (cache_control) / PR #70 skillOverrides + project_claude_plugins_provisioning (idle plugins) = 全 rehash
  - 本文 9/13/14/21-25/27-30 → /research, /think decision+/decision+/debate, /digest+/absorb, /review+code-reviewer(COLDNESS_BIAS+minimum change), backend-architect, debugger+systematic-debugging, document-factory, test-engineer+TDD, /timekeeper, /onboarding, /review+challenge, /morning+morning-briefing = 全 rehash
  - 本文 1-8/10-12/15-20/26 → N/A (content marketing/business/非技術者説明 = 個人 SWE harness scope外)
  - メタ運用 (top5 に絞る・refine・効かない rule 削除) → improve-policy.md Pruning-First + empirical-prompt-tuning = rehash
- 抽象度ミスマッチ: 記事=chat UI コピペ persona / dotfiles=CLI skill/agent codification。採用しても価値追加ゼロ (活用有無と独立した結論)
- **wiring spot-check (ユーザー要請: rehash 先が死蔵でないか)**:
  - skill 12個 (research/think/digest/timekeeper/morning-briefing/daily-report/debate/decision/onboarding/quiz/teachback/review) → 全て skillOverrides 非抑制 = 活用候補として温存、死蔵なし
  - agent 6/7 実配線あり: code-reviewer (17 caller, /review 起動), document-factory (init-project Agent 起動), debugger, test-engineer, test-analyzer (/review), backend-architect (file-pattern-router 登録)
  - **drift 1件発見**: nextjs-architecture-expert は agents/_archived/ に退役済みだが、私が rehash #22 で誤引用 (Already ハロシネーション)。references/agent-orchestration-map.md:187 がまだ退役済み agent を参照 → 別タスクで訂正提案
- MEMORY.md 索引: 追記しない (記事採用 0)
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash → user 選択 skip + wiring spot-check)

### wiring-check #2 追記 (2026-06-09, 同記事 sairahul1 引用版の重複 absorb)

- 同記事 (Khairallah 30 system prompts) の sairahul1 引用版を再投入 → Saturation 再判定も独立に delta=0 一致 (gate の再現性確認)
- 今回はマルチモデル連携 hook の配線を検証 (前回 #1 は skill/agent 配線): agent-router / suggest-gemini / post-test-analysis / error-to-codex は**全て Rust binary `claude-hooks` に移行済で live** (`user_prompt.rs` / `pre_tool.rs` / `post_bash.rs`、binary は 2026-04-14 build・settings.json 登録済)
- Python `.py` 3つ (agent-router/suggest-gemini/post-test-analysis) は settings.json 未登録の移行残骸 (DEPRECATED マーカーなし)。error-to-codex.py のみ削除済 (de016cf)
- **MEMORY drift 発見・訂正**: MEMORY.md マルチモデル連携セクションが旧 .py 名で記載 → wiring-check を「死蔵」と誤誘導していた。Rust 移行先を明記して訂正 (2026-06-09)
- **.py→Rust ドキュメント drift が 23ファイルに波及**: 現役13 + active plan2 + test1 が要修正、ADR/spec/completed・paused plan 7 は immutable 除外 → L 規模整合プランを `docs/plans/active/2026-06-09-python-hook-rust-doc-reconciliation-plan.md` に保存、新セッション /rpi 実行
- 教訓: skip の「Already/rehash」判定で matched_prior の **配線 live 確認 (B)** と **存在確認 (A)** を区別する。今回は MEMORY stale が A を B に見せかけていた

## [2026-06-12] ingest | nrslib サーヴァントエンジニアリング (レビュー速度改善)

- ソース: https://speakerdeck.com/nrslib/implementation-got-faster-so-what-about-reviews-an-invitation-to-servant-engineering-recreating-your-own-code-reviews-with-ai
- 判定: Gap 2個 (tiering+計測), 既採用未実装 1個, Partial 4個, Already 3個, N/A 1個 (family 8件目 PASS-warning)
- 取り込み: 全8タスク採用 → docs/plans/active/2026-06-12-servant-engineering-review-speed-plan.md (L)
- 特記: Codex が CLAUDE.md S規模 Codex Gate vs review SKILL ~10行省略の policy conflict を検出

## [2026-06-14] ingest-skip (validation-only, adopt=0) | Opik Self-Repairing Harness + Karpathy Loop Engineering
- ソース: https://x.com/_avichawla/status/2065727218991735000 + "Your Agent Harness Should Repair Itself" (Comet ML/Opik vendor article)
- 判定: family self-evolving/self-healing-harness N>=13, Saturation PASS(warning), per-method 台帳で全12手法 rehash (delta=0) → 採用 0
- 取り込み: なし (loop engineering=ralph-loop, self-repair=self-healing CREAO が丸ごとカバー)
- Validation-only: /improve 退役 orphan を露出 → 退役処理 (T4-C plan superseded+completed/, regression-gate.py 他を decommission-log flag 2026-07-14, self-healing report frontmatter 訂正)
- 詳細: docs/research/2026-06-14-opik-self-repairing-harness-absorb-analysis.md

## [2026-06-17] ingest-skip | Agent harness engineering with Claude: 14-step roadmap (movez Substack)
- ソース: movez.substack.com (Addy Osmani loop engineering を参照した harness 14-step roadmap)
- 理由: topic family "harness-engineering/self-improving-system" saturated-pure-rehash (N>=10 件目, 採用率<20%, delta=0)
- 根拠: 直近同系 vendor 記事が連続採用0 (Opik 2026-06-14 delta=0 / Hermes 2026-05-31 delta=0 / Cursor 2026-04-30 採用0)。決定打=3日前の 2026-06-12-fable5-14steps が同一テーマ・同一14ステップ構造を absorb 済み
- per-method 照合台帳 (delta=0 の立証 — 全14手法 → matched_prior 名指し):
  - 1 harness=model/tools/permissions/context → `docs/agent-harness-contract.md` + harness-stability.md (rehash)
  - 2 .claude/ folder layout → MEMORY.md「dotfiles 構造」.config/claude/ 実構造 (rehash)
  - 3 harness vs loop vs system 3層 → 2026-06-12-fable5-14steps + cc-7-layer-memory-model.md (rehash)
  - 4 default harness baseline → 2026-04-30-cursor-harness baseline 説明 (rehash)
  - 5 CLAUDE.md <500 tokens → feedback_claudemd_length.md(IFScale)、dotfiles は意図的に >500=反証済 (rehash)
  - 6 settings.json permissions undo-cost test → deny rules + change-surface-matrix.md + careful skill (rehash)
  - 7 subagents writer-vs-checker → 2026-04-30-cursor-harness「#7 R-002 役割分離」Already確定 + Codex Review Gate (rehash)
  - 8 skills reusable procedures → 2026-04-12-tan-thin-harness + skill-writing-principles.md (rehash)
  - 9 hooks deterministic (PreToolUse exit2/PostToolUse fmt) → determinism_boundary.md + claude-hooks Rust 4層 (rehash)
  - 10 add a loop (/loop + /goal grader) → 2026-06-12-fable5-14steps /goal 採用 + 2026-04-02-ralph-loop (rehash)
  - 11 dynamic workflows (agent/parallel/pipeline) → MEMORY.md「Workflow tool は deliberate non-adopt」(rehash)
  - 12 memory write-before-walk/read-at-start/distill → cc-7-layer-memory-model.md + memory-schema + handoff-template (rehash)
  - 13 close the loop output→lesson→skill → autoevolve_details.md 4層ループ + /promote-learnings (rehash)
  - 14 ship harness as plugin → project_claude_plugins_provisioning.md(task claude:plugins) + 本ブランチ ponytail プラグイン (rehash)
- 該当 family のキーワード hit: harness, loop engineer, self-improv, self-evolv, recursive self
- スキップ判定: Phase 1.5 gate (SATURATED-pure-rehash, ユーザー承認 skip)

## [2026-06-17] ingest | stop-slop (AI tell removal from prose)
- ソース: https://github.com/hardikpandya/stop-slop
- 判定: Gap 6 / Partial 2 / Already 2 / N/A 1
- 取り込み: 1 件 (prose.md に false agency→能動態 / 英語 throat-clearing opener / em-dash soft-default)
- 棄却: skill 丸ごと vendor (YAGNI)、絶対ルール (二次 slop)、5次元スコア、jargon/binary/Wh-
- 分析: docs/research/2026-06-17-stop-slop-prose-anti-slop-absorb-analysis.md

## [2026-06-17] ingest | Agentic Code Review
- ソース: テキスト直貼り (essay, Sean Goedecke 系)
- 判定: Gap 1 / Partial 3 / Already 4 / N/A 2 (code-review-best-practices family N=9, PASS warning)
- 取り込み: 1 件 (test-analyzer 4c アサーション書き換え検出 = diff-delta、4b tautological では捕まらない gap)
- Phase 2.5: Codex(cmux) + Gemini 両 fallback 失敗 (wander/出力未回収) — S規模1件ゆえ Pass2 判定で続行
- 分析: docs/research/2026-06-17-agentic-code-review-absorb-analysis.md

## [2026-06-17] ingest | How to Create Loops with Claude (kumai_yu/Qiita)
- ソース: https://qiita.com/kumai_yu/items/54ded70a5a68a5ca15d5
- 判定: 全11手法 Already (Gap 0 / Partial 0 / N/A 0) → 採用 0
- family: loop-engineering / multi-agent-orchestration (N=15, SATURATED-pure-rehash, delta=0)
- 根拠: 一次ソース Addy Osmani の loop engineering エッセイは既に references/comprehension-debt-policy.md に出典明記で absorb 済み (二次紹介ゆえ採用0)。3日前 Opik 記事の同判定と一致
- ユーザー: Saturation Gate で continue 選択 → フル workflow (Phase2 + Phase2.5 Gemini) 実行も採用0確定
- Phase2.5: Gemini novel 候補2点 (context poisoning / tool-call 上限) は記事の主張でなく既存実装でカバー → 棄却 (Gemini imagination ガード)
- 分析: docs/research/2026-06-17-loops-with-claude-absorb-analysis.md

## [2026-06-17] ingest (full workflow, adopt=0) | Hermes VPS 24/7 OS Complete Guide
- ソース: https://zenn.dev/sora_biz/articles/hermes-vps-complete-guide (sora_biz, Zenn)
- 判定: Hermes 記事4本目、personal-agent-os/self-evolving family 飽和。全10手法 rehash (delta=0)
- continue 選択でフル検証 (Phase 2-5 + Codex/Gemini) → Gap 0、採用 0
- Phase 2.5: Codex「採用0妥当、(8)双方向リモコンは N/A by security posture/scope mismatch、(4)VPS≠ローカルMac で可用性モデル相違」/ Gemini「別途 Hermes 立てる ROI 低、skill 蓄積はドメイン依存で非転移、TokenMix.ai 検証は hallucination 懸念」
- per-method 台帳 + 詳細: docs/research/2026-06-17-hermes-vps-24-7-os-absorb-analysis.md
- 次回短絡 anchor: Hermes ツール記事 / "Personal OS reframe" framing は reference-only 短絡可

## [2026-06-17] ingest (full workflow, adopt=0) | Hermes Analyst 10x Better + 6 Lessons (再提出)
- ソース: 0xJeff (Hermes Analyst 10x Better / 6 Workflows 6 Lessons 60 Days) — テキスト貼付
- 判定: personal-agent-os/hermes family (実ファイル N=9)。**「6 Lessons」記事は 2026-06-02 absorb の exact twin**、「10x Better」の唯一の新規非N/A手法 Nested Orchestrator もカバー済 → delta=0、採用 0
- continue 選択でフル検証 (Phase 2-2.5 + Codex/Gemini)
- Phase 2.5: Codex 格上げ提案2件を検証で棄却 — echo chamber=2026-06-02 で design note+watch 採用済(新規不要)、Nested Orchestrator cross-pollination=`multi-agent-coordination-patterns.md:89`(Agent Teams)+`:67`(親 synthesis)+Workflow patterns でカバー済(Codex は subagent-delegation-guide:138 のみ読み coordination-patterns 見落とし=狭く深い盲点)。Gemini 700s 不完全→失敗記録
- ゲート教訓: Phase 1.5 で固有名詞 "hermes" を grep せず orchestration/skill キーワードで引いたため exact twin を見落とし(飽和結論には到達)。次回は著者/製品名を直 grep
- 既存 anchor 通り: Hermes ツール記事は reference-only 短絡可 (twin/vendor content)

## [2026-06-18] ingest-skip (light Phase 2, adopt=0) | Vercel eve agent framework

- ソース: https://vercel.com/blog/introducing-eve
- family: harness-engineering (N≈10, 採用率~60% PASS-warning)。TS production framework vs Claude Code CLI の scope mismatch でユーザーが light-phase2 選択
- 結果: delta_methods 3 手法 (durable execution / needsApproval / connections-as-file) を Phase 2 まで検証 → 全 11 手法 Already or N/A、Gap 0 → adopt=0 (skip 同等)
- Gemini 敵対レビュー (ユーザー要求): adopt=2 推奨も 4 提案全て却下 (Claude Code platform 機能の再実装 or 宣言済みへの config 追加 = imagination バイアス) → adopt=0 維持。副産物: platform が transcript/resume・MCP OAuth・skill on-demand を内蔵という強論拠を獲得
- per-method 台帳 (全 11 手法) + 詳細: docs/research/2026-06-18-vercel-eve-agent-framework-absorb-analysis.md
- 教訓: production agent framework 製品 (TS/Node deploy 型) は CLI harness と scope mismatch で構造的に採用0。N>=3 で family 横断教訓化判断

## [2026-06-18] ingest | The Self-Improving Loop: 300-agent swarm on Kimi K2.6, verified by Opus 4.8
- ソース: Kimi.ai ベンダーマーケ記事 (テキスト貼り付け)
- 判定: Already 10, Gap 0, N/A 1 (Kimi 製品固有)。採用 1 (borderline, S)
- family: multi-agent-orchestration + self-improving-loop (cross, 合算 N≈14)。SATURATED-pure-rehash (delta=0) だが user が continue 選択
- per-method 台帳: 全10手法 rehash、Sonnet Explore で prior 実在裏取り (8 exists / 2 partial、hallucination なし)
- Phase 2.5: Codex+Gemini 並列とも「採用0妥当」。Best-of-N/Generator-Verifier は AlphaCode 時代の標準、Kimi の差分は手法でなく安価大規模実行の経済性
- 採用: best-of-n-guide.md に Cost-Arbitrage 小節 (低単価生成 + deterministic verifier + p<0.3 のときのみ cheap N≥3 → high-reasoning verify-only)。経済前提 (無料 open-weight runner) は Claude harness に transfer しない
- 詳細: docs/research/2026-06-18-kimi-k26-self-improving-swarm-loop-absorb-analysis.md

## [2026-06-18] ingest-skip | Claude Codeで10倍の生産性を手にいれる並列ループエージェント (熊井悠/ランスティア)
- ソース: https://qiita.com/kumai_yu/items/54ded70a5a68a5ca15d5 (X 投稿テキスト貼り付け)
- 理由: topic family "multi-agent-orchestration" saturated-borderline (N≈14, 採用率<20%, delta=1)
- きっかけの Carlini Cコンパイラ実験 (16体Opus並列/$20k/Linuxカーネルコンパイル可) も同 family 既知事例、新規論点なし。6日前 kimi-k26 (2026-06-18) も同 family で Gap 0
- per-method 照合台帳 (全7手法、matched_prior 名指し):
  - 1. 無限ループで止めない (loop-until-done) → `2026-06-03-dynamic-workflows` "loop-until-done | Already | implement-loop/review-loop/completion-gate.py" (rehash)
  - 2. 並列化 (fan-out 役割分担) → `2026-06-03-dynamic-workflows` "fan-out-and-synthesize | Already | research/dispatch" + multi-agent-coordination-patterns.md (rehash)
  - 3. 仕様駆動×TDD → `2026-05-27-sairahul-7agent` "7-agent chain | Already | /epd" + "Acceptance tests | Already | test-engineer" (rehash)
  - 4. 出力最小化でコンテキスト保護 → `2026-06-03-dynamic-workflows` "token budget | Partial" + ADR-0002/0007 Progressive Disclosure (rehash)
  - 5. 5フェーズフロー (調査→spec承認→TDD実装→統合ゲート→並列レビュー) → `2026-05-27-sairahul-7agent` "7-agent chain | Already | /epd (Spec→Spike→Validate→Build→Review)"。構成要素全て Already、「並列グループ宣言=spec でファイル独立性明示」のみ partial で Task Parallelizability Gate でほぼカバー (ambiguous, delta に計上)
  - 6. サボり封じ (implementer 禁止事項+reviewer 二重構造) → `2026-06-17-agentic-code-review` "test変更の精査(assertion書き換え)→採用" で test-analyzer 4c 追加済 + silent-failure-hunter.md + CLAUDE.md "暗黙フォールバック・モック・NO-OP 絶対禁止" (rehash)
  - 7. CLAUDE.md は案内役、手順はスキルに → `2026-06-03-dynamic-workflows` + ADR-0007 thin-claudemd-thick-rules (rehash)
- delta=1 (手法5 ambiguous のみ)。user が skip 選択 (手法5 も Task Parallelizability Gate でカバー済みと判断)
- スキップ判定: Phase 1.5 gate (SATURATED-borderline)

## [2026-06-20] ingest | Knowledge Work Plugins (Anthropic 公式 repo)
- ソース: https://github.com/anthropics/knowledge-work-plugins
- 判定: Gap 0 / Partial 1 / Already 7 / N/A (ドメインプラグイン 16+) — **採用 0**
- family: anthropic-knowledge-work-plugins (新規, N=1) — PASS gate (新分野)
- 正体: Claude Cowork 向けロール別ドメインプラグイン市場 (sales/legal/finance/HR/marketing/CS/PM/data/ops/design/bio/SMB/pdf + cowork-plugin-management メタ層)。**非エンジニア業務向けで開発者ハーネスと職務ミスマッチ**
- ドメインプラグイン (営業/法務/財務等) は全 N/A。転用可能メタ層 8 中 7 が Already (dotfiles 先行): marketplace.json / skill-creator / 7層メモリ / design-skill-routing / careful+completion-gate / developer-onboarding / thin-thick。`~~placeholder` 配布 (1件 partial) は公式自身が「外部配布時のみ使え」と限定 → N/A
- Phase 2.5 (Codex+Gemini): domain mismatch で採用0確定のため **user 承認のもと省略**
- validation-only: dotfiles メタパターンが公式 Cowork 規約と**整合・先行** (drift なし)。次回 role-plugin 記事は Phase 1 で「メタ層のみ照合・ドメイン N/A」短絡可
- 詳細: docs/research/2026-06-20-knowledge-work-plugins-absorb-analysis.md

## [2026-06-20] ingest | Khairallah "How to Build Your First Team of AI Agents Using Claude (Full Course)"

- ソース: Twitter/X thread (@eng_khairallah1), agent team intro listicle (full course 形式)
- 判定: **Gap 0 / Partial 0 / Already 8 / N/A 0、採用 0 件**
- Saturation Gate: multi-agent-orchestration family **N=30+** (SATURATED-pure-rehash)、user は念のため "continue (フル workflow)" を選択 → 結論変わらず adopt 0
- per-method 照合台帳 (delta=0 立証、全 8 手法に matched_prior 3点セット名指し): 3 roles → multi-agent-coordination-patterns 5パターン + code-reviewer/codex-reviewer / role-standard-format-boundaries → agent-design-lessons.md (Self-Rejection Rule + Codified Context) / worker-critic loop → Codex Review Gate (CLAUDE.md ワークフロー表) / MCP/connectors → settings.json + mcp-audit.py VeriGrey Tool Filter / sub-agent orchestration → Agent tool + Workflow tool (deliberate non-adopt) / 10-case eval → skill-audit + Codex Review Gate / persistent memory → 7-layer memory model / failure handling + loop hard limit → blueprint-pattern.md `max_iterations` 必須属性
- Phase 2.5: **Codex 成功 (retry, bounded timeout)** / **Gemini 失敗 (IneligibleTierError → Antigravity 移行要求)**。Codex は条件付きで 2 件 drift 指摘 ((a) reproducible 10-case eval contract / (b) role/standard/format/boundaries の明文化テンプレート) → 両方とも実態は欠落だが既存仕組み (skill-audit + Review Gate / single-purpose enforcement) で代替済、ROI 低で validation-only に降格
- 教訓: (1) Phase 1.5 台帳 name-pointing 立証は機能、(2) Codex via Bash tool は依然 silent exit、bounded timeout + 短縮プロンプト + tail -30 で retry 成功パターン確立、(3) **Gemini Code Assist for individuals は sunset**、`gemini -p` を Phase 2.5 で常用できなくなった (運用 drift)、(4) 入門 listicle の SATURATED 採用 0 でも台帳照合練習 + drift 露出の副産物あり

## [2026-06-20] ingest-skip-equivalent | Self-Updating Prompt (100 User Decisions)

- ソース: paste-only (Nick Mayhew/Anthropic on stage、recruiting 事例)
- 理由: topic family "self-evolving" SATURATED-pure-rehash (N=21+, 直近3件 adopt 0, delta=0)
- 判定経路: user continue 選択 → Phase 2 Pass 2 で adopt 0 確定 (Codex 批評で borderline 1件提案も user skip)
- per-method 照合台帳 (全5手法 rehash):
  - Markdown prose prompt → `2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md` (text-space optimizer)
  - Batch decision update → `2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md` (calibration-verdict-logger.py)
  - Two-layer split → `references/model-routing.md` (4-tier) + `2026-06-02-skillopt-...md` (objective/subjective lane)
  - Human decision logging → `2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md` (patterns.jsonl + session_events)
  - Feedback loop as product → `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md` + Wave3 YAGNI 確定 (sonicgarden)
- 採用: 0
- レポート: `docs/research/2026-06-20-anthropic-100-decisions-self-updating-prompt-absorb-analysis.md`
- 教訓: vendor blog 風記事 + family saturated + 経験則の数値根拠なし = 全 rehash の典型サイン。次回 keyword (self-update / apprentice / 100 decisions / feedback loop is product) 検出時は saturation gate skip 推奨可
- 詳細: docs/research/2026-06-20-khairallah-agent-team-intro-absorb-analysis.md
