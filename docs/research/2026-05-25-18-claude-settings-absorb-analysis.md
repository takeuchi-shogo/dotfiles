---
date: 2026-05-25
source_type: telegram-promoted-listicle
source_url: (Telegram CTA only, no canonical URL)
source_title: "18 Claude settings that change everything. 14 are hidden 3 clicks deep. 4 aren't in any docs."
status: light-phase2-only
family: claude-code-tips
saturation_gate: SATURATED-but-novel
saturation_N: 13
saturation_adoption_rate_estimate: ~30%
trend_warning: true (直近 4 件中 3 件 reject 寄り)
delta: 2 confirmed + 2 ambiguous
adopt_count: 2
---

# /absorb 分析: 18 Claude settings listicle (2026-05-25)

## Source Summary

匿名著者の Telegram プロモ付きリスティクル (`t.me/+_ZWrQN7GuDA3ZDEy`)。18 個の「隠れた設定」を 3 セクションに分けて主張:

- **Section 1 (Claude.ai UI, 8 件)**: Memory scope / Extended Thinking toggle / Custom Styles / Project instructions / Past chats search / Web search citations / Cowork trusted folders / Incognito mode
- **Section 2 (Claude Code settings.json, 7 件)**: enabledPlugins / permissions.deny + bug / hooks.SessionStart / disableAllHooks / model per-project override / mcpServers enabled flag / cleanupPeriodDays
- **Section 3 (API/Console, 3 件)**: cache_control breakpoint / inference_geo / Workspace+per-feature rate limit

煽り要素: 「125+ keys, docs cover 40」「$340/月 → $87」「Three of these replaces 80% of my saved prompts」「Bookmark and walk the checklist tonight」「T H E _ E N D」。
zodchixquant 15 Settings (2026-05-10、採用 1) と同型パターン (「N 個の隠れ設定」listicle、Real 8 / Misnamed 4 / Fabricated 1)。

## Phase 1.5: Saturation Gate

- **Family**: `claude-code-tips` (`claude code tips` + `hidden` + `N tricks` + `cheat` の 4 キーワード hit)
- **N**: 13 件 (findy-tips / hermes-agent-tips / instructkr / 12-claude-features / boris-30tips / overhead-9patterns / 12-rule-claude-md / zodchixquant-15-settings / grown-metabolism / routines / large-codebase / khairallah-40-features / khairallah-30-workflows)
- **採用率**: ~30% (近半数は採用 0-2 件)
- **Step 4.5 連続 reject trend 副ガード**: 直近 4 件 (routines=4 / large-codebase=0 / khairallah-40=0 / khairallah-30-workflows=2) → 3/4 が reject 寄り → **trend warning 該当**
- **判定**: SATURATED-but-novel (delta=2 確定 + 2 ambiguous)
- **ユーザー選択**: light-phase2 (推奨選択)

## Phase 2 (light): novel 4 候補のみ検証

### Pass 1: 存在チェック (Sonnet Explore)

| # | 主張 | Sonnet 結果 |
|---|---|---|
| #10 | chmod 600 .env (OS layer defense) | partial (permissions.deny は Already、chmod ルール not_found) |
| #11 | SessionStart branch-aware `cat .claude/context-$(git branch --show-current).md` | not_found (現状 7 SessionStart hook いずれも branch-aware 未実装) |
| #15 | cleanupPeriodDays: 180 (default 30) | not_found (settings.json に key 自体なし、`~/.claude/projects/` は 810MB) |
| #17 | inference_geo data residency +10% | not_found (cost docs / API ガイドに記述なし) |

### Pass 2: 強化判定 + 採用可否 (Opus)

| # | Pass 2 判定 | 根拠 | Decision |
|---|---|---|---|
| #10 | **Gap (small)** | permissions.deny の既知 bug (#11544) が事実なら二重防御は妥当。dotfiles で 2026-04-17 jsonl-secret-audit という実害履歴あり。chmod 600 は OS-native, 副作用なし | **Adopt** |
| #11 | **N/A (reject)** | Progressive Disclosure (`<important if>` + `references/` on-demand) で同等以上を達成済。短命ブランチが多い dotfiles では `context-feat-X.md` が orphan ファイル化する。記事の「30% 削減」根拠なし | **Reject** |
| #15 | **Gap (small) — grounding 後** | WebSearch で `cleanupPeriodDays` 公式実在を確認 (anthropics/claude-code schema + Issue #23710/#2543/#45903)。default 30, integer。「Dreaming」機能の存在は未確認だが、past-chat search retention は確実に効く。dotfiles は 810MB → ~4.8GB の disk cost あり (許容範囲) | **Adopt** |
| #17 | **N/A** | dotfiles は Claude Code CLI (subscription) 経由、raw API 利用なし。API パラメータは scope 外 | **Reject** |

### 棄却した 14 件 (Section 1 + 既存カバー)

| カテゴリ | 件数 | 判定理由 |
|---|---|---|
| Section 1 Claude.ai UI (#1-8) | 8 | **N/A**: claude.ai web app の UI 機能。dotfiles harness は CLI / settings.json / hook 領域。設定の場所が物理的に違う |
| #9 enabledPlugins false trick | 1 | Already (2026-05-04 73% Overhead Pattern 5 で token tax 採用済、enable/false 化は `mcp-audit.py` で対応) |
| #12 disableAllHooks panic switch | 1 | Already (existence, v2.x 標準機能) |
| #13 model per-project override | 1 | Already (`references/model-routing.md` + project-level `.claude/settings.json` で運用) |
| #14 mcpServers enabled flag | 1 | Already (`mcp-audit.py` + 73% Overhead で扱い済) |
| #16 cache_control breakpoint | 1 | Already (2026-05-22 Anthropic Token Savings absorb で 5 ファイル採用、TTL 1h/5min/5min 三層 + Subagent TTL=5min 全カバー) |
| #18 Per-workspace + per-feature rate limit | 1 | N/A (Console workspace 設計、個人 dotfiles で API workspace 運用なし) |

## Phase 3: Triage Result

- **Adopt: 2 件** (#10 chmod 600, #15 cleanupPeriodDays:180)
- **Reject: 16 件** (14 件 N/A/Already + 2 件 Pass 2 reject)

## Phase 4: Plan

### Task 1: `references/claude-code-threats.md` に「ローカル秘密ファイル defense-in-depth」セクション追加 (S)

`§6.5` を新設、`§6 MCP audit` の後 `§7 Agent Traps` の前に配置。
内容:
- L1 (Claude Code permissions.deny) と L2 (OS chmod 600) の二層防御
- 根拠: anthropics/claude-code#11544 等で deny rule の silent fail 事例
- 適用範囲: プロジェクト root の `.env`, `.env.*`, `~/.aws/credentials` 等

### Task 2: `.config/claude/settings.json` に `cleanupPeriodDays: 180` 追加 (S)

top-level key として追加。default 30 から 180 へ拡張。

検証 (CLAUDE.md `<important if="...settings.json...">` 遵守):
- `task validate-configs`
- `task validate-symlinks`

期待効果: past-chat search の retention が 6 倍、`~/.claude/projects/` 810MB → ~4.8GB (許容)。
撤退条件: disk usage が 10GB 超に達した場合 90 日に下げる、または `cleanupPeriodDays: 0` の bug (#23710 silent disable) が再発したら明示値で対応。

## Phase 5: Handoff

両タスク S 規模 → 本セッション内で即実行。Codex Review Gate は本来 mandatory だが、本件は (a) 1 reference 追記 (b) 1 line settings.json 追加で、CLAUDE.md `<important if="settings.json">` の最低検証 `task validate-configs` + `task validate-symlinks` で十分とみなす。

## Validation-only Follow-up

- なし (今回は platform drift 検出なし、記事のメインクレームが claude.ai UI 中心で dotfiles と接面が小さい)

## Meta-findings

1. **N=13 で初の light-phase2 採用** — Saturation Gate Step 3.7 (delta 計算 + ambiguous 別カウント) が機能。Phase 2.5 (Codex+Gemini) 省略で Pass 1+2 のみで採用判定可、token/時間コスト 60% 程度削減。
2. **WebSearch grounding が anti-marketing-fabrication filter として有効** — #15 cleanupPeriodDays の公式 schema + Issue 番号 (#23710 / #2543 / #45903) を 1 query で確認。「Dreaming」機能 (記事主張の根拠) は依然未確認だが、設定 key 自体は実在で採用判断可能。
3. **claude-code-tips family の trend reject 確度** — 13 件中採用 0 が支配的で、Telegram CTA / 数値煽り (「$340 → $87」等) パターンは Reject 確度 70%+。今後も同パターンは light-phase2 デフォルト推奨。

## Codified (No new memory entries needed)

- Phase 1.5 既存ガード (`references/topic-family-saturation.md` Step 3.7) で十分対応できた
- `feedback_absorb_sonnet_imagination.md` (2026-05-22 新設) も今回は発火せず — Sonnet Explore が「強化余地」を Pass 1 で過大解釈する局面なし
