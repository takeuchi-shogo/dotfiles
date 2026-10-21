---
status: reference
last_reviewed: 2026-10-21
---

# Harness Debt Register

ハーネス自体の技術的負債を追跡する。Bouchard の "harness debt" 概念に基づく。
Build to Delete 原則と連動し、各エントリに sunset 条件を明記する。

発火記録の欄は、Jediah Katz「Is the agent harness dead?」で紹介された運用
（応急処置を発火ログつきで登録し、発火しなくなったら削除 PR を出す）に倣う。

## 分類

| Type | 定義 | 例 |
|------|------|-----|
| **Threshold** | ヒューリスティック閾値が最適でない | edit loop 3回/10分 |
| **Coverage** | 検出すべき失敗パターンが未カバー | 新言語の lint 未対応 |
| **Staleness** | モデル進化で不要になった hook/rule が残存 | 旧モデル向け workaround |
| **Complexity** | hook 間の依存が複雑化 | 循環参照、暗黙の実行順序 |

## 登録台帳

| ID | Component | Type | Created | Next Review | Review Status | 最終発火日 | 発火回数 | Sunset Condition | Notes |
|----|-----------|------|---------|-------------|---------------|------------|----------|------------------|-------|
| HD-001 | edit-loop threshold (3/10min) | Threshold | 2026-03 | 2026-06 | 期限切れ | 未計測 | 未計測 | モデルの self-correction 精度が 95% 超 | Opus 5.0 で再評価。見直し判断は保留 |
| HD-002 | reasoning_effort static config | Threshold | 2026-03 | 2026-05 | 期限切れ | 未計測 | 未計測 | Reasoning Sandwich 自動化で解消 | 動的切替の実装待ち。見直し判断は保留 |
| HD-003 | autoevolve commit footer JSON self-reporting integrity (Rule 50) | Coverage | 2026-04-29 | 2026-07 | 期限切れ | 未計測 | 未計測 | `split_holdout.py` / `gaming-detector.py` の出力 hash を footer に bind する仕組み実装 | LLM が `holdout_delta` / `regression_summary` を計測なしに自己申告でき Rule 49 ROBUST gate を bypass 可能。yamadashy absorb 2026-04-29 review MEDIUM。見直し判断は保留 |
| HD-004 | dashboard_generator.py path containment | Coverage | 2026-04-29 | 2026-07 | 期限切れ | 未計測 | 未計測 | `--output` / `--history` を `~/.claude/agent-memory/` 配下に resolve & containment check 適用 | 現状ユーザー手動起動のみだが SKILL.md 経由で LLM がパス組み立てに関与する場合に問題化。yamadashy absorb 2026-04-29 review MEDIUM。見直し判断は保留 |
| HD-005 | dashboard_generator.py markdown injection sanitization | Coverage | 2026-04-29 | 2026-07 | 期限切れ | 未計測 | 未計測 | `_md_escape()` 導入: improve-history.jsonl の値を table セル化前にパイプ・改行・RTL override・ゼロ幅文字を除去 | autoevolve が LLM 生成値を improve-history.jsonl 経由で `_dashboard.md` に流し込む経路で間接 prompt injection。yamadashy absorb 2026-04-29 review MEDIUM。見直し判断は保留 |

## 欄の意味

| 欄 | 意味 |
|----|------|
| **Review Status** | `期限内` / `期限切れ`。Next Review を過ぎたら `期限切れ` にする。解消・延期・維持の結論は人間レビューまで書かない |
| **最終発火日** | 当該負債に紐づく応急処置（hook / shim / gate）が最後に発火した日 (`YYYY-MM-DD`)。未計測時は `未計測` |
| **発火回数** | 計測期間内の発火回数（整数）。未計測時は `未計測`。期間の定義は人手更新時に Notes へ書く |

## 運用

- Staleness 監査・簡素化チェック時にこの台帳を参照し、古い負債の解消を優先提案する
- 新 hook 追加時に Build to Delete 基準で sunset condition を設定する
- 四半期ごとに Staleness 監査を実施する（Next Review 日付を基準）
- Next Review を過ぎたエントリは Review Status を `期限切れ` にする。結論（削除・延期・維持）はユーザー判断を待つ
- 最終発火日 / 発火回数は推測で埋めない。値が無いときは `未計測` と明示する
- 解消済みエントリは削除せず `Status: resolved` を追記する（履歴保持）
- 発火の自動計測（例: `scripts/learner/staleness-detector.py` と `learnings/telemetry.jsonl` からの集計を台帳へ反映）は未実装。人手更新が現状の正本
