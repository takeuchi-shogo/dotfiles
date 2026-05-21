# PR Reviewer Launchd Playbook (Phase A)

`scripts/runtime/poll-pr-reviewer.sh` を launchd から 10 分間隔で実行し、
`knowledge-work/knowledgework` で自分が review-requested された PR を
cmux PR Review Agent に自動投入する。

> **想定環境**: work Mac (`MacBookPro-work`) のみ。private Mac では host gate で silent skip。

## 仕組み

```
launchd (10 min)
  └─> poll-pr-reviewer.sh
        ├─ host gate (work Mac only)
        ├─ active worktree 数 < MAX_PARALLEL(2) 確認
        ├─ gh search prs --review-requested=@me --repo knowledge-work/knowledgework
        ├─ 各 PR について .processed/pr-<#>.done なければ
        │    env CMUX_PR_NUMBER=<n> cmux new-workspace --command "PR Review Agent"
        └─ 成功で marker 作成
```

レビュー結果は `~/projects/knowledge-work/knowledgework-review/.claude/worktrees/pr-<#>/.claude/pr-reviews/pr-<#>.md` に出力される。**GitHub への投稿はしない**（人間 in the loop 維持）。

## Install

```bash
# 1. plist を展開して LaunchAgents に配置
mkdir -p ~/Library/LaunchAgents
sed "s|@@HOME@@|$HOME|g" \
  ~/dotfiles/scripts/runtime/com.user.pr-reviewer.plist.tpl \
  > ~/Library/LaunchAgents/com.user.pr-reviewer.plist

# 2. log ディレクトリ作成
mkdir -p ~/Library/Logs/pr-reviewer

# 3. launchd に登録
launchctl bootstrap "gui/$UID" ~/Library/LaunchAgents/com.user.pr-reviewer.plist

# 4. 確認
launchctl print "gui/$UID/com.user.pr-reviewer" | head
```

## 動作確認

```bash
# 手動で 1 回実行 (host gate 越え必須)
~/dotfiles/scripts/runtime/poll-pr-reviewer.sh

# ログ確認
tail -f ~/Library/Logs/pr-reviewer/poll.log

# 強制起動 (launchd 経由のスケジュール kick)
launchctl kickstart "gui/$UID/com.user.pr-reviewer"
```

期待する poll.log エントリ例:

```
2026-05-20T15:00:00+0900 [12345] poll: found 1 review-requested PR(s) (active: 0)
2026-05-20T15:00:01+0900 [12345] invoke cmux for pr-116123 (author: @haniwawww): feat(...): ...
2026-05-20T15:00:03+0900 [12345] ok pr-116123: marker written
```

cmux 側に新規 workspace が出現し、Setup pane で `CMUX_PR_NUMBER=116123` を拾って非対話で worktree を作る → Claude pane が起動するのが正常系。

## Uninstall

```bash
launchctl bootout "gui/$UID/com.user.pr-reviewer"
rm ~/Library/LaunchAgents/com.user.pr-reviewer.plist
```

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| poll.log に何も書かれない | host gate で early exit (`MacBookPro-work` 以外) | 想定通り。private Mac では動かさない |
| `ERROR: gh not in PATH` | launchd の PATH に Homebrew が無い | plist の `EnvironmentVariables/PATH` を確認 |
| `ERROR: gh search failed` | `gh auth` 切れ、または rate limit | `gh auth status` で確認、または 10 分待つ |
| `skip cycle: 2 active worktree(s)` | 並列上限到達 | 想定通り。終わったレビューの worktree を `git worktree remove` |
| 同じ PR が再度起動される | marker `.processed/pr-<#>.done` が消えた | 意図せず削除されていないか確認 |
| cmux invoke 失敗 | cmux 未起動、または `PR Review Agent` action 未定義 | cmux 起動状況と `.config/cmux/cmux.json` 確認 |

## 設計判断

- **並列上限 2**: サブスクレート枠保護。同時に複数の Claude セッションが走るとレート制限・コスト懸念
- **10 分間隔**: GitHub Search API は秒間ベースで rate limit (30 req/min 程度)。10 分なら十分余裕
- **marker 戦略**: PR 番号ベース。レビュー再実行 (force) したい場合は marker を手動削除
- **host gate**: launchd plist は誤って private Mac の chezmoi 同期で load される可能性。スクリプト側にも防御層
- **GitHub 投稿しない**: `gh pr review --comment` は呼ばない。出力 markdown を人間が読んで判断 (人間 in the loop 維持)

## 関連

- Plan: `docs/plans/active/2026-05-19-pr-review-agent-plan.md`
- Setup script: `scripts/runtime/prepare-pr-review.sh`
- cmux action: `.config/cmux/cmux.json` actions.pr-review-agent
- Review template: `templates/pr-review/REVIEW_TASK.md.tpl`
