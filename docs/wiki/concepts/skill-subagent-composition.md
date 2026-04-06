# Skill ↔ Subagent 合成パターン

Skills と Subagents は Claude Code の2つの再利用単位であり、相互参照が可能。組み合わせ方向によって異なるユースケースに対応する。

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

## 関連

- [マルチエージェント・アーキテクチャ](multi-agent-architecture.md) — 複数エージェントの協調パターン
- [スキル設計](skill-design.md) — SKILL.md のベストプラクティス
- [Claude Code アーキテクチャ](claude-code-architecture.md) — サブエージェント・スキルシステムの内部設計

## ソース

- "Skills can use subagents, Subagents can use skills" — X post on Claude Code agent design patterns
- 分析レポート: `docs/research/2026-04-07-skill-subagent-composition-analysis.md`
