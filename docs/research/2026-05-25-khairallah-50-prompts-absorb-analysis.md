---
source: "50 Claude Prompts That Replace an Entire Team - Most Users Don't Know (Khairallah, @eng_khairallah1)"
date: 2026-05-25
status: integrated-partial
adopted: 4
pending_m_tasks: 5
author_family: "Khairallah (4th article)"
content_family: "generic-ai-prompt-collection (1st article in this sub-family)"
saturation_judgment_pass1: "SATURATED-pure-rehash + content scope mismatch (INCORRECT — see Section 'Self-correction')"
saturation_judgment_corrected: "Partial saturation. Content scope mismatch overestimated 40 件. Author family declining but per-prompt verbatim shows 14/16 adopt 候補"
---

## Source Summary

**主張**: 構造化プロンプト (role + context + format + success criteria + constraints) で同じモデルから劇的に良い出力を得られる。50個の copy-paste-ready prompt template コレクション。

**手法**: 5 Part × 10 = 50 個の role-play prompt template
- Part 1 (1-10) Content Creation: article writer / X thread / repurpose / headline / calendar / email sequence / SEO / case study / video / bio
- Part 2 (11-20) Business: competitive analysis / business model / pricing / persona / pitch deck / weekly report / SWOT / outreach / roadmap / meeting
- Part 3 (21-30) Coding: feature builder / code review / DB schema / API / bug debug / test suite / tech docs / refactor / devops / perf
- Part 4 (31-40) Research: market / trend / data / survey / lit review / decision matrix / risk / interview Q / legal / competitor content
- Part 5 (41-50) Productivity: task prio / email / meeting notes / learning plan / SOP / finance / habit / negotiation / weekly review / life decision

**根拠**: 著者数ヶ月の anecdotal 蓄積。「professional team output」訴求。出典・実証データなし。

**前提条件**: casual Claude.ai / ChatGPT 個人ユーザーの generic な business/content/productivity task が default audience。**ただし dotfiles の specialized skill (research/think/spec/timekeeper/mizchi-blog-style 等) との verbatim 一致箇所が多数存在することが Pass 2 で判明**。

## Self-correction: 初回判定の誤り (重要な学習)

**初回判定**: 0 件採用 (light-phase2 で N/A 多発)

**user 指摘**: 「それは手抜きではなく？」

**Codex (gpt-5.5, xhigh reasoning) による批評結果**:
- Verdict: **mixed。ただし手続き面は手抜き。**
- 40 件 N/A 一括判定は手抜き
- Prompt 22 の Already 判定は **誤読** (coldness_bias は "良い点ゼロを警告" であって "問題を捏造するな" ではない)
- Phase 2.5 skip は self-preference bias の温床
- Phase 1.5 で "skip 推奨" を framing したのは **Effort-Avoidance bias**

**手抜きの構造**:
1. Part 1 (Content), Part 2 (Business), Part 4 (Research), Part 5 (Productivity) = 40 件を「scope mismatch」で verbatim 照合を一括 skip
2. Pass 2 で Sonnet 報告 (exploration spiral 中断) の二次引用に留まり、Opus 自身で Read 照合せず
3. Phase 2.5 (Codex+Gemini 並列批評) を完全省略 — Opus self-preference 補正なし
4. user 提示時に「skip 推奨」を最初の選択肢として framing

## Phase 1.5 Saturation Gate (初回判定 + 訂正)

| 項目 | 初回判定 | 訂正後 |
|------|----------|--------|
| Khairallah author N 件目 | 4 件目 | 4 件目 (変更なし) |
| Author family trend | 4 → 0 → 2 → ? (減衰中) | 4 → 0 → 2 → **4 (訂正)** |
| Content family | generic-ai-prompt-collection | (変更なし) |
| Scope match rate | 10/50 (誤り、scope 外 framing) | **14/16 件 adopt 候補 (Codex Pass 2 verbatim 検証)** |
| delta 推定 | ≈ 0 | **14 件 (verbatim 一致 + 強化可能)** |
| 判定 | SATURATED-pure-rehash | **Partial saturation (per-prompt verbatim で訂正)** |

## Pass 2 Verbatim Verification (Codex gpt-5.5 による正規実行)

16 件 (Codex Q1 で Partial 候補と指摘された 15 件 + P22 誤読訂正) を verbatim 照合した結果:

| # | Prompt | 記事 verbatim 引用 | dotfiles 既存 verbatim 引用 (file:line) | 判定 | 強化案 |
|---|---|---|---|---|---|
| P1 | Article Writer | "bold claim / short paras (3 sentences max) / specific numbers" | `mizchi-blog-style/SKILL.md:27,30,35` "tl;dr 先出し" / "具体的なコマンド / コード / 数値" / "AI 臭の典型パターン" | **Already 強化可能** | テーブル row 3 件追加 (LinkedIn fluff / 段落 3 文 / bold hook) — **実装済 (S1)** |
| P3 | Content Repurposer | "1 source → 5 platform-native pieces" | `rewrite/SKILL.md:80-84` "Vault コンテンツの多形式展開" / "複数プリセットで連続実行" | **Partial** | `:84` の後ろに `repurpose` chain (X thread / LinkedIn / newsletter / quote / YouTube) を追加 — **実装済 (Sub)** |
| P7 | SEO Optimizer | "title tag <60 char / meta desc <155 char..." | 該当 contract なし | **N/A** | — |
| P16 | Weekly Business Report | "3-sentence top-line / metrics (this/last/change%)" | `weekly-review/templates/weekly-report.md:1,33-36` "Metric / This Week / Last Week / Trend" | **Partial** | T2 plan (M) — Top-line + Change % + Wins/Concerns/Action Items |
| P19 | Product Roadmap | "90-day by month ... P0/P1/P2 + Impact High/Med/Low" | `spec/SKILL.md:86,107` + `feature-tracker/SKILL.md:33` | **Partial** | T4 plan (M) — JSON schema 拡張 |
| P20 | Meeting Agenda | "agenda with time allocations / pre-read 1 page" | 該当なし | **N/A** | — |
| P22 | Code Reviewer | "If the code is solid, say so. Do not invent issues to seem thorough" | `code-reviewer.md:14-16,20,88-89` "Findings / Scores / Verdict" + "LGTM — no issues detected" + "誤検出を除外する" | **Already 強化可能** (誤読訂正) | `:20` 後に "問題を作るために推測しない" 明文化 — **実装済 (S2)** |
| P31 | Market Research | "market size / players / 5 emerging trends..." | `research/SKILL.md:91,261` + `research-report-template.md:27` | **Partial** | T1 plan (M) — `--template=market` preset |
| P32 | Trend Spotter | "5 accelerating / 3 peaking / 2 emerging" | `research/SKILL.md:99-101` "contrarian / historical / empirical" | **Partial** | T1 plan (M) — `--template=trend` preset |
| P35 | Literature Review | "field overview / theories / 5 key papers" | `paper-analysis/SKILL.md:186-188,199-205,213,241` | **Already 強化可能** | `:241` "Must-Read Papers (3) → (5)" — **実装済 (Sub)** |
| P36 | Decision Matrix | "weighted criteria (1-5) × scores (1-10)" | `think/SKILL.md:148-160,186-193` "重み (1-5) + 加重合計 + 撤退条件" | **Already 強化可能** | T3 plan (M) — `/10` 明文化 + 「別選択肢が上回る条件」 |
| P37 | Risk Assessment | "likelihood/impact/mitigation/contingency" | `references/pre-mortem-checklist.md:35-43,54-56` + `references/reversible-decisions.md:33-39` | **Already 強化可能** | T3 関連 / pre-mortem-checklist の risk matrix 拡張 |
| P41 | Daily Task Prioritizer | "must do / should do / can wait... Flag delegateable" | `timekeeper/SKILL.md:92,94,96-98,100` "最重要 / 優先順 / 時間ブロック / やらない" | **Already 強化可能** | T2 関連 / `:94` を Must/Should/Can wait 分類に |
| P45 | SOP Writer | "Purpose/Scope/Prerequisites/Step-by-step..." | `docs/playbooks/codex-rules-operations.md:5` + `symlink-management.md:12,19` + `document-factory.md:146` | **Partial** | T5 plan (M) — document-factory に SOP type 追加 |
| P49 | Weekly Review | "7 questions one-at-a-time" | `weekly-review/SKILL.md:53,195-205,211-221` + `weekly-report.md:19-31` | **Already 強化可能** | T2 plan (M) — 7-Q reflection + max 5 action items |
| P50 | Life Decision | "which failure would I regret more" | `think/SKILL.md:148-160,170-175,186-193,195-205` | **Partial** | T3 plan (M) — regret asymmetry + change-condition |

### Codex Pass 2 Summary
- **Already 強化可能**: 7 件 (P1, P22, P35, P36, P37, P41, P49)
- **Partial**: 7 件 (P3, P16, P19, P31, P32, P45, P50)
- **Gap**: 0 件
- **N/A**: 2 件 (P7, P20)

## Integration Decisions (Final)

### S 規模即実装 (本セッション完了)

| # | 変更ファイル | 変更内容 |
|---|---|---|
| S1 | `mizchi-blog-style/SKILL.md` テーブル | LinkedIn fluff / 段落 3 文 / bold hook の 3 row 追加 |
| S2 | `code-reviewer.md:20` 直後 | "問題を作るために推測しない。`file:line` と再現可能な根拠がない指摘は Non-Finding に降格" 明文化 |
| Sub | `rewrite/SKILL.md:84` | `repurpose` chain (1 source → 5 platform-native pieces) 追記 |
| Sub | `paper-analysis/SKILL.md:241` | "Must-Read Papers (3) → (5)" 拡張 |

### M 規模 plan 保存 (5 タスク)

詳細: [docs/plans/active/2026-05-25-khairallah-50-prompts-m-tasks.md](../plans/active/2026-05-25-khairallah-50-prompts-m-tasks.md)

| Task | 影響 file | Prompts | Size |
|------|----------|---------|------|
| T1 | `research/SKILL.md` + templates | P31, P32 | M |
| T2 | `weekly-review/SKILL.md` + templates | P16, P49 | M |
| T3 | `think/SKILL.md` + `decision/SKILL.md` | P36, P50 (+ P37) | M |
| T4 | `feature-tracker/SKILL.md` + `spec/SKILL.md` | P19 | M |
| T5 | `document-factory.md` + `playbooks/` | P45 | M |

### N/A 確定

- P7 (SEO Optimizer): 個人 dotfiles で SEO 専用 skill 化するほどの反復価値なし
- P20 (Meeting Agenda): 個人 dev で頻発しない

### 真の scope out (Codex Q1 で同意)

P2/P4-P6/P8-P15/P17/P18/P33/P34/P38-P40/P42-P44/P46/P47 は dotfiles の個人 dev engineering harness で頻発しないため scope 外。これは正当な絞り込み。ただし初回 80% を一括 N/A した粒度は粗かった。

## Meta-Learnings (重要)

### 1. /absorb の手続き面 anti-pattern (今回学習)

| 罠 | 今回の発生 | 防止策候補 |
|---|---|---|
| Effort-Avoidance bias by "skip 推奨" framing | Phase 1.5 で "Khairallah author 4 件目" を理由に skip ラベル先頭提示 | `references/topic-family-saturation.md` の selection prompt から "(推奨)" ラベルを外し、verbatim 件数を提示するに留める |
| Phase 2.5 skip with self-preference bias | light-phase2 で「Gap 0 件」確定前に Codex 並列批評を必須化していなかった | SKILL.md anti-pattern に「light-phase2 でも Gap 0 件確定の前に Codex 単独 Pass 2 verbatim 確認必須」を追加 |
| Sonnet exploration spiral 報告の二次引用 | code-reviewer.md:168 を Sonnet 経由で「coldness_bias = don't invent issues」と誤判定 | Opus が委譲先報告の重要 line は **直接 Read で verify** することを明文化 |
| Scope mismatch の granularity 不足 | 40 件を一括 N/A、per-prompt 検証なし | scope-out 判定は **prompt 単位** で行い、Part 単位の一括判定を禁止 |

### 2. dotfiles の対応 skill カタログを Phase 1.5 で先に enumerate すべき

今回は Phase 1.5 で「Khairallah author 4 件目」だけで saturation 判定したが、dotfiles 側に対応 skill (research / think / weekly-review / timekeeper / spec / mizchi-blog-style 等) が実在することを明示的に enumerate しなかった。**Phase 1 抽出直後に「対応 skill 候補リスト」を Sonnet Explore に dispatch すべき**。

### 3. user の「手抜きでは？」介入が valuable

絶対的に正しい self-evaluation は困難。user の単純な疑問が effort-avoidance bias を破る decisive intervention になった。

### 4. Codex (gpt-5.5, xhigh reasoning) は self-preference bias 補正に有効

Opus 単独だと "Sonnet 報告で十分" と判断するが、Codex は code-reviewer.md:168 を独自 Read して誤読を指摘。**model-family diversity (OpenAI vs Anthropic) の bias mitigation 効果が実証**。

## References

- **Khairallah 過去 absorb (author family)**:
  - [Routines (2026-05-14)](2026-05-14-claude-code-routines-absorb-analysis.md) — 4 件採用 (peak)
  - [40 Features (2026-05-22)](2026-05-22-khairallah-40-features-absorb-analysis.md) — 0 件採用 + Sonnet imagination 4 件罠
  - [30 Workflows (2026-05-23)](2026-05-23-khairallah-30-workflows-absorb-analysis.md) — 2 件採用 (light-phase2 self-correction)
  - 本記事: **初回 0 件 → user 介入 → Codex 検証 → 4 件即実装 + 5 M plan**

- **Anti-pattern references**:
  - `/absorb` SKILL.md L446 (Sonnet imagination 罠)
  - `memory/feedback_absorb_sonnet_imagination.md`
  - `memory/feedback_absorb_already_deepdive.md` (Already=存在確認≠品質保証)

- **Implementation source (Pass 2 verification)**:
  - Codex Pass 2 verbatim result: `/tmp/codex-absorb-pass2-result.md` (16/16 件 verbatim 照合済)
  - Codex 1st critique: `/tmp/codex-absorb-critique-result.md` (Verdict: mixed/手抜き、Q1-Q5 詳細)

- **M-task plan**: [docs/plans/active/2026-05-25-khairallah-50-prompts-m-tasks.md](../plans/active/2026-05-25-khairallah-50-prompts-m-tasks.md)
