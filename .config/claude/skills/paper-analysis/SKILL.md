---
name: paper-analysis
description: |
  複数の学術論文を構造的に分析するワークフロー。個別要約ではなく、論文群の関係性・矛盾・コンセンサス・
  ギャップ・暗黙仮定を多角的に抽出し、階層的な知識地図を生成する。
  Triggers: '論文分析', '文献レビュー', 'paper analysis', 'literature review', '論文群を分析',
  '複数論文', 'systematic review', 'papers uploaded'.
  Do NOT use for: 単一記事の要約（直接要約で十分）、記事の知見統合（use /absorb）、
  対話型学習（use /deep-read）、文献ノート作成（use /digest）。
origin: self
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
metadata:
  pattern: pipeline
---

# Paper Analysis — 複数論文の構造的分析

複数の学術論文を入力し、9ステップの分析パイプラインで構造化レポートを生成する。

## Trigger

`/paper-analysis {論文群}` で起動。

入力形式:
- PDF ファイルパス（複数可）
- URL（arXiv, PubMed, DOI リンク等）
- テキスト貼り付け
- Obsidian ノートパス

## Safety Constraints

論文分析固有のリスクに対する安全機構:

| リスク | 対策 | 適用ステップ |
|--------|------|-------------|
| 幽霊引用（存在しない論文の生成） | DOI/URL の原典照合を必須化 | Step 2, 3 |
| Lost in the Middle（長文中央部の精度低下） | 20本超はグループ分割→統合 | 全ステップ |
| Sycophancy（矛盾を調和させる傾向） | Codex でセカンドオピニオン | Step 4, 9 |
| 再現性の欠如 | 分析パラメータをレポートに記録 | レポート出力時 |

## Workflow

```
/paper-analysis {論文群}
  Step 0: Intake        → 論文の正規化・メタデータ抽出     [Haiku/Gemini]
  Step 1: Landscape     → 論文間の関係性マッピング         [Sonnet]
  Step 2: Contradiction → 矛盾検出 + WHY 分析             [Sonnet + Scite]
  Step 3: Citation      → 概念の系譜追跡                  [Scite MCP]
  Step 4: Synthesis     → 信じている/争点/未解決 3層統合    [Opus]
  Step 5: Gap Scan      → 未回答問いの特定 + 原因診断      [Opus]
  Step 6: Method Audit  → 手法分類・偏り・弱点             [Sonnet]
  Step 7: Knowledge Map → 階層的知識地図                   [Opus]
  Step 8: So What       → 非専門家向け3点要約              [Opus]
  Step 9: Assumptions   → 暗黙仮定抽出 + 反事実分析        [Opus + Codex]
```

### ステップの選択実行

全9ステップを実行する必要はない。ユーザーが特定ステップを指定した場合はそれだけ実行する:
- `/paper-analysis --steps 1,4,8` — Landscape + Synthesis + So What のみ
- `/paper-analysis --quick` — Step 0,1,4,8 のみ（クイックモード）
- `/paper-analysis` — 全ステップ実行（デフォルト）

## Step 0: Intake — 論文の正規化 [Haiku/Gemini に委譲]

入力された論文群を正規化し、分析可能な形に整える。

### 委譲先の選択
- PDF/URL 5本以下 → `Agent(model: "haiku")` で個別取得+メタデータ抽出
- PDF/URL 6本以上 or リポジトリ → Gemini（1M コンテキスト）

### 抽出するメタデータ
各論文について:
- **著者** / **年** / **タイトル** / **DOI or URL**
- **核心主張**: 1文で
- **研究手法**: survey / experiment / simulation / meta-analysis / case-study / theoretical
- **分野キーワード**: 2-3語

### チャンキング判定
- 論文20本以下 → 全体を1コーパスとして分析
- 論文21本以上 → テーマ別に3-5グループに分割し、各グループを分析後に統合

### 出力
ユーザーにメタデータ一覧を提示し、確認を得る:

```
## 論文コーパス: {topic} ({N}本)

| # | 著者(年) | タイトル | 手法 | 核心主張 |
|---|---------|---------|------|---------|
| 1 | {author} ({year}) | {title} | {method} | {claim} |
```

**ユーザーの承認なしに Step 1 に進んではいけない。**

## Step 1: Landscape — 関係性マッピング [Sonnet に委譲]

`Agent(model: "sonnet")` に以下を依頼:

> 以下の論文メタデータを分析し、論文群の構造的関係性をマッピングしてください。
> 個別の要約はしないでください。関係性のみを出力してください。
>
> 1. **共有仮説クラスター**: 共通の前提や仮説を持つ論文をグループ化
> 2. **対立軸**: 意見が分かれている論点と、各陣営の論文
> 3. **時系列的発展**: 概念がどう進化してきたか
> 4. **矛盾フラグ**: 明らかに矛盾する主張のペア（Step 2 で詳細分析）

出力形式: テーブル + 箇条書き。散文禁止。

## Step 2: Contradiction — 矛盾検出 + WHY 分析 [Sonnet + Scite]

`Agent(model: "sonnet")` に以下を依頼。Scite MCP が利用可能な場合は引用コンテキスト（support/contradict/mention）を活用:

> Step 1 で検出された矛盾フラグと、論文全体を精査し、矛盾を網羅的に抽出してください。
>
> 各矛盾について:
> - **主張A**: 論文名 + 主張内容
> - **主張B**: 論文名 + 主張内容
> - **WHY**: なぜ矛盾するのか（手法の違い / データセットの違い / 時代の違い / 定義の違い）
> - **解決可能性**: 条件を分ければ両立するか、根本的に対立するか
>
> テーブル形式で出力。

**原典照合ゲート**: 矛盾として報告する際は、各主張が論文のどの部分（セクション/ページ）に記載されているか参照を付けること。参照なしの矛盾報告は無効。

## Step 3: Citation — 概念の系譜追跡 [Scite MCP]

論文群から最頻出の3-5概念を特定し、各概念の知的系譜を追跡する。

Scite MCP が利用可能な場合:
- Smart Citations で support/contradict 関係を取得
- 引用グラフから系譜を構築

Scite MCP が利用不可の場合:
- 論文本文内の引用関係から手動で系譜を構築（精度は低下）

各概念について:
- **導入者**: 誰が最初に提唱したか
- **批判者**: 誰が異議を唱えたか + 批判の内容
- **精緻化**: 誰がどう改良したか
- **現在の合意**: コンセンサスがあるか、まだ争点か

**原典照合ゲート**: 引用関係は論文本文の参照リストで検証可能なもののみ報告。LLM の記憶に基づく引用は `[unverified]` タグを付ける。

## Step 4: Synthesis — 3層統合 [Opus]

Step 1-3 の結果を統合し、分野全体の知識状態を3層で記述する。**個別論文の要約は含めない。**

| 層 | 内容 |
|----|------|
| **Consensus** | 分野が集合的に信じていること。複数論文の証拠で裏付け |
| **Contested** | 活発に議論されている争点。各陣営の論拠 |
| **Unresolved** | 証拠不足で結論が出ていない問い |

最後に: **この分野で最も重要な未回答の問いを1つ** 特定する。

400語以内。修飾語・ヘッジ禁止。

### Sycophancy 防止
Step 2 の矛盾が Synthesis で「調和」されていないか自己チェック。矛盾は Contested 層に残すこと。

## Step 5: Gap Scan — 未回答問いの特定 [Opus]

論文群が **完全には答えていない** 5つの研究問いを特定する。

各ギャップについて:
- **問い**: 未回答の研究問い
- **なぜ存在するか**: too hard（技術的に困難）/ too niche（ニッチすぎる）/ overlooked（見落とされている）
- **最も接近した論文**: この問いに最も近い答えを出している論文
- **必要な手法**: ギャップを埋めるために必要な研究手法

## Step 6: Method Audit — 手法分類・偏り検出 [Sonnet に委譲]

`Agent(model: "sonnet")` に以下を依頼:

> 以下の論文群の研究手法を分析してください。
>
> 1. **手法分類**: 各論文を survey / experiment / simulation / meta-analysis / case-study / theoretical に分類し、分布を示す
> 2. **支配的手法**: この分野で最も使われている手法とその理由
> 3. **過小利用手法**: 使われるべきだが使われていない手法
> 4. **最も弱い手法**: 手法論上の弱点が顕著な論文とその理由

テーブル形式で出力。

## Step 7: Knowledge Map — 階層的知識地図 [Opus]

Step 1-6 の結果を統合し、分野の知識構造を階層的アウトラインで表現する。**散文禁止。**

```
## Knowledge Map: {topic}

### Central Claim
{分野全体が軌道する中核主張}

### Supporting Pillars (3-5)
1. {確立されたサブ主張} — 根拠: {論文名}
2. ...

### Contested Zones (2-3)
1. {活発な議論} — {陣営A} vs {陣営B}
2. ...

### Frontier Questions (1-2)
1. {誰も解いていない問い}

### Must-Read Papers (3)
1. {論文名} — {なぜ最初に読むべきか}
2. ...
```

## Step 8: So What — 非専門家向け3点要約 [Opus]

分野全体を5分で説明する想定で、以下の3点のみ出力する:

1. **この分野が証明した1文**: 学術的修飾語なし。直球で
2. **正直に認める限界**: この分野がまだ知らないこと
3. **最も重要な現実世界への含意**: 1つだけ。抽象論禁止

**ルール**: ジャーゴン禁止。ヘッジ禁止。学術的修辞禁止。

## Step 9: Assumptions — 暗黙仮定の抽出 + 反事実分析 [Opus + Codex]

### Opus: 仮定抽出

論文群の **多数派が共有しているが、明示的に検証していない仮定** を列挙する。

各仮定について:
- **仮定の内容**: 明示的に述べる
- **依存論文**: この仮定に最も依存している1-2本
- **反事実**: この仮定が誤りだった場合に分野全体に何が起こるか

### Codex: セカンドオピニオン

Opus の仮定リストを `codex-rescue` に渡し、以下を批評してもらう:
- 見落とした仮定はないか
- 反事実分析は十分か
- 仮定の重要度ランキングは適切か

## Report Generation

全ステップ完了後、分析レポートを生成する。

**テンプレート**: `templates/paper-analysis-report.md`

保存先: `docs/research/YYYY-MM-DD-{topic-slug}-paper-analysis.md`

## Chaining

- **知見の統合**: 分析結果を `/absorb` で自セットアップに取り込み
- **深い理解**: 特定論文を `/deep-read` で対話的に掘り下げ
- **Obsidian 保存**: `/digest` で個別論文を Literature Note 化
- **追加調査**: Gap Scan の結果を `/research` で深掘り
