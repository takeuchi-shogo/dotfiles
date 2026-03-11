---
name: codex-memory-capture
description: Lightweight durable memory workflow for Codex. Use when a repo-specific rule repeats, a user corrects the agent, a validation nuance is discovered, or a harness-level failure should be remembered across future sessions.
---

# Codex Memory Capture

繰り返し発生する repo 固有ルールや failure を `~/.codex/memories/` に残す。

## When To Use

- 同じ friction や failure を 2 回経験した
- ユーザーが明示的に修正方針を示した
- validation / MCP / workflow の repo 固有ルールが見つかった
- 次回の session でも確実に再利用したい学びがある

## Workflow

1. 覚える価値がある stable rule か確認する。
2. category、pattern、action を短く決める。
3. `scripts/capture_memory.py` を実行する。
4. 次の session では `~/.codex/memories/dotfiles-memory.md` を確認する。

## Command

```bash
python3 .agents/skills/codex-memory-capture/scripts/capture_memory.py \
  --category validation \
  --pattern "validate-configs may skip optional tool checks" \
  --action "Treat missing optional binaries as skip, not failure" \
  --evidence ".bin/validate_configs.sh"
```

## Output

- `~/.codex/memories/dotfiles-learnings.jsonl`
- `~/.codex/memories/dotfiles-memory.md`

## Rule

- 一度しか起きていないものは記録しない。
- secret や一時的な状態は記録しない。
- 既存 entry と重複する場合は追加しない。
