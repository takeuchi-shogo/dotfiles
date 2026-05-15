---
status: reference
last_reviewed: 2026-05-14
---

# Routine Prompt Rubric — Bulletproof Prompt 6 要素

> 出典: Khairallah "How to Set Up Claude Code Routines" (2026-05-13 absorb) Step 3。
> 関連: [`managed-agents-scheduling.md`](managed-agents-scheduling.md) — Routine 設計の上位文書 / [`scheduling-decision-table.md`](scheduling-decision-table.md) — どの仕組みでスケジュールを組むか

`/schedule` で Routine を作るとき、prompt は **次回 run でも同じ品質を出せる** 自己完結性が必要。会話 context は無く、毎 run が clean start。曖昧な prompt は run ごとの出力 drift を生む。

## なぜ rubric が必要か

- Routine は無人実行: 観察者なしで動く。曖昧な prompt は出力品質が run ごとに変動する
- 会話履歴なし: 「前回の続き」が無い。全前提を prompt 内に明示しないと再現性が壊れる
- 副作用が外部に出る: Slack 投稿 / PR コメント / Issue 作成等。曖昧な指示は意図しない副作用を招く
- デバッグが事後: 失敗は翌朝発見。失敗モード列挙が事前必須

## 6 要素テンプレート

```markdown
## Role
あなたは <専門領域> の <役職>。<判断視点> を最優先する。

## Task
<具体的な対象オブジェクト> に対して <動詞> する。
スコープ: <含む対象> / 含まない: <除外対象>

## Process
1. <第 1 ステップ: 何を読むか>
2. <第 2 ステップ: 何を分析するか>
3. <第 3 ステップ: 何を判定するか>
4. <第 4 ステップ: どこに出力するか>

## Output Specification
- 形式: <markdown / JSON / inline comment / Slack message>
- 必須セクション: <列挙>
- 文字数 / 件数: <上限>
- verdict 形式: <approve/request-changes/none 等>

## Error Handling
- <条件 A> なら <代替動作 A>
- <条件 B> なら <代替動作 B>
- 取得失敗時: <fallback または abort 条件>
- 不明な状態時: skip + 通知 (silent fail 禁止)

## Constraints
- <絶対禁止 1> (例: コード直接修正禁止)
- <絶対禁止 2> (例: main branch への push 禁止)
- <上限 1> (例: 1 PR あたり inline comment 最大 3 件)
- <停止条件> (例: 50 ファイル超の PR は skip + manual review 通知)
```

## Good 例: Daily PR Review Routine

```markdown
## Role
あなたは security + performance に特化したシニアコードレビュアー。
business logic 変更は scope 外で、変更が壊していないか / 副作用の連鎖がないかに集中する。

## Task
このリポジトリの open PR のうち、最も古いものを 1 件レビューする。
スコープ: PR description + 変更ファイル / 含まない: PR が依存する他 PR の review

## Process
1. `gh pr list --state open --json number,createdAt --sort created --limit 1` で対象 PR 取得
2. `gh pr view <NUM> --json title,body,files` で description + 変更概要を読む
3. `gh pr diff <NUM>` で diff 全体を読み、security / logic / perf の 3 観点で評価
4. issue を発見したら `gh pr review <NUM> --comment --body "..."` で inline コメント投稿
5. 最後に summary コメント (issue 件数 / 1 段落 assessment / verdict) を投稿

## Output Specification
- 形式: GitHub PR comment (markdown)
- summary 必須セクション: Issue count by severity / Assessment / Verdict (approve | request-changes)
- inline comment 上限: 1 ファイル 3 件まで
- summary 本文: 200 字以内

## Error Handling
- open PR が 0 件: Slack #engineering に「No open PRs to review today.」と投稿
- PR の変更ファイル数 > 50: skip + 「manual review needed: PR #<NUM> has <count> files」を Slack 投稿
- gh コマンド失敗時: stderr を出力して exit 1 (silent fail 禁止)

## Constraints
- Critical severity の issue がある PR は絶対に approve しない
- コードは絶対に修正しない (コメントのみ)
- 1 ファイルあたり inline comment は最大 3 件 (noise 抑制)
- 自分の過去コメントが残っている PR は skip (重複防止)
```

## Bad 例 (anti-pattern)

```markdown
PR を確認してコメントしてください。問題があれば指摘して、なければ approve してください。
```

**何が悪いか**:
- Role 未定義 → security 観点 / style 観点 / 性能観点が run ごとにブレる
- Task の対象が曖昧 → どの PR か、複数あれば何件か不明
- Process 未指定 → diff を読まずに title だけで判定する run が出る
- Output 形式未指定 → 文字数 / 形式 / verdict 表現が drift
- Error Handling 未定義 → open PR が 0 件のとき silent success or 嘘の approve が出る
- Constraints 未定義 → main 直 push / コード直接修正の risk

## Routines 固有の追加注記

- **prompt は self-contained**: 会話 context 無し / 別ファイル参照は repo 内パスで明示 (`@docs/...` か `cat <path>` を Process に含める)
- **副作用は冪等**: 同じ run が 2 回走っても被害が出ない設計 (例: 同じコメントを 2 度投稿しない仕組みを Constraints に書く)
- **fail loud**: error は silent skip せず通知 (Slack / Issue / log)。Routines は無人なので silent fail は致命的
- **`claude/` branch prefix 制約**: コード変更を伴う Routine は `claude/<feature>` branch にしか push できない (default)。main 直 push は最初から構造的に不可能 — Constraints に「main への push 禁止」と書くのは redundant だが、Routine 出力を merge する人間レビュー過程は別途必要

## Pre-flight Checklist (Routine 公開前)

- [ ] Role / Task / Process / Output / Error / Constraints の 6 セクション全てある
- [ ] Process の各ステップが「読む対象」「分析方法」「判定基準」「出力先」を含む
- [ ] Error Handling に「該当ゼロ件」「閾値超過」「外部 API 失敗」の 3 ケースがある
- [ ] Constraints に「絶対禁止」「数値上限」「停止条件」の 3 種類がある
- [ ] 同 Routine を 2 回連続走らせても副作用が冪等
- [ ] 失敗時に必ず通知が飛ぶ (silent fail なし)
- [ ] `claude/` branch prefix 制約と整合 (コード変更を伴う場合)

## 関連

- [`managed-agents-scheduling.md`](managed-agents-scheduling.md) — Routine 全体設計 / pilot
- [`scheduling-decision-table.md`](scheduling-decision-table.md) — どの仕組みでスケジュールを組むか
- [`pre-mortem-checklist.md`](pre-mortem-checklist.md) — 失敗モード列挙
