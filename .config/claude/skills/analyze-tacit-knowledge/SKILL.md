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
3. 各暗黙知に id, domain, confidence, model_attribution を付与
   - `model_attribution`: どのモデルが発見した知見か（`claude` / `codex` / `gemini` / `unknown`）
   - セッションログの委譲元（Agent ツール呼び出し、`codex exec`、`gemini-explore` 等）から判定
   - 判定できない場合は `unknown` を設定

**User Interaction Point**: 抽出結果をユーザーに提示。
```
以下の暗黙知が見つかりました:

1. [domain] {knowledge} (confidence: {n}, model: {model_attribution})
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
   - `promote` → 上位原則ドキュメントの新規作成（`principle_creation`）or 既存への追記（`principle_update`）
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
4. **Cross-Model Insight Export**: `model_attribution` が `codex` or `gemini` の知見を `references/cross-model-insights.md` の該当セクションに追記する。HACRL の双方向知識転移に基づき、モデル固有の発見を他モデルのコンテキストに還元する
5. 変更サマリを出力

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
