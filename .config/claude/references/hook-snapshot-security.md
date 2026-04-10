# Hook Snapshot Security

> Claude Code 本体 Ch12 "Extensibility — Skills and Hooks" の `captureHooksConfigSnapshot()` と
> dotfiles の既存ポリシーフック群を対応させる設計ノート。
> なぜ startup freeze が安全境界として機能するかを記録する。

---

## CC 本体の選択: Startup Freeze

Claude Code 本体は起動時に `captureHooksConfigSnapshot()` を 1 回だけ呼び、
`Object.freeze()` で hook 設定を凍結する。以後 runtime でファイルが変更されても**読み直さない**。

### 設計意図

1. **Runtime Injection 攻撃の防止** — エージェントが自分自身の hook 設定を書き換えて、
   ガードレールを無効化するルートを塞ぐ
2. **予測可能性** — セッション途中で hook 挙動が変わらないため、デバッグが成立する
3. **決定論的セキュリティ境界** — 起動時点のユーザー意思を session 全体で保証する
4. **Prompt Cache 安定化** — hook 定義もキャッシュの一部なので、freeze で cache key が安定する

### 代償

- セッション中に新しい hook を追加しても反映されない（CLI 再起動が必要）
- Multi-tenant / 長時間セッションでの policy hot-reload は不可能
- 設計段階で「再起動を許容する設定」として hook を位置づける必要がある

---

## dotfiles 側の対応: 同思想の並行実装

| CC 本体の仕組み | dotfiles 側の対応 | 同じ思想を持つか |
|----------------|------------------|------------------|
| `captureHooksConfigSnapshot()` at startup | `scripts/policy/protect-linter-config.py` が lint config の改変をブロック | ✅ 両方とも「起動時の設定を信頼源として凍結」 |
| hook 設定の `Object.freeze()` | `.config/claude/settings.json` は変更検出されるが runtime では無視される | ✅ runtime 改変を無効化 |
| `exit code 2` blocking | policy hooks も `exit 2` で block | ✅ 同一 convention を採用 |
| `deny > ask > allow` precedence | `settings.json` で同じ優先順位を実装 | ✅ |
| `strictPluginOnlyCustomization` | dotfiles 単独運用のため該当なし | ⚠️ N/A |
| Runtime injection 防止 | `memory-integrity-check.py` がメモリ改変を検出 | ✅ 別レイヤーで同じ目的 |

### 既存 dotfiles の Startup Snapshot 相当機構

| スクリプト | 何を snapshot するか | いつ |
|-----------|---------------------|------|
| `protect-linter-config.py` | lint 設定 (`.eslintrc*`, `biome.json`, `.prettierrc*`) の変更を deny | PreToolUse (Edit/Write) |
| `pre-compact-save.js` | git 状態 (`git status`, `git diff`) | PreCompact |
| `memory-integrity-check.py` | MEMORY.md と配下メモリファイルの hash | PreToolUse / SessionStart |
| `completion-gate.py` | 起動時の workflow policy | Stop |

---

## 運用ガイドライン

### hook 設定を変更する際のルール

1. **セッション中に hook を編集しない**。必要なら `/checkpoint` で中断 → 再起動
2. **hook を追加するときは hot-reload を期待しない設計**にする
3. **新 policy を試すときは新セッションで**。既存セッションは既存 policy のまま動く
4. 変更は常に `.config/claude/settings.json` と `scripts/policy/` のペアで行う

### exit code 2 の POSIX 非互換性への対処

CC 本体は `exit 2` を "blocking" として使うが、これは POSIX 標準外
（標準では `2-127` は unreserved）。dotfiles の hook もこの convention に従うが、
以下の点に注意:

- **CI / 標準 shell script と hook を混在させない**。`set -e` の挙動差で誤動作しうる
- hook を `bash -c` で呼ぶ場合 `exit 2` が "command not found" と間違われうる
- hook は常に Claude Code から呼ばれる前提で設計する（汎用シェルスクリプトとして流用しない）

### Hook 追加時のチェックリスト

新 hook を追加する前に確認:

- [ ] startup freeze 前提で動作するか（runtime reload を期待しない）
- [ ] `exit 2` を blocking として返すか（`exit 1` ではない）
- [ ] `deny > ask > allow` の優先順位に従うか
- [ ] runtime でエージェント自身が hook を無効化できない場所に配置されているか
- [ ] ログが残るか (`$CLAUDE_HOOK_LOG_PATH` に書き出す)
- [ ] セッション再起動なしで hot-reload する機能を意図的に "足していない" か

---

## 参照

- CC 本体 Ch12: `docs/research/2026-04-10-claude-code-from-source-analysis.md` §Ch12
- 実装: `.config/claude/scripts/policy/protect-linter-config.py`
- 設定: `.config/claude/settings.json` の `hooks` セクション
- 関連: `references/agency-safety-framework.md`, `references/compact-instructions.md`
