---
source: https://arxiv.org/abs/2603.29848
date: 2026-04-02
status: integrated
---

## Source Summary

**AgentFixer: From Failure Detection to Fix Recommendations in LLM Agentic Systems**
Mulian, Zeltyn, Levy, Galanti, Yaeli, Shlomov (IBM, 2026-02)

LLM エージェントシステムの包括的バリデーションフレームワーク。15 診断ツール + 2 根本原因分析モジュールで構成。ルールベースチェックと LLM-as-a-Judge を組み合わせ、入力/プロンプト/出力の弱点を体系的に検出。

- パース関連障害が全障害の **38%**
- 64-88% の LLM コールで軽微な違反を検出（単体では無害だが累積で信頼性劣化）
- プロンプト改善で Llama 4 (+8%), Mistral (+7%) がフロンティアモデルとの差を縮小
- GPT-4o の成功ケース 93% を保持しつつ 10 タスクを回復
- Trace 比較ツールが 46.2% のケースで根本原因特定に優位

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 15 診断ツール体系 | Partial | failure-taxonomy.md に FM-001-020 あり。サブエージェント出力バリデーション未実装 |
| 2 | カスケードパース戦略 | Gap | パースエラー時のフォールバック機構なし |
| 3 | Trace 比較ツール | Partial | session-trace-store.py で raw 保存あり。対比分析機能なし |
| 4 | Criticality 分類 | Partial | autoFixable フラグあり。severity レベル未定義 |
| 5 | プロンプトリファインメント | N/A | skill/agent 定義ベースのため文脈が異なる |
| 6 | Interactive HTML ダッシュボード | N/A | 運用不要 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|---|---|---|
| A1 | failure-taxonomy.md | パース関連 FM なし | FM-021 追加 |
| A2 | 2パスレビュー | 軽微な違反の累積を見逃す | minor violation 累積パターン警告 |
| A3 | review-consensus-policy.md | — | 強化不要 |

## Integration Decisions

全5項目を取り込み:

1. FM-021: Output Parse Failure → `failure-taxonomy.md`
2. カスケードパース戦略 → `references/cascade-parse-strategy.md`（新規）
3. Severity 分類（Critical/Moderate/Minor） → `failure-taxonomy.md`
4. Trace 対比分析 → `failure-taxonomy.md` 運用セクション
5. Minor violation 累積パターン警告 → `agents/code-reviewer.md`

## Plan (実行済み)

| # | タスク | ファイル | 状態 |
|---|--------|---------|------|
| T1 | FM-021 + severity + trace 対比 | `references/failure-taxonomy.md` | done |
| T2 | カスケードパース戦略 | `references/cascade-parse-strategy.md` | done |
| T3 | Minor violation 累積警告 | `agents/code-reviewer.md` | done |
