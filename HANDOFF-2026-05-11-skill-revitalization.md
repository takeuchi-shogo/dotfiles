# Handoff: Skill Revitalization Phase 1+2 Complete (2026-05-11)

> **次セッション開始時**: このファイルを Read してから本文末尾の「最初に打つプロンプト」を実行

## 本日の成果 (2026-05-11)

11 commit pushed to master:

```
d05e720 📝 docs(plans): track docs/plans/ subdirectory plans (30 files, +7182)
0269b14 📝 docs(handoff): preserve 2026-05-09 skill revitalization handoff
07c5fd7 🔧 chore(claude): suppress auto-permission prompt UI
2c1fe25 📝 docs(absorb): integrate zodchi 15-settings showThinkingSummaries guide (2026-05-10)
3f21862 🔧 chore(absorb): integrate 12-rule CLAUDE.md silent-success audit + test intent rubric (2026-05-10)
936dbaa 📝 docs(absorb): integrate HTML effectiveness output-format guide (2026-05-09)
c34a60c ♻️ refactor(agents): revitalize 3 under-used agents (Phase 2 batch 3)
f927a34 ♻️ refactor(skills): revitalize 4 under-used skills (Phase 2 batch 2)
fa3f72e ♻️ refactor(skills): revitalize 4 under-used skills (Phase 2 batch 1)
1e6e388 🗑️ chore(skills): remove 3 unused language skills (moonbit×2, gleam)
f71d534 🔧 chore(gitignore): track docs/plans/ subdirectories
```

## 完了タスク

### Phase 1a: Local skill 削除 (3件)
- moonbit-practice / moonbit-js-binding / gleam-practice 削除
- skills-lock.json から 3 entry 削除（gitignored、local sync）
- 4 ファイルの参照 cleanup（chezmoi-management/SKILL{,-ja}.md、apm-usage/publishing.md、skill-pruning-eval-reminder.sh）

### Phase 2: Local revitalization (11件)
description 改善で auto-invoke discoverability 向上:
- **Skills (8件)**: github-pr / dispatch / debate / daily-report / research / think / digest / obsidian-knowledge
- **Agents (3件)**: product-reviewer / ui-observer / type-design-analyzer
- パターン: triggers 5-8 → 10-12 個（自然な日本語追加）、`user-invocable: true` 明示、`metadata.chain` 追加、single-line description
- **重要修正**: `daily-report` の `disable-model-invocation: true` 削除（auto-invoke 0 回の root cause）

### .gitignore 整理
- `docs/plans/*.md` のみ ignore（root の ephemeral）、subdirectories trackable に
- 43 plan files (active/completed/paused/pending) を commit、`_index.md` も追跡対象

### 引き継ぎ harness 変更コミット
- HTML effectiveness absorb (2026-05-09): output-format-decision-table.md + html-artifact-recipes.md
- 12-rule CLAUDE.md absorb (2026-05-10): silent except 修正 + test intent rubric
- zodchi 15 settings absorb (2026-05-10): debug-thinking-summary.md
- settings.json: `skipAutoPermissionPrompt: true`

## 観察期間

**Day 0 = 2026-05-09** (recall Phase 0 spike)
**再計測日 = 2026-07-09** (60 日後)
- 利用 0 回 → 真の dead → 削除候補
- 利用 1+ 回 → keep
- 利用 5+ 回 → Well-used 入り、改善成功

## 次セッションのスコープ

### 優先順位

1. **lefthook 復活** (S 規模)
   ```bash
   git config --unset-all --local core.hooksPath
   ```
   現状 `core.hooksPath` が `/Users/takeuchishougo/dotfiles/.git/hooks` を指していて lefthook が「Skipping hook sync」状態。pre-commit/commit-msg は動いているが lefthook の自動 sync が無効。

2. **Phase 1b: Plugin-managed 5 件削除判断** (M 規模) — **2026-05-13 方針確定: 全件 B (放置)**
   - 対象 (5 件): codex-result-handling / requesting-code-review / receiving-code-review / obsidian-bases / json-canvas
   - 6 件目だった `claude-opus-4-5-migration` は **既に未 install** (marketplace に source あるのみ、`installed_plugins.json` 不在、現 session の skill 一覧にも不在) → 対象外
   - 5 件の親 plugin と巻き添え:
     - `codex-result-handling` → `codex@openai-codex` (巻き添え: codex-cli-runtime / gpt-5-4-prompting / /rescue / /setup)
     - `requesting-code-review` / `receiving-code-review` → `superpowers@claude-plugins-official` 5.0.7 (巻き添え: using-superpowers, writing-plans, executing-plans, brainstorming, systematic-debugging, TDD 等常用 8 件)
     - `obsidian-bases` / `json-canvas` → `obsidian@obsidian-skills` (巻き添え: defuddle, obsidian-cli, obsidian-markdown)
   - skills-lock.json には未登録 → plugin marketplace 経由のため個別 disable 機構なし
   - 選択肢評価:
     - A: plugin 全体 uninstall → **棄却** (常用 skill の損失が削除益を大幅に上回る)
     - B: 放置 → **採用** (description tax ≈ 5×150 = 750 token/session、実害小)
     - C: marketplace を fork → **棄却** (ROI 最悪、auto-update 喪失 + メンテ負債)
   - 確定方針: B (放置)、60 日後 (2026-07-09) tally で auto-invoke 0 が続けば upstream に「skill 単位 disable 機構」を issue/PR で提案

3. **Phase 3: Recent skip 50 件改善** (L 規模、subagent 並列推奨)
   - GCP 13 件 (本業使用、description 改善で復活見込み)
   - 学習系 keep 5 件 (nix/dotenvx/devbox/justfile/conventional-changelog)
   - UI 5 件 (trigger 強化最優先 ← user 希望)
   - Obsidian 拡張 3 件 (cli → skill 移行支援)

4. **Phase 4: 月次 tally 自動化 + AutoEvolve 統合** (M 規模)
   - `scripts/learner/skill_usage_tally.py` permanent 化
   - 月次 cron 設定

5. **Phase 5: 60 日後最終判定 (2026-07-09)**

## 関連ファイル

| パス | 内容 |
|---|---|
| `docs/plans/2026-05-09-skill-revitalization-plan.md` | メイン plan、Phase 1-5 (now tracked: gitignore 修正後) |
| `docs/plans/2026-05-09-skill-inventory-pruning-plan.md` | 旧 plan (削除中心、supersede 済み) |
| `docs/research/2026-05-09-skill-inventory-vs-usage.md` | PC 全体集計 |
| `.config/claude/references/skill-description-template.md` | Phase 0 spike テンプレート |

## 注意事項

- master 直変が継続している (本日 11 commits)。次セッションは feature ブランチ推奨
- master push は未実施 (ローカルのみ)
- worktree state (`.claude/worktrees/`) は untracked のまま (commit 不要)

## 最初に打つプロンプト (コピペ可)

### オプション A: HANDOFF + lefthook 復活 + Phase 1b 判断 (推奨)

```
HANDOFF-2026-05-11-skill-revitalization.md を読んで状況把握して。

1. lefthook の core.hooksPath を unset して有効化
2. Phase 1b (plugin-managed 6 件) の方針を提案 (A/B/C)
3. user 判断後に実行
```

### オプション B: Phase 3 直行 (Recent skip 50 件改善)

```
HANDOFF-2026-05-11-skill-revitalization.md を読んで Phase 3 に着手。
GCP 13 件から始めて、subagent 並列で description 改善を進めて。
テンプレート: .config/claude/references/skill-description-template.md
```

### オプション C: 軽量再開 (確認のみ)

```
昨日の skill revitalization の状況を HANDOFF-2026-05-11-skill-revitalization.md で確認して、現状サマリーをくれ。
```

## 終了状態 (2026-05-11)

- Phase 1a (local 削除 3件) ✅
- Phase 2 (local revitalization 11件) ✅
- 引き継ぎ harness 変更 5 commit ✅
- docs/plans/ subdirectory tracking ✅
- 観察期間継続中（Day 2 / 60）
- 次セッション scope = 本ファイル

## 2026-05-13 追記

- lefthook 復活完了: `git config --unset-all --local core.hooksPath` + `lefthook install` で pre-commit/commit-msg 再 sync (lefthook 2.1.6)
- Phase 1b 確定: 全件 B (放置)、対象は 6 → 5 件に訂正 (上記 §「Phase 1b」参照)
- 次の優先: Phase 3 (Recent skip 50 件改善、GCP 13 件から)
