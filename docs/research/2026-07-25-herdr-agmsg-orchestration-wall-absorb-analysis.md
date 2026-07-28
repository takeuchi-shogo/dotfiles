---
title: "伝書鳩をやめた日 — herdr × agmsg で「オーケストレーションの壁」を越える — absorb analysis"
date: 2026-07-25
status: analyzed
family: multi-agent-orchestration
source:
  title: "伝書鳩をやめた日 — herdr × agmsg で「オーケストレーションの壁」を越える"
  author: 不明（ユーザー貼り付けテキスト）
参考リンク:
  - "Boris Cherny \"Steps of AI Adoption\": https://x.com/bcherny/status/2077929379661844559"
  - "@horatjp: https://zenn.dev/horatjp/articles/multi-agent-dev-agmsg-herdr"
  - "Nao8: https://zenn.dev/dragon1208/articles/45708cc45a7a7c"
  - "tumf: https://blog.tumf.dev/posts/diary/2026/7/1/herdr-vs-tmux-performance/"
adopted: 4
validation-only: 0
---

# 伝書鳩をやめた日 (herdr × agmsg) — absorb 分析 (採用 4)

## Source Summary (主張・手法・根拠・前提条件)

**主張**: エージェント並列運用の律速はモデルの賢さでなく人間の attention ルーティングにある。Boris Cherny の Steps of AI Adoption 5段階 (Step0 Gated / Step1 Assisted 1体ペアプロ / Step2 Parallel 5-10体 / Step3 Supervised autonomy ~100体 / Step4 AI-native 1000体+) のうち、壁は Step2 と Step3 の間にある。herdr が「見る」(attention ルーティング) を、agmsg が「話す」(Claude kicks off Claude) をそれぞれ解決する。

**根拠**: 記事著者の実運用体験 (6体並列で「どの子が止まってるか探す」のが仕事になった)。tumf 実測でメモリは tmux の約12.6倍 (100セッションで 4.5MB vs 56.3MB)。

**前提条件**: 5-10体を日常的に並列運用していること。macOS + Ghostty 環境。

**手法 (M1-M12)**:

- **M1**: Steps of AI Adoption 5段階で自己位置を定める
- **M2**: 壁の律速は人間の attention ルーティング (伝書鳩化)
- **M3**: herdr = agent multiplexer (working/blocked/done/idle の状態認識層、CLI/Socket API、detach 永続、SSH でモバイル巡回)
- **M4**: agmsg = SQLite 1ファイル mailbox のエージェント間直接通信 (サーバー不要、CLAUDE.md 規約1枚で3体チーム)
- **M5**: 実装とレビューを別モデルに分離 (self-review の甘さ回避 + サブスク消費枠の分散)
- **M6**: 層モデル (emulator / multiplexer / agent multiplexer / agent messaging) — tmux vs cmux vs herdr は競合でなく層が違う
- **M7**: blocked 優先ジャンプを1キーに (herdr agent list → focus、blocked がなければ idle 巡回)
- **M8**: idle 10分超を launchd 5分毎チェック → macOS 通知
- **M9**: 成果物を herdr pane split + nvim --remote で開く、逆方向は選択範囲を `@path#L10-L25` 形式で隣 pane に送る
- **M10**: キーマップを層で統一 (無修飾=pane / shift=workspace / 左option=tab)、Ghostty `macos-option-as-alt = left`
- **M11**: worktree = 同一 workspace 内の新 tab (pane=一時作業 / tab=worktree / workspace=プロジェクト)
- **M12**: "let Claude kick off Claude" — ループとルーチンへの分解

## Phase 1.5 Saturation Gate

判定: PASS (warning)。family = multi-agent-orchestration (N=17+)。採用率は直近5件で 3/5 (>=20%)。Step4.5 連続 reject trend は直近3件 07-25(採用1)/07-22(採用0)/07-08(採用2) で発火せず。Step7 Stale-Plan Audit は直近3件すべて30日未満のため skip。

飽和 family だが本記事はパターン論でなく道具層 (herdr/agmsg) の角度である点を明記する。

## Phase 2 判定表

**Gap/Partial/N/A**:

- **M6 層モデル明文化 = Gap**。`terminal-tooling.md` は Ghostty/cmux/aerospace の3層、`.tmux.conf:1-3` は tmux=SSH専用と明記している。しかし `.config/claude/references/cmux-ecosystem.md` の herdr 言及は grep 0件。`scripts/runtime/herdr-launch-worker.sh` と `herdr-collect-result.sh` が実在するのに参照元は自己参照のみ。CLAUDE.md は hub-and-spoke 委譲を cmux 版 launch-worker.sh に一本化したままで、二重パイプラインが無宣言で並走している。
- **M7 blocked 横断ジャンプ = Gap**。herdr CLI に agent list/get/read/send-keys/prompt/focus/wait/explain が実在する。dotfiles 側は `herdr-collect-result.sh:80-96` が単一 pane の blocked 検出をするのみで、全 pane 横断一覧はない。
- **M4 agmsg = N/A (非採用維持)**。当初 Partial (再評価候補) と判定したが、Phase 2.5 の Codex 批評で降格した。
- **M8 idle 検出 = Partial**。`patrol-agent.sh` + `com.claude.patrol-agent.plist` (5分間隔) + `cmux-notify.sh` は完備しているが、検出対象は headless `claude -p` の stall で ps etime/cpu ヒューリスティックを使う。herdr の agent_status は見ていないため、対話 pane の放置は検出圏外にある。
- **M9 nvim 連携 = Gap (低優先)**。sidekick.nvim / `nvim --remote` ともに grep 0件。nvim 側は avante.nvim (provider=copilot) で Claude Code/herdr とは無関係。`keybindings.json` の ctrl+e は `chat:externalEditor` で用途が別。
- **M1 Steps of AI Adoption = N/A 寄り**。`governance-levels.md` の4段階は AutoEvolve の自動化権限レベルで軸が別。記事の段階論は mechanism を持たない framing 文書で、「static-checkable rules は mechanism に寄せる」原則と衝突する。
- **M11 worktree の tab 割当 = N/A**。dotfiles は cmux workspace 1 : worktree 1 で確定済み (`cmux-worktree-daemon.sh` + `Taskfile.yml:332-346` + `.config/zsh/functions/worktree.zsh`)。

**Already 強化分析**:

- **M3 herdr 本体 = Already (強化不要)**。skill 302行 (`.config/claude/skills/herdr/SKILL.md`) + `herdr-launch-worker.sh` + `herdr-collect-result.sh` + `.config/zsh/tools/herdr.zsh` 補完 + `settings.json:338` の integration hook。記事より深く配線済みである。
- **M5 実装/レビューのモデル分離 = Already (強化不要)**。Codex Review Gate (codex-reviewer + code-reviewer 並列) が CLAUDE.md と `workflow-guide.md:386-461` で必須化済み。
- **M12 Claude kicks off Claude = Already**。ralph-loop skill / cron / launchd / `references/scheduling-decision-table.md` の /goal。2026-06-17 loops-with-claude absorb で「既存資産で網羅済み・採用0」と照合済み。
- **M10 キーマップ層 = Already (強化可能だが低優先)**。`.config/ghostty/keybind.conf` の SAND ニーモニック体系、`macos.conf:124` に `macos-option-as-alt = ` (空値)。`docs/wiki/concepts/terminal-tooling.md:14,36` に3層構成の設計意図がある。

## Phase 2.5 Refine

Codex (gpt-5.6-terra, sandbox read-only) の批評を採用した。Gemini は IneligibleTierError (individuals sunset) のため経路 degraded、Codex 単独批評であることを明記する。

初回の長文プロンプトは 600s で空出力 (memory `feedback_codex_bash_tool_unreachable` の silent-exit 事例)。短縮プロンプトで再試行し成功した (57,718 tokens)。

Codex の5点:

1. cmux/herdr は片寄せず使い分けを文書化すべき。cmux=worktree隔離/長時間/複数モデル、herdr=状態認識/対話介入/承認待ち対応。herdr 版は `--worktree` 未対応なので統合は機能後退になる。
2. conductor 中継は正当で、agmsg 再評価は不要。conductor は単なる伝書鳩ではなく役割分担・結果比較・撤退判断を担う集約点である。直接通信は spoke 間の反復往復や非同期依存が恒常化し、conductor の文脈・待ち時間が実測でボトルネック化してからでよい。`multi-agent-coordination-patterns.md:131-151` の Message Bus 非採用は妥当。
3. herdr 状態は停滞検出の補助信号として拡張価値がある。ただし working が長いだけで異常扱いせず、working継続 + 出力無変化 + 経過時間の複合条件に限る。
4. blocked への1キー跳躍は作る価値がある。単一ユーザーでも承認待ちは「気づいて操作する」までがクリティカルパスになる。ただし独自の状態DBは作らず、herdr の状態をそのまま使う。
5. 最優先は起動ルーティング規約。二重実装そのものより「選択が担当者の記憶依存」であることが最大リスクである。

判定変更: M4 を Partial(再評価候補) → N/A(非採用維持) に降格した。

## 実測で確認した事実 (verbatim 確認済み)

- herdr は nix 経由でインストール済み・実使用中 (`nix/flake.nix:17` `herdr.url = "github:ogulcancelik/herdr"`、`nix/home/default.nix:51`)。`~/.config/herdr/session-history.json` 221KB。
- 分析時点で 7 体のエージェントが 4 workspace で稼働 (agent_status: working 3 / idle 4、claude 6 + cursor 1)。`herdr agent list` は JSON で agent_status / pane_id / workspace_id / terminal_title を返す。
- `scripts/runtime/herdr-launch-worker.sh:15` に `# ponytail: --worktree は未移植。worktree 分離が要る場合は cmux 版 launch-worker.sh を使う` が既存する。使い分け規約はコード内コメント1行にしか存在せず、reference には一切ない — これが M6 Gap の直接の裏付けになる。
- cmux 版 `launch-worker.sh:33,80-84` は `--worktree` オプションを持ち `/tmp/cmux-worktrees/` に `git worktree add` する。
- `~/.config/herdr/config.toml` は `nix/home/default.nix:113` の outLink (mkOutOfStoreSymlink) で `dotfiles/.config/herdr/config.toml` を指す。つまり live 編集が即反映され `nix:switch` は不要になる。
- config.toml に既に `previous_agent = "prefix+,"` / `next_agent = "prefix+."` / `focus_agent = "prefix+alt+1..9"` が設定済み。さらに `agent_panel_sort` に "spaces"(既定) と "priority"(attention queue) の2択が native で存在する (現在コメントアウトで spaces)。
- config.toml は `[[keys.command]]` でカスタムコマンドを `type = shell/pane/popup` で束縛できる (既に prefix+f=file viewer / prefix+alt+g=lazygit / prefix+alt+d=hunk が稼働)。
- `~/.claude/hooks/herdr-agent-state.sh` は herdr 自身が `herdr integration` で設置・管理するファイル (ヘッダに "installed by herdr / managed by herdr" と明記) であり、dotfiles 未追跡は正常である。dotfiles 側 `settings.json:338` は `[ -x ] && ... || true` でガード済み。
- `.cursor/hooks.json:6` が参照するパスは `/Users/shogo_takeuchi/.cursor/herdr-agent-state.sh` で、このマシンのユーザー名 (takeuchishougo) と不一致 — 別マシン (勤務先) 向けの可能性があり、要ユーザー確認。未検証事項として記録する。

## Phase 3 Triage 結果

ユーザーは M6 / M7 / M8 / M9 の 4 件すべてを採用選択した。

## Phase 4 統合プラン

- **T1 [S] M6 起動ルーティング規約の明文化** — `.config/claude/references/cmux-ecosystem.md` に herdr 節を新設し、cmux=worktree隔離/長時間/並列、herdr=状態認識/対話介入/承認待ち対応の使い分けと herdr 版 `--worktree` 未対応を明記する。`.config/claude/references/subagent-vs-cmux-worker.md` の判定表に herdr 行を追加する。Codex 最優先。
- **T2 [S] M7 blocked 優先ジャンプ** — ponytail ラダーに従い、(1) まず `.config/herdr/config.toml` で `agent_panel_sort = "priority"` を有効化し、既存の `next_agent` (prefix+.) で attention queue 巡回になるか実機確認する。(2) 不足する場合のみ `herdr agent list --json` を jq で filter して `herdr agent focus` する薄いスクリプトを `scripts/runtime/` に置き、`[[keys.command]]` `type="shell"` で束縛する。独自の状態DBは作らない。
- **T3 [M] M8 停滞検出の herdr 状態拡張** — `scripts/runtime/patrol-agent.sh` に `herdr agent list` ベースの補助信号を追加する。判定は Codex 指示どおり「working継続 + 出力無変化 + 経過時間」の複合条件に限定し、working の長さ単独では発火させない。通知は既存 `cmux-notify.sh` を再利用する。
- **T4 [M] M9 nvim 連携** — herdr pane split + `nvim --remote` で成果物を開くスクリプトと、nvim の選択範囲を `@path#L10-L25` 形式で隣 pane に送る keymap を作る。低優先、T1-T3 完了後に着手判断する。

**依存関係**: T1 は独立。T2 は独立 (config 1行から)。T3 は T2 の agent list 経験を流用できるが必須依存ではない。T4 は独立。

**規模合計**: L (T1+T2 は S 2件、T3+T4 は M 2件)。

## 未検証事項 / 注意

- `agent_panel_sort = "priority"` にしたとき `next_agent` が panel 順に追随するかは未検証 (公式ドキュメント未確認、実機確認が必要)。
- `.cursor/hooks.json` のユーザー名不一致は意図的 (勤務先マシン向け) の可能性があり、ユーザー確認前に修正しないこと。
- tumf のメモリ実測値 (12.6倍、4.5MB vs 56.3MB) は記事経由の二次情報で未検証。採用判断の根拠には使っていない。
- Gemini 批評は取得できていない (IneligibleTierError)。Codex 単独のセカンドオピニオンである。

## 教訓

- 飽和 family (multi-agent-orchestration N=17+) でも、パターン論でなく「自分が既に入れた道具の未文書化領域」を突く記事は delta が出る。本件の Gap 2件はいずれも記事の新規性ではなく、記事の framing が dotfiles 内の drift (herdr 導入が reference に未反映) を露出させたことによる。
- ponytail ラダーは absorb にも効く。M7 は「スクリプトを書く」前に config 1行 (`agent_panel_sort = "priority"`) と native の `[[keys.command]]` を確認すべきだった。記事の手法をそのまま移植すると自作スクリプトから始めてしまう。
- 記事が推す新ツール (agmsg) は Codex 批評で明確に非採用維持となった。「見る」の Gap は実在し「話す」の Gap は実在しない、という非対称が本 absorb の結論である。
