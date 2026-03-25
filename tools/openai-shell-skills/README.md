# OpenAI Shell Skills

OpenAI Hosted Shell / Local Shell 向けの最小 skill bundle 置き場。

## Purpose

- dotfiles 内の Codex skill をそのまま流用せず、OpenAI API へ持ち出せる最小 bundle を分離する
- first pilot 用の reproducible な skill を repo 内に残す
- `SKILL.md`、script、sample input、artifact path をまとめて管理する

## Current Bundles

- `frontend-prompt-brief/`
  - frontend prompt / implementation brief を Markdown artifact に落とす最小 bundle
  - 初回 Hosted Shell pilot の第一候補

## Validation

- `python3 tools/openai-shell-skills/frontend-prompt-brief/scripts/build_brief.py --input tools/openai-shell-skills/frontend-prompt-brief/examples/sample_input.json --output tmp/openai-shell-skills/frontend-prompt-brief.md`
- docs を更新した場合は `task validate-readmes`
