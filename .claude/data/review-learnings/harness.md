# harness レビュー観点 (hooks / scripts / settings.json / agents / skills / CLAUDE.md)

用途: `/review` 時に code-reviewer プロンプトへ注入される個人レビュー観点 (harness 実体ファイルの変更に対して)。
更新方法: 過去のレビュー指摘 (`feedback_*.md` / `review-findings.jsonl`) から蒸留。新しい指摘が出たら出典コメント付きで追記する。創作禁止 — trace できない rule は書かない。

## settings.json

- settings.json に hook を追加・変更したら、対象スクリプト名で**全文を grep** して既存呼び出しを確認したか。1 配列だけ見て「ギャップ」と判定すると重複呼び出しになる (Stop/SubagentStop/PostToolUse:Agent/Notification は別 event)。 <!-- source: feedback_settings_json_grep_first.md -->
- 同じ目的の hook を追加する場合、event semantic の差 (Stop vs SubagentStop vs PostToolUse:Agent) を明示的に説明できるか確認する。説明できなければ重複の可能性が高い。 <!-- source: feedback_settings_json_grep_first.md -->
- SessionStart 等の hook を削除する変更は、それに依存する downstream (例: completion-gate の session-aware filter) が壊れないか確認する。hook 削除は parallel-session false-positive を生む。 <!-- source: rf-2026-05-04-001 -->
- `skipAutoPermissionPrompt: true` や `defaultMode: auto` を入れる変更は、file/credential 操作の user 確認をバイパスし権限境界を緩める。multi-agent orchestration 下では特に security boundary を弱める。 <!-- source: rf-2026-05-04-002 / rf-2026-05-03-003 -->
- 外部 GitHub plugin / marketplace を default-enable する変更は、Harness Stability protocol (30 日評価期間) を踏んでいるか確認する。 <!-- source: rf-2026-04-25-001 -->
- marketplace / plugin の命名が既存パターン (`{org}-{descriptor}`) から逸脱していないか確認する。 <!-- source: rf-2026-04-25-002 -->

## shell scripts (bash / zsh)

- zsh script で `local path` / `local status` / `local cdpath` / `fpath` 等の**予約変数**を再宣言していないか。`local path` は PATH array を壊し `command not found` を、`local status` は read-only エラーを起こす。bash では無害なので 3-way レビューでも見逃される。短い別名 (`wp`, `st`) を使う。 <!-- source: feedback_zsh_reserved_vars.md -->
- cron / 自動化 script で `set -e` 下の外部コマンド失敗が、ログ無しで silent に死んで再試行もされない設計になっていないか。`|| { log; exit 0; }` で可視化し、STATE_FILE を未更新にして catch-up 再試行できるようにする。 <!-- source: rf-2026-06-12-001 -->
- subprocess 呼び出しを `check=False` で実行して non-zero exit を正常扱いしていないか。失敗は RuntimeError で raise する。 <!-- source: rf-2026-04-11-003 (brevity-benchmark.py) -->

## hook ロジック (正規表現 / silent failure)

- hook の正規表現が `step:0` や全角数字を許容していないか。`[1-9][0-9]*` 等で意図した範囲に絞る。日本語混じり入力では `\b` 境界が誤動作するので `(?=[^a-zA-Z0-9]|$)` を使う。 <!-- source: rf-2026-04-11-001 (agent-invocation-logger.py) -->
- untrusted input (session_id 等) を path に使う箇所で path traversal を防いでいるか。実機で再現確認する。 <!-- source: rf-2026-05-03-001 -->
- 設定ファイル (trusted-domains.json 等) の fail-open で stderr 警告を出しているか。不在時に黙って fallback すると誤検知ノイズが見えなくなる。 <!-- source: rf-2026-05-06-006 -->
- tool_response が list 型 (Claude content block `[{type:text,text:...}]`) のケースを文字列化ロジックが正しく扱えているか。空文字列扱いすると検出が無効化される。 <!-- source: rf-2026-05-06-001 -->
- 正規表現で保証済みの値に対する try/except が dead code になっていないか。 <!-- source: rf-2026-04-11-002 -->

## 言語選択

- 新規ツールの言語選択で、アプリ規模 (複数モジュール / サブコマンド) なら Go を推奨する。単機能 hook なら Rust も可。判断基準はユーザーのレビュー可能性。 <!-- source: feedback_language_choice.md -->

## CLAUDE.md / 生成物

- CLAUDE.md を直接編集していないか。CLAUDE.md は `templates/claude-md/*.md` からの生成物で、直接編集は lefthook `build-claude-check` が reject する。ソースを編集して再生成する。 <!-- source: feedback_worktree_review_symlink_stale.md -->

## worktree レビュー時の注意 (false positive 防止)

- worktree 内の変更をレビューしているとき、`~/.claude/` symlink 経由で main repo の旧版を読んでいないか。レビュアーの BLOCK/MUST は worktree 実ファイルの該当行を grep で反証してから採否を決める。 <!-- source: feedback_worktree_review_symlink_stale.md -->
