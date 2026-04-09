---
title: "Skill Evaluation & Self-Improving Loop Analysis"
date: 2026-04-09
source: "External article (text, no URL)"
type: analysis
status: triaged
---

# Skill Evaluation & Self-Improving Loop — 分析レポート

## 記事の要約

スキルの評価と継続的改善に関する実践記事。

**主張**: スキルの「作成」は簡単だが「継続的改善」が本当のエンジニアリング。評価(eval)はハーネスが自動化を構築するための足場。

**手法**:
1. **Trajectory-based evaluation** — 正解率・介入回数・ツールコール数の3メトリクス
2. **4-category improvement taxonomy** — Informational / Failed calls / Command formatting / Architectural info
3. **Self-improving loop** — 実行→評価→フィードバック→改善の連続ループ
4. **Automatic skill evolution** — 退化検出→修正提案→自動更新
5. **Meta-skill** — スキル最適化専用スキル

**根拠**: デバッグスキルが60%→大幅改善。1行の情報追加で failure class 消滅。ルーティング情報で4-5コール→1コール。

## ギャップ分析

### Gap / Partial

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | compute_skill_score() per-skill attribution | **Gap** | skill_name 引数を受け取るがイベントを絞り込んでいない。全スキルに同一セッションスコアが記録されるバグ |
| 2 | スコアスケール統一 (1-10) | **Gap** | session_events.py は 1-10、テストは 0.0-1.0、skill_amender.py は 0.4/0.6 閾値。内部不整合 |
| 3 | per-skill intervention_count | **Partial** | corrections + friction_event_count が存在するが per-skill 帰属と評価式への接続が欠落 |
| 4 | per-skill tool_call_count | **Partial** | tool_calls/related_tools が存在するが効率指標への接続が欠落 |
| 5 | Root-cause taxonomy 実装 | **Partial** | autoevolve-core.md に記述あるが skill_amender.py が edit_instruction に一本化 |
| 6 | Task gap detection | **Partial** | 既存スキル提案のみ。新規スキル提案は「最後の手段」に限定すべき |

### Already (強化可能)

| # | 既存の仕組み | 強化案 |
|---|-------------|--------|
| A | regression-gate.py | 構造チェックのみ → 振る舞い回帰テスト追加 |
| B | contrastive-trace-analyzer.py | 仕様(tool choice/sequence比較)と実装(近傍エラー頻度集計)の乖離修正 |
| C | classify_failure_pattern() | external_env_change カテゴリ追加 + 既存分類の実データ分岐 |
| D | 改善提案 ROI 推定 | informational fix 優先ヒューリスティック追加 |

## セカンドオピニオン

### Codex 批評 (3/5)
- **最重要**: compute_skill_score() の per-skill 帰属が壊れている。これが直らない限りメトリクス追加は無意味
- スコアスケール不整合 (1-10 vs 0.0-1.0)
- regression-gate.py は構造チェックのみで振る舞い回帰を見ていない
- contrastive-trace-analyzer.py は仕様と実装が乖離
- classify_failure_pattern() は edit_instruction 一本化で文書の taxonomy を未実装

### Gemini 補完
- Regression protection は構造チェックのみ（Better Harness も同様の制約）
- コンテキストファイル追加は推論トークン +10-22%
- RL ベースのスキル最適化は個人プロジェクトで ROI 低
- 過適合検出と自動改善ループの不安定性が未解決課題

## Triage 結果

全項目取り込み（8タスク3Wave）。統合プラン: `docs/plans/2026-04-09-skill-eval-improvement-plan.md`
