---
title: learned 昇格ループ — 観測→学習→昇格パイプラインのシンプル再構築
date: 2026-05-31
status: approved (design)
scope: L
related:
  - docs/audit/telemetry-coverage.md
  - docs/adr/0005-autoevolve-four-layer-loop.md
  - .config/claude/scripts/learner/session-learner.py
  - .config/claude/scripts/learner/failure-clusterer.py
---

# learned 昇格ループ

## 背景 — 何が壊れているか

「外部記事を /absorb する」労力(1.5ヶ月で 81 本、直近はほぼ全スキップ)に比べ、**自前の運用ログから学ぶループが死んでいる**ことが調査で判明した。実データ証拠:

- `learnings/telemetry.jsonl`(3029件)・`patterns.jsonl`(1108件)・`strategy-outcomes.jsonl`(2799件)等は**毎日更新され続けている**(観測は生きている)
- しかし全レコードが `score:0.0` / `tier:raw` / `promotion_status:pending` — **採点・昇格の多段が一度も機能していない**
- `friction-events.jsonl` は 7件で 5/7 停止、`errors.jsonl` は 26件で 4/14 停止
- 断線の根因(複合):
  1. **スキーマ・ドリフト**: telemetry レコードに `category` フィールドが無く、`session-learner`(category==telemetry を除外)も `failure-clusterer`(category==error を抽出)も両方空振り
  2. **昇格ループ未配線**: `autoevolve-runner.sh` は cron を想定するコメントだけで crontab 未登録 → 一度も自動実行されていない
  3. **入力源の枯渇**: friction-events は専用検出器(webfetch-truncation)依存で、汎用失敗データが流れ込まない

設計ドキュメント(ADR/複数 plan)は分厚いのに、**実データが最後まで流れた形跡がない**。これは「良さそうで作り込んだ harness が配線されないまま腐った残骸」と判断した。

## 学習素材の実態(棚卸し結果)

`telemetry.jsonl` の `subagent_complete` は空疎(failure_mode 空・agent名なし・0.5固定)で学習源に不適。本命は `patterns.jsonl`:

| type | 件数 | 性質 | 本設計での扱い |
|---|---|---|---|
| `learned` | **124** | scope 付き・粒度高・actionable(例:「review 指摘は実ファイルで裏取りしてから採否」) | **主軸:昇格候補** |
| `doom_loop` | 455 | `{count, target, tool}` のみ。同一ファイル反復読み検出。生では薄い | 副産物(頻出 target 集計、後続) |
| `exploration_spiral` | 377 | 連続 Read 検出 | 副産物(同上) |
| `rejected` | 138 | 棄却の負の知識 | 対象外(将来候補) |

## 目的 / 非目標

**目的**: `patterns.jsonl` の `type:learned`(124件、以降も増える)pending を、durable artifact(skill / reference / CLAUDE.md rule / policy script)へ昇格させる**軽量で死蔵しないループ**を1本構築する。

**非目標**:
- 壊れた scoring/promotion 多段の蘇生(退役する)
- doom_loop/exploration_spiral の深掘り分析(別タスク、本ループは件数集計の nudge のみ)
- telemetry.jsonl の subagent_complete の活用(空疎なため対象外)

## アーキテクチャ — コア1本 + 薄い入口3つ

危険なのは「3つの独立実装」。抽出ロジックを1本に集約し、入口を薄く保つことで KISS / DRY を維持する。

### コア(共通・純粋ロジック)
`scripts/learner/extract-promotion-candidates.py`(新規)
- 入力: `learnings/patterns.jsonl`(type==learned)+ `learnings/promoted-ledger.jsonl`(処理済み key、下記)
- 処理: 未処理 learned のみ抽出 → `scope` でグルーピング → 既存 artifact との重複チェック → 推奨昇格先を付与
- 出力: 候補リスト(stdout JSON)。副作用なし(冪等・読み取り専用)

### 状態管理 — hash ベース ledger(jsonl 追記問題への対処)
`patterns.jsonl` は**追記専用でレコード書き換え不可**。`promotion_status` をその場で更新できないため、採否は別 ledger で管理する:

```
learnings/promoted-ledger.jsonl  (新規・追記専用)
  1行 = {"key": <冪等キー>, "decision": "adopted"|"rejected"|"deferred",
          "target_artifact": "<path>", "timestamp": "..."}
```
- **冪等キー**: learned レコードに `hash` フィールドは無い(`detail` / `generalized_detail` を持つ)。コアが `generalized_detail`(無ければ `detail`)の SHA1 を算出してキーとする。これにより**同一知見が複数セッションで再記録されても1候補に束ねられる**(timestamp+session_id では別キーになり重複が通ってしまうため不採用)
- コアは ledger の key と照合し**未処理のみ**を出す(処理済みは二度と出ない)
- 既存の append パターン(`append_to_learnings`)と一致

### 入口3つ(役割を分離して死蔵を防ぐ)

| # | 入口 | 役割 | 死蔵対策 |
|---|---|---|---|
| 1 | **skill `/promote-learnings`**(本体) | コアを呼び候補提示 → 対話採否 → ledger 追記。採用時は「どの artifact に何を足すか」まで提案 | ユーザーが起動するので必ず読まれる |
| 2 | **週次 nudge** | 既存 launchd を**置換**。「pending N件、トップ3 scope」だけ通知し `/promote-learnings` へ誘導 | **レポート本体を作らない**=読む作業を生まない |
| 3 | **/improve 統合** | /improve のチェック項目に「learned 昇格 pending N件」を1行追加、多ければ skill へ誘導 | 既存の走る文脈に相乗り |

### 昇格先の振り分け(半自動)
`scope → artifact` のマップ + Claude のレビュー判断。完全自動は誤爆、完全手動は面倒なため中間を取る。

| scope 例 | 推奨昇格先 |
|---|---|
| `cc-bash`, `cc-*`(harness 挙動) | CLAUDE.md rule / references |
| `review-gate`, `review-*` | `agents/code-reviewer.md` 等 |
| `zero-width`, security 系 | 該当 policy script / security-reviewer |
| `absorb`, `triage`, `skills` | 該当 skill / references |
| マップ外 | Claude が候補提示し、ユーザーが配置先を決定 |

マップはあくまで初期推奨。最終配置は skill 内で Claude が候補内容を読んで提案し、ユーザーが承認する。

## 退役範囲(harness-stability 準拠:即削除せず無効化 → 30日評価)

| 対象 | 判定 | 措置 |
|---|---|---|
| `session-learner.py`(patterns/quality/metrics を書く) | 生存・有用 | **残す** |
| `failure-clusterer.py`(Stop hook、category==error 空振り) | 死亡 | Stop hook(settings.json:310)から外す |
| launchd `com.user.nightly.friction-aggregate.plist`(friction-events 依存で空) | 死亡 | `launchctl unload` → 週次 nudge に置換 |
| `friction-weekly-digest.sh`(同上) | 死亡 | 新 nudge スクリプトに置換 |
| `autoevolve-runner.sh`(cron 未登録で元から不動) | 休眠 | 触らず寝かせる(30日評価対象) |
| `webfetch-truncation-detector.py`(WebFetch時のみ発火) | 生存 | 残す(害なし) |

退役は「無効化 + 措置日を記録 → 30日後に削除を評価」。即削除しない(`references/harness-stability.md` 準拠)。

## エラーハンドリング

- コア: 入力 jsonl が壊れた行を含む場合は `jq -R 'fromjson?'` 相当の tolerant parse でスキップ(既存 aggregate スクリプトの H5 パターン踏襲)。patterns.jsonl 不在時は「候補 0件」を返し fail しない
- skill: ledger 書き込み失敗は Fail Fast(採否が記録できないなら作業を止める)
- nudge: 候補 0件なら通知を出さない(ノイズ防止)

## テスト方針

- コアは純粋ロジック(jsonl in → JSON out)。固定 fixture でユニットテスト
- 重点: **ledger 照合の冪等性**(同じ hash は二度出ない)、scope→artifact マップの分岐、壊れた行の tolerant parse、空入力
- skill は採否 → ledger 追記の往復を手動シナリオで検証

## リスクと撤退条件

- **リスク1**: skill を結局起動せず candidates が溜まる → nudge の N件表示で気づける設計。3ヶ月起動0なら本ループ自体が死蔵と判断し退役を再評価
- **リスク2**: scope→artifact マップが実態と乖離 → マップ外は手動 fallback があるので破綻しない。乖離が頻発したらマップを更新
- **リスク3 (echo chamber / self-reinforcing)**: 昇格は `importance` 降順 + **完全一致 (SHA1) dedup** のみ。完全一致でない *semantic に近い* learned が同じ結論を反復昇格すると、memory が monoculture 化し、既存の前提を強化する方向だけに偏りうる(出典: 0xJeff "60 Days with Hermes Analyst" 2026-06-02 absorb。feedback loop の未解決問題として提起 "outputs tend to gravitate towards existing holdings... haven't solved this yet")。
  - **今は自動ガードを置かない (YAGNI)**: 本ループは稼働前で echo chamber は未観測。`contradiction-scanner.py`(矛盾検出)・`submodular_selection.py`/`diversity-selection-guide.md`(多様性選択)という部品は既存だが**未配線**。観測なしに昇格ゲートへ配線するのは premature scaffolding。
  - **代わりに heuristic を skill に置く**: `/promote-learnings` の採否判断に「多様性チェック」を1項追加(下記 skill 参照)。設計段階の risk として codify するに留める。
  - **watch 条件 (これが観測されたら配線を再検討)**: (a) 同一 `scope` の learned が**3 連続バッチ以上**昇格を占有、または (b) 既存 memory に**矛盾/反証する** learned が恒常的に reject され続ける。いずれかを観測したら `contradiction-scanner.py` / `submodular_selection.py` の昇格ゲート統合(M 規模)を起票する。
- **撤退条件**: learned の流入が枯れる(session-learner が patterns を書かなくなる)なら、このループの前提が崩れるので停止して再調査

## 未解決事項
- **echo chamber の自動ガード**: リスク3 の watch 条件を満たすまで意図的に未実装(YAGNI)。観測トリガーで再検討する。
