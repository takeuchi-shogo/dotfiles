---
source: "Using Claude Code: The Unreasonable Effectiveness of HTML (thariqs.github.io/html-effectiveness)"
author: "Thariq Shihipar (@trq212, Anthropic Claude Code team)"
date: 2026-05-09
status: analyzed
classification: partial-adopt
adopted_tasks: 2
rejected_main_claims: 5
---

## Source Summary

**主張**: Markdown より HTML を agent 出力のデフォルトにすべき。spec / plan / report / PR review / throwaway editor を HTML 化することで、情報密度・可読性・共有性・双方向性が向上する。著者は markdown を「ほぼ完全に廃止」した自称 HTML maximalist。

**手法**:
1. **情報密度の向上** — table / CSS / SVG / script / canvas / spatial layout / inline image を HTML で表現
2. **視認性・構造化** — 100 行超の markdown は読まれない、HTML はタブ・図解・mobile responsive
3. **共有・配布** — S3 upload / browser native render / permalink 共有
4. **双方向インタラクション** — sliders / drag-drop / copy-as-prompt button / config editor

**根拠**: 著者個人の経験論ベース。定量データなし。自称 HTML maximalist のバイアスが強い。

**前提条件**:
- 組織内での colleague との共有が前提 (個人 dotfiles 文脈と非整合)
- 1M context (Opus 4.7) 環境前提 (200K Sonnet 日常運用と非整合)
- 生成時間 markdown 比 2-4x を著者自身が認める
- version control での diff が noisy になると著者自認

---

## Gap Analysis (Pass 1: 存在チェック → Pass 2.5: Codex/Gemini 修正)

| # | 手法 | Phase 2 初期 | Phase 2.5 修正後 | 詳細 |
|---|------|-------------|-----------------|------|
| 1 | spec / plan / research を HTML で出力 | Gap | **Reject** | Pruning-First + token tax + Brevity Bias 警告。docs/research/ 130+ files が markdown 基盤。移行コスト大 |
| 2 | HTML 出力の frontend-design skill 活用 | Already | **Already 強化不要** | UI 用途で完成、汎用 output には不適 |
| 3 | SVG diagram 生成 | Partial | **Already** | excalidraw + Mermaid (markdown 内 GitHub native render) で十分、新規追加不要 |
| 4 | playground skill テンプレート活用 | Already | **Partial → Keep (T2)** | 既存 6 templates カバー外の 2 use case (drag-drop / config editor) が未収録 |
| 5 | PR review HTML annotation | Gap | **Reject** | `/review` の `difit --comment` で十分。GitHub PR は markdown 標準。Pages abuse risk あり |
| 6 | design system HTML reference | Partial | **Reject** | `ui-ux-pro-max` の MASTER.md で完成、二重管理になる |
| 7 | playground throwaway editor | Already | **Partial → Keep (T2)** | 記事の "ephemeral tool" 発想は有用だが既存 templates に recipe 未収録 |
| 8 | reports / research を HTML 配信 | Gap | **Reject** | docs/research/ markdown infrastructure の再発明。memory-vec / chezmoi migration tax 大 |
| 9 | ui-ux-pro-max mobile responsive | Already | **Already 強化不要** | 既存で十分 |
| 10 | HTML hosting / sharing pattern | Gap | **Reject** | 個人 dotfiles で share 価値少。S3 運用は scope 外 |
| 新 | HTML / markdown / Mermaid 選択メタ決定表 | Gap | **Keep (T1)** | 既存 skill の使い分けガイドが現状欠落。decision-tables-index 追記で完結 |

---

## Phase 2.5 セカンドオピニオン統合

### Codex 批評

> "Codex 視点では helpful バイアス警戒で、HTML 化は広げすぎ。spec/plan/research の HTML 化は後続 agent re-ingest の token tax が重く、MEMORY index 汚染も起きる。"

主要指摘:
1. **見落とし**: HTML は後続 agent の re-ingest 時に token tax (推定 1.3-1.8x) が重く、`<div>` spam で embedding 汚染が起きる
2. **過大評価**: spec/plan/research の HTML 化は、著者自己申告の HTML maximalist バイアスが強く、定量根拠なし
3. **前提の誤り**: 組織 share / 1M context 前提を、個人 dotfiles / 日常 200K 運用へそのまま移植することへの無批判な採用
4. **優先度**: PR review HTML は GitHub 添付 / Pages abuse risk まで含め低優先
5. **採用提案**: skill / reference に「HTML を使う条件 / 禁止条件」を決定表として追記 → T1 に対応

### Gemini 批評 (Google Search grounding)

> "Anthropic 公式 Skills (google/skills, mizchi/skills) はすべて markdown ベース。HTML maximalism は author 個人観察であり組織標準ではない。"

主要指摘:
1. **公式との矛盾**: Anthropic 配布 skills が全 markdown ベースという事実は記事と矛盾する
2. **実害の列挙**: Token overhead 1.3-1.8x / XSS リスク / embedding 汚染 (`<div>` spam) / accessibility 悪化 / grep 不適
3. **代替最適解**: Mermaid + Markdown で GitHub native render が実現できる
4. **棄却**: Notion / Coda (bidirectional × / version control ×) の HTML sharing pattern
5. **HTML maximalism 全面採用を推奨しない**: 決定表のみ作成で十分

両者一致: HTML maximalism 全面採用を Reject。共通推奨: 出力形式の決定表のみ作成 (T1)。

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す可能性 | 強化判定 |
|---|---|---|---|
| 2 | `frontend-design` skill | HTML を汎用 output に拡張 | **強化不要** — UI 専用で役割明確、汎用化は責務違い |
| 3 | `excalidraw` + `Mermaid` 内包 | SVG 直接生成 | **強化不要** — markdown 内 diagram で GitHub render 十分 |
| 4/7 | `playground` 6 templates | throwaway interactive tool | **Partial 採用** — 2 use case が未収録のため T2 で recipe 追加 |
| 9 | `ui-ux-pro-max` MASTER.md | mobile responsive / design system HTML | **強化不要** — 既存で完成 |

---

## Integration Decisions

### Gap / Partial → 採用

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 新 | HTML / markdown 選択メタ決定表 | **採用 (T1, S)** | 既存 skill の使い分けガイドが欠落、1 ファイル追加で完結 |
| 4/7 | playground recipes 2 件追加 | **採用 (T2, S)** | 既存 templates カバー外の 2 use case を recipe 化 |

### Gap / Partial → 棄却

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | spec / plan / research HTML 化 | **棄却** | Pruning-First、token tax、markdown 基盤流用が安い |
| 5 | PR review HTML annotation | **棄却** | difit --comment で十分、GitHub markdown 標準 |
| 6 | design system HTML reference | **棄却** | ui-ux-pro-max MASTER.md で完成、二重管理 |
| 8 | reports / research HTML 配信 | **棄却** | docs/research/ 130+ files markdown インフラ再発明 |
| 10 | HTML hosting / sharing | **棄却** | 個人 dotfiles 文脈で share 価値少、S3 scope 外 |

### Already 強化 → 不要

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 2 | frontend-design 汎用拡張 | **強化不要** | 責務違い |
| 3 | excalidraw / Mermaid 拡張 | **強化不要** | 現状で十分 |
| 9 | ui-ux-pro-max 拡張 | **強化不要** | 現状で十分 |

---

## Plan

### T1 (S): `references/output-format-decision-table.md` 新規作成

- **Files**:
  - `~/dotfiles/.config/claude/references/output-format-decision-table.md` (新規)
  - `~/dotfiles/.config/claude/references/decision-tables-index.md` (1 行追加)
- **Changes**:
  - markdown / HTML / Mermaid 埋込 / playground / excalidraw の選択基準を 1 表に統合
  - HTML を選ぶ条件 (4 つすべて満たす場合のみ): interactive element 必須 / 1M context 環境 / browser share 目的 / agent re-ingest なし
  - HTML を避ける条件 (8 項目): spec/plan/research / version control diffable 必須 / grep 対象 / memory 索引対象 / agent re-ingest あり / markdown infrastructure 既存 / 200K 環境 / 個人用途
  - decision-tables-index.md に「出力形式選択」を 1 行追加
- **Size**: S (2 ファイル)
- **検証**: `task validate-configs` 通過確認

### T2 (S): `references/html-artifact-recipes.md` 新規作成

- **Files**:
  - `~/dotfiles/.config/claude/references/html-artifact-recipes.md` (新規)
- **Changes**:
  - playground 既存 6 templates の use case 一覧表を先頭に掲載
  - 記事の use case のうち既存外 2 例を recipe 化:
    1. **Priority triage with drag-drop** (Linear ticket 風の kanban 優先度並べ替え)
    2. **Config editor with dependencies** (feature flag や環境変数の依存関係付き設定 UI)
  - T1 (`output-format-decision-table.md`) から相互参照リンク
- **Size**: S (1 ファイル)
- **検証**: playground skill を呼び出して動作確認

---

## 棄却項目 (記事の主要主張)

- HTML output 全般導入 — Pruning-First + 後続 agent re-ingest token tax (1.3-1.8x)
- spec / plan / research の HTML 化 — markdown infrastructure 流用が安い、130+ files の再発明
- PR review HTML annotation — GitHub PR workflow と非整合、difit --comment で代替
- design system HTML reference — 既存 ui-ux-pro-max MASTER.md で完成
- HTML hosting / sharing pattern — 個人 dotfiles 文脈で share 価値少

---

## 当 dotfiles 文脈での教訓

1. **著者バイアスの識別**: HTML maximalist 自己宣言は信頼性の警告信号。定量根拠なしの "unreasonable effectiveness" 見出しは誇張。
2. **公式との照合**: Anthropic 公式配布の google/skills・mizchi/skills が全 markdown ベースという事実は記事と矛盾する。公式実装を証拠として重視する。
3. **前提の文脈移植エラー**: 「colleague と share する」「1M context」前提を、個人 dotfiles / 200K Sonnet 日常運用に無批判に移植しない。
4. **Pruning-First との衝突**: HTML 大量生成は docs/research/ 130+ files の markdown infrastructure と衝突し、grep / memory-vec / chezmoi 全層で tax が増える。
5. **token tax の定量化**: Codex/Gemini 双方が 1.3-1.8x の re-ingest overhead を指摘。spec/plan を HTML 化するほど後続 agent の有効文脈が縮む。

---

## Triage 結果

User 選択: **T1 + T2** (両方採用、すべて S 規模)。

---

## Notes

- 記事の HTML maximalism 主張は個人最適化の観点であり、dotfiles engineering harness には **部分採用** に留める
- 採用 2 タスクは「判断の欠落を埋める決定表 (T1) + 既存 playground レシピ補完 (T2)」に絞る
- HTML が有効な領域 (interactive throwaway UI) は playground skill が既に担当しており、そこへの recipe 追加が最小インパクト
- 記事本文は取得経路 text-paste のため URL 正確性未検証 (thariqs.github.io/html-effectiveness)
