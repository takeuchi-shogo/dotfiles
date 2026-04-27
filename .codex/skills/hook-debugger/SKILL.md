---
name: hook-debugger
description: >
  Codex hooks が期待通り発火しない・エラーになる時の診断 Runbook。
  config.toml [hooks] table の検証、hooks.json との優先順位確認、stdin JSON 検証、
  exit code 確認、既知バグ #19199 の workaround を案内。
  Triggers: 'codex hook が動かない', 'codex hook not firing', 'codex hook error',
  'PostToolUse が発火しない', 'PreToolUse が効かない', 'codex_hooks crash'.
  Do NOT use for: Claude hook デバッグ (use Claude 版 hook-debugger), Codex hook の新規作成 (まず公式 docs を読む).
origin: self
metadata:
  pattern: runbook
  version: 1.0.0-codex
  category: harness
  platform: codex
---

# Hook Debugger (Codex 版) — Runbook

Codex CLI v0.124.0+ の hooks framework が期待通り動作しない時の体系的な診断手順。

**前提**: 公式 docs https://developers.openai.com/codex/hooks を読んでいること。

## Codex Hooks の最重要 Gotcha

| # | 罠 | 影響 |
|---|----|------|
| 1 | `[features] codex_hooks = true` を書き忘れる | hooks が **サイレントに無視** される |
| 2 | TOML 構造が一層 `[[hooks.PostToolUse]]` のみ | `command` が認識されない。**二層** `[[hooks.X]]` + `[[hooks.X.hooks]]` 必須 |
| 3 | event 名を snake_case (`post_tool_use`) にする | 認識されない。**PascalCase** (`PostToolUse`) 必須 |
| 4 | v0.124.0 既知バグ #19199 | "invalid type: map, expected a sequence" で起動クラッシュ |

## Symptom → Action マッピング

| 症状 | 最も可能性の高い原因 | 確認手順 |
|-----|-------------------|---------|
| Codex 起動でクラッシュ ("invalid type: map") | #19199 | Step 0 |
| hook が発火しない (起動はする) | feature flag 未設定 / event 名誤り / matcher 不一致 | Step 1 → Step 2 → Step 3 |
| hook がエラーで失敗 | command 構文エラー / PATH 問題 / shebang 不在 | Step 4 |
| hook の出力が無視される | stdout JSON 形式不備 / exit code 誤用 | Step 5 |
| hook が遅すぎる / kill される | timeout 不足 (デフォルト 600s) | Step 6 |

## Step 0: 起動クラッシュ (#19199)

```bash
# Codex が起動するか
codex --version
# クラッシュする場合: stderr を確認
codex exec --skip-git-repo-check 'echo test' 2>&1 | head
```

エラーが `Error loading config.toml: invalid type: map, expected a sequence in 'hooks'` の場合:

1. 一時的に rollback: `codex_hooks = false`
2. 設定を **二層構造で厳密に** 書き直す (Step 2 参照)
3. 段階的に hooks を追加 (1 つずつ)

## Step 1: Feature flag 確認

```bash
# 設定ファイル
grep -E "codex_hooks|\[features\]" ~/.codex/config.toml
# 期待: codex_hooks = true が [features] テーブル下にある

# 機能フラグ
codex features list 2>&1 | grep codex_hooks
# 期待: codex_hooks  stable  true
```

`true` でない場合は `[features] codex_hooks = true` を追加。

## Step 2: Event 名と TOML 構造の検証

正しい二層構造 (config.toml):
```toml
[features]
codex_hooks = true

[[hooks.PostToolUse]]              # 外側: matcher
matcher = "apply_patch"

[[hooks.PostToolUse.hooks]]        # 内側: command
type = "command"
command = "/path/to/script.sh"
timeout = 30
statusMessage = "Running hook"
```

正しい event 名 (PascalCase):
- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `PermissionRequest`
- `Stop`

❌ よくあるミス:
- `[hooks.post_tool_use]` (snake_case)
- `[[hooks.PostToolUse]]` だけで内側 `[[hooks.PostToolUse.hooks]]` を書かない
- `command = ...` を外側に書く

## Step 3: Matcher パターンの検証

matcher は **regex 文字列**:

```toml
matcher = "Bash"                # tool 名 = "Bash"
matcher = "^apply_patch$"       # apply_patch のみ厳密一致
matcher = "Edit|Write"          # OR
matcher = "mcp__filesystem__.*" # MCP tool prefix
matcher = "startup|resume"      # SessionStart 用
```

regex のテスト:
```bash
# ツール名が matcher にマッチするか
python3 -c "import re; print(bool(re.search(r'apply_patch', 'apply_patch')))"
```

## Step 4: スクリプトの手動実行

```bash
# 実行権限とパス
ls -la /path/to/hook-script.sh
which python3

# Codex の hook stdin に渡される JSON 構造で手動テスト
echo '{
  "session_id": "test",
  "transcript_path": "/tmp/test",
  "cwd": "/tmp",
  "hook_event_name": "PostToolUse",
  "model": "gpt-5.5",
  "turn_id": "test"
}' | /path/to/hook-script.sh
```

期待:
- `exit 0`: 続行
- `exit 2`: ブロック (理由は stderr に出力)
- それ以外: failure 扱い

## Step 5: stdout JSON / exit code

PostToolUse / PreToolUse の hook は **任意で** stdout に JSON を出せる:

```json
{
  "continue": true,
  "stopReason": null,
  "systemMessage": "optional message",
  "suppressOutput": false,
  "hookSpecificOutput": { /* event 別 */ }
}
```

ブロックしたい場合: **exit code 2** + stderr にメッセージ (Claude と一致)。

SessionStart は plain text を stdout に出力 (JSON 不要)。

## Step 6: Timeout

```toml
[[hooks.PostToolUse.hooks]]
type = "command"
command = "..."
timeout = 30  # 秒。省略時は 600
```

長時間処理は別プロセスに逃がして hook 自体は即 return。

## Step 7: hooks.json との関係

```bash
# hooks.json も読まれる
ls ~/.codex/hooks.json
ls .codex/hooks.json
```

config.toml と hooks.json の優先順位は **公式 docs に明記なし**。両方書いた場合の挙動は要実測。原則: 片方だけにする。

## Gotchas

- **環境変数**: `CODEX_TOOL_NAME` 等の env var は **公式 docs に未記載**。情報伝達は **stdin JSON** が公式
- **stdin 消費**: hook script で `input()` などを先に呼ぶと stdin JSON が消える
- **PATH の違い**: hook 実行時の PATH はシェルと異なる。**フルパス推奨**
- **並行実行**: 同じ event に複数 hook を登録した場合の実行順序は保証されない
- **MCP tool**: `mcp__<server>__<tool>` 形式の tool 名で matcher 可能 (PR #18385)
- **apply_patch hooks**: PR #18391 で apply_patch にも hooks が emit される
- **Bash PostToolUse**: `write_stdin` 経由の exec_command 完了時にも emit (PR #18888)

## 既知バグ参照

- [#19199](https://github.com/openai/codex/issues/19199): v0.124.0 で `codex_hooks=true` 時にクラッシュ報告
- [#18893](https://github.com/openai/codex/pull/18893): hooks 公式サポート PR
- [#19012](https://github.com/openai/codex/pull/19012): codex_hooks stable 化 PR

## Related

- 公式 Hooks ガイド: https://developers.openai.com/codex/hooks
- Config Reference: https://developers.openai.com/codex/config-reference
- Claude 版 hook-debugger: `~/.claude/skills/hook-debugger/SKILL.md` (Claude 用、別途維持)
