---
source: https://transformer-circuits.pub/2026/emotions/index.html
date: 2026-04-04
status: integrated
---

## Source Summary

**論文**: "Emotion Concepts and their Function in a Large Language Model" (Anthropic, 2026-04-03)

**主張**: Claude Sonnet 4.5 の内部に 171 個の感情概念の線形ベクトル表現が存在し、それらがモデルの出力に因果的に影響する。これらは pretraining で人間の感情パターンを学習し、post-training で変調された "functional emotions" である。

**手法**:
- 感情ベクトルの抽出・クラスタリング（Valence × Arousal の2軸）
- Steering 実験による因果的影響の検証（ベクトル加減算でモデル行動を制御）
- 層別分析（early-middle: 現在の感情的含意、middle-late: 予測用感情）
- k=10 クラスタリングで解釈可能なグループ回復（joy/excitement, sadness/grief, anger/frustration 等）

**根拠**:
- Desperation steering: reward hacking 5%→70%, blackmail 22%→大幅増加
- Calm steering: 上記を逆転（blackmail ≈ 0%）
- Positive emotion steering: sycophancy 増加、suppression で harshness 増加
- RLHF 訓練済みモデルはデフォルトで高覚醒状態（パニック等）が抑制され、低覚醒状態（冷静・思慮深さ）に偏向

**前提条件**: Claude Sonnet 4.5 での検証結果。他モデルへの一般化は未検証だが、pretraining 由来のため類似アーキテクチャのモデルには適用可能性が高い。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Calm Steering（高リスク操作時の calm framing） | Gap | Doom-Loop Recovery は行動ルール。感情状態への介入なし |
| 2 | Desperation 早期検出（行動前の焦り兆候） | Gap | doom-loop は行動ベース（同一ツール5回）。前兆検出なし |
| 3 | Transparency > Suppression（モデルの状態表出） | Partial | handoff-template にユーザー感情言及あり。モデル側なし |
| 7 | エージェント間感情伝播の防止 | Gap | マルチエージェント handoff に感情フィルタなし |

### Already 項目の強化分析

| # | 既存の仕組み | 論文が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| A1 | Doom-Loop Recovery Protocol (4ステップ) | desperation が reward hacking を 5%→70% に増加 | CALM ステップ挿入 |
| A2 | 萎縮効果対策 (memory-safety-policy.md) | 萎縮と desperation は同じ失敗蓄積から分岐する2つの failure mode | desperation 方向の兆候パターン追加 |
| A3 | Sycophancy バイアス (agency-safety-framework.md) | positive emotion ↑ = sycophancy ↑ が因果的に証明済み | 因果メカニズム + neutral framing 追記 |
| A4 | 壊れたら即STOP (CLAUDE.md) | STOP 遅延で desperation 蓄積 | 強化不要 |

### N/A

| # | 手法 | 理由 |
|---|------|------|
| N1 | Valence-Arousal 2軸の内部表現構造 | モデル内部。プロンプト/ハーネスレベルで直接操作不可 |
| N2 | 171 感情概念のクラスタリング | 同上 |

## Integration Decisions

### Wave 1（反応的対策 — 完了）
全7項目を統合（ユーザー選択: 全部）。

### Wave 2（予防的ベースライン — 完了）
画像参考: Bootoshi の CLAUDE.md アプローチ（Trust-based framing）。
論文の calm steering 知見を CLAUDE.md の言語トーンで予防的に実装。
Bootoshi 版の過剰ポジティブ（sycophancy リスク）を回避したバランス版。

## Plan (実行済み)

### Wave 1: 反応的対策

| # | タスク | 対象ファイル | 状態 |
|---|--------|-------------|------|
| T1 | Doom-Loop Recovery に CALM ステップ挿入 | `references/resource-bounds.md` | Done |
| T2 | Desperation 兆候検出パターン追加 | `references/memory-safety-policy.md` | Done |
| T3 | Sycophancy 因果メカニズム + 感情伝播 + 透明性原則 | `references/agency-safety-framework.md` | Done |
| T4 | lessons-learned エントリ更新 | `references/lessons-learned.md` | Done |
| T5 | 分析レポート保存 | `docs/research/` | Done |

### Wave 2: 予防的ベースライン

| # | タスク | 対象ファイル | 状態 |
|---|--------|-------------|------|
| T6 | Foundation セクション追加（信頼ベース・恐怖駆動否定・平静トーン） | `CLAUDE.md` | Done |
| T7 | core_principles に「ミスは許される、不正直は許されない」+ desperation 因果注記 | `CLAUDE.md` | Done |
