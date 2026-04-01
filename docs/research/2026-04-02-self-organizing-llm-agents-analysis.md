---
source: https://arxiv.org/abs/2603.28990
date: 2026-04-02
status: integrated
---

## Source Summary

**タイトル**: "Drop the Hierarchy and Roles: How Self-Organizing LLM Agents Outperform Designed Structures"
**著者**: Victoria Dochkina (モスクワ物理工科大学)
**規模**: 25,000+ タスク、8 LLM、4〜256 エージェント、8 協調プロトコル、4 複雑度レベル

### 主張

マルチエージェント LLM 協調において、「最小構造 + 最大役割自律」(Sequential プロトコル) が最適。
プロトコル選択が品質差異の 44% を説明し、モデル選択は ~14%。

### 手法

- 4 プロトコル (Coordinator/Sequential/Broadcast/Shared) の体系的比較
- 4〜256 エージェントへのスケーリング検証
- 能力閾値の特定（強モデル: 自律 +3.5%、弱モデル: 自律 -9.6%）
- 出現特性の観察（動的役割発明、自発的自己棄却、自己組織化階層）

### 根拠

- Sequential vs Shared: +44% (Cohen's d=1.86, p<0.0001)
- Sequential vs Coordinator: +14% (p<0.001)
- 4→256 エージェントで品質低下なし (p=0.61)
- DeepSeek が Claude の 95% 品質を 24 倍低コストで達成

### 前提条件

- 強力なモデル (Claude/DeepSeek クラス) で効果大
- 弱いモデルでは自律性が逆効果
- 合成タスクでの検証（実ビジネスワークフローは未検証）

---

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Sequential プロトコル採用 | Gap | Implicit Coordinator パターン |
| 2 | 能力閾値に基づく自律度調整 | Partial | Codex/Gemini 委譲はあるが能力別調整なし |
| 3 | 自発的自己棄却メカニズム | Gap | エージェントは常にフルスコープ実行 |
| 4 | エージェント障害耐性 | Gap | マルチエージェント障害回復なし |
| 5 | 動的役割発明 (RSI→0) | N/A | 固定専門エージェントが適切 |
| 6 | 三環構憲フレームワーク | N/A | hooks + policies + CLAUDE.md で同等 |

### Already 項目の強化分析

| # | 既存の仕組み | 強化案 |
|---|---|---|
| A1 | Scaffolding > Model (CLAUDE.md) | 44% vs 14% 定量値追記 |
| A3 | Implicit Coordinator (orchestration-map) | Sequential 検討セクション追記 |

---

## Integration Decisions

全 Gap/Partial (1-4) + 両 Already 強化 (A1, A3) を統合。

## Plan (実行済み)

| # | タスク | 対象ファイル |
|---|--------|-------------|
| T1 | Scaffolding > Model に 44% vs 14% 追記 | CLAUDE.md |
| T2 | Sequential パターン検討セクション | agent-orchestration-map.md |
| T3 | Sequential Protocol ガイドライン | subagent-delegation-guide.md |
| T4 | 能力閾値に基づく自律度調整 | subagent-delegation-guide.md |
| T5 | 自発的自己棄却メカニズム | subagent-delegation-guide.md |
| T6 | エージェント障害耐性パターン | subagent-delegation-guide.md |
