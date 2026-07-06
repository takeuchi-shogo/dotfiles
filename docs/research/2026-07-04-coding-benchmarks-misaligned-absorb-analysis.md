---
title: "Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering — absorb analysis"
date: 2026-07-04
status: light-phase2-only
adoption: 0
operation: ingest-skip (light Phase 2, adopt=0)
family: eval-loop / harness-quality-gate (隣接 — 厳密 taxonomy 4 族には非該当、明示判断で隣接扱い)
saturation: PASS (warning) + Step 4.5 SATURATED-trending (直近 2 件連続採用 0) → user 選択 light-phase2
source:
  title: "Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering"
  authors: "Maria I. Gorinova, Macey Baker, Amy Heineike, Maksim Shaposhnikov, Rob Willoughby, Dru Knox"
  type: academic-position-paper
  url: https://arxiv.org/abs/2606.17799
  submitted: 2026-06-16
fetch_metadata:
  url: https://arxiv.org/abs/2606.17799
  route: webfetch (alphaxiv overview/abs とも 403 → arxiv abs + html。Jina Reader curl は permission denied)
  faithfulness: WebFetch 内部 Haiku 要約経由。長文引用は要約ベース、主要数値は abs / html の 2 経路抽出で相互確認済み
---

# Coding Benchmarks Misaligned — absorb analysis (mini report)

## Source Summary

- **主張**: 現行コーディングベンチマーク (SWE-Bench 系) はエージェント前時代の設計。コーディングエージェントの実体は「モデル + ハーネス + 環境 + フィードバック信号」の system harness なのに、単一 end-to-end スコアに折り畳むため 3 症状を生む — (1) モデルとハーネスの混同、(2) 単一参照解への固定、(3) コンポーネント単位信号の欠如。
- **根拠**: 同一モデル (Claude Opus 4.6) でハーネス差 20pt+ (TerminalBench) / SWE-Bench Verified で 2-3x rate variation / solution leak 32.67% / AIDev 456k PR の実世界受入率 35-64% vs ベンチマーク >70% の乖離。
- **前提条件**: 主聴衆はベンチマーク設計者・リーダーボード運営者。個人 harness への適用は「原則翻訳」が必要 (zero-trust absorb と同型)。

## Saturation Gate (Phase 1.5)

- 本論文は未 absorb (索引 hit なし)。厳密 taxonomy 4 族に非該当 → **明示判断で eval-loop / harness-quality-gate family に隣接扱い** (N≥5: ai-evals-framework / Better Harness / Skill Eval Loop / Hermes / Opik)。
- 採用率 ≥20% → PASS (warning)。ただし **Step 4.5 発火**: 直近 2 件 (Opik 2026-06-14 採用 0 / Hermes 2026-05-31 採用 0) が連続 reject → SATURATED-trending。
- user 選択: **light-phase2** (delta 4 手法のみ検証)。
- Stale-Plan Audit: 直近 2 件とも status 明示済 (light-phase2-only / reference-only、採用 0 でタスクなし) → audit 対象なし。

## Per-method 照合台帳 (全 7 手法 — scope 判断の立証)

| # | current 手法 | verdict | 根拠 (rehash/除外は名指し) |
|---|---|---|---|
| M1 | System Harness 5 構成要素分解フレーム (Tasks/Agent Harness/Environment/Context/Feedback Signals) | excluded as rehash | `~/.claude/CLAUDE.md` `<core_principles>` の「Scaffolding > Model / 観測可能にする: 協調プロトコル選択が品質差異の 44%、モデル選択は ~14%」+ harness-engineering family 既 absorb 群 (`2026-03-28-harness-engineering-comprehensive-analysis.md` ほか N=20+)。「エージェント = モデルでなくシステム複合体」という概念フレームは codify 済み |
| M2 | フィードバック 3 層ループ taxonomy (inner/middle/outer) | **delta (in-scope)** | Phase 2 で検証 (下表) |
| M3 | 非モデル軸 ablation (固定ベースライン + ハーネス軸比較) | **delta (in-scope)** | Phase 2 で検証 (下表) |
| M4 | 複数形状 behavioral verifier (property / oracle / differential) | **delta (in-scope)** | Phase 2 で検証 (下表) |
| M5 | コンポーネント単位評価 (context 有効性・invariant 遵守度) | **delta (in-scope)** | Phase 2 で検証 (下表) |
| M6 | 行動仕様・不変条件の形式化 (operationalization gap) | excluded as N/A | 論文自身が「最難関の未解決問題」と位置づけ解法を提供しない (open problem)。dotfiles 側は /spec skill + golden-check (GP-001〜011) + completion-gate が仕様強制の実装形。採用可能な手法が原文に存在しない |
| M7 | 実世界シグナル (受入率/revert 率) とベンチマークスコアの乖離監視 | excluded as N/A | リーダーボード運営者向け提言。個人版の outer-loop 信号の実態は M2 の outer 層判定に統合して検証済み |

## Phase 2 判定 (Pass 1: Sonnet Explore / Pass 2: main 判定)

| # | 手法 | 判定 | 現状 |
|---|---|---|---|
| M2 | 3 層フィードバック taxonomy | **Already (inner/middle) + 既知 Partial (outer)** | inner: lefthook (pre-commit 9 checks) + completion-gate.py + PostToolUse auto-format で成熟。middle: review tier preflight + Codex Review Gate で成熟。outer: 古典的 PR 受入/revert 追跡は個人 dotfiles に不在 — 代替信号は `experiment_tracker.py` (measure_effect/check_regression) と `calibration-verdict-logger.py` (人間裁定一致率)。outer 層が構築→断線→退役を繰り返す構造的弱点は `docs/decommission-log.md` に記録済みの既知課題であり、論文は解決手法を提供しない → 採用なし |
| M3 | 非モデル軸 ablation | **Partial (採用非推奨)** | skill 単位は実装済: skill-audit 3-arm evaluation (モデル固定・無介入/簡潔指示/with-skill の 3 群) + `aggregate_benchmark.py --variants` (K-variant RLOO/GRPO) + `split_holdout.py` (層化 holdout)。hook/prompt/CLAUDE.md レベルの汎用 ablation gate は不在だが、これは /improve 退役 (2026-05-03、5 サイクル連続 false-positive) の**意図的設計判断**。汎用化の再導入は Hermes absorb の judgment anchor (retire 維持が正解) と衝突 → 不採用 |
| M4 | 複数形状 verifier | **Already (強化不要)** | 論文の 3 形状すべてに対応物あり — differential: `review-consensus-policy.md` (複数レビュアー合議 + CONFLICT 明示 + capability-weighted synthesis) / oracle: `evaluator-calibration-guide.md` + `evaluator_metrics.py` (TPR/TNR + Rogan-Gladen 補正、test 済) / property 的: planted-bug reviewer eval (FM カテゴリ単位合否、単一 golden diff 非依存) |
| M5 | コンポーネント単位評価 | **Already (強化不要)** | skill 単位 (usage tier + per-step credit assignment)、reviewer 単位 (`review-metrics.jsonl` + capability scores)、agent 単位 (orthogonality check) が実装済。既知の限界 = `observability-signals.md` Gap 1-6「信号は収集されるが action loop 未接続 (owner unassigned)」— 論文の症状 3 と同型の問題意識だが、論文は接続方法を提供しない (問いの提示のみ) → 採用なし |

- **Phase 2.5**: 省略 (light-phase2 flag、Gap 判定 0 件のため昇格条件不成立)。
- **Phase 3 Triage**: 採用候補 0 件のため省略。

## Decisions

- **採用: 0 件** — 4 delta 手法すべて Already / Partial (既知)。Partial の残余 (汎用 harness ablation / outer-loop 持続) はいずれも過去の意図的 retire 判断と衝突する方向で、論文側に反証となる新手法・新データなし。
- **Validation-only follow-up: 0 件** — Explore 結果は既知の状態 (decommission-log / observability-signals Gap 1-6) を再確認したのみで、stale fact / drift の露出なし。
- **Reference 価値 (採用件数外)**: CLAUDE.md「Scaffolding > Model」原則および harness eval 設計への **academic backing**。引用可能データ: 同一モデルでハーネス差 20pt+ (TerminalBench) / AIDev 実世界受入 35-64% vs bench >70%。ハーネス評価の設計論を外部に説明する際の一次文献として本レポートをポインタ化。

## 教訓

- eval 系 position paper は dotfiles の既存哲学と**一致しすぎる**ケースがある — 一致は採用ではなく backing (引用価値) として記録する。「論文が dotfiles の設計判断 (multi-shaped verifier / component attribution / ablation) を後追いで正当化した」構図。
- 主聴衆がベンチマーク運営者の提言 (メタデータ義務化・リーダーボード改革) は個人 harness では機械的に N/A — enterprise→個人の原則翻訳フィルタ (zero-trust absorb の教訓) がそのまま効いた。
