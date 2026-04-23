---
status: active
last_reviewed: 2026-04-23
---

# Add Hook Playbook

新しい PreToolUse / PostToolUse / UserPromptSubmit hook を `.config/claude/settings.json` に追加するときの 6-step。

## 前提

- hook は agent の挙動を deterministic に制約するメカニズム
- prompt 指示で済むなら hook 化しない（`Static-checkable rules は mechanism に寄せる` 原則）
- 既存 hook の重複を避ける: `jq '.hooks | keys' .config/claude/settings.json` で全 phase 確認

## 6-step

### 1. Scope 決定（どの phase に発火させるか）

| 目的 | phase | 例 |
|---|---|---|
| ツール実行**前**にブロック / 警告 | `PreToolUse` | linter config の編集ブロック |
| ツール実行**後**に検査 / 自動修正 | `PostToolUse` | format + size-check |
| ユーザー入力**前**に介入 | `UserPromptSubmit` | prompt injection 検出 |
| 通知のみ | `Notification` | エージェント完了 |
| compact 前後の永続化 | `PreCompact` / `PostCompact` | running-brief 更新 |
| セッション開始時 | `SessionStart` | env bootstrap |

**判定**: hard block が必要 → Pre / 観測のみ → Post / 介入なら Pre。

### 2. Script 配置先選定

| ディレクトリ | 用途 | 例 |
|---|---|---|
| `.config/claude/scripts/policy/` | hook で呼ぶ制約・検証・警告 | completion-gate.py, file-proliferation-guard.py, claudemd-size-check.py |
| `.config/claude/scripts/runtime/` | hook で呼ぶ実行時補助・bootstrap | env-bootstrap.py, error-rate-monitor.py |
| `.config/claude/scripts/learner/` | hook で呼ぶデータ収集・学習 | session-learner.py, failure-clusterer.py |
| `scripts/lifecycle/` | CLI で直接実行する定期処理 | dead-weight-scan.py, doc-status-audit.py |

**重要**: hook から呼ぶ script は `.config/claude/scripts/` 配下に置く（`~/.claude/scripts/` symlink 経由で settings.json から `$HOME/.claude/scripts/...` 参照）。CLI 単独実行の lifecycle スクリプトはリポジトリ直下 `scripts/lifecycle/` に置く（symlink なし）。

**判定**: 「制約か観測か学習か掃除か」の 4 択。

### 3. Script 実装

最小テンプレート (Python):

```python
#!/usr/bin/env python3
"""<目的を1行>"""
import json, sys, os
def main() -> int:
    if os.environ.get("MY_HOOK_DISABLE") == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # 解析失敗時は素通り
    # 必要なフィールドだけ取り出す
    tool_input = payload.get("tool_input") or {}
    # 判定ロジック
    if <bad>:
        print("[my-hook] WARNING: ...", file=sys.stderr)
        return 0  # soft warning
        # return 2  # hard block (PreToolUse のみ意味あり)
    return 0
if __name__ == "__main__":
    sys.exit(main())
```

注意:
- stdin から JSON を受け取る（`tool_input`, `tool_name`, `session_id` 等）
- exit 0 = 通過、exit 2 = ブロック（PreToolUse のみ）
- stderr にメッセージ → claude-code に displayed
- env var で disable できるようにする（debug / 一時無効化）

### 4. settings.json に matcher + command 登録

```bash
# 既存の matcher に hook を追加（jq で安全に）
cp .config/claude/settings.json /tmp/settings.json.bak
jq '.hooks.PostToolUse[0].hooks += [
  {"type":"command","command":"python3 $HOME/.claude/scripts/policy/my-hook.py","timeout":5}
]' /tmp/settings.json.bak > .config/claude/settings.json
```

新規 matcher を追加する場合:

```bash
jq '.hooks.PostToolUse += [
  {"matcher":"Edit|Write","hooks":[{"type":"command","command":"...","timeout":5}]}
]' /tmp/settings.json.bak > .config/claude/settings.json
```

### 5. 正規表現テスト

matcher の regex は **日本語の `\b` を使わない**:

```
NG:  "matcher": "\\bspec\\b"        # 日本語の前後で誤マッチ
OK:  "matcher": "(?=[^a-zA-Z0-9]|$)spec(?=[^a-zA-Z0-9]|$)"
```

テスト: 実際に該当ツールを発火させて hook が動くか確認。

```bash
# 手動でスクリプト単体テスト
echo '{"tool_input":{"file_path":"/path/to/test"}}' | python3 scripts/policy/my-hook.py
echo "exit=$?"

# settings.json の構文チェック
jq . .config/claude/settings.json > /dev/null && echo OK
```

### 6. Validate / Rollback / Commit

```bash
task validate-configs       # JSON 構文確認
task validate-symlinks      # symlink 経由の参照確認

# rollback 条件を hook ファイル冒頭にコメント
# 例: "誤警告が 1 セッションで 5 回超えたら settings.json から外す"

# commit
git add .config/claude/settings.json scripts/policy/my-hook.py
git commit -m "feat(hooks): add my-hook for ..."
```

## Anti-patterns

- ✗ exit 2 を PostToolUse で使う（無効、ブロックされない）
- ✗ regex で `\b` を日本語環境で使う
- ✗ 1 hook で複数の責務（format + lint + custom check）
- ✗ stdin の JSON 失敗で例外を投げて exit 1
- ✗ env var disable を用意せず stuck

## 関連

- 既存 hook の一覧: `jq '.hooks' .config/claude/settings.json`
- hook デバッグ: `/hook-debugger` skill
- 4 層分類: `docs/adr/0001-hook-four-layer-separation.md`
- philosophy: `docs/adr/0006-hook-philosophy.md`
