---
status: active
last_reviewed: 2026-10-19
---

# Create Skill Playbook

新しい skill (slash command) を `.config/claude/skills/` に追加するときの 6-step。

## 前提

- skill = skip 不能な contract。prompt より強い
- 既存 skill を必ず確認（重複禁止）: `ls .config/claude/skills/`
- 詳細原則: `skill-creator:skill-creator` + `.config/claude/references/skill-patterns.md` / `skill-invocation-patterns.md`
  （旧 `skill-writing-principles.md` は **2026-09-25**（+0900、commit `060fba03` / PR #259）にローカル skill-creator 退役で削除。wiki 概念記事の「2026-09-24」は日付ずれ）
- **対象外**: 個人の working-style を transcript から掘って `*-mode` skill にする流れ（pstack `/automate-me`）。流儀の正本は `CLAUDE.md` / `AGENTS.md` / memory。automate-me 本体の導入は見送り（研究メモ `docs/research/2026-10-19-pstack-formal-verification-absorb-analysis.md`）

## 6-step

### 1. Scope 判定

| Scope | 配置先 | 例 |
|---|---|---|
| project 固有 | `<repo>/.claude/skills/` | dotfiles 専用 validate |
| 汎用（全プロジェクト） | `~/.claude/skills/` (= `.config/claude/skills/`) | /commit, /review |
| Codex 兼用 | `~/.codex/skills/` + `.agents/skills/` の dual publish | $codex-* skill |

**判定基準**:
- このプロジェクトの conventions に強く依存 → project 固有
- 言語横断・他 repo でも有用 → 汎用
- Codex でも使う → dual publish

### 2. Archetype 選定

`.config/claude/references/task-archetypes/` から最も近いものを選ぶ:
- auth, db-migration, error-handling, external-api, validation 等

該当なしなら新規 archetype を `references/task-archetypes/` に追加（後続で）。

### 3. SKILL.md frontmatter 作成

```yaml
---
name: my-skill
description: |
  <1-2 行で「何をするか」+ 用途>。Triggers: 'キーワード1', 'キーワード2'.
  Do NOT use for: <反例 1>, <反例 2>.
---
```

**ベストプラクティス**:
- description は 200 文字以内（一覧で truncate される）
- Triggers と Do NOT use を必ず併記（routing 精度↑）
- 動詞 + 名詞で description（「実行する」「生成する」）
- 模倣すべき例: `/spec`, `/review`, `/absorb` の skill description

### 4. Do / Don't ペア化（本文）

`docs/playbooks/stale-doc-retirement.md` の形式に倣う:
- 各禁止事項に対応する「代わりに何をするか」を明示
- 警告だけだと over-exploration trap を招く（AGENTS.md absorb 2026-04-23 知見）

```markdown
## Anti-patterns
- ✗ X する → ✓ 代わりに Y する
- ✗ A を直に編集 → ✓ B 経由で更新
```

### 5. A/B テスト

**task skill**（再現可能な手順・判定があるもの）が機能するか実測:

```bash
# 同じタスクを skill あり / なしで実行
/skill-audit my-skill   # 自動 A/B benchmark
```

- A/B delta < 0pp → skill 不要 (revert)
- A/B delta +2pp 以上 → keep
- delta 微妙 → 1 ヶ月運用後に再評価

#### A/B の対象範囲

| 種別 | Step 5 A/B | 代わりに使うもの |
|------|------------|------------------|
| **task skill** | **必須** | skill-audit A/B（本 Step） |
| **reference skill**（手順より参照知識・方針） | 対象外 | 人間レビュー / Invert Test / 読者テスト |
| **routing skill**（起動・振り分けが本体） | 対象外 | `skill-audit` の description conflict-scan / trigger 精度 |
| **hybrid**（task + routing） | task 面のみ A/B | routing 面は conflict-scan |
| **個人 `*-mode`（working-style）** | 対象外 | **別トラック**（下記） |

**別トラック**: pstack `/automate-me` 相当の専用フロー（transcript 採掘 → 個人 `*-mode` 起草 → vibe-check）。本 repo では **見送り**。流儀の正本は `CLAUDE.md` / `AGENTS.md` / memory。create-skill の 6-step では扱わない。

### 6. Validate / Symlink / Commit

```bash
# symlink が切れていないか
task validate-symlinks

# settings.json には skill 登録不要（自動発見）
# だが skills/index.json を更新するスクリプトがある場合は実行

git add .config/claude/skills/my-skill/SKILL.md
git commit -m "feat(skills): add my-skill for ..."
```

注: 本 Step は validate / symlink / commit まで。worktree 分離や PR 作成は含まない（learned-promote / worktree playbook 側）。

## Anti-patterns

- ✗ 既存 skill と機能重複（必ず `ls skills/` 確認）
- ✗ description に Triggers / Do NOT use を書かない（routing 精度低下）
- ✗ skill を hook 化できる場合に skill にする（hook の方が強制力上）
- ✗ **task skill** を A/B 検証なしで採用 → CQS スコア悪化の温床
- ✗ reference / routing / 個人 `*-mode` に task 用 A/B を押し付ける（上表の対象外を無視）

## 関連

- 作成パイプライン: `skill-creator:skill-creator`
- パターン: `.config/claude/references/skill-patterns.md`
- 衝突解決: `.config/claude/references/skill-conflict-resolution.md`
- 起動パターン: `.config/claude/references/skill-invocation-patterns.md`
- インベントリ: `.config/claude/references/skill-inventory.md`
- 失敗→skill: `.config/claude/skills/skill-audit/references/failure-to-skill-loop.md`
