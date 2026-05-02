---
status: active
last_reviewed: 2026-04-23
---

# Harness Stability Policy

## 原則: 30日評価なしに捨てない

ハーネスの構成要素（hooks, skills, agents, references）を削除・置換する前に:
1. 最低 30 日の実運用データを収集する
2. dead-weight-scan.py で使用頻度を計測する
3. 代替案が同等以上の効果を発揮することを確認する

## 例外

- セキュリティ上の問題が発覚した場合: 即時削除
- 明らかに未使用 (0 invocations in 30 days): dead-weight scan で検出後に削除可

## Hook 実行時間モニタリング

重い hook はセッション全体を遅らせる。最低限の規律:

- `settings.json` の hook 設定で `timeout` を必ず指定する。指定なしのデフォルトは 60s 程度 (単位: 公式仕様は未公開、settings.json 実測値と Claude Code 既定動作から推定) だが、PreToolUse / PostToolUse のような頻発 hook は 5-10s が現実的上限
- 実行時間 > 5s の hook は再設計候補。集計手段は ad-hoc (個別 hook に `time` ラッパー / observability ログから p50/p95 抽出 / `dead-weight-scan.py` の延長で測定) — 専用 stats スクリプトは未実装
- 例外なく守らせたい規則 (golden-check, protect-linter-config 等) は短時間化を最優先。長い処理は非同期 (background) または PostToolUse → 別プロセスにオフロード

> 出典: Boris Tip 10 absorb (2026-04-30) — 「hook が重いとセッション全体が遅くなる、実行時間の上限を設けておけ」

## 背景

「切り替えない」の強制は実験速度を殺す。「30日評価」が撤退条件を客観化する。
