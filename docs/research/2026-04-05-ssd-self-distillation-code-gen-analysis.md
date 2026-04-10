---
source: https://arxiv.org/abs/2604.01193
date: 2026-04-05
status: integrated
---

# Embarrassingly Simple Self-Distillation Improves Code Generation — 分析レポート

## Source Summary

**主張**: LLM は自分自身の出力だけでコード生成性能を大幅に改善できる。報酬モデル・検証器・教師モデル・RL は不要。

**手法**:
- 凍結モデルから高温度でサンプリング（検証なし）
- 生サンプルに対して標準クロスエントロピーで SFT
- サンプリングとデコーディングで独立した温度を使用
- Precision-exploration conflict を文脈依存トークン分布リシェイピングで解消

**根拠**: Qwen3-30B-Instruct で 42.4% → 55.3% pass@1（+12.9pt）。4B/8B/30B、Qwen/Llama で汎化。難問ほどゲインが大。

**前提条件**: コード生成タスク。実行可能な出力があるドメイン。ベースモデルがある程度の能力を持つこと。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | SFT による自己蒸留（重み更新） | N/A | Model 層は外部提供。trajectory-learning wiki で区分済み |
| 2 | 独立温度デコーディング | N/A | API ユーザーとして直接制御不要。プロンプトレベルで対処 |
| 3 | 検証なしサンプルからの学習 | Partial | trajectory learning は成功/失敗対比を前提。SSD は未検証でも有効と示す |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| A | verbalized-sampling-guide | 高温度の生サンプル群自体に学習価値がある | VS 不採用候補も session-trace に記録 |
| B | best-of-n-guide | 「全サンプルから学ぶ」> 「最良を選ぶ」 | 敗者パターンを learnings に取り込む |
| C | KISS / Build to Delete | シンプルな手法が複雑な手法を凌駕 | 強化不要 |
| D | precision-exploration トレードオフ | 文脈依存の探索度調整 | situation-strategy-map に難易度軸追加 |

## Integration Decisions

- **取り込み**: #3 (Partial), A, B, D
- **スキップ**: #1 (N/A), #2 (N/A), C (強化不要)

## Plan

1. trajectory-learning.md に未検証トレース学習の指針 + 難易度→探索度軸の追加
2. verbalized-sampling-guide.md に不採用候補の活用セクション追加
3. best-of-n-guide.md に敗者パターン活用ステップ追加

## 差分統合（2026-04-06, alphaxiv overview からの追加知見）

alphaxiv の構造化レポートで得られた詳細データを基に追加統合を実施。

### 追加取り込み

| # | 対象 | 変更内容 |
|---|------|---------|
| 4 | situation-strategy-map.md | 難易度→探索度軸エントリ追加（前回プラン残件） |
| 5 | situation-strategy-map.md | Lock/Fork ステップ分類エントリ追加（Precision-Exploration Conflict のハーネス翻訳） |
| 6 | CLAUDE.md core_principles | Scaffolding > Model に SSD 定量データ追加（+11.8pp vs +2.2pp） |
| A | trajectory-learning.md | "Bad Data, Good Results" に基づく品質フィルタ緩和ガイドライン追加 |
| B | best-of-n-guide.md | Pass@5 > Pass@1 の多様性保持定量根拠追加 |

## 再確認 (2026-04-10)

`/absorb` 再実行時に全 7 項目の実装を確認。差分候補として以下を検討したが、いずれも既存カバレッジ（Lock/Fork エントリ + subagent-delegation-guide）で間接的に充足しており、新規変更は見送り:

- Small model stability tradeoff: 小規模モデルは自己改善ループで不安定（±2pp 外）— 現行の Opus→Sonnet/Haiku 委譲ポリシーで実質カバー
- "Effective temperature" composable property: 生成側 × 評価側の探索度が乗算合成 — Lock/Fork task-step 分類で十分近似

ステータス: **integrated (no further action)**。
