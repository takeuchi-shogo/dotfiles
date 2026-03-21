# OpenAI Frontend Prompt Workflow Templates

このファイルは OpenAI の frontend blog と公開 `frontend-skill` をもとにした再構成版テンプレート集。
OpenAI がこのままの 1 本を公式配布しているわけではない。

## Source Mapping

- official-derived:
  - low / medium reasoning から始める
  - visual references / mood board
  - design system tokens
  - typography roles
  - narrative structure
  - full-bleed hero
  - cardless default
  - brand first
  - motion 2-3
  - desktop / mobile verification
  - Playwright validation
- custom packaging:
  - intake questions
  - output modes
  - ChatGPT / Codex / API 別の整形

## Intake Checklist

- surface type: landing page / app / dashboard / mixed
- product / brand
- audience
- style
- palette
- mood
- composition
- copy / context / goal
- CTA
- implementation target: ChatGPT / Codex / Responses API
- reference UI or screenshot
- image generation needed or not

## Ask-Back Message Template

```text
prompt を正しく組むために、先に4点だけください。

1. 何を作る prompt ですか。landing page / app / dashboard のどれですか。
2. product / brand と audience は何ですか。
3. visual direction はありますか。なければ style / palette / mood だけでも大丈夫です。
4. 実際に使う copy、goal、CTA はありますか。
```

## Template: Landing Page

```text
GPT-5.4 を使って、React と Tailwind で visually strong な landing page を作成してください。
reasoning は low から開始してください。

実装前に、まず以下の3つを書いてください。
- visual thesis: mood, material, energy を1文で示す
- content plan: hero, support, detail, final CTA
- interaction thesis: ページの印象を変える 2-3 個の motion idea

必要なら最初に mood board または複数の visual option を作成してください。
visual reference を作るときは、以下の属性を明示してください。
- style: [style]
- color palette: [palette]
- composition: [composition]
- mood: [mood]

画像については以下に従ってください。
- uploaded / pre-generated image があれば優先して使う
- なければ image generation tool を使う
- 明示要求がない限り web image を参照・リンクしない
- imagery は product, place, atmosphere, context のいずれかを見せる
- decorative gradient や abstract background だけを main visual にしない
- signage, logo, typographic clutter が UI と競合する画像を使わない
- collage が必要ない限り、複数の瞬間は複数画像で扱う

以下の design system を最初に定義してください。
- tokens: background, surface, primary text, muted text, accent
- typography roles: display, headline, body, caption
- typeface は最大 2 つ
- accent color は基本 1 つ

page structure は以下を基本にしてください。
1. Hero
2. Support
3. Detail
4. Final CTA

もし social proof が必要なら追加してよいですが、section 数は 6 以下にしてください。

Hero は以下を守ってください。
- first viewport は one composition として読めるようにする
- hero は full-bleed image または dominant visual plane を基本にする
- branded landing page では hero 自体を edge-to-edge にし、inner text/action column だけを制約する
- brand first, headline second, body third, CTA fourth
- brand または product name は hero-level signal にする
- headline が brand を上回らないようにする
- hero の text column は narrow にし、image の calm area に置く
- text over image は strong contrast と clear tap targets を保つ
- hero に detached badge, floating badge, promo sticker, info chip, callout box を載せない
- hero に cards を使わない
- hero の first viewport には通常、brand, 1 headline, 1 short supporting sentence, 1 CTA group, 1 dominant image だけを置く
- stats, schedules, event listings, promos, metadata rows, secondary marketing content を first viewport に置かない
- sticky/fixed header がある場合は hero budget に含める
- 100vh/100svh を使う場合は persistent UI chrome を差し引くか、header を overlay する

Section rules:
- 各 section は one job, one headline, one dominant visual idea, one primary takeaway/action
- no more than one dominant idea per section
- pill clusters, stat strips, icon rows, boxed promos, competing text blocks を避ける
- card は default で使わない
- border, shadow, background, radius を外しても理解や操作に影響がないなら、それは card にしない
- copy は短く、scan しやすくする
- product language を使い、design commentary を UI に出さない
- supporting copy は通常 1 文程度
- 30 percent 削って良くなるなら削る

Motion:
- visually led work なら 2-3 個の intentional motion を入れる
- hero の entrance sequence を 1 つ
- scroll-linked / sticky / depth effect を 1 つ
- hover / reveal / layout transition を 1 つ
- motion は noticeable, smooth on mobile, fast, restrained, consistent であること
- ornamental only なら削除する

Implementation:
- generic, overbuilt layout を避ける
- purple-on-white defaults に寄せない
- desktop / mobile の両方で正しく見えるようにする
- React では useEffectEvent, startTransition, useDeferredValue を必要時に優先し、既存方針がない限り useMemo/useCallback を増やさない

実データとして以下を使ってください。
[copy/context/goal]

最後に Playwright で以下を確認してください。
- rendered page inspection
- desktop / mobile viewport
- navigation and layout behavior
- overlap / state issue
- reference がある場合は visual alignment
- brand が first screen で明確か
- strong visual anchor があるか
- headline だけ読んで page が理解できるか
- cards が本当に必要か
- motion が hierarchy / atmosphere を改善しているか
```

## Template: App / Dashboard

```text
GPT-5.4 を使って、React と Tailwind で app / dashboard UI を作成してください。
reasoning は low または medium から開始してください。

実装前に、まず以下の3つを書いてください。
- visual thesis
- content plan
- interaction thesis

以下の design system を最初に定義してください。
- tokens: background, surface, primary text, muted text, accent
- typography roles: display, headline, body, caption
- few colors を基本にする
- accent color は原則 1 つ

App UI は以下を中心に構成してください。
- primary workspace
- navigation
- secondary context or inspector
- one clear accent for action or state

以下を基本方針にしてください。
- calm surface hierarchy
- strong typography and spacing
- dense but readable information
- minimal chrome
- cards only when the card is the interaction

以下は避けてください。
- dashboard-card mosaics
- thick borders on every region
- decorative gradients behind routine product UI
- multiple competing accent colors
- ornamental icons that do not improve scanning

panel が plain layout でも意味を保てるなら、card treatment を外してください。

Copy rules:
- utility copy を marketing copy より優先する
- orientation, status, action を優先する
- hero section は明示要求がある場合以外は入れない
- working surface から始める: KPIs, charts, filters, tables, status, task context
- section heading は area の意味または user action を示す
- aspirational hero line, metaphor, campaign-style language, executive-summary banner を product surface に入れない
- supporting text は scope, behavior, freshness, decision value を1文で示す
- operator が headings, labels, numbers だけ見ても理解できることを目標にする

fixed / floating UI は text, button, key content と重ならないように safe area に置いてください。

必要なら motion を使ってよいですが、noise ではなく hierarchy と affordance の強化に限定してください。

実データとして以下を使ってください。
[context/data/workflow]

最後に Playwright で以下を確認してください。
- rendered app inspection
- 複数 viewport
- key flow navigation
- state / navigation issue
- fixed / floating layout safety
- headings, labels, numbers だけで即座に理解できるか
```

## Template: Short ChatGPT Version

```text
GPT-5.4 で React + Tailwind の frontend を作ってください。reasoning は low から始めてください。

最初に visual thesis、content plan、interaction thesis を書いてください。
必要なら mood board を先に出してください。

design constraints:
- one H1
- max 6 sections
- max 2 typefaces
- one accent color
- one primary CTA above the fold

define:
- tokens: background, surface, primary text, muted text, accent
- typography: display, headline, body, caption

landing page なら:
- first viewport must read as one composition
- brand first
- full-bleed hero
- no hero cards
- one dominant visual anchor

app/dashboard なら:
- utility copy over marketing copy
- workspace-first layout
- avoid dashboard-card mosaic

use real copy and context:
[copy/context/goal]

verify desktop/mobile layout and key flows before finishing.
```

## Template: Handoff To Frontend Skill

```text
Use $frontend-skill.

Build this frontend with the following brief.

Surface:
- [landing page / app / dashboard]

Product and audience:
- [product / brand]
- [audience]

Visual direction:
- style: [style]
- palette: [palette]
- mood: [mood]
- composition: [composition]

Content:
- goal: [goal]
- CTA: [CTA]
- required sections: [sections]
- real copy/context: [copy/context]

Implementation constraints:
- Use React + TypeScript + Tailwind
- Start with reasoning low unless complexity clearly requires medium
- If a screenshot or reference UI is attached, match spacing, hierarchy, and visual rhythm closely
- Verify desktop/mobile and fix overlap, hierarchy, and navigation issues before finishing

Before coding:
- write visual thesis
- write content plan
- write interaction thesis
```
