---
source: https://github.com/safishamsi/graphify
date: 2026-04-27
status: analyzed (本体インストール棄却、3 件採択)
---

## Source Summary

**主張**: graphify はコードベース・論文・マルチメディアを knowledge graph に変換するツール。Karpathy benchmark において 71.5x のトークン削減を主張し、Claude Code / Codex / Cursor など 12+ AI assistants と統合可能なコンテキスト圧縮基盤を提供する。

**手法**:
1. AST extraction (tree-sitter、25 言語対応) でコード構造を解析
2. Whisper transcription (domain-aware prompts) で音声・動画を文字起こし
3. Claude subagent 並列抽出 (docs / papers / images) でマルチモーダル関係抽出
4. Leiden community detection でクラスタリング
5. 対話型 vis.js 可視化 + GRAPH_REPORT.md + JSON クエリ可能出力

**根拠**: Karpathy benchmark (52 files: repos + 5 papers + 4 images の混合コーパス) で 71.5x トークン削減、一般混合コーパスで 5.4x。三値関係タグ (EXTRACTED / INFERRED / AMBIGUOUS) でプロヴェナンスを明示。

**前提条件**: Python 3.10+, tree-sitter, MIT ライセンス、ローカル完全実行 (Claude API 呼び出しは必要)、Claude Code / Codex / Cursor / Copilot 12+ AI assistants と統合可能。

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | tree-sitter + SQLite グラフ | Already | CRG MCP 実装済み (`.config/claude/settings.json` に登録)。SQLite ベースのグラフ保存 + コミュニティ検出を提供 |
| 2 | tree-sitter AST | Already | CRG MCP + ast-grep-practice skill。構造解析パスは既存 |
| 3 | Whisper 文字起こし | N/A | digest skill が PDF / YouTube をカバー。音声・動画専用パスは現状ニーズなし |
| 4 | 並列抽出 (paper / PDF / 画像) | Partial | paper-analysis + compile-wiki は要約止まり。concept → concept の**関係抽出**は未実装 |
| 5 | Leiden community detection | Already | CRG の `list_communities_tool` が対応 |
| 6 | vis.js 対話型 HTML 可視化 | N/A (YAGNI) | Codex + Gemini 批評で棄却。cosmograph.app が 2026 ベスト代替。ローカル常駐 HTML は不要 |
| 7 | コンテキスト圧縮 | Already | compile-wiki + knowledge-pipeline で既存パス確立済み |
| 8 | 中心性ベース hub detection | Partial | CRG `query_graph_tool` で算出可能だが、paper-analysis / compile-wiki で**活用する仕組みが未実装** |
| 9 | 三値タグ EXTRACTED / INFERRED / AMBIGUOUS | Partial (補完) | 既存の confidence score (0–100) と直交する provenance 軸。置換ではなく**併記が有効** |
| 10 | ローカル完全実行 | N/A | Claude API 依存という点で実質同等。差異なし |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | graphify が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| A1 | paper-analysis / compile-wiki の並列処理 | 要約止まりで concept→concept 関係を抽出しない。知識グラフに接続できない | concept→concept 関係抽出 subagent を paper-analysis に追加。`references/relation-extraction.md` に抽出パターン定義 | 強化可能 |
| A2 | confidence score (0–100) | provenance 軸 (どの根拠から得たか) が欠落。確度と由来は直交する別軸 | 三値タグ (EXTRACTED / INFERRED / AMBIGUOUS) を confidence score と**併記**する規約を `references/provenance-tagging.md` に定義 | 強化可能 |

---

## Phase 2.5 Refine (Codex + Gemini 批評統合)

### Codex 主要指摘 (4 点)

1. **vis.js は YAGNI**: `#6 Gap → N/A` に降格。ローカル HTML 可視化は維持コストに見合わない。cosmograph.app を代替候補として記録
2. **過小評価の修正**: digest / paper-analysis は要約止まり。「コンテキスト圧縮」は Already だが「関係抽出」は真の Partial — `#4 Already → Partial` に修正
3. **71.5x ベンチマークの過大解釈**: Karpathy 混合コーパス特化値 (repos+papers+images の特殊条件)。実運用に近い CRG 8.2x 相当と見るべき。reference に記録して比較軸を確保
4. **三値タグ vs confidence は置換不可**: provenance 軸 (どこから得たか) と確度軸 (どれほど確かか) は直交。`#9 Partial → Partial (補完)` に維持

### Gemini 主要指摘

- **Aider repomap**: 1/3 token コスト、保守ゼロの代替実装が存在。graphify 本体導入の費用対効果をさらに下げる根拠
- **MCP Code Indexer** (Anthropic 公式構築中): 標準化見込みがあり、graphify 独自インストールはリスク要因
- **vis.js は時代遅れ**: 2026 ベストは cosmograph.app。`#6 棄却` を補強
- **三値タグは GraphRAG 由来の業界標準**: provenance タグ付けは先行事例が多く、confidence と組み合わせた仕様化が容易

### 判定の修正サマリ

| # | 変更前 | 変更後 | 理由 |
|---|--------|--------|------|
| 4 | Already | Partial | 関係抽出が真の Gap として浮上 |
| 6 | Gap | N/A (YAGNI) | Codex + Gemini で棄却。cosmograph.app 代替あり |
| 9 | 新規追加 | Partial (補完) | provenance 軸として confidence score に併記 |
| 11 | 新規追加 | 記録 | 71.5x ベンチマークを reference に保存 |

---

## Integration Decisions

### Gap / Partial 取捨

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 4 | 関係抽出 (paper / PDF) | **採用 → T1** | 要約止まりの paper-analysis に concept→concept 抽出を追加。CRG との接合ポイント |
| 6 | vis.js 対話型可視化 | **棄却** | YAGNI。cosmograph.app 代替あり、ローカル常駐 HTML は Build to Delete 違反 |
| 8 | hub detection 活用 | **スキップ (T1 後評価)** | T1 が完了してから CRG との接続を評価。先行着手はオーバーエンジニアリング |
| 10 | ローカル完全実行 | **棄却** | 現状と差異なし |

### Already 強化 取捨

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A1 | paper-analysis 関係抽出強化 | **採用 → T1** | 最優先。既存 skill の機能穴を埋める最小変更 |
| A2 | 三値タグ provenance 併記 | **採用 → T2** | confidence score と直交、GraphRAG 業界標準に合わせる。references 1 ファイル追加で軽量 |

### 棄却一覧

| 項目 | 棄却理由 |
|------|----------|
| graphify 本体インストール | CRG と 70% 重複。Build to Delete 違反。Aider repomap / MCP Code Indexer の代替あり |
| vis.js 可視化 | YAGNI。cosmograph.app 代替あり |
| Whisper 統合 | digest skill で代替。独自音声パスは現状不要 |
| --watch / git hook 常駐更新 | Build to Delete 衝突。常駐プロセスは削除コストが高い |

---

## Plan

| # | タスク | 対象ファイル | 規模 |
|---|--------|-------------|------|
| T1 | paper-analysis 関係抽出強化 | `skills/paper-analysis/SKILL.md`、`references/relation-extraction.md`、`templates/paper-analysis-report.md` | M |
| T2 | 三値タグ provenance 併記規約 | `references/provenance-tagging.md`、paper-analysis-report.md テンプレ更新、concept-article.md テンプレ更新 | S |
| T3 | ベンチマーク reference 記録 | `references/codebase-graph-benchmarks.md` | S |

**依存関係**: T1 → T2 (テンプレ衝突リスク: 先に T1 でテンプレを確定してから T2 で tag セクションを追記)、T3 は独立実行可能。

### Task 1: paper-analysis 関係抽出強化 (M)

- **Files**:
  - `.config/claude/skills/paper-analysis/SKILL.md` (新セクション: Relation Extraction Phase)
  - `references/relation-extraction.md` (新規: 関係タイプ定義 + 抽出パターン)
  - `templates/paper-analysis-report.md` (Relations セクション追加)
- **Changes**:
  - SKILL.md に「Step 3.5: Concept Relation Extraction」を追加。concept A → (relation_type) → concept B の三つ組で出力。関係タイプは `references/relation-extraction.md` に従う
  - `references/relation-extraction.md`: EXTENDS / CONTRADICTS / APPLIES / INSTANTIATES / CITES の 5 関係タイプを定義。三値タグ (EXTRACTED / INFERRED / AMBIGUOUS) をカラムに持つテーブル形式
  - テンプレートに `## Relations` セクション追加、三つ組テーブルとタグカラム付き
- **Rationale**: CRG `query_graph_tool` へのフィード候補を生成。要約止まりから知識グラフ連携へ

### Task 2: 三値タグ provenance 併記規約 (S)

- **Files**:
  - `references/provenance-tagging.md` (新規: 三値タグ定義 + confidence score との組み合わせ方針)
  - paper-analysis-report.md、concept-article.md テンプレート (tag カラム挿入)
- **Changes**:
  - `references/provenance-tagging.md`: EXTRACTED (文書から直接引用)、INFERRED (複数ソースから推論)、AMBIGUOUS (根拠が弱いまたは競合) の定義。confidence score 0–100 との関係 (直交する別軸であることを明記)。判定フローチャート
  - テンプレート: Relations テーブルに `provenance` カラム追加
- **Rationale**: GraphRAG 業界標準。T1 後に追記する形で最小変更

### Task 3: ベンチマーク reference 記録 (S)

- **Files**:
  - `references/codebase-graph-benchmarks.md` (新規)
- **Changes**:
  - graphify 71.5x (Karpathy 混合コーパス: 52 files、条件明記)、5.4x (一般混合)
  - CRG 8.2x 相当の実績値 (現在値)
  - Aider repomap の token コスト比較
  - 比較注意事項: コーパス構成差異 (repos only vs repos+papers+images) を明記
- **Rationale**: 将来の tool 選定比較軸として保存。数字の一人歩きを防ぐ文脈付き記録

---

## Risks & Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-----------|
| T1 関係抽出が hallucination を増やす | 誤った関係がグラフに混入 | 三値タグの AMBIGUOUS を必須カラムとして運用。graphify の Hallucination Defense (±10 行閾値) パターンを参考に line 番号必須化 |
| T2 provenance タグの判定が属人的 | タグの一貫性低下 | `references/provenance-tagging.md` に判定フローチャートを入れ、ambiguous ケースを例示 |
| T3 ベンチマーク数値が独り歩き | 71.5x を鵜呑みにした過剰な tool 評価 | 条件 (corpus 構成、ファイル数) を数値と同行に記載。数値単体での参照を禁止する注意書き追加 |
| CRG 標準化 (MCP Code Indexer) でグラフ基盤が変わる | T1 の出力形式が無駄に | T1 は CRG 非依存の三つ組テキスト出力に留める。グラフ連携は別タスクに分離 |
