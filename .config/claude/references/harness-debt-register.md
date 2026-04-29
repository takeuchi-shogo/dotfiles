---
status: reference
last_reviewed: 2026-04-29
---

# Harness Debt Register

ハーネス自体の技術的負債を追跡する。Bouchard の "harness debt" 概念に基づく。
Build to Delete 原則と連動し、各エントリに sunset 条件を明記する。

## 分類

| Type | 定義 | 例 |
|------|------|-----|
| **Threshold** | ヒューリスティック閾値が最適でない | edit loop 3回/10分 |
| **Coverage** | 検出すべき失敗パターンが未カバー | 新言語の lint 未対応 |
| **Staleness** | モデル進化で不要になった hook/rule が残存 | 旧モデル向け workaround |
| **Complexity** | hook 間の依存が複雑化 | 循環参照、暗黙の実行順序 |

## 登録台帳

| ID | Component | Type | Created | Next Review | Sunset Condition | Notes |
|----|-----------|------|---------|------------|------------------|-------|
| HD-001 | edit-loop threshold (3/10min) | Threshold | 2026-03 | 2026-06 | モデルの self-correction 精度が 95% 超 | Opus 5.0 で再評価 |
| HD-002 | reasoning_effort static config | Threshold | 2026-03 | 2026-05 | Reasoning Sandwich 自動化で解消 | 動的切替の実装待ち |
| HD-003 | autoevolve commit footer JSON self-reporting integrity (Rule 50) | Coverage | 2026-04-29 | 2026-07 | `split_holdout.py` / `gaming-detector.py` の出力 hash を footer に bind する仕組み実装 | LLM が `holdout_delta` / `regression_summary` を計測なしに自己申告でき Rule 49 ROBUST gate を bypass 可能。yamadashy absorb 2026-04-29 review MEDIUM |
| HD-004 | dashboard_generator.py path containment | Coverage | 2026-04-29 | 2026-07 | `--output` / `--history` を `~/.claude/agent-memory/` 配下に resolve & containment check 適用 | 現状ユーザー手動起動のみだが SKILL.md 経由で LLM がパス組み立てに関与する場合に問題化。yamadashy absorb 2026-04-29 review MEDIUM |
| HD-005 | dashboard_generator.py markdown injection sanitization | Coverage | 2026-04-29 | 2026-07 | `_md_escape()` 導入: improve-history.jsonl の値を table セル化前にパイプ・改行・RTL override・ゼロ幅文字を除去 | autoevolve が LLM 生成値を improve-history.jsonl 経由で `_dashboard.md` に流し込む経路で間接 prompt injection。yamadashy absorb 2026-04-29 review MEDIUM |

## 運用

- `/improve` 実行時にこの台帳を参照し、古い負債の解消を優先提案
- 新 hook 追加時に Build to Delete 基準で sunset condition を設定
- 四半期ごとに Staleness 監査を実施（Next Review 日付を基準）
- 解消済みエントリは削除せず `Status: resolved` を追記（履歴保持）
