---
title: オートハーネス
topics: [harness]
sources: [2026-03-31-autoharness-code-harness-synthesis-analysis.md, 2026-04-02-autoharness-governance-framework-analysis.md, 2026-03-31-meta-harness-analysis.md]
updated: 2026-04-04
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

## 実践的な適用

dotfiles の hook 体系は AutoHarness の思想を部分的に実装している。`golden-check`・`completion-gate`・`protect-linter-config` が Action Filter パターンに対応し、`session-learner.py` + `findings-to-autoevolve.py` が Critic-Refiner の近似を担う。CLAUDE.md の `Scaffolding > Model` 原則には Harness-as-Policy(0.870) > GPT-5.2-High(0.844) の定量根拠が追記済み。Meta-Harness の知見から、セッション実行の生トレース保存が AutoEvolve の精度向上に直結することが示されている。

## 関連概念

- [harness-engineering](harness-engineering.md) — ハーネス設計の基本原則と4層 hook アーキテクチャ
- [quality-gates](quality-gates.md) — Codex Review Gate など品質を担保するゲート機構
- [self-improving-agents](self-improving-agents.md) — Critic-Refiner ループによるエージェントの自律改善

## ソース

- [AutoHarness コードハーネス合成分析](../../research/2026-03-31-autoharness-code-harness-synthesis-analysis.md) — Harness-as-Policy の定量結果と Critic-Refiner ループ
- [AutoHarness ガバナンスフレームワーク分析](../../research/2026-04-02-autoharness-governance-framework-analysis.md) — YAML Constitution と 3段階パイプライン設計
- [Meta-Harness 分析](../../research/2026-03-31-meta-harness-analysis.md) — FS ベース生トレースアクセスと Pareto frontier 探索
