---
source: "Article: Slava Zhenylenko (Augment), \"A good AGENTS.md is a model upgrade\""
analysis: "docs/research/2026-04-23-agents-md-patterns-absorb-analysis.md"
date: 2026-04-23
status: active
size: L
success_criteria:
  - "docs/research/, docs/plans/, .config/claude/references/ の全 .md に `status: active|reference|archive` frontmatter が付与される"
  - "`AGENTS.md` / `.codex/AGENTS.md` が 120-130 行の範囲に収まる"
  - "CLAUDE.md core_principles セクションの警告系が全て「do 対」で記述される"
  - "新 pattern 導入時の stale doc retirement 手順が playbook 化されている"
  - "AGENTS.md / CLAUDE.md / references のサイズが hook で計測・警告される"
  - "hook 追加 / skill 作成 / agent 追加 の numbered 6-step workflow playbook が存在する"
  - "散在する decision tables が `decision-tables-index.md` から一覧できる"
---

# AGENTS.md patterns absorb 統合プラン

## Goal

Augment の AuggieBench 実測に基づく AGENTS.md ベストプラクティスを、dotfiles の **harness engineering 文脈に翻訳** して取り込む。

**Codex 最優先指摘:**
- **search-result sprawl の境界設定** と **root AGENTS.md 圧縮** から着手
- module-level AGENTS.md 増設（逆効果）は棄却

**棄却した項目:**
- module-level AGENTS.md の増設（単一ファイル前提 vs. dotfiles harness の文脈差）
- 13-stage deploy workflow の機械的コピー（原理のみ採用）
- Skills/slash commands を don't+do の代替として再設計（既に実装済み）

---

## Task Breakdown

### Task 1 (P1, L): Search-result sprawl 監査

**Why**: Codex 最優先指摘。dotfiles は 478 md / 4.6MB で Augment 記事の「226 docs / 2MB で崩壊」レンジに到達。AGENTS.md 直接 auto-load ではないが、grep/semantic search で拾われる（~50%）。active/reference/archive 境界と検索除外・索引が本丸。

**Steps**:
1. Schema 策定: `status: active | reference | archive` frontmatter + `last_reviewed` date
2. `.config/claude/references/doc-status-schema.md` を新規作成（schema 定義）
3. `scripts/lifecycle/doc-status-audit.py` を新規作成:
   - docs/research/, docs/plans/, .config/claude/references/ を走査
   - frontmatter 未設定を検出 → stdout にレポート
   - `--fix` オプションで最終更新日を基に初期値を推定 (active if <90 days, reference if cited in CLAUDE.md/MEMORY.md, else archive)
4. バッチ実行: 全ファイルに frontmatter を付与（手動レビュー or --fix）
5. `docs/research/_index.md` と `docs/plans/_index.md` (新規) に status 列を追加
6. PostToolUse hook: Grep/Glob 結果に archive ドキュメントが含まれたら suppress 推奨を出す
7. `.claudeignore` 候補: `docs/plans/archive/`, `docs/research/archive/` の除外検討

**Files affected**:
- new: `.config/claude/references/doc-status-schema.md`
- new: `scripts/lifecycle/doc-status-audit.py`
- new: `docs/plans/_index.md`
- modified: `docs/research/_index.md`, 約 500 .md files (frontmatter only)
- modified: `.config/claude/settings.json` (PostToolUse hook)

---

### Task 2 (P1, M): root AGENTS.md / .codex/AGENTS.md 圧縮

**Why**: Codex 指摘。現状 149行 / 151行で記事推奨 100-150 行の上限ぎりぎり/超過。Mandatory Skill Usage と Change Surface Matrix が重複。

**Steps**:
1. `AGENTS.md` を精査し、references/ に退避可能な部分を特定
2. 重複セクション（Mandatory Skill Usage / Change Surface Matrix）を `references/` に整理
3. `AGENTS.md` を 120-130 行に圧縮、references へのリンクに置換
4. `.codex/AGENTS.md` も同様に 120-130 行に圧縮
5. 直接参照を 10-15 個に収める

**Files**:
- modified: `AGENTS.md`
- modified: `.codex/AGENTS.md`
- possibly new: `references/mandatory-skill-usage.md` (if not already exists)

---

### Task 3 (P2, S): Pair don't with do 強化

**Why**: Codex 指摘。root CLAUDE.md の "No features/abstractions/Don't refactor" は do が抽象的。30-50 の極端ではないが萎縮リスク。

**Steps**:
1. `/Users/takeuchishougo/dotfiles/CLAUDE.md` の "2. Simplicity First" / "3. Surgical Changes" セクションを精査
2. 各 "No X" / "Don't Y" に concrete do を対で追加
3. rules/ 全般も軽く見直し（react.md は既に ❌/✅ あり、模範）

**Files**:
- modified: `CLAUDE.md` (project-level)
- possibly modified: `.config/claude/rules/*.md` (spot check)

---

### Task 4 (P2, S): Stale doc retirement playbook

**Why**: Codex oversight。新 pattern 導入時に旧 doc を archive/削除する手順がない。Build to Delete 原則の実装。

**Steps**:
1. `docs/playbooks/stale-doc-retirement.md` を作成
2. 手順: (a) 新 pattern 発表時に grep で旧 pattern 記述を発見 (b) status: archive に変更 (c) 置き換えポインタを先頭に追記 (d) 一定期間後に削除判定
3. `references/improve-policy.md` の Pruning-First 運用と連携

**Files**:
- new: `docs/playbooks/stale-doc-retirement.md`

---

### Task 5 (P3, S): Token-based size limit

**Why**: Gemini 補完。>4KB / 4000 tokens で Lost in the Middle。「100-150 行」より token が実態。

**Steps**:
1. `docs/adr/0007-thin-claudemd-thick-rules.md` に追記:
   - CLAUDE.md ≤ 4KB (推奨 3KB)
   - AGENTS.md ≤ 4KB
   - references/ 単独 ≤ 8KB
   - 超過時は分割を検討
2. `scripts/policy/claudemd-size-check.py` を新規作成（既存の類似 hook があれば拡張）:
   - Write/Edit 時に CLAUDE.md / AGENTS.md / references/*.md を計測
   - 超過で warning（hard block ではない）
3. `.config/claude/settings.json` に PostToolUse hook 登録

**Files**:
- modified: `docs/adr/0007-thin-claudemd-thick-rules.md`
- new: `scripts/policy/claudemd-size-check.py`
- modified: `.config/claude/settings.json`

---

### Task 6 (P3, M): Workflow playbooks

**Why**: Augment 記事の「6-step deploy workflow」で correctness +25% / completeness +20%。dotfiles で頻出タスクにこのパターンを適用。

**Steps**:
1. `docs/playbooks/add-hook.md` — PreToolUse / PostToolUse hook の numbered 6-step (settings.json 編集 → script 作成 → 正規表現テスト → ログ確認 → rollback 条件 → commit)
2. `docs/playbooks/create-skill.md` — skill 新規作成の 6-step
3. `docs/playbooks/add-agent.md` — subagent 新規作成の 6-step

**Files**:
- new: `docs/playbooks/add-hook.md`
- new: `docs/playbooks/create-skill.md`
- new: `docs/playbooks/add-agent.md`

---

### Task 7 (P3, S): Decision-tables index

**Why**: Codex 指摘。decision tables が分散。記事の 25% best_practices 効果を最大化するには索引が必要。

**Steps**:
1. `.config/claude/references/decision-tables-index.md` を新規作成
2. 既存の決定表をリスト化:
   - model-routing.md
   - cwd-routing-matrix.md
   - change-surface-matrix.md
   - CLAUDE.md の S/M/L workflow
   - hook vs instruction (determinism_boundary)
   - /epd vs /rpi (skill description 群)
3. CLAUDE.md から 1 link で参照できるようにする

**Files**:
- new: `.config/claude/references/decision-tables-index.md`
- modified: `AGENTS.md` (1 link 追加、Task 2 と調整)

---

## Dependency Graph

```
Task 1 (sprawl 監査)  ─┐
                        ├→ Task 4 (retirement playbook)
Task 2 (AGENTS 圧縮)  ─┼→ Task 5 (size limit ADR)
                        ├→ Task 7 (decision tables index)
Task 3 (don't/do) ─── 独立
Task 6 (workflow playbooks) ─── 独立
```

---

## Rollout Strategy

- **Phase A (Week 1)**: Task 1 + Task 2 (P1 並列実行、最大効果)
- **Phase B (Week 2)**: Task 3 + Task 4 + Task 7
- **Phase C (Week 3)**: Task 5 + Task 6

各 Phase 完了時に: `task validate-configs && task validate-symlinks` で harness の整合性確認。

## Rollback

- Task 1: frontmatter 削除で原状復帰。script と hook は remove で OK
- Task 2: git revert で AGENTS.md 復元
- Task 5: hook を settings.json から外せば無効化
- その他: 新規ファイルの削除で rollback

---

## Pre-mortem (失敗モード)

1. **frontmatter 付与で 500 files 変更 → commit diff 爆発**: `--fix` モードは段階的に (研究領域ごと) コミットする
2. **archive 判定の誤爆**: 90 日経過でも load-bearing な reference がある。手動レビュー必須、`--fix` は提案のみ
3. **hook で Grep が使いにくくなる**: suppress 推奨は soft warning のみ、hard block しない
4. **AGENTS.md 圧縮で重要な情報欠落**: references への link 切れを `scripts/policy/validate-refs.py` (仮) で検証
5. **size check hook の誤警告**: token 計算の精度。最初は文字数 proxy で運用し、実測後に tiktoken 化検討

---

## Reversible Decisions

- **status schema の具体値**: active/reference/archive 以外に draft/deprecated を入れるかは運用後 1 ヶ月で再検討
- **archive 閾値 90 日**: アクセスパターンを見て調整
- **AGENTS.md 上限 125 行**: Augment は 100-150 推奨、dotfiles の実情で再調整

---

## Chaining

- 実行: `/rpi docs/plans/active/2026-04-23-agents-md-absorb-plan.md`
- または Phase A から段階実行: まず Task 1 + Task 2 を新セッションで

## Notes

- Augment の single-file AGENTS.md 前提と dotfiles の harness engineering 文脈は異なる。本プランは記事の **原理** を翻訳したもので、機械的翻訳ではない
- Skills/slash commands を "don't + do" の強化版として扱う Gemini 観点は既に dotfiles で実装済み（skill 自体が skip 不能な contract）
