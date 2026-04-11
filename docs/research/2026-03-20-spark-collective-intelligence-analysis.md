---
source: "Spark: self-improving agents meeting collective intelligence (spark.xyz blog)"
date: 2026-03-20
status: analyzed
---

## Source Summary

**主張**: Skills/Custom Instructions は AI を「一貫性のある」ものにするが「熟達」には至らない。Spark は仮説検証→測定→昇格→共有の再帰ループで、エージェントにドメイン専門性を自律的に獲得させる。

**手法**:
1. 再帰的自己改善ループ (6段階): Try → Measure → Record → Promote → Share → Human Review
2. 知識ピラミッド (4層): Raw Outcomes → Exploratory Frontier (>=0.66) → Benchmark Evidence (>=0.72) → Doctrine
3. Domain Chip (プラガブル専門性モジュール): evaluate, suggest, packets, watchtower インターフェース
4. 1変数テスト: 1回の試行で1つだけ変更し因果帰属を明確化
5. 矛盾マッピング: 相反するアドバイスを文脈別にスコアリングし境界条件を特定
6. エビデンス付き自己編集: 3質問 (何を解決/どう測定/壊れたら?) + 回帰チェック
7. 4段階ガバナンス: Observe Only → Review Required → Checked Auto-Merge → Trusted Auto-Apply
8. 集合知 (Swarm): エージェント間で検証済み知見をカプセル化して共有

**根拠**: 3000+ソースから225パケット→142ベンチマーク通過→47候補→23 Doctrine (99.2%フィルタリング率)

**前提条件**: ベンチマークスイートが存在すること、繰り返し測定可能なドメインであること

## Gap Analysis

| # | Spark の手法 | 判定 | 既存実装 / 差分 |
|---|-------------|------|----------------|
| 1 | 再帰的自己改善ループ | Already | AutoEvolve 4層 + EvoSkill --evolve |
| 2 | 知識ピラミッド (4層) | Partial | learnings.jsonl→rules/references 昇格あり。スコア閾値付き段階的昇格パイプラインなし |
| 3 | Domain Chip | Partial | skill-archetype あり。evaluate/watchtower 標準化なし |
| 4 | 1変数テスト | Already | autoresearch --single-change + Rule 17-19 |
| 5 | 矛盾マッピング | Gap | 矛盾検出メカニズムなし。相反 learnings は後勝ち |
| 6 | エビデンス付き自己編集 | Partial | emit_proposal_verdict() + ドリフトガード。3質問フレームワーク未形式化 |
| 7 | 4段階ガバナンス | Partial | binary (review required or not)。信頼度ベース段階的自律性なし |
| 8 | 集合知 (Swarm) | N/A | 単一ユーザー dotfiles。クロスプロジェクト共有として再解釈可能だが優先度低 |
| 9 | 不変台帳 | Already | learnings/*.jsonl + strategy-outcomes.jsonl |
| 10 | 戦略競争可視化 | Partial | strategy-outcomes.jsonl あり。ランキング可視化なし |
| 11 | 99.2% フィルタリング | Partial | gaming-detector + quality gate。段階通過率計測なし |

## Integration Decisions

取り込み対象 (ユーザー選択):
- **#2 知識ピラミッド** — 4層昇格パイプライン
- **#5 矛盾マッピング** — 相反 learnings の境界条件特定
- **#6 自己編集3質問** — improve 提案時の構造化チェック
- **#7 段階的ガバナンス** — 4段階自律性レベル

スキップ:
- #1, #4, #9: Already 実装済み
- #3: Domain Chip は skill-archetype で十分。標準化は過剰設計
- #8: 単一ユーザー環境では N/A
- #10, #11: Nice-to-have だが優先度低

## Plan

→ `docs/plans/2026-03-20-spark-integration.md` 参照
