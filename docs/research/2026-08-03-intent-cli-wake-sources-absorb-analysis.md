---
title: "AIエージェント4体を herdr だけでオーケストレーションする intent-cli — 指示待ちで止まらない仕組み — absorb analysis"
date: 2026-08-03
status: analyzed
family: multi-agent-orchestration
source:
  title: "AIエージェント4体を herdr だけでオーケストレーションする intent-cli — 指示待ちで止まらない仕組み"
  author: 不明（ユーザー貼り付けテキスト）
  url: "https://github.com/J-Tech-Japan/intent-system/releases/tag/v0.8.0"
adopted: 4
validation-only: 0
---

## Source Summary

主張: マルチエージェント開発ループの停止は「誰かが失敗する」形では起きない。全員 idle・誰も失敗していないのに全体が止まる。原因は wake 源が 1 系統しかないこと。解は wake の多重化と「全 wake 源が落ちても検出できる」停滞検査。

手法 9 件:
- M1 wake 源の多重化 (1系統→3系統)
- M2 状態変化イベント購読 (herdr socket の pane.agent_status_changed。ワーカーの協力不要)
- M3 複合判定 (状態 + 完了マーカー + 成果物 + canonical fact。状態変化は「何かが起きた」としか言っておらず成功を意味しない)
- M4 委譲コマンドの payload に task id・期待成果物・受信者が実行すべき報告コマンドをデータとして埋め込む (契約をプロンプト文でなくツール側へ)
- M5 transport 非依存の同一コマンド面 (agmsg / herdr-only で同形。AI が覚える語彙を 1 つに)
- M6 「wake 源が複数あるから大丈夫」ではなく「すべての wake 源が落ちても停滞が検出できる」を設計基準に
- M7 承認済みだが未マージの PR を検出
- M8 合成テスト 11 項目全通過でも実作業 1 サイクル目で停止した。自チームで dogfood してから出荷
- M9 旧方式 (agmsg) を非推奨にせず両モードを可逆に維持

根拠: 合成テストは全通過したが実作業 1 サイクル目で停止。dogfood で出た欠陥 4 件はいずれも合成テストで出ない類 (切替手順の案内先が空 / 旧フック設定の残留 / ペイン ID 空でのコマンド投入 / イベント全件再生)。
前提条件: herdr でターミナル制御される 4 ロール常駐体制。agmsg の codex 対応は専用ブリッジ約 2,900 行 (agmsg 全体の約 27%)。

## Phase 1.5 Saturation Gate

family = multi-agent-orchestration、N=17+。採用率は直近 5 件で 3/5 (2026-07-22 graph-engineering 採用0 / 2026-07-25 graph-engineering 採用1 / 2026-07-25 herdr-agmsg 採用4 / 2026-07-08 agentic-os 採用2 / 2026-06-03 dynamic-workflows 採用0) → **PASS (warning: 重複領域)**。

Step 7 Stale-Plan Audit: 前回 absorb `docs/research/2026-07-25-herdr-agmsg-orchestration-wall-absorb-analysis.md` は同一プロダクト系列の前バージョン。その T1/T2 は PR #186 で merge 済み、T3/T4 は `docs/plans/active/2026-07-25-herdr-attention-routing-plan.md` に active のまま未着手であることを確認。今回の記事は T3 (agent_status による停滞検出) の続きにあたる。

## Phase 2 判定表 (Phase 2.5 反映後)

| # | 手法 | Phase 2 判定 | Phase 2.5 後 | 根拠 |
|---|---|---|---|---|
| M1 | wake 源の多重化 | Partial | Partial (根拠を訂正) | 対話 hub-and-spoke は人間がターンを駆動するが、nightly orchestrator は `~/Library/LaunchAgents/com.user.nightly.orchestrator.plist` で launchd 配線済み (実在を確認)。「人間が conductor だから安全」は無人経路に不成立 |
| M2 | 状態変化イベント購読 | Gap | **Partial** | collector 起動時は `herdr-collect-result.sh:87` の `herdr wait agent-status` が push wake として機能。常駐 listener が要るのは無人 herdr dispatch のみ |
| M3 | 複合判定 (状態≠成功) | Already (強化可能) | **Partial** | `herdr-collect-result.sh` の claude 経路は 状態(idle/done) + 成果物(非空) の 2 条件。claude の PROMPT は `herdr agent send` で TUI に打ち込まれ画面に残るため「非空」は構造的に常に真 |
| M4 | payload に task id/成果物/報告コマンド | Already | **Partial** | `herdr-launch-worker.sh:56-57` に WORKER_ID / RESULT_FILE はあるが、通常経路は raw `--task`。期待成果物のスキーマは self-improve preset の特例のみ (Codex 指摘) |
| M5 | transport 非依存の同一コマンド面 | Gap (drift) | Gap (制御面) | `.config/claude/skills/dispatch/SKILL.md` の herdr 言及が **0 件** (grep 実測)。herdr worker 2 スクリプトは実装済みなのに router から到達不能。cmux 外は subagent に落とす分岐しかない |
| M6 | 全 wake 源 down でも停滞検出 | Gap | Gap (確定) | `patrol-agent.sh` は headless `claude -p` のみ。T3 plan も idle を異常扱いしないため「全員 idle・未回収」を検出しない (Codex 指摘) |
| M7 | 承認済み未マージ PR 検出 | N/A | N/A (理由を訂正) | 当初は「open PR 4 件すべて reviewDecision 空」を根拠にしたが、Codex 指摘の通り正しい理由は `scripts/runtime/poll-pr-reviewer.sh` の reviewer が別 work-host 専用で `gh pr review` を実行しない設計にある |
| M8 | dogfood で出荷判定 | Already | **Unverified** | T3 plan の検証欄が「手動で working 放置 pane を作る」= 合成テスト型で、記事の教訓そのものを踏んでいる |
| M9 | 旧方式を非推奨にせず可逆 | Already | Already | `references/harness-stability.md` の 30 日評価 + `docs/decommission-log.md` の flag→削除済 実運用。記事より厳格 |

## Phase 2.5 Refine

Gemini は IneligibleTierError (individuals sunset) のため **Codex 単独批評**。呼び出しは `codex exec --skip-git-repo-check -m gpt-5.6-terra --sandbox read-only --config model_reasoning_effort=xhigh` の直接実行。

Codex の結論 (verbatim 冒頭): 「結論：M1 の根拠は崩れ、M2 は「Gap」より条件付き Partial、M3/M4/M8/M9 は評価を下げるべきです。最大の漏れは「完了イベント」ではなく、**起動済みで未回収の仕事を誰が再照合するか**です。」

Codex により判定を 5 件修正 (M1 根拠 / M2 Gap→Partial / M3 Already→Partial / M4 Already→Partial / M8 Already→Unverified)。

**Codex 指摘のうち裏取りで退けたもの**: Codex は M1 の根拠として `.agents/skills/autonomous-skill/scripts/run-session.sh:159` の autonomous runner が「承認なしで自動継続」する点を挙げたが、実ファイル確認の結果これは commit 554f5df5 "add vendored Codex skills" で入った **vendored Codex skill** であり、`docs/decommission-log.md:28` で 2026-06-21 に物理削除された dotfiles native の autonomous とは別物。launchd 配線もない (人間起動)。M1 の訂正根拠として有効なのは nightly orchestrator の方だけ。

## 記事の手法リストにない最大の発見 (Codex 発見・裏取り済み)

`scripts/lib/dispatch_logger.sh:8` のセッション ID は `date+$$` でプロセスごとに振られる。launch と collect を別コマンドで実行すると 1 つの worker のログが 2 ファイルに分かれるが、`scripts/runtime/dispatch-log.sh:27` の `_latest_log` は既定で最新 1 本しか読まない。結果として **「起動済みで未回収の worker」を答えられる場所が存在せず**、`filter --worker` も片側しか拾えなかった。記事の言う「最後の網」が dotfiles では欠落していた。

## Phase 3 Triage 結果

ユーザーが T1-T4 すべてを選択。

## Phase 4 実施内容 (すべて実装済み)

ブランチ `feat/herdr-wake-sources` (worktree `worktrees/herdr-wake-sources`、master から分岐)。

**T1 [S] dispatch router に herdr 分岐** — `.config/claude/skills/dispatch/SKILL.md`
- `<IMPORTANT>` ブロックの判定順を `CMUX_WORKSPACE_ID` → `HERDR_ENV` → サブエージェント に変更
- 「cmux 外での挙動」節に herdr 経路を追加。`herdr-launch-worker.sh --model/--task` と `herdr-collect-result.sh --pane/--worker/--timeout` の実フラグを確認して記載
- 判定に効く差分 2 点のみ記載 (`--worktree` 未対応 / 承認待ちは exit 4)。使い分け表は `references/subagent-vs-cmux-worker.md` が正として重複を作らない (instruction DRY)
- 前回 absorb の T1 が reference 2 本しか直しておらず router 本体が取り残されていた drift の修正

**T2 [S] 未回収 worker の検出** — `scripts/runtime/dispatch-log.sh` + `scripts/lib/dispatch_logger.sh`
- `_all_logs()` を追加し `filter` を全セッション横断に変更
- `pending` サブコマンドを追加 (dispatch されたが result が来ていない worker を経過時間・last_state つきで列挙)
- `LOG_DIR` を `DISPATCH_LOG_DIR` env で上書き可能にした。`dispatch_logger.sh` 側は `DISPATCH_SESSION_ID` を既に env で受けるのに `DISPATCH_LOG_DIR` だけ固定だった非対称も揃えた

**T3 [S] collect の成功条件を強化** — `scripts/runtime/herdr-launch-worker.sh` + `herdr-collect-result.sh`
- launch (claude 経路) が送信 PROMPT を `${RESULT_FILE}.prompt` に控える
- collect が「エコー行を除いた残りが非空か」を追加判定。空なら `no response (prompt echo only)` で失敗扱い
- `.prompt` が無い旧 worker は従来通り素通し (後方互換)
- 成果物本体は書き換えない (判定にだけエコー除去を使う)

**T4 [S] T3 plan の設計訂正** — `docs/plans/active/2026-07-25-herdr-attention-routing-plan.md`
- 「idle は異常でないので採用しない」を「idle 単独は通知しない。ただし idle かつ未回収は異常」に訂正し、発火条件を `agent_status == idle/done` ∧ `pending に載っている` の AND に変更
- 検証欄に「合成テストだけで完了としない。実際の委譲サイクルを 1 本通す」を追加 (記事 M8 の教訓)
- `last_reviewed` を 2026-08-03 に更新

## 検証結果 (実行済み)

- `uvx pytest tests/runtime/test_dispatch_log_pending.py -q` → **4 passed**。新規テストは launch/collect がセッションを跨いだ状態を fixture で再現し、pending が未回収 worker のみを出すこと・filter が 2 セッション横断で 4 行返すことを検査する
- **このテストが実バグを 1 件捕まえた**: `_all_logs()` の `ls` はヒット無しで exit 1 を返すため、`set -e` によりエラーメッセージ出力前にスクリプトが黙って死んでいた (既存 `_latest_log` は `| head -1` でパイプ末尾が 0 になるため露見しなかった)。`|| true` で修正済み
- T3 のエコー除去判定は 4 ケース (エコーのみ / エコー+応答 / エコー+空白のみ / 折り返し変形) を手動スクリプトで検査し 4/4 通過。**自動テストは未整備** — 判定ロジックがシェルスクリプト内にインラインで、実行には live な herdr pane が要るため
- `bash -n` 4 ファイル通過、`task validate-configs` 実行済み

## 未検証事項 / 注意

- T3 の変更は実 herdr pane での通し確認をしていない。`.prompt` sidecar の書き出しと除去判定は単体検査のみ
- `pending` は実ログでの動作確認をしていない (`/tmp/cmux-dispatch-log/` が空だったため fixture のみ)
- M2 の常駐 listener (記事の socket 購読) は不採用。collector 起動時は既に push wake が効いており、常駐が要るのは無人 herdr dispatch のみ。実際に回収漏れが観測されてから検討する (Codex の P3 判断に同意)

## 教訓

- 同一プロダクトの続報 absorb は、前回の plan の未着手タスクを先に開くと当たりが早い。今回は記事の中核 (wake 源 #1) が前回 T3 とほぼ同一テーマだった
- 前回 absorb の修正が reference には届いて router には届いていなかった。**「配線を直した」と「呼ばれる場所を直した」は別**で、grep 0 件は後者の欠落を機械的に出せる
- 記事の手法 9 件のうち最も価値があったのは手法そのものではなく **「すべての wake 源が落ちても検出できるか」という検査基準**。この基準で dotfiles を見ると、dispatch ログが「未回収の worker」を答えられない構造だと分かった
- Codex の指摘も裏取りする。autonomous runner の件は vendored skill と退役済み native 実装の取り違えだった
