---
status: reference
last_reviewed: 2026-05-09
---

# Output Format Decision Table

「この出力は markdown / HTML / Mermaid 埋込 / playground / excalidraw のどれで作るべきか」を 1 表で決める。

「HTML をデフォルトにすべき」という主張 (Thariq Shihipar "The Unreasonable Effectiveness of HTML", 2026-05) を absorb した結果、当 dotfiles では **markdown を引き続き default**、HTML は限定条件下で採用と判定。本表はその選択基準。

## 主表: シナリオ別の推奨フォーマット

| シナリオ | 推奨 | 第二候補 | 理由 |
|---------|------|---------|------|
| spec / plan / research レポート (`docs/specs/`, `docs/plans/`, `docs/research/`) | **markdown** | Mermaid 埋込 | search/grep, vector index, version control, agent re-ingest 効率 |
| 後続 agent が ingest する artifact | **markdown 必須** | (HTML 禁止) | HTML タグで token 1.3-1.8x、embedding 汚染 |
| GitHub PR description / review comment | **markdown** | (HTML 不採用) | GitHub native render、`difit --comment` 統合 |
| design system reference (`ui-ux-pro-max` の MASTER.md) | **markdown** | (HTML 不採用) | version control + memory 連携 |
| 探索的に複数 design / option を比較 | **playground (HTML)** | markdown grid | live preview、双方向性、copy-as-prompt |
| feature flag / config 編集 UI | **playground (HTML)** | markdown table | drag-drop、prerequisite warning、copy diff |
| 単体の diagram (system flow / state / sequence) | **Mermaid 埋込 markdown** | excalidraw JSON | markdown grep 互換、GitHub render |
| 編集可能性が必要な diagram | **excalidraw skill** | (HTML 不採用) | Obsidian 編集互換、JSON pure |
| live data dashboard / interactive 解析 | **playground (HTML)** | (markdown 不可) | live preview 必須 |
| 1 度しか作らない throwaway visualization | **playground (HTML)** | markdown grid | 双方向性が本質、再 ingest 不要 |

## HTML を選ぶ条件 (記事の利点)

以下を **すべて** 満たす場合のみ HTML 単独ファイル出力を採用:

1. **情報密度が markdown では足りない** — グリッド比較、SVG illustration、interactive control が本質
2. **throwaway** — 1 度作って捨てる、または GitHub Pages で公開する artifact
3. **読み手は人間のみ** — 後続 agent が ingest しない
4. **双方向性が必須** — sliders / drag-drop / live preview / copy-as-prompt button

該当する場合は `playground` skill (既存 6 templates) または `frontend-design` skill を使う。

## HTML を避ける条件 (Codex + Gemini 批評)

以下のいずれかに該当する場合は markdown を選ぶ:

1. **後続 agent re-ingest**: HTML タグで token 1.3-1.8x、`<div>` spam で embedding 汚染
2. **version control diff**: HTML diff は noisy (著者も認める downside)
3. **search/grep 互換性**: HTML タグでパターンマッチ崩れ、ripgrep 不適
4. **security**: subagent が読む環境では XSS/onerror injection リスク
5. **accessibility**: agent 生成 HTML は非セマンティック (`<div>` spam) → screen reader は markdown より悪化
6. **生成時間**: markdown の 2-4x (著者自認の cost)
7. **個人 dotfiles 文脈**: 「colleague と share する」前提が当てはまらず share 価値が小さい
8. **Pruning-First**: 既存 markdown infrastructure (130+ research files, decision tables, MEMORY) を流用する方が安い

## 中間策: Mermaid embedded markdown

記事の「HTML で diagram 描く」利点の多くは Mermaid 埋込 markdown で代替可能 (Gemini 推奨):

- system flow / sequence / state / class / ER diagram → ` ```mermaid ` ブロック
- table data → markdown table
- 真の interactive 要素 (slider/drag) のみ → playground 単独で

GitHub / VSCode / Obsidian 全てが Mermaid native render をサポート。

## 関連 reference

- [`html-artifact-recipes.md`](html-artifact-recipes.md) — 記事の use case のうち playground 既存 6 templates でカバー外の 2 recipe
- [`decision-tables-index.md`](decision-tables-index.md) — 全決定表の索引
- `playground` skill — 6 templates (design / data-explorer / concept-map / document-critique / diff-review / code-map)
- `excalidraw` skill — diagram → JSON
- `frontend-design` skill — UI artifact 用 HTML/CSS/JS 生成

## 出典

- 記事: Thariq Shihipar "Using Claude Code: The Unreasonable Effectiveness of HTML" (2026-05, GitHub Pages)
- 批評統合: [`docs/research/2026-05-09-html-effectiveness-absorb-analysis.md`](../../../docs/research/2026-05-09-html-effectiveness-absorb-analysis.md)
- 主要批評根拠:
  - **Codex**: "HTML maximalism は helpful バイアス取り込みすぎ" — 個人 dotfiles と組織 share の文脈差を指摘
  - **Gemini**: Anthropic 公式 Skills (google/skills, mizchi/skills) は全 markdown ベース。HTML maximalism は組織標準ではない
