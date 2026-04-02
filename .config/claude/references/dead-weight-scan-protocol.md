# Dead Weight Scan Protocol

> 「何をやめられるか？」を定期的に問う棚卸しチェックリスト。
> 出典: Anthropic "Harnessing Claude's Intelligence" (2026-04-02) — モデル進化に伴い、過去に有効だった指示が dead weight 化する。

## トリガー

- `/improve` の Step 5 陳腐化チェック（自動）
- モデルアップグレード後の初回セッション（手動推奨）
- CLAUDE.md が 150 行を超えた場合（check-claudemd-lines.sh で検知）

## スキャン対象と問い

### 1. CLAUDE.md の `<important if>` ブロック

各ブロックについて:
- この条件分岐は現行モデルでまだ必要か？（モデルがデフォルトで守る動作ではないか）
- 過去のインシデント起因の指示なら、そのインシデントはまだ再現しうるか？

### 2. Compaction / Context 管理ルール

- compaction fallback の閾値はモデル能力に見合っているか？
- context anxiety 対策（reset, checkpoint 頻度）は過剰ではないか？

### 3. references/ のルール・チェックリスト

- 統合済み記事由来のルールで、現行モデルが自然に守るものはないか？
- 3ヶ月以上参照されていない reference は本当に必要か？

### 4. hooks / scripts

- policy hook が防いでいるミスを現行モデルはまだ犯すか？
- hook の正規表現が過剰にマッチして false positive を出していないか？

### 5. エージェント定義

- サブエージェントの指示で、現行モデルに不要な「当たり前」の指示はないか？
- 古いモデル向けの workaround（冗長な例示、ステップバイステップ強制）が残っていないか？

## 判定基準

| 判定 | アクション |
|------|----------|
| **Dead weight** | 削除。commit message に理由を記録 |
| **Possibly stale** | 1セッション無効化して副作用を観察。問題なければ削除 |
| **Still needed** | 維持。次回スキャン時に再評価 |

## Anti-Patterns

- 「念のため残す」は dead weight を増やす最大の原因。判断に迷ったら `Possibly stale` として実験
- 一度に大量削除しない。1サイクル最大 5 項目の除去に制限
- 削除時は git で追跡可能にし、必要なら `git revert` で復元できるようにする
