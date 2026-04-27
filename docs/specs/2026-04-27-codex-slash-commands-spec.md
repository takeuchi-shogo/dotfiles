# Spec: Codex Slash Commands Parity

**Date**: 2026-04-27
**Source**: [absorb analysis](../research/2026-04-27-codex-claude-parity-absorb-analysis.md)
**Status**: deferred
**Workflow**: spec → /epd or /spike (別セッション推奨)

## Context

Claude Code は user-defined スラッシュコマンドを `~/.config/claude/commands/*.md` で配備可能 (32 件 in this user's setup)。Codex CLI は **ユーザー定義スラッシュコマンド機能が公式に存在しない** (公式 docs 確認、2026-04-27)。組み込みコマンドのみ:
- `/model`, `/fast`, `/permissions`, `/personality`, `/plan`, `/status`, `/diff` 等

## Existing Parity (Already)

Claude commands の多くは **Codex で skill として並存**:

| Claude command | Codex 側並存 | 状態 |
|----------------|------------|------|
| `/commit` | `commit` skill | ✅ Already |
| `/spec` | `spec` skill | ✅ Already |
| `/spike` | `spike` skill | ✅ Already |
| `/validate` | `validate` skill | ✅ Already |
| `/review` | `review` skill (plugin 経由) | ✅ Already |
| `/checkpoint` | `codex-checkpoint-resume` skill | ✅ Already |
| `/research` | `research` skill | ✅ Already |
| `/security-review` | `security-review` skill | ✅ Already |
| `/security-scan` | `security-scan` skill | ✅ Already |
| `/absorb` | `absorb` skill | ✅ Already |
| `/recall` | `recall` skill | ✅ Already |
| `/timekeeper` | `timekeeper` skill | ✅ Already |
| `/onboarding` | `onboarding` skill | ✅ Already |
| `/eureka` | `eureka` skill | ✅ Already |
| `/challenge` | `challenge` skill | ✅ Already |
| `/fix-issue` | `fix-issue` skill | ✅ Already |
| `/feature-tracker` | `feature-tracker` skill | ✅ Already |

## True Gaps

| Claude command | Codex 並存 | 候補化判断 |
|----------------|------------|-----------|
| `/rpi` (Research → Plan → Implement) | なし | **skill 化候補** (要評価) |
| `/improve` (AutoEvolve cycle) | なし | **skill 化候補** (要評価) |
| `/quiz` (self-assessment) | なし | 価値低 (skip) |
| `/output-mode` | なし | Codex は `personality` で代替 (Already) |
| `/persona` | `personality` 設定で代替 | Already |
| `/profile-drip` | なし | 価値低 (skip) |
| `/note` | `obsidian` skill 群で代替 | Already |
| `/init-project` | なし | 価値中 (skill 化候補) |
| `/check-context` | なし | 価値中 (skill 化候補) |
| `/memory-status` | なし | 価値中 (skill 化候補) |
| `/interview` | `interview` skill (plugin) | Already |
| `/analyze-tacit-knowledge` | なし | 価値低 (skip) |
| `/autonomous` | なし | 価値中 (要 user 判断) |
| `/implement-loop` | `ralph-loop` plugin で代替 | Already |
| `/review-loop` | `ralph-loop` plugin で代替 | Already |

## Spec

### Goal
Claude commands で **Codex に並存しない** ものを skill として配備する。

### Acceptance Criteria
1. `/rpi`, `/improve`, `/init-project`, `/check-context`, `/memory-status` の 5 件を Codex skill として配備
2. 各 skill は Codex の `developer_instructions` 規約に従う
3. natural-language trigger に対応 (e.g., "rpi で実装" / "改善サイクル走らせて")
4. 既存 Codex skill との重複なし

### Scope
- IN: 上記 5 skill の配備
- IN: AGENTS.md の Mandatory Skill Usage への追加
- OUT: 価値低判定された 5 件 (quiz / persona / profile-drip / analyze-tacit-knowledge / autonomous)
- OUT: Already 判定された 17 件
- OUT: ralph-loop / obsidian など plugin 経由の代替

### Risks
- 既存 Claude command と同名で配備すると、Claude/Codex 間で挙動差異 → skill name に suffix を付けて区別 (例: `rpi-codex`)
- 5 件のうち実利用されないものがある → user に "実装前 gate" で確認

## Implementation Sketch

```bash
# Phase 1: skill scaffolding
mkdir -p ~/dotfiles/.codex/skills/{rpi,improve,init-project,check-context,memory-status}

# Phase 2: SKILL.md 作成 (Claude commands を Codex 規約に変換)
# - frontmatter: name, description, triggers, do-not-use-for
# - body: Claude tool 呼び出し (Skill, Agent) → Codex 表現
# - 既存 codex-* skills を template として使う

# Phase 3: symlink to ~/.codex/skills/
ln -s ~/dotfiles/.codex/skills/rpi ~/.codex/skills/rpi
# ... (各 skill)

# Phase 4: 検証
codex exec --skip-git-repo-check -p fast 'rpi の概要を教えて'
```

## Recommended Workflow

1. 別セッションで `/spike` を起動
2. `rpi` skill を最初に prototype (最も価値が高い)
3. 動作確認後、残り 4 件を順次配備
4. 全配備後、`/validate` で acceptance criteria を確認
