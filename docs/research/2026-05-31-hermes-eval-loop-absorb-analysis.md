---
title: "How To Fix AI Slop (Using Hermes) — absorb analysis"
date: 2026-05-31
source:
  title: "How To Fix AI Slop (Using Hermes)"
  author: unknown (Hermes vendor marketing)
  type: marketing-article
  url: null (pasted text)
family: eval-loop / harness-quality-gate
saturation: SATURATED-pure-rehash (delta=0)
status: reference-only
adopted: 0
mode: full-workflow (user override of skip recommendation)
---

# How To Fix AI Slop (Using Hermes) — absorb analysis

## Source Summary

Hermes（OSS エージェント）のマーケティング記事。

**主張**: AI slop はプロンプト問題ではなくシステム問題（品質管理層の欠如）。生成側
（prompt/model/memory）ではなく**出力側（測定→ゲート→ループ化）**を直せ。eval loop こそが
システム。

**8 手法**:
1. eval loop（生成→採点→閾値ゲート→修正→再採点）
2. 3 箇所での eval（出荷前 regression / 実行時 guardrail / 本番 continuous sampling）
3. benchmark 3 要素（test cases / metrics 0-1 / threshold 0.7）
4. gold standard（ベスト 20-50 を ground truth に）
5. rubric ベース LLM-as-judge
6. metric library（exact match / validator / semantic similarity）
7. failure → 新テストケース化（👎で書き戻し、品質の床が自動上昇）
8. Hermes 実装（skills / memory / cron / approval buttons）

## Phase 1.5: Saturation Gate

- **Family**: `eval-loop / harness-quality-gate`
- **過去同 family absorb（N ≥ 4）**: Skill Eval Loop（Wave1 実装済）/ Better Harness
  eval hill-climbing / PostHog Friction→Eval / CREAO Self-Healing Tri-judge / Empirical
  Prompt Tuning
- **判定**: SATURATED-pure-rehash（delta=0、全手法が既存 mechanism に対応）
- **ユーザー選択**: continue（skip 推奨を override し、新角度取りこぼし検査のためフル workflow 実行）

## Phase 2: 判定テーブル（Pass 1 Explore + Pass 2 Opus + Codex 修正）

Codex 批評により「全て Already」を 3 層分類に修正:

| # | 手法 | 判定 | 実装 vs 動作 |
|---|------|------|------|
| 1 | eval loop パイプライン | Already（無効） | framework 完成（eval-generator/run_reviewer_eval/split_holdout）、**2026-05-03 /improve retire で停止** |
| 2 | 3 箇所 eval | Already（一部稼働） | 出荷前 regression=⏸️停止 / 実行時 guardrail=✅稼働 / 本番監視=⚠️記録のみ |
| 3 | benchmark 3 要素 | Already（稼働） | `reviewer-eval-tuples.json` + 6 次元×threshold (`benchmark-dimensions.md`) |
| 4 | gold standard | Already（部分） | `baseline-eval.json` 初期化あり、dynamic update 不明 |
| 5 | rubric LLM-as-judge | Already（簡易版稼働） | FM→judge routing + keyword scoring、5 次元 rubric は code-reviewer |
| 6 | metric library | Already | 6 次元 × good/warn/danger threshold |
| 7 | failure→testcase | Already（無効） | failure-clusterer + eval-generator 完成、hypothesis loop は /improve と共に停止 |
| 8 | Hermes 実装 | N/A | ベンダー固有（cron/approval buttons/Telegram） |

**3 層分類（Codex）**: Primitives Already（#3,5,6 稼働）/ Active loop Retired（#1,7 意図的無効化）
/ Signal-to-action Partial（#2,4 記録あり action 接続なし、observability-signals.md Gap 2/3 で明示済み）

## Phase 2.5: Refine

### Codex（gpt-5.5, xhigh, read-only）

- 「新規テクニックなし」は妥当だが「全て Already」は**過大**。無効化・読み手不在を Already に
  含めるのは self-preference bias というより**分類の粗さ**。
- retire 根本原因は human gate 欠如**だけではない**。記録上は「5 連続 false-positive + 認知負荷が
  価値を上回った」= **judge/proposal の precision 問題**。
- approval button は「誤変更 ship リスク」は下げるが「ノイズ候補を人間が読む負担」は下げない ──
  **false-positive 生成器の出口に人間を置くだけなら失敗を UX に移すだけ**。記事の処方箋は dotfiles の
  退役原因に**半分しか噛み合わない**。
- **推奨**: approval-gated 再接続はしない。**retire 維持**。採るなら read-only calibration のみ
  （failure-clusters Top-N を週次/手動サンプル、採用率・noise 率測定、precision 安定後に testcase 化検討）。

### Gemini

タイムアウト（exit 124、grounding 完了前）。過去前例（Gemini クォータ枯渇 → Codex 単独で判定十分）
に従い Codex + Opus 分析で確定。

## Decision: 採用 0 件

- **新規テクニック**: 0（全 primitives 実装済み、loop は意図的 retire、gap は文書化済み）
- **read-only calibration**: 棄却（weekly-review annotation [2026-05-28 codex-research-agent absorb]
  と部分重複、retire 済み loop への新機構追加は Pruning-First 違反）

## 反証データ（reusable judgment anchor）

> 記事の中心主張「failure→testcase の自動ループが品質の床を自動で上げる」「approval button を
> 足せば安全」は、dotfiles が `/improve` で**実装→ 5 連続 false-positive → 2026-05-03 retire** した
> 機構そのもの。**自動 self-improvement loop = false-positive slop 製造機**であり、approval button は
> root cause（candidate-generation の precision）を解決せず noise レビュー負担を UX に転嫁するだけ。
> 次回 eval-loop / Hermes 系記事の absorb では、この反証データを judgment anchor とし「自動ループ採用」
> 主張を precision audit 前提なしには採らない。

## メタ学習

- continue（skip override）が有効だった点: 私の Pass 2「全て Already（実装済み）」という premature
  judgment を、Pass 1 Explore が「framework 構築済みだが大半 DISABLED」と是正し、Codex が
  「3 層分類 + retire 原因は precision」とさらに精緻化した。delta=0 でも**実装状態軸の検査**には価値があった。
- ただし最終採用は 0 で、Saturation Gate の skip 推奨自体は正しかった（記事から actionable な novel
  instruction はゼロ）。
