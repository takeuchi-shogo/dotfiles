# Design / Frontend Skill Routing

design / UI / frontend 関連 skill の使い分けマトリクス。
routing degradation を防ぐため、Triggers と Do NOT use for を grid 化する。

> **vendor SKILL.md (taste-skill 系) は `npx skills add` で再 install すると上書きされる。** routing の master は本ファイル。SKILL.md 編集は最小限に留め、矛盾時は本ファイルが正。

## クイック判定フロー

```
新規 UI を作る?
├─ YES (greenfield)
│   ├─ Landing page / Portfolio / Marketing site                    → taste-skill (v2)
│   ├─ SaaS Dashboard / Admin / data-heavy UI / Design system 体系設計 → ui-ux-pro-max
│   ├─ Mobile App UI (a11y 含む)                                    → ui-ux-pro-max
│   ├─ Polish / Distill / Critique / Energize / Calm (creative refine) → frontend-design (plugin)
│   └─ 単発 component / Artifact / HTML 1 枚                          → frontend-design (plugin) or playground:playground
└─ NO (existing UI を直す)
    ├─ Full UI overhaul (cream→modern 等の rebrand)                 → redesign-skill
    ├─ Targeted polish (色味調整 / typography 整え)                   → impeccable
    └─ A11y / WCAG / Web Interface Guidelines 監査                  → web-design-guidelines
```

## 並列 / 補助 skill

| 用途 | Skill |
|------|------|
| Brand kit / Logo / Identity board     | `brandkit` |
| プロジェクト root に DESIGN.md 配置 (grilling + awesome-design-md exemplar) | `design-md-init` |
| Truncation 防止 (長文 code 切れ抑制)    | `output-skill` |
| React/Next perf 最適化                 | `react-best-practices` |
| React composition pattern              | `vercel-composition-patterns` |
| UI 原則 reference (animation/typo 等)   | `userinterface-wiki` |

## 個別 skill 早見表

| Skill | install name | Trigger 領域 | Do NOT use for | 推奨 agent |
|------|-------------|------------|---------------|----------|
| `taste-skill` (v2) | `design-taste-frontend` | Landing / Portfolio / Marketing anti-slop (vibe 不明時の default) | Dashboard, data tables, multi-step product UI, design system 体系設計 (use ui-ux-pro-max), existing UI overhaul (use redesign-skill) | Claude Code / Codex |
| `redesign-skill` | `redesign-existing-projects` | Full UI overhaul (audit + restructure) | New greenfield, targeted polish (use impeccable) | Claude Code / Codex |
| `brandkit` | `brandkit` | Logo / identity / brand board 画像生成 | Code 生成、UI 実装 | ChatGPT Images / Codex image / MCP |
| `design-md-init` | (dotfiles 直置き) | プロジェクト root に DESIGN.md 配置 (grill-me 47 branch + awesome-design-md exemplar) | 既存 DESIGN.md の改修、greenfield UI 実装そのもの | Claude Code |
| `output-skill` | `full-output-enforcement` | Truncation 防止、placeholder 禁止 enforce | 普通の短いタスク | All agents |
| `frontend-design` (plugin) | (Anthropic) | Creative build/refine (polish / distill / critique / energize / calm)、単発 component / Artifact | Dashboard / Admin / design system 体系設計 (use ui-ux-pro-max), Landing / Portfolio (use taste-skill), UI review (use web-design-guidelines) | Claude Code |
| `ui-ux-pro-max` | `ui-ux-pro-max` | Design system / a11y / typography / color / chart の体系設計、SaaS Dashboard、Mobile App UI | Landing / Portfolio (use taste-skill), creative polish/refine (use frontend-design), UI コード review (use web-design-guidelines) | Claude Code |
| `web-design-guidelines` | `web-design-guidelines` | UI コード review 専用 (WCAG / Web Interface Guidelines / accessibility audit) | 実装 (use frontend-design / ui-ux-pro-max), 新規生成 (use taste-skill), 体系設計 (use ui-ux-pro-max) | Claude Code |
| `impeccable` | `impeccable` | Targeted polish (色 / typography / motion) | Full overhaul (use redesign-skill) | Claude Code |
| `userinterface-wiki` | `userinterface-wiki` | UI 原則 reference (11 カテゴリ) | 実装、判断ゲート | Claude Code |
| `react-best-practices` | `react-best-practices` | React/Next perf 最適化 (40+ rules) | Vue / Svelte / プレーン HTML | Claude Code |
| `vercel-composition-patterns` | `vercel-composition-patterns` | React component composition | 非 React stack | Claude Code |

## メタ原則

1. **1 task で 1 greenfield skill**: 同一 task に対して greenfield UI 実装 skill を 2 つ以上同時起動しない。Tier A 3 個 (taste-skill / frontend-design / ui-ux-pro-max) のうち、scope → 1 つを決定する。
2. **scope で逆引き**: Landing / Portfolio / Marketing site → taste-skill (v2)。SaaS Dashboard / Admin / design system 体系設計 / a11y → ui-ux-pro-max。Mobile App UI → ui-ux-pro-max。単発 component / Artifact / creative polish/refine (polish / distill / critique) → frontend-design。**UI レビュー (WCAG / guidelines audit) は実装 skill ではなく `web-design-guidelines` を使う** (実装 3 skill との明確な境界)。
3. **redesign vs polish vs review**: existing UI を直す場合は **作業の規模** で分岐。full overhaul → redesign-skill / targeted polish → impeccable / guideline check → web-design-guidelines。
4. **画像生成系は brand のみ**: `brandkit` のみが画像生成 skill (image-gen tool 必須)。UI 実装の参照画像が必要な場合は別途 ChatGPT Images / Codex image / MCP を使う (skill ではなく agent 環境前提)。
5. **vendor SKILL.md は最小編集**: `npx skills add` で再 install すると frontmatter が上書きされる。重要な使い分け情報は本ファイルに集約する。

## 関連

- 既存 design skill との関係: `references/skill-relations.md` (もしあれば)
- skill 数全体管理: `references/improve-policy.md` Pruning-First セクション
- skill 健全性監査: `/skill-audit` (description 衝突検出)
- 飽和検出 (新規 absorb 時): `references/topic-family-saturation.md`
