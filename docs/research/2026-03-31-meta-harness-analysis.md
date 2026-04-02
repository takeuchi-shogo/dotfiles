---
source: https://arxiv.org/abs/2603.28052
date: 2026-03-31
updated: 2026-04-03
status: integrated
---

# Meta-Harness: End-to-End Optimization of Model Harnesses

## Source Summary

**著者**: Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, Omar Khattab, Chelsea Finn
**主張**: LLMの性能はハーネス（モデルを包むコード）で決まり、その最適化は自動化できる。圧縮フィードバックではなくファイルシステム経由の生トレースへの選択的アクセスが鍵。

### 手法
- **Meta-Harness システム**: エージェント型 Proposer（Claude Code + Opus 4.6）が過去の全候補のソースコード・スコア・実行トレースに FS 経由でアクセスし、ハーネスコードを自動探索
- **FS ベース履歴**: 各候補のコード・評価スコア・完全な実行トレースをファイルシステムに保存。Proposer は grep/cat で選択的に調査（中央値82ファイル/回、20以上の過去候補を参照）
- **Pareto frontier 探索**: 精度・コスト等の多目的 tradeoff curve 上の複数候補を維持
- **コード空間探索**: プロンプトテキストではなく、検索・メモリ・プロンプト構築のコードレベルで探索

### 根拠（実験結果）
- **オンライン文章分類**: SoTA (ACE) を +7.7pt 上回り、コンテキスト消費は 1/4。未知の9データセットにも汎化 (+2.9pt)
- **検索拡張数学推論**: IMOレベル200問で +4.7pt（5モデル平均）。単一ハーネスが5つの異なるモデルに転移
- **エージェント型コーディング**: TerminalBench-2 で Opus 4.6 #2, Haiku 4.5 #1

### 重要アブレーション
| Proposer への情報 | 中央値精度 | 最高精度 |
|---|---|---|
| スコアのみ | 34.6 | 41.3 |
| スコア + 要約 | 34.9 | 38.7 |
| **フル（トレース含む）** | **50.0** | **56.7** |

**要約を入れると逆に性能が下がる**。生トレースへの直接アクセスが決定的に重要。

### 前提条件
- 強力なコーディングエージェント（Claude Code + Opus 4.6）が Proposer として必要
- 評価1回で最大1000万トークンの診断情報（既存手法の1000倍スケール）

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | セッション実行トレースの raw 保存 + FS アクセス | **Partial** | experiment_tracker.py が仮説・スコアを記録、session-learner.py がイベント抽出。だが全プロンプト・全ツール呼び出し・全出力の raw 保存 + Proposer の FS 経由選択的アクセスはない |
| 2 | Pareto frontier 維持（精度 vs コスト） | **Gap** | best-of-n-guide.md は単一目的の並列探索。多目的 Pareto frontier 維持なし |
| 3 | 環境ブートストラップ（System Snapshot） | **Gap** | statusline.sh は表示用。セッション開始時の環境スナップショット注入なし |

### Already 項目の強化分析

| # | 既存の仕組み | 論文が示す弱点/知見 | 強化案 |
|---|---|---|---|
| A1 | AutoEvolve Proposer (improve-policy.md ルール13: H 注入 20件上限+60日超サマリー化) | Proposer が82ファイル/回読み因果推論。サマリー化は性能を下げる | H 注入方式を FS 保持 + 選択的アクセスに変更 |
| A2 | 「生データ優先のデバッグ」原則 (CLAUDE.md) | 要約を入れると性能が下がる (50.0→34.9)。原則は正しいが AutoEvolve の H 注入で矛盾 | A1 と同時に矛盾解消 |
| A3 | cross-model-insights.md + Scaffolding > Model 原則 | 単一ハーネスが5モデルに転移 +4.7pt | スキル改善 A/B テストに cross-model 検証ステップ追加 |
| A4 | confound 検出・ドリフトガード (gaming-detector.py, 単一変更規律) | 論文 Proposer も同様のパターンを発見 | **強化不要** — 既に十分 |
| A5 | harness-rationale.md (Morph 22:1 比率) | 同一モデルで 6x 性能差 | 6x 根拠を Morph 22:1 と並記 |

## Integration Decisions

### 選択された項目
- **Gap/Partial 全件**: #1 トレース raw 保存、#2 Pareto frontier、#3 環境ブートストラップ
- **強化**: A1 + A2 (H注入方式見直し)、A3 (cross-model検証)、A5 (rationale追記)

## Plan

7タスク、3 Wave。詳細は `docs/plans/2026-03-31-meta-harness-integration.md` 参照。

| Wave | # | タスク | 規模 |
|------|---|--------|------|
| 1 | T1 | 実行トレース raw 保存の設計 | M |
| 1 | T2 | improve-policy H 注入方式見直し | S |
| 2 | T3 | 環境ブートストラップ hook | M |
| 2 | T4 | Pareto frontier の best-of-n 拡張 | S |
| 3 | T5 | cross-model 検証プロトコル | S |
| 3 | T6 | harness-rationale 6x 根拠追記 | S |
| 3 | T7 | 分析レポート + MEMORY.md 更新 | S |

## Supplemental Integration (2026-04-03)

Neural AVB ブログ記事 "Meta-Harness - Automated model harness optimization" の差分統合。
論文自体は 03-31 に統合済み。ブログ記事の popularized 解説から追加で6項目を取り込み。

### 追加統合項目

| # | タスク | ファイル | 内容 |
|---|--------|---------|------|
| S1 | Skill 精錬ステップ | `skills/skill-creator/SKILL.md` | Step 2.5 追加: 3-5回のデバッグランで Skill テキスト精錬 |
| S2 | 苦戦ベースライン | `skills/spike/SKILL.md` | Step 4 にベースライン選定原則追加 |
| S3 | CLI-over-Logs | `references/improve-policy.md` | Rule 38: 構造化クエリでトレース探索 |
| S4 | Warm-starts | `references/situation-strategy-map.md` | 外部経験の構造化取り込みセクション追加 |
| S5 | MH vs DGM-H 対比 | `references/cross-model-insights.md` | 探索戦略比較テーブル追加 |
| S6 | 評価の外出し | `references/improve-policy.md` | Rule 39: Critic-Refiner 外部化強化 |
