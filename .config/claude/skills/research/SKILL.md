---
name: research
description: >
  マルチエージェント並列リサーチ。研究テーマを分解し、claude -p 子プロセスで並列実行、
  結果を集約してレポートを生成する。深い調査や複数ソースの統合が必要な場合に使用。
  Do NOT use for simple single-query searches — use WebSearch or gemini skill instead.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# Deep Research — Multi-Agent Orchestration

## Trigger

`/research {topic}` で起動。

## Workflow

1. **Reconnaissance** — トピックの初期調査、サブ目標の分解
2. **Plan** — サブタスクのリスト提示、ユーザー確認
3. **Execute** — claude -p で並列実行（最大8並列）
4. **Aggregate** — 結果を集約
5. **Polish** — チャプター毎に精査、最終レポート生成

## Step 1: Reconnaissance

トピックについて軽く調査し、以下を特定する:

- 調査の範囲（何を含み、何を含まないか）
- 3-8個のサブ目標に分解
- 各サブ目標に使うべきツール/ソース

## Step 2: Plan

サブタスクを一覧としてユーザーに提示し、承認を得る:

```
## リサーチ計画: {topic}

| # | サブ目標 | 手法 | 推定時間 |
|---|---------|------|---------|
| 1 | {goal}  | {tool} | ~N min |
```

**ユーザーの承認なしに Step 3 に進んではいけない。**

## Step 3: Execute

### フレーミング注入

各サブタスクのプロンプト先頭に **Async フレーミング**（`references/subagent-framing.md`）を付加する:

> あなたは非同期サブエージェントです。結果はユーザーに直接報告されます。
> 背景・分析・結論を含む自己完結的なレポートを作成してください。ソースや根拠を明記してください。

### ツール優先度

1. **MCP ツール**: brave-search, context7（インストール済みの場合）
2. **WebFetch/WebSearch**: 標準ツール
3. **gemini CLI**: 大規模分析が必要な場合（`gemini -p "..." 2>/dev/null`）

### 並列実行

サブタスクが3つ以上の場合、`claude -p` で並列実行する:

```bash
# 各サブタスクを .research/{name}/prompts/{n}.md に保存（一時ワークスペース）
# 並列で実行
for i in $(seq 1 $N); do
  claude -p "$(cat .research/{name}/prompts/${i}.md)" \
    --allowedTools "Read,WebFetch,WebSearch,Bash,Grep,Glob" \
    > .research/{name}/child_outputs/${i}.md 2>/dev/null &
done
wait
```

サブタスクが2つ以下の場合は Agent ツールで並列実行する（子プロセス不要）。

### ディレクトリ構造

```
.research/{name}/          # 一時ワークスペース（.gitignore 対象）
├── prompts/               # サブタスクプロンプト
├── child_outputs/         # 子プロセス出力
└── logs/                  # 実行ログ

docs/research/             # 最終レポートの保存先（git 管理）
└── YYYY-MM-DD-{name}.md
```

## Step 4: Aggregate

全子プロセスの出力を読み取り、以下を生成:

- Executive Summary（3-5文）
- 各サブ目標の結果（ソース付き）
- 発見事項のクロスリファレンス

## Step 5: Polish

チャプター毎に精査:

1. ソースの信頼性を検証
2. 矛盾する情報を特定・注記
3. 不足情報のギャップを明示

最終レポートを `docs/research/YYYY-MM-DD-{name}.md` に保存。
`.research/{name}/` の中間ファイルはそのまま残す（.gitignore 対象）。

## Scale-Aware Execution

| サブタスク数 | 実行方法                                |
| ------------ | --------------------------------------- |
| 1-2          | Agent ツールで並列（子プロセス不要）    |
| 3-8          | claude -p で並列実行                    |
| 9+           | 2バッチに分割して順次実行（メモリ保護） |

## Anti-Patterns

- ユーザー承認なしに並列実行を開始する
- 1つの単純な質問に /research を使う（→ WebSearch で十分）
- 子プロセスの出力をそのまま貼り付ける（必ず集約・構造化する）
- ソースなしで結論を述べる
