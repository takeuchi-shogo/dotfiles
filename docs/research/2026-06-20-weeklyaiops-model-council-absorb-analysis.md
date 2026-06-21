---
date: 2026-06-20
source_title: "How to get Fable-level intelligence back (model council / fusion)"
source_url: weeklyaiops.com community marketing
source_author: unknown (weeklyaiops community)
family: multi-agent-orchestration
family_count: 15+
saturation: SATURATED-pure-rehash
delta: 0
adoption: 0
status: rejected
phase_25: skipped (Codex Bash 不到達 + Gemini sunset の dual-degraded)
---

# Model Council ("Fable-level intelligence" 再構築) absorb 分析

## Source Summary

Fable 5 廃止後の Opus 4.8 「lobotomized」感覚を council (parallel panel + judge synthesizer) で取り戻す主張。OpenRouter own published reasoning test で 2-model panel + judge が 69/100 (Fable 5 単独 65.3)、3 cheap models refereed が 64.7。 reframe: "hire a team, don't rent a genius"。Frontier model を judge 席に、cheap models を panel に。Use case 5 種 (migration / deep research / orchestrating long jobs / briefing lighter agent / building KB)。Router ≠ Council (synthesis step 必須)。ツール 6 種 (openrouter fusion / orcarouter / gavel / openfusion / fusion-fable / llm-consortium)。weeklyaiops.com community 誘導の marketing 構造。

## Phase 1.5 Saturation Gate

family: multi-agent-orchestration / N≥15 / 直近 3 件 (2026-06-20 Kimi self-verifying / 2026-06-20 Khairallah Agent Team / 2026-06-18 Kimi swarm) は採用率 ~0、特に 6/20 Kimi は 9 手法全 rehash delta=0 で確立済パターン。

ユーザー判定: `continue` (台帳照合に念のため検証、結論変わらず adopt=0)。

## per-method 照合台帳 (全 11 手法 — skip の立証責任を継続記録)

| # | current 手法 | verdict | matched_prior (ファイル + heading + 同等性) |
|---|--------------|---------|---------------------------------------------|
| 1 | Council = panel + judge synthesizer | rehash | `2026-06-18-kimi-k26-self-improving-swarm.md` "Generator-Verifier" + `references/best-of-n-guide.md` / 並列候補 + verifier 統合は同型 |
| 2 | Frontier judge + cheap panel | rehash | `references/model-routing.md` "Opus=判断・統合 / Sonnet=実装" + `best-of-n-guide.md` Cost-Arbitrage 節 / 高tier=judge・低tier=生成 は完全同型 |
| 3 | Per-task judge tuning (prose vs test) | rehash | `skills/review/SKILL.md` Step 0 tier (light/standard/deep) + Codex Review Gate (test実行) / テーマ別 judge は既存 tier 設計と同型 |
| 4 | Migration: council decides, cheap exec | rehash | `references/multi-agent-coordination-patterns.md` Orchestrator-Subagent (デフォルト) + `2026-06-17-hermes-vps-24-7-os` Nested Orchestrator (cross-poll 採用済) / 言い換え |
| 5 | Deep research panel + judge | rehash | `/research` (multi-source 並列 + 集約) + `/deep-research` (fan-out → adversarial verify → synthesis) / 1対1 同型 |
| 6 | Orchestrating long multi-step jobs | rehash | `2026-06-03-dynamic-workflows` Workflow tool fan-out/pipeline + `/rpi` + `/epd` / 複数 step 協調と同型 |
| 7 | Briefing lighter agent (vague → sharp brief) | rehash | `/spec` (Prompt-as-PRD for downstream) + `/spike` → `/rpi` chain / 上流判断・下流執行は同型 |
| 8 | KB building (structure + fill) | rehash | `/absorb` Phase 5+ (Opus 判断 + Sonnet BG 並列書込) + `project_memory_vec_vault_index.md` (indexer + Vault Lit Note) / decision-by-judge + fill-by-cheap 同型 |
| 9 | Router ≠ Council (synthesis step 必須) | rehash | `2026-06-03-dynamic-workflows` で Workflow tool deliberate non-adopt 判断時に synthesis step の有無を council 条件として明示済 + Codex Review Gate (codex-reviewer + code-reviewer 並列 + Opus 統合) は council shape with judge |
| 10 | Code judge runs tests (objective referee) | rehash | `skills/review/SKILL.md` Codex Review Gate + lefthook test gate + `/verify` skill / code 判断は deterministic test runner、prose は synthesizer は既存設計 |
| 11 | "Would I pay premium?" gut check | rehash | `references/model-routing.md` tier 判断 + `skills/review/SKILL.md` Step 0 (S規模=light skip) / コスト見合い召集判断と同型 |
| - | openrouter fusion / orcarouter / gavel / openfusion / fusion-fable / llm-consortium | N/A | Claude-Code-specific harness 境界外 (agent-harness-contract.md)、Plus 内コストで per-call billing 切替無価値 |

delta = 0 (全 11 手法 matched_prior 3点名指し済、novel + ambiguous ゼロ)。

## Phase 2 Judgment

11 Already (強化不要) / 6 N/A (tools) / 0 Partial / 0 Gap。

## Phase 2.5 — dual-degraded fallback

Codex CLI Bash 不到達 + Gemini sunset の dual-degraded ベースライン (2026-06-20 Kimi self-verifying absorb で確立)。per-method 台帳 (matched_prior 3点名指し) を self-bias 補正の代替証拠とする。

**Opus 自問: 過大評価していないか?** ledger 引用句 (Cost-Arbitrage / Orchestrator-Subagent / Generator-Verifier / synthesis-step 条件) を実ファイル grep で確認済。dotfiles harness は council shape を deterministic verifier 限定で運用、prose synthesizer も `/research` + Codex Review Gate でカバー。

**Opus 自問: 過小評価していないか?** ツール 6 種は Claude-Code-specific harness 境界外、Plus 内収まり中で per-call billing 切替の経済効用なし。"Fable 5 廃止" 文脈は `feedback_model_fable_classifier_outage.md` で既知、対策も cmux Worker + model routing で配線済。

## Triage / Decision

採用 0 件。Phase 4 (Plan) スキップ、Phase 5+ (Wiki INDEX / Obsidian / MEMORY.md 追記) も skip 同等扱いで省略。

## 教訓

- **community marketing は次回ベンダー検出で短絡可** (Hermes / Kimi に続く 3 系統目)。weeklyaiops.com / "convene the room" / "rent a genius" 系慣用句を Phase 1 で検出 → reference-only 即時判定可能
- **"Fable 5 廃止後の取り戻し" framing は council 系の新たな marketing ハンドル** だが、council 自体は AlphaCode 時代の Generator-Verifier の言い換え。家族飽和は手法名でなく shape で判定するので skill drift なし
- council 用語の濫用に注意: dotfiles は council を deterministic verifier に限定 (best-of-n-guide.md)、prose synthesis 用 council は `/research` + Codex Review Gate でカバー済

## Validation-only Follow-up

なし (drift 露出なし、既存資産で完全カバー)。
