---
name: dev-cycle
description: "Claude Code + Codex 協調開発サイクルを Issue 作成からマージまで一貫実行するオーケストレーター。auto（全自動）/ semi（確認ポイント付き）/ manual（手順ガイド）の3モードで実行。 Triggers: 'dev-cycle', '開発サイクル', 'Issue から マージまで', 'Claude + Codex サイクル', 'フル開発フロー Issue 起点', 'Issue 作成から実装まで', '全自動開発'. Do NOT use for: 仕様が既に明確な単発タスク（use /rpi）、Issue なしの直接実装（use /epd）、レビューのみ（use /review or /codex-review）。"
allowed-tools: "Read, Bash, Grep, Glob, AskUserQuestion, Agent, Skill"
metadata:
  pattern: orchestrator
  version: 1.0.0
  category: workflow
---

# /dev-cycle -- Claude Code + Codex 協調開発サイクル

Issue 作成からマージまでの6ステップを、Claude Code と Codex の協調で実行する。

## サイクル概要

```
[1] Claude: 要件 -> Issue 作成         (/create-issue)
[2] Codex: Issue レビュー              (/codex-review-issue)
[3] Claude Code: 実装 -> Push -> PR    (/rpi + /create-pr-wait)
[4] Codex: PR にレビューコメント投稿   (/codex-review --post-to-pr)
[5] ユーザー: 補完コメント             (手動)
[6] AI: 修正 -> ユーザー確認 -> マージ (/github-pr + fix-routing-guide)
```

## 使い方

```
/dev-cycle auto "要件テキスト"     -- 全自動（Step 5 でユーザー待機）
/dev-cycle semi "要件テキスト"     -- 半自動（4箇所で確認ポイント）
/dev-cycle manual                  -- 手順ガイドのみ表示
```

---

## Mode A: auto

引数: `auto "要件テキスト"`

Step 1-4 を自動で連続実行する。Step 5 でユーザーに通知して待機。Step 6 で AI が修正しユーザーがマージ判断。

### 実行手順

**Step 1 -- Issue 作成**
`/create-issue` を実行し、要件テキストから Issue を作成する。Issue 番号を取得して次ステップへ渡す。

**Step 2 -- Issue レビュー**
`/codex-review-issue #N` を実行する。

MUST 指摘への対応:
- MUST 指摘がない場合 → Step 3 へ進む
- MUST 指摘がある場合 → AskUserQuestion で「Issue に MUST 指摘があります。修正方法を選んでください: A) AI が Issue を自動修正して再レビュー B) ユーザーが GitHub で手動修正 C) 指摘を確認済みとしてそのまま進む」と確認
  - A: `gh issue edit #N --body "..."` で修正 → `/codex-review-issue #N` で再レビュー（最大2回）
  - B: ユーザーの修正完了を待つ
  - C: そのまま Step 3 へ（ユーザー判断を尊重）

**Step 3 -- 実装 + PR 作成**
`/rpi #N` で実装し、`/create-pr-wait` で PR を作成する。PR 番号を取得して次ステップへ渡す。

**Step 4 -- PR レビューコメント投稿**
`/codex-review --post-to-pr #PR` でレビューコメントを PR に投稿する。

**Step 5 -- ユーザー補完コメント**
AskUserQuestion で以下を伝える:

> PR #PR にレビューコメントが投稿されました。補完コメントがあれば GitHub で追記してください。完了したら教えてください。

ユーザーの応答を待つ。

**Step 6 -- 修正 + マージ**
`references/fix-routing-guide.md` に従ってレビューコメントを分類・対応する。修正完了後、`/github-pr` でマージ判断を実行する。マージ判断は常にユーザーが行う。

---

## Mode B: manual

引数: `manual`（要件テキスト不要）

以下のガイドを出力して終了する。実行はユーザーが各スキルを個別に呼ぶ。

```
## Dev Cycle -- Manual Mode

以下の順序でスキルを実行してください:

1. /create-issue "要件テキスト"       -- Issue 作成
2. /codex-review-issue #N             -- Issue レビュー
3. /rpi #N                            -- 実装
4. /create-pr-wait                    -- PR 作成 + CI 監視
5. /codex-review --post-to-pr #PR    -- PR レビューコメント
6. GitHub で補完コメントを追加
7. /github-pr                         -- コメント対応 + マージ判断

各ステップの詳細は対応するスキルを参照。
```

---

## Mode C: semi

引数: `semi "要件テキスト"`

auto と同じフローだが、以下の4箇所で AskUserQuestion による確認を挟む。

### 確認ポイント

| タイミング | 質問 |
|------------|------|
| Step 1-2 完了後 | 「Issue #N が作成・レビューされました。実装に進みますか?」 |
| Step 3 完了後 | 「PR #PR が作成されました。Codex レビューを実行しますか?」 |
| Step 4 完了後 | 「レビューコメントが投稿されました。補完コメントを追加しますか?」 |
| Step 6 修正完了後 | 「修正が完了しました。マージしますか?」 |

確認で「いいえ」の場合、そのステップで中断し状況を報告する。ユーザーが手動で対応した後、途中から再開可能。

---

## エラーハンドリング

- **Codex 429 エラー**: 30 秒待って再試行する。3回失敗でユーザーに報告
- **Issue レビューで MUST 指摘**: Issue を修正してからステップ 3 に進む。自動修正できない場合はユーザーに確認
- **CI 失敗**: `/create-pr-wait` が最大3回リトライする。3回失敗でユーザーに報告
- **中断からの再開**: semi モードで途中のステップから再開可能。Issue 番号と PR 番号を指定して再開する

## Gotchas

- auto モードは長時間かかる（Issue 作成からマージまで）。途中で中断した場合は semi モードで途中から再開可能
- `/rpi` は Issue 番号を引数に取る。Issue が作成されていることが前提
- Codex レビューはレート制限がある。429 エラー時は 30 秒待って再試行
- dotfiles リポジトリでは `--skip-git-repo-check` が必要（symlink 問題）

## Decision: dev-cycle vs rpi vs epd

| 状況 | 推奨 | 理由 |
|------|------|------|
| 要件から Issue + Codex レビュー + 実装 + マージまで | `/dev-cycle auto` | 全工程を自動化 |
| 途中確認しながら進めたい | `/dev-cycle semi` | 4箇所で判断ポイント |
| Issue は既にある、仕様も明確 | `/rpi` | Issue 起点の実装のみ |
| Issue なし、仕様が曖昧 | `/epd` | Spec から始める |
| レビューだけ欲しい | `/review` or `/codex-review` | レビュー専用 |

## Anti-Patterns

| NG | 理由 |
|----|------|
| auto モードでユーザー確認なしにマージする | マージ判断は常にユーザーが行う |
| Issue レビュー結果を無視して実装に進む | MUST 指摘がある場合は Issue を修正してから |
| 全ステップを1つの巨大プロンプトで実行する | 各ステップは独立したスキル呼び出しで分離する |
| semi モードで確認ポイントをスキップする | semi の意味がなくなる |

## 関連スキル・リファレンス

- `/create-issue` -- Step 1
- `/codex-review-issue` -- Step 2
- `/rpi`, `/create-pr-wait` -- Step 3
- `/codex-review --post-to-pr` -- Step 4
- `/github-pr` -- Step 6
- `references/fix-routing-guide.md` -- Step 6 の修正振り分け
