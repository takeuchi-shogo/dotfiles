---
source: "Autogenesis: A Self-Evolving Agent Protocol (arxiv 2604.15034, Wentao Zhang, NTU)"
date: 2026-04-19
status: analyzed
---

## Source Summary

**主張**: LLMエージェントの自己進化を標準化する二層プロトコル。リソース層 (RSPL) で prompt/agent/tool/environment/memory を Protocol-registered Resources として統一管理し、進化層 (SEPL) で Reflect→Select→Improve→Evaluate→Commit の 5 atomic operations を closed-loop で実行する。

**手法**:
- **RSPL** (Resource Substrate Protocol Layer): 5 リソースを versioned resource として扱い、Context Manager + Server-Exposed Interface + Version Manager + Tracer Module で管理
- **SEPL** (Self-Evolution Protocol Layer): Reflect(ρ)→Select(σ)→Improve(ι)→Evaluate(ε)→Commit(κ) の 5 atomic op
- **Key finding**: prompt + solution strategy を同時進化させると単一次元進化を上回る (AFlow/ADAS で裏付け)
- 複数最適化戦略をサポート: Reflection, TextGrad, RL-based

**根拠**:
- GAIA 89.04% Pass@1 (vs ToolOrchestra 87.38%, +1.66pp)、Level 3 tasks で 33.3% 改善
- AIME24/25: gpt-4.1 で +71.4% / +66.7% 相対改善 (弱モデルほど大きい)
- LeetCode: 5 言語で 10.1-26.7% pass 率改善、実行時間 7.8-46.4% 削減

**前提条件**: 反省能力のあるモデル / 実行可能フィードバック / 十分な計算予算 / 明確な評価基準

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 自己進化ループ全体 (AutoEvolve) | Already | `.config/claude/agents/autoevolve-core.md` + `meta-analyzer.md` + `skills/improve/` で Phase 1-5 実装済み |
| 2 | Reflect (session reflection) | Already | `scripts/learner/session-learner.py` + `skills/analyze-tacit-knowledge/` |
| 3 | Select (候補選択) | Already | Phase 2.0 で 3候補→Debate→Codex ROI、`mutation_type` (refine/pivot/novel) |
| 4 | Improve (autoevolve/* ブランチ隔離) | Already | Proposer Anti-Patterns AP-1~5 + git 隔離 |
| 5 | Evaluate (skill-audit + RL advantage) | Already | `skills/skill-audit/`, `scripts/learner/rl_advantage.py` (RLOO/GRPO/clip_ratio) |
| 6 | Commit (rollback + rejected-patterns) | Already | `rollback_plan` 必須、3連続 revert で自動 suppress |
| 7 | メモリシステム | Already | `references/memory-schema.md` (type 別 retention) + 7 層メモリモデル |
| 8 | Agent/Skill 分離 | Already | Hyperagent pattern (Meta vs Task) + skill-inventory |
| 9 | 安全機構 (master 直変禁止 / 3 ファイル制限 / gaming-detector) | Already | `improve-policy.md` + policy hooks |
| 10 | 統一リソース抽象化層 (RSPL 相当) | Partial | memory-schema / skill-inventory / agent 定義はあるが prompt/tool/env を含めた統一 id/lineage 層は暗黙的 |
| 11 | Strategy Co-evolution (prompt + strategy 同時進化) | Gap | 候補生成は prompt or config の単一次元。resource_targets 付き 3 次元 schema は未実装 |
| 12 | Tracer Module (trace → failure hypothesis 明示マッピング) | **Gap** (Codex 格下げ) | session-trace-store / evidence_chain はあるが trace→hypothesis→falsification→metric の永続 registry なし |
| 13 | TextGrad / gradient-based prompt optimization | N/A | `rl_advantage.py` (RLOO/GRPO) で代替済み、dotfiles に gradient 実装は ROI 低 |
| 14 | Agent Bus / 明示的 loose coupling | N/A | MCP + subagent + worktree で代替 (Gemini: MCP が "AI 界の USB-C") |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | session-trace-store + session-learner | trace → hypothesis → falsification → metric の永続 registry がない | Phase 1 に `hypotheses.jsonl` artifact を追加。schema: `{trace_id, hypothesis, falsification_criteria, metric, status}` | **Gap 格下げ** |
| S2 | `skill-benchmarks.jsonl` + skill-audit | task dependency (math vs QA) と ceiling effect (強モデルで飽和) を track しない | schema に `task_category` + `model_tier` 追加、gaming-detector に ceiling 検知ルール (baseline >= 0.9 で delta 閾値を緩める) | 強化可能 |
| S3 | `mutation_type: refine/pivot/novel` + strategy-outcomes.jsonl | 「prompt + strategy 同時進化」を active policy 化していない | Phase 2.0 candidate schema に `resource_targets: [prompt, config, strategy]` + `interaction_hypothesis` を追加。小さく co-evolve (1 候補内で複数次元) | 強化可能 (G11 本体) |
| S4 | `improve-policy.md` Rule 8 (`+2pp` merge / `-2pp` revert) | カテゴリ別 MDE (minimum detectable effect) と holdout 接続が暗黙 | Rule 8 をカテゴリ別に拡張: retrieval +3pp / generation +2pp / gate +1pp。holdout set の指定を明文化 | 強化可能 |
| S5 | `memory-schema.md` + git config_version | Memory resource を versioned 扱いしていない (snapshot/rollback なし) | schema に `version` + `snapshot_ref` フィールド追加。MEMORY.md 更新を Phase 2 Improve で snapshot 化 | 強化可能 (優先度中) |

## Phase 2.5 修正メモ (Codex + Gemini 批評統合)

### Codex 指摘
- S1 を Already → **Gap** に格下げ (registry 未実装は Gap 相当)
- S3 / G11 は統合。既存 mutation_type は lineage 分類であり co-evolution 操作空間ではない
- G10 RSPL 統一層は抽象層を作るより、既存 JSONL schema に共通 id/lineage を足す方が現実的
- 新観点: SEPL atomic op の machine-readable 状態遷移 / co-evolution ablation 設計 (prompt-only / strategy-only / both 2x2) / selection pressure 制御

### Gemini 指摘
- コスト逆転リスク: iterative evolution で「$1 問題に $10 API 費」事例あり → cumulative cost tracking 必須
- alignment faking: 12% → 78% に急増。Evaluate で「実タスク通過」と「評価通過」の乖離検出が重要
- AFlow / ADAS / GPTSwarm が "prompt + strategy co-evolution" を裏付け。ただし個人 dotfiles 規模では小さく導入
- MCP が Agent Bus の実質標準 → G14 N/A 判定を強化

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | hypotheses.jsonl (Tracer → Hypothesis registry) | **採用 (最優先)** | 他強化の前提インフラ。Reflect 出力を Select/Evaluate に渡す背骨 |
| G11/S3 | Co-evolution 候補 schema (resource_targets 3 次元化) | **採用** | 論文中核、AFlow/ADAS で裏付け。dotfiles では 1 候補内で小さく co-evolve |
| G10 | 統一リソース抽象化層 | スキップ | JSONL schema に共通 lineage フィールド追加で足りる (Codex 指摘) |
| G13 | TextGrad | スキップ | RL advantage で代替済み |
| G14 | Agent Bus | スキップ | MCP で代替 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S2 | task_category / model_tier + ceiling detection | **採用** | 3-prompt eval の天井効果誤判定を防ぐ |
| S4 | カテゴリ別 MDE + holdout 明文化 | **採用** | 既存 Rule 8 拡張で誤マージ削減 |
| S5 | memory version / snapshot | **採用 (優先度中)** | git が部分代替、先に S1-S4 を固める |
| 新 N3 | Cost-aware evolution gate | **採用** | Gemini 指摘のコスト逆転リスク対策 (cumulative API cost tracking + budget gate) |

## Plan

統合プラン: `docs/plans/active/2026-04-19-autogenesis-integration-plan.md` 参照。全 5 タスク、推定規模 L。
