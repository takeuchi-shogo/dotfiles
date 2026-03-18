# Workflow Decision Guide

## EPD vs RPI vs Spike

| Situation | Recommended | Reason |
|-----------|------------|--------|
| 仕様が不確実、探索が必要 | `/epd` | Spec→Spike→Validate の探索サイクルが必要 |
| 仕様が明確、実装のみ | `/rpi` | Research→Plan→Implement で直行 |
| 素早い技術検証 | `/spike` | worktree で隔離、テスト/lint 不要 |
| バグ修正 | 直接修正 or `/rpi` | 既知の問題なら探索不要 |
| 1行変更 | 直接修正 | ワークフロー不要 |

## EPD Phase Overview

| Phase | 名前 | 目的 | 成果物 |
|-------|------|------|--------|
| 1 | Spec | 仕様定義 | `docs/specs/{feature}.prompt.md` |
| 2 | Spike | 技術検証 | プロトタイプ + spike-report |
| 3 | Refine | 仕様修正 | 更新された spec |
| 4 | Decide | Go/No-Go | 判断記録 |
| 5 | Build | 実装 | プロダクションコード |
| 6 | Review | 品質確認 | レビューレポート |
| 7 | Ship | デリバリー | PR or merge |
