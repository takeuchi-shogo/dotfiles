---
source: https://zenn.dev/chiman/articles/b233cc808d6af3
date: 2026-03-18
status: integrated
---

# Claude Code / Codex で Kaggle 金メダルを取った話 — 分析レポート

## Source Summary

**著者**: kinosuke（Kaggle Master）
**成果**: Kaggle コンペ 5位/3,803チーム（Top 0.1%）、金メダル獲得

### 主張

- 「実装と分析は AI に、アイディアと判断は人間に」
- 実装コストの劇的削減により試行回数が増加（5-Fold CV 合計 1,515 回）
- スコア改善のアイディアはほぼ全て人間由来。AI の提案の打率は低い
- 実装の差がなくなった分、差がつくのはアイディアとデータ理解の深さ

### 手法

- **EXP + child-exp 階層実験管理**: パイプライン変更→新EXP、パラメータ変更→child-exp
- **CLAUDE.md 430行 / AGENTS.md 270行**: 正しい/間違った実装の両方を明記、繰り返すバグの注意書き、ガードレールリスト
- **EXP_SUMMARY.md**: 実験履歴の一元管理（AI の記憶として機能）
- **失敗データの制限**: 失敗実験を過度に読ませると AI が消極的になるため、ガードレールとしてのみ使用

### 根拠

- AI は具体的指示への実装精度が高い。「siglip の image encoder を使って train pipeline を書いて」等
- 「精度を上げろ」等のアバウトな指示には教科書的施策のみ提案
- コンペ特注のドメイン工夫が苦手

### 前提条件

- データ量が少なく学習時間が短いコンペで有効
- タスクがシンプル（画像回帰）でパイプラインの構造が単純
- 定量評価が可能

## Gap Analysis

| # | 手法/知見 | 判定 | 現状 |
|---|----------|------|------|
| 1 | "実装はAI、判断は人間" | Already | CLAUDE.md の "Humans steer, agents execute" |
| 2 | 正しい/間違った実装の両方を記載 | Partial | 正しい例はあるが Bad Example 併記は未体系化 |
| 3 | 失敗経験をガードレールリストに圧縮 | Partial | continuous-learning はあるが禁止リスト形式は未整理 |
| 4 | 失敗データ過剰供給で AI が消極化 | Gap | memory-safety-policy に観点なし |
| 5 | EXP + child-exp 階層管理 | N/A | Kaggle/ML 固有 |
| 6 | EXP_SUMMARY.md | Already | memory + checkpoint + recall |
| 7 | モデル性格差の認識 | Gap | 委譲ルールに性格傾向の記載なし |
| 8 | 「分布を歪める系は全滅」パターン | N/A | ML ドメイン固有 |
| 9 | 限定的指示→直接的解決に収束 | Partial | brainstorming で発散促進はあるが未文書化 |

## Integration Decisions

以下の 3 項目を統合:

1. **[Gap→統合] 失敗メモリ萎縮対策**: `references/memory-safety-policy.md` に「Failure Memory Accumulation & AI Conservatism」セクション追加。萎縮メカニズム、失敗データのガードレール圧縮形式、注入上限、萎縮兆候の検出基準を記載
2. **[Gap→統合] モデル性格傾向**: `rules/codex-delegation.md` と `rules/gemini-delegation.md` に「性格傾向バイアス」セクション追加。Codex は曖昧指示に定番施策のみ、Gemini は過度に楽観的
3. **[Partial→memory] Bad Example 併記パターン**: feedback memory として記録。CLAUDE.md/rules に正しい例と間違った例を併記することで AI の精度が向上するパターン

## AI 性格傾向の詳細（記事からの観察）

### Claude

- 失敗を重ねると消極的に（「0.73 を超えるのは極めて困難」）
- 撤退を提案する（「撤退（現実的）」）
- 学習の場としての着地を試みる

### Gemini

- 分析結果に興奮（"宝の山を見つけた状態"）
- 全力で盛り上げる性格
- 実際には無駄な提案も多い

### 実践的教訓

- 課題を限定的に指示すると AI は「その課題の直接的解決」に収束する
- 「精度を上げろ」等の曖昧な指示には教科書的な施策のみ提案
- **具体的な仮説や方向性を含む指示**が最も効果的
