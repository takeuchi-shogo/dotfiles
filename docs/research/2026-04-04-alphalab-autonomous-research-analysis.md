---
source: https://brendanhogan.github.io/alphalab-paper/AlphaLab.pdf
date: 2026-04-04
status: analyzed
---

## Source Summary

**AlphaLab: Autonomous Multi-Agent Research Across Optimization Domains with Frontier LLMs**
Morgan Stanley (Hogan et al.)

データセットと自然言語目標だけで自律的に研究を実行するマルチエージェントシステム。
3フェーズ（探索→敵対的評価構築→GPU実験）で動作し、Persistent Playbook で累積知識を蓄積。

### 主要手法

1. **3フェーズ自律ワークフロー**: Explorer→Builder/Critic/Tester→Strategist/Worker/Supervisor
2. **Adversarial Validation**: Builder/Critic/Tester を完全コンテキスト分離。Critic は Builder の推論を見ない
3. **Persistent Playbook**: 「やるな」含む累積知識。Strategist が消費し無駄な実験を防止
4. **Domain Adapters**: 11ファイルでドメイン固有化。新ドメインではLLMが自動生成
5. **Multi-Model Search**: GPT-5.2 と Opus 4.6 が質的に異なる解を発見（互いに補完）
6. **Supervisor**: エラーレートスパイク時にドメイン知識を自動パッチ
7. **Convergence-Aware**: 25-30実験でプラトー検出。予算判断に使用

### 根拠

- CUDA最適化: torch.compile比4.4×平均（最大91×）
- LLM事前学習: ベースライン比22%低いvalidation loss
- 交通予測: seasonal naïve比23-25%改善
- コスト: 1キャンペーン$150-200、Phase1に2-3時間

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Persistent Playbook（負の知識含む） | Partial | メモリ+AutoEvolve learnings はあるが「やるな」リストの構造化蓄積がない |
| 2 | Domain Adapter 自動生成 | Partial | agents/+references/+rules/ あるが新ドメインへの自動生成なし |
| 3 | Convergence-Aware Budgeting | Gap | /improve に改善幅の収束検出なし |
| 4 | 3フェーズ自律研究ワークフロー | N/A | ML研究向け。dotfilesハーネスのドメインと異なる |
| 5 | Supervisor（エラースパイク反応パッチ） | Partial | error-to-codex.py あるがレート監視・自動パッチなし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| A | Adversarial Gate (phase4-adversarial-gate.md) | Builder/Critic/Tester コンテキスト完全分離 | 強化不要 — Codex が別モデルで fresh context レビュー済み |
| B | Multi-Model Diversity (/debate, model-expertise-map.md) | 同一タスクを複数モデルが独立実装→異なる解空間を探索 | 強化可能 — 実装タスクでのマルチモデル競争メカニズム追加 |
| C | Context Isolation (/debate の clean context) | 協調的合理化の防止 | 強化不要 — /debate と Review Gate で既に実現 |

## Integration Decisions

全 Gap/Partial (#1,2,3,5) + Already 強化 (#B) を取り込む。

## Plan

→ `docs/plans/2026-04-04-alphalab-integration.md` に別途記載
