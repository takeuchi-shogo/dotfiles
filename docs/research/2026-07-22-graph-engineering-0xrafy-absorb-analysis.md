---
title: "Graph Engineering with Claude: 11-Step Roadmap From Loops to Graph Architect — absorb analysis"
date: 2026-07-22
source:
  title: "Graph Engineering with Claude: the 11-Step Roadmap From Loops to Graph Architect"
  author: 0xRafy (X)
  url: https://x.com/0xRafy/status/2079542513317118268
  type: x-post
status: light-phase2-only
family: multi-agent-orchestration (主) / loop-engineering (副) — cross-family
saturation: "SATURATED-borderline (delta=1, ambiguous #10 のみ) — user light-phase2 選択"
adopted: 0
validation-only: 0
---

# Graph Engineering with Claude (@0xRafy) — absorb 分析 (light-phase2, 採用 0)

## 結論

「loop engineering の次は graph engineering」と自己位置づけする入門チュートリアル。11 手法中 10 が named prior で rehash (delta=1)、唯一の半 novel #10 (Fallback Paths) も light-phase2 検証で **全構成要素が Already + 宣言的 DAG 版は退役判断済み** と確定。**採用 0 件**。

多エージェント graph の基盤 (Workflow tool / LangGraph 型フレームワーク) は `2026-05-31-32-hacks` 以来 deliberate non-adopt、宣言的ノード別 `on_failure` は blueprint-pattern (実行エンジン /autonomous、2026-06-21 退役・invocation 0) で試行済み。記事は退役済み領域の再パッケージ。

## Source Summary

- **主張**: 単一ループは複雑タスクで context を溢れさせる。Node/Edge/Router/State の 4 プリミティブで専門エージェントを graph に組み、routing・並列化・検証を組織化せよ
- **手法**: 11 ステップ — 単一ループの問題認識 / 4 プリミティブ / 4 時代区分 (prompt→context→loop→graph) / Sequential Chain / Router (Haiku 分類) / Parallel Fan-out / Loop with Gate (Builder≠Reviewer) / Human-in-the-loop / State + Model Tiering / Fallback Paths / 60 行実装例
- **根拠**: context overflow の実例、並列化の wall-clock 短縮、Haiku few-shot 分類 > Sonnet zero-shot。定量ベンチなし
- **前提条件**: Claude API 直叩き + 自前 graph 実装 (フレームワーク不要を標榜)

## Phase 1.5: per-method 照合台帳 (全 11 手法、delta=1)

| # | current 手法 | verdict | matched_prior (ファイル名 + 引用 + 同等性) |
|---|---|---|---|
| 1 | 単一ループの問題認識 (context 混在→分割・専門化) | rehash | `2026-06-03-dynamic-workflows`「単一コンテキストの failure mode (agentic laziness / self-preferential bias / goal drift) を独立コンテキストの subagent オーケストレーションで構造的に回避」— 問題設定・解決策とも同一 |
| 2 | Node/Edge/Router/State 4 プリミティブ | rehash | `2026-06-03-dynamic-workflows`「JS で agent()/parallel()/pipeline()/phase() を呼び subagent を協調する harness を動的生成」— agent graph 構築プリミティブとして同一機能。基盤 (Workflow tool) は 32-hacks で deliberate non-adopt 記録済 |
| 3 | 4 時代区分 (prompt→context→loop→graph) | rehash | `2026-06-17-loops-with-claude`「Addy Osmani の loop engineering エッセイ紹介」— era 進行フレーミングは Osmani 一次ソース absorb 済 (`comprehension-debt-policy.md` に出典明記)。「graph 段」の追加は self-positioning で手法でない |
| 4 | Sequential Chain + 終端検証ノード | rehash | `2026-06-03-dynamic-workflows` #2「loop-until-done \| Already \| implement-loop/review-loop/completion-gate.py」+ `2026-04-11-multi-agent-coordination-patterns` #1 Generator-Verifier「completion-gate (PASS/NEEDS_FIX/BLOCK 明示基準)」— 直列実行+終端ゲートと同一 |
| 5 | Router (Haiku 分類→専門 agent 分岐) | rehash | `2026-06-03-dynamic-workflows` #3「classify-and-act / model routing \| Already \| agent-router.py + model-routing.md」— 安価モデル分類→専門エージェント分岐が同一 |
| 6 | Parallel Fan-out + Collector 合成 | rehash | `2026-06-03-dynamic-workflows` #1「fan-out-and-synthesize \| Already \| research/dispatch skill」— 並列実行+合成ノードが同一 |
| 7 | Loop with Gate (Builder≠Reviewer、自己検証禁止) | rehash | `2026-04-11-multi-agent-coordination-patterns` #1「Generator-Verifier: 明示的な評価基準に基づくフィードバックループ」+ `2026-07-08-agentic-os` 原則 2「Nothing grades its own homework」+ `2026-07-08-loop-engineering-es` #3「実行者≠検証者 — Codex Review Gate で model-family diversity 達成済」 |
| 8 | Human-in-the-loop (高リスク承認ゲート) | rehash | `2026-07-08-loop-engineering-es` #6「閉→開ループ \| governance-levels.md 4段階 + 定量昇格条件 (承認率>80%)」— 人間承認→自律の段階制の下位ケース。confirm-first は CLAUDE.md + careful skill で既存 |
| 9 | State 管理 + Model Tiering (Haiku=分類/Sonnet=実装/Opus=QA) | rehash | `2026-07-08-agentic-os` #1「DISPATCH テーブル \| Already \| model-routing.md Tier 0-3」+ 採用 C「effort 規律」。State 側は `2026-04-11-multi-agent-coordination-patterns` #5「Shared State — 制約明示を採用済」— Model Tiering は dotfiles CLAUDE.md の中核運用そのもの |
| 10 | Fallback Paths (ノード別エラー経路) | **ambiguous → 検証 (下記)** | 近接 prior は `2026-04-11-multi-agent-coordination-patterns` #7「Feedback Loop Management (termination 条件必須)」+ `2026-06-14-opik` #3「Exit before loop (done/max-iter/budget)」— 「ノード別 fallback edge の網羅設計」を 1:1 名指しできず半 novel に倒した |
| 11 | Full Example (60 行サポートチケットグラフ) | rehash | `2026-06-03-dynamic-workflows`「classify-and-act」実装例と同型 (分類→specialist→reviewer→retry→human)。#5+#7+#8 の合成で独立手法でない |

## Phase 2 (light): #10 Fallback Paths のみ検証

Pass 1 (Sonnet Explore) + Pass 2 (Opus 判定):

| 記事の構成要素 | 判定 | 既存 |
|---|---|---|
| (a) timeout → 部分結果 + flag 継続 | Already | `references/graduated-completion.md` (Full/Partial/Blocked + handback report + [WIP] PR) + `subagent-delegation-guide.md` L1013 (タイムアウト→結果なし統合、親が補完) |
| (b) Reviewer crash → 人間レビューへ経路変更 | Already | `scripts/policy/completion-gate.py` MAX_RETRIES=2 → `_generate_handback_report()` + `review-loop-patterns.md` の人間介入ポイント |
| (c) 全体失敗 → state を disk 保存 + alert | Already | `scripts/runtime/checkpoint_manager.py` (自動 checkpoint 3 経路書き込み) + `scripts/runtime/patrol-agent.sh` (3 段カスケード通知: cmux-notify→osascript→log) |
| (d) graceful error handling (エラー無視禁止) | Already | `references/failure-taxonomy.md` Graceful Degradation (hook 4 層フォールバックチェーン) + `references/hook-failure-policy.md` (30 caller の fail-open/fail-closed 宣言カタログ) |
| ノード別 fallback edge の宣言的定義 | **N/A (退役判断維持)** | `references/blueprint-pattern.md` + `references/blueprints/*.yaml` の `on_failure: retry\|skip\|abort\|handback` が同一概念を仕様化済み。実行エンジン /autonomous は invocation 0 で 2026-06-21 退役 (decommission-log)。graph 基盤自体も deliberate non-adopt (32-hacks) |

Gap 0 件 → フル workflow への自動昇格なし。Phase 2.5 は light flag により省略。

## Triage / Adopted

- 採用候補: **0 件** (Gap なし、Already 強化可能なし)
- Validation-only: **なし** — blueprint「仕様のみ・エンジン退役」は decommission-log に記録済みで新規 drift ではない。/goal pilot 未消化 (06-12 採用から ~40 日) は `2026-07-08-loop-engineering-es` で記録済みの既知 pending (本 absorb で再露出したのみ)

## 教訓 (family-level)

- **loop-engineering 系譜の「次の era」宣言 (graph engineering) も中身は multi-agent-orchestration の既出パターン集**。era リブランドは saturation gate の family 照合を両 family で行えば数分で剥がせる
- 半 novel と判定した唯一の手法 (ノード別 fallback) も「dotfiles が過去に仕様化→退役した機構」に着地。ambiguous 行の light-phase2 検証は退役履歴 (decommission-log) との突き合わせが決定打になる
