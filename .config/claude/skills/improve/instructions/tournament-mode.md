# Tournament Mode

> 複数の改善戦略を並列実行し、スコア比較で最適解を選定する。
> `/improve --tournament` で手動起動、または CQS Stagnant 時に自動提案。

## トリガー

| 条件 | 発動 |
|------|------|
| `/improve --tournament` | 手動起動 |
| CQS 0.0-2.0 AND 前回 improve が neutral | 自動提案（ユーザー確認後に実行） |

## フロー

### Step 1: 戦略生成

改善対象に対して 2-3 の異なるアプローチを生成する:

- **Approach A (Conservative)**: 既存パターンの延長。小さな修正
- **Approach B (Innovative)**: 新パターン導入。構造的な変更
- **Approach C (Hybrid)**: A と B の折衷（任意）

各アプローチは以下を含む:
- 仮説: 何を変えると何が改善するか
- 変更対象ファイル（最大3ファイル/variant）
- 期待される効果

### Step 2: 並列実行

各アプローチを独立 worktree で実装する。

```bash
# Approach A
git worktree add /tmp/tournament-a -b tournament/a
# Approach B
git worktree add /tmp/tournament-b -b tournament/b
```

各 worktree で:
1. 実装
2. テスト実行（`uv run pytest tests/`）
3. レビュースコア取得（code-reviewer を実行）

### Step 3: スコア比較

`references/review-dimensions.md` の5次元スコアで比較する。

```
weighted_score = Σ(dimension_score × weight)
```

判定:
- 加重平均スコアが最高のバリアントを勝者とする
- 差が 0.5 未満の場合は Conservative を優先（KISS 原則）
- テスト失敗のバリアントは自動除外

### Step 4: 勝者マージ

1. 勝者の worktree ブランチを `autoevolve/` ブランチにリネーム
2. 敗者の worktree を削除（`git worktree remove`）
3. 通常の improve フロー（ユーザーレビュー→merge）に接続

## 制約

- 最大 3 バリアント（トークンコスト制御）
- 各バリアント最大 10 ターン
- tournament は 1 改善サイクルにつき最大 1 回
- improve-policy.md の全安全ルールを各バリアントに適用
- worktree 内でも master 直接変更禁止

## レポート出力

```markdown
## Tournament Result

| Approach | Hypothesis | Test | Score | Winner |
|----------|-----------|------|-------|--------|
| A (Conservative) | ... | PASS | 4.2 | |
| B (Innovative) | ... | PASS | 4.5 | ★ |

### Score Breakdown (Winner: B)
correctness: 5/5, security: 4/5, maintainability: 4/5
performance: 5/5, consistency: 4/5
weakest: security

### Decision
B selected: score delta +0.3 (above 0.5 threshold)
```
