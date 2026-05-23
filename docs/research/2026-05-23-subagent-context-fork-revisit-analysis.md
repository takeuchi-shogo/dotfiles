---
source: "Keep your Claude Code context clean with Subagents (aitmpl 系記事 — 同一記事の再投入)"
date: 2026-05-23
status: validation-only-follow-up
supersedes: null
tracks-back-to: 2026-04-27-subagent-context-fork-absorb-analysis.md
related-absorbs:
  - 2026-05-04-distribution-vs-escalation-absorb-analysis.md
  - 2026-05-22-anthropic-engineers-token-savings-absorb-analysis.md
---

# Subagent Context Fork (revisit) absorb 分析

## ソース

- 記事: 同 aitmpl 系 "Keep your Claude Code context clean with Subagents"
- 取り込み日: 2026-05-23
- 注: 2026-04-27 に同じ記事を一度 absorb 済 (frontmatter `tracks-back-to` 参照)

## Saturation Gate (Phase 1.5)

- family: **subagent / context-fork**
- N: 5+ 件 (subagent-patterns / skill-subagent-composition / subagents-claude-code / subagent-context-fork / 30-subagents-2026)
- 完全一致先行例: 2026-04-27-subagent-context-fork-absorb-analysis.md (同 aitmpl 記事)
- 採用率: 前回 3 件採用済
- 手法 delta: **0 (pure-rehash)** — Phase 1 抽出 8 手法すべて前回と一致
- 判定: SATURATED-pure-rehash → ユーザーは `continue` (フル workflow) を選択

## Phase 2 (light revisit) — 前回採用 3 タスクの実施状況確認

Sonnet Explore で前回 T2/T3/T4 の現状を調査。

| 前回タスク | 採用判定 (2026-04-27) | 現状 (2026-05-23) |
|---|---|---|
| T2 context-monitor.py に event timeline 追加 | 採用 | **未実施** (statusline 用のみ稼働、JSONL ログ機能なし) |
| T3 observability-signals.md に 3 指標追加 (Explore 命中率 / Plan 差し戻し率 / cache hit rate) | 採用 | **ドキュメント化のみ** (計測機構なし) |
| T4 references/fork-experiment.md 新規作成 | 採用 | **未作成** |

## Phase 2.5 (Codex + Gemini)

### Codex (gpt-5.5 read-only) 判定

- 記事採用 0 妥当、Reference Only + Validation-only follow-up で OK
- **T3 cache hit rate** → 2026-05-22 で session_observer 側に **実装済** (棚卸し: superseded/吸収済)
- **T2 event timeline** → agent-invocation-logger + SubagentStop monitor で部分充足、追加 timeline は不要 (narrowed)
- **T4 /fork ガイド** → **廃止寄り**。新規ファイル不要、`subagent-delegation-guide.md` に 1 段落注記で十分 (narrowed)
- **副次採用あり**: `/absorb` に「過去採用タスクが 30 日未実施なら、再採用前に superseded / narrowed / retired を明示」する **stale-plan audit** を入れる価値あり
- 「未実施タスクを backlog と見すぎている」と指摘。今回の価値は記事ではなく **古い採用判断の剪定**

### Gemini grounding 補足 (要 verification)

- `/fork` と `CLAUDE_CODE_FORK_SUBAGENT=1` は v2.1.117+ で experimental → stable に昇格と主張 (出典: spybara.com/anthropic/claude-code/history、信頼度: 中)
- aitmpl context-timeline は 2026-04 更新 (Opus 1M 対応)
- 2026-05-22 Token Savings 記事の TTL 三層 + Prefix Sharing 10x cheaper を裏付け

仮に stable 化が事実でも、**context cleanliness と逆方向**の設計判断は不変 → N/A (intentional non-adoption) を維持。

## Integration Decisions

### 記事採用

| # | 項目 | 判定 |
|---|------|------|
| 1-8 | 全 8 手法 | **採用 0** (前回 2026-04-27 で analyze 済、新規論点 delta=0) |

### 副次採用 (validation-only follow-up)

| # | 項目 | 判定 | サイズ |
|---|------|------|--------|
| A1 | `/absorb` に Stale-Plan Audit step (Step 7) を追加 | 採用 | S |
| A2 | 2026-04-27 レポートの棚卸し (frontmatter `status: partially-superseded` + 棚卸し追記) | 採用 | S |
| A3 | `subagent-delegation-guide.md` に `/fork` 意図的非採用の 1 段落注記 | 採用 | S |

## Plan (実行済 — 同セッション内)

### A1: Stale-Plan Audit を /absorb に追加

- **Files**:
  - `.config/claude/skills/absorb/references/topic-family-saturation.md` (Step 7 を Safety rules の前に追加)
  - `.claude/skills/absorb/SKILL.md` (Phase 1.5 末尾に Step 7 pointer を追加)
- **目的**: 同 family の過去 absorb で採用したタスクが時間経過で陳腐化していないか mechanism で audit する。Phase 1.5 Saturation Gate の姉妹機能。
- **判定条件**: N >= 1 + `status` 未明示 + `date` から 30 日経過 → AskUserQuestion で implemented / superseded / narrowed / retired / kept を選択
- **安全側ルール**: `kept` 選択は明示的判断であり `kept-by: YYYY-MM-DD` を必須記録 (暗黙的放置との区別)

### A2: 2026-04-27 レポートの棚卸し追記

- **Files**: `docs/research/2026-04-27-subagent-context-fork-absorb-analysis.md`
- **Changes**:
  - frontmatter: `status: partially-superseded` + `audited` ブロック追加
  - 末尾に `## 棚卸し (2026-05-23 re-absorb)` セクション (T2/T3/T4 の再判定)

### A3: subagent-delegation-guide に /fork 注記

- **Files**: `.config/claude/references/subagent-delegation-guide.md` (Context Inheritance Policy セクション末尾、Subagent Prompt Cache TTL の前)
- **Changes**: `CLAUDE_CODE_FORK_SUBAGENT=1` と `/fork` の意図的非採用を 3 つの理由 (設計と逆方向 / 代替が機能 / Distribution vs Escalation 再確認) と共に 1 段落で明記

## Risks & Tradeoffs

- **Gemini grounding の verification 不足**: stable 化主張の出典 URL が大雑把 (`docs.claude.com`)。stable 化が事実でも判断は不変なので影響なし
- **Stale-Plan Audit のオーバーヘッド**: Phase 1.5 に Step 7 追加で 1 回の AskUserQuestion が増える。30 日未満 + status 明示は auto-skip なので通常パスへの影響は小
- **棚卸し UX のスケール**: audit 対象が 4 件以上ある family で AskUserQuestion が過負荷になる懸念 → 最新 3 件のみ対象、残りは log.md に「次回 audit 候補」記録で緩和

## Validation-only Follow-up

本 absorb で記事採用は 0 だが、副次発見として以下が確認された:

1. **前回採用タスク (T2/T3/T4) の 1 ヶ月停滞**: 「未実施タスクを backlog と見すぎる」failure mode を mechanism (A1 Step 7) で防ぐ
2. **drift 検出 (superseded の見逃し)**: T3 cache hit rate が 2026-05-22 session_observer 実装に吸収済であることが Codex 指摘で判明 → A2 棚卸しで明示化
3. **インライン注記による新規ファイル抑制**: T4 の「新規 file 作成」採用判断を A3 で「既存 reference に 1 段落 inline」に narrow → Pruning-First 原則

これは「article-backed novel instruction」ではなく「**platform drift validation triggered by article**」に該当する。Khairallah 40 Features absorb (2026-05-22) と同パターン。

## 関連リンク

- 前回 absorb (棚卸し対象): `docs/research/2026-04-27-subagent-context-fork-absorb-analysis.md`
- 関連 absorb:
  - 2026-05-04 Distribution vs Escalation (Forked subagent N/A 再確認)
  - 2026-05-22 Anthropic Token Savings (TTL 三層 + session_observer cache 実装、T3 を superseded 化した absorb)
- /absorb 強化: `.config/claude/skills/absorb/references/topic-family-saturation.md` Step 7 (新設)
- /fork 注記: `.config/claude/references/subagent-delegation-guide.md` Context Inheritance Policy セクション
