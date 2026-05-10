---
source: "https://github.com/forrestchang/andrej-karpathy-skills/tree/main"
analysis: "docs/research/2026-04-20-karpathy-skills-absorb-analysis.md"
date: 2026-04-20
status: active
size: M
success_criteria:
  - "CURSOR.md 内の broken link (.cursor/rules/karpathy-guidelines.mdc, skills/karpathy-guidelines/SKILL.md) が解消され、task validate-readmes が pass する"
  - "PLANS.md Required Sections に Success Criteria が追加され、completion-gate.py が読む frontmatter `success_criteria:` と形式整合する"
  - "AGENTS.md (root) と .codex/AGENTS.md に Karpathy 4 原則へのポインタが追加される (本体複製はしない)"
  - ".cursor/rules/global.mdc に Karpathy 4 原則簡潔版が Core Principles 下に追記される"
  - "docs/adr/0006-hook-philosophy.md が作成され、3 分類 (block / advisory / human judgment) で既存 hook を整理する"
  - "task validate-configs と task validate-symlinks が pass する"
---

# Karpathy Skills absorb 統合プラン

## Goal

Karpathy 4 原則 (Think Before Coding / Simplicity First / Surgical Changes /
Goal-Driven Execution) の実効性を高めるため、

1. 配布 contract (CURSOR.md の broken link) を修正し、
2. PLANS.md ↔ `completion-gate.py` の success_criteria 接続を閉じ、
3. Codex / Cursor 側にも 4 原則を配布し、
4. Hook 採用判断の哲学を ADR で成文化する。

原則本体の定義は既に `dotfiles/CLAUDE.md` に存在するため、
**複製せずポインタで配布する**方針 (Surgical Changes)。

## Scope

### 触るファイル

- `CURSOR.md` — broken link を撤去し、global.mdc + CLAUDE.md への参照に書き換え
- `.cursor/rules/global.mdc` — Core Principles 直下に Karpathy 4 原則簡潔版を追記
- `PLANS.md` — Required Sections に `## Success Criteria` を Goal 直後に挿入。Working Rules に frontmatter 記法注記
- `AGENTS.md` (root) — Workflow に「Karpathy 4 原則は `CLAUDE.md` 参照」ポインタ追加
- `.codex/AGENTS.md` — Core Workflow に同様のポインタ追加
- `docs/adr/0006-hook-philosophy.md` — 新規作成
- `docs/adr/README.md` — ADR 一覧に 0006 を追記

### 触らないファイル

- `dotfiles/CLAUDE.md` — 4 原則本体は既に存在、変更不要 (Surgical Changes)
- 既存 hook スクリプト (`protect-linter-config.py`, `change-surface-advisor.py`, `completion-gate.py` 等) — ADR で哲学を書くだけ、挙動は変えない
- 既存 skill 本体 (/epd, /simplify, /verification-before-completion 等) — 変更なし
- `.config/claude/CLAUDE.md` — 既存 `core_principles` は温存

## Constraints

### 壊してはいけない挙動

- 既存 hook の動作 (`protect-linter-config.py`, `change-surface-advisor.py`, `completion-gate.py` 等) は全て無変更
- 既存の PLANS.md ベースの plan ファイル群は、Success Criteria 未記載でも validation 失敗にしない (新規 plan にのみ soft enforcement)

### 互換性・承認条件

- Karpathy 哲学: **Hard enforcement NG**。新規 hook を増やさない
- ADR 0006 は「既存 hook 3 分類を後付けで整理」する役割のみ。新規 hook 提案は別 ADR で行う
- Plan の Success Criteria 追加は **Required だが、文面形式は自由** (checklist / 箇条書き / 散文いずれも可)

### その他

- frontmatter `success_criteria:` の YAML 形式は `completion-gate.py:330-343` の parser に合わせる (list of strings)
- ADR 形式は既存 `docs/adr/0001-0005` と整合させる

## Validation

### 自動検証

- `task validate-configs` — dotfiles 設定構文チェック
- `task validate-readmes` — ローカルリンク検証 (CURSOR.md の broken link 解消を確認)
- `task validate-symlinks` — symlink 整合性
- (ADR 関連) `docs/adr/README.md` のリンク切れなし

### 手動検証

- PLANS.md 編集後: `completion-gate.py:330-343` を再読し、frontmatter 抽出と `success_criteria:` 形式が一致するか確認
- ADR 0006 作成後: 既存 ADR 0001-0005 と見出し構成・トーンが揃っているか確認
- 配布整合: `dotfiles/CLAUDE.md` の 4 原則と、新規追加する簡潔版 / ポインタに矛盾がないか確認
- 日本語で読み直し、意味が通るか確認

## Steps

### Task A — CURSOR.md 配布 contract 修正 (15 分)

1. `.cursor/rules/global.mdc` の Core Principles 直下に Karpathy 4 原則の簡潔版を追記
   (既存 KISS/YAGNI/DRY/最小インパクト/search-first は温存)
2. `CURSOR.md` を書き直し:
   - `.cursor/rules/karpathy-guidelines.mdc` への参照を `global.mdc` + `CLAUDE.md` への参照に変更
   - `skills/karpathy-guidelines/SKILL.md` への言及を削除
3. 検証: `task validate-readmes`

### Task B — PLANS.md Success Criteria 追加 (10 分)

1. Required Sections (`PLANS.md:21-58`) の `## Goal` 直後に `## Success Criteria` を挿入
2. Working Rules に「frontmatter の `success_criteria:` は `completion-gate.py` が Ralph Loop で読む」旨を注記
3. 検証: `completion-gate.py:330-343` を再読し、YAML リスト形式との整合を確認

### Task C — Codex / Cursor 配布 (20 分)

1. `AGENTS.md` (root) の Workflow 節に「Karpathy 4 原則は `CLAUDE.md` を参照」のポインタを追加
2. `.codex/AGENTS.md` の Core Workflow に同様のポインタを追加
3. (`.cursor/rules/global.mdc` は Task A で対応済み)
4. 検証: `task validate-configs` + 日本語で読み直して意味が通るか確認

### Task D — Hook Philosophy ADR (30 分)

1. `docs/adr/0006-hook-philosophy.md` を新規作成:
   - **Context**: Karpathy "Hard enforcement NG" vs 既存 `.config/claude/CLAUDE.md:25` 「static-checkable は mechanism へ」/ `:90` 「review/gate は pass/block」の緊張
   - **Decision**: 3 分類で hook を整理
     - **Deterministic block**: 形式違反を機械的に遮断 (例: `protect-linter-config.py`)
     - **Semantic advisory**: 判断材料を提供するが block しない (例: `change-surface-advisor.py`)
     - **Human judgment**: instruction のみ、hook なし (例: Karpathy 4 原則本体)
   - **Consequences**: 将来の hook 追加時はこの 3 分類で判定。semantic judgment の deterministic 化は禁忌
   - **既存 hook の分類例**: protect-linter-config (block), change-surface-advisor (advisory), completion-gate (block、success_criteria ベース), 4 原則 (human judgment)
2. `docs/adr/README.md` の ADR 一覧に 0006 を追記
3. 検証: 既存 ADR 0001-0005 と形式整合 (見出し・トーン・フィールド)

## Progress

- [ ] Task A: CURSOR.md 配布 contract 修正
- [ ] Task B: PLANS.md Success Criteria 追加
- [ ] Task C: Codex 側 Karpathy 配布
- [ ] Task D: Hook Philosophy ADR

## Surprises & Discoveries

(実行中に記載)

## Decision Log

- **2026-04-20**: Karpathy 原則 4 本体は `dotfiles/CLAUDE.md` に既に存在するため、
  同じ内容を別ファイルに複製しない。ポインタ配布のみ (Surgical Changes 原則)
- **2026-04-20**: Hook を新規追加せず、既存 hook の分類を ADR で事後整理する方針
  (Karpathy "Hard enforcement NG" を尊重)
- **2026-04-20**: `.cursor/rules/karpathy-guidelines.mdc` は新規作成せず、
  `global.mdc` に merge する (単一ファイルで完結、Simplicity First)
- **2026-04-20**: Codex が提案した pre-commit regex enforce / post-write
  scope hook / 定量複雑度計測 / multi-model gate 全面導入 / Plan 全タスク
  mandatory 化は全て棄却。儀式化・harness debt・哲学違反の判定
- **2026-04-20**: 本プラン自身の frontmatter に `success_criteria:` を書き、
  Task B で PLANS.md に Required として昇格させる前の prefigure とする

## Outcome

(完了後に記載)
