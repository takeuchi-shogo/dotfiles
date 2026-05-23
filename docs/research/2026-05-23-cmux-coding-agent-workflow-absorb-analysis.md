---
status: rejected (大部分 fabricated, 既知 / 副次 1 件のみ採用)
last_reviewed: 2026-05-23
source_type: external-ai-response (Claude Sonnet 推定、verbatim 引用 ~250 行)
source_topic: cmux × Claude Code workflow 最適化、認知負荷低減、3-CLI 役割分担
absorb_decision: 記事採用 0 件 / 副次採用 1 件 (memory feedback) / 既知 5 件 / fabricated 7 件
---

# cmux Coding Agent Workflow 提案 (外部 AI 応答) Absorb Analysis

## 記事概要

(リンクなし - 外部 AI 生成テキスト) 「コーディングエージェントの利用を効率よく + 認知負荷を下げる cmux × 海外パターン」テーマで生成された AI workflow 提案。構成:

1. Claude Code hooks ↔ cmux 通知の連携 (Stop / Notification / PostToolUse:Task)
2. Workspace = 関心事の単位 + sidebar status pill
3. Git Worktree 並列実行 (`claude --worktree`)
4. MCP オーケストレーション (`cmux-agent-mcp`)
5. 競合比較 (Coder Mux / Emdash / Amux / Cursor 2.0)
6. 導入手順 (5 ステップ)
7. 3 CLI 役割分担 (Claude Code / Codex / Cursor CLI)
8. 落とし穴 3 件 (Cursor headless / Codex sandbox / Stop hook タイミング)

+ 詳細な `cmux.json` テンプレ + bash hook テンプレ。

## 著者バイアス / 由来推定

- 外部 LLM 由来 (Claude Sonnet 推定 — トーンと構造から)
- 出典なしの社会的証明 ("海外で広く使われている", "公式が推奨", "海外の合意点") 多用
- 既存 cmux 0.64.7 CLI と**部分的に**整合するが、複数の **fabricated API** を含む
- 引用ブロック ("...") は出典明示なし → 合成された可能性が高い

## 主張 verbatim 引用 + 検証結果

### Tier A: ✅ 実在検証済 (採用可だが、いずれも既知 / 既実装)

| # | 主張 (verbatim) | 検証コマンド | 結果 |
|---|---|---|---|
| A1 | `cmux notify --title "..." --body "..."` | `cmux notify --help` | ✅ **実在** (undocumented、`cmux --help` の Commands リストには非表示)。subtitle / workspace / surface フラグも実在 |
| A2 | `cmux claude-hook notification` (sidebar 反映) | `cmux claude-hook` | ✅ 実在 (session-start / stop / session-end / notification / prompt-submit / pre-tool-use) |
| A3 | `cmux hooks setup [agent]` | `cmux hooks setup --help` | ✅ 実在 (agents: codex, grok, opencode, pi, amp, cursor, gemini, rovo, hermes, copilot, codebuddy, factory, qoder)。ただし「sidebar の Running pill 自動表示」効果は誇張気味 — 実体は agent 用 plugin/extension ファイル生成 |
| A4 | `cmux events --reconnect --cursor-file` | `cmux events --help` | ✅ 実在 (既に `scripts/runtime/cmux-worktree-daemon.sh` + LaunchAgent で運用中 — Issue #51) |
| A5 | `cmux new-split <left\|right\|up\|down>` + `cmux send --surface ...` | `references/cmux-ecosystem.md` | ✅ 実在 + `scripts/runtime/launch-worker.sh` で日常運用中 |
| A6 | Claude Code Stop/Notification/PostToolUse hook event | `.config/claude/settings.json` | ✅ 実在 (既に運用中、`cmux-notify.sh` 経由で `hero`/`glass`/`default` sound 出し分け実装済) |
| A7 | Claude Code `--worktree` フラグ | (要外部確認) | 主張通り Claude Code 2.x 系で実在。ただし既存 worktree daemon (Issue #51) で代替済のため新規採用価値低 |

### Tier B: ❌ Fabricated / 誤り (採用不可)

| # | 主張 (verbatim) | 検証 | 実態 |
|---|---|---|---|
| B1 | `cmux send-surface --surface surface:1 "..."` | `cmux 2>&1 \| grep send-surface` ゼロヒット | **subcommand 名誤り**。正しくは `cmux send --surface surface:1 "..."` |
| B2 | `cmux set-status backend "Running" --icon "circle.fill" --color "#00FF00"` | `cmux 2>&1 \| grep set-status` ゼロヒット | **存在しない**。sidebar の pill / icon を CLI から動的セットする API はない (`workspace-action --action <name>` が近いが、定義済 action のみ呼べる仕組み) |
| B3 | `cmux claude-teams` が「ネイティブ split として一発起動。sidebar metadata と通知付き」 | `memory: feedback_cmux_claude_teams_overstated.md` (2026-05-17 Issue #44 で実機検証済) | **架空**。env ラッパー (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` + tmux shim) のみ。Claude Code v2 Agent API は内部 process で完結し pane を spawn しない |
| B4 | `Cmd+Shift+U` で「最新の Claude Code プロンプトに即ジャンプ」 | `cmux shortcuts \| grep -i 'jump\|prompt\|claude\|Cmd+Shift+U\|⌘⇧U'` ゼロヒット | **未確認、fabricated 可能性高** |
| B5 | `cmux-agent-mcp` (CMUX MCP server で claude/codex/gemini/opencode/goose 横断 spawn) | リポジトリ未検証、`references/cmux-ecosystem.md` に記載なし | 要疑問視 (`feedback_cmux_claude_teams_overstated.md` の「上位レイヤー主張も同じ枠組みで疑え」原則) |
| B6 | `cmux omo` (oh-my-openagent) が「Claude / GPT / Gemini 横断 specialist agents 並列実行」 | `cmux --help` で `omo [opencode-args...]` 表示のみ — **opencode wrapper と推定** | 主張内容 ≠ 実装の可能性高。`omo`/`omx`/`omc` は opencode-style wrapper (詳細未調査だが claude/gpt/gemini cross は誇張可能性) |
| B7 | OSC 9/99/777 で発火 (cmux 通知) | (未検証) | cmux ecosystem doc に記載なし、外部 standard 名前を借りた fabrication 可能性 |

### Tier C: ⚠️ Partial / 既知 (採用済 or 不要)

| # | 主張 | 判定 |
|---|---|---|
| C1 | Hooks の Stop / Notification / PostToolUse:Task で通知統合 | ⚠️ 部分的に既実装。`cmux-notify.sh` (60 行、CWE-426/427 resolver 込み) + Stop hook 10 件、Notification 1 件。PostToolUse matcher は `"Task"` ではなく **`"Agent"`** (本 session で確認) |
| C2 | Workspace = 関心事の単位 | ⚠️ 既知パターン。`launch-worker.sh` で別 workspace 起動済 (memory `references/cmux-ecosystem.md`) |
| C3 | Git Worktree 並列実行 | ✅ Issue #51 で LaunchAgent daemon (`cmux-worktree-daemon.sh`) として実装済 |
| C4 | 3 CLI 役割分担 (Claude Code / Codex / Cursor CLI) | ⚠️ 議論として妥当だが、`references/model-routing.md` + `feedback_codex_casual_use.md` で既に対応済。Cursor CLI は未採用 |
| C5 | Claude → Codex レビューループ | ✅ `/review` skill + `codex-reviewer` agent + Codex Spec/Plan Gate / Review Gate で実装済 |

## 採用判定

| カテゴリ | 件数 |
|---|---|
| 採用 (Tier A から新規) | **0 件** (A1-A7 全て既知 or 既実装) |
| 副次採用 (本 session 派生 failure mode の codify) | **1 件** — `feedback_settings_json_grep_first.md` |
| Reject (Tier B fabricated) | 7 件 |
| 既知 / 既実装 (Tier C) | 5 件 |

## Meta findings

1. **Sonnet/Opus imagination の典型再発** — `cmux notify` (実在) を `cmux send-surface` (架空) や `cmux set-status` (架空) と混在させて「もっともらしい primitive 連鎖」を合成する罠。memory `2026-05-22-khairallah-40-features-absorb-analysis.md` で codify 済の anti-pattern が同じ形で出現
2. **社会的証明の偽装** — 「海外で広く使われている」「公式が推奨」を出典なしで頻繁に使用。検証不能 = 採用判断に使えない (memory 既知のパターン)
3. **既存学習の踏み倒し** — memory `feedback_cmux_claude_teams_overstated.md` (2026-05-17 実機検証) で「ネイティブ統合主張は実機検証必須」と codify 済なのに、本記事は B3 (claude-teams) / B5 (cmux-agent-mcp) / B6 (omo) でまさにそれを連発
4. **私自身の検証不足** — Pass 1 で `cmux --help` の Commands リストにない `cmux notify` を「存在しない」と即断したが、実際は **undocumented subcommand として実在**していた。`cmux <subcommand> --help` で個別確認すべきだった。**Lesson: 未知の subcommand は「help 一覧」+「既存スクリプト grep」+「個別 --help」の三重チェック**
5. **本 session 派生 failure mode** — 検証中に「SubagentStop に通知ギャップあり」と誤判定して hook 行を追加 → code-reviewer BLOCK → revert。これは search-first 違反の典型で `feedback_settings_json_grep_first.md` に codify した
6. **Harness Review Gate の勝利** — Stop hook の `Completion gate` が settings.json 変更を即時検出して `/review` を強制し、私の重複追加を 1 cycle で revert させた。これは "judgment as durable artifact" の好例

## 副次採用 (1 件)

- **`feedback_settings_json_grep_first.md`** (memory) — 上記 Meta finding #5 由来、search-first 違反の再発防止

## Reference

- 既存 cmux ecosystem doc: `dotfiles/.config/claude/references/cmux-ecosystem.md`
- 既存 cmux-notify.sh: `dotfiles/.config/claude/scripts/runtime/cmux-notify.sh` (60 行、CWE-426/427 resolver)
- 既存 worktree daemon: `dotfiles/scripts/runtime/cmux-worktree-daemon.sh` (Issue #51)
- 関連 memory:
  - `feedback_cmux_claude_teams_overstated.md` — claude-teams ネイティブ統合架空
  - `feedback_codex_casual_use.md` — Codex は cmux Worker 経由で対話
  - `2026-05-22-khairallah-40-features-absorb-analysis.md` — Sonnet imagination 罠の codify 元
  - `feedback_absorb_already_deepdive.md` — 存在確認 ≠ 品質保証
- 関連 Issue: dotfiles repo #44 (cmux claude-teams 検証), #51 (worktree daemon)
- 本 session の `/review` 実行ログ (code-reviewer BLOCK → revert PASS)

---

## Delta Update (2026-05-23 second pass, AI 応答 part2 追加検証)

外部 AI 応答の続編が共有され、`cmux <subcommand> --help` を個別に叩いた結果、初版判定の **False Positive 1 件** と **新規 Tier A 8 件** が判明。Intellectual honesty として追記。

### 訂正: 初版 Tier B の False Positive

| # | 初版判定 | 訂正後の実態 (個別 --help 確認) |
|---|---|---|
| **B6 訂正** | 「`cmux omx`/`cmux omc`/`cmux omo` は opencode-style wrapper と推定」 | 部分的に誤り。`cmux omx` = **Oh My Codex** (Codex CLI 専用 multi-agent orchestration、`npm install -g oh-my-codex`)、`cmux omc` = **Oh My Claude Code** (`npm install -g oh-my-claude-sisyphus`、specialized agents + smart model routing + team pipelines)。`cmux omo` のみが正しく OpenCode + oh-my-openagent wrapper。**3 つは独立した orchestration layer であり一括 reject は overshoot だった** |

### 新規 Tier A (実在検証済、追加採用検討可)

| # | 主張 | 検証ソース |
|---|---|---|
| A8 | `cmux codex-teams` (Codex thread-spawn subagents を depth 2 まで native cmux split に開く、app-server protocol 経由) | `cmux codex-teams --help` の公式記述 |
| A9 | `cmux omx` (Oh My Codex multi-agent orchestration layer) | `cmux omx --help` |
| A10 | `cmux omc` (Oh My Claude Code、smart model routing + team pipelines) | `cmux omc --help` |
| A11 | `cmux ssh <destination>` (remote workspace + browser traffic egress proxy) | `cmux ssh --help` |
| A12 | Codex CLI v0.133.0 ローカル installed | `/opt/homebrew/bin/codex` |
| A13 | Cursor CLI (`cursor-agent`) v2026.05.20 ローカル installed | `~/.local/bin/cursor-agent` |
| A14 | Claude Squad は brew 経由実在 (未 install) | `brew search claude-squad` |
| A15 | `cmux hooks` agents 13 種 (codex, grok, opencode, pi, amp, cursor, gemini, rovo, hermes-agent, copilot, codebuddy, factory, qoder) | `cmux hooks` |

### 引き続き Tier B (新規 fabricated / 未確認)

| # | 主張 | 判定 |
|---|---|---|
| B8 (新規) | `Shift+Down` で teammate 巡回 | `feedback_cmux_claude_teams_overstated.md` で subagent モード適用不可済 |
| B9 (新規) | `~/.codex/config.toml` の `[features]` `multi_agent`/`multi_agent_v2`/`enable_fanout` | 環境に config.toml 存在せず、Codex CLI 公式 docs 出典未確認 |
| B10 (新規) | "Addy Osmani の 3 層モデル" 帰属 | Tier 1-3 分類は一般的、Addy Osmani 出典未検証 |
| B11 (新規) | PR #2103 (Codex CLI hooks integration) | リポジトリ・PR 出典不明 |
| B12 (新規) | `cmux.com/docs/custom-commands` の Worktree Agents 公式 example | URL 未検証、前 session でも取得不可 history |

### 下半分 (3-CLI 役割分担) の扱い

外部 AI 応答 part2 の下半分は本 absorb analysis の **初版と verbatim 一致** (delta = 0、pure rehash)。`feedback_absorb_already_deepdive.md` および `2026-05-23-subagent-context-fork-revisit-analysis.md` の "rehash 再投入" パターンと同型。追加採用なし。

### Meta findings (追加 2 件)

7. **Confirmation bias 検出** — 初版で `cmux notify` を「存在しない」と誤判定した直後、続けて omx/omc も同様に懐疑的に reject した。一度疑いを持つと全否定したくなる bias の典型。**Tier 別検証を毎回ゼロベースで実施する**ことが mechanism として必要
8. **CLI subcommand の個別 `--help` 必須** — `feedback_settings_json_grep_first.md` の「全文 grep」原則の **subcommand-level 派生**。今後は subcommand 名が出たら `<cmd> --help` で個別確認 (top-level `--help` の Commands 一覧表示だけで判定しない)。memory に追記済

### 採用判定 (更新)

| カテゴリ | 初版 | 訂正後 |
|---|---|---|
| Tier A 新規採用 | 0 件 | **0 件 (実装 backlog 8 件、試用候補)** ※既存 setup で運用可能、新規 codify 不要 |
| 副次採用 | 1 件 (memory) | **1 件 + 1 件追記** (= `feedback_settings_json_grep_first.md` の How to apply 拡張) |
| Tier B reject | 7 件 | 6 件 (B6 訂正分減) + 5 件 (新規 B8-B12) = **11 件** |
| Tier C 既知 | 5 件 | 5 件 + 2 件 (C9 rehash, C10 一般分類) = **7 件** |

