---
title: "The event driven future of AI — absorb analysis"
date: 2026-07-27
source:
  title: "The event driven future of AI"
  author: "@TheGlobalMinima (X), 2026-07-26"
  url: https://x.com/TheGlobalMinima/status/2081351146661130399
  local: "~/Documents/Obsidian Vault/raw/The event driven future of AI.md (fetch 経路不要)"
status: implemented
family: なし (新分野・明示記録)
---

# The event driven future of AI — absorb 分析

## 主張

エージェントの作業は request/response の寿命を超えた。長時間エージェントは endpoint ではなくイベントの consumer/producer として設計せよ。根拠は Anthropic harness の 3h50m/$124 実行、OpenAI Responses `background=True`、GitHub webhook の 10 秒窓、Confluent/Temporal の設計論。前提条件は「長時間・自律・非同期」の作業に限る点で、著者自身が「小チームは Postgres の jobs テーブルで十分、broker は後」と明言している。

## Phase 1.5 Saturation Gate

PASS (新分野)。`harness-engineering` は "harness" 1 hit のみで閾値 3 未満。`multi-agent-orchestration` (N=14) との重なりは orchestrator/worker/blackboard → topic 写像の 1 節のみで、本記事の手法はプロンプト協調層でなくトランスポート層のため同 family に入れない判断を明示記録した (安全側ルール「判断が割れたらどちらにも分類しない」)。

## Phase 2 → 2.5 の判定変更 (Codex 批評により 4 件訂正)

| 手法 | 旧判定 | 新判定 | 根拠 (ファイル:行) |
|---|---|---|---|
| 大ペイロードの外部退避 | Already | Already (根拠差替) | `output-offload.py` は settings.json に配線されておらず死んでいる。実体は Rust `tools/claude-hooks/src/post_bash.rs:15` (/tmp へ best-effort) |
| 完了記録を durable 後に置く | Already 強化不要 | Partial | `completion-gate.py:1216` `_find_unbacked_claimed_paths` は主張文中のファイルパス実在のみ照合。commit/push/PR は未検証 |
| dead letter topic | Already 強化不要 | N/A | `failure-escalation-protocol.md` は人手 Issue 昇格 runbook で DLQ ではない。ただし本環境に DLQ は不要 |
| correlation id | Already 強化不要 | Partial | Rust `tools/claude-hooks/src/events.rs:163` の emit に `session_id` が無い。実運用の Bash PostToolUse は Rust 側なので横断 correlation は不成立 |
| at-least-once 前提の冪等 handler | Already | Partial・実害あり | 下記「冪等性の実害」参照 |

その他: broker/topic/partition/consumer group/offset、状態=イベントの fold、移行手順、orchestrator→topic 写像 は N/A (単一ユーザーのローカルハーネスで broker もサーバーも無い)。schema versioning は `memory-schema.md:77-80` が reader 側 graceful degradation を意図的採用しており Partial (意図的)。replay≠決定的再現の明文化は Gap だが `session-observer.py --replay` は transcript 再生表示のみでモデル再実行しないため実害の所在が薄く不採用。

## 冪等性の実害 (Codex 指摘 → 全て実ファイルで裏取り済み)

1. `scripts/runtime/tech-researcher/run-tech-researcher.sh:264` — `adoption-ledger.jsonl` へ候補記事ごとに無条件 `>>`。dedupe は run 内の候補 URL に対してのみ (`:125`) で ledger 相手ではない。timeout kill → retry で同一 (date,url) が二重計上され、採用率 = 情報源ランキングの主指標が歪む
2. `scripts/runtime/nightly/run-learned-promote.sh` — `gh pr create` が非ゼロ終了した場合は `:481` が `push origin ":$BRANCH"` でリモートを消すので綺麗。ただし push 成功後〜pr create 前に timeout kill されると `:481` に到達せず、`trap _cleanup` は worktree とローカルブランチしか消さない → orphan remote branch が残り、次回の open-PR guard は PR を見るので拾えない。窓は狭いが実在 (Codex の主張のうち「gh 失敗でも orphan」は誤りで、kill 限定に訂正)
3. 全 retry ジョブ共通 — attempt ごとに Discord `@here`。retry 成功後も初回失敗通知は撤回されない (偽陽性の緊急通知)

なお `retry: 1` は 9 ジョブ (当初 7 と誤認、`jobs.yaml` 先頭 40 行のみ見ていたため)。

## 採用 (1 件、実装済み)

**A: tech-researcher ledger の retry 冪等化** — `scripts/runtime/tech-researcher/run-tech-researcher.sh`。追記ループの前に同日の既存 URL 集合を jq で構築し、既出 URL は追記を skip して ADOPTED_COUNT だけ計上。`declare -A` は launchd の login shell が古い bash に落ちる既知の罠 (MEMORY.md の nightly codex 移行の教訓) を避けるため使わず、同ファイル既存の空白区切り集合 idiom に合わせた。検証: `bash -n` OK / 実 ledger (2043 行) に対し既存 URL 検出 PASS・未知 URL 素通し PASS・該当日なし=空集合 PASS。**実データの重複は現時点 0 件 — 修正は予防であり復旧ではない**。

## 不採用 (ユーザー選択)

- B: learned-promote の orphan remote branch 回収
- C: retry 中の Discord 通知集約
- D: Rust `events.rs` への session_id 追加 (correlation 復旧)

いずれも実害と根拠は上記に記録済みで、必要になった時点で着手できる。

## Validation-only Follow-up (記事 framing が露出させた drift、2 件とも修正済み)

| 対象 | drift 内容 | 訂正 |
|---|---|---|
| `.config/claude/references/memory-schema.md:71-75` | Retention 実施表が `learner/session-trace-store.py` を `traces/*.jsonl` の 30 日 retention owner として「既存」と記載。実ファイルは存在せず (`__pycache__` の .pyc 残骸のみ)、`~/.claude/agent-memory/traces/` 自体も未生成 | 架空行を削除し「event 系 JSONL に retention を実施している機構は無い (日数定義のみ存在)」と実測日付つきで明記 |
| `memory/feedback_tool_output_verify_mutations.md:39-40` | 「この memory は今や backstop — 第一防衛線は gate (機械) に移った」と記載。しかし gate の実装はファイルパス主張のみ照合で、この memory の主題である commit/push/PR/Issue/merge は `git`/`gh` を叩かず素通し | 適用範囲を二分して明記。ファイルパス主張は gate が第一防衛線、mutation 系は機械の防衛線が無く依然この memory が第一防衛線、と訂正 |

## Phase 2.5 の実行記録 (degradation あり)

- Codex: 1 回目 `codex exec` foreground が Bash tool の 600s 上限で timeout。2 回目 cmux `launch-worker.sh` は「cmux is not available」で exit。3 回目 background `codex exec --sandbox read-only` (150,917 tokens) で成功。指摘 5 点は全て実ファイルで裏取りし、4 点採用・1 点 (learned-promote の orphan 条件) を訂正して採用
- Gemini: sunset (IneligibleTierError) のため未実行。Phase 2.5 は Codex 単独 = model-family diversity は片肺

## 教訓

1. **死んだファイルを根拠に Already と判定した** — `output-offload.py` は settings.json に文字列すら無かった。Pass 1 の Explore がファイル実在を確認しても「配線されているか」は別問題。hook 由来の Already 判定は settings.json 側から逆引きして確認する
2. **記事の比喩に既存機構を当てはめる際、機能の同一性を過大評価した** — dead letter → Issue escalate、offset commit → Claim Verification Gate はいずれも「近いが別物」。Codex の「不正確です。もっとも本環境に本物の DLQ は不要です」という切り分け (比喩は誤り / 結論は正しい) が有効だった
3. **N/A が大半でも採用 0 とは限らない** — トランスポート層の手法は全て N/A だったが、その背後の原則 (at-least-once なら handler を冪等に) は retry を持つ既存ジョブに直接刺さった
