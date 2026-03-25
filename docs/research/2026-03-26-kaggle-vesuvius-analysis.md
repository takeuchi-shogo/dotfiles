---
source: https://blog.recruit.co.jp/data/articles/kaggle_vesvius/
date: 2026-03-26
status: integrated
---

## Source Summary

Recruit Data Blog の羽鳥冬星氏による Kaggle ヴェスヴィオ・チャレンジ（古代巻物CTスキャンの3Dセグメンテーション）12位金メダルの振り返り。

**主張**: fullres + lowres のアンサンブルと超 long epoch training（4000ep）で金メダル獲得。Claude Code の Skills 機能を活用することで Kaggle ワークフローの定型タスクを自動化し、開発効率を向上。

**手法**:
1. nnUNet ベースの3Dセグメンテーション
2. 4モデルアンサンブル（fullres 60% + lowres 40%）
3. TTA（8方向ミラーリング）+ ヒステリシス閾値 + Opening/Closing
4. Claude Code Skills: submit監視、推論効率レビュー、ディスカッション整形、notebook一括DL
5. 「暗黙の前提」のズレを skill 化で解消するパターン

**根拠**: Private LB 0.552 → 0.613 へ改善。上位チームも同様の long epoch 戦略を採用（1位: 4000ep、3位: 8000ep）。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Kaggle submit 監視 skill | Gap | Kaggle API 統合なし |
| 2 | Kaggle 推論効率レビュー skill | Gap | `/review` は汎用、ドメイン固有制約チェックリストなし |
| 3 | ディスカッション整形 skill | N/A | 汎用Web処理。`/digest` の延長で対応可能 |
| 4 | notebook 一括DL skill | Gap | Kaggle API 統合スキルなし |
| 5 | 定型タスクの skill 化パターン（暗黙の前提ズレ解消） | Partial | `skill-patterns.md` に16パターンあるが原則未記載 |
| 6 | submit→採点→ログ→次実験ループ自動化 | Partial | checkpoint_manager, /improve --evolve でループ基盤あり |
| 7 | Claude Code × Kaggle ベストプラクティス | Partial | memory-safety-policy.md に萎縮対策あり |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| A | skill-patterns.md（16パターン） | 暗黙の前提が都度指示だとドリフトする | **強化**: Implicit Assumption Pinning 原則を追加 |
| B | /review + review-checklists/ | 推論効率観点の専用レビューskill | **強化**: ドメイン固有チェックリスト追加テンプレート |
| C | cmux-notify.sh 通知基盤 | nohup + 仮想環境 + 採点待ち → 通知 | 強化不要: /schedule + cmux-notify.sh で同等 |

## Integration Decisions

- **#5 + #A 採用**: `skill-patterns.md` に「Implicit Assumption Pinning」設計原則を追加
- **#B 採用**: `review-checklists/TEMPLATE.md` にドメイン固有チェックリスト追加テンプレートを作成
- **#1,2,4 スキップ**: Kaggle 固有。現在 Kaggle コンペに参加していないため不要
- **#3 スキップ (N/A)**: 汎用Web処理
- **#6,7 スキップ**: 既存基盤で対応可能

## Changes Made

1. `.config/claude/references/skill-patterns.md` — Design Principles セクションに Implicit Assumption Pinning を追加
2. `.config/claude/references/review-checklists/TEMPLATE.md` — ドメイン固有チェックリスト追加テンプレートを新規作成
