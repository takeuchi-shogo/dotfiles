---
title: オートハーネス
topics: [harness]
sources: [2026-03-31-autoharness-code-harness-synthesis-analysis.md, 2026-04-02-autoharness-governance-framework-analysis.md, 2026-03-31-meta-harness-analysis.md, 2026-04-29-symphony-clawsweeper-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 4
confidence: established
---

# オートハーネス

## 概要

LLM エージェントの失敗は「知識の欠如」ではなく「実行の不正確さ」に起因するという観察から生まれた、ハーネス（エージェントを包むコード）の自動合成・最適化フレームワーク。小モデル+ハーネスが大モデル単体を上回れることを実証し、Scaffolding > Model という設計哲学の定量的根拠を提供する。

## 主要な知見

- **Harness-as-Policy の定量優位**: Harness-as-Policy(0.870) > GPT-5.2-High(0.844)、推論コストはほぼ $0（GPT-5.2 は ~$640）
- **Action Filter パターン**: `propose_action()` で出力生成 → 検証関数で合法性チェック → 失敗時は rejection sampling で再生成
- **Critic-Refiner 分離ループ**: 10 並列環境で Rollout → Critic がエラー集約（最大5件）→ Refiner（LLM）がコード改善。平均 14.5 反復で収束
- **生トレースへの直接アクセスが決定的**: 要約を挟むと性能が低下する。スコアのみ(50.0)、スコア+要約(34.9)、フル生トレース(50.0の中央値精度) — 情報圧縮は逆効果
- **YAML Constitution**: 宣言的ガバナンス設定でポリシーとコードを分離し、ハーネスの保守性を高める
- **Progressive Trust**: セッション内の承認パターンを記録し 1h decay で信頼スコアを管理
- **5層コンテキスト管理**: Budget → Truncation → Microcompact → AutoCompact + circuit breaker → File Restoration の段階的縮退
- **Meta-Harness の Pareto frontier 探索**: 精度・コスト等の多目的 tradeoff curve 上の複数候補を維持し、コード空間で探索する
- **既存 TODO 消化を新規 Gap 探索より優先する原則**: 自律メンテナンスハーネスの改善は、新たな仕組みの追加より先に、既にドキュメント化済みだが未実装の stop condition（no-op diff 検出・validation failure summary・token budget 超過・session_lost 詳細化など）を消化すべきという判断が Symphony/ClawSweeper 分析で確認された。自己修復ハーネスは「積み残しの完了」を「新規スコープ」より優先することで blast radius を抑える `[EXTRACTED, conf=80]`
- **Snapshot hash 付き構造化 Evidence Record**: 自律 TODO 処理エージェントの実行記録を、生ログの保存だけでなく `decision` / `evidence` / `snapshot_hash` を持つ構造化レコードとして残し、snapshot からの drift を検出した場合は apply をスキップする設計が有効。drift 検出のスコープを単一実行内に限定し、cron 階層化のような常時稼働の重量級実装は個人規模では YAGNI と判断された `[EXTRACTED, conf=75]`
- **Keep-open bias（Conservative Close Threshold）**: 自律的な Issue/TODO 処理は「閉じすぎない」バイアスを明示的に持たせるべきという知見。ClawSweeper は day-1 で 4000 issue を close する一方、proposal レーンの close rate は 7 日間 0% を維持しており、提案（review）と適用（apply）のレーンを分離し人間レビューを経るまでは close しない設計が定着率を支えている `[EXTRACTED, conf=75]`

## 実践的な適用

dotfiles の hook 体系は AutoHarness の思想を部分的に実装している。`golden-check`・`completion-gate`・`protect-linter-config` が Action Filter パターンに対応し、`session-learner.py` + `findings-to-autoevolve.py` が Critic-Refiner の近似を担う。CLAUDE.md の `Scaffolding > Model` 原則には Harness-as-Policy(0.870) > GPT-5.2-High(0.844) の定量根拠が追記済み。Meta-Harness の知見から、セッション実行の生トレース保存が AutoEvolve の精度向上に直結することが示されている。`tools/codex-janitor` は自律的なメンテナンスハーネスの実例であり、Symphony/ClawSweeper 分析を受けて既存 TODO（no-op diff・validation failure summary・token budget stop condition）の消化、snapshot hash 付き evidence record、keep-open bias の明記が優先課題として整理されている。

## 関連概念

- [harness-engineering](harness-engineering.md) — ハーネス設計の基本原則と4層 hook アーキテクチャ
- [quality-gates](quality-gates.md) — Codex Review Gate など品質を担保するゲート機構
- [self-improving-agents](self-improving-agents.md) — Critic-Refiner ループによるエージェントの自律改善
- [long-running-agents](long-running-agents.md) — 自律 TODO 処理・per-task isolation など長時間自律実行の設計パターン

## ソース

- [AutoHarness コードハーネス合成分析](../../research/2026-03-31-autoharness-code-harness-synthesis-analysis.md) — Harness-as-Policy の定量結果と Critic-Refiner ループ
- [AutoHarness ガバナンスフレームワーク分析](../../research/2026-04-02-autoharness-governance-framework-analysis.md) — YAML Constitution と 3段階パイプライン設計
- [Meta-Harness 分析](../../research/2026-03-31-meta-harness-analysis.md) — FS ベース生トレースアクセスと Pareto frontier 探索
- [Symphony/ClawSweeper Absorb 分析](../../research/2026-04-29-symphony-clawsweeper-absorb-analysis.md) — OpenAI の orchestration layer 分析、Janitor既存TODO消化・snapshot hash evidence record・keep-open biasの3件採用
