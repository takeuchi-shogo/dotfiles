---
source: https://arxiv.org/pdf/2603.24755
title: "SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks"
authors: Gabriel Orlanski et al. (UW-Madison, WSU, MIT)
date: 2026-03-30
status: integrated
---

## Source Summary

### 主張
AIコーディングエージェントは反復的タスクで品質劣化（"slop"）を蓄積する。11モデル×20問題で完全解決ゼロ。プロンプト介入は初期品質（intercept）を改善するが劣化速度（slope）は変わらない。

### 手法
- **SlopCodeBench**: 20問題×93チェックポイント。各チェックポイントで自身の既存コードを拡張する反復タスク
- **Structural Erosion**: 高CC(>10)関数への複雑性集中度。mass(f) = CC(f) × √SLOC(f)
- **Verbosity**: 137個のAST-Grepルール + クローン検出で冗長コードを定量化
- **3つのプロンプト戦略**: just_solve (baseline), anti_slop (冗長禁止), plan_first (計画先行)
- **人間コード比較**: 48 OSS Python リポジトリとの品質比較

### 根拠（データ）
- Erosion: 80%の trajectory で上昇、Verbosity: 89.8%で上昇
- エージェントコードは人間比 2.2x verbose、erosion 0.68 vs 0.31
- 人間コードは時間経過で品質横ばい、エージェントは単調増加で劣化
- anti_slop: 初期 verbosity を 34.5% 削減するが slope は同一。コスト 47.9% 増、パス率改善なし
- Opus 4.6 が最高 strict solve rate 17.2% だが end-to-end 完全解決はゼロ

### 前提条件
- Python track のみで評価（言語非依存設計だが実験はPython）
- 各チェックポイント間でセッションリセット（prior context なし）
- 最小プロンプト（ハーネスの品質戦略に依存）

## 核心的知見

### 1. Slope vs Intercept の分離
プロンプトによる品質指示は**初期品質（intercept）を改善**するが、**反復ごとの劣化速度（slope）は変わらない**。
これは CLAUDE.md の KISS/YAGNI/DRY 原則が「最初の1回」には効くが、5回目、10回目の変更での品質維持には不十分であることを意味する。

### 2. God Function 化パターン
反復的編集の主要失敗モード: 新ロジックが既存関数にパッチされ、focused callable に分割されない。
例: circuit_eval の main() が CC=29→285、84行→1099行に膨張（9つのコマンド分岐が同じ parsing scaffold をコピペ）。

### 3. 初期アーキテクチャ決定の複利効果
C1 でハードコードした言語固有ロジックが C2, C5 で cascading rewrite を引き起こす。
extensible dispatch を選んだエージェントは後続チェックポイントで有利。

### 4. テストスイートは structural decay を検出できない
機能的正確性（pass/fail）は維持されたまま品質が劣化する。
Core テスト合格率は安定、Error/Regression テストで崩壊。

### 5. LLM 固有の冗長パターン
- Identity list comprehension（filter の代わり）
- Single-use 中間変数
- Empty checks instead of building around iteration
- コピペ scaffold（同じ引数パース構造を複数箇所にコピー）
- 構造的 duplication が verbosity 成長の 66% を占める

## Gap Analysis

### Gap / Partial / N/A
| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 劣化 slope 認識 | Gap | 未認識。references/ に codify |
| 2 | LLM固有冗長パターン検出 | Partial | 汎用ルールのみ。LLM固有パターン未定義 |
| 3 | 反復間品質トラッキング | Gap | セッション横断の品質追跡なし |
| 4 | 初期アーキテクチャ拡張性ゲート | Partial | /spec はあるが拡張性評価が明示的でない |
| 5 | 人間コードキャリブレーション | N/A | ベンチマーク手法 |
| 6 | Complexity mass 定量式 | N/A | 既存閾値で十分 |

### Already (強化可能)
| # | 既存 | 強化案 |
|---|------|--------|
| A1 | CLAUDE.md core_principles | code-quality.md に LLM Anti-Slop Patterns 追加 |
| A2 | simplification-rules.md CC>10 | God function 化パターン具体例追加 |
| A3 | /review 並列レビュー | cross-cutting.md に CC-9 Iterative Slop Detection 追加 |
| A4 | Boy Scout Don't | 関数レベル肥大化禁止を明示 |

## Integration Decisions
全項目取り込み（Gap 1-4, 強化 A1-A4）。

## Plan

### Wave 1: Reference + Rules（同一セッション）
1. `references/iterative-degradation-awareness.md` 新規作成 — slope vs intercept 知見
2. `rules/common/code-quality.md` — LLM Anti-Slop + Boy Scout Don't 関数レベル追加
3. `skills/simplify/references/simplification-rules.md` — God function 化パターン + LLM冗長ルール
4. `references/review-checklists/cross-cutting.md` — CC-9 追加

### Wave 2: Skill 強化（同一セッション）
5. `/spec` スキル — 拡張性評価ゲート追加

### Wave 3: トラッキング設計（同一 or 別セッション）
6. 反復間品質トラッキング — golden-check.py or session-learner に品質劣化シグナル検出
