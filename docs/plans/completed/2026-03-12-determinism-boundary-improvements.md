---
status: active
last_reviewed: 2026-04-23
---

# Determinism Boundary 改善プラン

**日付**: 2026-03-12
**契機**: Cornelius "The Determinism Boundary" 記事の分析結果

## 改善項目

- [x] 1. golden-check に GP-002（バウンダリバリデーション）を追加 [S]
- [x] 2. completion-gate に Review Gate を追加 [M]
- [x] 3. agent-harness-contract.md に hook 閾値サマリーを追記 [S]
- [x] 4. C-007 の分類を Hybrid に修正（constraints-library.md） [S]
- [x] 5. Search-First Gate を追加（PreToolUse Edit|Write） [M]
- [x] 6. doc-garden-check 降格の教訓を MEMORY.md に記録 [S]

## 方針

- 各改善は最小差分で実装
- 既存の hook パターン（hook_utils.py）に従う
- テストが存在するスクリプトは対応するテストも更新
