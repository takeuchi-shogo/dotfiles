# Design Decision Tree (grill-me seed)

このドキュメントは `design-md-init` skill が `grill-me` に渡すシード。
47 branch をカテゴリ別に列挙、各 branch に **推奨デフォルト** と **判断材料** を併記する。

grill-me には以下の指示で渡す:

> 各 branch を 1 問ずつ relentlessly に grill してください。default を accept する場合は次へ進んで OK。
> ユーザーが「わからない」と答えたら推奨 default に倒し、選んだ理由を 1 行メモ。
> 全 47 branch 抜けたら、最後に vibe profile 5 軸 (vibe_word / density / variance / motion / mode) と
> deltas (exemplar に上書きしたい項目) を要約して返してください。

---

## A. Vibe / Atmosphere (6 branches)

### A1. vibe_word
近づけたいブランドを 1 つ選ぶ。exemplar マッチの主軸。
- 候補: `linear` / `stripe` / `notion` / `vercel` / `airbnb` / `apple` / `brutalist` / `editorial` / `playful` / `enterprise`
- **default: linear**(汎用 SaaS で最も無難)

### A2. density
情報密度。
- `airy`(art gallery、余白多) / `balanced`(daily app) / `dense`(cockpit、データ多)
- **default: balanced**

### A3. variance
レイアウトの規則性。
- `symmetric`(中央揃え、グリッド忠実) / `asymmetric`(オフセット、対角線) / `chaotic`(awwwards 系)
- **default: asymmetric**(generic を避ける最小コスト)

### A4. motion
動きの強度。
- `static`(transition のみ) / `fluid`(CSS animation 中心) / `cinematic`(GSAP / spring choreography)
- **default: fluid**

### A5. formality
口調 / 印象。
- `playful` / `professional` / `serious` / `editorial`
- **default: professional**

### A6. audience
ターゲット。
- `consumer` / `b2b-saas` / `developer-tool` / `enterprise` / `internal-tool`
- **default: b2b-saas**

---

## B. Color (7 branches)

### B1. mode
- `light` / `dark` / `both`(両対応)
- **default: both**(2026 年は両対応がベース)

### B2. neutral_base
基調の neutral 系統。
- `zinc`(青寄り無彩色) / `slate`(青寄り) / `stone`(暖系無彩色) / `gray`(中庸) / `warm-gray`
- **default: zinc**(Linear / Vercel 系の硬質感)

### B3. accent_count
強調色の数。
- `1`(最も洗練) / `2`(primary + secondary) / `3`(rare、データビズ用途)
- **default: 1**

### B4. accent_hue
accent 1 色目の系統。
- `blue` / `green` / `red` / `purple` / `orange` / `yellow` / `pink` / `teal` / `mono`(無彩色のみ)
- **default: blue**

### B5. accent_saturation
- `muted`(<60%) / `mid`(60-80%) / `vivid`(>80%、warning 表示色 OK)
- **default: mid**(ban: vivid purple/neon は anti-pattern)

### B6. semantic_palette
- `success / warning / error / info` を全部持つか、`error / success` だけか、無しか
- **default: full set**(form ある UI なら必要)

### B7. banned_palettes
明示的に避けたい色。
- AI 臭の典型: `ai-purple-neon` / `gradient-rainbow` / `pure-black-000` / `pure-white-fff`
- **default: ban ai-purple-neon + pure-black-000 + gradient-rainbow**

---

## C. Typography (7 branches)

### C1. display_font
見出し用。
- 候補: `Geist` / `Satoshi` / `Cabinet Grotesk` / `Inter` / `Outfit` / `Fraunces`(serif) / `Instrument Serif`
- **default: Geist**(2026 年で最も汎用、Inter よりキャラ立つ)
- ban 推奨: `Inter`(generic SaaS 感)

### C2. body_font
本文用。
- display と同じ or 別フォント
- **default: display と同じ**(2 font 戦略を取りたい時のみ別指定)

### C3. mono_font
コード / 数字。
- `Geist Mono` / `JetBrains Mono` / `IBM Plex Mono` / `Berkeley Mono`
- **default: Geist Mono**(display と統一感)

### C4. type_scale
- `1.2`(minor third、密) / `1.25`(major third) / `1.333`(perfect fourth、定番) / `1.5`(perfect fifth、開く)
- **default: 1.25**

### C5. line_height_body
- `tight`(1.4) / `normal`(1.5-1.6) / `relaxed`(1.7-1.8)
- **default: relaxed (1.7)**

### C6. max_line_length
- `60ch` / `65ch` / `75ch` / `none`
- **default: 65ch**

### C7. weight_ladder
使用 weight の段数。
- `2`(regular + bold) / `3`(regular + medium + bold) / `4`(light + regular + medium + bold)
- **default: 3**

---

## D. Spacing & Layout (5 branches)

### D1. spacing_unit
- `4px`(細かい制御) / `8px`(Tailwind 標準) / `mixed`(4 + 8)
- **default: 4px base** scale で `4, 8, 12, 16, 24, 32, 48, 64, 96, 128`

### D2. grid_system
- `12-col` / `8-col` / `none`(free flow)
- **default: 12-col**

### D3. container_max_width
- `1280px` / `1440px` / `1536px` / `full`
- **default: 1280px**

### D4. gutter
- `16px` / `24px` / `32px`
- **default: 24px**

### D5. vertical_rhythm
セクション間 spacing。
- `tight`(64px) / `normal`(96px) / `generous`(160px)
- **default: normal**

---

## E. Radius / Shadow / Border (3 branches)

### E1. radius_scale
- `sharp`(0 / 2 / 4) / `moderate`(4 / 8 / 12) / `friendly`(8 / 16 / 24) / `pill-extreme`(9999)
- **default: moderate**

### E2. shadow_ladder
elevation tier 数。
- `none`(border only) / `2-tier`(sm + md) / `3-tier`(sm + md + lg) / `5-tier`(細かい階層)
- **default: 3-tier**

### E3. border_treatment
- `hairline`(1px) / `bold`(2-3px) / `mixed`
- **default: hairline**

---

## F. Components (7 branches)

### F1. button_variants
- 最小セット: `primary` / `secondary`
- 拡張: `primary` / `secondary` / `ghost` / `destructive` / `link`
- **default: 拡張セット**

### F2. form_error_pattern
- `inline-below-field`(リアルタイム) / `summary-top`(submit 時) / `both`
- **default: inline-below-field**

### F3. card_style
- `elevated`(shadow) / `outlined`(border) / `flat`(背景色のみ)
- **default: outlined**(Linear / Notion 系)

### F4. nav_pattern
- `top-bar` / `sidebar` / `hybrid` / `none`(landing only)
- **default: top-bar**

### F5. empty_state_pattern
- `illustration + copy + cta` / `icon + copy` / `text-only`
- **default: icon + copy + cta**

### F6. loading_pattern
- `skeleton`(layout 維持) / `spinner` / `progress-bar` / `hybrid`
- **default: skeleton**(層をぼかさず体感速度上がる)

### F7. feedback_pattern
- toast 位置: `top-right` / `bottom-right` / `bottom-center` / `inline`
- **default: bottom-right**

---

## G. Motion (5 branches)

### G1. duration_scale
- `instant`(100ms) / `quick`(150-200ms) / `smooth`(250-300ms) / `expressive`(400-500ms)
- **default: quick**(default 150ms / longer 250ms)

### G2. easing
- `linear` / `ease-out` / `cubic-bezier(0.4, 0, 0.2, 1)`(Material) / `spring`
- **default: cubic-bezier(0.4, 0, 0.2, 1)**

### G3. entrance_choreography
- `none` / `fade` / `slide-up` / `scale + fade`
- **default: fade + slide-up (8px)**

### G4. hover_behavior
- `color-shift-only` / `subtle-elevation` / `pronounced`
- **default: color-shift + subtle-elevation**

### G5. focus_ring
- `outline-2px-solid` / `ring-shadow`(box-shadow ring) / `underline`(text のみ)
- **default: ring-shadow**(rounded UI と相性◎)

---

## H. Anti-Patterns (2 branches)

### H1. ai_cliches_to_ban
明示禁止リスト。
- `ai-purple-neon-glow` / `gradient-rainbow-bg` / `glassmorphism-overuse` / `floating-cards-everywhere` / `emoji-in-headings`
- **default: 上 5 つ全 ban**

### H2. competitor_mimicry_to_avoid
真似したくない参照。
- ユーザーに 0-2 件聞く(例: 「`generic-bootstrap`、`shopify-app-store-feel` は避けたい」)
- **default: なし**

---

## I. Accessibility (3 branches)

### I1. contrast_target
- `WCAG AA`(4.5:1 / 3:1) / `WCAG AAA`(7:1 / 4.5:1)
- **default: AA**(AAA は editorial / 文章主体のみ)

### I2. focus_visibility
- `subtle`(色変化のみ) / `visible`(2px ring) / `prominent`(3px ring + offset)
- **default: visible**

### I3. reduced_motion
- `respect`(prefers-reduced-motion で motion を切る) / `none`
- **default: respect**(現代の baseline)

---

## J. Brand Voice (2 branches)

### J1. brand_evoke
近づけたいブランドの参照を 1-3 件。
- 例: `linear` / `notion` / `stripe` / `apple` / `vercel`
- **default: A1 で選んだ vibe_word と同じ 1 件**

### J2. brand_avoid
逆に「絶対そう見えたくない」参照を 0-2 件。
- 例: `generic-saas-bootstrap` / `crypto-bro` / `nft-glow` / `web3-rainbow`
- **default: generic-saas-bootstrap**

---

## まとめテンプレ(grill-me が最後に返す形)

```yaml
vibe_profile:
  vibe_word: <A1>
  density: <A2>
  variance: <A3>
  motion: <A4>
  mode: <B1>

selected_tokens:
  neutral_base: <B2>
  accent_hue: <B4>
  display_font: <C1>
  body_font: <C2>
  mono_font: <C3>
  type_scale: <C4>
  spacing_unit: <D1>
  radius_scale: <E1>

deltas:                # exemplar に上書きする項目
  - "<branch>: <exemplar 既定> → <user 指定>"

bans:                  # anti-pattern に追記
  - <H1 + H2 全て>

brand_voice:
  evoke: <J1 list>
  avoid: <J2 list>
```
