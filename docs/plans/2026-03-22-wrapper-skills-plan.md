# Wrapper Skills For Installed OpenAI Skills

## Goal
- 既に導入した curated skill を覚えなくても使えるように、repo-local wrapper skill を追加する
- GitHub review/CI と文書・成果物生成の2系統を短い呼び出しで扱えるようにする

## Scope
- 触るファイル:
  - `docs/plans/2026-03-22-wrapper-skills-plan.md`
  - `.agents/skills/github-review-workflow/SKILL.md`
  - `.agents/skills/github-review-workflow/agents/openai.yaml`
  - `.agents/skills/github-review-workflow/references/usage.md`
  - `.agents/skills/artifact-workflow/SKILL.md`
  - `.agents/skills/artifact-workflow/agents/openai.yaml`
  - `.agents/skills/artifact-workflow/references/usage.md`
  - `.bin/symlink.sh`
  - `.bin/validate_symlinks.sh`
  - `AGENTS.md`
- 触らないファイル:
  - `.codex/config.toml`
  - `.codex/rules/*`
  - 既存 curated skill 本体

## Constraints
- wrapper skill は既存 curated skill の上に薄く乗せる
- GitHub / Vercel / Sentry の認証前提は wrapper 側でも落とさない
- project-local skill は `~/.codex/skills/` と `~/.agents/skills/` の両方へ公開する

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
- curated skill は単体では強いが、どれを呼ぶかを毎回覚える friction がある
- `gh-fix-ci` は実装前に explicit approval を求める前提なので wrapper でも維持する

## Decision Log
- repo 固有の再利用性を優先し、wrapper は repo-local skill として追加する
- usage examples は `references/usage.md` に分離して、SKILL 本体は workflow 中心に保つ

## Outcome
- `github-review-workflow` と `artifact-workflow` を repo-local skill として追加した
- `task symlink` で `~/.codex/skills/` と `~/.agents/skills/` に公開した
- `task validate-configs` と `task validate-symlinks` を通した
