# ExecPlan Contract

複数ステップ・複数ファイル・長時間の変更では、実装前に plan を作り、作業中に更新する。

## When Required

- 複数ディレクトリをまたぐ
- 新しい skill / script / MCP / workflow を追加する
- Claude / Codex / symlink / validation のような harness 面を変更する
- 30 分以上かかる見込みがある
- 途中で中断・handoff・resume の可能性がある

軽微な typo や 1 ファイルの小修正では省略してよい。

## File Location

- 原則: `docs/plans/YYYY-MM-DD-<topic>-plan.md`
- 進行中の plan は必要に応じて `docs/plans/active/` に置く
- design を分けるときは `...-design.md` を隣に置いてよい

## Required Sections

```md
# <Task title>

## Goal
- 何を変えるか

## Scope
- 触るファイル、触らないファイル

## Constraints
- 壊してはいけない挙動
- 既存ルール、互換性、承認条件

## Validation
- 実行する task / test / lint / review

## Steps
1. 調査
2. 実装
3. 検証

## Progress
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Surprises & Discoveries
- 作業中に分かったこと

## Decision Log
- 重要な判断と理由

## Outcome
- 最終結果
- 未解決事項
```

## Working Rules

- plan は作って終わりではなく、作業中に更新する
- goal、scope、validation を途中で暗黙に変えない
- 想定外を見つけたら `Surprises & Discoveries` に残す
- 重要な方針変更は `Decision Log` に残す
- 中断前は checkpoint と plan の両方を最新化する
- 並列で別 task を進めるときは worktree で filesystem を分離する

## Agent Notes

- Codex:
  - 長時間作業は `$codex-checkpoint-resume` と併用する
  - 必要なら `$codex-session-hygiene` を使う
- Claude Code:
  - `plansDirectory` は `./tmp/plans` だが、永続化したい plan は `docs/plans/` に保存する
  - workflow の詳細は `.config/claude/references/workflow-guide.md` を参照する
