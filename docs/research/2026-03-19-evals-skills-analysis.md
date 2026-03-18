---
source: https://github.com/hamelsmu/evals-skills
date: 2026-03-19
status: integrated
---

## Source Summary

Hamel Husain (50+社の AI 評価支援) が作った LLM 評価パイプライン用 Claude Code スキルプラグイン。

**主張**: LLM 評価は error analysis → evaluator design → judge validation の順で行うべき。汎用メトリクス (ROUGE, BERTScore) ではなく、トレースから帰納的に導出した失敗モードに基づく binary Pass/Fail 評価が有効。

**手法**:
1. スキル執筆原則 (meta-skill.md) — directives not wisdom, cut general knowledge, 500行上限, concrete examples, 1-line anti-patterns
2. Evaluator 校正 (validate-evaluator) — TPR/TNR, Rogan-Gladen 補正, Bootstrap CI, train/dev/test 分割
3. ボトムアップ帰納 (error-analysis) — カテゴリをブレストせず ~100 トレースの観察から導出
4. スキル設計パターン — 1スキル1責務, Prerequisites 明示, Anti-Patterns 末尾リスト

**根拠**: 50社以上の実践経験、Maven 講座、arXiv:2404.12272 (Who Validates the Validators?)

**前提条件**: LLM パイプラインのトレースデータが利用可能なこと

## Gap Analysis

| # | 知見 | 判定 | 現状 | ギャップ |
|---|------|------|------|---------|
| 1 | "Write directives, not wisdom" | Partial | skill-creator は "explain the why" 推奨 | wisdom 削除の具体的 Good/Bad 例なし |
| 2 | "Cut general knowledge" | Gap | 未明文化 | エージェント既知情報の省略ルールなし |
| 3 | "Scope to the build task" | Partial | scope creep Gotcha のみ | プロセス助言削除の明確指示なし |
| 4 | "Start with good defaults" | Gap | 未明文化 | シンプル→複雑の順序原則なし |
| 5 | "Be concrete" | Partial | description の Good/Bad のみ | スキル本文全体への適用原則未整備 |
| 6 | "Warnings → directives/anti-patterns" | Gap | 一部スキルのみ | 変換プロセス未定義 |
| 7 | No nested references | Gap | 500行上限は既存 | 参照深さ1階層制限なし |
| 8 | TPR/TNR 分離計測 | Partial | accept_rate のみ | TNR 未計算、混同行列なし |
| 9 | Rogan-Gladen 補正 | Gap | 未実装 | バイアス補正なし |
| 10 | Bootstrap CI | Gap | 未実装 | 信頼区間未定量化 |
| 11 | train/dev/test 分割 | Gap | 分離ルールなし | データリーケージ防止なし |
| 12 | ボトムアップ帰納プロセス | Partial | 暗黙的 | 明文化不足 |
| 13 | Anti-Patterns 末尾リスト標準化 | Partial | 一部スキルのみ | 全スキル標準化指示なし |

## Integration Decisions

全項目を統合:
- **A**: #1-7, #13 → skill-writing-principles.md + skill-creator 更新
- **B**: #8-11 → evaluator_metrics.py 強化 + evaluator-calibration-guide.md
- **C**: #12 → continuous-learning 更新 + error-analysis-methodology.md

## Plan

### A. スキル執筆原則の強化 (M)
1. `skill-creator/references/skill-writing-principles.md` 新規作成
2. `skill-creator/SKILL.md` に参照追加 + Anti-Patterns 標準化

### B. Evaluator 校正の強化 (M)
1. `evaluator_metrics.py` に TPR/TNR, 混同行列, Rogan-Gladen, Bootstrap CI 追加
2. `references/evaluator-calibration-guide.md` 新規作成
3. `improve-policy.md` メトリクス更新

### C. ボトムアップ帰納プロセスの明文化 (S)
1. `continuous-learning/SKILL.md` に帰納原則追加
2. `references/error-analysis-methodology.md` 新規作成
