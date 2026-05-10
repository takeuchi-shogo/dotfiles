# Handoff: Skill Revitalization (2026-05-09)

> **次セッション開始時**: このファイルを Read してから本文末尾の「最初に打つプロンプト」を実行

## 本日の成果 (2026-05-09)

### 確定した方針

「Claude Cowork」記事の実装を始めようとしたが、200 session 集計の結果、**全 skill のうち使われているのは 21%、71% は未使用または低使用** と判明。新機能実装より **既存 skill の revitalization (改善 → 観察 → それでも未使用なら削除)** が優先 ROI と判断。

### Commits (master ブランチ、3 件)

```
01c3165 📝 docs(cowork): claude cowork equivalents guide + daily routines spec/plan
06a9bc5 📝 docs(skills): inventory tally + revitalization plan
7a7b54d ♻️ refactor(recall): revitalize description for auto-invoke (Phase 0 spike)
```

### 集計データ (PC 全体 1972 transcripts × 172 inventory)

- **Well-used (3+ 回)**: 35 (20%) — `/commit` 146, `/absorb` 91, `/review` 86, `agent:gemini-explore` 87 等
- **Under-used (1-2 回)**: 15 — improvement candidates
- **Dead (0 回, age > 30d)**: 15 — deletion candidates
- **Recent skip (0 回, age ≤ 30d)**: 107 — 30 day hold

### Phase 0 Spike 完了

- `recall/SKILL.md` の `disable-model-invocation: true` を削除 → Claude auto-invoke 可能に
- Triggers 5 → 12 個に拡充
- `references/skill-description-template.md` に再利用テンプレート保存

**Day 0 = 2026-05-09**。観察期間 60 日、**2026-07-09** に `/recall` 利用回数を再計測。

## 必要ファイル一覧

### Commit 済み (git log で参照可能)

| パス | 内容 |
|---|---|
| `docs/research/2026-05-09-skill-inventory-vs-usage.md` | PC 全体集計 (主要) |
| `docs/research/2026-05-09-skill-usage-tally.md` | dotfiles only 集計 (補助) |
| `docs/guides/2026-05-09-claude-cowork-equivalents.md` | Cowork 相当機能の使い方ガイド |
| `docs/specs/2026-05-09-daily-knowledge-routines-design.md` | (将来 plan、保留) |
| `.config/claude/references/skill-description-template.md` | revitalization テンプレート |

### `.gitignore` で除外 (local のみ)

⚠️ **`docs/plans/` は .gitignore で除外**。次セッションでは Read tool で local file を直接読む:

| パス | 内容 |
|---|---|
| `docs/plans/2026-05-09-skill-revitalization-plan.md` | **メイン plan**、Phase 1-5 |
| `docs/plans/2026-05-09-skill-inventory-pruning-plan.md` | 旧 plan (削除中心、supersede 済み) |
| `docs/plans/2026-05-09-daily-knowledge-routines-plan.md` | Cowork 実装 plan (revitalization 後の選択肢) |

`.gitignore` の root cause 調査も明日のスコープ。

## 明日以降のスコープ

### 優先順位

1. **`.gitignore` の `docs/plans/` 除外を調査・修正** (S 規模)
   - CLAUDE.md には「`docs/plans/` に昇格」と書いてあるが除外されている
   - 過去の plan ファイル ([commit log](git log --all -- 'docs/plans/' で確認可) は commit されているはず
   - 設定誤りの可能性、修正してから plan を git add -f で commit

2. **Phase 1: 削除確定 7 件** (S 規模、Codex Review Gate 必要)
   - `claude-opus-4-5-migration` (plugin、機能消滅)
   - `codex-result-handling` (codex CLI 直接代替)
   - `requesting-code-review` (本環境 `/review` で代替)
   - `receiving-code-review` (同上)
   - `moonbit-practice`, `moonbit-js-binding` (言語使わない)
   - `gleam-practice` (同上)

3. **Phase 2: Under-used 14 件改善** (M 規模、subagent dispatch 推奨)
   - `recall` テンプレートを横展開
   - 対象: github-pr / dispatch / debate / daily-report / agent:product-reviewer / using-superpowers / dispatching-parallel-agents / research / think / digest / obsidian-knowledge / agent:ui-observer / agent:type-design-analyzer / finishing-a-development-branch
   - subagent: 1 skill = 1 subagent dispatch (TDD 不要、description rewrite のみ)

4. **Phase 3: Recent skip 中優先 50 件** (L 規模、subagent 並列)
   - GCP 13 件 (本業使用、description 改善)
   - 学習系 keep 5 件 (nix/dotenvx/devbox/justfile/conventional-changelog)
   - UI 5 件 (trigger 強化最優先 ← user 希望)
   - Obsidian 拡張 3 件 (cli → skill 移行支援)
   - その他

5. **Phase 4: 月次 tally 自動化 + AutoEvolve 統合** (M 規模)
   - `scripts/learner/skill_usage_tally.py` permanent 化
   - 月次 cron 設定

6. **Phase 5: 60 日後最終判定 (2026-07-09)** — 改善後も 0 回なら削除

## 別件 (今日触っていない、引き継ぎ事項)

```
M .config/claude/references/decision-tables-index.md
M .config/claude/settings.json (ハーネス変更、Stop hook で /review 要求済み)
?? .config/claude/references/html-artifact-recipes.md
?? .config/claude/references/output-format-decision-table.md
?? docs/research/2026-05-09-html-effectiveness-absorb-analysis.md
```

`settings.json` の harness 変更は本セッション開始前から M 状態。`/review` でハーネスレビューを通す必要あり (本日 Stop hook が要求していた)。

## 最初に打つプロンプト (コピペ可)

### オプション A: 完全引き継ぎ (推奨)

```
昨日の skill revitalization の続きを進めたい。

引き継ぎ情報:
- HANDOFF: HANDOFF-2026-05-09-skill-revitalization.md を読んで
- メイン plan: docs/plans/2026-05-09-skill-revitalization-plan.md (.gitignore で除外、local 参照)
- 集計: docs/research/2026-05-09-skill-inventory-vs-usage.md
- テンプレ: .config/claude/references/skill-description-template.md
- Phase 0 spike commit: 7a7b54d

最初に:
1. HANDOFF を読んで状況把握
2. .gitignore で docs/plans/ が除外されている問題を調査・修正提案
3. その後 Phase 1 (削除 7 件) または Phase 2 (Under-used 14 件改善) に着手

進め方は HANDOFF の「優先順位」に従って提案して。
```

### オプション B: Phase 直行 (Phase 2 から開始)

```
HANDOFF-2026-05-09-skill-revitalization.md を読んで、Phase 2 (Under-used 14 件改善) を subagent dispatch で並列実行して。
テンプレートは .config/claude/references/skill-description-template.md。
recall (commit 7a7b54d) と同じパターンで横展開。
```

### オプション C: 軽量再開 (確認のみ)

```
昨日の skill revitalization の状況を HANDOFF-2026-05-09-skill-revitalization.md で確認して、現状サマリーをくれ。
```

## 注意事項

- **master 直変** していたので、明日以降 feature ブランチに切り替え推奨
- `git config --unset-all --local core.hooksPath` で lefthook を有効化する hint が出ていた (今日は未対応)
- Codex Review Gate (`codex-reviewer + code-reviewer 並列`) は M/L 規模変更で必須

## 終了状態 (Day 0)

- skill revitalization 方針確定 ✅
- Phase 0 spike 完了 ✅
- 集計 + plan + guide commit 済み ✅
- 観察期間スタート ✅
- 明日以降の scope と引き継ぎ情報 = 本ファイル
