---
source: "30 Claude Workflows That Most Users Never Know (@eng_khairallah1, undated, posted 2026-05-23)"
date: 2026-05-23
status: light-phase2-only
verdict: 採用 2 件 (B+D), 自己訂正 1 件 (C: Sonnet imagination), N/A 1 件 (A)
family: claude-code-tips
saturation: PASS (warning) — N=14+, 採用率 ~60% (>=20% 閾値超過)
phase_2_5: skipped (light-phase2, user 判断: S 規模 2 件 + Pass 2 自己訂正済みで bias risk 低)
---

## Source Summary

**主張**: 平均的な Claude ユーザーと power user の差は「Skills と workflows のセットアップ」にあり、30 項目を導入すれば週数時間節約できる。

**手法 (30 items)**:
1-10 (Skills): PDF/DOCX/PPTX/XLSX/Frontend Design/Canvas/SEO/Brand Guidelines/Marketing Bundle/Obsidian
11-20 (Workflows): Morning Briefing/Content Pipeline/Weekly Report/Email/Competitive Intel/File Org/Client Onboarding/Learning Summary/Social Media/Invoice
21-30 (Power Configs): context.md/CLAUDE.md/Prompt Library/Templates/Evaluation Checklist/Error Recovery/Multi-Project/Connector Stack/Feedback Loop/Skill Builder

**根拠**: 著者の経験談 (numerical claims なし、社会証明 + アジテーション中心)。

**前提条件**: ビジネス用途 (client/marketing 文脈)。個人 dotfiles 用途では一部 N/A。

## Phase 1.5: Saturation Gate 結果

- **Family**: `claude-code-tips` (キーワード hit: "30 workflows" = N tricks/tips pattern, "hidden features" pattern in tone)
- **N (過去 absorb 件数)**: 14+ (Boris 30 Tips, Three-Model Stack, 73% Overhead, 6 laws, 30 Sub-agents, 100+ Skills Best 6, Warp 15-skill, Top 67, 12-rule CLAUDE.md, zodchixquant 15, 9 Overnight, **Khairallah Routines (4 件採用)**, **Khairallah 40 Features (採用 0)**, mattpocock 5-skill)
- **採用率**: ~60% (8/14 で ≥1 件採用) → **PASS (warning)**
- **同著者**: 11 件目 (claude-code-tips family) + Khairallah 3 件目 (Routines/40 Features に続く)
- **Step 3.7 delta**: 4 candidates (B/C/D/A), Pass 2 で実 delta = 2 (B/D) に収束 (C は Sonnet imagination 自己訂正、A は個人用途で N/A)

## Gap Analysis (Pass 1: 存在チェック — Sonnet Explore 委譲結果)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| B | Skill 末尾 5 項目 self-check 埋め込み | **not_found** (95%) | /commit /spec /github-pr の末尾に 5 項目 checklist embed なし。verification-before-completion skill は外部呼び出し型で個別 skill 内 embed と異なる |
| C | "2 回訂正→自動 rule 昇格" threshold | partial (40%) | retrospective-codify は manual。`/improve` は deprecated 2026-05-03。observability-signals.md に "3 回再発" pattern detection あるが「自動昇格」ではなく「人間トリガー」 |
| D | 週次 (金曜) 15 分 Claude 出力 review cadence | partial (35%) | `/weekly-review` は GTD 棚卸し (Issue+Inbox)、`/timekeeper review` は日次 belief 変化。「今週 Claude 出力品質 review」専用は不在 |
| A | Brand Guidelines Skill (トーン自動適用) | partial (65%) | `/persona` (4 種類、手動切替)、`/rewrite` (audience 別)、`mizchi-blog-style.md` 存在。「全 output 自動適用 brand layer」としては機能していない |
| 残り 26 項目 (#1-7, 9-24, 27-28, 30) | — | Already / N/A | MEMORY.md + skills.sh 66-skill install + obsidian:* skill + CLAUDE.md 既存仕組みで全カバー |

## Pass 2: 記事原文 verbatim 引用照合 (Sonnet imagination 除外)

### C の自己訂正 (重要)

私 (Opus) の Step 3.7 で「**2 回訂正 threshold**」と framing したが、記事原文を verbatim で再確認すると:

> "When Claude gets something wrong, most users just correct it in the moment and move on. Power users update their Skills: ... Every mistake becomes a permanent fix."

**記事の閾値は "every mistake" = 1**。私の "2 回" は完全に Sonnet imagination (というより Opus imagination)。これは feedback_*.md (37 件) で既に実践済み、`retrospective-codify` skill 経由。**C は Already (削除、新規採用なし)**。

**メタ学習**: MEMORY.md の `feedback_absorb_sonnet_imagination.md` を私 (Opus 自身) も Pass 2 で適用する必要がある。Sonnet imagination は Pass 1 の Sonnet Explore だけでなく、Opus の Step 3.7 framing でも発生する。

### B/D の verbatim 確認

**B (#25)**:
> "Create a quality checklist that Claude runs against every output before delivering it to you:
> - Does it follow the instructions completely?
> - Is it the correct format and length?
> - Are all claims specific (numbers, names, dates) rather than vague?
> - Does it match the required tone?
> - Would I be comfortable sharing this with a client without edits?
>
> **Add this to the end of every Skill**. Quality goes up immediately."

→ 5 項目 verbatim + every Skill 末尾 embed 指示が明示。Gap 確定。

**D (#29)**:
> "Every Friday, spend fifteen minutes reviewing Claude's outputs from the week:
> - What output did not meet my standard?
> - What instruction change would have fixed it?
> - What new task could I add to my workflow next week?"

→ 3 質問 verbatim + Friday + 15 分 + Claude-output focus が既存 weekly-review/timekeeper と異なる。Gap 確定。

**A (#8)**:
> "Encode your brand - colors, fonts, tone of voice, messaging rules - into a Skill that automatically applies everywhere."

→ 企業ブランド想定 (colors/fonts/messaging rules)。個人 dotfiles では over-engineering。N/A。

## Phase 2.5: Refine (Codex + Gemini)

**省略** (light-phase2 mode、user 判断)。理由:
- Gap が S 規模 2 件のみ
- Pass 2 で Sonnet imagination 1 件を Opus 自身が verbatim 引用照合で自己訂正済み
- 同著者 11 件目 (Khairallah 3 件目) で Gemini grounding 価値は前回 absorb で活用済み
- Codex bias check に +3-5 分使う ROI が低い

省略判定の根拠を本レポートに明示 (mechanical compliance より judgment 優先)。

## Integration Decisions

### Gap / Partial (採用)

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| B | Skill 末尾 5 項目 self-check 埋め込み | **採用 (T1)** | /commit /spec の 2 skill 末尾に inline embed。記事原文 verbatim + dotfiles 文脈 adapt (「client」→「レビュアー」)。/github-pr /review への展開は valuation 後 follow-up |
| D | 金曜 weekly Claude 出力 review skill 新設 | **採用 (T2)** | `output-review` skill 新設、3 質問 verbatim + 金曜 + 15 分。`/timekeeper review` (日次 belief) と `/weekly-review` (GTD 棚卸し) と直交 |

### Sonnet/Opus imagination 訂正 (Reject)

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| C | "2 回訂正 threshold" | **Reject (自己訂正)** | 記事原文に "twice" / "2 回" / "repeated" は不在。"Every mistake = permanent fix" = 閾値 1。feedback_*.md (37 件) で既実践済み。Opus imagination で過大評価していた |

### N/A

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | Brand Guidelines Skill | **N/A** | 企業ブランド想定 (colors/fonts/messaging rules)。個人 dotfiles では `/persona` + `user_*.md` memory で十分。over-engineering |

### Already (記事内容で既存仕組み確認のみ)

| # | 項目 | 詳細 |
|---|------|------|
| #1-4 | PDF/DOCX/PPTX/XLSX skill | Anthropic 公式 skill、skills.sh 経由で install 済み (100+ Skills Best 6 absorb 2026-05-06 で確認) |
| #5 | Frontend Design | `frontend-design:frontend-design` skill installed |
| #6 | Canvas Design | N/A (個人開発で不要) |
| #7 | SEO | N/A (web 開発用途外) |
| #9 | Marketing Skills Bundle | N/A (個人開発で不要) |
| #10 | Obsidian Skills | `obsidian:*` skill family installed (defuddle, obsidian-cli, markdown, json-canvas, bases) |
| #11-20 | Workflows (Morning Briefing 等) | `/timekeeper`, `/daily-report`, `/digest`, `/research`, `/dependency-auditor`, `schedule` skill で部分カバー。個人 dotfiles 用途で大半 N/A |
| #21 | context.md | CLAUDE.md + user_*.md memory で同等 (常時コンテキスト読み込み済み) |
| #22 | CLAUDE.md | 既存 (両 global + project) |
| #23 | Prompt Library | slash command 体系で同等 |
| #24 | Template System | `templates/team-project/`, `templates/analysis-report.md` 等で同等 |
| #27 | Multi-Project Workspace | `.claude/skills/` per repo + worktree + cmux で同等 |
| #28 | Connector Stack | MCP server 12+ installed (alphaxiv, brave-search, Gmail, Calendar, Drive, context7, openaiDeveloperDocs, playwright, scite) |
| #30 | Skill Builder Workflow | `skill-creator`, `apm-usage` skill で同等 |

## Plan

### Task 1 (B): /commit と /spec 末尾に Output Self-Check embed

- **Files**:
  - `.config/claude/skills/commit/SKILL.md`
  - `.config/claude/skills/spec/SKILL.md`
- **Changes**: 末尾に `## Output Self-Check` セクション追加。記事 verbatim 5 項目を dotfiles 文脈に adapt (「client」→「レビュアー / 実装者」)
- **Size**: S (各 ~12 行追加)

### Task 2 (D): output-review skill 新設

- **Files**: `.config/claude/skills/output-review/SKILL.md` (新規)
- **Changes**: 3 質問 verbatim + 金曜 15 分 + Claude-output focus。`/timekeeper`, `/weekly-review` との差別化を明記
- **Size**: S (新 skill 1 ファイル ~60 行)

### Task 3: 分析レポート保存

- **Files**: 本ファイル
- **Changes**: 既存
- **Size**: S

### Task 4: MEMORY.md ポインタ追記

- **Files**: `/Users/takeuchishougo/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Changes**: 外部知見索引に 1 行追記
- **Size**: S

## Verdict

**採用合計**: 2 件 (B + D、両方 S 規模)
**Reject**: 1 件 (C、Opus imagination 自己訂正、actionable な学びは「Opus 自身も Pass 2 で記事原文 verbatim 照合せよ」)
**N/A**: 1 件 (A、個人用途 over-engineering)
**Already**: 24 件 (残り 26 項目のうち、Canvas/SEO/Marketing を N/A 扱いとした分以外)

同著者 Khairallah の 3 件目で初めて 2 件採用 (Routines: 4 件, 40 Features: 0 件, 本記事: 2 件)。listicle 形式でも generic noun から実装機会を Pass 2 で verbatim 引用照合すれば真の Gap が抽出できる事例。

## メタ学習

1. **Opus imagination も Pass 2 で発生する**: Sonnet imagination 罠 (memory `feedback_absorb_sonnet_imagination.md`) は Pass 1 Sonnet だけでなく、Opus の Step 3.7 (手法 delta 計算) の framing 段階でも発生する。Step 3.7 で「強化案」を考えるとき、記事原文を verbatim で引用照合する作業を必ず挟むこと
2. **PASS (warning) でも yield はある**: 同 family N=14+ でも、Pass 2 で 4→2 に絞れば Gap 採用 2 件は確保可能。saturation gate は skip 判定ではなく「重複領域に注意して filtering を強化」のシグナルとして読む
3. **light-phase2 mode で Phase 2.5 省略する判断**: S 規模 + Pass 2 自己訂正済みなら ROI 低い。mechanical compliance より judgment を優先する根拠を本レポートに明示する慣行を確立

## 関連

- `docs/research/2026-05-14-claude-code-routines-absorb-analysis.md` — Khairallah 同著者 (1 件目、4 件採用)
- `docs/research/2026-05-22-khairallah-40-features-absorb-analysis.md` — Khairallah 同著者 (2 件目、採用 0 + Sonnet imagination 罠 codify)
- `memory/feedback_absorb_sonnet_imagination.md` — Pass 2 verbatim 引用照合 rule
- `memory/feedback_absorb_thoroughness.md` — listicle 形式でも deep-dive の価値あり (Boris 30 Tips 知見)
