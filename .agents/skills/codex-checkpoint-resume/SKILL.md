---
name: codex-checkpoint-resume
description: Durable checkpoint workflow for Codex long-horizon tasks. Use before stopping unfinished work, before compaction, before handoff, or whenever a task will continue across sessions and you need a filesystem checkpoint plus a concrete resume prompt.
---

# Codex Checkpoint Resume

長時間タスクを中断する前に、再開に必要な state を filesystem に落とす。

## When To Use

- まだ終わっていない作業をここで止めるとき
- context が長くなり compact / resume を使う前
- 別 agent / 別 session へ handoff するとき
- 複数の validation や review を後続ターンへ回すとき

## Workflow

1. 今の goal、進捗、次の一手を 1-2 文でまとめる。
2. 主要な focus file と未実行コマンドを列挙する。
3. `scripts/save_checkpoint.py` を実行して `tmp/codex-state/` に保存する。
4. 次ターンでは checkpoint を読んでから再開する。

## Command

```bash
python3 .agents/skills/codex-checkpoint-resume/scripts/save_checkpoint.py \
  --goal "Codex harness improvements" \
  --summary "AGENTS and validation cleanup are done" \
  --next-step "Implement memory capture and run validation" \
  --file AGENTS.md \
  --file .bin/validate_configs.sh \
  --command "task validate-configs" \
  --command "task validate-symlinks"
```

## Output

- `tmp/codex-state/latest-checkpoint.md`
- `tmp/codex-state/checkpoints/*.md`

## Resume Rule

- 再開時は最新 checkpoint を読み、書かれている `Next Step` から始める。
- checkpoint が stale なら `git status` と diff を見て更新する。
