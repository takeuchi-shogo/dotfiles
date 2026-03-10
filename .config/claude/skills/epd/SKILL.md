---
name: epd
description: "EPD統合ワークフロー。Spec → Spike → Validate → Implement → Review の一連のフローを実行。Harrison Chase の Builder or Reviewer パラダイムに基づく。大きな機能開発で使用。"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, EnterWorktree, EnterPlanMode, ExitPlanMode
user-invocable: true
---

# EPD: Engineering, Product & Design Workflow

アイデアから本番コードまでの一連のフローを EPD（Engineering, Product, Design）の3軸で実行する。

## Philosophy

Harrison Chase "How Coding Agents Are Reshaping EPD" に基づく:

- 実装コストはほぼゼロ → まずプロトタイプで検証
- ボトルネックはレビュー → 3軸で品質担保
- PRD は構造化プロンプト → agent にそのまま渡せる仕様書

## Full Workflow

```
/epd {idea}
  Phase 1: Spec     → /spec でPrompt-as-PRD を生成
  Phase 2: Spike    → /spike でプロトタイプ → /validate で検証
  Phase 3: Decide   → proceed / pivot / abandon
  Phase 4: Build    → /rpi で正式実装
  Phase 5: Review   → /review で3軸レビュー（eng + product + design）
  Phase 6: Ship     → /commit
```

## Phase 1: Spec

spec スキルを呼び出して Prompt-as-PRD を生成する。

- ユーザーとの対話で要件を明確化
- `docs/specs/{feature}.prompt.md` に保存
- acceptance criteria を必ず含める

## Phase 2: Spike

spike スキルを呼び出してプロトタイプを作成・検証する。

- worktree で隔離
- 最小実装 → validate で検証
- spike report を出力

## Phase 3: Decide

spike report に基づいてユーザーに判断を求める:

- **Proceed**: Phase 4 に進む
- **Pivot**: spec を修正して Phase 2 に戻る
- **Abandon**: ワークフロー終了

## Phase 4: Build

rpi スキル（Research → Plan → Implement）を呼び出して正式実装する。

- spike のコードは参考として参照可能
- テスト・lint・コード品質は通常基準で実施
- spec の Prompt セクションを実装指示として活用

## Phase 5: Review

review スキルを呼び出して3軸レビューを実行する。

- **Engineering**: code-reviewer + 言語専門 + codex-reviewer 等（従来通り）
- **Product**: product-reviewer（spec file 存在時に自動追加）
- **Design**: design-reviewer（UI 変更時に自動追加）

レビュー指摘がある場合は修正 → 再レビュー

## Phase 6: Ship

commit コマンドでコミットする。

## Shortcuts

全フェーズを実行する必要はない。状況に応じてスキップ可能:

| 状況                           | ショートカット                     |
| ------------------------------ | ---------------------------------- |
| spec が既にある                | Phase 1 をスキップ                 |
| プロトタイプ不要（確信がある） | Phase 2-3 をスキップ、直接 Phase 4 |
| 小さな変更                     | `/rpi` を直接使用（`/epd` 不要）   |

## Anti-Patterns

- spike のコードを本番に持ち込む（Phase 4 で正式実装する）
- Decide フェーズをスキップする（ユーザー判断は必須）
- spec なしで Build に進む（最低限 acceptance criteria が必要）
