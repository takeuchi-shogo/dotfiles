# Frontend Prompt Workflow Skill

## Goal
- GPT-5.4 向け frontend prompt template を忘れず再利用できるよう、repo-local skill と公開設定を追加する
- 必要情報が足りないときに、Codex が聞き返せる workflow を skill に組み込む

## Scope
- 触るファイル:
  - `docs/plans/2026-03-22-frontend-prompt-workflow-plan.md`
  - `.agents/skills/openai-frontend-prompt-workflow/SKILL.md`
  - `.agents/skills/openai-frontend-prompt-workflow/agents/openai.yaml`
  - `.agents/skills/openai-frontend-prompt-workflow/references/templates.md`
  - `.bin/symlink.sh`
  - `AGENTS.md`
- 触らないファイル:
  - `.codex/config.toml`
  - `.codex/rules/*`
  - Claude hook / script

## Constraints
- OpenAI 公式ブログと公開 `frontend-skill` を踏まえつつ、長い転載ではなく再構成で保存する
- project-local skill は `~/.codex/skills/` と `~/.agents/skills/` の両方へ公開する
- 聞き返し workflow は Codex の通常対話で実行できる範囲に留める

## Validation
- `task validate-configs`
- `task symlink`
- `task validate-symlinks`

## Steps
1. 調査
2. 実装
3. 検証

## Progress
- [x] Step 1
- [x] Step 2
- [x] Step 3

## Surprises & Discoveries
- project-local skill は `.agents/skills/` に置くだけでは不十分で、`.bin/symlink.sh` の公開対象更新が必要
- Codex 用の durable 再利用は skill が主で、memory は補助として使うのが repo の設計に合う

## Decision Log
- repo 固有の再利用 surface として、memory より先に repo-local skill を追加する
- skill 本文は workflow を中心にし、長いテンプレート本体は reference file に分離する

## Outcome
- `openai-frontend-prompt-workflow` を repo-local skill として追加した
- `task symlink` で `~/.codex/skills/` と `~/.agents/skills/` に公開した
- `task validate-configs` と `task validate-symlinks` を通した
- `~/.codex/memories/dotfiles-memory.md` に durable memory を追加した
