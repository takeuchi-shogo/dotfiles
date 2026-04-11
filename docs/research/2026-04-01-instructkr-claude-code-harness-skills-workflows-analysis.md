---
source: https://github.com/instructkr/claude-code/tree/main/src
date: 2026-04-01
status: analyzed
related:
  - docs/research/2026-03-31-instructkr-claude-code-src-analysis.md
---

## Focus

前回メモが `src/` 全体の内部構造の俯瞰だったのに対し、このメモは以下に絞る。

- harness のアーキテクチャ
- system prompt / agent prompt / memory prompt の構成法
- skills の定義・配布・発火モデル
- workflow の組み立て方
- 実践上の設計パターン

結論から言うと、この repo の本質は「CLI 本体」よりも、**markdown-configurable な agent harness** にある。`CLAUDE.md`、rules、skills、agents、hooks、attachments、prompt sections、permission system が一体で動いており、特定の 1 ファイルが harness なのではなく、複数の設定レイヤーが turn ごとに合成される control plane になっている。

## Harness Architecture

### 1. Harness は layered control plane

静的読解から見えた主なレイヤーは次の順。

1. **default system prompt**
   - `src/constants/prompts.ts`
2. **effective system prompt composer**
   - `src/utils/systemPrompt.ts`
3. **durable repo/user instructions**
   - `src/utils/claudemd.ts`
4. **markdown-configurable runtime surfaces**
   - `src/utils/markdownConfigLoader.ts`
5. **skills / agents frontmatter**
   - `src/skills/loadSkillsDir.ts`
6. **event-driven hooks**
   - `src/utils/hooks/hooksConfigManager.ts`
   - `src/utils/sessionStart.ts`
7. **runtime attachments / reminders**
   - `src/utils/messages.ts`
   - `src/constants/prompts.ts`
8. **permission / tool execution control**
   - `src/services/tools/toolExecution.ts`

この構造の重要点は、instruction を 1 箇所へ全部押し込まないこと。repo knowledge、workflow knowledge、runtime reminder、tool policy が別の層に分かれている。

### 2. CLAUDE.md は docs ではなく prompt substrate

`src/utils/claudemd.ts` によると memory/instruction の優先順位は明確に定義されている。

1. managed memory
2. user memory
3. project memory
4. local memory

さらに:

- `@include` を解釈できる
- `.claude/rules/*.md` を読み込む
- frontmatter `paths` で適用範囲を絞れる
- `InstructionsLoaded` hook を発火できる

つまり `CLAUDE.md` は README 的な説明文ではなく、**runtime にロードされる instruction program** として扱われている。repo 運用 knowledge は skill にも hook にも寄せられるが、持続的で横断的なルールはまずここへ載る設計。

### 3. Markdown directory 群が harness surface

`src/utils/markdownConfigLoader.ts` の `CLAUDE_CONFIG_DIRECTORIES` は以下を持つ。

- `commands`
- `agents`
- `output-styles`
- `skills`
- `workflows`
- feature flag により `templates`

ここから分かるのは、Claude Code 内部では markdown が単なる文書ではなく、**config artifact** として統一的に扱われていること。skill だけが特別なのではなく、agent も workflow も同じ family に入っている。

## Prompt Architecture

### 1. Prompt は static と dynamic を分離している

`src/constants/prompts.ts` には `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` があり、session-specific guidance をその後ろへ押し出している。狙いは明白で、**cache しやすい静的 prefix と、turn ごとに変わる guidance を分けること**。

`src/constants/systemPromptSections.ts` も同じ思想で、system prompt section を memoize し、必要時だけ cache break する API を持つ。

これは実践上かなり重要で、skill list、agent list、MCP 状態、permission 状態のような「正しいが揺れやすい」情報を全部 system prompt 本文へ直書きすると、prompt cache を壊しやすい。ここではそれを architecture で避けている。

### 2. Effective system prompt は role layering で決まる

`src/utils/systemPrompt.ts` の `buildEffectiveSystemPrompt()` は優先順位を持つ。

1. override system prompt
2. coordinator prompt
3. agent prompt
4. custom system prompt
5. default system prompt

加えて proactive mode では agent prompt を default prompt に append する。

この設計の含意は、agent は「runtime subprocess」以前に **prompt-layering primitive** だということ。agent type を変えるとは、実行主体を変えるだけでなく、prompt identity を差し替えることでもある。

### 3. Skill discovery は prompt 本文より reminder attachment を重視

`src/constants/prompts.ts` の `getDiscoverSkillsGuidance()` と `src/utils/messages.ts` の reminder まわりを見ると、使える skill を常に system prompt 本文へ全列挙するより、**必要時に reminder として差し込む** 方針が見える。

これは次の利点を持つ。

- prompt 本体の肥大化を抑える
- cache 破壊を減らす
- 実行時に relevant な skill だけを surfaced できる

言い換えると、この repo は「prompt に全部教える」より **prompt と runtime surfacing を分担** している。

## Skills Architecture

### 1. Skill は markdown snippet ではなく typed prompt object

`src/skills/loadSkillsDir.ts` の frontmatter parser から、skill がかなり厚い object であることが分かる。主な frontmatter:

- `description`
- `allowed-tools`
- `arguments`
- `when_to_use`
- `version`
- `model`
- `disable-model-invocation`
- `user-invocable`
- `hooks`
- `context: fork`
- `agent`
- `effort`
- `shell`

この時点で skill は単なるテンプレ文ではなく、**permission, invocation, routing, execution context を持つ mini-program** と見た方が近い。

### 2. Skill body は runtime で materialize される

`createSkillCommand()` は skill markdown を slash command 的な prompt command に変換する。その際に:

- skill base directory を prompt に付与
- 引数置換
- `${CLAUDE_SKILL_DIR}` / `${CLAUDE_SESSION_ID}` 展開
- 条件付きで prompt 内 shell 実行
- prompt shell 実行時に `allowed-tools` を temporary allow として扱う

という処理がある。

重要なのは、skill の本文が静的文字列ではなく **session context に応じて具体化される prompt artifact** だということ。

### 3. Skill loading は discovery system を兼ねる

`getSkillDirCommands()` は skill を複数ソースから統合する。

- managed
- user
- project
- additional directories
- legacy `/commands`

さらに:

- file identity で dedupe
- `skillsLocked` / plugin-only policy を尊重
- `paths` frontmatter による conditional skill
- touched path から nested skill dir discovery

このため skill system は「定義を読む仕組み」だけでなく、**どの skill を今 surfacing すべきかを判定する discovery engine** でもある。

### 4. Bundled skills が internal best practice の実装例

`src/skills/bundled/remember.ts` や `src/skills/bundled/skillify.ts` は特に参考になる。

- `remember`:
  - memory をどう整理し、何を保存対象にするかを workflow として明文化
- `skillify`:
  - セッションから再利用可能 workflow を抽出し、ユーザーへの interview を経て SKILL.md 化する

特に `skillify` は、「良い skill とは何か」を内省的に説明していて価値が高い。そこでは:

- Goal
- Inputs
- ordered Steps
- Success criteria
- optional Artifacts
- Human checkpoint
- Rules
- Execution mode

を入れるよう要求している。つまりこの repo の skill 観は、**曖昧な tips 集ではなく、完了条件つき workflow spec** である。

## Workflow Architecture

### 1. Workflow は slash command だけではない

この snapshot を読むと、workflow は少なくとも 4 つの経路で組み立てられている。

1. **skill as on-demand workflow**
2. **hook as event-driven workflow**
3. **agent as delegated workflow**
4. **CLAUDE.md / rules as durable workflow constraints**

つまり「workflow を作る」とは独立の DSL を 1 つ書くことではなく、side effect の性質に応じて載せるレイヤーを変えること。

### 2. Hook system が workflow automation の主軸

`src/utils/hooks/hooksConfigManager.ts` の event 一覧を見ると、hook が非常に広い lifecycle を覆っている。

- `PreToolUse`
- `PostToolUse`
- `PostToolUseFailure`
- `PermissionDenied`
- `UserPromptSubmit`
- `SessionStart`
- `Stop`
- `SubagentStart`
- `SubagentStop`
- `PreCompact`
- `PostCompact`
- `SessionEnd`
- `PermissionRequest`
- `Setup`
- `TaskCreated`
- `TaskCompleted`
- `Elicitation`
- `ElicitationResult`
- `ConfigChange`
- `InstructionsLoaded`
- `WorktreeCreate`
- `WorktreeRemove`
- `CwdChanged`
- `FileChanged`

ここから分かるのは、この repo における workflow は「一連の手順書」だけでなく、**session lifecycle へ差し込む event program** でもあること。

### 3. SessionStart / Setup / frontmatter hooks が workflow wiring を担う

`src/utils/sessionStart.ts` と `src/utils/hooks/registerFrontmatterHooks.ts` を見ると、plugin hooks や skill/agent frontmatter hooks が session scoped に登録される。

つまり workflow は skill 本文の中だけで完結せず、**skill を入れた瞬間に hook wiring まで session へ注入できる**。この構造により、knowledge artifact と automation artifact を同じ配布単位にまとめられる。

### 4. Workflow scripts は参照されるが snapshot では欠落

`src/commands.ts` と `src/tools.ts` は `WORKFLOW_SCRIPTS` feature のもとで `./commands/workflows/index.js` や `WorkflowTool` を参照している。しかし snapshot 内に対応実装は見当たらない。

確認できた範囲では:

- registry 側の import trace は存在する
- `markdownConfigLoader` は `workflows` directory を知っている
- しかし `src/commands/workflows/` や `src/tools/WorkflowTool/` 実装は archive から欠けている

したがって、**workflow surface 自体は product concept として存在するが、この公開 snapshot だけでは完全な実装を追い切れない**。

## Practical Methods

### 1. Artifact placement を分ける

`src/commands/init.ts` がかなり露骨に設計原則を示している。

- **CLAUDE.md note**
  - 常時効かせたい repo instruction
- **Skill**
  - 必要時だけ呼びたい workflow や reference knowledge
- **Hook**
  - Claude に必ず実行させたい deterministic automation

この切り分けは実務的で、そのまま再利用価値がある。

### 2. Good skill は “Success criteria first”

`skillify.ts` のプロンプト設計では、各 step に Success criteria を必須化している。これは良い workflow を作るうえで重要で、モデルは「何をするか」より「いつ次へ進んでいいか」が曖昧だと壊れやすい。

再利用できる skill を書くなら、最低でも以下を固定するべき。

- trigger / `when_to_use`
- input arguments
- step order
- success artifact
- human checkpoint
- hard rules

### 3. Main prompt に全部載せない

この repo は relevant な guidance を reminder / attachment / dynamic section に逃がしている。実践上も、以下は main system prompt に常駐させない方がよい。

- 長大な skill catalog
- 揮発的な session state
- tool availability の細かな変動
- path-specific ルールの全文

代わりに:

- durable で横断的なものは `CLAUDE.md`
- 条件付きのものは rules / path-scoped instruction
- 操作手順は skill
- 自動化は hook
- runtime surfacing は attachment / reminder

という分離が有効。

### 4. Agent は “delegation primitive” ではなく “context control primitive”

`src/tools/AgentTool/prompt.ts` は特に実践的で、agent を使う目的を「理解の外注」ではなく context 制御として説明している。

主な原則:

- fork は context を保ったままノイズを隔離したい時に使う
- fresh specialized agent は独立した second opinion がほしい時に使う
- research と implementation を混ぜて雑に投げない
- “based on your findings, fix it” のように理解を丸投げしない

これは multi-agent workflow を安定させる上でかなり本質的なルール。

### 5. Interview-based setup を標準化している

`src/commands/init.ts` は repo 初期化を単なる scaffold 生成にしていない。コードベース探索、ユーザー interview、proposal 生成、artifact type の選定、hook/skill/CLAUDE.md への振り分けまでを一連の setup workflow として prompt に埋め込んでいる。

つまりこの repo は、workflow を user-facing feature として提供するだけでなく、**workflow を設計する workflow** まで prompt 化している。

## Transferable Patterns

他の harness へ移植しやすいパターンを整理すると:

1. **Prompt cache boundary を明示的に持つ**
   - static と dynamic を分ける
2. **Instruction を 1 file に集約しない**
   - durable notes / conditional rules / workflow skills / event hooks に分離
3. **Skill を spec 化する**
   - trigger、inputs、steps、success criteria、human checkpoint を必須に近づける
4. **Runtime surfacing を別レイヤーにする**
   - relevant skills や agents を attachment/reminder で出す
5. **Hooks を first-class workflow mechanism として扱う**
   - tool event, compact, config change, subagent lifecycle まで覆う
6. **Agent 利用を context isolation の問題として設計する**
   - 何を別 agent に切るかを task size ではなく context noise で決める

## Caveats

- 調査は `src/` snapshot の静的読解ベース。build や test はしていない。
- `WORKFLOW_SCRIPTS` まわりは registry 参照に対して実装が欠けるため、公開 snapshot に含まれない内部コードがある可能性が高い。
- `src` は一部 transformed artifact を含む可能性があり、authoring source と 1:1 ではない。

## Files Worth Reading

このテーマで優先度が高いファイル:

- `src/constants/prompts.ts`
- `src/constants/systemPromptSections.ts`
- `src/utils/systemPrompt.ts`
- `src/utils/claudemd.ts`
- `src/utils/markdownConfigLoader.ts`
- `src/skills/loadSkillsDir.ts`
- `src/skills/bundled/remember.ts`
- `src/skills/bundled/skillify.ts`
- `src/utils/hooks/hooksConfigManager.ts`
- `src/utils/sessionStart.ts`
- `src/utils/messages.ts`
- `src/tools/AgentTool/prompt.ts`
- `src/commands/init.ts`
