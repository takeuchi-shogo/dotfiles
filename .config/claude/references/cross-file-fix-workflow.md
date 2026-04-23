---
status: reference
last_reviewed: 2026-04-23
---

# Cross-File Fix Workflow

cross-file-reviewer の FIX モードで使用する修正ワークフロー。

## 修正対象の判断基準

| 深刻度 | アクション |
|--------|-----------|
| CRITICAL | 自動修正（コンパイルエラー/ランタイムエラー） |
| HIGH | 自動修正（実行時問題） |
| MEDIUM | 報告のみ — 修正はユーザー判断 |
| LOW | 報告のみ |

## 修正前の安全策

1. **worktree 分離**（推奨）: `isolation: worktree` で起動されている場合はそのまま修正
2. **git stash**: worktree でない場合、修正前に `git stash push -m "pre-cross-file-fix"` で現状を保存
3. **差分確認**: 修正対象ファイルの現在の差分を `git diff` で確認し、未コミットの変更と衝突しないか検証

## 修正手順

1. 指摘リストを深刻度順（CRITICAL → HIGH）でソート
2. 各指摘について:
   a. 対象ファイルを Read で確認
   b. 変更が他の箇所に波及しないか Grep で検証
   c. Edit で最小限の修正を適用
3. 全修正完了後、lint/test を実行して副作用がないか確認:
   ```bash
   # プロジェクトの lint コマンド（あれば）
   ${LINT_CMD:-true}
   # プロジェクトのテストコマンド（あれば）
   ${TEST_CMD:-true}
   ```

## 修正後の必須検証

- [ ] lint がパスすること
- [ ] 既存テストが全てパスすること
- [ ] 修正が指摘内容と正確に対応していること（過剰修正しない）
- [ ] 新たなファイル間不整合が発生していないこと

## ロールバック手順

修正後にテストが失敗した場合:

```bash
# worktree の場合: worktree を破棄
git worktree remove <worktree-path> --force

# stash の場合: stash を復元
git checkout -- .
git stash pop
```

## 制約

- FIX モードはレビューフェーズ完了後にのみ使用可能
- 1回の FIX セッションで修正するファイル数は最大 10 ファイル
- 修正内容はレビュー指摘に直接対応するもののみ（追加の改善は行わない）
