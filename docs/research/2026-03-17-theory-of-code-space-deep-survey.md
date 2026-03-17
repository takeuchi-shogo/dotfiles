# Theory of Code Space: 深層調査レポート

**対象論文**: "Theory of Code Space: Do Code Agents Understand Software Architecture?"
**arXiv**: 2603.00601v3 (2026年2月28日公開、3月5日改訂)
**著者**: Grigory Sapunov (Intento CTO, PhD in AI, Google ML Expert)
**調査日**: 2026-03-17

---

## Executive Summary

コードエージェント（Claude Code, SWE-agent, Cursor 等）はベンチマークで高スコアを出すが、実際の複数モジュールが相互依存するコードベースでは苦戦する。本論文は **Theory of Code Space (ToCS)** ベンチマークを提案し、エージェントが**アーキテクチャ的信念（architectural beliefs）を構築・維持・更新できるか**を測定する。

**3つの核心的発見**:
1. **Active-Passive Gap はモデル依存**: GPT-5.3-Codex は能動探索が全ファイル一括提示を上回る (APG=-0.22)。Gemini 2.5 Flash は逆 (APG=+0.23)
2. **Self-scaffolding はモデル依存**: scratchpad モード（構造化 JSON を保持）は GPT に +14 F1 ポイントの大幅改善だが、Gemini にはほぼ効果なし
3. **Belief state 安定性は規模に依存しない**: 最小モデル (Gemini 2.5 Flash) が完全安定、大きいモデル (Gemini 2.5 Pro) が壊滅的崩壊

**Claude Sonnet 4.6 の結果**: Dep F1=0.664（2位）、Precision=0.983（ほぼ完璧）、Inv F1=0.778（1位）。高精度・低再現率の探索戦略。

---

## 第1章: ToCS ベンチマークの設計思想

### 1.1 問題の定式化

コードベース理解を**潜在的アーキテクチャ状態に対する信念構築**として定式化:

- **Ground truth S**: 型付き依存グラフ G=(V,E)、エッジ型 τ∈{imports, calls_api, data_flows_to, registry_wires}、モジュール間不変条件 I、公開契約 C
- **評価対象**: 信念 M_t(S) に対する3操作 — **Construct**（部分観測から構築）、**Revise**（環境変化時に更新）、**Exploit**（下流タスクに使用）
- v0.1 は Construct のみ評価。Revise/Exploit は将来版

### 1.2 部分観察性と行動空間

エージェントは5つのアクションで探索:

| アクション | コスト | 返却情報 |
|-----------|-------|---------|
| `LIST(d)` | 0 | ディレクトリ内のファイル名のみ |
| `OPEN(f)` | 1 | ファイル全内容 |
| `SEARCH(q)` | 1 | マッチするパス+行番号（**内容は返さない**） |
| `INSPECT(f,s)` | 1 | シンボルの型シグネチャ+docstring のみ |
| `DONE()` | 0 | 終了 |

**予算制約**: デフォルト B=20。SEARCH はロケーションのみ返し内容は返さない — アーキテクチャ理解には意図的な OPEN 判断が必要。

### 1.3 認知マップのプロービング

**K=3 アクション毎**にハーネスが中断し、構造化 JSON での信念外部化を要求:

```json
{
  "components": [{"name": "...", "status": "explored|inferred|unknown",
                   "purpose": "...", "exports": [], "dependencies": [],
                   "confidence": 0.0-1.0}],
  "invariants": [{"type": "boundary|dataflow|interface|invariant|purpose",
                   "src": "...", "dst": "...", "via": "...",
                   "pattern": "...", "evidence": "..."}],
  "uncertainty": "..."
}
```

**プロービングは無料**（予算を消費しない）。これにより最終スナップショットだけでなく**信念の時系列変化**を観測可能。

### 1.4 4つのエッジ型と発見難易度

| エッジ型 | 割合 | 発見方法 | 難易度 |
|---------|------|---------|-------|
| `imports` | ~67% | AST パース / import 文を読む | 低 |
| `calls_api` | ~17% | 関数本体を読む必要あり | 中 |
| `registry_wires` | ~9% | config + registry ロジックの理解が必要 | 高 |
| `data_flows_to` | ~7% | オーケストレーター経由の多段推論が必要 | 最高 |

**重要**: エッジの約1/3は import 追跡では発見不可能。構文解析と意味理解の間に意味のあるギャップが存在。

### 1.5 不変条件の植え込み

各コードベースに15-16個の制約を植え込み:
- **Forbidden dependency**: 「モジュール A はモジュール C を直接インポートしてはならない」
- **Interface-only access**: 「モジュール X はインターフェース Z を通じてのみ Y にアクセス」
- **Validation chain**: 「データはモジュール W に到達する前に validation を通過すること」

各制約は**テスト証拠、構造パターン、またはドキュメント**として発見可能な形で埋め込まれる。

---

## 第2章: 実験結果 — モデル比較

### 2.1 全体ランキング

| 順位 | モデル | Dep F1 | Precision | Recall | AUC | Inv F1 |
|------|--------|--------|-----------|--------|-----|--------|
| — | Oracle | 1.000 | 1.000 | 1.000 | — | — |
| 1 | **GPT-5.3-Codex** | **0.676** | 0.782 | **0.597** | **0.306** | 0.739 |
| 2 | **Claude Sonnet 4.6** | 0.664 | **0.983** | 0.502 | 0.350 | **0.778** |
| 3 | Config-Aware (ルールベース) | 0.577 | 0.736 | 0.475 | 0.212 | 0.000 |
| 4 | Random | 0.538 | 1.000 | 0.368 | 0.142 | 0.000 |
| 5 | Gemini 2.5 Flash | 0.470 | 0.642 | 0.373 | 0.259 | 0.517 |
| 6 | Gemini 3.1 Pro | 0.321 | 0.764 | 0.212 | 0.140 | 0.423 |
| 7 | BFS-Import | 0.293 | 1.000 | 0.173 | 0.079 | 0.000 |
| 8 | Gemini 2.5 Pro | 0.242 | 1.000 | 0.138 | 0.205 | 0.376 |
| 9 | Gemini 3 Flash | 0.147 | 0.897 | 0.080 | 0.133 | 0.125 |

### 2.2 核心的洞察

**GPT vs Claude の戦略差**:
- **GPT-5.3-Codex**: 広範カバレッジ戦略（最高 recall 0.597）。多くのファイルを開き幅広く依存関係を検出
- **Claude Sonnet 4.6**: 精密探索戦略（ほぼ完璧な precision 0.983）。開いたファイルから正確に依存関係を抽出。**不変条件発見では1位** (Inv F1=0.778)

**LLM エージェントのみが4種全エッジ型を発見**:
- ルールベース手法は最大2種（imports + registry_wires）しか発見できない
- `data_flows_to`（最高難易度）は Gemini 3.1 Pro が recall 50%、GPT-5.3 が 31% — **多段推論能力の指標**
- Claude は data_flows_to の recall が 0% — ここが改善余地

**Precision-Recall の分離**:
- Claude (precision 0.983) と Gemini 2.5 Pro (precision 1.000) は同等の精度だが、recall が 0.502 vs 0.138 — **精度だけでは理解度を測れない**

### 2.3 エッジ型別 Recall

| モデル | imports | calls_api | data_flows | registry_wires |
|--------|---------|-----------|-----------|-----------------|
| GPT-5.3-Codex | 0.69 | 0.15 | **0.31** | **1.00** |
| Claude Sonnet 4.6 | 0.56 | 0.15 | 0.00 | **1.00** |
| Gemini 2.5 Flash | 0.47 | 0.18 | 0.00 | 0.37 |
| Gemini 3.1 Pro | 0.27 | 0.00 | **0.50** | 0.00 |

- GPT と Claude は registry_wires を完全検出（config→registry のパターン理解）
- Claude は data_flows_to を検出できていない — **オーケストレーター経由の多段推論が弱点**

---

## 第3章: Active-Passive Gap — 探索能力の分解

### 3.1 4条件による分解

| 条件 | 説明 |
|------|------|
| **Active** | エージェントが予算内で自律的にアクション選択 |
| **Passive-Full** | 全ファイルを一括提示、1回のみプローブ |
| **Passive-Oracle** | Oracle が最適なBファイルを選択、K ステップ毎にプローブ |
| **Passive-Replay** | 先行 Active 実行と同じ観測トレースを再生（決定不要） |

**分解式**: APG_total = APG_selection + APG_decision
- APG_selection = Passive-Oracle - Active（ファイル選択の非最適性）
- APG_decision = Passive-Replay - Active（決定の認知コスト）

### 3.2 GPT-5.3-Codex: 能動探索が勝る

| 条件 | Dep F1 | Inv F1 |
|------|--------|--------|
| Passive-Full | 0.457 | 0.757 |
| Passive-Replay | 0.665 | 0.752 |
| **Active** | **0.676** | 0.739 |
| Passive-Oracle | 0.737 | 0.683 |

- **APG_total = -0.219**: 能動探索が全ファイル一括を**大幅に上回る**
- **原因**: 27-30ファイルを同時に見ると**情報過負荷**。逐次探索により焦点を絞った処理が可能
- Active ≈ Passive-Replay: 探索**判断のコストはほぼゼロ**
- Passive-Oracle > Active: ファイル選択にはまだ改善余地 (6ポイント差)

### 3.3 Gemini 2.5 Flash: 受動提示が勝る

| 条件 | Dep F1 | Inv F1 |
|------|--------|--------|
| **Passive-Full** | **0.696** | 0.696 |
| Passive-Replay | 0.561 | 0.665 |
| Active | 0.469 | 0.516 |
| Passive-Oracle | 0.641 | 0.349 |

- **APG_total = +0.226**: 全ファイル一括が能動探索を大幅に上回る
- Gemini は全ファイルを一度に見て "thinking" 推論で処理するのが得意だが、探索戦略は非効率
- **「負の決定コスト」**: GPT のトレースを追従する方が自力探索より良い → 探索判断自体が理解を**阻害**

### 3.4 不変条件発見のパターン

**両モデルとも Passive-Full が最高** (GPT: 0.757, Gemini: 0.696):
- 不変条件は複数モジュールに跨るため、全体を俯瞰できる方が有利
- 逐次提示（Oracle順序でも）では横断的制約の合成が困難

---

## 第4章: Belief Externalization と Self-Scaffolding

### 4.1 Scratchpad 効果

| モデル | Scratchpad | No-probe | Probe-only |
|--------|-----------|----------|-----------|
| GPT-5.3 Dep F1 | **0.676** | 0.538 | 0.464 |
| GPT-5.3 Inv F1 | **0.739** | 0.570 | 0.447 |
| Gemini 2.5F Dep F1 | 0.469 | **0.480** | 0.401 |
| Gemini 2.5F Inv F1 | **0.516** | 0.273 | 0.481 |

**GPT**: scratchpad >> no-probe >> probe-only。**+14 F1 ポイント**の大幅改善。自身の prior map を外部ワーキングメモリとして使い、信念の一貫性を維持。

**Gemini**: no-probe ≈ scratchpad >> probe-only。Dep F1 にはほぼ効果なし。ただし**不変条件発見には +24 ポイントの大幅効果** — Gemini は scratchpad を依存関係追跡ではなく横断的推論に使う。

**Probe-only は両モデルで最弱**: 構造化出力の生成がアテンション・コンテキスト予算を消費し、自己参照の利益なし。

### 4.2 Belief State Instability — 3つのパターン

| モデル | パターン | 説明 |
|--------|---------|------|
| **Gemini 2.5 Flash** | 完全安定 | 全プローブで正しいエッジのロストがゼロ |
| **Gemini 2.5 Pro** | 壊滅的崩壊 | ステップ9でピーク F1=0.33 → 1回のプローブで12個の正しいエッジが消失 |
| **Gemini 3 Flash** | 近接バイアス | 各プローブで直近の3-5コンポーネントのみ報告 |
| **Gemini 3.1 Pro** | 可変不安定 | 最良のコードベースでは単調蓄積、最悪では全エッジがゼロに |

**最重要洞察**: 信念状態の維持能力は**モデル規模に依存しない**。最小モデル (Gemini 2.5 Flash) が最も安定。訓練目標に依存する可能性が高い。

### 4.3 Externalization Gap

GPT-5.3 は imports エッジの recall 69%、Gemini 3 Flash / 2.5 Pro は 11-12% — **同等数のファイルを開いたにもかかわらず 6倍の差**。

これは「見たものを理解する能力」ではなく「理解を外部化する能力」の差。プロンプト仕様の曖昧さも寄与:
- Gemini 2.5 Flash の false positive の 45% は**エッジ型の混同**（import と calls_api の両方を報告）
- 22% は非コンポーネントファイルをエンドポイントとして報告
- **真のハルシネーションはわずか 5%**

---

## 第5章: コードエージェント設計への実務的含意

### 5.1 論文が提案する4つの改善パス

| パス | 説明 | 現在の我々のハーネスとの関係 |
|------|------|--------------------------|
| **ハイブリッドアプローチ** | AST 抽出 + LLM 分析の組み合わせ | 未実装。`imports` エッジは AST で自動取得し、LLM には意味的理解に集中させる |
| **Belief externalization 訓練** | 信念外部化の品質向上 | probe/scratchpad パターンを Claude Code の探索に応用可能 |
| **探索戦略の最適化** | Oracle vs Agent で 6-17 ポイント差 | ファイル選択ヒューリスティクスの改善余地 |
| **明示的状態管理** | scratchpad が GPT に +14 F1 | **直接適用可能**: 構造化された「プロジェクト理解マップ」のコンテキスト保持 |

### 5.2 我々のハーネスへの具体的適用可能性

#### A. Cognitive Map as Scratchpad（最重要）

論文の最大の発見: **構造化信念マップをコンテキストに保持すると、Claude の性能が向上する可能性**。

現状の我々のハーネス:
- `SessionStart` hook でプロジェクト情報を注入
- CLAUDE.md に Change Surface Matrix がある
- しかし、**探索中に構造化されたアーキテクチャ信念を動的に更新・保持する仕組みはない**

ToCS の示唆する改善:
- 大規模タスク開始時に「プロジェクト構造マップ」を JSON で構築
- 探索の進行に伴い動的に更新
- コンテキスト圧縮時にも保持されるよう外部ファイルとして永続化

#### B. Active Exploration Strategy の最適化

Claude Sonnet 4.6 の特性（論文データより）:
- **Precision 0.983**: 見たものは正確に理解する
- **Recall 0.502**: 見るべきファイルの選択に改善余地
- **data_flows_to recall 0%**: 多段推論による暗黙的データフローの検出が弱い

改善策:
- config/registry ファイルを優先的に読む戦略（Config-Aware ベースラインの知見）
- オーケストレーターファイルの明示的な識別と deep reading

#### C. Belief State Maintenance

論文は Gemini の catastrophic collapse を報告したが、**Claude については直接テストされていない**。ただし我々のハーネスにおける context compaction 後の情報ロストは類似の問題。

対策:
- `/checkpoint` で構造化マップを永続化
- PreCompact hook で重要な「信念状態」を保護

#### D. Prompt Specification の重要性

論文の Lesson 5: 「プロンプト仕様は実験変数」— Claude は ancient prompt と new prompt で F1 差がわずか +0.012（他モデルは +0.11〜0.14）。Claude は**プロンプト変更に対してロバスト**。ただしこれは「既に良いプロンプトで引き出せている」ことの証左であり、プロンプト改善の天井に近い可能性。

---

## 第6章: 関連ベンチマークとの位置付け

### 6.1 コードエージェント評価の全体像

| ベンチマーク | 評価対象 | ToCS との差異 |
|------------|---------|-------------|
| **SWE-bench** | バグ修正パッチの正確性 | 出力の正しさのみ。アーキテクチャ理解は測定しない |
| **SWE-bench Pro** | より大規模な修正 (平均4.1ファイル) | マルチファイルだがアーキテクチャ信念は測定しない |
| **SWE-ContextBench** | 経験再利用 | 文脈学習を測定。信念の構築・維持は対象外 |
| **RefactorBench** | マルチファイルリファクタリング | 出力の正しさのみ。信念状態のプローブなし |
| **FeatureBench** | 新機能開発 | 出力正しさ。探索予算・信念外部化なし |
| **ToCS** | **アーキテクチャ信念の構築・維持** | 唯一、探索予算+定期プローブ+型付き依存グラフ評価 |

**ToCS のユニークさ**: 「エージェントが何を見たか」「何を出力したか」ではなく「**エージェントが何を信じているか**」を測定する唯一のベンチマーク。

### 6.2 Theory of Space からの移植

ToCS は空間推論の「Theory of Space」フレームワーク（グリッドワールドでの Active-Passive Gap と Belief Inertia の測定）をコードに移植:

| Theory of Space | Theory of Code Space |
|----------------|---------------------|
| グリッドワールド | 手続き生成コードベース |
| 空間マップ | モジュール依存グラフ |
| 移動アクション | LIST/OPEN/SEARCH/INSPECT |
| 位置の信念 | アーキテクチャの信念 |
| — | **Architectural Constraint Discovery**（新規追加） |

**重要な発見の差異**: Theory of Space では全モデルで Active < Passive (APG>0)。ToCS では**方向がモデル依存** — GPT は Active が勝る。コード探索は空間探索より豊かな意味的フィードバックを持つためと考えられる。

---

## 第7章: 著者と論文の信頼性

### 7.1 著者背景

**Grigory Sapunov**: Intento 共同創業者・CTO。PhD in AI。Google ML Developer Expert。20年以上のソフトウェアエンジニアリング経験。Medium / Unite.AI で AI 技術記事を執筆。Simon & Schuster から書籍出版。

単独著者の論文だが、実験設計は堅実で再現性に配慮（手続き的コードベース生成、オープンソースベンチマーク公開）。

### 7.2 限界

著者自身が明示する限界:
- Pipeline アーキテクチャのみ（1パターン）
- Python のみ
- 中立的ファイル名（mod_a.py 等 — 実プロジェクトより難しい）
- ドキュメントなし
- 6モデル × 3コードベース × 1実行 — 統計的検出力は限定的
- 単一プロンプトデザイン

---

## 第8章: 統合的評価と展望

### 8.1 最も重要な知見（ランク順）

1. **Scratchpad = 外部ワーキングメモリ**: GPT に +14 F1。構造化された信念マップをコンテキストに保持することがアーキテクチャ理解を大幅に改善する。**これは Claude Code のハーネス設計に直接応用可能**

2. **Belief externalization ≠ Understanding**: 同じファイルを見ても外部化能力に 6倍の差。プロンプト仕様（エッジ型の定義、コンポーネント境界の明確化）が一次変数

3. **Active-Passive Gap の方向はモデル固有**: Claude は精密探索型（precision 0.983）。情報過負荷の回避と、見逃しの最小化のバランスが設計課題

4. **不変条件発見には全体俯瞰が有利**: 横断的制約は逐次探索より全ファイル一括が効く。大規模タスクでは最初にプロジェクト全体の「地図」を作るフェーズが有用

5. **信念安定性はモデル規模に依存しない**: 訓練目標の影響。context compaction 後の信念ロスト対策が重要

### 8.2 前論文（CoT Monitorability）との関連

| 側面 | CoT Monitorability | Theory of Code Space |
|------|-------------------|---------------------|
| 対象 | モデル内部の推論過程 | エージェントの外部化された信念 |
| 評価対象 | 忠実性 (faithfulness) | 正確性 + 安定性 |
| 実務的影響 | モデル提供者の責任 | **エージェント設計者の責任** |
| 我々への適用 | 間接的（理論的裏付け） | **直接的（設計改善）** |

### 8.3 今後の展望

**Phase 2 (計画中)**: 複数アーキテクチャパターン、追加言語、ドキュメントチャネル、REVISE モード
**Phase 3**: 大規模実験、オープンウェイトモデル、プロンプト ablation

---

## 参考文献

### 主要論文
- Sapunov, G. (2026). "Theory of Code Space: Do Code Agents Understand Software Architecture?" [arXiv:2603.00601](https://arxiv.org/abs/2603.00601)

### 関連ベンチマーク
- [SWE-bench](https://www.swebench.com/) — バグ修正ベンチマーク
- [SWE-ContextBench](https://arxiv.org/abs/2602.08316) — コンテキスト学習ベンチマーク
- [SWE-bench Pro](https://arxiv.org/pdf/2509.16941) — エンタープライズ級問題
- [FeatureBench](https://openreview.net/forum?id=41xrZ3uGuI) — 新機能開発

### 著者
- [Grigory Sapunov - Google Scholar](https://scholar.google.com/citations?user=WiQAER0AAAAJ)
- [Intento](https://inten.to/) — 著者のCTO先

### 業界レポート
- [Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)
