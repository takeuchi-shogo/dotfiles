# Tacit Knowledge Analyzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** セッションログから暗黙知を自動抽出し、3層構造で蓄積・進化させるパイプラインスキルを実装する

**Architecture:** 7ステージパイプライン（Ingest → Detect → Integrate → Propose → Debate → Apply）を1つのスキルとして実装。データストアは `.claude/tacit-knowledge/` 配下の JSONL + Markdown。各ステージは独立した関数としてスキル内で定義し、ユーザー対話ポイントで一時停止する。

**Tech Stack:** Claude Code Skill (Markdown + LLM prompt), JSONL data store, Agent Teams (subagent)

**Spec:** `docs/superpowers/specs/2026-03-22-tacit-knowledge-analyzer-design.md`

---

## File Structure

```
.config/claude/skills/analyze-tacit-knowledge/
├── SKILL.md                          # メインスキル定義（パイプライン全体のオーケストレーション）
├── references/
│   ├── detection-signals.md          # Stage 2: 齟齬検出シグナル一覧
│   ├── extraction-prompt.md          # Stage 3: 暗黙知抽出用プロンプトテンプレート
│   ├── integration-rules.md          # Stage 4: 突合判定ルール
│   ├── debate-personas.md            # Stage 6: Agent Teams ペルソナ定義
│   └── knowledge-schema.md           # knowledge-base.jsonl のスキーマ定義
└── templates/
    ├── analysis-report.md            # 分析結果レポートテンプレート
    └── proposal.md                   # 反映提案テンプレート

.config/claude/commands/
└── analyze-tacit-knowledge.md        # スラッシュコマンド定義

.claude/tacit-knowledge/              # データストア（git管理対象）
├── knowledge-base.jsonl              # 全知見のindex
├── analysis-history/                 # 過去の分析結果
└── debates/                          # Agent Teams議論ログ
```

**設計判断: データストアのパス**
- `.claude/tacit-knowledge/` はdotfilesリポジトリ内に配置（symlink経由で `~/.claude/tacit-knowledge/` としてもアクセス可能）
- knowledge-base.jsonl は git 管理対象とする（知見の進化を履歴で追跡できる）
- analysis-history/ と debates/ も git 管理対象（導出過程の記録として価値がある）

---

## Task 1: データストアの初期化と knowledge-base.jsonl スキーマ定義

**Files:**
- Create: `.config/claude/skills/analyze-tacit-knowledge/references/knowledge-schema.md`
- Create: `.claude/tacit-knowledge/knowledge-base.jsonl`
- Create: `.claude/tacit-knowledge/analysis-history/.gitkeep`
- Create: `.claude/tacit-knowledge/debates/.gitkeep`

- [ ] **Step 1: knowledge-schema.md を作成**

```markdown
# Knowledge Base Schema

## knowledge-base.jsonl

1行1エントリの JSONL 形式。各エントリは1つの暗黙知を表す。

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | 一意ID。形式: `tk-YYYYMMDD-NNN` |
| knowledge | string | yes | 暗黙知の内容（自然言語） |
| gap | string | yes | AIの出力とユーザーの期待のズレ |
| user_correction | string | yes | ユーザーの修正指示 |
| domain | string | yes | ドメインカテゴリ（例: `content-creation/tone`） |
| layer | number | yes | 知識レイヤー（2: スキルルール/個別の学び, 3: 上位原則） |
| confidence | number | yes | 確信度 0.0-1.0 |
| sources | string[] | yes | 検出元セッションID |
| created | string | yes | 作成日 ISO 8601 |
| updated | string | yes | 更新日 ISO 8601 |
| applied_to | string[] | no | 反映先ファイルパス |
| status | string | yes | `active`, `promoted`, `superseded` |

### Example

\`\`\`jsonl
{"id":"tk-20260322-001","knowledge":"受け手に判断を委ねるスタンス。処方的表現は信頼を損なう","gap":"AIが処方的トーンで書いた（〜すべき）","user_correction":"確信の表明だけで止める。行動指示はしない","domain":"content-creation/tone","layer":2,"confidence":0.85,"sources":["session-abc123"],"created":"2026-03-22","updated":"2026-03-22","applied_to":[],"status":"active"}
\`\`\`

### Verdict Types (Stage 4 Integration)

| Verdict | Condition | Action |
|---------|-----------|--------|
| new | 既存indexに類似なし | 新規エントリ追加 |
| reinforce | 同domain・同方向の既存あり | confidence上昇、sources追加 |
| contradict | 既存と逆方向 | フラグ立て、Stage 6議論対象 |
| promote | 同domainの知見3件以上 | Layer 3昇格候補 |
```

- [ ] **Step 2: データストアディレクトリとファイルを作成**

```bash
mkdir -p /Users/takeuchishougo/dotfiles/.claude/tacit-knowledge/analysis-history
mkdir -p /Users/takeuchishougo/dotfiles/.claude/tacit-knowledge/debates
touch /Users/takeuchishougo/dotfiles/.claude/tacit-knowledge/analysis-history/.gitkeep
touch /Users/takeuchishougo/dotfiles/.claude/tacit-knowledge/debates/.gitkeep
```

空の knowledge-base.jsonl を作成（中身なし、ファイルだけ存在）:

```bash
touch /Users/takeuchishougo/dotfiles/.claude/tacit-knowledge/knowledge-base.jsonl
```

- [ ] **Step 3: Commit**

```bash
git add .config/claude/skills/analyze-tacit-knowledge/references/knowledge-schema.md
git add .claude/tacit-knowledge/
git commit -m "$(cat <<'EOF'
🔧 chore: initialize tacit-knowledge data store and schema

knowledge-base.jsonl schema definition and empty data store structure
for the tacit knowledge analyzer pipeline.
EOF
)"
```

---

## Task 2: Stage 2 齟齬検出シグナル定義

**Files:**
- Create: `.config/claude/skills/analyze-tacit-knowledge/references/detection-signals.md`

- [ ] **Step 1: detection-signals.md を作成**

```markdown
# Detection Signals - Stage 2

セッションログから認識齟齬を検出するためのシグナル定義。

## Signal Categories

### 1. 明示的修正指示 (Explicit Correction)

ユーザーが直接的にAIの出力を否定・修正する発言。

**検出キーワード:**
- 否定: 「違う」「そうじゃない」「そうではなく」「ではなくて」「じゃなくて」
- 修正要求: 「〜に変えて」「〜にして」「〜に修正して」「直して」「やり直して」
- 不一致: 「イメージと違う」「求めてるのは」「そういうことじゃない」

**confidence:** 0.9（明示的修正は暗黙知の直接的な表出）

### 2. やり直し (Redo)

同一ファイルへの複数回 Edit がユーザーフィードバックを挟んで発生。

**検出方法:**
- 同一ファイルパスに対する Edit/Write tool_use が2回以上
- 間にユーザーメッセージ（type: "user", content: string）が存在
- tool_result ではなく、ユーザーの自発的なメッセージであること

**confidence:** 0.8

### 3. 方針転換 (Direction Change)

ユーザーがアプローチの変更を指示。

**検出キーワード:**
- 「やっぱり」「こっちのアプローチで」「方針変更」「別の方法で」
- 「前のやつに戻して」「最初の案で」

**confidence:** 0.7（方針転換は暗黙知の場合もあるが、単なる試行錯誤の場合もある）

### 4. 不満・苛立ち (Frustration)

ユーザーが繰り返しの修正に苛立ちを示す。

**検出キーワード:**
- 「毎回」「何度も言ってる」「さっきも言った」「同じことを」
- 「いつも」「また同じ」

**confidence:** 0.95（繰り返しの修正は高確度で暗黙知のギャップを示す）

### 5. 早期中断 (Early Interruption)

ユーザーが assistant の出力途中で割り込み。

**検出方法:**
- assistant メッセージの直後に、tool_result ではないユーザーメッセージ
- assistant メッセージの stop_reason が "end_turn" ではない、または出力が短い

**confidence:** 0.6（中断の理由は様々なので低め）

### 6. 追加説明 (Supplementary Explanation)

ユーザーが長い補足説明を追加。AIの前提理解が不足していた兆候。

**検出方法:**
- ユーザーメッセージの文字数が 200 文字以上
- 直前に assistant の出力がある（初回の指示ではない）
- メッセージ内に背景説明、前提条件、コンテキストの補足が含まれる

**confidence:** 0.65

## Detection Output Format

各検出ポイントは以下の構造で Stage 3 に渡す:

\`\`\`yaml
- signal_type: "explicit_correction"
  confidence: 0.9
  context:
    before: "assistant の直前の出力（関連部分を抜粋）"
    user_message: "ユーザーの修正指示（全文）"
    after: "修正後の assistant の出力（あれば）"
  session_id: "session-xxx"
  timestamp: "2026-03-22T10:30:00Z"
\`\`\`
```

- [ ] **Step 2: Commit**

```bash
git add .config/claude/skills/analyze-tacit-knowledge/references/detection-signals.md
git commit -m "$(cat <<'EOF'
📝 docs: add detection signals reference for Stage 2

6 signal categories with keywords, detection methods, and confidence
levels for identifying tacit knowledge gaps in session logs.
EOF
)"
```

---

## Task 3: Stage 3 暗黙知抽出プロンプトテンプレート

**Files:**
- Create: `.config/claude/skills/analyze-tacit-knowledge/references/extraction-prompt.md`

- [ ] **Step 1: extraction-prompt.md を作成**

```markdown
# Extraction Prompt - Stage 3

Stage 2 で検出した齟齬ポイントから暗黙知を抽出するためのプロンプトテンプレート。

## Prompt Template

以下の齟齬ポイントを分析し、ユーザーの暗黙知を抽出してください。

### Input

{detection_points}

### Instructions

各齟齬ポイントについて、以下の3つの観点で分析してください:

1. **何がズレていたか（gap）**: AIの出力と修正後を比較し、具体的なズレを特定
2. **なぜそう判断したか（implicit_knowledge）**: 修正指示の言葉から、ユーザーが持つ暗黙の判断基準を推測
3. **どのドメインか（domain）**: この知見が属するドメインカテゴリを分類

### Domain Categories

以下のカテゴリから選択するか、新しいカテゴリを提案してください:

- `content-creation/tone` — 文章のトーン・表現
- `content-creation/structure` — 文章の構成・構造
- `content-creation/audience` — 読者・受け手への配慮
- `communication/stakeholder` — ステークホルダーとのコミュニケーション
- `communication/information-filtering` — 情報の取捨選択
- `decision-making/priority` — 優先順位の判断
- `decision-making/boundary` — 自動化と人間判断の境界
- `workflow/process` — 作業プロセス・手順
- `quality/standard` — 品質基準・品質の肌感覚

### Grouping Rule

同一セッション内で同じ domain・同じ種類の修正が複数回出現した場合、1つの暗黙知としてグルーピングしてください。confidence はグループ内の最高値を採用し、すべての齟齬ポイントを evidence として含めてください。

### Output Format

\`\`\`yaml
extracted_knowledge:
  - id: tk-{date}-{seq}
    gap: "{AIの出力とユーザーの期待のズレ}"
    user_correction: "{ユーザーの修正指示の要約}"
    implicit_knowledge: "{抽出された暗黙知}"
    domain: "{domain category}"
    confidence: {0.0-1.0}
    evidence:
      - signal_type: "{detection signal type}"
        context: "{齟齬ポイントの要約}"
\`\`\`
```

- [ ] **Step 2: Commit**

```bash
git add .config/claude/skills/analyze-tacit-knowledge/references/extraction-prompt.md
git commit -m "$(cat <<'EOF'
📝 docs: add extraction prompt template for Stage 3

Prompt template for extracting tacit knowledge from detected gaps,
including domain categories and grouping rules.
EOF
)"
```

---

## Task 4: Stage 4 突合判定ルールと Stage 5 提案テンプレート

**Files:**
- Create: `.config/claude/skills/analyze-tacit-knowledge/references/integration-rules.md`
- Create: `.config/claude/skills/analyze-tacit-knowledge/templates/proposal.md`

- [ ] **Step 1: integration-rules.md を作成**

```markdown
# Integration Rules - Stage 4

抽出した暗黙知を既存の knowledge-base.jsonl と突合するためのルール。

## Matching Algorithm

### Step 1: 類似度判定

新規抽出した知見と既存エントリを以下の基準で比較:

1. **domain 一致**: 同じ domain カテゴリかどうか
2. **意味的類似**: knowledge フィールドの意味的な近さ（LLM判定）
3. **方向性**: 同じ方向の知見か、矛盾する知見か

### Step 2: Verdict 判定

| Verdict | 条件 | アクション |
|---------|------|-----------|
| `new` | 既存indexに domain 一致かつ意味的に類似するエントリがない | 新規エントリとして追加候補に |
| `reinforce` | 既存エントリと同 domain・同方向 | 既存エントリの confidence を `min(existing + 0.05, 1.0)` に更新、sources に新セッションID追加 |
| `contradict` | 既存エントリと同 domain だが逆方向 | 両エントリにフラグ立て、Stage 6 の議論対象に |
| `promote` | 同 domain の active エントリが3件以上 | Layer 3（上位原則）への昇格候補としてマーク |

### Step 3: 昇格候補の判定

以下の条件をすべて満たす場合、昇格候補とする:
- 同一 domain に active な Layer 2 エントリが3件以上
- 各エントリの confidence がすべて 0.7 以上
- 矛盾するエントリ（contradict verdict）がない

## Prompt for LLM-based Matching

既存の knowledge-base.jsonl エントリと新規抽出した知見を比較し、各知見について verdict を判定してください。

### Input
- 新規知見: {extracted_knowledge}
- 既存エントリ: {existing_entries}

### Output
\`\`\`yaml
verdicts:
  - knowledge_id: "tk-xxx"
    verdict: "new|reinforce|contradict|promote"
    matched_entry_id: "tk-yyy"  # reinforce/contradict の場合
    reason: "判定理由"
\`\`\`
```

- [ ] **Step 2: proposal.md テンプレートを作成**

```markdown
# Proposal Template - Stage 5

## Proposal {n}/{total}: {type}

- **Target:** `{file_path}`
- **Type:** {rule_addition | learning_creation | principle_creation | principle_update}
- **Content:**

{proposed_content}

- **Evidence:** {source_sessions} で同一修正が {count} 回
- **Confidence:** {confidence}
- **Knowledge IDs:** {related_knowledge_ids}

---

### Layer Mapping

| Knowledge Layer | Type | Target Pattern |
|----------------|------|----------------|
| Layer 2: スキルルール | rule_addition | 対象スキルの SKILL.md にルール追記 |
| Layer 2: 個別の学び | learning_creation | `learnings/{date}-{topic}.md` に新規作成 |
| Layer 3: 上位原則 | principle_creation | `principles/{topic}.md` に新規作成 |
| Layer 3: 上位原則更新 | principle_update | 既存の上位原則ドキュメントに追記 |
```

- [ ] **Step 3: Commit**

```bash
git add .config/claude/skills/analyze-tacit-knowledge/references/integration-rules.md
git add .config/claude/skills/analyze-tacit-knowledge/templates/proposal.md
git commit -m "$(cat <<'EOF'
📝 docs: add integration rules (Stage 4) and proposal template (Stage 5)

Matching algorithm with 4 verdicts (new/reinforce/contradict/promote)
and structured proposal template for knowledge application.
EOF
)"
```

---

## Task 5: Stage 6 Agent Teams ペルソナ定義

**Files:**
- Create: `.config/claude/skills/analyze-tacit-knowledge/references/debate-personas.md`

- [ ] **Step 1: debate-personas.md を作成**

```markdown
# Debate Personas - Stage 6

昇格候補・矛盾知見に対して多角的に検証する Agent Teams のペルソナ定義。

## Trigger Conditions

以下のいずれかの条件を満たす場合に Stage 6 を実行:
- Stage 4 で `promote` verdict が1件以上
- Stage 4 で `contradict` verdict が1件以上

いずれの条件も満たさない場合、Stage 6 をスキップして Stage 7 に進む。

## Personas

### 1. 実務者 (Practitioner)

**Role:** 現場での実用性を検証する
**Perspective:** 「このルールは日々の業務で実際に機能するか？例外が多すぎて形骸化しないか？」
**Focus:**
- ルールの適用頻度と実用性
- 例外ケースの洗い出し
- 既存のワークフローとの整合性

### 2. 抽象化担当 (Abstractor)

**Role:** 個別ルールから上位原則を導出する
**Perspective:** 「これらの個別ルールに共通する、より深い判断基準は何か？」
**Focus:**
- 複数の Layer 2 知見を貫く構造の発見
- 適切な抽象度の判断（具体的すぎず、空疎にならない）
- 原則として言語化する際の表現

### 3. 反証担当 (Devil's Advocate)

**Role:** 導出された原則の脆弱性を検証する
**Perspective:** 「この原則が逆効果になるケースは？盲目的に従うとどんな問題が起きるか？」
**Focus:**
- 原則の適用限界
- 矛盾する状況の特定
- 過度な一般化のリスク

### 4. 統合担当 (Integrator)

**Role:** 既存の上位原則との整合性を確認する
**Perspective:** 「既存の原則体系にどう位置づけるか？矛盾や重複はないか？」
**Focus:**
- 既存の principles/ ドキュメントとの整合性
- 原則間の優先順位
- 体系としての一貫性

### 5. ユーザー代弁者 (User Advocate)

**Role:** ユーザーの意図を正しく捉えているか確認する
**Perspective:** 「この抽象化はユーザーの本来の意図を正しく反映しているか？過剰解釈していないか？」
**Focus:**
- 元の修正指示との整合性
- 過剰解釈・過少解釈の検出
- ユーザーが「これは自分の考えだ」と認められるか

## Debate Output Format

\`\`\`markdown
## Debate Result

### Discussed Items
- {knowledge_ids and their proposed promotions/contradictions}

### Consensus
- **Verdict:** promote | defer | revise | reject
- **Derived Principle:** "{導出された上位原則}" (promote の場合)
- **Reasoning:** {各ペルソナの意見の要約と合意形成の過程}

### Dissenting Views
- {合意に至らなかった意見とその理由}
\`\`\`
```

- [ ] **Step 2: Commit**

```bash
git add .config/claude/skills/analyze-tacit-knowledge/references/debate-personas.md
git commit -m "$(cat <<'EOF'
📝 docs: add Agent Teams debate personas for Stage 6

5 personas (Practitioner, Abstractor, Devil's Advocate, Integrator,
User Advocate) with trigger conditions and output format.
EOF
)"
```

---

## Task 6: 分析レポートテンプレート

**Files:**
- Create: `.config/claude/skills/analyze-tacit-knowledge/templates/analysis-report.md`

- [ ] **Step 1: analysis-report.md を作成**

```markdown
# Analysis Report - {date}

**Session(s):** {session_ids}
**Period:** {period}
**Analyzer version:** 1.0

---

## Stage 2: Detection Summary

| Signal Type | Count | Avg Confidence |
|------------|-------|----------------|
| {signal_type} | {count} | {avg_confidence} |

**Total detection points:** {total}

## Stage 3: Extracted Knowledge

{extracted_knowledge_list}

## Stage 4: Integration Results

| Verdict | Count | Details |
|---------|-------|---------|
| New | {count} | {brief} |
| Reinforce | {count} | {brief} |
| Contradict | {count} | {brief} |
| Promote | {count} | {brief} |

## Stage 5: Proposals

{proposals_list}

## Stage 6: Debate Results (if applicable)

{debate_summary}

## Stage 7: Applied Changes

| Action | Target | Status |
|--------|--------|--------|
| {action} | {file_path} | {approved/rejected} |

---

## Knowledge Base Statistics

- Total entries: {total_entries}
- Layer 2: {layer2_count}
- Layer 3: {layer3_count}
- Domains: {domain_list}
- Last promotion: {last_promotion_date}
```

- [ ] **Step 2: Commit**

```bash
git add .config/claude/skills/analyze-tacit-knowledge/templates/analysis-report.md
git commit -m "$(cat <<'EOF'
📝 docs: add analysis report template

Structured template for recording full pipeline execution results,
from detection through application.
EOF
)"
```

---

## Task 7: スラッシュコマンド定義

**Files:**
- Create: `.config/claude/commands/analyze-tacit-knowledge.md`

- [ ] **Step 1: コマンドファイルを作成**

```markdown
---
description: セッションログから暗黙知を抽出し、3層構造で蓄積・進化させる
argument-hint: "[latest] | [period:Nd] | [session:ID] | [status]"
---

# Tacit Knowledge Analyzer

Analyze session logs to extract and accumulate tacit knowledge: $ARGUMENTS

Use the `analyze-tacit-knowledge` skill to execute the 7-stage pipeline.
```

- [ ] **Step 2: Commit**

```bash
git add .config/claude/commands/analyze-tacit-knowledge.md
git commit -m "$(cat <<'EOF'
🔧 chore: add /analyze-tacit-knowledge slash command

Routes to the analyze-tacit-knowledge skill with argument passthrough.
EOF
)"
```

---

## Task 8: メインスキル SKILL.md の実装

**Files:**
- Create: `.config/claude/skills/analyze-tacit-knowledge/SKILL.md`

これがパイプライン全体のオーケストレーションを行うメインファイル。

- [ ] **Step 1: SKILL.md を作成**

```markdown
---
name: analyze-tacit-knowledge
description: >
  セッションログから暗黙知を自動抽出し、3層構造（ログ要約 / スキルルール・個別の学び / 上位原則）で蓄積・進化させるパイプラインスキル。
  蓄積型アーキテクチャ: 実行するたびに過去の分析結果と突合し、知見の体系を進化させる。
  Triggers: '/analyze-tacit-knowledge', '暗黙知', 'tacit knowledge', '認識齟齬', 'セッション分析',
  '知見抽出', 'knowledge extraction', '暗黙知の言語化'.
  Do NOT use for: 単純なセッションログの要約（daily-report を使用）、
  スキルの新規作成（skill-creator を使用）。
metadata:
  pattern: analyzer
allowed-tools: "Read, Write, Edit, Bash, Glob, Grep, Agent"
argument-hint: "[latest] | [period:Nd] | [session:ID] | [status]"
---

# Tacit Knowledge Analyzer

セッションログから暗黙知を抽出し、3層構造で蓄積するパイプライン。

## Pipeline Overview

```
Stage 1: Ingest   → Stage 2: Detect   → Stage 3: Extract
    → Stage 4: Integrate → Stage 5: Propose
    → Stage 6: Debate    → Stage 7: Apply
```

## Execution

### Arguments

| Argument | Description |
|----------|-------------|
| `latest` (default) | 最新セッション1件を分析 |
| `period:Nd` | 直近N日間の全セッションを分析（例: `period:7d`） |
| `session:ID` | 特定セッションIDを分析 |
| `status` | 現在の知見蓄積状況を表示 |

### Status Mode

`status` が指定された場合、パイプラインを実行せず knowledge-base.jsonl の統計を表示:

1. Read `.claude/tacit-knowledge/knowledge-base.jsonl`
2. 以下を集計して表示:
   - 総エントリ数
   - Layer 別分布（Layer 2 / Layer 3）
   - Domain 別分布
   - 直近の昇格イベント
   - 直近の分析日時
3. 終了

### Pipeline Mode

#### Stage 1: Ingest

1. 引数に応じてセッションログファイルを特定:
   - `latest`: `~/.claude/projects/` 配下の最新セッションディレクトリを特定
   - `period:Nd`: 直近N日のタイムスタンプを持つセッションを列挙
   - `session:ID`: 指定されたセッションIDのログを直接読み込み

2. セッションログの所在を確認:
   ```bash
   # プロジェクトごとのセッションディレクトリを列挙
   find ~/.claude/projects/ -name "*.jsonl" -newer /tmp/cutoff_marker 2>/dev/null | head -20
   ```

3. JSONL を読み込み、以下をフィルタ:
   - `type: "user"` かつ `message.content` が string のエントリ（ユーザーの自発的メッセージ）
   - `type: "assistant"` のエントリ（AIの応答）
   - `type: "user"` かつ `message.content` が tool_result のエントリ（ツール実行結果）
   - `type: "progress"` は除外

4. `parentUuid` チェーンで会話の流れを再構築

#### Stage 2: Detect

`references/detection-signals.md` に定義された6つのシグナルカテゴリで齟齬を検出。

各シグナルについて:
1. キーワードマッチ or 構造的パターンマッチを実行
2. 検出ポイントごとに前後の文脈（assistant出力 + ユーザー修正 + 修正後出力）を紐づけ
3. detection_points リストとして Stage 3 に渡す

**検出が0件の場合**: 「このセッションでは認識齟齬が検出されませんでした」と報告して終了。

#### Stage 3: Extract

`references/extraction-prompt.md` のテンプレートを使い、検出ポイントから暗黙知を抽出。

1. detection_points をプロンプトに埋め込み、LLM に暗黙知の抽出を依頼
2. 同一セッション内の重複パターンをグルーピング
3. 各暗黙知に id, domain, confidence を付与

**User Interaction Point**: 抽出結果をユーザーに提示。
```
以下の暗黙知が見つかりました:

1. [domain] {knowledge} (confidence: {n})
   Gap: {gap}
   Your correction: {correction}

2. ...

合っていますか？修正・追加・削除があれば教えてください。
```

ユーザーの修正を反映してから Stage 4 に進む。

#### Stage 4: Integrate

`references/integration-rules.md` に従い、既存の knowledge-base.jsonl と突合。

1. `.claude/tacit-knowledge/knowledge-base.jsonl` を読み込み
2. 各抽出知見について verdict を判定（new / reinforce / contradict / promote）
3. 判定結果を Stage 5 に渡す

#### Stage 5: Propose

`templates/proposal.md` のフォーマットで反映提案を生成。

1. 各知見の layer と verdict に基づき、反映先を決定:
   - `new` (Layer 2) → スキルルール追記 or 個別の学び作成
   - `reinforce` → 既存エントリの更新のみ（ファイル反映は不要）
   - `promote` → 上位原則ドキュメントの作成/更新
   - `contradict` → Stage 6 の議論対象としてマーク

2. 反映先のファイルが存在するか確認し、具体的な変更内容を生成

**User Interaction Point**: 提案一覧を提示。
```
以下の反映を提案します:

## Proposal 1/N: スキルルール追記
- Target: {file_path}
- Content: "{proposed_rule}"
- Evidence: {sessions} で {count} 回の同一修正

[承認 / 修正 / 却下]

## Proposal 2/N: ...
```

個別に承認/修正/却下を受け付ける。

#### Stage 6: Debate

`references/debate-personas.md` に定義されたペルソナで議論。

**Trigger**: Stage 4 で `promote` or `contradict` verdict が存在する場合のみ実行。

1. Agent (general-purpose) を起動し、5つのペルソナによる議論を実行
2. 議論の入力: 昇格候補の知見群 + 既存の上位原則ドキュメント（あれば）
3. 議論結果を `debates/` に保存

**User Interaction Point**: 議論結果と導出された原則を提示。
```
Agent Teams の議論結果:

## 導出された上位原則
"{principle}"

## 議論の要約
- 実務者: {opinion}
- 抽象化担当: {opinion}
- 反証担当: {opinion}
- 統合担当: {opinion}
- ユーザー代弁者: {opinion}

## Verdict: {promote / defer / revise / reject}

この原則を反映しますか？
```

#### Stage 7: Apply

承認された提案を実行:

1. 対象ファイルに Edit/Write で変更を適用
2. knowledge-base.jsonl を更新:
   - 新規エントリ追加
   - 既存エントリの confidence/sources 更新
   - 昇格済みエントリの layer を 3 に、status を `promoted` に変更
3. 分析レポートを `analysis-history/` に保存（`templates/analysis-report.md` 使用）
4. 変更サマリを出力

```
## Applied Changes

| Action | Target | Status |
|--------|--------|--------|
| Rule added | skills/content-draft.md | Applied |
| Knowledge base | +2 new, 1 reinforced | Updated |
| Debate log | debates/2026-03-22-debate-001.md | Saved |
| Analysis report | analysis-history/2026-03-22-session-xxx.md | Saved |
```

## Error Handling

- **セッションログが見つからない場合**: エラーメッセージを表示し、パスの確認を促す
- **knowledge-base.jsonl が空の場合**: Stage 4 で全エントリを `new` として処理（初回実行）
- **検出が0件の場合**: Stage 2 完了後に報告して終了（Stage 3 以降をスキップ）
- **ユーザーが全提案を却下した場合**: knowledge-base.jsonl の更新のみ行い、ファイル反映はスキップ
```

- [ ] **Step 2: Commit**

```bash
git add .config/claude/skills/analyze-tacit-knowledge/SKILL.md
git commit -m "$(cat <<'EOF'
✨ feat: implement analyze-tacit-knowledge skill

7-stage pipeline for extracting tacit knowledge from session logs:
Ingest → Detect → Extract → Integrate → Propose → Debate → Apply

Accumulative architecture with knowledge-base.jsonl as the core data
store, Agent Teams debate for principle derivation, and 3 user
interaction points for human-in-the-loop validation.
EOF
)"
```

---

## Task 9: 動作確認（Spike）

- [ ] **Step 1: セッションログの実在確認**

```bash
# 最新のセッションログを探す
find ~/.claude/projects/ -name "*.jsonl" -type f 2>/dev/null | head -5
```

期待: JSONL ファイルが見つかること。

- [ ] **Step 2: JSONL の構造確認**

見つかったログの先頭数行を読み、Stage 1 の正規化ロジックが想定通り動くか確認:

```bash
head -3 <found_jsonl_path> | python3 -m json.tool --no-ensure-ascii
```

期待: `type`, `message.role`, `message.content`, `parentUuid`, `timestamp` フィールドが存在すること。

- [ ] **Step 3: /analyze-tacit-knowledge status を実行**

スキルが正しく呼び出されるか確認。knowledge-base.jsonl が空なので「エントリなし」と表示されるはず。

- [ ] **Step 4: /analyze-tacit-knowledge latest を実行**

最新セッションに対してパイプラインを実行。各ステージが順に動作し、ユーザー対話ポイントで停止することを確認。

- [ ] **Step 5: 結果確認**

- knowledge-base.jsonl にエントリが追加されたか
- analysis-history/ にレポートが生成されたか
- 提案されたファイル変更が適用されたか（承認した場合）

---

## Dependency Graph

```
Task 1 (data store)
    ↓
Task 2 (detection signals)  ←── independent
Task 3 (extraction prompt)  ←── independent
Task 4 (integration rules)  ←── independent
Task 5 (debate personas)    ←── independent
Task 6 (report template)    ←── independent
Task 7 (slash command)      ←── independent
    ↓
Task 8 (SKILL.md) ←── depends on Tasks 1-7 (references all assets)
    ↓
Task 9 (spike / verification) ←── depends on Task 8
```

Tasks 2-7 are independent and can be executed in parallel.
