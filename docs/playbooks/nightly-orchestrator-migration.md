# Nightly Orchestrator 移行 playbook

## 切替（ビルド先行で空白期間を作らない）
1. `cd tools/nightly-orchestrator && go build -o nightly-orchestrator .` ← **ビルド成功を必ず先に確認**
2. `./nightly-orchestrator --dry-run` で計画を確認
3. `bash scripts/runtime/nightly/launchd-uninstall.sh`（旧 11 エントリ削除）
4. `task nightly:install`（caffeinate + orchestrator。内部で再ビルド）

**重要**: 1 でビルドが通らなければ 3 に進まない。先に uninstall すると、ビルド失敗時に
その夜のバッチが caffeinate 以外 1 本も起動しない空白が生じる（Gemini 指摘）。

## Rollback（orchestrator に問題が出た夜の翌日）
旧個別 plist 方式に戻す:
1. `launchctl unload ~/Library/LaunchAgents/com.user.nightly.orchestrator.plist && rm 同ファイル`
2. launchd commit を revert: `git revert <Task 9: launchd orchestrator 化 commit>`
3. `task nightly:install`（旧 11 エントリが復活）

**lib 変更（Task 5）は revert 不要**: `NIGHTLY_ORCHESTRATED` 未設定の旧 launchd 直叩きでは
lock/fail-count は従来動作（後方互換）、JSONL lock は単一プロセスで即取得＝無害。偽成功検出のみ
常時有効だが望ましい改善なので残す。完全に旧 lib へ戻す場合のみ Task 5 commit も revert する
（半移行状態でも壊れない設計だが、挙動を完全一致させたいとき）。

## 緊急停止（その夜だけ止める）
`touch ~/.claude/agent-memory/LOOP_DISABLED`
→ orchestrator は全ジョブ skip し「LOOP_DISABLED」サマリを Discord に送る。
解除: `rm ~/.claude/agent-memory/LOOP_DISABLED`

## 既知の注意
- 1 晩並走は不可（JSONL / last-run / lock 共有のため二重実行になる）
- orchestrator は go バイナリ。コード変更後は `task nightly:install` で再ビルドが必要
- 切替は必ず「ビルド成功確認 → uninstall → install」の順
