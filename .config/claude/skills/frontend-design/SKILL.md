---
name: frontend-design
description: >
  Create or refine frontend interfaces with high design quality. Use for building new web components, pages,
  artifacts, posters, or applications AND for refining existing UI code (polish, distill, critique, energize, calm).
  Avoids generic AI aesthetics.
  Triggers: 'UI作って', 'ページ作成', 'コンポーネント', 'デザイン改善', 'UI磨いて', 'polish', 'distill', 'UIがダサい', 'AI臭い'.
  Do NOT use for: UIレビュー/監査（use /web-design-guidelines）、フロントエンドアーキテクチャ（use /senior-frontend）、パフォーマンス最適化（use /react-best-practices）。
license: Complete terms in LICENSE.txt
metadata:
  pattern: generator
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

Before implementation, always write:
- **Visual thesis**: one sentence describing mood, material, and energy
- **Content plan**: hero, support, detail, final CTA for marketing surfaces; workspace, navigation, secondary context for app surfaces
- **Interaction thesis**: 2-3 motion ideas that materially change the feel of the page

If the task is underspecified, ask for or infer:
- **Surface type**: landing page, app, dashboard, or mixed
- **Product / brand / audience**
- **Real content**: actual copy, goal, CTA, required sections
- **Visual references**: screenshot, mood board, or explicit style / palette / composition / mood

If no visual reference exists and imagery matters, propose a quick mood-board direction first instead of jumping straight into generic layout work.

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

## Surface Rules

For landing pages and promotional surfaces:
- Treat the first viewport as a single composition, not a pile of components.
- Prefer a full-bleed hero or dominant visual plane.
- Make the brand or product name a hero-level signal.
- Default to no cards, especially in the hero.
- Give each section one job, one dominant visual idea, and one takeaway.
- Keep the hero budget tight: brand, headline, short support copy, CTA group, dominant visual.
- Use real imagery or a real-looking visual anchor; decorative gradients alone are not enough.

For apps and dashboards:
- Default to calm surface hierarchy and utility copy over marketing copy.
- Start from the working surface, not a homepage-style hero, unless explicitly requested.
- Use cards only when the card itself is the interaction.
- Avoid dashboard-card mosaics, thick borders on every region, and decorative gradients behind routine product UI.
- Optimize for scanability: headings, labels, numbers, status, and action should explain the product at a glance.

Across both:
- Limit the system by default: two typefaces max and one accent color.
- Motion should create presence and hierarchy, not noise.
- Verify desktop and mobile composition before considering the work complete.

## Refine Mode

When the user provides **existing UI code** to improve (not build from scratch), switch to Refine mode. The user may say "磨いて", "改善して", "polish", "distill", or reference a specific operation below.

### Operations

Five operations, each with a distinct lens. Apply one or combine as needed:

| Operation | Lens | What it does |
|-----------|------|-------------|
| **distill** | 削ぎ落とし | 過剰な装飾・コンポーネント・階層を除去。本質だけ残す。AI過剰UIの解毒剤 |
| **polish** | 仕上げ | タイポグラフィ・スペーシング・レイアウトリズムを精密調整。出荷前の最終パス |
| **critique** | 診断 | UXデザインレビュー + 技術品質チェック。コードは変えず、問題点と改善案を報告 |
| **energize** | 活性化 | 地味なUIに色・動き・インパクトを注入。colorize + animate + bolder を統合 |
| **calm** | 鎮静 | 過剰なUIをトーンダウン。コントラスト・密度・装飾を抑え、明瞭さを上げる |

### Refine Workflow

1. **診断**: 既存コードを読み、`references/anti-patterns.md` と `references/refine-operations.md` に照らして問題を特定
2. **方針**: どの operation を適用するか判断（ユーザー指定 or 自動判定）
3. **実行**: コードを修正。変更理由をインラインコメントで残さない（diff で分かる）
4. **検証**: 修正前後の視覚的差分を説明

### Auto-Detection

ユーザーが operation を指定しない場合、以下で自動判定:

- AI臭が強い（purple gradient, Inter, generic cards） → **distill**
- 機能は良いが雑 → **polish**
- 地味すぎる → **energize**
- 過剰すぎる → **calm**
- 判断つかない → **critique** で診断してから提案

## Skill Assets

- `references/anti-patterns.md` — Frontend design anti-patterns (Typography, Colors, Layout, Motion, General)
- `references/refine-operations.md` — Refine mode operation definitions and checklists
