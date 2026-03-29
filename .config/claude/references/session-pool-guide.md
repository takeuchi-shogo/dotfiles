# Session Pool Guide

並列セッション（Agent tool / autonomous / worktree）の運用ガイドライン。

## 推奨並列数

| タスク規模 | 推奨セッション数 | 根拠 |
|-----------|----------------|------|
| S（1ファイル変更） | 1-2 | オーバーヘッドが利益を上回る |
| M（2-5ファイル） | 3-5 | レビュー並列化で効果的 |
| L（6ファイル超） | 5-10 | worktree 隔離で conflict 回避 |

## リソース考慮事項

### API Rate Limit
- Claude API の rate limit を考慮し、同時セッション数を制限
- Codex/Gemini CLI 併用時は各モデルの rate limit も考慮
- 目安: 並列エージェント数 ≤ 10（rate limit headroom を確保）

### ローカルリソース
- 各 worktree は ~50-200MB のディスクを消費（リポジトリサイズ依存）
- Bash 実行を含むエージェントはCPU/メモリを消費
- `autonomous` の長時間実行時はリソース監視を推奨

### Context Window
- 親セッションの context も消費される（エージェント結果の受信）
- 10+ エージェントの結果を同時受信すると context 圧迫のリスク
- 対策: `run_in_background: true` で非同期受信、結果は要約のみ返す

## Conflict 回避パターン

### Worktree 隔離（推奨）
- `isolation: "worktree"` で Agent tool を呼び出す
- 各エージェントが独立したファイルシステムで動作
- merge は親セッションが制御

### ファイル分割
- 同一ファイルを複数エージェントが編集しない
- Task 分解時にファイル境界でタスクを分割
- 共有ファイル（CLAUDE.md 等）への書き込みは直列化

### Lock 機構
- `autonomous` の `run.lock` で排他制御
- 同一ディレクトリへの並列書き込みを防止

## /autonomous での並列セッション

`/autonomous` スキルで max_sessions を決定する際の基準:

1. **タスクの独立性**: 共有状態がないタスクのみ並列化
2. **タスク粒度**: 1タスク = 1セッションで完結する粒度に分解
3. **merge コスト**: 並列数が増えるほど merge conflict リスクが上昇
4. **推奨**: まず 3-5 並列で開始し、問題なければ増やす

## ベストプラクティス

1. **Small batch, fast feedback**: 大量並列より、小バッチ→検証→次バッチ
2. **Worktree cleanup**: 完了した worktree は速やかに削除（`.claude/worktrees/`）
3. **Progress monitoring**: `autonomous` の `progress.md` で進捗追跡
4. **Graceful degradation**: エージェントが失敗しても他に影響しない設計
5. **結果の検証**: 並列実行結果は必ず統合後にレビュー（`/review`）
