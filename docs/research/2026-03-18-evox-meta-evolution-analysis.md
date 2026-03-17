---
source: https://arxiv.org/abs/2602.23413
date: 2026-03-18
status: analyzed
---

## Source Summary

**EvoX: Meta-Evolution for Automated Discovery** (UC Berkeley, Stanford, Bespoke Labs)

- **主張**: LLM駆動の進化的探索において、解候補だけでなく「探索戦略自体」も進化させる二重ループ（メタ進化）により、固定戦略の停滞を突破する
- **手法**:
  1. 二重ループ共進化: 内側（解の進化）+ 外側（戦略の進化）
  2. 停滞検知による demand-driven 戦略切替（閾値τ、スライディングウィンドウW）
  3. Population State Descriptor φ(D): スコア統計 + フロンティア構造 + 進捗指標 + 直近ウィンドウ統計
  4. 戦略データベース H: 過去戦略の (戦略, 状態, パフォーマンス) を記録し条件付き推論
  5. 3種の変異オペレータ: local refinement / structural variation / free-form variation
  6. 戦略バリデーション: デプロイ前に新戦略を検証
- **根拠**: ~200タスク（数学最適化8, システム最適化6, アルゴリズム172+10）で AlphaEvolve, OpenEvolve, GEPA, ShinkaEvolve を上回る
- **前提条件**: 100回程度の反復最適化を前提。評価関数が明確に定義可能なタスク

## Gap Analysis

| # | EvoX 手法 | 判定 | 現状 | 差分 |
|---|----------|------|------|------|
| 1 | 二重ループ共進化 | N/A | Claude Code のタスクは通常1-5回試行で完了。フルのメタ進化ループは過剰 | — |
| 2 | 停滞検知 → 戦略切替 | Partial | error-to-codex.py（エラー反応型）、CFS検出あり。停滞閾値τは未実装 | エラー反応型→停滞予防型への進化 |
| 3 | Population State Descriptor | Partial | context-monitor.py、session-learner.py で個別メトリクスあり。統合ディスクリプタなし | メトリクス統合層が欠如 |
| 4 | 戦略データベース H | Partial | learnings/*.jsonl に what-happened は記録。which-strategy-worked は未記録 | 戦略有効性の記録が欠如 |
| 5 | 変異オペレータの適応的選択 | Partial | improve-policy.md に分類あり。進捗に応じた動的選択なし | 分類あり、動的選択なし |
| 6 | 戦略バリデーション | Already | completion-gate.py, golden-check.py, A/B testing で十分 | — |
| 7 | スライディングウィンドウ進捗監視 | Gap | セッション単位のみ。タスク内反復での進捗停滞の定量化なし | — |
| 8 | コスト効率最適化 | Already | マルチモデル連携で用途別使い分け済み | — |

## Integration Decisions

- **A: 停滞検知 → 戦略切替** → 取り込み（高優先）
- **B: 戦略有効性データベース** → 取り込み（中優先）
- **C: 変異オペレータの適応的選択** → 取り込み（中優先）
- **D: 統合状態ディスクリプタ** → 取り込み（低優先）
- **E: タスク内メタ進化ループ** → スキップ（N/A: Claude Code のタスク粒度に合わない）

## Plan

### Task A: 停滞検知 → 戦略切替フック (stagnation-detector.py)

**場所**: `.config/claude/scripts/policy/stagnation-detector.py`
**トリガー**: PostToolUse (Bash) — error-to-codex.py と同フック、ただし異なる視点
**ロジック**:
1. セッション内の直近 N 回の Bash 実行を追跡（state file で管理）
2. 連続失敗回数・同一コマンド再実行・スコア改善なし をカウント
3. 閾値超過時に戦略切替を提案:
   - 連続3回同種エラー → "structural variation を試行してください（別アプローチ検討）"
   - 連続5回失敗 → "codex-debugger で根本原因分析を推奨"
   - 同一ファイルへの編集が5回超 → "設計の見直しを検討（refinement 限界）"
4. EvoX の demand-driven パターン: 進捗がある間は介入しない

**依存**: session_events.py の emit_event、hook_utils

### Task B: 戦略有効性データベース (strategy-outcomes.jsonl)

**場所**: `~/.claude/agent-memory/learnings/strategy-outcomes.jsonl`
**スキーマ**:
```json
{
  "timestamp": "ISO8601",
  "project": "string",
  "task_type": "debug|implement|refactor|investigate",
  "approach": "refinement|structural|exploratory|codex-deep|gemini-research",
  "context": {
    "error_type": "string|null",
    "consecutive_failures": 0,
    "files_touched": 3
  },
  "outcome": "success|partial|failure",
  "improvement_delta": 0.0,
  "notes": "string"
}
```
**記録タイミング**: session-learner.py のセッション終了時に、アプローチ分類を推論して記録

### Task C: 変異オペレータの適応的選択ガイド

**場所**: `.config/claude/references/variation-operators.md`
**内容**: EvoX の Signal Processing ケーススタディから抽出した段階的切替パターン:
- **初期（探索フェーズ）**: free-form variation — 幅広いアプローチを試す
- **中盤（構造変更フェーズ）**: structural variation — 有効だったパターンの組み合わせ
- **終盤（洗練フェーズ）**: local refinement — 微調整で最終品質を上げる
- **停滞時**: 現フェーズの1段階上に戻る（refinement→structural、structural→free-form）

**適用先**: stagnation-detector.py の提案メッセージに組み込み

### Task D: 統合状態ディスクリプタ

**場所**: session_events.py に `build_state_descriptor()` 関数を追加
**内容**:
```python
def build_state_descriptor() -> dict:
    """EvoX の φ(D) に相当する統合状態要約"""
    return {
        "score_stats": {"best": ..., "recent_mean": ..., "spread": ...},
        "progress": {"steps_since_improvement": ..., "improvement_rate": ...},
        "diversity": {"unique_approaches": ..., "files_touched": ...},
        "context_pressure": {"used_pct": ..., "remaining_budget": ...},
    }
```
**用途**: stagnation-detector.py と session-learner.py が参照。戦略切替の判断材料
