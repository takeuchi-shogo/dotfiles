---
name: research
description: "マルチモデル並列リサーチ。研究テーマを分解し、サブタスクの性質に応じて claude -p / Gemini / Codex に自動割り当てして並列実行、結果を集約してレポートを生成する。深い調査や複数ソースの統合が必要な場合に使用。Triggers: '調査して', '深掘り', 'research', '複数ソース', '並列調査', 'リサーチして', 'まとめて調べて', '徹底的に調べて', 'multi-source investigation', 'deep dive', 'comprehensive research'. Do NOT use for: 単発検索 (use WebSearch)、単一モデルへの質問 (use /codex or /gemini)、記事 1 本の要約 (use /digest)。"
origin: self
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
metadata:
  pattern: pipeline
  chain:
    upstream: ["/spec (リサーチテーマ定義)"]
    downstream: ["/absorb (取り込み判断)", "/digest (記事 1 本要約)"]
---

# Deep Research — Multi-Agent Orchestration

## Philosophy: Thoroughness over Helpfulness

リサーチの第一義は **網羅性と検証可能性**。helpful に寄せて未検証情報を埋めない。

- 情報不足は明示する（「該当なし」「未解決」と記載）。推測で埋めない
- 速度より網羅性を優先。複数ソースの突き合わせで矛盾を surface する
- 出典のない主張は `[要追加調査]` タグを付与する
- ベンチマーク「#1」等の外部主張は評価バイアス前提で扱い、単独の採用根拠にしない

> 出典: Onyx DeepResearch 設計哲学 "Prefer being thorough over being helpful"（Akshay Pachaar 2026-04）。

## Trigger

`/research {topic}` で起動。

## Workflow

1. **Reconnaissance** — トピックの初期調査、サブ目標の分解
2. **Plan** — サブタスクのリスト提示、ユーザー確認
3. **Execute** — claude -p で並列実行（最大8並列）
4. **Aggregate** — 結果を集約
5. **Polish** — チャプター毎に精査、最終レポート生成

## Lifecycle Registry

セッション開始時に `task_registry.register()` でタスクを登録し、Polish 完了時に
`update_status()` で完了状態と成果物パスを記録する。

**Trigger 条件**: 単発 query は登録不要。サブタスクが 2 件以上（並列実行）の場合のみ登録。
理由: schema 規約（task-registry-schema.md）の「短寿命の Sync subagent は registry に書かない」。

**Step 2 Plan 完了時に register**:
```bash
TASK_ID=$(python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts/lib')
from task_registry import register
print(register('async', 'research', '<topic>', metadata={'subtask_count': N, 'angles': '<csv>'}))
")
```

**Step 5 Polish 完了時に update_status**:
```bash
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts/lib')
from task_registry import update_status
update_status('$TASK_ID', 'completed',
    output_path='<report path>',
    metadata={'duration_ms': N, 'subtask_count': N})
"
```

エラーで中断した場合は `update_status('$TASK_ID', 'failed', error='<msg>')` を呼ぶ。
metadata の任意拡張規約は `references/task-registry-schema.md` 参照。

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

### `--angles` preset (多角度リサーチ)

`--angles=academic,practitioner,contrarian,historical,empirical` を指定すると、サブ目標を以下の **5 角度テンプレート** で強制展開する。単一視点に偏らないよう多様性を担保するための opt-in オプション。

出典: Kevin's "Modified Karpathy Method" (2026-04) の `/research [topic]` — 5-8 並列エージェントを学術/実務/反対/歴史/実証の 5 角度で展開するパターンの移植。

| angle | 担当視点 | デフォルトモデル | 具体的な焦点 |
|-------|---------|-----------------|-------------|
| `academic` | 学術文献・理論 | Scite MCP | 査読論文、理論的裏付け、研究ギャップ |
| `practitioner` | 実務採用・事例 | Gemini | プロダクション事例、採用企業、運用知見 |
| `contrarian` | 反対意見・批判 | Codex | 手法の限界、失敗事例、反証、代替案 |
| `historical` | 歴史的経緯 | claude -p | 先行手法、議論の変遷、deprecated アプローチ |
| `empirical` | 実証データ | Gemini | ベンチマーク、統計、定量比較 |

#### 起動方法

- **明示的指定**: `/research <topic> --angles=academic,practitioner,contrarian,historical,empirical`
- **部分指定**: `--angles=academic,contrarian` のように 2-5 角度を自由に組み合わせ可能
- **自動提案**: トピックが「技術選定」「手法比較」「設計判断」を含む場合、Step 2 Plan で preset 採用を **推奨** する（`AskUserQuestion` で確認）

#### preset 使用時の Reconnaissance 出力

preset を使う場合、Step 1 の出力に各 angle のサブ目標を明示する:

```
## Reconnaissance (--angles preset)

| angle | サブ目標 | 担当モデル |
|-------|---------|-----------|
| academic | {topic} の理論的基盤・査読研究の要約 | Scite MCP |
| practitioner | {topic} を本番採用した企業・実例 | Gemini |
| contrarian | {topic} に対する批判・失敗事例・代替案 | Codex |
| historical | {topic} 手法の変遷・先行手法・議論史 | claude -p |
| empirical | {topic} のベンチマーク・定量データ | Gemini |
```

各 angle は **独立した Agent 呼び出し** として起動され、Step 4 Aggregate で統合される。

#### 既存ワークフローとの関係

- `--angles` は **opt-in** — 指定しなければ従来通り性質ベースの自動割り当て
- preset 指定時も既存の「3サブタスク以上なら Gemini 最低1つ」「Codex/Gemini 利用不可時の claude -p フォールバック」ルールは尊重
- サブ目標数の上限 8 を超える場合は優先度の低い angle を自動スキップ (contrarian > historical > empirical > practitioner > academic の優先順)

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

### Query Variant Axis（クエリ構造の多様化）

`--angles` が **視点の多様化** (何を問うか) を担うのに対し、Query Variant Axis は **クエリ構造の多様化** (どう問うか) を担う。両者は直交し、組み合わせて使える。

> 出典: Onyx DeepResearch Stack 6-stage retrieval pipeline (Akshay Pachaar 2026-04) — keyword 検索は brittle、vector 類似度は multi-hop で破綻する。並列な query variant 生成で recall を上げる。

| variant | 意図 | 有効な場面 |
|---------|------|-----------|
| `semantic` | 意味的言い換え（同義語・別の表現） | 正しい用語を知らない、ドメイン用語の揺れ |
| `keyword` | 具体的なキーワード列挙 | ピンポイントの識別子・固有名詞・エラーメッセージ |
| `broad` | 抽象化した広域クエリ | 関連領域の地図を描く、文脈取得 |

### 使い分け

- **単一サブタスク**: variant は **不要** (オーバーヘッドが利益を上回る)
- **recall 重視のサブタスク**: 「関連文献を網羅したい」「特定の主張を裏付けたい」→ 3 variant を並列発行
- **--angles と併用**: 各 angle 内で recall が弱いと感じたら variant を展開。例: `academic` angle × `semantic` variant + `keyword` variant

### 実装

variant 並列は **Step 3 Execute 内のサブタスクプロンプト** で表現する。1 サブタスク = 1 variant として Agent ツール呼び出しを増やすのではなく、サブタスクプロンプト内で「以下の 3 つのクエリを並列で発行してください」と指示する（Agent 数を増やすと統合コストが伸びる）。

```
以下のトピックを 3 つの query variant で並列検索してください:
1. semantic: {topic を意味的に言い換えた 2-3 表現}
2. keyword: {topic の核となるキーワード + 関連識別子 5-10 個}
3. broad: {topic を含む上位カテゴリの広域クエリ}

それぞれの結果を Reciprocal Rank Fusion 的に統合し、上位のヒットを採用してください。
```

### 棄却した代替案

- **mandatory な 3 variant 全採用**: Gemini 指摘で「狭い検索空間で token 30% を無駄焼却」するリスクあり。advisory のみとする
- **6-stage retrieval pipeline 全採用**: CLI harness には over-engineering。LLM selection ステップのみ Aggregate に軽量採用（次節 Step 4）

## Step 3: Execute

### フレーミング注入

各サブタスクのプロンプト先頭に **Async フレーミング**（`references/subagent-framing.md`）を付加する:

> あなたは非同期サブエージェントです。結果はユーザーに直接報告されます。
> 背景・分析・結論を含む自己完結的なレポートを作成してください。ソースや根拠を明記してください。

### ツール（各モデル共通）

- **MCP ツール**: brave-search, context7, scite（インストール済みの場合）
- **Scite MCP**: 学術文献検索・Smart Citations・引用グラフ分析。学術トピックのサブタスクで積極的に使用
- **WebFetch/WebSearch**: 標準ツール (URL 取得経路は `references/web-fetch-policy.md` に従う — trusted 外ドメインはサイレント truncation 回避のため `curl + defuddle` 推奨)

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
codex exec --skip-git-repo-check -m gpt-5.5 \
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

### Pre-synthesis Reflection & LLM Selection（on-demand）

> 出典: Onyx DeepResearch pipeline (Akshay Pachaar 2026-04) — retrieval と synthesis の間に LLM selection 段階を挟まないと hallucination が混入する。ただし全セッションで強制すると token 30% を無駄焼却する (Gemini 周辺調査)。したがって **on-demand trigger** のみ採用する。

Aggregate 本体に入る前に、以下の 2 条件のいずれかを満たす場合だけ軽量な reflection + selection を実施する。

#### Trigger 条件（いずれか 1 つ）

- **Coverage gap 検出**: Step 2 Plan のサブ目標のうち、未回答 / 単一ソースのみのものが 1 つ以上
- **矛盾検出**: サブタスク間でエビデンス強度が拮抗する矛盾が 1 つ以上
- **新方向の兆候**: サブタスク出力に Plan 段階で想定していなかった重要トピックが現れた

上記いずれも該当しない場合は reflection をスキップし、直接 Aggregate 品質基準に進む。

#### Reflection Checklist（構造化出力）

trigger 条件に当たった場合、以下の 4 項目で構造化出力する:

| 項目 | 内容 |
|------|------|
| **Coverage** | Plan のどのサブ目標が回答済み / 部分的 / 未回答か |
| **Gaps** | 未解決の論点、単一ソースのみの主張、エビデンス不足の箇所 |
| **New directions** | 当初 Plan に無かったが重要と判明したトピック（追加調査候補） |
| **Converge?** | 追加サイクルで新情報が得られる見込みがあるか（yes/no + 根拠 1 行） |

`Converge? = no` なら Aggregate に進む。`yes` ならユーザーに「追加サイクルを回すか」を確認する（自動で回さない — token budget を守る）。

#### LLM Selection（軽量）

reflection で抽出した gap / 矛盾について、synthesis 前に原文 chunk を LLM で選別する軽量ステップ。並列エージェントが返した全 chunk を読み直すのではなく、**関係する gap / 矛盾の chunk のみ** を再評価する:

1. gap / 矛盾に関係するサブタスク出力から最大 10 chunk を抽出
2. LLM に「以下の主張に直接関係する chunk だけ保持、残りは破棄」と指示
3. 選別後の chunk だけを Aggregate の quality filter に渡す

**mandatory 化しない理由**: Gemini の指摘によれば LLM selection は hallucination を 40-60% 削減するが +15-30 秒の latency を伴う。全サブタスクで強制すると全体 latency が倍増する。

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
| **Citation Merge & Renumber** | 並列エージェントが独立に付けた citation 番号を統合レポート用に renumber する。同一ソース URL は 1 番号に統合、残りを連続採番。inline citation をテキスト中で置換。全主張が最終 citation に辿れることを確認（orphan citation 禁止）。出典: Onyx DeepResearch の citation integrity 原則 |

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
