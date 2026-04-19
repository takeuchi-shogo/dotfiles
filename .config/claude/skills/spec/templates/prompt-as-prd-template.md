# {Product/Feature Name} — Prompt-as-PRD

## Context
<!-- なぜこの機能が必要か。背景と動機 -->

## Problem Statement
<!-- 解決する問題を1-3文で -->

## Proposed Solution
<!-- 解決アプローチの概要 -->

## Acceptance Criteria
<!-- 検証可能な完了条件。各項目は Given/When/Then または箇条書き -->
- [ ] AC-1:
- [ ] AC-2:
- [ ] AC-3:

## Scenarios
<!-- mizchi/empirical-prompt-tuning: 2-3 シナリオ (中央値 + エッジ) で baseline を構成 -->
<!-- median は必須。edge_cases は 1 件以上推奨。holdout_scenarios は最適化ループから隔離 -->

### median
<!-- 通常の期待されるユースケース。最低 1 つ必須 -->
- Scenario 1:
  - Given:
  - When:
  - Then:

### edge_cases
<!-- 境界値・異常系・想定外入力。improve ループの主な学習対象 -->
- Edge 1:
  - Given:
  - When:
  - Then:

### holdout_scenarios
<!-- 改善ループに混入させない検証専用シナリオ (Rule 47 Holdout Contamination 対策) -->
<!-- convergence 判定時のみ使用。spec 更新時に holdout_scenarios は変更しない -->
- Holdout 1:
  - Given:
  - When:
  - Then:

## Exit Criteria (撤退条件)
<!-- いつ止めるか。時間上限、失敗回数、メトリクス閾値など -->
- 撤退条件:
- 許容リスク:

## Out of Scope
<!-- 明示的に含めないもの -->

## Technical Notes
<!-- 実装の制約、依存関係、アーキテクチャ考慮事項 -->

## Open Questions
<!-- 未決定事項。実装前に解決が必要 -->
