---
status: active
last_reviewed: 2026-04-23
---

# Create Skill Playbook

新しい skill (slash command) を `.config/claude/skills/` に追加するときの 6-step。

## 前提

- skill = skip 不能な contract。prompt より強い
- 既存 skill を必ず確認（重複禁止）: `ls .config/claude/skills/`
- 詳細原則: `.config/claude/references/skill-writing-principles.md`

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

新 skill が機能するか実測:

```bash
# 同じタスクを skill あり / なしで実行
/skill-audit my-skill   # 自動 A/B benchmark
```

- A/B delta < 0pp → skill 不要 (revert)
- A/B delta +2pp 以上 → keep
- delta 微妙 → 1 ヶ月運用後に再評価

### 6. Validate / Symlink / Commit

```bash
# symlink が切れていないか
task validate-symlinks

# settings.json には skill 登録不要（自動発見）
# だが skills/index.json を更新するスクリプトがある場合は実行

git add .config/claude/skills/my-skill/SKILL.md
git commit -m "feat(skills): add my-skill for ..."
```

## Anti-patterns

- ✗ 既存 skill と機能重複（必ず `ls skills/` 確認）
- ✗ description に Triggers / Do NOT use を書かない（routing 精度低下）
- ✗ skill を hook 化できる場合に skill にする（hook の方が強制力上）
- ✗ A/B 検証なしで採用 → CQS スコア悪化の温床

## 関連

- 原則: `.config/claude/references/skill-writing-principles.md`
- 衝突解決: `.config/claude/references/skill-conflict-resolution.md`
- 起動パターン: `.config/claude/references/skill-invocation-patterns.md`
- インベントリ: `.config/claude/references/skill-inventory.md`
