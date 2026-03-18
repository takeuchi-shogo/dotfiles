---
name: spec
description: ユーザーのアイデアをインタビュー形式で深掘りし、構造化された仕様書（目的、要件、受け入れ基準、制約）を生成する。実装前に使用。
---

# Spec Generation Skill

## When to Use

- 新機能の実装前
- 要件が曖昧な時
- 複数の実装方法がある時

## Workflow

1. ユーザーのアイデアを確認
2. 1つずつ明確化の質問をする（多肢選択を優先）:
   - 目的: 何を達成したいか
   - ユーザー: 誰が使うか
   - 制約: 技術的・時間的制約
   - 成功基準: どうなれば完成か
3. 2-3 のアプローチを提案（トレードオフ付き、推奨を明示）
4. 仕様書を生成:
   ```
   # [Feature Name] Spec
   ## Goal
   ## Requirements
   ## Acceptance Criteria
   ## Constraints
   ## Out of Scope
   ```
5. プロジェクトの `docs/specs/` に保存
