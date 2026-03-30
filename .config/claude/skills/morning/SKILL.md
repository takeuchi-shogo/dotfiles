---
name: morning
description: >
  朝の開発計画を生成する。GitHub Issues/Projects の状態、進行中タスク、優先度を分析し、今日取り組むべきタスクを提案。毎朝のセッション開始時に使用。
  Triggers: 'おはよう', '今日の計画', 'morning', '朝のプラン', 'what should I work on today'.
  Do NOT use for: 日報作成（use /daily-report）、週次レビュー（use /weekly-review）、振り返り（use /timekeeper review）。
---

## Skill Assets

- `templates/morning-routine.md` — Morning routine template (energy check, today's focus, time blocks, carry-over)
disable-model-invocation: true
allowed-tools: Bash(gh *), Read, Grep, Glob
metadata:
  pattern: inversion+generator
---

# Morning Planning

朝のセッション開始時に、今日の開発計画を生成する。

## 設定確認

!`cat .claude/dev-ops.local.json 2>/dev/null || echo "NOT_CONFIGURED"`

上記が `NOT_CONFIGURED` の場合:
「開発オペレーション設定がまだありません。`/dev-ops-setup` を実行してセットアップしてください。」と案内して終了。

## 情報収集（並列実行）

以下の情報を `gh` CLI で並列取得する:

### 1. 自分にアサインされた Issue

```bash
gh issue list --assignee {my_username} --state open --json number,title,labels,milestone,updatedAt --limit 30
```

チームラベルが設定されている場合はラベルでもフィルタ:
```bash
gh issue list --label {team_label} --state open --json number,title,labels,assignees,milestone,updatedAt --limit 30
```

### 2. 進行中タスク（GitHub Projects がある場合）

```bash
gh project item-list {project_number} --owner {owner} --format json --limit 100
```

Status が「In Progress」「In Review」のアイテムを抽出。

### 3. 最近のアクティビティ

```bash
# 昨日以降の自分のコミット
git log --oneline --since="yesterday" --author="{my_username}" --no-merges 2>/dev/null | head -10

# オープン中の自分の PR
gh pr list --author {my_username} --state open --json number,title,reviewDecision,statusCheckRollup --limit 10
```

### 4. レビュー待ちの PR

```bash
gh pr list --search "review-requested:{my_username}" --state open --json number,title,author,createdAt --limit 10
```

## TELOS 目標確認（計画生成前）

GitHub タスクを提案する前に、ユーザーの目標体系を確認する:

1. `memory/telos_goals.md` を読み、現在の短期目標を把握
2. 収集した GitHub タスクを目標に紐づける（どの目標に貢献するか）
3. GitHub タスクと目標の関連が薄い場合、目標に沿った行動を1つ「目標連動タスク」として提案

**出力に反映**: 計画の各タスクに `[目標: ...]` タグを付与する（該当する場合のみ）。

## 計画生成

収集した情報を分析し、以下の形式で今日の計画を提案:

```
## 今日の計画 (YYYY-MM-DD)

### 継続中のタスク
- [ ] #XX タスクタイトル [In Progress] — 昨日のコミット: "xxx"
- [ ] #YY タスクタイトル [In Review] — PR #ZZ レビュー待ち

### レビュー依頼
- [ ] PR #AA "タイトル" by @author — N日前に依頼

### 今日着手推奨
- [ ] #BB タスクタイトル [Ready/P1] — 理由: 優先度高・期限近い
- [ ] #CC タスクタイトル [Ready/P2] — 理由: 依存タスクなし

### 注意事項
- PR #DD のCIが失敗中 — 確認が必要
- #EE の期限が明後日 — 優先度を上げることを推奨
```

## 提案ルール

1. **継続中タスク最優先**: In Progress のタスクがあればそれを最初に
2. **レビューは午前中に**: レビュー待ちPRがあれば早めに対応を推奨
3. **新規着手は2-3個まで**: 多すぎるタスクを提案しない
4. **期限考慮**: milestone や期限が近いものを優先
5. **優先度ラベル**: P0 > P1 > P2 > P3 の順

## GitHub Projects がない場合

GitHub Issues のみで動作する。ステータスは:
- ラベル（`in-progress`, `ready` 等）
- アサイン状況
- Issue のオープン/クローズ状態

から推定する。

## Anti-Patterns

| NG | 理由 |
|----|------|
| GitHub 状態を確認せずに計画する | 前日の進捗や新 Issue を見落とし、優先度がずれる |
| 1日に5個以上のタスクを計画する | 消化しきれず挫折感が残る。2-3個に絞る |
| 計画だけして実行に移らない | /morning の後は即座にタスクに着手する |
