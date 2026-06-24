---
date: 2026-06-25
type: absorb-analysis
source:
  title: "Agent-as-a-Router: Agentic Model Routing for Coding Tasks (ACRouter)"
  url: https://arxiv.org/abs/2606.22902
  authors: Pengfei Zhou, Zhiwei Tang, Yixing Ma, et al.
family: multi-agent-orchestration / model-routing
status: rejected-data-regime-mismatch
adopted: 0
codified: 2  # 判断 codify (closed-loop plan 着手条件 + model-routing.md 注記)
method: "Workflow 9 agents (Map 6 次元 + Critique 3 レンズ adversarial)"
---

# ACRouter (Agent-as-a-Router) absorb 分析

## TL;DR

ACRouter をフルで取り込むことは **不採用 (reject)**。理由はベンチの弱さではなく、**dotfiles の data regime が論文の前提を構造的に満たさない**こと。実データで立証した。論文そのものではなく「なぜ活かせないか」の判断を成果物にした (closed-loop plan の着手条件 + model-routing.md の方針注記)。

中心洞察 "information deficit > reasoning failure" は移植価値があるが、既に CLAUDE.md `<core_principles>` の "Scaffolding > Model" に codify 済み = 新規取り込み不要。

## Source Summary

ルーティングを **C-A-F loop** (Context→Action→Feedback→Context) として定式化し、デプロイ中に execution-grounded experience を蓄積して「情報ギャップ」を閉じる。

- **中心的発見**: ボトルネックは reasoning failure ではなく **information deficit**。dimension 別の実績統計を vanilla LLM router に足すだけで 41.41% → 47.74% (+15.3% relative)、heuristic DimensionBest (47.50%) すら超える。
- **3 モジュール**: Orchestrator (DimensionBest priors + Memory top-10 kNN + fine-tuned Qwen3.5-0.8B + heuristic weighted voting) / Verifier (AST + sandbox exec + self-consistency + LLM-judge を task-type 別 weight で統合、ground-truth test 不要) / Memory (online vector store, task-embedding kNN k=10 sim≥0.5, FIFO 20K)。
- **cost-aware reward**: r = 1.0·perf − 0.1·cost($)。regret-based streaming 評価 (CumReg = N·(V_oracle − V_router))。cold-start は probing set 200 val tasks で warm-start。
- **前提**: ~10K probing set、fine-tune 基盤、複数モデルを全タスクで実走させる予算。ensemble/MoA は扱わない (routing-centric = タスクごと単一ベストモデル)。

## Saturation Gate (Phase 1.5)

family: multi-agent-orchestration (N=14, 飽和気味) に近いが、C-A-F loop / information-deficit / regret-based eval / execution-grounded Verifier feedback は prior absorb に名指しできる rehash がなく **delta 大 → PASS (novel)**。ユーザー明示要求 + ultracode で続行。

## Map: dotfiles 6 次元マッピング (実データ)

全 6 次元が **gap または partial**。F→C loop が構造的に断線している。決定的なのは実データ:

| 次元 (ACRouter component) | verdict | dotfiles 実態 |
|---|---|---|
| Orchestrator + dimension stats | gap | `model-routing.md` は static Tier 表。`agent-invocations.jsonl` に `task_type` 全件欠落 = dimension priors の原料なし |
| F→C loop (Feedback→Context) | gap | `dispatch_logger.sh` JSONL / `collect-result.sh` 結果が次の routing に戻らない。3 箇所で断線 |
| Memory (kNN 経験 retrieval) | gap | `race-outcomes.jsonl` / `routing-decisions.jsonl` 不在 (find 0 件)。過去実績を routing に引く仕組みなし |
| Verifier ([0,1] スコア) | partial | code-reviewer/codex-reviewer の LLM-judge と completion-gate の pass/fail はあるが、単一 [0,1] スコアに統合されず routing に紐付かない |
| cost-aware reward | gap | cost-gate は AutoEvolve 予算管理のみ。perf×cost 結合スコアなし。token_in は placeholder (多くが値 1) |
| hub-and-spoke (経験駆動) | gap | conductor=メインが毎回ゼロから役割割当、過去実績を使わない |

**決定的な実データ** (`agent-invocations.jsonl`, 1299 件):
- model 記録は 303/1299 件のみ (残 996 = `model=None`)。記録分も **sonnet 272 (90%) / haiku 25 / opus は 73 日で 6 件**。
- `score` 全件 0.0、`exit_status` 全件 completed (失敗ラベルすら無い)。
- `task_type` 全件欠落。
- `/improve`・AutoEvolve は 2026-05-03 retire 済み (自動更新トリガー不在)。
- `docs/plans/2026-04-11-routing-observability-closed-loop.md` が F→C 断線を自己診断済み、Wave 1-3 は **status: proposed のまま 2 ヶ月放置**。

## Critique: 3 レンズ adversarial (opus high)

3 レンズ全てが「フル ACRouter は不採用」に収斂した。

### over-engineering 検出
ACRouter の重量級要素 (fine-tuned Qwen / ~10K probing set / sandbox Verifier 統合 / 20K vector Memory + kNN / regret harness / リアルタイム cost-aware 閉ループ) は全て **N/A または over-engineering**。**前提崩壊**: 選択が 90% Sonnet に収束し、学習で削れる regret がほぼゼロ。改善の母数がないところに学習機構を足すのは定義上 over-engineering。

### low-data regime 懐疑 → reject
「実装すれば閉じる gap」ではなく「**data 生成構造が経験駆動 routing を統計的に不能にしている構造的不一致**」。
- モデル選択 experience は 73 日で 303 件・週数十件、opus=6 件と片肺 → バンディットの片腕がほぼ未試行で regret 推定が定義不能。
- task_type 軸ゼロで DimensionBest priors のセルが原理的に空 (proxy しても 32/44 セルが n<30)。
- verifier score 全件 0.0 = Feedback の相互情報量ゼロ。過去ログは遡及スコアリング不能。
- cold-start を救う probing set も遡及生成原資も無い。kNN 近傍は密度・意味分離の両面で機能保証なし (negative transfer リスク)。

### minimal F→C loop 設計
フル却下。最小案として agent-invocation-logger.py に score (review verdict 文字列の粗い 3 値) + task_type (keyword 分類) の 2 フィールド追加が提示されたが、low-data レンズが「母数不足で推定値がノイズと区別できない」と警告。`race-outcomes.jsonl` / `routing-decisions.jsonl` の新設は「消費者不在の死蔵」(claude-observe.sh 退役の教訓) で却下。

## 決定

**フル ACRouter: 不採用 (reject)**。data regime 不一致を実データで立証。

**採用 (codify のみ、新規インフラ 0)**:
1. `docs/plans/2026-04-11-routing-observability-closed-loop.md` に着手条件を明文化 — 「着手前提 = model 選択の分散回復 (現状 90% Sonnet)、score に非ゼロ信号。それまで Wave 2-3 は YAGNI」。2 ヶ月放置プランに決着。
2. `.config/claude/references/model-routing.md` に方針注記 — 「routing 改善は学習器でなく dimension 実績統計の可視化 (information-deficit 原理)。当 harness は learnable regret 小。閉ループ化は分散が増えてから」。

これは core principle **「判断をゲート化する / 批評を成果物にする」**「Build to Delete」に沿う。論文を helpful に取り込まず、網羅検証の上で却下を立証し、その判断を将来参照可能な artifact にした。

## Codex degraded (Phase 2.5 の制約)

model-family diversity (bias mitigation) のため Codex worker を hub-and-spoke で起動したが、重い hearable login shell (morning-briefing hook) でコマンドが send 不達 (`return`/`enter` 両方効かず)。degraded として記録。opus 3 レンズの adversarial が一致し、self-preference bias で甘く見た形跡もなく (むしろ厳しく却下)、結論の確度は高いと判断。

**副次の learning**: `launch-worker.sh` の codex case は claude case (`sleep 5`) と違い shell-ready を待たずに send する。重い login shell の workspace で send 不達になる。修正候補。

## 着手条件 / 撤退条件 (再掲)

将来 ACRouter (または閉ループ routing) に着手する前提:
- `agent-invocations.jsonl` の model 多様性が回復 (sonnet 偏重が崩れる)
- `score` に非ゼロ信号が乗る

着手するなら ACRouter フル移植ではなく、closed-loop plan Wave 2 を「計測のみ」スコープに絞り、3 ヶ月貯めて「sonnet 偏重を覆すモデル差がデータに出るか」を先に検証 → 出なければ Build to Delete で計測ごと撤去。
