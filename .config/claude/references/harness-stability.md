---
status: active
last_reviewed: 2026-04-23
---

# Harness Stability Policy

## 原則: 30日評価なしに捨てない

ハーネスの構成要素（hooks, skills, agents, references）を削除・置換する前に:
1. 最低 30 日の実運用データを収集する
2. 使用頻度を計測する。**自動計測があるのは skill だけ** — `scripts/policy/skill-tracker.py` (settings.json の `Skill` matcher に登録済) が呼び出しを記録する。hook / agent / reference には自動計測器がなく、`decommission-log.md:22` の二重確認 (実行ログ + 全期間 transcript の手動照合) に頼る
3. 代替案が同等以上の効果を発揮することを確認する

手順は `references/dead-weight-scan-protocol.md` に従う。

learner 側の 2 本を計測の根拠にしないこと:

- `scripts/learner/staleness-detector.py` — hook 未登録。`memory-eviction.py` からの import と `/improve` 実行時の advisory (`improve-policy.md:489`) が唯一の consumer で、常時収集はしていない
- `scripts/learner/skill-usage-tracker.py` — consumer ゼロの休眠スクリプト。`.config/claude/README.md:190,237` と `references/diagrams/architecture-overview.md:45` は Stop/SessionEnd で動くと書いているが、settings.json に登録がなく実行されていない (要修正の drift)

## 例外

- セキュリティ上の問題が発覚した場合: 即時削除
- 明らかに未使用 (skill は skill-tracker のログ、それ以外は transcript 照合で 0 invocations in 30 days)
- **モデル世代交代時の振る舞い指示**: 30 日ルールの対象外。`references/dead-weight-scan-protocol.md` の「モデル世代交代時の ablation」に従う

## 原則: 新しい検査は report から始める

新しい検査 (hook / lint rule / scanner) を初日から block にすると、規律ではなく **回避の作法** が育つ。
抑制コメントを反射的に足す、閾値を緩める、対象から除外する。導入は次の順で昇格させる。

1. **collect** — 検出のみ。block も warn もせず、件数と内容を記録する
2. **drain** — 既存違反 (baseline) をゼロにする。「誰も読まない警告リストに 1 件足す」を許さない
3. **gate** — baseline が空になってから block に上げる。以後の再発は hook / CI が落とす

昇格させない判断も同じくらい正しい。false positive が構造的に避けられない検査
(エントリポイントを推論しきれない dead-code scan 等) は collect のまま据え置き、
「これは gate ではなくレビュー補助」と明記する。

妥協を残すなら **期限と解消条件を書く** — 「今は warn。理由は X。X が解消したら error に上げる」。
条件のない warn は永久に warn のまま残る。

既存の先例: `skills/ast-grep-practice/references/cli.md` の「デフォルトで開始 → 段階的に厳しくする」
（`--error` の閾値を後から上げる）。

この節が扱うのは **検査を導入するときの厳しさの段階** であって、hook が予期せずクラッシュした
ときの挙動ではない。後者は `hook-failure-policy.md` の fail-open / fail-closed が別軸で決める。
security / policy gate は collect 段階でも `fail_closed=True` を維持する。

> 出典: isamu「1日500コミットは、もう読めない」absorb (2026-07-31) — 「初日からブロックすると
> 回避の作法が育つ」「drain してから ratchet する」。削除側の 30 日評価と対になる導入側の規律。

## Hook 実行時間モニタリング

重い hook はセッション全体を遅らせる。最低限の規律:

- `settings.json` の hook 設定で `timeout` を必ず指定する。指定なしのデフォルトは 60s 程度 (単位: 公式仕様は未公開、settings.json 実測値と Claude Code 既定動作から推定) だが、PreToolUse / PostToolUse のような頻発 hook は 5-10s が現実的上限
- 実行時間 > 5s の hook は再設計候補。集計手段は ad-hoc (個別 hook に `time` ラッパー / observability ログから p50/p95 抽出) — 専用 stats スクリプトは未実装
- 例外なく守らせたい規則 (golden-check, protect-linter-config 等) は短時間化を最優先。長い処理は非同期 (background) または PostToolUse → 別プロセスにオフロード

> 出典: Boris Tip 10 absorb (2026-04-30) — 「hook が重いとセッション全体が遅くなる、実行時間の上限を設けておけ」

## 背景

「切り替えない」の強制は実験速度を殺す。「30日評価」が撤退条件を客観化する。
