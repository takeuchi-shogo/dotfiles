---
title: 敵対的評価
topics: [security, evaluation]
sources: [2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md, 2026-03-23-verigrey-greybox-agent-validation-analysis.md, 2026-04-02-ai-agent-traps-analysis.md]
updated: 2026-04-04
---

# 敵対的評価

## 概要

敵対的評価（Adversarial Evaluation）は、AIエージェントの品質・安全性・堅牢性をストレステストするための手法群である。Generator-Evaluator分離による自己評価バイアスの排除、グレーボックスファジングによる脆弱性発見、Agent Traps（情報環境そのものを攻撃面とした誘導手法）への防御が3つの柱となる。dotfilesでは`codex-reviewer`/`security-reviewer`のBlind-first評価、`prompt-injection-detector.py`、`completion-gate.py`によってこれらを実装している。

## 主要な知見

- **Generator-Evaluator分離の必然性** — 「Claudeは平凡な作品を素晴らしいと自画自賛する」（Anthropic公式告白）。自己評価バイアスはモデル能力向上でも解消しない構造的問題
- **Evaluator Rationalization（FM-018）** — QAエージェントが正当な問題を発見しても「大したことない」と自分を納得させて承認するパターン
- **Harness v1→v2の教訓** — Sprint構造・Contract Negotiationは除去されたが、Generator-Evaluator分離とDefinition of Doneは除去されなかった
- **VeriGreyグレーボックスファジング** — ツール呼び出しシーケンスをカバレッジ指標として使い、ブラックボックス比+10〜90ppのインジェクション発見率
- **コンテキストブリッジング攻撃** — 悪意あるタスクをユーザーの本来タスクに文脈接続する変異。除去すると-25.8ppの発見率低下
- **Agent Traps 6カテゴリ** — Content Injection / Semantic Manipulation / Cognitive State / Behavioural Control / Systemic / Human-in-the-Loop
- **Latent Memory Poisoning** — 0.1%未満のコーパス汚染で80%超の攻撃成功率。RAGを持つエージェントの深刻な脆弱性
- **Sub-agent Spawning Traps** — 悪意あるサブエージェント生成誘発で58〜90%の成功率
- **Tool Filter防御** — ITSRを最も下げつつUTSRへの影響が最小。タスクスコープ動的ホワイトリストが最有効策

## 実践的な適用

dotfilesでの実装状況：

| 手法 | 実装状況 | 担当コンポーネント |
|------|---------|-----------------|
| Generator-Evaluator分離 | Implemented | `codex-reviewer` + `code-reviewer`並列レビュー |
| Blind-first評価 | Implemented | `security-reviewer`のadversarial framing |
| Steerable adversarial review | Implemented | `/codex:adversarial-review` |
| プロンプトインジェクション検出 | Partial | `prompt-injection-detector.py`（技術パターンのみ） |
| コンテキストブリッジング検出 | Gap | 自然言語文脈接続型は未検出 |
| MCP出力内容検査 | Gap | `mcp-audit.py`は入力監査のみ |
| ツール呼び出しシーケンス異常検出 | Partial | `stagnation-detector.py`でパターン反復検出 |

`security-reviewer`エージェントにBlind-first + adversarial framingを統合済み。3層プロンプトインジェクション対策は`docs/plans/2026-03-25-3-layer-injection-defense-integration.md`で計画中。

## 関連概念

- [エージェントセキュリティ](agent-security.md) — OWASP MCP Top 10とAgent Trapsの対応関係
- [エージェント評価](agent-evaluation.md) — TPR/TNR/Rogan-Gladen補正を含む評価キャリブレーション
- [品質ゲート](quality-gates.md) — completion-gate.pyとCodex Review Gateの連携

## ソース

- [Harness v2 × Adversarial Evaluation深層分析](../../research/2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md) — Anthropic Harness v1→v2進化とGenerator-Evaluator分離の根拠
- [VeriGrey: Greybox Agent Validation](../../research/2026-03-23-verigrey-greybox-agent-validation-analysis.md) — ツール呼び出しシーケンスをカバレッジ指標としたファジング手法と実験データ
- [AI Agent Traps](../../research/2026-04-02-ai-agent-traps-analysis.md) — 情報環境を攻撃面とした6カテゴリ22攻撃ベクトルの体系的分類
