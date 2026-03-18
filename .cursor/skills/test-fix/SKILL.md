---
name: test-fix
description: テストを実行し、失敗を分析して修正する。修正→再実行→全パスまでループする（最大3イテレーション）。
---

# Test Fix Loop Skill

## When to Use

- テストが失敗している時
- CI が red の時
- リファクタリング後にテストを通したい時

## Workflow

1. テストフレームワークを自動検出:
   - `package.json` → jest / vitest / mocha
   - `pyproject.toml` / `pytest.ini` → pytest
   - `go.mod` → go test
   - `Cargo.toml` → cargo test
2. 全テスト実行、失敗を収集
3. 各失敗を分類:
   - **Type Error**: 型の不一致
   - **Logic Error**: 期待値と実値の不一致
   - **Runtime Error**: 例外・パニック
   - **Flaky**: 非決定的な失敗
4. 根本原因を分析し、修正を実装
5. 再実行して確認
6. 最大3イテレーション。超えたらユーザーに報告:
   - 修正できなかった失敗の一覧
   - 推定される原因
   - 推奨される次のステップ

## Rules

- テスト自体を変更して通すのは最終手段
- 実装コードを修正してテストを通す
- Flaky テストは原因を報告し、修正を提案
