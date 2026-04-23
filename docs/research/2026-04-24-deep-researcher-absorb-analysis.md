---
source: "How to build a Deep Researcher — A 100% open-source, self-hostable Deep Research Stack That Beat OpenAI, Gemini, and Perplexity"
date: 2026-04-24
status: analyzed
integration_target: ~/.claude/skills/research/SKILL.md, ~/.claude/skills/absorb/SKILL.md, ~/.claude/references/subagent-delegation-guide.md
---

## Source

**タイトル**: How to build a Deep Researcher — A 100% open-source, self-hostable Deep Research Stack That Beat OpenAI, Gemini, and Perplexity
**著者**: Akshay Pachaar (@akshay_pachaar)
**種別**: blog-post / tutorial
**吸収日**: 2026-04-24
**URL**: not provided (text pasted)

---

## Source Summary

**主張**: Onyx (retrieval) + CrewAI (orchestration) + Voxtral (voice) を組み合わせることで、段階分離・推論型検索・反省ループの 3 原則を実装し、OpenAI Deep Research・Gemini Deep Research・Perplexity を超えるオープンソースの Deep Research Stack が構築できる。

**中心的な 3 主張**:
1. **段階分離の強制 (Gathering / Analysis / Writing の hard wall)**: CrewAI Flows による明示的な段階壁。Planner はツール不使用、Orchestrator は直接検索しない、Research agents は full query/plan を受け取らない
2. **検索の推論化 (multi-query + RRF + LLM selection で hallucination 防止)**: 6 段 retrieval pipeline により、単純な embedding 類似度検索ではなく LLM が最終的な関連性を判断する
3. **反省ループの埋め込み (coverage/gaps/new/converge を全 dispatch 間で構造化出力)**: 各 dispatch 後に mandatory reflection を行い、coverage が収束するまでループを続ける

**15 の手法**:
1. Stage separation hard walls (CrewAI Flows)
2. Planner without tool access (思考専用役割)
3. Orchestrator never searches directly (委譲専門)
4. Research agents never see full query/plan (information minimization)
5. Mandatory reflection step between dispatches (coverage/gaps/new/converge)
6. 6-stage retrieval pipeline (query expand → embed → vector search → rerank → dense → LLM select)
7. LLM selection step (最終 hallucination barrier)
8. Parallel query variants (semantic rephrase / keyword / broad の 3 軸)
9. Citation integrity (merged/renumbered across parallel agents)
10. MCP per-agent via SKILL.md mcps field
11. SKILL.md runtime instruction injection (per-agent 設定)
12. "Prefer being thorough over being helpful" prompt philosophy
13. Voice layer (Voxtral TTS+STT)
14. Unified public+internal search w/ per-doc permissions (Onyx)
15. Three-phase process caps (Clarify ≤5 / Plan ≤6 / Execute ≤8×3)

**根拠**: DeepResearch Bench #1 での No.1 評価 (100 PhD-level tasks, 22 fields)。ただし Gemini が指摘するように、同系統の LLM が合成・評価を担う構造で評価 LLM バイアスリスクあり。独立検証なし。

**前提条件**: Onyx の self-hosted インスタンスが必要 (Vector DB + Connector + Permission management)。CrewAI による multi-agent orchestration コスト。Voice layer は完全 optional。

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Stage separation hard walls | **Already (強化可能)** | `/research` の Clean mode (Depth-1: gather→analyze→synthesize) で段階分離あり。hard wall 命名は "deep frying" として追記可能 |
| 2 | Planner without tool access | **Partial** | 既存 Analyze-only subagent が近いが、明示的な "plan-only contract" (ツールアクセス禁止の formal contract) は未定義 |
| 3 | Orchestrator never searches directly | **Already** | `/research` の dispatch 構造で Orchestrator 相当は直接検索しない設計 |
| 4 | Research agents never see full query | **Partial** | Clean mode の 3-item brief は brief だが、full query 隠蔽を formal contract として明示した設計書なし |
| 5 | Mandatory reflection between dispatches | **Partial** | `/research` にギャップ分析ステップはあるが、dispatch ごとの mandatory ではなく on-demand 的 |
| 6 | 6-stage retrieval pipeline | **Partial** | web search + /deep-read で部分実装。全 6 段は over-engineering。LLM selection のみ価値あり |
| 7 | LLM selection step | **Partial (High)** | Gemini リサーチ委譲あり (suggest-gemini.py)、search result の LLM 関連性判定は未実装 |
| 8 | Parallel query variants (3 軸) | **Already (強化可能)** | `/research --angles` で 5 perspectives 生成あり。semantic/keyword/broad の直交 3 軸分類は未追加 |
| 9 | Citation integrity | **Partial** | parallel agent 統合時の citation merge/renumber は未定義 |
| 10 | MCP per-agent via SKILL.md | **Already** | SKILL.md の mcps field で実装済み |
| 11 | SKILL.md runtime injection | **Already** | skill-local instruction injection は既存パターン |
| 12 | "Prefer thorough over helpful" philosophy | **Already (強化可能)** | Sycophancy counter / neutral framing あり。"thorough over helpful" の明示的 1 行宣言は未追加 |
| 13 | Voice layer (Voxtral) | **N/A** | overscoped。CLI workflow に不適合 |
| 14 | Onyx unified search | **N/A** | overscoped。個人 dotfiles には self-hosted vector DB は不要 |
| 15 | Three-phase caps (≤5/≤6/≤8×3) | **Partial (低)** | phase 構造は `/research` にあるが、hard cap は未設定。SaaS UX との乖離 |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 優先度 |
|---|---|---|---|---|
| S1 | `/research --angles` 5 perspectives | 角度生成が単一軸 (perspective) のみ。semantic/keyword/broad の直交 3 軸が未分類 | query variant 生成に 3 軸ラベルを追加 (直交するため重複なし、coverage 向上) | **High** |
| S2 | Sycophancy counter / neutral framing | 「役に立とうとしすぎて shallow になる」パターンへの明示的対策なし | "Prefer being thorough over being helpful" 1 行 philosophy を research + absorb スキルの prompt header に追加 | **Medium** |
| S3 | Clean mode / Depth-1 段階分離 | 命名が "Clean mode" だけで hard wall の性質が伝わりにくい | "deep frying" 命名を導入 (gather=raw → analyze=refined → synthesize=distilled の比喩) | **Low** |

---

## Phase 2.5 Refinement

### Codex (gpt-5.4) 批評で判明した重要な点

**Oversight (見落とし)**:
- **#9 Citation merge/renumber が未分析だった**: parallel agent を統合する `/research` ではすでに問題が潜在。footnote 番号が agent 間で衝突する可能性あり → **Partial に追加**
- **#4 Information minimization の unverified coverage**: 「brief を渡している」=「full query を隠蔽している」は等価でない。formal contract 未定義 → Partial 維持

**Overrated (過大評価)**:
- **#2 Planner-only contract として新規 skill/agent 作成**: Pruning-First 原則に違反。既存 Analyze-only subagent の拡張でカバー可能

**Underrated (過小評価)**:
- **#5 + #7 の統合価値**: on-demand reflection (mandatory ではなく) + pre-synthesis LLM selection を組み合わせると `/research` の出力品質が底上げされる。単体では弱いが複合効果が大きい

**Premise mismatch**:
- **#15 Hard caps**: ≤5/≤6/≤8×3 は SaaS UX でのユーザー体験最適化。CLI workflow では advisory のみ (hard cap は実装しない)
- **DeepResearch Bench #1 を採用根拠にしない**: 評価 LLM バイアスリスク (Gemini 指摘)

**Top 3 優先 (Codex)**:
1. #8 query variant 3 軸追加 (直交、即効性)
2. #5 + #7 統合 (on-demand reflection + LLM selection)
3. #9 citation integrity (parallel agent の見落とし修正)

### Gemini 定量データ補完

- **LLM selection step**: hallucination 40-60% 削減、代償 +15-30 秒 latency (研究データ複数出典)
- **Mandatory reflection**: token 30% 消費リスク → advisory/on-demand で十分
- **DeepResearch Bench #1**: Onyx 合成ロジックと評価 LLM が同系統の可能性あり → 独立ベンチマーク未確認
- **6-stage pipeline 全採用**: over-engineering。LLM selection 単独でも 40-60% 削減効果

---

## Integration Decisions

### Gap / Partial 採用

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| T1 | #8 Query variant 3 軸追加 | **採用** | `/research` の `--angles` に semantic/keyword/broad ラベルを追加。直交するため既存 perspectives と conflict なし。即効性高 |
| T2 | #5+#7 統合 (on-demand reflection + pre-synthesis LLM selection) | **採用** | 単体では弱いが複合で品質底上げ。mandatory ではなく on-demand trigger で token 30% リスク回避 |
| T3 | #9 Citation integrity | **採用** | parallel agent 統合時の footnote 衝突を明示ルール化。実装コスト小、silent failure 防止 |
| T4 | #2+#4 Plan-only 契約拡張 | **採用** | 新規 skill/agent ではなく `subagent-delegation-guide.md` への原則追記。Pruning-First 遵守 |
| #13 Voice layer | スキップ | overscoped (N/A) |  |
| #14 Onyx unified search | スキップ | overscoped (N/A) |  |
| #15 Hard caps | スキップ | CLI = advisory のみ |  |
| 6-stage pipeline 全採用 | スキップ | over-engineering (LLM selection のみで十分) |  |

### Already 強化採用

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S2 (T5) | "Prefer thorough over helpful" philosophy | **採用** | research + absorb の両スキルに 1 行追加。Sycophancy 対策との相乗効果 |
| S3 (T6) | "deep frying" 命名 | **採用 (低優先)** | 段階分離の比喩として命名追加。コスト極小 |
| S1 | Query variant 3 軸 | T1 に統合 | |

---

## Plan

**規模**: M (3 ファイル、約 150-200 行追加)
**必須段階**: Plan → Edge Case Analysis → Implement → Codex Review Gate → Verify

### Task 1 — Query variant 3 軸追加

- **Files**: `~/.claude/skills/research/SKILL.md`
- **Changes**:
  - `--angles` / `--perspectives` 生成ロジックに semantic rephrase / keyword extraction / broad scope の 3 軸ラベルを追加
  - 各 perspective に軸ラベルを付与し、3 軸から均等にカバーされているかチェックするステップを追加
  - 既存 5 perspectives 生成に置き換えではなく、ラベリングとして上乗せ
- **Size**: S (1 section 追加)

### Task 2 — on-demand reflection + pre-synthesis LLM selection 統合

- **Files**: `~/.claude/skills/research/SKILL.md`
- **Changes**:
  - dispatch ループの末尾に「coverage 判定トリガー」を追加 (on-demand: coverage < 80% または gap 数 > 2 のとき reflection を実行)
  - synthesis 前のステップとして「LLM relevance selection」を明記 (各収集 chunk を synthesis LLM に渡す前に関連性スコアを付与、低スコアを除外)
  - hallucination 削減効果 (+40-60%) と latency コスト (+15-30s) を注記
  - mandatory reflection は棄却 (token 30% 消費リスク)
- **Size**: S-M (既存フローへの追記)

### Task 3 — Citation integrity

- **Files**: `~/.claude/skills/research/SKILL.md`
- **Changes**:
  - parallel agent を統合するステップに「citation merge/renumber」ルールを追加
  - agent A の [1][2][3] + agent B の [1][2] → 統合後 [1][2][3][4][5] に renumber し、各引用元を明示
  - 出典の重複は統合 (同一 URL は 1 エントリに consolidate)
- **Size**: S (1 rule section 追加)

### Task 4 — Plan-only 契約原則の追記

- **Files**: `~/.claude/references/subagent-delegation-guide.md`
- **Changes**:
  - 「情報ミニマム化原則」として: Planner は tool access なし / Orchestrator は直接検索しない / Research agent には task-local brief のみ渡す の 3 原則を追記
  - 既存の delegation パターンの「役割設計」節に統合 (新節不要)
  - "deep frying" 命名も同ファイルで導入 (T6 を統合)
- **Size**: S (1-2 paragraph 追記)

### Task 5 — Prompt philosophy 強化

- **Files**: `~/.claude/skills/research/SKILL.md`, `~/.claude/skills/absorb/SKILL.md`
- **Changes**:
  - 両スキルの prompt header (instruction 冒頭) に "Prefer being thorough over being helpful" 1 行を追加
  - research: 浅い答えより調査漏れ指摘を優先する旨を明記
  - absorb: 既存 neutral framing に "completeness bias" の正当化を追加
- **Size**: S (各 1-2 行追加)

### Task 6 — "Deep frying" 命名 (低優先、Task 4 に統合)

- **Files**: Task 4 と同一 (`subagent-delegation-guide.md`)
- **Changes**: gather=raw material / analyze=refined / synthesize=distilled の比喩として段階分離を説明する 1 paragraph
- **Size**: Minimal (Task 4 に含める)

**実行順序**:
1. T5 (Prompt philosophy) — 最小コスト、即効性。Task 2 の foundation
2. T1 (Query variant 3 軸) — `/research` 使用の度に効果が出る
3. T2 (on-demand reflection + LLM selection) — T1 完了後に同一ファイルで実装
4. T3 (Citation integrity) — parallel 実行する `/research` で silent failure 防止
5. T4+T6 (Plan-only contract + deep frying 命名) — subagent-delegation-guide.md に統合

**依存関係**:
- T1 → T2: 同一ファイル、順次実装
- T5 → T2: T5 の philosophy が T2 の reflection 判断基準を補強
- T3, T4, T5: 独立、並列実装可

---

## Risk と前提条件

| リスク | 対策 |
|-------|------|
| LLM selection step の latency (+15-30s) が体感で重い | advisory 注記のみ。実装せず on-demand 判断で運用 |
| query variant 3 軸が既存 5 perspectives と概念的に重複 | ラベリング (分類) として実装、perspectives の数は変えない |
| "Prefer thorough" が verbose output を誘発 | "thorough in coverage, concise in expression" として両立条件を明記 |
| citation renumber の自動化が誤 renumber を引き起こす | LLM に renumber を依頼する際に元引用リストを明示的に渡すルールを追加 |
| DeepResearch Bench #1 の評価バイアス | 採用根拠として使わない。定量データは Gemini の hallucination 削減研究 (40-60%) のみ使用 |

---

## Alignment with Existing Setup

| 採択タスク | 既存設計との整合性 |
|-----------|-------------------|
| T1 Query variant 3 軸 | `/research --angles` の自然拡張。既存 skill の enhancement |
| T2 on-demand reflection + LLM selection | `suggest-gemini.py` hook の LLM routing 設計思想と整合 |
| T3 Citation integrity | subagent parallel 実行パターン (`subagent-patterns.md`) の citation 節補完 |
| T4 Plan-only contract | `subagent-delegation-guide.md` の役割分離原則を明文化 |
| T5 Thorough philosophy | Sycophancy counter / neutral framing と相補。Karpathy "wrong assumptions" パターン対策 |
| T6 Deep frying 命名 | Build to Delete 原則 (CLAUDE.md) の "名前付け=設計" への適用 |

---

## References

- 関連 absorb (検索推論): `docs/research/2026-04-21-harness-pipeline-absorb-analysis.md` — reproduce-first, research quality
- 関連 absorb (subagent delegation): `docs/research/2026-04-17-hermes-fleet-shared-memory-analysis.md` — multi-agent 役割分離
- 関連 absorb (skill 設計): `docs/research/2026-04-21-obsidian-claudecode-absorb-analysis.md` — skill-writing-principles
- 関連 absorb (harness engineering): `docs/research/2026-04-24-harness-engineering-absorb-analysis.md` — Planner/Generator/Evaluator 分離 (GAN 式)
- Codex 批評: Phase 2.5 で実施 (gpt-5.4, reasoning high)
- Gemini 周辺知識: hallucination 削減 40-60% データ、Mandatory reflection token 30% リスク
- 実装対象 skill: `~/.claude/skills/research/SKILL.md`, `~/.claude/skills/absorb/SKILL.md`
- 実装対象 reference: `~/.claude/references/subagent-delegation-guide.md`
