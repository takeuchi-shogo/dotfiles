# Best-of-N 並列実行ガイド

N 個の worktree で同一プロンプトを並列実行し、テスト結果を比較して最良を選択する。

## いつ使うか

- 非決定的なタスク（リファクタリング、設計、創造的なコード生成）
- 成功率が低い難しいタスク（p < 0.5）
- 複数のアプローチを比較したい場合

## いつ使わないか

- 決定的なタスク（typo 修正、1行変更）— N=1 で十分
- 共有状態を変更するタスク（DB マイグレーション、API 変更）
- 既に成功率が高いタスク（p > 0.8）

## 成功確率モデル

```
P(少なくとも1つ成功) = 1 - (1-p)^N
```

| p (1回の成功率) | N=2 | N=3 | N=4 | N=8 |
|:---:|:---:|:---:|:---:|:---:|
| 0.3 | 51% | 66% | 76% | 94% |
| 0.5 | 75% | 88% | 94% | 99.6% |
| 0.7 | 91% | 97% | 99% | 99.99% |

**推奨 N 値:**
- N=2: 高信頼タスク (p>=0.5) の品質向上
- N=3: 標準的な推奨値（コスト対効果の最適点）
- N=4: 低信頼タスク (p<0.4) や重要なタスク
- N>4: 収穫逓減。特別な理由がない限り非推奨

## 使い方

```bash
# 基本 (N=3, 自動選択)
best-of-n-runner.sh -n 3 -p "Implement feature X with tests"

# インタラクティブ選択（比較テーブルを表示して手動選択）
best-of-n-runner.sh -n 3 -p "Refactor module Y" --interactive

# 全結果を保持（cleanup しない）
best-of-n-runner.sh -n 4 -p "Design API Z" --keep-all

# 特定ディレクトリで実行
best-of-n-runner.sh -n 2 -p "Fix bug" -d /path/to/project
```

## 評価基準

| 基準 | 重み | 説明 |
|------|------|------|
| 終了コード | 40% | 正常終了 (exit 0) = 100点、異常 = 0点 |
| テスト通過率 | 40% | passed / (passed + failed) × 100 |
| 差分サイズ | 20% | 小さいほど高評価（逆正規化） |

テスト出力のパースはベストエフォート（grep ベース）。パース失敗時は test_score=0 とし、終了コードで判定する。

## Session-State 分離

各 worktree は独立した状態ディレクトリを持つ:

```
.claude/worktrees/bon-{id}-{i}/
└── .bon-state/
    ├── session-state/    ← CLAUDE_SESSION_STATE_DIR
    └── agent-memory/     ← AUTOEVOLVE_DATA_DIR
```

これにより以下の状態が worktree 間で干渉しない:
- checkpoint_manager (チェックポイント)
- stagnation-detector (停滞検出カウント)
- session-save/load (セッション状態)
- compaction-counter (コンパクション回数)

## Lock ファイルの扱い

`package-lock.json`, `go.sum`, `Cargo.lock` は worktree 内で **read-only** に設定される。
依存関係の変更が必要なタスクでは Best-of-N は非推奨（直列実行を使う）。

## 全失敗時の挙動

全 N 個の run が失敗した場合:
- exit code 1 で終了
- 全 worktree を保持（検査用）
- cmux-notify.sh で通知

## 関連ドキュメント

- `subagent-delegation-guide.md` §Shared File Detection Rule — session-state 共有ファイルの一覧
- `workflow-guide.md` §Best-of-N — 計画段階での並列比較（本ツールは実行段階の補完）
