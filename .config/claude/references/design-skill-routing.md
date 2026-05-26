# Design / Frontend Skill Routing

19 個の design / UI / frontend 関連 skill の使い分けマトリクス。
117 skill 中の routing degradation を防ぐため、Triggers と Do NOT use for を grid 化する。

> **vendor SKILL.md (taste-skill 系) は `npx skills add` で再 install すると上書きされる。** routing の master は本ファイル。SKILL.md 編集は最小限に留め、矛盾時は本ファイルが正。

## クイック判定フロー

```
新規 UI を作る?
├─ YES (greenfield)
│   ├─ Landing page / Portfolio / Marketing site (taste-skill 適用領域)
│   │   ├─ vibe: premium consumer (luxury, artisan, brand)         → soft-skill
│   │   ├─ vibe: editorial / Notion / Linear / minimalist           → minimalist-skill
│   │   ├─ vibe: experimental / Awwwards / agency (Beta)            → brutalist-skill
│   │   ├─ Codex agent + 高 GSAP motion 要求                         → gpt-taste
│   │   └─ default (vibe 不明 / 中庸)                                → taste-skill (v2)
│   ├─ SaaS Dashboard / Admin / data-heavy UI                       → frontend-design (plugin) or ui-ux-pro-max
│   ├─ Mobile App UI                                                → ui-ux-pro-max (実装) + imagegen-frontend-mobile (画像参照)
│   └─ 単発 component / Artifact / HTML 1 枚                          → frontend-design (plugin) or playground:playground
└─ NO (existing UI を直す)
    ├─ Full UI overhaul (cream→modern 等の rebrand)                 → redesign-skill
    ├─ Targeted polish (色味調整 / typography 整え)                   → impeccable
    └─ A11y / WCAG / Web Interface Guidelines 監査                  → web-design-guidelines
```

## 並列 / 補助 skill

| 用途 | Skill |
|------|------|
| 画像参照ボード生成 (web)                | `imagegen-frontend-web` |
| 画像参照ボード生成 (mobile)             | `imagegen-frontend-mobile` |
| Brand kit / Logo / Identity board     | `brandkit` |
| Codex 専用 image→code pipeline         | `image-to-code-skill` (Codex only) |
| Google Stitch 用 DESIGN.md 生成        | `stitch-skill` (Stitch only) |
| Truncation 防止 (長文 code 切れ抑制)    | `output-skill` |
| React/Next perf 最適化                 | `react-best-practices` |
| React composition pattern              | `vercel-composition-patterns` |
| UI 原則 reference (animation/typo 等)   | `userinterface-wiki` |

## 個別 skill 早見表

| Skill | install name | Trigger 領域 | Do NOT use for | 推奨 agent |
|------|-------------|------------|---------------|----------|
| `taste-skill` (v2) | `design-taste-frontend` | Landing / Portfolio / Redesign anti-slop, vibe 不明 | Dashboard, data tables, multi-step product UI | Claude Code / Codex |
| `gpt-taste` | `gpt-taste` | Codex agent + GSAP motion 強化、AIDA 構造 | Claude Code main session (taste-skill v2 優先) | Codex のみ |
| `soft-skill` | `high-end-visual-design` | premium consumer / luxury brief | Technical / B2B / dashboard | Claude Code / Codex |
| `minimalist-skill` | `minimalist-ui` | Notion / Linear / editorial brief | Premium consumer (use soft-skill), experimental | Claude Code / Codex |
| `brutalist-skill` (Beta) | `industrial-brutalist-ui` | Experimental / Swiss + military terminal vibe | Production sites, accessibility-first | Claude Code / Codex |
| `redesign-skill` | `redesign-existing-projects` | Full UI overhaul (audit + restructure) | New greenfield, targeted polish (use impeccable) | Claude Code / Codex |
| `image-to-code-skill` | `image-to-code` | Codex の image generate → analyze → code pipeline | Claude Code main session, dashboards | Codex のみ |
| `imagegen-frontend-web` | `imagegen-frontend-web` | Web デザイン参照画像生成 (per-section) | Code 生成、Claude Code 単独 (image-gen tool 必須) | ChatGPT Images / Codex image / MCP |
| `imagegen-frontend-mobile` | `imagegen-frontend-mobile` | Mobile screen / flow 画像生成 (mockup) | Code 生成、Web 用 | ChatGPT Images / Codex image / MCP |
| `brandkit` | `brandkit` | Logo / identity / brand board 画像生成 | Code 生成、UI 実装 | ChatGPT Images / Codex image / MCP |
| `stitch-skill` | `stitch-design-taste` | Google Stitch 用 DESIGN.md export | 一般 UI 実装、Stitch 非使用時 | Google Stitch |
| `output-skill` | `full-output-enforcement` | Truncation 防止、placeholder 禁止 enforce | 普通の短いタスク | All agents |
| `frontend-design` (plugin) | (Anthropic) | Production-grade 独自 UI、component / page / app | (上書き不可、plugin) | Claude Code |
| `ui-ux-pro-max` | `ui-ux-pro-max` | 10 stack 対応 UI/UX、accessibility 含む | Codex 専用 task (gpt-taste 使う) | Claude Code |
| `web-design-guidelines` | `web-design-guidelines` | UI コード review (WCAG / guidelines) | 実装、新規生成 | Claude Code |
| `impeccable` | `impeccable` | Targeted polish (色 / typography / motion) | Full overhaul (use redesign-skill) | Claude Code |
| `userinterface-wiki` | `userinterface-wiki` | UI 原則 reference (11 カテゴリ) | 実装、判断ゲート | Claude Code |
| `react-best-practices` | `react-best-practices` | React/Next perf 最適化 (40+ rules) | Vue / Svelte / プレーン HTML | Claude Code |
| `vercel-composition-patterns` | `vercel-composition-patterns` | React component composition | 非 React stack | Claude Code |

## メタ原則

1. **1 task で 1 greenfield skill**: 同一 task に対して greenfield UI 実装 skill を 2 つ以上同時起動しない。Tier A 7 個 (taste/gpt-taste/soft/minimalist/brutalist/frontend-design/ui-ux-pro-max) のうち、vibe → 1 つを決定する。
2. **vibe 明確 → 専用 skill、vibe 不明 → taste-skill v2**: brief の vibe word から逆引きする。`Awwwards`/`brutalist` → brutalist、`Linear`/`Notion`/`editorial` → minimalist、`luxury`/`premium consumer`/`heritage` → soft、それ以外 → taste-skill v2。
3. **redesign vs polish vs review**: existing UI を直す場合は **作業の規模** で分岐。full overhaul → redesign-skill / targeted polish → impeccable / guideline check → web-design-guidelines。
4. **画像生成系は agent 環境前提**: `imagegen-*` 3 個は image-gen tool (ChatGPT Images / Codex image mode / MCP image) が **必須**。Claude Code 単独 (text-only) では出力できない。
5. **Codex 専用 skill の routing**: `image-to-code-skill` と `gpt-taste` は Codex agent でのみ起動。Claude Code main session では taste-skill v2 + 既存 frontend-design に dispatch する。
6. **vendor SKILL.md は最小編集**: `npx skills add` で再 install すると frontmatter が上書きされる。重要な使い分け情報は本ファイルに集約する。

## 関連

- 既存 design skill との関係: `references/skill-relations.md` (もしあれば)
- skill 数全体管理: `references/improve-policy.md` Pruning-First セクション
- skill 健全性監査: `/skill-audit` (description 衝突検出)
- 飽和検出 (新規 absorb 時): `references/topic-family-saturation.md`
