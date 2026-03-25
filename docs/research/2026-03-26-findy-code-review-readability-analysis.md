---
source: https://speakerdeck.com/smorisaki/20260324-findykodorebiyunixiao-kuchu-fang-jian
date: 2026-03-26
status: integrated
---

## Source Summary

森崎修司（名古屋大学）「コードレビューに効く読みやすさの処方箋」Findy オンライン講演, 2026-03-23。

**主張**: コードレビュー指摘の42.2%は読みやすさに関するもので、Linterでカバーできるのは30%未満。読みやすさを3層（Legibility/Readability/Understandability）で体系化し、学術的に検証された検出指標を活用すべき。

**手法**:
1. 3層読みやすさモデル（Legibility/Readability/Understandability）
2. Linguistic Anti-patterns 6分類（振る舞い A-C + 属性 D-F）
3. Atoms of Confusion（誤読の最小単位15パターン）
4. Model-based 読解戦略（メンタルモデル構築→判断）
5. AI readability の限界（全体抽象化の失敗、論理表現の誤認識）

**根拠**: GitHub 385 PR調査（Oliveira et al., 2024）、73名プログラマ実験（Gopstein et al., 2018）、MISRA-C 8種類コード検証（Sugiyama et al., 2025）

**前提条件**: チーム開発でコードレビューを実施している環境。言語非依存だがC系言語の知見が多い。

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 3層読みやすさモデル | Partial | readability-principles.md は構造的可読性に集中、3層区別なし |
| 2 | Linguistic Anti-patterns 6分類 | Partial | 命名の what 原則 + 例3で部分カバー、体系的A-F未整備 |
| 3 | Atoms of Confusion | Gap | 相当する概念なし |
| 4 | Model-based 読解戦略 | Partial | ファイル探索原則のみ、コード読解戦略は未明文化 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|--------------|--------|
| A | review-dimensions.md maintainability (0.20) | PR の 42.2% が読みやすさ | 強化不要（重み変更の根拠不足） |
| B | code-reviewer.md 命名チェック | 体系的検出ルールなし | 強化: cross-cutting.md に CC-8 追加 |
| C | comment-analyzer.md コメント整合性 | 属性名vs型の矛盾が対象外 | 強化: D-F チェック追加 |
| D | lint-category-map.md | Linter 30%未満を裏付け | 強化不要 |
| E | cross-model-insights.md | AI 固有の弱点パターン未記載 | 強化: 3パターン追加 |

## Integration Decisions

全 Gap/Partial (1-4) + 全強化 (B, C, E) を統合。

## Integration Summary

| タスク | 対象ファイル | 変更内容 |
|--------|-------------|----------|
| #1 | readability-principles.md | 3層モデルのフレーミング追加、Atoms of Confusion (8), Model-based 読解 (9) セクション追加 |
| #2 | review-checklists/cross-cutting.md | CC-8 Linguistic Anti-patterns (A-F 6分類テーブル) 追加 |
| #3 | agents/comment-analyzer.md | 2.7 属性レベル矛盾チェック (D-F) 追加 |
| #4 | references/cross-model-insights.md | Shared Blind Spots に AI readability 弱点3パターン追加 |

## References

- [1] Oliveira et al. (2024) "Understanding code understandability improvements in code reviews" IEEE TSE
- [2] Oliveira et al. (2022) "A systematic literature review on formatting elements" SSRN
- [3] Arnaoudova et al. (2016) "Linguistic antipatterns" Empirical Software Engineering
- [4] Gopstein et al. (2018) "Atoms of confusion in the wild" MSR
- [5] Sugiyama et al. (2025) "Model-based Decision-making and Comprehension" IEEE TSE
- [6] Sarsa et al. (2022) "Automatic generation with large language models" ICER
