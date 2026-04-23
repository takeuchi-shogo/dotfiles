---
source: "Skill Graphs 2.0 — 3層合成モデル (atoms/molecules/compounds) でのレバレッジ獲得"
date: 2026-04-23
status: integrated
---

## Source Summary

**主張**: Skill graph の深い依存グラフは agent の信頼性を壊す。skills を 3 層 (atoms / molecules / compounds) に分類し、composition を skill 側に押し込むことで解決する。compound 層を人間が driver することで 100x のレバレッジを得る。

**手法**:
- Atoms (capabilities): 単一目的プリミティブ、他 skill を呼ばない、ほぼ決定的
- Molecules (composites): 2-10 atoms の explicit chaining、runtime 判断を最小化
- Compounds (playbooks): molecules を束ねる orchestrator、人間が driver
- Explicit > Runtime: composition を skill 側に寄せ、agent の runtime 判断を最小化
- Human RAM Model: 並列 5 agents 前提で level を上げることで 100x leverage
- Reliability Ceiling: compound が 8-10 molecules 超で信頼性低下 (著者の実測)
- Testing Non-triviality: skill reliability テストが非自明、autoresearch の余地

**根拠**: 著者の実践経験 (capabilities/composites/playbooks 構造で稼働中)、Reddit/X の dense graph で stall する実体験報告、Gemini 調査による数学的裏付け ($0.9^n$ 指数減衰、n=8 → 43%, n=10 → 35%)

**前提条件**: 複数 skill が graph 的に関係、並列 agent ワークフロー、Coordinator パターンの束縛が軽い設計思想

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| K1 | skill の 3 層分類 | Partial | `pattern: orchestrator/checklist/reference` field が存在 (skill-creator/references/planning-guide.md)。atom/molecule/compound の明示的 tier は未標準化 |
| K2 | explicit composition | Already (強化可能、Codex 格上げ) | pattern field + /epd 内の Phase→skill 静的記述で既存。frontmatter `composes:` 宣言は未実装 |
| K3 | runtime decision 最小化 | Already | hook 体系 (completion-gate, agent-router, plan-lifecycle) + agent-orchestration-map.md |
| K4 | parallel orchestration | Already | /dispatch + cmux 4 層 + race mode。references/cmux-ecosystem.md:95-213 |
| K5 | skill reliability testing | Partial (Codex 格下げ) | /skill-audit は単一 skill eval。**graph-level** reliability は未実装 |
| K6 | reliability ceiling | Already (強化可能) | ceiling detection (baseline ≥ 0.9) + Context Rot 300-400k。**composition depth (skill→skill) の計測は未実装** |
| K7 | compound orchestrator | Partial (Codex 格下げ) | /epd, /rpi, dev-cycle。ただし /epd は command (thin) + skill の分散実装で責務境界が未定義 |
| K8 | leverage / human-driven layer | Already (強化可能) | "Humans steer, agents execute" + Never delegate understanding。**どの level を人間が drive するかの粒度規範が薄い** |
| G1 | Tool Poisoning 対策 (Gemini) | **Already** (再評価で格下げ) | mcp-audit.py (skill-MCP scoping + sequence anomaly) + mcp-response-inspector.py (VeriGrey arXiv:2603.17639 Gap #5 + AgentWatcher arXiv:2604.01194 10 rule) が実装済み |
| G2 | Skill Graph Embedding (Gemini) | N/A | Planning overhead 大、YAGNI。不要 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | ceiling detection (baseline ≥ 0.9) | composition depth と **8-molecule ceiling** ($0.9^n$ 指数減衰) が未運用 | /skill-audit に Step 0.7 (Composition Depth Check)、PLANS.md に Compound Plan Ceiling (≤8 molecules 推奨) | 強化可能 |
| S2 | "Humans steer, agents execute" + P3 | どの level を人間 drive するか粒度規範なし、Codex は **Human RAM モデルとの衝突** を指摘 | ADR-0008 で drive 責任のレイヤリング (atom=hook / molecule=subagent / compound=人間) | 強化可能 |

## Phase 2.5 Refine (Codex + Gemini 批評統合)

### Codex の指摘で変更した判定

- **K2**: Partial → Already (強化可能)。planning-guide.md の pattern field + /epd の Phase→skill 静的記述で事実上の explicit composition は成立
- **K5**: Already → Partial。/skill-audit は単一 skill eval、autoresearch は graph-level reliability。問題領域が違う
- **K7**: Already → Partial。/epd は command (thin) + skill の分散実装で責務境界未定義
- **前提の衝突**: Human RAM モデル (5 並列 agents) ↔ Coordinator (Never delegate understanding) の非両立を指摘

### Gemini の周辺知識で追加した視点

- 3 層分類は **2025-2026 業界標準** (Mastra / LangGraph 2.0 / Anthropic Skills)
- 8-10 molecule ceiling は数学的に $0.9^n$ で裏付け (Planning Drift)
- 新規論点 G1 (Tool Poisoning 対策) を提起 — ただし実装調査で Already 判定に格下げ

## Integration Decisions

### Gap / Partial 取捨

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| K1 | skill の 3 層分類強制 | **スキップ** | Pruning-First 違反、skill 増殖リスク、pattern field の拡張で代替可能 |
| K5 | graph-level reliability | **採用** (S1 に統合) | Step 0.7 で composition depth metric として実装 |
| K7 | /epd 責務境界 | **スキップ** (実装は保留) | ADR-0008 に drive 責任を記述することで最小限カバー |
| G1 | Tool Poisoning hook | **スキップ** | mcp-audit + mcp-response-inspector で既に arXiv ベース実装済み |
| G2 | Skill Graph Embedding | **スキップ** | YAGNI、Planning overhead 大 |

### Already 強化 取捨

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | composition_depth + PLANS.md ceiling | **採用 (A1)** | 最優先、観測の穴を埋める |
| S2 | Coordinator vs Human RAM ADR | **採用 (A2)** | 中核教義と記事提唱の衝突を明文化しないと将来揺らぐ |

## Plan

### Task 1: /skill-audit に composition_depth metric + PLANS.md compound ceiling

- **Files**:
  - `.config/claude/skills/skill-audit/SKILL.md` (Step 0.7 追加)
  - `PLANS.md` (Compound Plan Ceiling セクション追加)
- **Changes**:
  - SKILL.md: Step 0.7 Composition Depth Check を新設。Skill() 明示呼び出し / 自然言語呼び出しフレーズ / Agent() / Bash 間接呼び出しを静的解析し、最大 depth を算出。判定閾値 (1-2: atom/simple molecule、3-5: complex molecule、6-8: compound、9+: over-ceiling)
  - PLANS.md: Compound Plan Ceiling セクションで ≤8 molecules 推奨と分割指針。ADR-0008 / skill-audit Step 0.7 への参照
- **Size**: M
- **Rationale**: Gemini の $0.9^n$ 裏付け + Codex の A1 優先度
- **Status**: ✅ 完了

### Task 2: ADR-0008 (Coordinator vs Human RAM)

- **Files**: `docs/adr/0008-coordinator-vs-human-ram.md`
- **Changes**:
  - Context: Skill Graphs 2.0 Human RAM ↔ Coordinator パターンの衝突
  - Decision: Coordinator を維持し、drive 責任を atom / simple molecule / complex molecule / compound でレイヤリング。並列 5 は atom/simple molecule に限定、compound は 1 本ずつ
  - Consequences: 中核教義保持、判断軸明確化、並列度制約
- **Size**: S
- **Rationale**: Codex の前提誤り指摘を取り込む
- **Status**: ✅ 完了

### Task 3: 分析レポート + プラン保存 + MEMORY.md ポインタ

- **Files**:
  - `docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md` (本ファイル)
  - `docs/plans/active/2026-04-23-skill-graphs-2.0-plan.md`
  - `MEMORY.md`
- **Changes**: 本レポート / プラン / ポインタ 1 行
- **Size**: S

## Risks & Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-----------|
| composition_depth の静的解析が自然言語呼び出しを取りこぼす | metric の信頼性低下 | Step 0.7 に「低信頼」と注記、runtime チェインは別物と明記 |
| ADR-0008 の層境界が実運用で曖昧 | drive 責任の判定ブレ | ADR-0008 Consequences にレベル境界の曖昧さを明示、6-12 ヶ月後の再評価を予告 |
| Pruning-First 違反の隣接再発 | skill 増殖 | K1/G2 の棄却を Decision Log に残す |

## Execution

| Size | Approach | 採用 |
|------|----------|------|
| M | ユーザー確認後、同一セッションで実行 | ✅ |
