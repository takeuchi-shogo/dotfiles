---
status: reference
last_reviewed: 2026-05-09
---

# HTML Artifact Recipes

`playground` skill の既存 6 templates でカバーされる範囲と、記事 "The Unreasonable Effectiveness of HTML" (Thariq Shihipar, 2026-05) で言及された use case のうち **既存テンプレート外の 2 recipe** をまとめる。

選択基準は [`output-format-decision-table.md`](output-format-decision-table.md) を参照。HTML を採用する条件 (4 つすべて満たす) を確認してから本書を使うこと。

## 既存 playground templates (該当する use case はそのまま使う)

| Template | カバーする use case |
|----------|-------------------|
| `design-playground` | visual design (color, typography, spacing, component variants) |
| `data-explorer` | SQL / API / pipeline / regex / **prompt tuner with variable slots** |
| `concept-map` | learning, knowledge gaps, scope mapping |
| `document-critique` | document review (approve / reject / comment) / **annotation export** |
| `diff-review` | PR / git diff line-by-line commenting |
| `code-map` | codebase architecture (component graph, data flow, layers) |

記事の例のうち以下は既存 templates でカバー済み:
- "side-by-side prompt editor with variable slots highlighted, live render" → **`data-explorer`**
- "annotation export buttons, approve/reject rows" → **`document-critique`**

## Gap recipes (既存 templates 外)

### R1: Priority triage (drag-drop columns)

**Use case**: Linear ticket / TODO / 30+ items を Now / Next / Later / Cut 列にドラッグ振り分けして markdown export

**Prompt example**:
> Make me an HTML file with each item as a draggable card across Now / Next / Later / Cut columns. Pre-sort by your best guess. Add a "copy as markdown" button that exports the final ordering with a one-line rationale per bucket.

**Closest template**: `document-critique` (cards UI を流用) または `concept-map` (column 構造を流用)。完全一致なし

**実装スケルトン**:
```html
<!-- 4 columns × draggable cards × HTML5 drag-drop API × copy-as-markdown -->
<div class="board">
  <div class="col" data-bucket="now">...</div>
  <div class="col" data-bucket="next">...</div>
  <div class="col" data-bucket="later">...</div>
  <div class="col" data-bucket="cut">...</div>
</div>
<button id="copy-md">Copy as markdown</button>
```
出力テンプレ: `## Now\n- card1 — rationale\n## Next\n- card2 — rationale ...`

### R2: Config editor with dependencies

**Use case**: feature flag / env var / YAML config の structured 編集。前提条件チェック付き

**Prompt example**:
> Build a form-based editor for our config. Group flags by area, show dependencies between them, warn me if I enable a flag whose prerequisite is off. Add a "copy diff" button that gives me just the changed keys.

**Closest template**: `data-explorer` の form variant。完全一致なし

**実装スケルトン**:
```html
<!-- form-based editor × dependency graph × diff-only export -->
<form id="config">
  <fieldset data-area="auth">
    <input name="enable_oauth" type="checkbox" data-requires="enable_users"/>
  </fieldset>
</form>
<div id="warnings"></div>
<button id="copy-diff">Copy diff</button>
```
warning logic: `data-requires` chain を traverse、prereq が off なら赤表示。

## アンチパターン

以下は HTML artifact を作るべきでない:

- 仕様書 / spec を HTML で書く → markdown (`docs/specs/`)
- code review / PR を HTML で書く → markdown + `difit --comment`
- design system reference を HTML で persist → `ui-ux-pro-max` の MASTER.md
- diagram 1 つだけ欲しい → Mermaid 埋込 markdown または `excalidraw` skill
- 後続 agent (subagent / vector index) が読む artifact → markdown

詳細: [`output-format-decision-table.md`](output-format-decision-table.md)

## 出典

- 記事: Thariq Shihipar "Using Claude Code: The Unreasonable Effectiveness of HTML" (2026-05)
- 批評統合: [`docs/research/2026-05-09-html-effectiveness-absorb-analysis.md`](../../../docs/research/2026-05-09-html-effectiveness-absorb-analysis.md)
