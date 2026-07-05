---
title: Skill ↔ Subagent 合成パターン
topics: [skill, agent]
sources: [2026-04-08-subagents-claude-code-analysis.md, 2026-04-17-claude-code-session-mgmt-analysis.md, 2026-04-23-skill-graphs-2.0-absorb-analysis.md, 2026-04-27-subagent-context-fork-absorb-analysis.md, 2026-05-31-4-agent-pipeline-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 5
confidence: established
---

# Skill ↔ Subagent 合成パターン

## 概要

Skills と Subagents は Claude Code の2つの再利用単位であり、相互参照が可能。Agent → Skills (ロール定義: 知識を起動時に注入) と Skill → Agent (タスク隔離: fork したコンテキストで実行) の 2 方向の合成があり、組み合わせ方向によって異なるユースケースに対応する。

## 2つの合成方向

### Agent → Skills（ロール定義）

エージェントの frontmatter に `skills:` を指定し、ドメイン知識を起動時に注入する。スキル内容はエージェントのコンテキストに自動展開される。

```yaml
# agents/frontend-developer.md
skills: senior-frontend, react-best-practices
```

エージェントは **アクター**、スキルは **参照資料**。エージェントのロールに必要な知識を事前に焼き込む用途。

### Skill → Agent（タスク隔離）

スキルの frontmatter に `context: fork` と `agent:` を指定し、スキル内容をサブエージェントのタスクプロンプトとして隔離実行する。

```yaml
# skills/prompt-review/SKILL.md
context: fork
agent: Explore
```

スキルは **タスク定義**、エージェントは **実行環境**。メインコンテキストを汚染させたくない冗長なタスクに使用。

## 判断基準

| やりたいこと | パターン | 理由 |
|-------------|----------|------|
| 常に同じ知識が必要なエージェント | Agent + `skills:` | ロール定義に参照資料を焼き込む |
| 冗長な出力を隔離したい | Skill + `context: fork` | メインコンテキストを保護 |
| 新しい専門エージェントを作る | エージェントファイルを作成 | `context: fork` は後付けオプション |

## 制約

- `context: fork` はタスク指示を含むスキルでのみ有効
- ガイドライン系スキル（規約集、チェックリスト等）を fork すると、actionable なプロンプトが渡らず空振りする
- 複数エージェントのオーケストレーションが必要な場合は `context: fork` ではなくスキル本文内で Agent tool を明示呼び出しする

## 現セットアップの状態（2026-04-07 時点）

- **Agent → Skills**: 15+ エージェントが活用（成熟）
- **Skill → Agent**: `prompt-review` のみ使用（拡大余地あり）
- 各スキル改善時に `context: fork` への移行を個別検討する方針

## Subagent 委譲の判断基準

- **Mental Test Heuristic**: 「この出力を後で再利用するか、それとも結論だけ必要か？→結論だけなら subagent に委譲」（Claude Code公式 Session Management記事）。冗長な中間出力をメインコンテキストから隔離する際の一行判断基準
- **Context cleanliness原則としてのFork非採用**: `CLAUDE_CODE_FORK_SUBAGENT=1`（親contextの全継承）はデフォルトで意図的に非採用。Subagentは要約のみ親に返すのがcontext isolationの核心的価値であり、全継承は設計思想と逆方向。例外的な手動実験にのみ限定する
- **Drive responsibility のレイヤリング**: 「誰がどのレベルを操縦するか」を atom=hook駆動 / molecule=subagent駆動 / compound=人間駆動、と層別に規定する（ADR-0008）。Coordinator教義（Never delegate understanding）と Human RAM Model（並列5 agents前提のレバレッジ論）の緊張関係を明文化し、並列度をatom/simple molecule層に限定する
- **公式5パターン + 4指示方法**: research delegation / parallel independent tasks / fresh perspective review / pre-commit verification / pipeline の5パターンと、conversational / custom agent / CLAUDE.md / skills+hooks の4指示方法（Claude Code公式ブログ）。ソロ環境でのfresh perspective review（advisory review）が最も過小評価されやすく、ハーネス変更時のmandatory review blockで補強する
- **固定パイプラインの意図的不採用**: Planner→Coder→Tester→Reviewerの4役割固定パイプラインは、dotfilesの動的S/M/L分岐とCoordinator一貫性（Never delegate understanding）に反するため不採用。ただしTesterの役割境界（テスト側バグは自分で直す、production側バグは直さず報告してSTOP）は有用な知見として`test-engineer`の運用に採用

## 関連知見の重複整理

Skill Graphs 2.0 の3層合成モデル（atoms/molecules/compounds）自体は [スキルチェイニング](skill-chaining.md) を参照。本記事では同モデルのうち「誰が各層を駆動するか」という Agent/Subagent 視点の drive responsibility のみを扱う。

## 関連

- [マルチエージェント・アーキテクチャ](multi-agent-architecture.md) — 複数エージェントの協調パターン
- [スキル設計](skill-design.md) — SKILL.md のベストプラクティス
- [Claude Code アーキテクチャ](claude-code-architecture.md) — サブエージェント・スキルシステムの内部設計

## ソース

- "Skills can use subagents, Subagents can use skills" — X post on Claude Code agent design patterns
- 分析レポート: `docs/research/2026-04-07-skill-subagent-composition-analysis.md`
- [Subagents in Claude Code (公式ブログ)](../../research/2026-04-08-subagents-claude-code-analysis.md) — 公式サブエージェント指南を分析、レビュー強制と可観測性を追加
- [Claude Codeセッション管理と1Mコンテキスト記事分析](../../research/2026-04-17-claude-code-session-mgmt-analysis.md) — Claude Code公式1Mコンテキスト記事分析、Rewind等6項目を全採用
- [Skill Graphs 2.0](../../research/2026-04-23-skill-graphs-2.0-absorb-analysis.md) — Skill Graphs記事を分析、composition depth計測とADR追加を採用
- [Subagent Context Fork absorb分析](../../research/2026-04-27-subagent-context-fork-absorb-analysis.md) — Subagent context fork記事を分析、fork機能非採用・観測3件採用
- [4-Agent Pipeline (Planner→Coder→Tester→Reviewer) absorb分析](../../research/2026-05-31-4-agent-pipeline-absorb-analysis.md) — 4エージェント固定パイプラインを分析、Tester境界1件のみ採用しほぼ不採用
