---
status: active
last_reviewed: 2026-07-25
---

# Integration Plan: herdr attention ルーティング (T3 / T4)

## Overview

| Field | Value |
|-------|-------|
| Source | 「伝書鳩をやめた日 — herdr × agmsg で「オーケストレーションの壁」を越える」 |
| 分析レポート | `docs/research/2026-07-25-herdr-agmsg-orchestration-wall-absorb-analysis.md` |
| 先行実装 | T1 (起動ルーティング規約) / T2 (`agent_panel_sort = "priority"`) はブランチ `docs/herdr-routing-convention` で実装済み |
| 規模 | M × 2 |

T1/T2 の実装で「見る」の入口は塞いだ。残りは停滞検出の精度 (T3) とエディタ往復 (T4)。

## T3 [M] 停滞検出に herdr の agent_status を足す

### 現状

`scripts/runtime/patrol-agent.sh` (249行) が `com.claude.patrol-agent.plist` で 5 分毎に起動し、
headless `claude -p` セッションの stall を `ps` の etime / cpu ヒューリスティックで検出して
`cmux-notify.sh` (cmux notify → osascript fallback → afplay) で通知する。

対話 pane で放置されたエージェントは検出圏外にある。`herdr agent list` は
`agent_status` (working / blocked / idle / done) と `state_change_seq` を JSON で返すので、
この信号を補助として足せる。

### 設計

Codex 批評 (2026-07-25) の制約をそのまま採用する:

> `working` が長いだけで異常扱いしないこと。`working 継続 + 出力無変化 + 経過時間` の複合条件に限るべき。

- **発火条件**: `agent_status` が `working` のまま、かつ pane 出力が変化せず (`revision` /
  `state_change_seq` が据え置き)、かつ一定時間経過。3 条件の AND。
- **blocked は別扱い**: `blocked` は停滞ではなく承認待ちなので、T2 の attention queue 側で拾う。
  ここで二重に通知しない (instruction DRY)。
- **idle の扱い**: 記事は「10 分以上 idle なら通知」を推奨するが、dotfiles では idle =
  ターンが終わって待機中であり異常ではない。**採用しない**。忘却対策は T2 の巡回で足りる。
- **通知**: 既存 `cmux-notify.sh` を再利用する。新しい通知経路は作らない。
- **状態の保持**: 独自の state DB は作らない (Codex 指示)。前回観測との比較が要るなら
  patrol-agent.sh が既に使っている一時ファイル形式に合わせる。

### 撤退条件

- 誤検知が週 1 回を超えたら閾値を上げるのではなく機能ごと外す。停滞検出は補助信号であって、
  信頼できない通知はノイズとして attention を奪う (この absorb の主題そのもの)。
- `herdr agent list` の呼び出しが 5 分毎の patrol に体感できる遅延を足すなら、
  patrol 本体から切り離して別 launchd に分ける。

### 検証

- 手動で `working` のまま放置した pane を作り、閾値時間経過後に通知が出ることを確認する。
- 正常にターンを終えた pane で発火しないことを確認する (false positive の確認が本体)。

## T4 [M] Neovim 連携

### 現状

`sidekick.nvim` / `nvim --remote` ともに未使用。nvim 側は `avante.nvim` (provider=copilot) で、
Claude Code や herdr との成果物受け渡しはない。`keybindings.json` の `ctrl+e` は
`chat:externalEditor` で用途が別。

### 設計

- **エージェント → エディタ**: `herdr pane split` で同一 tab に pane を割り、`nvim --remote`
  で既存インスタンスに開く。エージェントに使わせるスクリプトとして `scripts/runtime/` に置く。
- **エディタ → エージェント**: nvim の選択範囲を `@path#L10-L25` 形式に整形して
  `herdr agent send-keys` か `herdr agent prompt` で隣 pane に送る keymap。

### 着手判断

T3 完了後に、実際にエディタとエージェントを往復している頻度を見てから決める。
往復が日に数回なら手作業のコピーで足りる。**現時点では YAGNI 寄り**。

## 依存関係

T3 と T4 は独立。どちらも T1/T2 のマージ後に着手する (`agent_panel_sort = "priority"` の
実機挙動が T3 の設計前提になるため)。

## 未検証事項

- `agent_panel_sort = "priority"` にしたとき `next_agent` (prefix+.) が panel 順に追随するかは未検証。
  公式ドキュメントで確認できていないため、T1/T2 マージ後の実機確認が先。
- 追随しない場合は `herdr agent list` を jq で filter して `herdr agent focus` する薄いスクリプトを
  `[[keys.command]]` type="shell" で束縛する (T2 の fallback)。
