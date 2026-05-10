---
source: "@zodchixquant 「15 Claude Code Settings Most Developers Never Touch (And Why They Should)」"
date: 2026-05-10
status: integrated
---

## Source Summary

**主張**: Anthropic は 2026 年 3 月に Claude Code のデフォルト thinking effort を high → medium に下げた。これに気付かず「モデルが劣化した」と誤解する開発者が多い。env vars 2 個と settings.json 修正で「pre-February quality」を取り戻せる。15 設定の包括チェックリストを提示。

**手法 (15 項)**:
1. `/effort high` slash + `CLAUDE_CODE_DEFAULT_EFFORT=high` env var
2. `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` env var
3. `permissions.defaultMode: "acceptEdits"` (6 modes 主張)
4. allow/deny rules
5. `/model` mid-session 切り替え
6. `/compact <custom-instructions>`
7. `/memory add` で手動学習
8. PostToolUse auto-format hook (`Write(*.ts)` matcher 形式)
9. PreToolUse log filter hook (`Bash(cat *log*)` matcher 形式)
10. `claude -w` (worktree isolation)
11. `claude --bare` (高速起動)
12. `claude -p ... --max-budget-usd 5.00` (CI 予算上限)
13. `showThinkingSummaries: true`
14. parallel subagent 数の prompt 内明示
15. `/mcp` で MCP token tax 監視

**根拠**: Anthropic engineering postmortem (april-23) で March 4 effort change が公式に確認できる。記事は「Boris Cherny on HN」と二次出典を捏造しているが、一次出典は実在。

**前提条件**: Claude Code v2.1+ で Opus 4.6/Sonnet 4.6 利用想定。Opus 4.7 は adaptive reasoning 強制のため env var 効果なし (記事漏れ)。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1a | `/effort high` slash | Already | mid-session 切替で運用可。実在 (cli-reference) |
| 1b | `CLAUDE_CODE_DEFAULT_EFFORT=high` | **Misnamed → Already (記事超え)** | 正式名は `CLAUDE_CODE_EFFORT_LEVEL`。settings.json:790 で `effortLevel: "xhigh"` (high より上) を persistent 設定済み |
| 2 | `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` | Already (caveat あり) | settings.json:8 で設定済み。**ただし Opus 4.7 では no-op** (公式 docs: "Has no effect on Opus 4.7, which always uses adaptive reasoning") — 記事漏れ |
| 3 | `permissions.defaultMode: "acceptEdits"` | N/A | 6 modes 主張は実在。ただし当 setup は `disableBypassPermissionsMode: "disable"` で bypass 系を harness レベルで禁止し、84 allow + 127 deny で厳格運用。`acceptEdits` 化は harness 思想と相反 |
| 4 | allow/deny rules | Already | settings.json line 16-177 で 84 allow + 127 deny 完全実装 |
| 5 | `/model` 切り替え | Already | references/model-routing.md で運用 |
| 6 | `/compact <instructions>` | Already | references/compact-instructions.md で steering 運用 |
| 7 | `/memory add` | Already | MEMORY.md + 3 層スコープ (user/project/local) で運用 |
| 8 | PostToolUse auto-format hook | Already | claude-hooks (Rust) format pipeline (settings.json:434-694) |
| 9 | PreToolUse log filter (`Bash(cat *log*)`) | **Misnamed + Partial** | hook docs: `matcher` は tool/event 名のみ、引数 glob は `if` 構文。9 個 PreToolUse hook あり、log 特化なし |
| 10 | `claude -w` worktree | Already | `.claude/worktrees/{purring-noodling-haven, spike+memory-vector}` で実運用中 |
| 11 | `claude --bare` | Gap (低価値) | 実在。ただし auto-discovery 全 skip = CLAUDE.md/skill/hook を活かす当 harness と相反 |
| 12 | `claude -p ... --max-budget-usd` | Gap (将来用) | 実在 (print mode only)。現在 CI 自動化なし |
| 13 | `showThinkingSummaries: true` | Gap (検討余地) | 実在。常時 ON は冗長性 ↑ なので debug 時のみ有効化が妥当 |
| 14 | parallel subagent 数明示 | Partial | references/model-routing.md に並行戦略あるが上限値なし |
| 15 | `/mcp` で token 監視 | Already | mcp-audit.py (settings.json:407-411) で audit + scope 制御 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | settings.json:8 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` | Opus 4.7 では no-op だが、設定値を見ても気付けない | settings.json comment or references で caveat を明示 | 強化可能 (ユーザー判断: 棄却) |
| S2 | settings.json:790 `effortLevel: "xhigh"` | 記事の `high` より高い設定だが意図不明 | xhigh 採用根拠を 1 行 documentation | 強化可能 (ユーザー判断: 棄却) |
| S3 | references/model-routing.md (subagent 並行戦略) | 並行数上限なし | "max parallel = 3-5" 等の guidance 追加 | 強化可能 (Pruning-First で見送り) |
| S4 | mcp-audit.py | token tax (per-server overhead) 監視なし、危険操作 block のみ | tool 数 + estimated token 計算を audit log に追加 | 強化可能 (Pruning-First で見送り) |

## Refine 経路 (Phase 2.5)

3 経路で交差検証:
- **Sonnet Explore**: 既存 setup 照合 (Already 8/Partial 3/Gap 4 と判定 — Codex 検証で多くが Real と判明し再評価)
- **Codex (gpt-5.5)**: 一次ソース URL 提示 (15 主張中 Real 8/Misnamed 4/Fabricated 1/Plausible 1/Inconclusive 1)
- **公式 docs WebFetch 直接**: code.claude.com/docs/en/{env-vars, cli-reference, settings} と www.anthropic.com/engineering/april-23-postmortem を verbatim 確認

**Codex/Gemini 並列の役割**: Gemini は API rate limit でフォローアップ取得失敗。代替に Opus が直接 WebFetch で公式 docs (`code.claude.com`) を逐語確認。Codex 判定がほぼ正確だった。

### 重要な事実修正

1. **`CLAUDE_CODE_DEFAULT_EFFORT` は存在しない env var** — 正式名は `CLAUDE_CODE_EFFORT_LEVEL` (precedence: env > `/effort` > settings `effortLevel`)
2. **「Boris Cherny on HN」は出典捏造** — 一次出典は Anthropic engineering "april-23-postmortem" で「On March 4, we changed Claude Code's default reasoning effort from `high` to `medium` to reduce the very long latency」
3. **`CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` は Opus 4.7 では no-op** — 公式 docs に明記、記事は重大な caveat を漏らしている (現主モデル Opus 4.7 では env var が効果なし)
4. **`permissions.defaultMode` は 6 modes 実在** — `default/acceptEdits/plan/auto/dontAsk/bypassPermissions` (Opus の事前知識 4 modes は古かった)
5. **hook matcher 構文** — `Write(*.ts)` / `Bash(cat *log*)` 風の引数 glob は `matcher` ではなく `if` キーで書く

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | `--bare` 高速起動 | スキップ | auto-discovery 全 skip = CLAUDE.md/skill/hook 活用ハーネスと相反 |
| 2 | `--max-budget-usd` CI 予算上限 | スキップ | 現在 CI 自動化なし、必要時に再検討 |
| 3 | `showThinkingSummaries` debug 用 | **採用** | 常時 ON は冗長性 ↑ だが、debug 時の thinking 全表示は価値あり。運用ガイドを追加 |
| 4 | `acceptEdits` defaultMode | スキップ | harness 思想 (`disableBypassPermissionsMode: "disable"`) と相反 |
| 5 | log filter hook | スキップ | 必要時に追加可、現在 friction なし |
| 6 | parallel subagent 上限値明示 | スキップ | 現運用 friction なし |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | DISABLE_ADAPTIVE_THINKING の Opus 4.7 caveat 注記 | スキップ | ユーザー判断: dotfiles 変更せず、本レポートに記録のみ |
| S2 | `effortLevel: xhigh` 採用根拠 documentation | スキップ | 同上 |
| S3 | model-routing.md に並行数上限 | スキップ | Pruning-First |
| S4 | mcp-audit に token tax 計算 | スキップ | Pruning-First |

## Plan

### Task 1: showThinkingSummaries 運用ガイド作成
- **Files**: `references/debug-thinking-summary.md` (新規, ~50 行)
- **Changes**: 設定の意味、いつ ON にするか、CLI flag 一時 ON、副作用 (UI 冗長化)、Opus 4.7 における thinking redaction の仕組みを記述
- **Size**: S (1 ファイル)

### Task 2: 分析レポート保存
- **Files**: `docs/research/2026-05-10-zodchixquant-15-settings-absorb-analysis.md` (本ファイル, 新規)
- **Changes**: 本分析結果の永続化
- **Size**: S (1 ファイル)

### Task 3: MEMORY.md ポインタ追記
- **Files**: `MEMORY.md` (1 行追記)
- **Changes**: `## 外部知見索引` セクションに本レポートへの 1 行ポインタ
- **Size**: S (1 ファイル, 1 行)

## 教訓

1. **集客記事も技術主張は検証する**: zodchixquant の Telegram 誘導記事は集客バイアス強だが、15 主張中 8 件は公式 docs と整合 (March 4 effort change 含む)。著者バイアスで全棄却すると **真実を見落とす**。
2. **Codex の reasoning depth + 一次ソース要求は強力**: Sonnet Explore は「既存にない」を Gap と判定したが、多くは公式 docs に存在 (Real 8 件)。Codex の `code.claude.com` URL 提示で再評価できた。
3. **二次出典は積極的に疑う**: 「Boris Cherny confirmed on HN」は捏造。一次出典 Anthropic engineering blog に直接当たれば真偽が分かる。
4. **記事漏れの caveat こそ価値**: 記事採用ではなく、**記事が言わない caveat** (Opus 4.7 不適用、misnamed env var) を抽出することが最も価値が高い場合がある。本件はユーザー判断で dotfiles 注記せず、本レポートに記録のみ。
5. **Phase 2 Pass 1 (Sonnet) と Phase 2.5 (Codex) の役割分担が機能した**: Sonnet = 既存 setup 内側、Codex = 公式 docs 外側 + 一次出典追跡。Gemini が rate limit で失敗したが、Opus 直接 WebFetch でフォロー成功。
