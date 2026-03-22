# Tacit Knowledge Analyzer - Design Spec

## Overview

Claude Code セッションログから暗黙知を自動抽出し、3層構造（ログ要約 / スキルルール・個別の学び / 上位原則）で蓄積・進化させるパイプラインスキル。

実行するたびに過去の分析結果と突合し、知見の体系を進化させる蓄積型アーキテクチャ。

## Background

AI エージェントとの業務中、ユーザーが繰り返し同じ修正を指示するケースがある。この修正差分こそが「AI の平均的思考」と「ユーザー固有の判断基準」のギャップであり、暗黙知そのもの。

現状、この暗黙知の抽出・蓄積は手動で行われている。本スキルはこのプロセスをパイプラインとして自動化し、業務を進めるだけで暗黙知が形式知として積み上がる仕組みを実現する。

## Architecture: 7-Stage Pipeline

```
/analyze-tacit-knowledge [session-id|latest|period:7d|status]

Stage 1: Ingest     -- セッションログ読み込み・正規化
Stage 2: Detect     -- 認識齟齬ポイントの検出
Stage 3: Extract    -- 齟齬から暗黙知パターンを抽出
Stage 4: Integrate  -- 過去の知見indexと突合
Stage 5: Propose    -- 反映先と具体的な変更内容を提案
Stage 6: Debate     -- Agent Teamsで多角的に検証、上位原則の導出
Stage 7: Apply      -- ユーザー承認後、ファイルに反映しindexを更新
```

### User Interaction Points

- Stage 3 完了後: 「こういう暗黙知が見つかりました。合っていますか？」
- Stage 5 完了後: 「この反映先・内容でよいですか？」
- Stage 6 完了後: 「議論の結果、この上位原則を導出しました。反映しますか？」
- Stage 7: 承認されたもののみ反映

## Stage Details

### Stage 1: Ingest

Claude Code のセッションログは `~/.claude/projects/*/sessions/` 配下に JSONL で保存されている。各行はメッセージオブジェクト（role, content, tool_use 等）。

**Input patterns:**

| Pattern | Description |
|---------|-------------|
| `latest` | 最新セッション1件 |
| `session-id` | 特定セッション指定 |
| `period:7d` | 直近N日間の全セッション |

**Normalization:** JSONL から以下を抽出してワーキングデータを構築:
- human -> assistant の往復ペア
- tool_use（Edit, Write 等）とその結果
- タイムスタンプ

### Stage 2: Detect

認識齟齬を示すシグナルをパターンマッチで検出:

| Signal | Detection Method |
|--------|-----------------|
| 明示的修正指示 | 「違う」「そうじゃない」「〜に変えて」等のキーワード |
| やり直し | 同一ファイルへの複数回 Edit（ユーザーフィードバック挟み） |
| 方針転換 | 「やっぱり」「こっちのアプローチで」 |
| 不満・苛立ち | 「毎回」「何度も言ってる」 |
| 早期中断 | ユーザーが assistant の出力途中で割り込み |
| 追加説明 | 長い補足説明（AI の出力が前提を外していた兆候） |

各検出ポイントに前後の文脈（直前の assistant 出力 + ユーザーの修正指示 + 修正後の出力）を紐づけて Stage 3 に渡す。

### Stage 3: Extract

Stage 2 で検出した齟齬ポイントごとに、LLM で以下を抽出:

```yaml
- id: tk-20260322-001
  gap: "AIが処方的トーンで書いた"
  user_correction: "確信の表明だけで止める。行動指示はしない"
  implicit_knowledge: "受け手に判断を委ねるスタンス。処方は信頼を損なう"
  domain: "content-creation/tone"
  confidence: 0.85
```

**Extraction dimensions:**
- AI の出力と修正後の差分から「何がズレていたか」
- 修正指示の言葉から「なぜそう判断したか」（暗黙の判断基準）
- 複数の齟齬に共通するパターン（同じ domain、同じ種類の修正）

同一セッション内で繰り返される修正パターンはグルーピングし、1つの暗黙知としてまとめる。

### Stage 4: Integrate

過去の知見 index `knowledge-base.jsonl` と突合:

| Verdict | Condition | Action |
|---------|-----------|--------|
| **新規** | 既存 index に類似なし | 新規エントリとして追加候補 |
| **強化** | 既存の知見と同 domain・同方向 | 既存エントリの confidence 上昇、事例追加 |
| **矛盾** | 既存の知見と逆方向 | フラグを立てて Stage 6 の議論対象に |
| **昇格候補** | 同 domain の知見が3件以上蓄積 | Layer 3（上位原則）への昇格候補としてマーク |

### Stage 5: Propose

Stage 4 の結果を受けて、具体的な反映先と変更内容を生成:

| Knowledge Layer | Target | Example |
|----------------|--------|---------|
| Layer 2: スキルルール | 対象スキルファイルへのルール追記 | `skills/content-draft.md` に「処方的表現を避ける」追加 |
| Layer 2: 個別の学び | `learnings/` 配下に Markdown 生成 | `learnings/2026-03-22-tone-control.md` |
| Layer 3: 上位原則 | 上位ドキュメントへの追記/新規作成 | `principles/communication-stance.md` |

**Proposal format:**

```markdown
## Proposal 1/3: Skill Rule Addition
- Target: skills/content-draft.md
- Type: rule addition
- Content: "末尾で行動を指示しない。事実と見解を提示し、判断は受け手に委ねる"
- Evidence: session xxx, yyy, zzz で同一修正が3回
- Confidence: 0.9
```

### Stage 6: Debate

Stage 4 で「昇格候補」「矛盾」とマークされた知見に対して Agent Teams で議論。

**Personas (5 roles):**

| Role | Perspective |
|------|-------------|
| 実務者 | 「現場でこのルールは実用的か」 |
| 抽象化担当 | 「個別ルールの背後にある原則は何か」 |
| 反証担当 | 「この原則が逆効果になるケースは？」 |
| 統合担当 | 「既存の上位原則との整合性は」 |
| ユーザー代弁者 | 「ユーザーの意図をこの抽象度で正しく捉えているか」 |

**Input:** 昇格候補の知見群 + 既存の上位原則ドキュメント
**Output:** 導出された上位原則（または「まだ昇格は早い」の判断）

### Stage 7: Apply

承認された提案を実行:

1. **File reflection** -- 対象ファイルに Edit/Write で変更を適用
2. **Index update** -- knowledge-base.jsonl に新規エントリ追加、既存エントリの confidence/sources 更新、昇格済みは layer を 3 に変更
3. **Change summary** -- 何をどこに反映したかの一覧を出力

## Data Store

```
.claude/tacit-knowledge/
├── knowledge-base.jsonl    # 全知見のindex（蓄積型の心臓部）
├── analysis-history/       # 過去の分析結果
│   └── 2026-03-22-session-xxx.md
└── debates/                # Agent Teams議論ログ
    └── 2026-03-22-debate-001.md
```

### knowledge-base.jsonl Schema

```jsonl
{"id":"tk-...","knowledge":"...","domain":"...","layer":2,"confidence":0.85,"sources":["session-xxx"],"created":"2026-03-22","updated":"2026-03-22","applied_to":["skills/content-draft.md"]}
```

`knowledge-base.jsonl` が蓄積の核。次回実行時に Stage 4 がこれを読み、知見の進化（個別の学び -> 上位原則への昇格）を追跡する。

## Skill Interface

```
/analyze-tacit-knowledge              # 最新セッションを分析
/analyze-tacit-knowledge period:7d    # 直近7日間
/analyze-tacit-knowledge session:xxx  # 特定セッション
/analyze-tacit-knowledge status       # 現在の知見蓄積状況を表示
```

`status` は knowledge-base.jsonl の統計を表示: 知見数、layer 別分布、domain 別分布、直近の昇格イベント。

## Design Decisions

1. **Pipeline over monolith**: 各ステージが独立しているので途中で人間が介入・修正でき、段階的に機能追加しやすい
2. **JSONL for knowledge base**: 追記が容易、git diff で差分が見やすい、LLM が直接読める
3. **Agent Teams for principle derivation**: セッション内の自己分析は確認バイアスに引きずられる。複数視点をぶつけることで上位構造が浮かび上がる
4. **Accumulative architecture**: 実行するたびに過去の知見と突合し、confidence の更新・昇格判定を行うことで知識体系が進化する

## Future Extensions

- **Hook integration**: セッション終了時に自動実行（アプローチ3への拡張）
- **Multi-format input**: ChatGPT/Gemini のエクスポート対応
- **Dashboard**: 暗黙知の蓄積状況を可視化する Web UI
- **Team sharing**: チーム内で知見を共有・マージする仕組み
