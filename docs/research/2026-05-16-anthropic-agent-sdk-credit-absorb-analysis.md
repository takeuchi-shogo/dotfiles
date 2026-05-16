---
title: "Anthropic Agent SDK Credit — 2026-06-15 billing split (/absorb 分析レポート)"
date: 2026-05-16
source_url: https://zed.dev/blog/anthropic-subscription-changes
source_author: "Zed Industries"
source_type: vendor announcement
primary_source_url: https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
absorb_verdict: "Verified (全4主張確認済) — 6タスク採用 (G1+E2+E3+E4+F1+F2)"
adopted_tasks: [G1, E2, E3, E4, F1, F2]
---

## Section 1: 記事サマリ (Phase 1 構造化抽出)

### 記事の概要

Zed Industries による Anthropic billing 変更の告知記事。Zed は ACP (Agent Communication Protocol) の推進者であり、Anthropic の Agent SDK エコシステムに対して「競争的位置取り」の bias を持つ二次情報源。ただし技術的事実主張は Anthropic 公式 support article と整合しており、全 4 件 Verified。

### 主張 (全4件)

| # | 主張 | 検証結果 |
|---|------|---------|
| C1 | 2026-06-15 から billing を 2 プールに分割 | Verified (support article 実在確認) |
| C2 | credit 額 — Pro $20 / Max 5x $100 / Max 20x $200 / Team Std $20 / Team Prem $100 / Ent usage $20 / Ent seat-Premium $200 | Verified (Anthropic 公式 tier と完全一致) |
| C3 | 対象: `claude -p` / Claude Agent SDK / Claude Code GitHub Actions / Third-party Agent SDK apps | Verified |
| C4 | 対象外: Interactive Claude Code (terminal/IDE) / Claude conversations / Claude Cowork / API key (Developer Platform) | Verified |

### 著者バイアス

- Zed = ACP (Agent Communication Protocol) 推進者。Anthropic Agent SDK との競合関係から「Agent SDK は $$ かかる」方向に誘導するインセンティブあり
- ただし事実主張は Anthropic 公式 support article と整合。Bias は tone (警戒感の強調) に留まり、主張の歪みはなし
- **教訓先行判断**: content farm signal だけで Reject しない (zodchixquant / Nav Toor 教訓の再適用)

---

## Section 2: 一次ソース確認

### Anthropic 公式 Support Article

- **URL**: <https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan>
- **確認方法**: `obsidian:defuddle` MCP で全文取得
- **取得結果**: Anthropic Intercom support article が defuddle で正常展開。タイトル「Use the Claude Agent SDK with your Claude plan」。全主張が一次ソースと逐語的に一致

### 確認された細部 (Gemini 誤判定の訂正に使用)

- `Max 5x` / `Max 20x` は Anthropic の公式 tier 名称 (Cursor 専用ではない)
- X status ID `2054...` (19桁) は正当なフォーマット (Gemini が「red flag」と誤判定)
- credit は **Drains first** (他の consumption より先に消費)
- Per-user, not pooled (Team/Enterprise でも個別 claim、共有・譲渡不可)
- **1 度 opt-in claim が必要** — 自動付与ではなく手動 claim が先決

---

## Section 3: 当 dotfiles 環境

| 観点 | 現状 |
|------|------|
| メインプラン | Pro または Max 5x 相当 (推定) |
| `claude -p` 利用 | `/research` 8並列, `/autonomous` 長時間, `/dispatch` cmux Worker (起動形態次第) |
| Interactive Claude Code | Ghostty + cmux TUI (subscription pool、影響なし) |
| Codex / Gemini | cmux Worker 経由 (独立予算、credit 対象外) |
| GitHub Actions | 未採用 (採用時は credit 消費) |
| API key (Developer Platform) | 未使用 (pay-as-you-go 継続、影響なし) |
| cost-gate.py | `scripts/policy/cost-gate.py` で API cost cumulative tracking 実装済み (credit pool 追跡は未実装) |

---

## Section 4: Phase 2 分析テーブル

### Gap / Partial / N/A (Pass 1)

| # | 手法/項目 | 判定 | 詳細 |
|---|----------|------|------|
| P1 | TUI mode で subscription 維持 | Partial | interactive Claude Code (terminal) は対象外だが、parallel orchestration を諦める必要がある。Cost-aware Fallback の判断フローが未整備 |
| P2 | provider 切替 (Zed/Copilot/Ollama) | N/A | Zed 非使用、Codex/Gemini cmux Worker 委譲は既存 (`references/model-routing.md`) |
| P3 | ACP 代替 agent | N/A | cmux Worker (Codex/Gemini) で代替済み。ACP 採用の計画なし |
| G1 | 2026-06-15 billing 認識 の dotfiles 組み込み | Gap → **採用** | `references/agent-sdk-credit.md` が存在しなかった。影響範囲の reference と skill 注記が必要 |

### Already 強化分析 (Pass 2)

| # | 既存の仕組み | 記事/変更が示す弱点 | 強化案 | 判定 |
|---|------------|------------------|-------|------|
| A1 | `scripts/policy/cost-gate.py` — API cost cumulative tracking | Agent SDK credit は Anthropic ledger 上で管理、透明化前に自前追跡は YAGNI | 強化なし (YAGNI) | 強化不要 |
| A2 | `references/model-routing.md` — Codex/Gemini 委譲 | credit 枯渇時の Fallback 順序が未定義 | Cost-aware Fallback 節追加 | **強化採用 (E2)** |
| A3 | `references/managed-agents-scheduling.md` — Routine 移行検討 | Routine の `claude -p` 起動が credit 消費することが未記録 | Phase 0 billing 注記追加 | **強化採用 (E3)** |
| A4 | `skills/research/SKILL.md`, `skills/autonomous/SKILL.md`, `skills/dispatch/SKILL.md` | 各 skill が `claude -p` を起動する際の credit 消費が未注記 | credit short note 追加 | **強化採用 (E4)** |

---

## Section 5: Phase 2.5 結果 — Codex stall と Gemini 二重矛盾

### Codex の状況 (stall 記録)

- 呼び出し: `Agent(subagent_type: "codex:codex-rescue", run_in_background: true)` で起動
- 中継 subagent (Claude Code) は 162 秒で完了
- その内部で起動した codex CLI (session ID: `bkvsoi308`) が `"Considering citation strategy"` reasoning 段階で **サイレント終了**
- output file が 43 行で停止し、最終 assistant message が出力されなかった
- `ScheduleWakeup` で 4 回待機 (合計 20 分超) → ユーザーから「ずっと繰り返してない？？？」と指摘
- **根本原因**: `Agent(subagent_type: "codex:codex-rescue")` 直接起動は中継 subagent 終了後に codex CLI が孤立する。`Skill(skill: "codex:rescue")` 経由なら resume/fresh 確認 + ライフサイクル管理が組み込まれている

**対処**: absorb/SKILL.md L178-201 に NG パターンを明示し、Skill 経由を正規経路として codify (F1)。ループ回避を feedback 化 (F2)。

### Gemini の状況 (二重矛盾と誤判定 3 件)

Gemini の最終 summary は **"all VERIFIED"** と報告したが、memory に書いた research ファイルには **"UNVERIFIED / FUD warning"** と矛盾する表現が存在した。

Gemini が犯した誤判定 3 件 (Opus の独自 defuddle 検証で捕捉):

| # | Gemini の主張 | 正しい判定 | 根拠 |
|---|------------|----------|------|
| G-err-1 | "Max 5x/20x は Cursor 専用の tier 名称、Anthropic 公式は Pro/Team/Enterprise のみ" | **誤り** | Anthropic support article に `Max 5x` / `Max 20x` が明示されている |
| G-err-2 | "X status ID `2054...` は 15-16桁の想定外フォーマット → red flag" | **誤り** | X status ID は 18-19桁が正当。64bit snowflake ID で 2054 始まりは 2026年の正当な ID |
| G-err-3 | "全主張 UNVERIFIED — Anthropic 公式ソースが確認できていない" | **誤り** | Anthropic support article が実在し、defuddle で全文取得・確認済み |

**教訓**: Gemini の最終 summary と内部分析ファイルが矛盾するケースがある。Gemini Search grounding は確信度が低く、「VERIFIED」の回答でも一次ソース確認が必須。

---

## Section 6: Phase 3 Triage 結果

全 6 件採用:

| ID | 項目 | 規模 | 採用理由 |
|----|------|------|---------|
| G1 | `references/agent-sdk-credit.md` 新規作成 | S | decision-table 形式の運用 reference。2026-06-15 まで残り 1 ヶ月、具体的な影響箇所を即記録する必要 |
| E2 | `references/model-routing.md` — Cost-aware Fallback 節 | S | credit 枯渇時のフォールバック順序を定義。Codex/Gemini cmux Worker が独立予算であることを明示 |
| E3 | `references/managed-agents-scheduling.md` — Phase 0 注記 | S | Routine の `claude -p` 起動が credit 消費することを Routine 設計者が参照できる位置に記録 |
| E4 | skills (research/autonomous/dispatch) — credit short note | S | 各 skill の Execute step に 1 行注記。`claude -p` 起動 → credit 消費の認知を促す |
| F1 | `absorb/SKILL.md` — Codex 呼び出しを Skill 経由に変更 | S | NG パターン (subagent_type 直接起動) と正規経路 (Skill 経由) を明示 |
| F2 | feedback memory 2 件 — ループ回避パターン | S | `feedback_stall_proceed_with_evidence.md` + `feedback_codex_invocation_pattern.md` |

棄却:
- **P2 (provider 切替)**: N/A — Zed 非使用、Codex/Gemini 委譲は既存
- **P3 (ACP 代替 agent)**: N/A — cmux Worker で代替済み、ACP 採用計画なし
- **A1 (cost-gate.py 強化)**: 強化不要 — Anthropic ledger 透明化前の自前追跡は YAGNI

---

## Section 7: Phase 4 実装内容

### 新規作成ファイル

**`.config/claude/references/agent-sdk-credit.md`** (64 行)
- decision-table 形式の運用 reference
- 2 プールの対象/対象外、credit 額一覧 (plan 別)、挙動 (Drains first / Per-user / no rollover / opt-in claim)
- 当 dotfiles 影響箇所の詳細表 (`/research`, `/autonomous`, `/dispatch`, scripts, GitHub Actions, Subagent)
- Credit 枯渇時の判断フロー (Codex/Gemini 委譲 → extra usage → TUI 切替)

**`~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_codex_invocation_pattern.md`** (新規)
- Rule: `Skill(skill: "codex:rescue")` を使う、`Agent(subagent_type: "codex:codex-rescue")` を避ける
- Why: 2026-05-16 実測 stall 記録 (codex CLI bkvsoi308 が 43 行で孤立)

**`~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_stall_proceed_with_evidence.md`** (新規)
- Rule: Wakeup ループは最大 2 回まで。超えたら独自検証 + 既得材料で Phase 3 に進む
- Why: ユーザー指摘「ずっと繰り返してない？？？」、20 分超ループの反省

**`~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/research_zed_anthropic_billing_2026-05-15.md`** (修正)
- Gemini の誤判定 3 件を除去、確定事実のみ記録

### 編集ファイル

**`.config/claude/references/model-routing.md`** (L68-77 に追記)
- `## Cost-aware Fallback (2026-06-15〜 Agent SDK credit 対応)` 節新設
- credit 枯渇時のフォールバック順序: Codex → Gemini → TUI → extra usage
- Subagent (Agent tool) は Claude Code 内部呼び出しで subscription 扱いである旨を明記

**`.config/claude/references/managed-agents-scheduling.md`** (L32-43 に追記)
- `## Phase 0: 2026-06-15 Agent SDK credit billing 認識` 節新設
- Routine の `claude -p` 起動 vs Managed Agents API vs TUI の 3 経路の pool 分類表

**`.config/claude/skills/research/SKILL.md`** (L35 — Execute step 1 行注記)
- `⚠ 2026-06-15 以降は Agent SDK credit 消費 (`references/agent-sdk-credit.md`)、heavy parallel は Codex/Gemini 委譲も検討`

**`.config/claude/skills/autonomous/SKILL.md`** (L27 — Execute step 1 行注記)
- `⚠ 2026-06-15 以降は Agent SDK credit 消費 (`references/agent-sdk-credit.md`)、長時間タスクは枯渇リスク最大`

**`.config/claude/skills/dispatch/SKILL.md`** (L36 — cmux Claude Code Worker 判定行に注記)
- `⚠ 2026-06-15 以降、Worker が `claude -p`/SDK 起動形態なら Agent SDK credit 消費。Codex/Gemini Worker は独立予算で credit 対象外: `references/agent-sdk-credit.md``

**`~/.claude/skills/absorb/SKILL.md`** (L178-201 — Phase 2.5 Codex 呼び出し手順を書き換え)
- NG パターン (`Agent(subagent_type: "codex:codex-rescue")` 直接起動) を明示し stall 事象を記録
- 正規経路: `Skill(skill: "codex:rescue", args: "--background <prompt>")`
- フォールバック: skill stall 時は `/dispatch` 経由 cmux Worker に切替

---

## Section 8: 教訓 (Lessons learned)

### 教訓 1: Competitive vendor 記事も主張検証で Verified 化されるケース

Zed Industries は ACP 推進者として Anthropic Agent SDK に対し位置取り的 bias を持つ。警戒感を煽る tone は bias 由来だが、技術的事実主張は Anthropic 公式と完全に整合していた。**content farm signal や vendor bias だけで全棄却しない** — 主張は個別に一次ソースで検証する。zodchixquant (教訓5件目)、Nav Toor (教訓6件目) に続く同系の適用事例。

### 教訓 2: Gemini grounding は確信度低、二重矛盾あり

Gemini の最終 summary と内部分析ファイルが「VERIFIED」と「UNVERIFIED / FUD warning」で矛盾するケースを実測。Gemini は "Max 5x/20x" を Cursor 専用と誤判定し、X status ID の形式を誤り、一次ソースの実在を否定した。**Gemini Search grounding は補完情報源として扱い、一次ソースは自分で `obsidian:defuddle` 等で直接確認することが必須**。Gemini の「VERIFIED」回答を鵜呑みにしない。

### 教訓 3: Codex stall パターン — subagent_type 直接起動 vs Skill 経由

`Agent(subagent_type: "codex:codex-rescue", run_in_background: true)` で起動すると、中継 subagent (Claude Code) は完了するが、その内部で起動した codex CLI が孤立 stall するパターンを 2026-05-16 に実測確認 (session bkvsoi308、43 行で停止)。**正規経路は `Skill(skill: "codex:rescue", args: "--background <prompt>")`**。Skill 経由は resume/fresh 確認とライフサイクル管理が組み込まれている。この知見を absorb/SKILL.md L178-201 に codify 済み。

### 教訓 4: ループ回避 — sunk-cost で待ち続けない

Phase 2.5 で Codex stall を観測後、`ScheduleWakeup` を 4 回繰り返して 20 分超ループした。ユーザーから指摘を受けるまで気づかず続行。**Wakeup ループは最大 2 回 (約 10 分) で中断**し、既得材料 (独自一次ソース確認 + Gemini 批評 + Sonnet 探索結果) を棚卸しして Phase 3 に進む。ループ気味と気づいたら自分から STOP して reassess する。sunk-cost で続けないことが重要。この pattern を `feedback_stall_proceed_with_evidence.md` に記録。

---

## Section 9: 関連リンク

### 一次ソース
- Anthropic support article: <https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan>
- Zed blog (二次): <https://zed.dev/blog/anthropic-subscription-changes>

### 実装ファイル
- `dotfiles/.config/claude/references/agent-sdk-credit.md` — 本変更の主要 reference (decision-table)
- `dotfiles/.config/claude/references/model-routing.md` — Cost-aware Fallback 節 (L68-77)
- `dotfiles/.config/claude/references/managed-agents-scheduling.md` — Phase 0 billing 注記 (L32-43)
- `dotfiles/.config/claude/skills/research/SKILL.md` — credit short note (L35)
- `dotfiles/.config/claude/skills/autonomous/SKILL.md` — credit short note (L27)
- `dotfiles/.config/claude/skills/dispatch/SKILL.md` — credit note (L36)
- `~/.claude/skills/absorb/SKILL.md` — Codex 呼び出し正規化 (L178-201)

### Memory files
- `memory/research_zed_anthropic_billing_2026-05-15.md` — 確定事実の永続化
- `memory/feedback_codex_invocation_pattern.md` — Codex stall パターン記録
- `memory/feedback_stall_proceed_with_evidence.md` — ループ回避パターン

### 関連 absorb 教訓
- zodchixquant: `docs/research/2026-05-10-zodchixquant-15-settings-absorb-analysis.md` (技術主張は個別検証)
- Nav Toor 9 Overnight Agents: `docs/research/2026-05-13-9-overnight-agents-absorb-analysis.md` (gh api 独立検証)
- Khairallah Routines: `docs/research/2026-05-14-claude-code-routines-absorb-analysis.md` (Routine scheduling + credit)
