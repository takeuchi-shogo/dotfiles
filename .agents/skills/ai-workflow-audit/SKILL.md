---
name: ai-workflow-audit
description: Audit and upgrade a repo's AI operating model. Use when improving Codex or Claude workflows, deciding what belongs in skills vs memory vs scripts, or sharing reusable AI practices across repos.
---

# AI Workflow Audit

`docs/guides/ai-workflow-audit.md` を前提に、単発の AI 利用を repo に残る workflow へ昇格する。

## When To Use

- harness 変更を設計するとき
- 同じ prompt や調査を何度も繰り返しているとき
- Codex / Claude / MCP / task の役割分担を整理したいとき
- 知見を他の repo に持ち出せる形へ整えたいとき

## Workflow

1. 何を改善したいかを 1 文で書く。
2. `AGENTS.md`、`Taskfile.yml`、`.mcp.json`、`.agents/skills/`、`.codex/`、`.config/claude/`、関連 docs を `rg` で確認する。
3. gap を次の lens で分類する。
   - discovery
   - orchestration
   - verification
   - memory and continuity
   - portability
   - packaging
4. 変更先を選ぶ。
   - session 限定: checkpoint
   - repo 固有: `AGENTS.md` or repo-local skill
   - cross-repo: global skill or durable memory
   - 実行保証: task / script / hook
   - 外部情報導線: MCP / config
5. 最小の artifact から実装する。まず既存 skill / script の extend を優先し、足りないときだけ build する。
6. 変更面に最も近い validation を実行する。

## Article Mapping

- Tool stacking: tool を増やすのではなく、task / skill / MCP / CLI の接続を設計する
- Research systems: 実装前調査を workflow に組み込む
- Coding: 繰り返しを script や config に落とす
- Agentic workflow design: checkpoint、memory、delegation を整える
- Prompt engineering: 再利用したい prompt は skill description や output format に固定する

## Output

- current friction
- chosen lens
- target surface
- smallest implementation
- validation plan

## Anti-Patterns

- prompt だけで済ませ、repo に何も残さない
- repo 固有ルールを durable memory に一般化しすぎる
- task や validation で担保すべきものを docs だけで済ませる
