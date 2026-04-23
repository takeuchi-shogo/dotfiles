---
status: active
last_reviewed: 2026-04-23
---

# Top 67 Claude Skills 記事 — Absorb 分析

**Date:** 2026-04-19
**Source:** X/Twitter 経由の記事「Top 67 Claude Skills That Turn a $20 Subscription Into a Full Dev Team」(polydao 投稿)
**Status:** Analyzed — 2 skills + 1 existing strengthening 採用、プラン: `docs/plans/active/2026-04-19-top67-skills-integration-plan.md`

## 記事の主張

Claude は単なるオートコンプリートではなく、スキル (SKILL.md folder) を使えば dev team (architect/reviewer/debugger/docs writer) として機能する。67 個のキュレーションされた Claude Skills を install コマンドと共に紹介。

**主要リポジトリ:**
- 公式: github.com/anthropics/skills
- Matt Pocock (15k stars): github.com/mattpocock/skills
- Community marketplace (66k+): skillsmp.com
- Superpowers suite: github.com/obra/superpowers

## 構造化抽出

### 手法カテゴリ (67 skills)

| カテゴリ | 件数 | 代表例 |
|---------|------|--------|
| Meta | 3 | Skill Creator, Write a Skill, Find Skills |
| Planning/Design | 6 | Grill Me, Write a PRD, PRD to Plan/Issues, Design an Interface, Request Refactor Plan |
| Code Dev | 16 | TDD, Triage Issue, QA, Code Review, Systematic Debugging, Brainstorming, Superpowers suite |
| Tooling/Setup | 4 | Setup Pre-Commit, Git Guardrails, Dependency Auditor, Git Work Trees |
| Issue/Project | 1 | GitHub Triage |
| Writing/Knowledge | 5 | Edit Article, Ubiquitous Language, API Doc Generator, Content Researcher, Obsidian Vault |
| UI/Design | 7 | Frontend Design, Theme Factory, Canvas Design, Brand Guidelines 等 |
| Business/Marketing | 6 | Stripe, Lead Research, Marketing Skills, Claude SEO 等 |
| Media | 5 | Nano Banana, Image Optimizer, Remotion, Video Toolkit |
| Office | 8 | PDF, DOCX, PPTX, XLSX, Excel MCP, GWS 等 |
| Multi-agent/Web | 5 | Stochastic Consensus, Model-chat Debate, Playwright, Firecrawl |

### 根拠

- Matt Pocock skills の 15k stars, SkillsMP の 66k+ skills という社会的証明
- 「67 個全部入れろ」ではなく「各セクションから 1 つ install」という段階的採用を推奨
- Meta skills (Skill Creator / Write a Skill) をまず入れることを強調

### 前提条件

- Claude Code + npm skills CLI 前提
- 個人 dev が "full dev team" を欲している文脈（ソロ開発者向けマーケティング）
- まだスキルを活用していない読者が主対象

## ギャップ分析 (Phase 2 + 2.5 Codex 批評後)

### Already (34 skills) — 既にカバー済み

記事の 67 skills のうち約半数は、このセットアップで以下いずれかによって既にカバー:
- ローカルスキル 93個 (`~/.claude/skills/`)
- Superpowers plugin (writing-skills/systematic-debugging/brainstorming/tdd/using-git-worktrees 等)
- サブエージェント 32個 (code-reviewer/security-reviewer/debugger 等)
- MCP tools (playwright, context7, code-review-graph)
- skills.sh 経由インストール (pdf, browser-use, supabase-postgres, cloudflare, redis)

代表マッピング:
- TDD → `superpowers:test-driven-development`
- Systematic Debugging → `superpowers:systematic-debugging`
- Brainstorming → `superpowers:brainstorming`
- Git Work Trees → `superpowers:using-git-worktrees`
- Write a Skill → `superpowers:writing-skills` + `skill-creator`
- Simplification Cascade → `simplify` skill
- Git Guardrails → `careful` skill + Lefthook + `protect-linter-config` hook
- PRD to Issues → `prd-to-issues` skill + `create-issue`
- Code Review → `review` skill + code-reviewer/codex-reviewer agent
- Obsidian Vault → `obsidian-vault-setup` + `obsidian-content` + `obsidian-knowledge` + obsidian plugin
- Stochastic Multi-Agent Consensus / Model-chat Debate → `debate` skill
- Playwright CLI → mcp\_\_playwright\_\_\*
- Image Generator → `nano-banana` skill
- PDF Processing → skills.sh installed

### Partial (8 skills) — 部分対応

- Write a PRD — `spec` skill (Prompt-as-PRD) は存在するが、interview フェーズが弱い
- PRD to Plan — `epd` で多段階だが tracer-bullet vertical slice は弱い
- Request Refactor Plan — `refactor-session` + `improve-codebase-architecture` で部分対応
- Triage Issue — `fix-issue` あるが TDD-based fix plan 生成は弱い
- QA — `validate` + `webapp-testing` で部分的
- Setup Pre-Commit — Lefthook で Go/TS/Python 横断だが Husky+lint-staged 専用は無し
- GitHub Triage — `github-pr` + `kanban` で部分
- Content Researcher — `research` は一般リサーチ、ライティング特化は無し

### Gap (2 skills, Codex 批評後厳選) — 真に価値あり

1. **Ubiquitous Language** — DDD glossary 抽出・コード/PRD/Issue との語彙 drift 検出。Memory では代替困難 (glossary artifact + 差分レビューが独立機能)
2. **Dependency Auditor** — 依存更新/license/supply-chain/unused dependency/lockfile diff の専用 lens。code-reviewer とは視点が独立

### 既存強化 (1件)

3. **`spec` skill 強化** — Write a PRD 相当の interview フェーズを Phase 0 として追加。新規スキル作成より upstream gate として拡張する方が波及効果大

### N/A (23 skills) — 当セットアップには不要

Office 系 (DOCX/PPTX/XLSX/GWS/Doc Co-Authoring)、マーケティング系 (Stripe/Lead Research/Marketing Skills/Claude SEO/YouTube)、メディア編集系 (Image Optimizer/Remotion/Video Toolkit)、デザイン特化 (Theme Factory/Canvas/Brand Guidelines/Algorithmic Art/Web Artifacts Builder)、niche migration (Migrate to Shoehorn)、教育系 (Scaffold Exercises) — いずれも個人 dev workflow の焦点外。MEMORY.md の **Pruning-First 方針** および **IFScale (指示数が重要)** の制約に反する。

## Codex 批評で却下した候補

記事で紹介され、一見取り込み価値がありそうだが除外:

- **Change Log Generator** — `/commit` (conventional commit) + Review Gate + PRD/Issue workflow + Lefthook で材料は揃っている。専用 skill より既存 workflow の output option で十分
- **API Documentation Generator** — API 設計/doc 生成の頻度が高くなければ、PRD workflow + Context7 MCP + Code Review で足りる。専用化は Brevity Bias に反する

## Codex 批評の核

> 「67個すべて良い」は記事側のマーケティング文脈に引っ張られすぎ。個人開発者を "full dev team" 化する話と、既に multi-model orchestration、Review Gate、shared memory、MCP、Lefthook を持つ環境では限界効用が違う。Pruning-First なら、新規 skill は「既存 skill の説明に1行足す」より強い理由が必要。

→ 採用 2 件 + 強化 1 件に絞ることで Skill discovery cost の増大を最小化。

## 採用判断

| 項目 | 採用 | 規模 | パス |
|------|------|------|------|
| Ubiquitous Language 新規 skill | Yes | M | `~/.claude/skills/ubiquitous-language/` |
| Dependency Auditor 新規 skill | Yes | S-M | `~/.claude/skills/dependency-auditor/` |
| `spec` skill 強化 (PRD interview) | Yes | S | `~/.claude/skills/spec/SKILL.md` |
| Change Log Generator | No | — | `/commit` で代替 |
| API Doc Generator | No | — | Context7 + PRD workflow で代替 |
| 他 23 件 | No | — | N/A (用途外) |

合計: skill 数 93 → 95 (+2)、既存強化 1

## Next Steps

- 実装プラン: `docs/plans/active/2026-04-19-top67-skills-integration-plan.md`
- 新セッションで `/rpi docs/plans/active/2026-04-19-top67-skills-integration-plan.md` を実行
- MEMORY.md には本レポートへの 1 行ポインタのみ追記

## Related Research

- [feedback_claudemd_length.md](../../memory/feedback_claudemd_length.md) — IFScale: 指示数の増加は性能を下げる
- [reference_brevity_tradeoff_research.md](../../memory/reference_brevity_tradeoff_research.md) — Brevity Bias と agent harness 失敗パターン
- `references/improve-policy.md` — Pruning-First 方針
