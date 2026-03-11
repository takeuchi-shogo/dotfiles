# AI Workflow Audit

単発の prompt を、repo に残る AI workflow へ昇格するためのガイド。

## When To Use

- AI の使い方が属人的で、再現性がない
- 同じ調査、同じ指示、同じ修正が繰り返される
- Codex と Claude Code の役割分担を整理したい
- 知見を他の repo にも持ち出せる形へ整えたい
- 新しい skill、memory、script、hook、MCP のどれに落とすべきか迷う

## Audit Lenses

### 1. Discovery

- 実装前に何を調べるか
- 既存 task、script、skill、MCP、docs を先に見ているか
- 調査結果が decision に反映されているか

### 2. Orchestration

- 単一モデルに頼らず、task、skill、MCP、CLI を組み合わせているか
- Codex と Claude Code の責務が分かれているか
- 手動で繰り返しているステップがないか

### 3. Verification

- 完了前に実コマンドで検証しているか
- review、lint、test、config validation の導線があるか
- 証拠がないまま「完了」と言っていないか

### 4. Memory And Continuity

- session をまたぐ情報が checkpoint に残っているか
- repo 固有ルールが durable memory や skill に昇格されているか
- 一時情報と恒久ルールが混ざっていないか

### 5. Portability

- repo 固有ルールと cross-repo ルールが分離されているか
- 他 repo に持ち出すとき、何をコピーすればよいか明確か
- 特定ツール前提の知識が、必要以上にグローバル化されていないか

### 6. Packaging

- よく使う判断や手順が skill 化されているか
- 必須の検証や整形が script / task / hook へ落ちているか
- 出力フォーマットが毎回ぶれていないか

## Promotion Matrix

| Situation | Best Surface | Why |
| --- | --- | --- |
| 今回の session だけ必要な状態 | checkpoint | transient で、次回再開にだけ使う |
| repo 固有の安定ルール | `AGENTS.md` or repo-local skill | repo と一緒に version 管理できる |
| 複数 repo で再利用する判断基準 | global skill or durable memory | repo をまたいで使い回せる |
| 毎回必ず守らせたい手順 | task / script / hook | 実行で強制できる |
| 外部情報の取得経路 | MCP / tool config | prompt ではなく接続面に寄せる |
| 変更対象に近い操作メモ | tool README / guide | 実ファイルの近くで見つけやすい |

## Recommended Workflow

1. Goal と friction を 1 文ずつ定義する
2. `AGENTS.md`、`Taskfile.yml`、validation script、`.mcp.json`、`.agents/skills/`、`.codex/`、`.config/claude/` を確認する
3. どの lens に gap があるかを 1 つか 2 つに絞る
4. 最小の昇格先を選ぶ
5. guide より skill、skill より script が適切なら昇格する
6. 変更面に最も近い validation を実行する

## Current Repo Mapping

### Codex

- repo rule: `AGENTS.md`
- repo-local workflow: `.agents/skills/`
- durable memory: `~/.codex/memories/`
- short-term continuity: `tmp/codex-state/`
- verification: `Taskfile.yml`, `.bin/validate_*.sh`

### Claude Code

- global instruction: `.config/claude/CLAUDE.md`
- reusable workflow: `.config/claude/skills/`
- agent routing: `.config/claude/agents/`
- automation: `.config/claude/scripts/`, `settings.json`
- continuity: `~/.claude/session-state/`, `~/.claude/agent-memory/`

## Share To Other Repos

- repo 固有の運用は各 repo の `AGENTS.md` と local skill に残す
- 複数 repo で再利用する判断基準は global skill や durable memory に昇格する
- 実行保証が必要なものは docs ではなく task / script / hook に移す
- まず guide を移植し、次に recurring なものだけ skill 化する

## Anti-Patterns

- prompt だけで運用し、再利用面に何も残さない
- repo 固有ルールを global memory に混ぜる
- 一時的な作業ログを durable memory に昇格する
- 新しい script を増やす前に既存 task / skill / MCP を見ない
