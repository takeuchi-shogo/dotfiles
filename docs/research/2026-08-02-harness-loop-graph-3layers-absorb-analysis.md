---
date: 2026-08-02
status: light-phase2-only
family: loop-engineering (N=16) × multi-agent-orchestration/graph era リブランド × harness-engineering (N=17+) cross-family
source: "Agent Harness Engineering vs Loop Engineering vs Graph Engineering" (@LunarResearcher, ユーザー貼り付け全文)
adopted: 1
---

# Harness vs Loop vs Graph Engineering — light-phase2 absorb 分析

## Source Summary

- **主張**: agent システムは harness（環境）/ loop（反復と検証）/ graph（フロー制御）の 3 層に分離して設計・デバッグする。「Environment → Feedback → Flow」。障害はどの層が所有するかを診断してから直す。
- **根拠**: データ・事例なし。概念整理のみの listicle（末尾に Follow/Bookmark CTA）。
- **前提**: production agent 設計者向け、フレームワーク非依存。

## Saturation Gate (Phase 1.5)

- **判定: SATURATED-borderline (delta=1)** → ユーザー選択 light-phase2。
- harness/loop/graph era 系統の 3 本目（0xRafy 07-22 採用0 → 0xCodila 07-25 採用1 → 本記事）。loop-engineering 直近 3 件（Opik / kumai_yu / angeldot_）は全て採用 0。同系統直近 5 件の採用率 1/5 = 20%（境界値）。
- taxonomy 注記: harness-engineering の keyword 閾値（3 語以上）は未達（"harness" 1 語のみ）だが、de-facto family（loop-engineering / graph era リブランド）直撃のため cross-family と明示判断。
- Stale-Plan Audit (Step 7): 同 family 最新 3 件（Dex 07-27 / 0xCodila 07-25 / 0xRafy 07-22）は全て 30 日未満 → 実装猶予期間で audit skip。

## per-method 照合台帳（全 9 手法 — rehash 除外の立証）

| # | current 手法 | verdict | matched_prior |
|---|---|---|---|
| 1 | 3層分離 framing (harness/loop/graph = Environment→Feedback→Flow) | rehash (excluded) | `2026-07-22-graph-engineering-0xrafy-absorb-analysis.md` の「loop の次は graph engineering」era リブランド判定 — 同じ layer taxonomy の命名リブランド、2 本連続で剥がした framing と同一 |
| 2 | Harness 6 要素 (context/tools/persistence/control/safety/observability) | rehash (excluded) | `2026-04-08-cc-harness-blueprint-analysis.md` の「4層フレームワーク + 18手法 → 7項目統合」+ `2026-04-06-agent-harness-anatomy-analysis.md` — harness 構成要素の列挙は anatomy/blueprint 系で既出・統合済 |
| 3 | Loop anatomy 7 要素 (trigger/goal/state/policy/evidence/feedback/stop) | rehash (excluded) | `2026-06-17-loops-with-claude-absorb-analysis.md` — 一次ソース Osmani の loop 構成要素は `comprehension-debt-policy.md` に出典明記で absorb 済、全 11 手法 named rehash と同内容 |
| 4 | "Loop on evidence, not confidence" (evidence ベース stop) | rehash (excluded) | `2026-06-14-opik-self-repairing-harness-absorb-analysis.md` 手法5「verification bar→loop safety」+ 手法6「green-but-unread」— 「agent の done 宣言は stop 条件でない」と同一命題 |
| 5 | Graph 設計対象 (nodes/edges/routing/concurrency/durability/human gates) | rehash (excluded) | `2026-07-22-graph-engineering-0xrafy-absorb-analysis.md` 11-step roadmap（10/11 named rehash、#10 Fallback Paths も Already 検証済）— graph 設計要素の列挙は 2 本で照合済 |
| 6 | **層別障害診断ルール** (operate 不能→harness / 不安定→loop / プロセス複雑→graph) | **ambiguous → 検証対象** | 症状→層の写像 heuristic。0xCodila #12「非適用条件」(採用済) は graph 単層の適用判断で、3 層への routing 表としては prior に named 対応物なし |
| 7 | Anti-patterns 5 種 | rehash (excluded) | graph too early = `2026-07-25-graph-engineering-0xcodila-absorb-analysis.md` #12（採用済）/ self-grading = 同レポート「Nothing grades its own homework」rehash 判定 / keep-trying = kumai_yu の stop rule / junk-drawer = `2026-05-02-30-subagents-2026-absorb-analysis.md` Subagent Count Ceiling / blame-the-model = `2026-07-04-coding-benchmarks-misaligned-absorb-analysis.md` Scaffolding>Model |
| 8 | Production checklist (5 カテゴリ) | rehash (excluded) | `2026-07-08-agentic-os-fable5-builders-guide-absorb-analysis.md` の 8 BUILD checklist（~90% 実装済判定）— 手法 2/3/5 の質問形式への再列挙で独立内容なし |
| 9 | Graphs-when-worth-it（適用/非適用条件） | rehash (excluded) | `2026-07-25-graph-engineering-0xcodila-absorb-analysis.md` #12 非適用条件（Partial→採用、subagent-delegation-guide Red 行として実装済）— 同等の negative criteria |

delta = 1（#6 のみ、ambiguous_count = 1）、prior_methods 取得 = ok。

## Phase 2 判定（#6 のみ、Pass 1 = Sonnet Explore / Pass 2 = Opus）

| 手法 | 判定 | 現状 |
|---|---|---|
| #6 層別障害診断ルール | **Partial** | 層ごとの診断機構は全て存在: harness = `failure-taxonomy.md` HFM-001〜004 + `hook-debugger` Symptom→Action 表 / loop = Circuit Breaker + verification gate / graph = 「Graph vs Prompt 修正診断」。欠けていたのは統合と索引 — `decision-tables-index.md`（CLAUDE.md 参照の総索引）が `repair-routing.md` も failure-taxonomy の診断フローも未リンク（grep 0 hit） |

- 記事原文に specific 提案あり（"Diagnose The Failure Before You Pick The Fix" セクション）— Sonnet imagination ではない。
- 副次発見: `repair-routing.md` は「症状でなく原因のレイヤーを直す」と同型構造だが、レイヤーの意味が**設定ファイル層**（references/rules/…）でありランタイム層とは別軸。混同防止の注記つきで索引に併記。
- Phase 2.5: Gap 0 件のため light flag で省略。

## Adopted / Rejected

- **採用 T1 (S, 1 file, 実装済み)**: `decision-tables-index.md` に「障害診断 系」セクション追加 — 症状→層の 3 行 routing（既存資産へのリンクのみ、新規表なし = instruction DRY）+ 未リンクだった `repair-routing.md` を別軸注記つきで索引化。リンク先アンカー（HFM-00 ×7 / Circuit Breaker ×2 / Graph vs Prompt ×2 / hook-debugger Symptom 表）は grep で実在確認済み。
- **不採用**: 手法 1-5, 7-9（台帳のとおり named rehash）。統一 symptom→層 新規表の作成も不採用（既存 3 資産と重複する parallel 表になるため routing のみ）。

## 教訓

- era リブランド 3 本目でも delta=1 は出た。出たのは「層の定義」でなく「層をまたぐ診断 routing」— 個別資産が揃った後の**索引欠落**は rehash 照合では検出できず、記事の framing が露出させる（0xkkai「索引する側と監視する側の非対称」と同型）。
- 総索引 (`decision-tables-index.md`) は新規表作成時の 1 行追記ルールがあるにも関わらず `repair-routing.md` / failure-taxonomy 診断フローが漏れていた — 「索引への追記」は表の作成者の記憶依存で、mechanism 化されていない（将来の静的照合候補）。

## 逸脱記録（Decision Log）

- Phase 1 Extract: 記事全文が既にコンテキスト内のため Haiku 委譲せず inline 実施（再送は情報ゼロの往復）。
- Phase 4 レポート書き出し: 同理由で Sonnet 委譲せず Opus 直接 Write。
