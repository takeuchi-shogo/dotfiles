---
source: "anonymous Telegram-promoted article (匿名 + skool.com 販売漏斗パターン)"
date: 2026-05-10
status: analyzed
verdict: "Selective adoption (T1+T2 のみ採用、T3 12-rule 全採用は Reject)"
adopted_tasks:
  - "T1: R12 silent success audit"
  - "T2: R9 test intent rubric"
rejected_tasks:
  - "T3: 12-rule CLAUDE.md 全採用 (Pruning-First 違反 + 200 行 ceiling 抵触)"
related:
  - docs/research/2026-04-20-karpathy-skills-absorb-analysis.md
---

# 12-rule CLAUDE.md (anonymous Telegram article) absorb 分析

## Source Summary

**主張**: Karpathy 4 ルール CLAUDE.md (forrestchang/andrej-karpathy-skills) に 8 ルールを追加し、合計 12 ルール CLAUDE.md template を提案。"30 codebases × 50 tasks × 6 weeks で mistake rate 41% → 3%" を訴求。

**手法 (追加 8 ルール)**:
- Rule 5: Use the model only for judgment calls (no routing/retry/deterministic transforms)
- Rule 6: Token budgets are not advisory (per-task 4k / per-session 30k)
- Rule 7: Surface conflicts, don't average them (pick one + flag)
- Rule 8: Read before you write (read exports/callers/utilities first)
- Rule 9: Tests verify intent, not just behavior (encode WHY)
- Rule 10: Checkpoint after every significant step
- Rule 11: Match the codebase's conventions, even if you disagree
- Rule 12: Fail loud (silent skip / silent success NG)

**メタ手法主張**:
- 200 行 CLAUDE.md ceiling
- 14 ルール超で compliance 76% → 52%
- ツール非依存に書け
- examples > rules ではない

**根拠**: 30 codebases × 50 tasks × 6 weeks 自称検証 (再現性ゼロ、出典なし)

**前提条件**: Multi-step agent workflow / Multi-codebase work / Long sessions

**著者バイアス**:
- 匿名著者 + 末尾 Telegram daily-tips promo
- skool.com 販売漏斗パターン (Boris/Three-Model Stack 系列)
- "Bookmark this and Repost" のエンゲージメント bait

## Phase 1: Extract → Phase 2 Pass 1 (existence check)

| Rule | Pass 1 判定 | 既存ファイル |
|------|-------------|-------------|
| R5 judgment-only | exists | `.config/claude/CLAUDE.md:26` "Static-checkable rules は mechanism に寄せる" |
| R6 token budget | partial | `scripts/policy/measure-instruction-budget.py` (6000 token threshold) |
| R7 surface conflicts | exists | `references/agent-conflict-patterns.md`, `references/skill-conflict-resolution.md` |
| R8 read before write | exists | user CLAUDE.md "search-first" + project CLAUDE.md "Editing rules" |
| R9 tests verify intent | partial | `agents/silent-failure-hunter.md`, `scripts/policy/completion-gate.py` |
| R10 checkpoint | exists | `skills/checkpoint/SKILL.md`, `scripts/runtime/checkpoint_manager.py` 3軸自動 |
| R11 match conventions | exists | project CLAUDE.md "Match existing style", `auto-format.js`, `convention-pinning.md` |
| R12 fail loud | exists | `agents/silent-failure-hunter.md`, `verification-before-completion` skill |

## Phase 2.5: Codex + Gemini 並列批評

### Codex (deep reasoning) の修正

- **R12 を S 採用候補に格上げ**: Codex が file:line で **実害発見**:
  - `scripts/policy/completion-gate.py:157-163` — test runner 例外で `return True, ""` (silent 成功扱い)
  - `scripts/runtime/checkpoint_manager.py:241-244, :247-251` — `except: pass` で例外握り潰し
- **R9 を S 採用候補に格上げ**: completion gate は test 実行確認のみ、test 意図品質は見ない `completion-gate.py:381-412`
- **R10 を Already → Partial 採用見送り**: checkpoint manager は手動/閾値、every step ではない
- **R6 修正**: per-task 4k/30k は記事根拠弱い、`/context で十分` ではなく skill tax 実測管理 (`docs/specs/2026-05-04-skill-tier-pruning.md:17-19`) に寄せるべき

### Gemini (周辺知識) の検証

| 検証項目 | 結果 |
|---------|------|
| GitHub stars 主張 | **120K → 実測 102K** (誇張) |
| 12-rule template 他コミュニティ採用 | **言及ゼロ** (content farm pattern) |
| 41% → 3% 改善率の独立検証 | **データなし** (fake precision) |
| 200-line ceiling の Anthropic 公式言及 | **出典不明** (著者の創作) |
| 著者評価 | Telegram + skool.com 販売漏斗パターン |
| 信頼性総合 | **低** |

## Integration Decisions

### 採用 (T1 + T2、S 規模、3 ファイル)

| # | Task | File | Change |
|---|------|------|--------|
| T1.1 | R12 silent success audit | `scripts/policy/completion-gate.py:157-163` | test runner 例外を silent 成功 (`return True, ""`) → fail loud (`return False, exc`) |
| T1.2 | R12 silent success audit | `scripts/runtime/checkpoint_manager.py:241-242` | `except: pass` → stderr に warning 出力 |
| T1.3 | R12 silent success audit | `scripts/runtime/checkpoint_manager.py:247-251` | top-level `try/except: pass` → stderr に warning + sys.exit(0) |
| T2.1 | R9 test intent rubric | `references/review-dimensions.md` | correctness 補足として Test Intent Rubric 4-5 行追記 |

### 棄却 (T3: 12-rule CLAUDE.md 全採用)

理由:
1. Codex + Gemini 共に Reject 推奨
2. Pruning-First 違反 (R5/R8/R10 は既に実装済み 78/100、追加文言は税)
3. 200 行 ceiling 抵触 (user 134 + project 30 = 164 行 → 220-250 行に膨張)
4. 記事根拠の弱さ (41% → 3% 出典なし、200 line ceiling 著者創作、stars 102K vs 主張 120K)
5. content farm pattern (Telegram + skool.com 販売漏斗、Boris/Three-Model Stack 同系列)
6. Karpathy Rule 1 既存 ("Push back when a simpler approach exists") — 既存セットアップで実害カバー済み

## 教訓

1. **Codex の deep reasoning が file:line 実害発見の決定打**: Opus は記事の Reject に傾きすぎていたが、Codex が既存ハーネスの silent success 実害 (completion-gate + checkpoint_manager) を pinpoint。記事自体は Reject でも、批評プロセスで副次採用が正当化された
2. **記事の信頼性 ≠ 採用判定**: 信頼性低 (Gemini 確認) でも、批評過程で発見される実害は採用根拠になる
3. **200 行 ceiling は著者創作だが、本リポは独自に同等の制約 (CLAUDE.md `200 lines could be 50`) を持つ**: 偶然一致しても出典として引用しない
4. **content farm pattern 検出ルーチン化**: Telegram + skool.com + 匿名 + fake precision は 2026-04-29 Boris/Three-Model Stack で確立済み。今回は 4 件目の検出
