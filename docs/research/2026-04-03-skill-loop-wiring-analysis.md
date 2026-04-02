---
source: "I Stopped Collecting Agent Skills. Started Wiring Them Into Loops." (2026-04, OpenClaw ユーザー記事)
date: 2026-04-03
status: integrated
---

## Source Summary

### 主張
スキルを「収集」するのではなく「ループ」として配線せよ。Template は1回で止まるが、Loop は回るたびに精度が上がる。

### 手法 — Three Rings of a Loop
1. **Scheduling** — cron でタイミング自動化
2. **Memory** — 結果と教訓をファイルに書き、次回コンテキストに読み込む
3. **Feedback** — 出力と人間の編集 diff からルール更新→スキルに書き戻し

### 5つのスキルタイプ
| # | タイプ | パターン |
|---|--------|---------|
| 1 | Writing | 夜間 diff review → 編集パターン蓄積 → ルール自動書き戻し |
| 2 | Research | 要約ではなく原文保存、判断は人間 |
| 3 | Review | 複数ペルソナ同時スコアリング → 低スコアパターンからチェックリスト抽出 |
| 4 | Memory | 3層: Log / Long-term rules / Handoff |
| 5 | Ops | cron chain: Heartbeat→Draft→Edit→Diff→Review→Rule update |

### 根拠
6ヶ月運用。Writing skill が v1.0→v1.3 に自律進化。「spent X weeks doing Y」パターンの自動検出・排除などの具体例。

### 前提条件
OpenClaw フレームワーク。コンテンツ制作（ライティング）がメインユースケース。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Diff-Distill-Writeback | Partial | continuous-learning はリアクティブ検知のみ。バッチ型 diff 蓄積→ルール蒸留→書き戻しの自動ループがない |
| 2 | Closed Loop Chain | Partial | 個別ピース（cron, session-trace, AutoEvolve, review-loop-patterns）は存在するが明示的チェーン定義がない |
| 3 | Multi-Persona Content Review | N/A | コードレビューでは既に複数エージェント並列。コンテンツ制作が主務ではない |

### Already 項目の強化分析

| # | 既存の仕組み | 強化案 |
|---|-------------|--------|
| 1 | Research: 原文保存 | 強化不要（完全一致） |
| 2 | Memory 3層 → 実際は7層 | 強化不要（より洗練） |
| 3 | Scheduling | 強化不要 |
| 4 | AutoEvolve フィードバックループ | 強化可能: 同種編集 N 回蓄積 → 自動ルール候補の閾値ルール |

## Integration Decisions

全項目を取り込み:
1. Diff-Distill-Writeback → improve-policy Rule 37 + output-diff カテゴリ追加
2. Closed Loop Chain → review-loop-patterns.md Section 4 追加
3. 閾値ルール → improve-policy Rule 37 に含む + continuous-learning トリガー追加

## Changes Made

### 1. `references/improve-policy.md`
- 実験カテゴリに `output-diff` 追加（AI出力 vs 人間編集の diff を蓄積→ルール候補生成）
- Rule 37: Diff-Distill-Writeback パターン（同種編集10+回で自動ルール候補生成、人間レビュー後にスキルへ書き戻し）

### 2. `references/review-loop-patterns.md`
- Section 4: Closed Loop Chain パターン追加
  - Three Rings テーブル（Scheduling / Memory / Feedback の当ハーネス実装マッピング）
  - チェーン設計原則（status file 駆動、冪等性、障害時再起動、人間介入ポイント）
  - 日次改善ループのチェーン例
  - 既存ハーネスとの接続テーブル

### 3. `skills/continuous-learning/SKILL.md`
- Trigger に「AI 出力に対してユーザーが同種の編集を繰り返した（Diff-Distill トリガー）」を追加
- Detect Pattern テーブルに「AI 出力を同じ方向に3回以上編集した？ → Diff-Distill 候補」を追加
