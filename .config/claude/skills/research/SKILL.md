---
name: research
description: >
  マルチモデル並列リサーチ。研究テーマを分解し、サブタスクの性質に応じて claude -p / Gemini / Codex に
  自動割り当てして並列実行、結果を集約してレポートを生成する。深い調査や複数ソースの統合が必要な場合に使用。
  Triggers: '調査して', '深掘り', 'research', '複数ソース', '並列調査', 'multi-source investigation'.
  Do NOT use for simple single-query searches — use WebSearch or gemini skill instead.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
metadata:
  pattern: pipeline
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

### サブ目標の多様性チェック

5個以上のサブ目標がある場合、冗長なサブ目標がないか目視確認する:

- 同じトピックを異なる角度で分解しているだけのペアがないか
- 統合しても調査品質が落ちないペアがあれば統合を検討

> Note: サブ目標タイトルは短文のため TF-IDF ベースの自動類似度計測は不向き。
> サブタスク**出力**の重複排除には Step 4 Aggregate の類似度ベース重複排除を使用する。
> 詳細: `references/diversity-selection-guide.md`

## Step 2: Plan

サブタスクを一覧としてユーザーに提示し、承認を得る:

```
## リサーチ計画: {topic}

| # | サブ目標 | モデル | 手法 | 推定時間 |
|---|---------|--------|------|---------|
| 1 | {goal}  | {model} | {tool} | ~N min |
```

### モデル自動割り当て

各サブタスクの性質に基づき、最適なモデルを**自動選択**する（人間の判断不要）:

| サブタスクの性質 | モデル | 理由 |
|----------------|--------|------|
| 外部エコシステム、代替案比較、ライブラリ調査、コミュニティ動向、セキュリティ脆弱性の動向 | **Gemini** | Google Search grounding + 1M コンテキスト |
| 設計判断、トレードオフ分析、リスク評価、アーキテクチャ比較 | **Codex** | 深い推論 (reasoning_effort=high) |
| 学術文献調査、引用分析、論文の信頼性評価、研究ギャップ発見 | **Scite MCP** | Smart Citations + 250M+ 論文検索 |
| コードベース分析、一般的な調査、ドキュメント読解 | **claude -p** | デフォルト |

**ルール**:
- 3サブタスク以上あれば、最低1つは Gemini に割り当てる（外部視点の確保）
- Gemini/Codex が利用不可の場合は claude -p にフォールバック
- 同一トピックを異なるモデルに割り当てない（重複回避）

**ユーザーの承認なしに Step 3 に進んではいけない。** モデル割り当ても含めて確認を得ること。

## Step 3: Execute

### フレーミング注入

各サブタスクのプロンプト先頭に **Async フレーミング**（`references/subagent-framing.md`）を付加する:

> あなたは非同期サブエージェントです。結果はユーザーに直接報告されます。
> 背景・分析・結論を含む自己完結的なレポートを作成してください。ソースや根拠を明記してください。

### ツール（各モデル共通）

- **MCP ツール**: brave-search, context7, scite（インストール済みの場合）
- **Scite MCP**: 学術文献検索・Smart Citations・引用グラフ分析。学術トピックのサブタスクで積極的に使用
- **WebFetch/WebSearch**: 標準ツール

### マルチモデル並列実行

Step 2 のモデル割り当てに基づき、各サブタスクを適切なモデルで実行する:

```bash
# claude -p サブタスク
claude -p "$(cat .research/{name}/prompts/${i}.md)" \
  --allowedTools "Read,WebFetch,WebSearch,Bash,Grep,Glob" \
  > .research/{name}/child_outputs/${i}.md 2>/dev/null &

# Gemini サブタスク
gemini --approval-mode plan \
  -p "$(cat .research/{name}/prompts/${i}.md)" \
  > .research/{name}/child_outputs/${i}.md 2>/dev/null &

# Codex サブタスク
codex exec --skip-git-repo-check -m gpt-5.4 \
  --config model_reasoning_effort="high" \
  --sandbox read-only \
  "$(cat .research/{name}/prompts/${i}.md)" \
  > .research/{name}/child_outputs/${i}.md 2>/dev/null &

wait
```

サブタスクが2つ以下の場合は Agent ツールで並列実行する（子プロセス不要）。

### フォールバック

モデルがエラーや空出力を返した場合、claude -p で同じプロンプトを再実行する。

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
- 各サブ目標の結果（ソース付き、**使用モデルを明記**）
- 発見事項のクロスリファレンス
- **クロスモデル分析**: 異なるモデルが同じトピックに言及している場合、合意・相違を注記

### Aggregate 品質基準

> 出典: Câmara+ 2026 "Self-Optimizing Multi-Agent Systems for Deep Research" — Aggregator が品質ゲートを担うことで最終レポートの信頼性が向上

集約時に以下の品質フィルタを適用する:

| チェック | アクション |
|---------|-----------|
| **重複排除** | 複数サブタスクが同一ソース/同一主張を報告 → 1つに統合し出典元を併記 |
| **矛盾検出** | サブタスク間で相反する主張 → 両方を明示し、エビデンス強度で優劣を注記 |
| **エビデンス強度フィルタ** | 根拠なし/単一ソースのみの主張 → `[要追加調査]` タグを付与 |
| **カバレッジ確認** | Step 2 のサブ目標に対して未回答の項目 → 明示的に「未解決」と記載 |
| **類似度ベース重複排除** | cosine > 0.7 のサブタスク出力ペア → 統合候補としてフラグ。`scripts/lib/diversity_metrics.py` で計測可能。詳細: `references/diversity-selection-guide.md` |

## Step 5: Polish

チャプター毎に精査:

1. ソースの信頼性を検証（Scite MCP 利用時は Smart Citations のサポート率/矛盾率を活用）
2. 矛盾する情報を特定・注記
3. 不足情報のギャップを明示

最終レポートを `docs/research/YYYY-MM-DD-{name}.md` に保存。
`.research/{name}/` の中間ファイルはそのまま残す（.gitignore 対象）。

### Step 6: Wiki フィードバック（任意）

レポートが `docs/research/` に保存され、`docs/wiki/` が存在する場合:
- 「wiki を更新しますか？」とユーザーに確認
- 承認された場合のみ `/compile-wiki update` を実行

## Scale-Aware Execution

| サブタスク数 | 実行方法                                |
| ------------ | --------------------------------------- |
| 1-2          | Agent ツールで並列（子プロセス不要）    |
| 3-8          | claude -p で並列実行                    |
| 9+           | 2バッチに分割して順次実行（メモリ保護） |

## Templates

- `templates/research-report-template.md` — リサーチレポート出力テンプレート

## Decision: research vs gemini vs debate

| 状況 | 推奨 | 理由 |
|------|------|------|
| 深い調査、複数ソースの統合が必要 | `/research` | マルチモデル並列リサーチ |
| 1M超の大規模コード/ドキュメント分析 | `/gemini` | 1Mコンテキスト活用 |
| 技術選定、トレードオフ比較 | `/debate` | 複数モデルの独立見解を収集 |
| 単純な検索クエリ | WebSearch | スキル不要 |

## Anti-Patterns

- ユーザー承認なしに並列実行を開始する
- 1つの単純な質問に /research を使う（→ WebSearch で十分）
- 子プロセスの出力をそのまま貼り付ける（必ず集約・構造化する）
- ソースなしで結論を述べる

## Gotchas

- **並列セッションの出力衝突**: 複数の claude -p が同じ `.research/{name}/` に書き込むとファイル破損する。サブタスクごとにサブディレクトリを分ける
- **MCP タイムアウト**: WebSearch/WebFetch は外部依存。タイムアウト時はフォールバック（内蔵知識ベースの回答）を使う
- **Gemini の hallucination**: Google Search grounding があっても Gemini は事実と異なる情報を返すことがある。クロスバリデーション必須
- **レポート肥大化**: サブタスクが多すぎると統合レポートが巨大になる。3-5 サブタスクが最適
- **言語プロトコル**: CLI への指示は英語、ユーザーへの報告は日本語。混在させるとモデルの出力品質が下がる

## Skill Assets

- サブタスクプロンプト: `templates/subtask-prompt.md`
- モデル割り当て基準: `references/model-assignment-guide.md`
- レポートテンプレート: `templates/research-report-template.md` (既存)
