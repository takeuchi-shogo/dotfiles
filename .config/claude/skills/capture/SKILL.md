---
name: capture
description: >
  GTD式の即時キャプチャ。思いつき、TODO、メモを GitHub Issue として即座に登録する。考えと記録を分離し、後で /morning や /weekly-review で整理する。
  Triggers: 'capture', '思いついた', 'TODO登録', 'メモっておいて', 'quick capture', 'inbox'.
  Do NOT use for: Obsidian への知見保存（use /note）、仕様書作成（use /spec）、既存 Issue の操作（use /kanban）。
origin: self
disable-model-invocation: true
allowed-tools: Bash(gh *)
argument-hint: "<memo text>"
metadata:
  pattern: generator
---

# Quick Capture

思いつきを即座に GitHub Issue としてキャプチャする。

## 設定確認

!`cat .claude/dev-ops.local.json 2>/dev/null || echo "NOT_CONFIGURED"`

上記が `NOT_CONFIGURED` の場合:
「開発オペレーション設定がまだありません。`/dev-ops-setup` を実行してセットアップしてください。」と案内して終了。

## キャプチャ内容

`$ARGUMENTS` の内容をキャプチャする。

引数がない場合は「何をキャプチャしますか？」と質問する。

## 処理フロー

### 1. 内容の整理

ユーザーの入力をそのまま使わず、以下を行う:
- タイトルを簡潔に生成（50文字以内）
- 本文にユーザーの元テキストを含める
- 可能なら種類を推定（bug / feature / task / idea / question）

### 2. Issue 作成

```bash
gh issue create \
  --title "{generated_title}" \
  --body "{body}" \
  --label "{capture_label}" \
  --assignee "{my_username}"
```

本文フォーマット:
```markdown
## Captured

{ユーザーの元テキスト}

## Context

- Captured at: {timestamp}
- Project: {owner}/{repo}
- Working branch: {current_branch}
- Related files: {直近で編集していたファイル（あれば）}

---
*Captured via `/capture` — 後で `/morning` または `/weekly-review` で整理*
```

### 3. チームラベル付与

`team_labels` が設定されている場合、それも追加:
```bash
gh issue edit {number} --add-label "{team_label}"
```

### 4. 確認メッセージ

```
Captured: #{number} "{title}"
Label: {capture_label}
URL: {issue_url}
```

## 複数キャプチャ

引数にカンマ区切りまたは改行で複数項目が含まれる場合、それぞれ別 Issue として作成する。
作成前に一覧を表示し、確認を取る。

## キャプチャの原則

- **即時性**: 考えを止めない。整理は後で
- **最小限の情報**: タイトルと元テキストだけで十分
- **コンテキスト自動付与**: ブランチ名や作業ファイルを自動記録
- **後処理前提**: inbox ラベルで `/morning` や `/weekly-review` で棚卸しされる
