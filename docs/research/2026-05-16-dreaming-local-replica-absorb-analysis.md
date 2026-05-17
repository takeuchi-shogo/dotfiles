---
source: "73% of my CLAUDE.md was lying to Claude (anonymous Telegram article)"
date: 2026-05-16
status: analyzed (大部分 reject, 既存仕組み上回り発見)
---

## Source Summary

**主張**: Anthropic の Managed Agents 向け新機能「Dreaming」(2026-05-06 公式発表) を、80 行の Python (`dream.py`) + 12 行 rubric で local 再現したと主張。100 sessions/6M tokens/11 minutes/$4.20 で著者の CLAUDE.md の 73% を削除、4 patterns (review=approve 73% / stack switch / quick fix 12 turns / prose 8x correction) を発見、削除分類 3 種 (one-off correction / aged context / contradiction) を提示。Telegram funnel + skool 誘導付き。

**手法**:
- T1: 4-phase script (Orient/Gather/Dream/Output) で local 再現
- T2: 12-line rubric (frequency 付き behavioral observation、Workflow/Decisions/NOT re-suggest の 3 節、40 行上限)
- T3: 14-30 day re-dream cycle ("CLAUDE.md is cache, not config")
- T4: dream-skill GitHub repo (48h で出たと主張)

**根拠**: Harvey 6x task completion (公式 announce 引用)、著者自身の 7-day before/after metric (turn-to-resolution -36%、token usage -22%、Claude 過信副作用)。

**前提条件**: 90 日分の Claude Code session 存在、Opus 4.7 API access、Telegram/skool 誘導への動線。

## Pre-Analysis: Falsifiable Verification (Phase 1.5)

| 主張 | 公式/実測 | 判定 |
|------|----------|------|
| Anthropic Dreaming feature 実在 | `platform.claude.com/docs/en/managed-agents/dreams` 公式 docs 取得確認、Research Preview/request access form あり | ✅ Real |
| Harvey 6x improvement | 公式 announce + VentureBeat/TheNewStack 等 | ✅ Real |
| 100 sessions cap | docs `Sessions per dream: 100` | ✅ Real |
| `claude-opus-4-7` model | 環境スナップショット + docs `Supported models: claude-opus-4-7, claude-sonnet-4-6` | ✅ Real |
| `~/.claude/projects/*/sessions/*.jsonl` path | **実測: `~/.claude/projects/<encoded-cwd>/<uuid>.jsonl` (sessions/ 不在)** | ❌ **Fabricated → dream.py glob 0 match で動かない** |
| `dream-skill` GitHub repo (48h 内) | `grandamenium/dream-skill` (62 stars), `mengazaa/claude-dream`, `sathwick-p/dream`, `richardbowman/claude-code-dream` 等複数実在 | ⚠️ 実在するが全て同じ simplified replica |
| Content farm pattern | Telegram funnel + 著者匿名 + 大袈裟数字 + "Part 2 next week"/"If saved a week, repost" | ✅ 8 件目 (Boris/Three-Model/Cyril/12-rule/zodchixquant/0xfene/Nav Toor/Khairallah に続く) |

## Critical Discovery: 公式 docs 一次取得で記事核心が崩壊

公式 docs (`platform.claude.com/docs/en/managed-agents/dreams`) を WebFetch で取得して判明:

| 項目 | 公式 docs | 記事 `dream.py` | 判定 |
|------|----------|----------------|------|
| API endpoint | `POST /v1/dreams` (beta headers `managed-agents-2026-04-01,dreaming-2026-04-21` 必須) | `client.messages.create()` | ❌ **完全に別 API** |
| Input type | `memory_store_id` + `session_ids` (Managed Agents resource ID 参照) | session JSONL 全文を 1 prompt に詰める | ❌ |
| パラメータ | `instructions` (4096 chars) のみ | `auto_apply` (Gemini が hallucinate、docs に**存在しない**) | ❌ |
| 動作対象 | Managed Agents API の memory_store + sessions resource | Claude Code Pro/Max user の local JSONL | ❌ **完全に別系統** |
| Billing | 標準 API token rates (model 依存) | 「$4.20 / pass」(著者主張) | ⚠️ |
| Access | research preview、request access form 必須 | (言及なし、Pro/Max user が呼べる前提) | ❌ |

**結論**: 記事の `dream.py` は **Anthropic Dreaming feature を呼んでいない**。実態は「100 sessions の JSONL を 1 つの巨大 prompt にして `messages.create()` に投げる**ただの要約タスク**」。"local replica" は marketing 用語の詐欺、Dreaming の curation/deduplication/insights surfacing pipeline は再現していない。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| T1 | dream.py 4-phase script | Reject (技術的虚偽) | `messages.create()` ≠ Dreaming feature。session path も破綻 |
| T2 | 12-line rubric (frequency 付き) | Reject (重複) | `analyze-tacit-knowledge` skill + 公式 `instructions` 仕様 (4096 chars) で十分 |
| T3 | 100 sessions cap | N/A | Dreaming 公式仕様。local 再現には依存しない |
| T4 | 14-30 day re-dream cycle | N/A | `friction-weekly-digest.sh` (2026-05-13 Yamadashy 由来統合) + `skill-usage-weekly.sh` で類似運用済 |
| T5 | 4 patterns (review=approve 等) | Reject (role mismatch) | Polymarket bot context、Nav Toor 教訓と同じ |
| T6 | 削除分類 3 種 (one-off/aged/contradiction) | Reject (既存上回り) | Pass 2 参照 |
| T7 | 7-day before/after metric | N/A | `friction-weekly-digest.sh` + `skill-usage-weekly.sh` |
| T8 | dream-skill GitHub repos | N/A | 実在するが全て同じ simplified replica、採用価値なし |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `improve-policy.md` Rule 26 (Contradiction Mapping) | 矛盾検出が必要 | `references/contradiction-mapping.md` で既に専用 reference あり | 強化不要 |
| S2 | `improve-policy.md` Rule 51 (Build to Delete wiring, dead-weight-scan, 30日 `[DEPRECATED]`/60日 削除提案) | aged context 削除 | 自動化済 (akira_papa_AI absorb 2026-04-21 由来) | 強化不要 |
| S3 | `improve-policy.md` Pruning-First philosophy (2026-04-11、pepabo absorb 由来) | 「追加より削除」原則 | active 運用中 | 強化不要 |
| S4 | `analyze-tacit-knowledge` skill (3層構造、セッションログから暗黙知抽出) | 4 patterns 自動発見 | 既存で十分、Polymarket bot context は適用不可 | 強化不要 |
| S5 | `friction-weekly-digest.sh` + `skill-usage-weekly.sh` | 7-day before/after metric | 既存で類似運用済 (Yamadashy 由来 2026-05-13) | 強化不要 |
| S6 | `/improve` skill | 自動 audit | **2026-05-03 retire** (false-positive 多発)、CLAUDE.md user instruction「自動修正系の再導入は不可」 | **強化禁止** |

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| T1 | dream.py 実装 | スキップ | 技術的虚偽 + `/improve` retire 教訓 |
| T2-T8 | その他全手法 | スキップ | Pass 1/2 で全て既存仕組みでカバー or N/A |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1-S6 | 全て | 強化スキップ | 既存仕組みが記事を上回る |

## Phase 2.5 Refinement (Codex + Gemini 並列批評)

- **Codex (codex:codex-rescue)**: agent type 名 typo (`codex:rescue`) で 1 回目失敗、`codex:codex-rescue` 2 回目で起動するも 27 分後も no output (background mode)。**前回 Khairallah absorb 2026-05-14 と同じ「Codex no output」パターン**、2 件目記録
- **Gemini (gemini-explore)**: 出力得たが **MEMORY.md context 汚染**で本記事 (anonymous Polymarket bot) を Khairallah と混同。OpenAI "Daybreak" 2026-05-11、$0.08/h 課金、Wisedocs 50% 削減、Netflix DevOps 採用、Claude Code v2.1.59+ Auto-Dream 等を主張するが**いずれも公式 docs 未記載で hallucination 疑い**。Gemini grounding でも `dream-skill` repos 実在予測は当てた
- **Opus 自前検証**: WebFetch で公式 docs 取得、`improve-policy.md` の grep で Rule 26/51 + Pruning-First を確認 → Phase 2.5 の主要価値は Gemini ではなく**公式 docs 一次取得**から得られた

## Plan

### Task 1: MEMORY.md 外部知見索引追記
- **Files**: `/Users/takeuchishougo/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Changes**: 1 行追加 (本 absorb レポート + 公式 Dreaming docs を一次ソースとして記録)
- **Size**: S

### Task 2: 本分析レポート
- **Files**: `docs/research/2026-05-16-dreaming-local-replica-absorb-analysis.md`
- **Changes**: 新規作成 (本ファイル)
- **Size**: S

## Lessons Learned

1. **記事の technical claim は個別検証**: content farm 8 件目だが、Dreaming feature 自体と Harvey 6x は本物。zodchixquant 教訓「集客記事も技術主張は検証する」を再確認
2. **dream.py 主張は marketing 詐欺**: `messages.create()` を呼ぶだけで Dreaming pipeline を呼んでいない。"local replica" 言葉に騙されない検証が重要
3. **Gemini grounding の MEMORY.md context 汚染**: 過去 absorb 記録 (Khairallah Routines) を本記事 (anonymous Polymarket bot) に混入する bias を確認。Gemini 出力は別ファミリ critique として価値あるが、判定の主役にしない
4. **Codex no output 2 件目** (前: Khairallah 2026-05-14): codex-rescue 27 分待っても結果取得不可。前回同様、前日 absorb 検証データ (Khairallah の Routines/Dreaming/Cowork verified) + 公式 docs 一次取得で Phase 2.5 補完可能、絶対依存ではない
5. **既存仕組みの強さ**: `improve-policy.md` Rule 26 (Contradiction Mapping) + Rule 51 (Build to Delete wiring) + Pruning-First philosophy は記事の「削除分類 3 種」を完全に上回る。Pruning-First 適用で「新規追加なし」が正解 (S2 採用: MEMORY.md ポインタ + 本レポートのみ)
6. **`/improve` retire (2026-05-03) との整合**: 記事の「自動 audit」「auto_apply」は false-positive 多発で retire 済み mechanism と同根のリスクを持つ。Memory Poisoning/Sleeper Agent リスク (Gemini 補完) も合わせて、自動化系の再導入は CLAUDE.md user instruction で禁止されている
7. **公式 Dreaming docs 動向監視**: Pro/Max user に research preview が拡張される可能性あり、MEMORY.md ポインタで監視継続

## Sources

- **一次ソース (公式)**: [Anthropic Dreams API docs - platform.claude.com](https://platform.claude.com/docs/en/managed-agents/dreams)
- **公式発表**: 2026-05-06 "Code with Claude" event
- **記事 (reject 対象)**: "73% of my CLAUDE.md was lying to Claude" (anonymous Telegram article、URL 不明)
- **二次報道**: [VentureBeat](https://venturebeat.com/technology/anthropic-introduces-dreaming-a-system-that-lets-ai-agents-learn-from-their-own-mistakes), [TheNewStack](https://thenewstack.io/anthropic-managed-agents-dreaming-outcomes/), [Let's Data Science](https://letsdatascience.com/blog/anthropic-dreaming-claude-managed-agents-self-improving-may-6)
- **既存覆い**: `dotfiles/.config/claude/references/improve-policy.md:285` (Rule 26 Contradiction Mapping), `:735` (Rule 51 Build to Delete wiring), `:741` (Pruning-First, pepabo absorb 由来)
