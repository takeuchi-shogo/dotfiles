---
name: hook-debugger
description: >
  Hook が期待通り発火しない・エラーになる時の診断 Runbook。ログ確認→正規表現検証→手動実行→修正の手順を案内。
  Triggers: 'hook が動かない', 'hook not firing', 'hook error', 'フック デバッグ',
  'hook debug', 'PostToolUse が発火しない', 'PreToolUse が効かない'.
  Do NOT use for hook の新規作成 — use /update-config skill instead.
origin: self
allowed-tools: Read, Bash, Grep, Glob
metadata:
  pattern: runbook
---

# Hook Debugger — Runbook

Hook が期待通り動作しない時の体系的な診断手順。

## Symptom → Action マッピング

| 症状 | 最も可能性の高い原因 | 確認手順 |
|-----|-------------------|---------|
| hook が発火しない | matcher パターン不一致 | Step 1 → Step 2 |
| hook がエラーで失敗 | スクリプトのパーミッション or 構文エラー | Step 3 |
| hook の出力が無視される | JSON 出力形式の不備 | Step 4 |
| hook が遅すぎる | タイムアウト設定不足 | Step 5 |

## Step 1: Hook 登録状況の確認

```bash
# settings.json / settings.local.json の hooks を一覧
./scripts/check-hook-health.sh
```

## Step 2: Matcher パターンの検証

```bash
# matcher が意図したツール名にマッチするか確認
# 注意: \b は日本語(Unicode)で誤動作する → (?=[^a-zA-Z0-9]|$) を使う
echo "Bash" | grep -P "^(Edit|Write)$"  # マッチしない例
echo "Edit" | grep -P "^(Edit|Write)$"  # マッチする例
```

よくあるミス:
- `Bash(git commit)` — `*` ワイルドカードが必要: `Bash(git commit *)`
- `Edit|Write` — 正しい。パイプは OR として機能する
- `Bash(npm .*)` — matcher は正規表現ではなくグロブパターン

## Step 3: スクリプトの手動実行

```bash
# スクリプトに実行権限があるか
ls -la ~/.claude/scripts/{layer}/{script-name}

# 手動で実行してエラーを確認
echo '{"tool_name":"Bash","tool_input":{"command":"echo test"}}' | \
  python3 ~/.claude/scripts/{layer}/{script-name}
```

## Step 4: JSON 出力形式の確認

PostToolUse / PreToolUse のスクリプトは JSON を stdout に出力する必要がある:

```json
// PreToolUse — ブロックする場合
{"decision": "block", "reason": "理由"}

// PreToolUse — 許可する場合（何も出力しない or）
{"decision": "allow"}

// PostToolUse — 追加コンテキストを返す場合
{"additionalContext": "補足情報"}
```

SessionStart は plain text を stdout に出力する（JSON ではない）。

## Step 5: タイムアウトの確認

デフォルトタイムアウトを超えるとスクリプトは kill される:

```bash
# タイムアウト値を確認
grep -A 5 'timeout' ~/.claude/settings.json ~/.claude/settings.local.json
```

## Gotchas

- **shebang 行**: `#!/usr/bin/env python3` がないと実行環境が不定になる
- **stdin の消費**: PreToolUse/PostToolUse は stdin から JSON を読む。`input()` で先に読むと `json.load(sys.stdin)` が空になる
- **PATH の違い**: hook 実行時の PATH はユーザーのシェルと異なる場合がある。フルパス推奨
- **並行実行**: 同じイベントに複数の hook が登録されている場合、実行順序は保証されない
- **SKILL.md hooks vs settings.json hooks**: SKILL.md の hooks はスキルが active な時のみ有効。settings.json はグローバル
