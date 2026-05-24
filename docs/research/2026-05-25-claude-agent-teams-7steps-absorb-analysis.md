---
source: "How to Build a Claude Agent Team in 7 Steps: From Solo Chat to Parallel Workforce (Twitter listicle, unattributed)"
date: 2026-05-25
status: light-phase2-with-codex-correction
adopted: 1
family: claude-code-tips listicle / agent-orchestration (hybrid)
family_count_at_absorb: claude-code-tips=8, agent-orchestration=6
---

## Source Summary

**主張**: Claude Code は 3 レベル (Subagents / Agent View / Agent Teams) のエージェント機能を持ち、`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` で実験フラグを有効化すると lead agent が teammates を coordinate する parallel workforce が構築できる。`CLAUDE_CODE_SUBAGENT_MODEL` で Sonnet ルーティングしてコスト削減、`claude agents` で Agent View dashboard、settings.json permissions と `--max-budget-usd` で guardrails、`CLAUDE_CODE_DEFAULT_EFFORT=high` / `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` で推論モード調整。

**手法 (12 項目)**: 上記の主要 5 つの env/CLI 主張 + 3-level taxonomy + decision framework + team prompt template + permissions guardrails + BEFORE/AFTER 比較。

**根拠**: anecdotal BEFORE/AFTER (4-part feature 1 day → 2h) のみ、データなし。

**前提条件**: 並列で独立 or 緩く依存タスク、experimental flag に抵抗ない、シェル env 永続化可能。

## Phase 1.5: Saturation Gate

- **Family 判定**: hybrid
  - claude-code-tips listicle family: **N=8 件目** (Boris 30 / Three-Model / 12-rule / zodchixquant 15 / Khairallah 40 / Khairallah 30 / 18 settings / 本記事)
  - agent-orchestration family: **N=6 件目** (Distribution vs Escalation / 30 Sub-Agents / Self-Healing / Symphony / Subagent Context Fork / 本記事)
- **判定**: SATURATED-but-novel (delta=5 だが fabrication 高リスク)
- **ユーザー選択**: light-phase2 + WebSearch grounding

## Phase 1.6: WebSearch Grounding (5 つの env/CLI 主張の実在性検証)

WebSearch で 5 並列検証 → **5/5 すべて公式実在**を確認:

| 主張 | 実在性 | 公式制約 |
|------|--------|---------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | ✅ REAL | 2026-02 research preview、Claude Code v2.1.32+、`TeamCreate/TaskCreate/TaskUpdate/TaskList/SendMessage` tools 解放 |
| `claude agents` (Agent View) | ✅ REAL | 2026-05 research preview、Pro/Max/Team/Enterprise/API、`claude --bg` / `claude attach` 併用 |
| `--max-budget-usd N.NN` | ✅ REAL | print mode (`-p`) のみ、最低 ~$0.05 (system prompt cache creation cost)、CI/CD 想定 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | ✅ REAL | **built-in agents (Explore/Plan/general-purpose) には override 不可** という制約あり |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` | ✅ REAL | **Opus 4.6 / Sonnet 4.6 のみ有効、Opus 4.7 では no-op** |
| `CLAUDE_CODE_DEFAULT_EFFORT=high` | ❌ **MISNAMED** | 正式は `CLAUDE_CODE_EFFORT_LEVEL` env var or `/effort` slash command |

## Pass 1 + Pass 2: 統合判定テーブル

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 3-level agent taxonomy | Already (強化不要) | `references/distribution-vs-escalation.md` + `2026-05-02-30-subagents-2026` でカバー |
| 2 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | **Already** | `settings.json:4` で設定済 |
| 3 | Lead agent decompose prompt | Already (強化不要) | `subagent-delegation-guide.md` でカバー |
| 4 | `CLAUDE_CODE_SUBAGENT_MODEL` | **N/A** | Opus 1M lock-in (個人 dotfiles 方針)。built-in agents 非適用制約も |
| 5 | `claude agents` Agent View | **Partial → 採用 (境界注記)** | ~~「cmux で上位互換」は **Confirmation bias** (Codex 批評で指摘、Pass 2 訂正)~~。Agent View / Agent Teams は **session-level / single-model**、cmux は **process-level / multi-model** で別レイヤー。`SendMessage`/`TaskCreate` の peer coordination は cmux にない。**採用**: `subagent-vs-cmux-worker.md` に境界注記追加 (S 規模) |
| 6 | Sessions survive terminal closure | Already | cmux Worker で同等 |
| 7 | Orchestration decision framework | Already (強化不要) | `model-routing.md`, `distribution-vs-escalation` でカバー |
| 8 | settings.json permissions allow/deny | Already (強化不要) | `settings.json:17-192` で詳細 allow/deny 設定済 |
| 9 | `--max-budget-usd 15.00` | **N/A (再確認)** | `2026-05-10 zodchixquant 15-settings absorb` で「CI 自動化なし → スキップ」決定済、状況変わらず |
| 10 | `CLAUDE_CODE_DEFAULT_EFFORT=high` | **記事誤記** | 正式名は `CLAUDE_CODE_EFFORT_LEVEL`。dotfiles は `settings.json:815 effortLevel: "xhigh"` 採用済 |
| 11 | `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` | **N/A** | Opus 4.7 で no-op。`debug-thinking-summary.md` に 2026-05-19 意図的除外記録済 |
| 12 | BEFORE/AFTER anecdotal | N/A | データなし、根拠不足 |

**判定サマリ (Codex 批評後訂正)**: Already 5 件 / Partial 1 件 (採用) / N/A 4 件 / misnamed 1 件 / anecdotal 1 件 = **採用 1 件 S**

## Phase 2.6: Codex 批評 (Confirmation bias 自己点検)

light-phase2 で Phase 2.5 を省略したため、ユーザー指摘で **Codex (gpt-5.5, sandbox=read-only, effort=xhigh)** に独立批評を依頼。cmux Worker (`launch-worker.sh`) は terminal context なしで spawn 失敗 → `codex exec` 直接呼び出しに fallback。

### Codex の指摘

> 採用 0 の「運用追加なし」は概ね妥当。ただし **#5 の理由付けは修正すべき**。`cmux Worker で上位互換` は **追認バイアス寄り**。公式 docs 上も Agent View/Agent Teams は「Claude session の dashboard / shared task list + peer messaging」で、cmux の process-level / 異モデル orchestration とは別レイヤー。Agent Teams の直接通信・共有タスクは cmux にはない。

### 各 Q への回答

- **Q1 #5 Agent View 判定**: ✅ **Confirmation bias 確認**。境界注記追加を採用 (S 規模)
- **Q2 SUBAGENT_MODEL caveat**: ❌ 採用不要。`settings.json:196` が `opus[1m]` lock-in、将来 Sonnet routing 再開時に `model-routing.md` に追加で足りる (YAGNI)
- **Q3 Pass 2 強化判定**: ❌ 採用不要。#7 は `multi-agent-coordination-patterns.md` + `subagent-delegation-guide.md` が既に上位、#8 の `Write(src/**)` は現設定が broad Write を allow していないため **権限拡大リスク** (採用すると security 低下)
- **Q4 見落とし**: ❌ 採用不要。「cmux 不在時の `claude agents` fallback」は反復 friction が出るまで文書化不要

### Codex 推奨採用: 1 件 S

`.config/claude/references/subagent-vs-cmux-worker.md` に Agent View / Agent Teams / cmux の境界注記セクション追加。

## Integration Decisions

| # | 項目 | 判定 | ファイル |
|---|------|------|---------|
| T1 | Agent View / Agent Teams / cmux の境界注記追加 | **採用 S** | `.config/claude/references/subagent-vs-cmux-worker.md` |

**実装内容**: `subagent-vs-cmux-worker.md` の最下部に「Agent View / Agent Teams との境界」セクションを追加。3 レイヤー (cmux=process-level multi-model / Agent View=session dashboard / Agent Teams=peer messaging) の用途別併存を明示。`last_reviewed: 2026-05-25` に更新。

**スキップ理由 (他 11 主張)**:
- 5 つの env/CLI 主張は **すべて公式実在を確認**したが、dotfiles ですでに以下のいずれかで処理済:
  1. AGENT_TEAMS flag — `settings.json:4` で有効化済
  2. SUBAGENT_MODEL — Opus 1M lock-in 方針で N/A
  3. EFFORT — `effortLevel: "xhigh"` settings.json key で採用済
  4. DISABLE_ADAPTIVE_THINKING — Opus 4.7 no-op で意図的除外済 (drift なし)
  5. `--max-budget-usd` — CI 自動化なしで先送り済 (2026-05-10 既決)
- 残りの 6 主張 (taxonomy / decision framework / permissions 等) は references で既存カバー
- 記事誤記 (`CLAUDE_CODE_DEFAULT_EFFORT`) は dotfiles 内で正名で記録済、drift なし

## Validation-only Follow-up

dotfiles 内に記事 framing で露出した drift / stale fact は **なし**。
- DISABLE_ADAPTIVE_THINKING の Opus 4.7 no-op は 2026-05-19 に先取り対応済
- AGENT_TEAMS flag の `feedback_cmux_claude_teams_overstated.md` (2026-05-17) で「env ラッパー + tmux shim、native pane spawn なし」と棚卸し済
- CLAUDE_CODE_SUBAGENT_MODEL の built-in agents 非適用制約は dotfiles で未記載だが、Opus 1M lock-in で実害なく追記不要

## Meta-findings

1. **Phase 1.5 saturation gate + WebSearch grounding の効果実証**: light-phase2 + WebSearch 5 並列で fabrication 疑惑 5 件を約 30 秒で切り分け (実在 5、misnamed 1)。Phase 2.5 (Codex+Gemini 並列批評) の代替として **WebSearch grounding は実在性検証には十分だが、判定の Confirmation bias 検証には不足**。今回 Codex 単独批評 (Q1 のみ採用) を後追いで実施しないと #5 の追認バイアスを見逃した。
2. **light-phase2 の構造的限界 (今回学習)**: WebSearch grounding は「主張が実在するか」を検証できるが、「既存方針で実在主張を切り捨てる判定が正しいか」は検証できない。**WebSearch ≠ Phase 2.5 (異モデル批評)**。light-phase2 の Codex 省略は許容するが、ユーザーが「合理的判断か」と問うた時点で **Codex 単独批評を必ず回す** べき (Foundation の「正直に言え」+ Sonnet imagination 罠の Opus 版自己点検)。
3. **記事 framing は典型的 promotional pattern**: 7-step listicle + BEFORE/AFTER 煽り + 古いモデル ID + "👇" + "Thanks for reading!" + "Same tool. Same subscription." 訴求 = Twitter promotional テンプレート。**主張は実在しても dotfiles 既決の確率が極めて高い**ことを 2026-05 系の 8 件目で再確認。ただし **「既決」判定の質を保証するには Codex 批評が必要**。
4. **公式 research preview の急速展開**: AGENT_TEAMS (2026-02) + Agent View (2026-05) と 4 ヶ月で 2 つの実験機能リリース。dotfiles は両方とも前倒し対応済 (`settings.json:4` + `managed-agents-scheduling.md`)、cmux Worker との role-split は今回の境界注記追加で **session-level / process-level / multi-model** の 3 レイヤー明示が完成。
5. **listicle family saturation taxonomy 閾値の妥当性**: claude-code-tips family 8 件目、agent-orchestration family 6 件目。直近 listicle 採用率: 18-settings (2) / 30-workflows (2) / 40-features (0) / 12-rule (0) / Boris 30 (0) / 本記事 (1) → 中央値 1 件、threshold 据え置き妥当。light-phase2 + Codex 批評の組合せで N+1 件目の「採用候補の取りこぼし」を補正できる仕組みが機能した実例。
6. **cmux Worker spawn 失敗パターン**: `launch-worker.sh --model codex` を Claude Code 内部から呼ぶと `Error: invalid_params: Surface is not a terminal` で失敗。`codex exec --skip-git-repo-check -m gpt-5.5 --sandbox read-only --config model_reasoning_effort="xhigh"` への fallback は CLAUDE.md 既定通り。記録: feedback memory 化候補。

## Sources

WebSearch grounding 結果 (5 並列):
- AGENT_TEAMS: [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams), [GitHub Issue #35447](https://github.com/anthropics/claude-code/issues/35447)
- Agent View: [claude.com/blog/agent-view-in-claude-code](https://claude.com/blog/agent-view-in-claude-code), [code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference)
- `--max-budget-usd`: [linuxjedi.co.uk: When the Docs Fall Short](https://linuxjedi.co.uk/when-the-docs-fall-short-investigating-claude-codes-budget-cap/)
- EFFORT / DISABLE_ADAPTIVE_THINKING: [code.claude.com/docs/en/model-config](https://code.claude.com/docs/en/model-config), [bswen.com: Disable Adaptive Reasoning](https://docs.bswen.com/blog/2026-04-09-claude-code-adaptive-reasoning-settings/)
- SUBAGENT_MODEL: [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents), [GitHub Issue #34821](https://github.com/anthropics/claude-code/issues/34821)
