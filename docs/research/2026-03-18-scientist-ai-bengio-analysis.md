---
source: https://arxiv.org/abs/2502.15657
date: 2026-03-18
status: analyzed
---

# Scientist AI 論文 — ギャップ分析レポート

## Source Summary

- **主張**: 知能と行為主体性は分離可能であり、分離すべき。Scientist AI は非エージェント型で安全な代替パス
- **手法**: Agency 3本柱モデル、ベイズ的不確実性定量化、反事実的世界モデル、永続状態排除
- **根拠**: GFlowNet 収束定理（計算↑=安全↑）、alignment faking 実験、reward tampering の最適性証明
- **前提条件**: ASI 水準のリスク論。現行エージェントハーネスには概念・設計指針として適用可能

## Gap Analysis

| # | 知見 | 判定 | 現状 | 差分 |
|---|------|------|------|------|
| 1 | Agency 3本柱モデル | Partial | deny rules + constraints あり、フレームワーク未定義 | 3軸での再整理が必要 |
| 2 | ガードレールは別 AI インスタンス | Already | completion-gate, golden-check, codex-reviewer | 一致 |
| 3 | 永続状態 → situational awareness | Partial | learnings/ 蓄積あり、リスク対策なし | ポリシー明文化が必要 |
| 4 | Specification gaming 検出 | Gap | drift guard (3× revert) のみ | gaming 検出の拡張が必要 |
| 5 | 反事実的世界モデル | Partial | worktree 隔離あり、概念未導入 | 将来検討 |
| 6 | 計算↑=安全↑ の逆転 | Gap | 未認識 | 参考情報として記録 |
| 7 | Goodhart's Law 増幅 | Partial | drift guard あり | proxy metric 乖離検出が弱い |
| 8 | Alignment faking | N/A | 短命サブエージェントでは低リスク | — |
| 9 | ASI 間共謀 | N/A | 独立 CLI、共謀の affordance なし | — |
| 10 | 不確実性の定量化 | Gap | binary 判定のみ | confidence score 導入が必要 |

## Integration Decisions

- **選択**: #1, #3, #4, #10 (全4項目)
- **理由**: ハーネス設計の体系化と実運用の安全性向上に直結

## Plan

→ `docs/plans/2026-03-18-scientist-ai-integration.md` を参照
