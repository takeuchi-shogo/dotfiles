# HANDOFF: γ-3 Skill Pruning Phase 1

**Date**: 2026-05-20
**Origin session**: e01a786e-3e52-4191-aceb-0de0395d2b68
**Recipient**: 新 worktree session (`feat-skill-pruning-phase1` 推奨)

## このタスクが分離された理由

`σ=2` (全部実行) の指示で ε/γ-4/γ-2/γ-1 を本 session で完了。γ-3 のみ M-L (35-task plan、DEAD 15 件削除目標、token tax -12% 削減目標) で context 圧迫リスクが高いため worktree に分離。

## このセッションで完了済 (master 直)

| 項目 | 結果 | 変更ファイル |
|---|---|---|
| **ε** MEMORY.md 整理 | 39.8KB → 約 19KB (limit 24.4KB 以下) | `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md` |
| **γ-4** docs drift | /improve mermaid ノード削除 + nix/README.md Phase 0+A 古記述更新 | `.config/claude/README.md` (L382/396/402 削除), `nix/README.md` (L1/L7 更新) |
| **γ-2** hard-coded paths | 5/6 修正 (scripts/security/ は permission denied で skip) | `scripts/runtime/_brevity_types.py`, `scripts/runtime/auto-morning-briefing.sh`, `.config/aerospace/aerospace.toml`, `.config/claude/skills/{think,timekeeper}/SKILL.md` |
| **γ-1 (c)** work.nix 検証 spec | 新規 112 行 spec | `docs/specs/2026-05-20-work-mac-validation.md` |
| **γ-1 (a)(b)** nix 緩和 | **Skip** | YAGNI: 個人 dotfiles の dotfiles dir 名固定 + 2 ホスト分の userName は design intent |

未 commit (master 上の working tree)。worktree 切り出しに含める/分離するかは判断。

## γ-3 タスク詳細

**Plan**: `docs/plans/2026-05-09-skill-inventory-pruning-plan.md` (335 行、35 task)

**Goal**: PC 全体 1972 transcripts ベース集計の **使用率 29% / 未使用 71%** を改善
- DEAD skill 15 件削除 → token tax -12% 目標
- Recent skip の前倒し評価
- Under-used skill の description / trigger 改善
- AutoEvolve 統合で usage promotion

**Constraints**:
- Harness Stability: skill/agent 削除は **3 file/cycle** 上限 (`references/harness-stability.md`)
- DEAD 判定は **30 日評価後** が原則
- Pruning-First (`references/improve-policy.md`)

## 別 session 起動手順

```bash
# 経路 C 推奨 (Issue #48 wt-new)
wt-new feat-skill-pruning-phase1

# 起動後 (新 worktree 内で)
cd ~/dotfiles/.claude/worktrees/feat-skill-pruning-phase1
claude
```

新 session 初手 prompt:
```
γ-3 (skill pruning Phase 1) を実行。HANDOFF-2026-05-20-gamma3-skill-pruning.md と docs/plans/2026-05-09-skill-inventory-pruning-plan.md を読んで、Phase 1 (DEAD 削除 15 件) から着手。1 cycle = 3 file 上限の harness-stability rule に従う。
```

## verify 用 baseline コマンド (新 session 開始時)

```bash
# 現在の skill 総数
ls ~/.claude/skills/ | wc -l           # APM 経由
find ~/.claude/skills -name "SKILL.md" -depth 2 | wc -l

# 最新 usage stats (もしあれば)
cat ~/.claude/scripts/runtime/skill-usage-*.log 2>/dev/null | tail -50

# Plan の Phase 1 進捗 marker
grep -E "^\s*- \[" docs/plans/2026-05-09-skill-inventory-pruning-plan.md | head -20
```

## 関連メモリ

- [MEMORY.md L41-43](../../.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md): AutoEvolve 4 層ループ
- [MEMORY.md L121]: 73% Overhead 9 Patterns — Pattern 5 (107 skill 12,283 token tax) Gap 確定
- 既存 skill pruning HANDOFF (参考): `HANDOFF-2026-05-09-skill-revitalization.md`, `HANDOFF-2026-05-11-skill-revitalization.md`

## 注意

- 本 session の未 commit 変更を merge してから worktree 切り出すと clean な base になる。あるいは master commit 後に worktree を rebase。
- γ-2 で skip した `scripts/security/scan-jsonl-secrets.py:143` は permission scope 拡張 (settings.local.json の permissions) が必要。worktree session で対応するか別 task として残す。
- 本 HANDOFF 自体は γ-3 着手時点で `completed/` に move して構わない。
