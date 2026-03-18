# Analysis Categories — 判断基準

## errors（エラーパターン分析）

**データソース**: `learnings/errors.jsonl`
**判断基準**:
- 同一エラーが 3回以上 → パターンとして認定
- root_cause フィールドがある場合、根本原因でグルーピング
- 環境固有（PATH, バージョン等）vs コード固有を分類

**改善アクション例**:
- hook 追加で事前検出
- rules/ にパターン追加
- エージェント定義に Symptom-Cause-Fix テーブル追加

## quality（品質違反分析）

**データソース**: `learnings/quality.jsonl`
**判断基準**:
- 違反ルール別に集計、上位5つを重点分析
- トレンド（増加/減少/横ばい）を直近30日で判定
- 新規違反 vs 再発を区別

**改善アクション例**:
- チェックリスト強化
- pre-commit hook でブロック
- Bad Example をルールに併記

## agents（エージェント効率分析）

**データソース**: `metrics/session-metrics.jsonl`
**判断基準**:
- 起動回数 × 成功率でランキング
- 平均所要時間が外れ値のエージェントを検出
- Knowledge Embedding Ratio < 50% → 改善候補

**改善アクション例**:
- エージェント定義にドメイン知識追加
- ルーティング条件の調整
- 不要エージェントの統廃合

## skills（スキル健全性分析）

**データソース**: `learnings/skill-executions.jsonl`, `skill-benchmarks.jsonl`
**判断基準**:
- failure_count >= 3 → degraded
- ベンチマークスコア < 0.8 → needs_improvement
- 30日以上ベンチマーク未実施 → stale

**改善アクション例**:
- SKILL.md のリライト
- テンプレート/references の追加
- --evolve ループで反復改善

## environment（環境設計分析）

**データソース**: 全カテゴリ横断
**判断基準**: Harness Audit Framework の4診断質問
1. アクセス不能な情報はあるか
2. 欠落したフィードバックループはあるか
3. コンテキスト汚染はあるか
4. 機械的に強制すべき制約はあるか

**起動条件**: errors.jsonl 20件以上 かつ 前回分析から7日以上経過
