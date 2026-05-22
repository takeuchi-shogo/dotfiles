---
source: "Khairallah (@eng_khairallah1) — How to Actually Set Up Claude. 40 Features Most Users Have Never Touched"
date: 2026-05-22
status: analyzed
verdict: Reject (採用 0) + validation-only follow-up 1 件 + meta-finding 2 件
---

# Khairallah「40 Features」absorb 分析

## Source Summary

**主張**: Claude (chat/desktop/code/API) には beginner が知らない 40 の機能/設定がある。設定すれば週 2-3 時間の生産性向上が得られる。

**手法 (40 features)**:
- Part 1: Chat (1-12) — Custom Instructions, Memory, Projects, Artifacts, Knowledge Files, Extended Thinking, LaTeX Rendering, Web Search, Conversation Styles, Keyboard Shortcuts, Multiple Conversations, Download/Share
- Part 2: Desktop/Cowork (13-22) — Cowork Tab, Folder Access Permissions, Scheduled Tasks /schedule, Sub-Agents, Slash Commands, Plugins (marketplace), Connectors (Gmail/Slack/GDrive/Calendar), Claude in Chrome, File Processing at Scale, Session History
- Part 3: Claude Code (23-32) — Claude Code terminal, Plan Mode Shift+Tab, CLAUDE.md, /compact /clear, Model Switching Opus/Sonnet, Screenshot Feedback, One Conversation Per Feature, Git Integration, MCP Server Connections, Context Engineering with .md
- Part 4: API (33-40) — API Access, System Prompts via API, Streaming Responses, Tool Use Function Calling, Temperature Control, Structured Outputs JSON Mode, Batch Processing, Evaluation Frameworks

**根拠**: 著者の experience narrative のみ。"2-3 hours/week saved" は unverifiable claim。検証可能な数値・事例・出典なし。

**前提条件**: Claude beginner〜intermediate ユーザー一般。dotfiles のような既存 harness 投資前提ではない。

## Phase 1.5: Saturation Gate 結果

**Family**: `claude-code-tips`
**過去 absorb 件数 (同 family)**: 10 件 (Top 67 Skills, Khairallah Routines, Boris 30 Tips, Three-Model Stack, 73% Overhead 9 Patterns, 100+ Skills Best 6, 12-rule CLAUDE.md, zodchixquant 15 Settings, 9 Overnight Agents, Claude Skills 6 法則)
**採用率**: 6/10 = 60% → 形式判定 **PASS (warning)**

ただし Opus の追加判断:
- 同著者 Khairallah の前回 (Routines, 4 件採用) は新機能 novel 解説、本記事は generic listicle で性格が異なる
- 内容パターンが過去 Reject 事例 (Boris 30 Tips: 公式 Docs 独自編纂 / 10 倍煽り) と一致
- ユーザー指示「手抜きしてない？」を受けてフル Phase 2-2.5 を実行

## Gap Analysis (Pass 1: 存在チェック) — Sonnet Explore 委譲結果

40 features すべて検証。判定サマリ:

| 判定 | 件数 | 該当 |
|------|------|------|
| Already (強化不要) | ~25 | Custom Instructions, Memory, Projects, Web Search, Sub-Agents, Slash Commands, Plan Mode, CLAUDE.md, /compact /clear, Model Switching, Git Integration, MCP, Context Engineering, API basics, JSON Mode, Streaming, Tool Use, Temperature, Evals 等 |
| partial | ~11 | Artifacts, Extended Thinking, Keyboard Shortcuts, Cowork Tab, Scheduled Tasks, Connectors, Claude in Chrome, Session History, Screenshot Feedback, One Conv Per Feature, Batch Processing |
| not_found | 3 | LaTeX (N/A), Download/Share Artifacts (N/A for CC), Plugins marketplace (skills.sh で代替) |
| Already (強化可能候補) | 5 (Sonnet TOP 5) | Per-Project CLAUDE.md, Scheduled Tasks Bridge, Extended Thinking Budget, Bulk Processing playbook, Session JSON schema |

## Already Strengthening Analysis (Pass 2: Sonnet imagination 除外)

Sonnet が出した TOP 5 強化候補について、**記事原文の該当文と照合**:

| # | Sonnet 提案 | 記事原文 | 判定 |
|---|-----------|---------|------|
| S1 | Per-Project CLAUDE.md template | "Create a file called CLAUDE.md in your project root. ... Every time you correct Claude twice on the same thing, add it to CLAUDE.md." | **Sonnet imagination** — 記事は基本コンセプトのみ、template 提案なし。既存 `<repo>/CLAUDE.md` + `~/.claude/CLAUDE.md` + "correct twice → add" rule 同等あり |
| S2 | Scheduled Tasks / Managed Agents Bridge | "Type /schedule in Cowork. Daily morning briefings. Weekly report generation. Friday file cleanup." | **Sonnet imagination** — 記事は use case 列挙のみ、Managed Agents bridge の話なし。`.config/claude/references/managed-agents-scheduling.md` で既に比較済 |
| S3 | Extended Thinking Budget Allocation table | "Ask Claude to 'think step by step' or enable extended thinking in settings" | **Sonnet imagination** — 記事は "use it" レベル、budget allocation 提案なし |
| S4 | Bulk Processing playbook | "Rename every file. Convert formats in bulk. Extract data from a hundred PDFs." | **Sonnet imagination** — examples 列挙のみ、playbook 化提案なし。YAGNI 違反 |
| S5 | Session JSON schema standardization | "Every session is saved with a full history" | **Sonnet imagination** — feature 存在の言及のみ、schema standardization 提案なし。`claude-observe.sh` で session observer 既存 |

**Pass 2 結論**: 5/5 すべて Sonnet が記事の generic phrasing から「強化案」を hallucinate していた。記事固有の specific novel insight = **0**。

## Phase 2.5: Codex + Gemini 並列批評結果

### Codex (codex:rescue, OpenAI gpt-5-class)

**判定**: Reject 維持 / 採用 0 件 / **validation-only follow-up 1 件**

Codex の重要 finding (Opus が見落としていた):
- dotfiles 内 `docs/guides/2026-05-09-claude-cowork-equivalents.md:5` に **「Claude Cowork は Anthropic 公式製品としては存在しない」と stale fact** が記載されている
- しかし現在の Anthropic 公式 Help Center で Cowork は confirmed feature (Claude Desktop の Cowork tab、2026 年初頭導入)
- 出典: [Get started with Claude Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork) / [Release notes](https://support.claude.com/en/articles/12138966-release-notes)
- これは記事を吸収するのではなく、**記事をきっかけにした platform drift audit** として扱う

Codex の追加指摘:
- 記事の真の factual issue は "invented terminology" ではなく **Cowork の重要制約の省略** (Desktop app awake 必要 / Compliance API 未収録 / 削除は明示許可必要 / usage limits 消費激しい)

### Gemini (Google Search grounding)

**判定**: 記事の事実認定は概ね正確、ただし誇張は激しい (Slop コンテンツ評価)

確認事項:
- "Cowork tab" は **実在の Anthropic 公式機能** (2026 年初頭 Claude Desktop に導入、Chat と並ぶ独立 mode)
- "Claude in Chrome" は **Anthropic 公式拡張機能** (Pro 以上向け)
- Khairallah は AI インフルエンサー (Web3Arabs 創設者)、Anthropic 公式情報を要約・発信。記事は技術コミュニティで Slop として批判される

### 3 モデル統合判定

| 項目 | Opus 当初 | Codex | Gemini | 確定 |
|-----|----------|-------|--------|------|
| TOP 5 採用 | 全て Sonnet imagination | 同意 | (中立) | **採用 0** |
| Cowork tab 実在性 | dubious | 公式実在 | 公式実在 | **実在 (Opus 誤り)** |
| Reject 判定 | Reject | Reject 維持 | (中立) | **Reject 維持** |
| Stale doc audit | 未検出 | **発見** | (未検査) | **1 件発見** |
| Sonnet imagination feedback memory 化 | 提案 | 賛同 | (中立) | **採用** |

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| - | TOP 5 強化候補 | **スキップ** | 全て Sonnet imagination、記事原文に specific 提案なし |
| - | partial 11 項目 | **スキップ** | 記事は generic 言及のみ、specific insight なし。dotfiles 既設定で機能的にカバー済 |

### Validation-only Follow-up (記事の framing が露出した既存 drift)

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| V1 | `docs/guides/2026-05-09-claude-cowork-equivalents.md` の Cowork 不在前提 | **採用 (stale doc 訂正)** | Codex 発見の platform drift。Cowork が実在することを反映して、dotfiles が Cowork を採用しない理由に書き直す |

### Meta-Findings (absorb workflow 自体の改善)

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| M1 | `/absorb` SKILL.md に Sonnet imagination ガード追加 | **採用** | Pass 2 で Sonnet 提案を採用候補に格上げする前に記事原文と引用照合する rule を anti-patterns に追加 |
| M2 | `/absorb` SKILL.md に未知用語 grounding rule 追加 | **採用** | "Cowork" 等の未知用語を即「factually dubious」と判定するバイアスを防ぐ。Phase 1 で Gemini grounding を先行する |
| M3 | `memory/feedback_absorb_sonnet_imagination.md` 作成 | **採用** | Already=存在確認≠強化不要 の逆方向 (Gap fabrication) を feedback memory に codify。両方向の罠を Pass 2 で同時に検査する |

## Plan (実装済み)

### Task 1: Cowork stale doc 訂正 (V1)

- **File**: `docs/guides/2026-05-09-claude-cowork-equivalents.md`
- **Changes**: Status を「2026-05-22 訂正」に更新。Section 1 タイトルを「Claude Cowork と dotfiles の役割分離 (採用しない理由)」に変更。Cowork 公式 docs リンク追加。Cowork 制約 (awake 必要 / Compliance 未収録 / 削除許可 / usage limits) を比較表に反映。dotfiles が Claude Code を選択する理由を 7 軸で明文化
- **Size**: S (1 ファイル、~30 行変更)
- **Status**: ✅ 実装済み

### Task 2: /absorb SKILL.md anti-patterns 追加 (M1, M2)

- **File**: `~/.claude/skills/absorb/SKILL.md`
- **Changes**: Anti-Patterns table に 4 行追加
  1. Sonnet 強化案を Pass 2 で検証せず昇格する罠 (Gap fabrication)
  2. 未知用語を grounding せず "factually dubious" 即断する罠
  3. 採用 0 = 終了 ではなく platform drift audit を別 ledger で扱う
  4. (Sonnet imagination の feedback memory link)
- **Size**: S (1 ファイル、+4 行)
- **Status**: ✅ 実装済み

### Task 3: feedback memory 作成 (M3)

- **File**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_absorb_sonnet_imagination.md`
- **Changes**: 新規作成。Sonnet imagination の発生事例 (本 absorb)、Pass 2 必須チェック、文体識別フィルター、`feedback_absorb_already_deepdive.md` との対関係を記録
- **Size**: S (新規 1 ファイル)
- **Status**: ✅ 実装済み

## Verdict

**最終推奨採用件数**: 0 件 (記事から)
**Validation-only follow-up**: 1 件 (stale doc audit)
**Meta-finding 採用**: 3 件 (skill 改善 + feedback memory)

記事自体は Reject (採用 0)、ただし absorb プロセスの meta-improvement が本 absorb の主たる成果。同分野 11 件目で初めて検出された pass 2 failure mode を codify。

## 関連

- `feedback_absorb_already_deepdive.md` — Already=存在確認≠品質保証 (過小評価の罠)
- `feedback_absorb_sonnet_imagination.md` — Sonnet imagination (過大評価の罠) — 本 absorb で新規作成
- `feedback_absorb_thoroughness.md` — 「手抜きしてない？」フィードバック原典 (2026-04-27 Codex/Claude Parity 由来)
- `docs/research/2026-05-14-claude-code-routines-absorb-analysis.md` — 同著者 Khairallah の前回 absorb (4 件採用、性格が異なる)
- `docs/research/2026-04-30-boris-30tips-absorb-analysis.md` — 同パターン記事の先行棄却 (公式 Docs 独自編纂)
