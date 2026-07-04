---
title: モデルルーティング
topics: [routing, agent, claude-code]
sources: [2026-04-30-three-model-stack-absorb-analysis.md, 2026-05-30-opus48-setup-guide-absorb-analysis.md, 2026-06-12-fable5-14steps-absorb-analysis.md, 2026-06-17-hermes-vps-24-7-os-absorb-analysis.md, 2026-06-20-weeklyaiops-model-council-absorb-analysis.md, 2026-06-25-acrouter-absorb-analysis.md]
updated: 2026-07-05
confidence: established
source_count: 6
last_validated: 2026-07-05
---

# モデルルーティング

## 概要

モデルルーティングは、タスクの性質に応じて Fable/Opus/Sonnet/Haiku などの階層を使い分け、コストと品質のバランスを取る設計である。dotfiles では `references/model-routing.md` を実体として、メイン(Fable)=指揮・判断、Opus=推論・設計分析、Sonnet=実装・並列実行、という役割分担が確立している。外部記事の多くは「コスト削減のための multi-model routing」を novel な発見として提示するが、繰り返しの absorb 検証によって、この設計は既に「静的な Tier 表 + hook ベースの soft routing」として実装済みであることが繰り返し確認されている。

## 主要な知見

- **End-to-End Completion > Per-Call Efficiency の原則が判断の核**: コスト削減 (~88%) を訴求する記事に対しても、「完走を重視する」原則が対立する主張を却下する根拠になっている `[EXTRACTED, conf=85]`
- **Model Safety Boundary という境界概念の欠落が繰り返し発見された**: Haiku を grader/prefilter として使う際、「非権威 cheap prefilter に留め、permission/safety/最終評価には使わない」という境界が model-routing.md に明記されていなかった。Fable 5 の安全境界 (server-side domain classifier → Opus 4.8 自動 fallback) と、ローカルの permission classifier outage は別物であることも合わせて文書化された `[EXTRACTED, conf=90]`
- **verification_status ラベル (verified/hypothesis/stale/retracted) の導入**: 自己改善エージェント記事から「数値主張と構造を分離して評価する」という原則を採用し、メモリスキーマに検証状態フィールドを追加した。欠落時は hypothesis 扱いとする `[EXTRACTED, conf=85]`
- **Fast Mode の用途指針**: 「Opus をより高速な出力に切り替えるモード（モデルダウングレードではない）」の使い分け表 — bulk refactor/codegen/docs/test-gen は speed>depth、debug/設計/security review は standard 維持、という指針を追加 `[EXTRACTED, conf=80]`
- **Council / Model Council パターンは Generator-Verifier の言い換えに過ぎない**: 「frontier model を judge に、cheap model を panel に」という主張は、`best-of-n-guide.md` の Cost-Arbitrage 節や Codex Review Gate (codex-reviewer + code-reviewer 並列 + Opus 統合) と shape が同型で、11 手法すべてが rehash と判定された `[EXTRACTED, conf=90]`
- **ACRouter (経験駆動のルーティング学習) は data regime 不一致で不採用**: 論文の中心洞察「reasoning failure ではなく information deficit がボトルネック」は移植価値があるが、既に CLAUDE.md の core principle「Scaffolding > Model」に codify 済みで新規取り込みは不要と判断された。実データ (`agent-invocations.jsonl` 1299 件) では model 記録が 303 件のみ・sonnet 90%・opus 6 件という偏りがあり、学習機構を支える分散が存在しないことが実証された `[EXTRACTED, conf=85]`
- **model-debt-register の Watch 行という低コストな中間状態**: 独立検証のない benchmark 訴求 (Kimi K2.6 等の open-weight model) に対して「採用しない」と「完全無視」の中間として、将来の再評価条件付き Watch 行を追加するパターンが確立した `[EXTRACTED, conf=75]`
- **Hermes VPS 24/7 OS のような「常時稼働 personal agent OS」系記事は token economics (per-task モデル振り分けで 10x コスト差) を訴求するが、dotfiles の model-routing.md Tier 表と完全に同型で新規性なし** `[EXTRACTED, conf=80]`
- **公式ベンチマーク数値は独立検証必須**: Kimi K2.6 の SWE-bench Verified 80.2% は Moonshot 公式発表の 78.5% と乖離があり、self-correction/多数決込みの数値である可能性が指摘された。300 並列 swarm の効果も独立検証では state conflict により成功率が急落するとされ、marketing 訴求と実測の乖離を意識する必要がある `[EXTRACTED, conf=70]`

## 実践的な適用

`.config/claude/references/model-routing.md` の Tier 表に Model Safety Boundary セクションが追加され、Haiku grader の境界とプラットフォーム側 fallback とローカル outage の区別が明文化されている。`references/memory-schema.md` には `verification_status` フィールドが追加され、`references/handoff-template.md` には検証済み事実/未検証仮説を分離するセクションが加わった。`references/resource-bounds.md` に Fast Mode の用途指針、`references/model-debt-register.md` に open-weight bulk delegation の Watch 行 (R-005) が追加されている。`docs/plans/2026-04-11-routing-observability-closed-loop.md` には ACRouter absorb を受けて「着手前提 = model 選択の分散回復」という着手条件が明記された。

## 関連概念

- [自己改善エージェント](self-improving-agents.md) — verification_status ラベルや STATE.md 構造など、モデル安全境界と併走する自己改善ループの設計
- [品質ゲート](quality-gates.md) — Codex Review Gate など、判断をゲート化する仕組みとモデル階層の接続点
- [プルーニングファースト](pruning-first.md) — 新規ルーティング機構 (ACRouter 等) を追加より既存強化で判断する姿勢
- [Sonnetイマジネーションバイアス](sonnet-imagination-bias.md) — モデル選定記事の absorb で繰り返し発生する過大評価バイアスとの関連

## ソース

- [Kimi K2.6+Opus 4.7+GPT-5.5 3モデルスタック absorb分析](../../research/2026-04-30-three-model-stack-absorb-analysis.md) — 3モデルコスト削減記事から model-debt-register への Watch 行 1 件のみ採用
- [The Claude Opus 4.8 Setup Guide (zodchixquant)](../../research/2026-05-30-opus48-setup-guide-absorb-analysis.md) — Opus 4.8 設定ガイドから Fast Mode 用途指針を採用、env var 名の誤情報 2 件を検出
- [Build self-improving agent system with Fable 5 in 14 steps (0xCodez)](../../research/2026-06-12-fable5-14steps-absorb-analysis.md) — verification_status ラベルと Model Safety Boundary を採用した中心レポート
- [Hermes VPS 24/7 OS Complete Guide (sora_biz)](../../research/2026-06-17-hermes-vps-24-7-os-absorb-analysis.md) — token economics 含む全10手法が rehash と判定され採用0
- [Model Council: How to get Fable-level intelligence back (weeklyaiops)](../../research/2026-06-20-weeklyaiops-model-council-absorb-analysis.md) — council/judge パターンが Generator-Verifier の言い換えと判定され採用0
- [Agent-as-a-Router: Agentic Model Routing for Coding Tasks (ACRouter, arXiv)](../../research/2026-06-25-acrouter-absorb-analysis.md) — 経験駆動ルーティング学習を data regime 不一致で却下、着手条件のみ codify
