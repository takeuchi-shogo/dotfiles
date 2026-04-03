# Cross-Model Insight Registry

HACRL (Heterogeneous Agent Collaborative RL) の双方向知識転移に基づき、各モデルが発見した reusable insight を蓄積する。
全エージェントが教師・生徒の両方の役割を担い、過去セッションの知見を次回の実装・レビュー・分析に活かす。

## 更新ポリシー

- `/analyze-tacit-knowledge` の Cross-Model Insight Export ステップから自動追記
- 手動追記も可（セッション中に有用な知見を発見した場合）
- 各エントリには `date`, `source_session`（任意）, `domain`, `insight` を記載
- 鮮度管理: 60日以上前のエントリは Archive セクションに移動

---

## Codex Insights

深い推論・リスク分析・障害モード特定から得られた知見。

| date | domain | insight |
|------|--------|---------|
| 2026-03-23 | hook-design | pre-commit hook で正規表現の `\b` を使うと日本語混在テキストで誤マッチする。`(?=[^a-zA-Z0-9]|$)` に置換すべき。Codex リスク分析で障害モードとして検出 |

## Gemini Insights

大規模コンテキスト分析・エコシステム調査・マルチモーダル処理から得られた知見。

| date | domain | insight |
|------|--------|---------|
| 2026-03-23 | architecture | dotfiles の symlink 構造で `~/.claude/references/` は直接 symlink されていないため、hook から参照する際は `lib/hook_utils.py` の `resolve_reference()` を経由する必要がある。Gemini の 1M コンテキスト分析でパス解決の不整合として発見 |

## Claude Insights

実装経験・デバッグ・パターン発見から得られた知見。

| date | domain | insight |
|------|--------|---------|
| 2026-03-23 | memory-system | MEMORY.md はセッション開始時の静的スナップショットであり、セッション中の更新は次セッションまで system prompt に反映されない。checkpoint/handoff 時は plan ファイルにも必要情報を書く必要がある |
| 2026-03-25 | context-management | **Context Anxiety のモデル別感受性差**: Sonnet 4.5 はコンテキスト 75-80% で早期打ち切り（premature wrapping）が顕著。Compaction だけでは解消せず full context reset が必要。Opus 4.6 では大幅に軽減されたが完全には消えない。長時間タスクでモデルを選択する際の判断材料。(出典: Anthropic "Harness Design for Long-Running Apps", 2026-03) |

---

## Model Empathy (Same-Model Pairing)

> AutoAgent (kevinrgu/autoagent, 2026-04): 同じモデルをメタ/タスクの両方に使うと最も効果的。
> メタエージェントは自身の推論傾向を暗黙的に理解しているため、タスクエージェントの失敗モードを
> 正確に診断し、そのモデルが実際に理解するハーネスを構築できる（"model empathy"）。

- Claude meta × Claude task > Claude meta × GPT task（SpreadsheetBench, TerminalBench で実証）
- **含意**: AutoEvolve の設計（Claude が Claude のハーネスを改善）は正しいアプローチ
- Codex は **meta-agent としては弱い** — 指示を無視して改善を途中で止める傾向がある（autoresearch でも同様に観察）
- Codex の最適な役割は **reviewer/adversary**（Phase 4 Adversarial Gate の現設計と一致）

---

## Shared Blind Spots

> 全モデルが一致する結果は信頼度が上がるが、**正しさの証明ではない**。
> LLM は共通の学習データ・アーキテクチャから類似のバイアスを共有するため、
> 全モデルが同じ間違いをするケースがある。
> (Schwartz "Vibe Physics", 2026-03: Claude/GPT/Gemini 全てが MS-bar subtraction と log(4π) 因子を見落とした)

### レビューアー数増加と盲点リスク

> Del et al. (arXiv:2603.19118): VC と SC の Kendall τ 相関はサンプル数増加で**単調増加**する。
> つまりレビューアーを増やすほど指摘が収束し、**全員が同じ方向を向く**。
> これは一見「合意の質が上がった」ように見えるが、実際には共有盲点の検出力は向上しない。

- N=2（異種）で得られる相補性が最も高く、N が増えるほど信号は収束する
- 「全レビューアーが PASS」は安心材料だが、**盲点が無いことの証明ではない**
- 盲点を検出するには、レビューアーを増やすより**異なるパラダイム**（手動テスト、ユーザーテスト、production monitoring）が有効

### AI のコード読みやすさ固有の弱点

人間と AI の「読みやすさ」の定義は完全には一致しない（Sarsa et al., 2022; 森崎, 2026）。
AI レビューアーが出力する指摘を鵜呑みにせず、以下の弱点を意識する:

| 弱点 | 具体例 | 対策 |
|------|--------|------|
| **大規模コードの全体抽象化が苦手** | 100行超の関数で特定箇所のみ説明し、全体の目的・構造を見落とす | レビュー前に関数の責務を1文で要約させ、漏れをチェック |
| **論理表現の誤認識** | `x > 100` を「xが100より小さい」と説明する | 条件式の自然言語説明が出たら、元のコードと照合する |
| **Linguistic Anti-patterns の検出漏れ** | `isValid()` が非boolを返すパターンを正常と判断する | CC-8 チェックリストで人間が補完する |

### Typicality Bias（RLHF 由来の画一化）

> Zhang et al. 2025 "Verbalized Sampling" (arXiv:2510.01171): RLHF の選好データに **typicality bias** がある（α ≈ 0.57-0.65）。人間は内容が同等でも「典型的な」回答を好み、アライメントがこのバイアスを増幅する。

- Sycophancy（期待への追従）とは異なるメカニズム: typicality bias はデータ由来、Sycophancy はモデルの応答傾向
- 全モデルが RLHF を経ているため、**クロスモデル検証でも典型的回答への収束は検出できない**
- 対策: 多様性が重要なタスクでは Verbalized Sampling を適用する（`references/verbalized-sampling-guide.md`）

### 記録すべきケース

- 全モデルが一致した結論が後で誤りと判明したケース
- 特定のドメイン知識で全モデルが共通の誤解を示したケース

### 対策

- クロスモデル全一致でも「検証済み」ではなく「信頼度が高い」と表現する
- 重要な判断では、モデル出力だけでなく外部ソース（公式ドキュメント、テスト実行結果）で裏取りする
- 既知の盲点パターンをこのセクションに蓄積し、同種の判断時に参照する

| date | domain | blind_spot |
|------|--------|------------|
| — | — | (初期エントリなし。発見次第追記) |

## Model Musical Chairs パターン

一つのモデルで詰まったら別モデルに投げる戦略。各モデルの認知バイアスが異なるため、同じ問題に対して異なるアプローチを取る可能性がある。

**切替トリガー:**
- `stagnation-detector.py` が同種エラー反復を検出（3回連続で同じパターンの失敗）
- 現在のモデルで 2 回のリトライ後も解決しない場合

**切替先の選択:**

| 現在のモデル | 推奨切替先 | 理由 |
|------------|-----------|------|
| Claude | Codex (gpt-5.4) | 深い推論・設計判断が得意。reasoning_effort: xhigh で集中分析 |
| Claude | Gemini | 1M コンテキストで広い視野。コードベース全体の依存関係を俯瞰 |
| Codex | Claude | 幅広い実装パターン。Codex の推論が深すぎて実用的でない場合 |

**既存の自動切替:**
- `error-to-codex.py`: エラー時に自動で Codex に委譲（実装済み）
- `suggest-gemini.py`: 大規模分析が必要な場合に Gemini を提案（実装済み）

**注意:** 収束（複数モデルが同じ結論に達する）は盲点リスクの兆候でもある。全モデルが失敗する場合は問題の前提自体を疑う。

出典: 逆瀬川 "Coding Agent Workflow 2026" — AI on AI Review セクション

## Harness Optimization Strategy Comparison

| 特性 | Meta-Harness (Lee+ 2026) | DGM-H / Hyperagents (arXiv:2603.19461) |
|------|--------------------------|----------------------------------------|
| **目的** | 既存ハーネスの改善 | ゼロからのタスク解決 |
| **探索戦略** | 線形反復（全履歴保持） | 再帰的ノード分割 + アーカイブ |
| **履歴管理** | 全候補をFS保持、grepで選択的アクセス | 高パフォーマンスバリアントを選択保存、残りは破棄 |
| **トークンコスト** | 高い（中央値82ファイル/回参照） | 中程度（分岐探索で必要な部分のみ） |
| **強み** | 因果推論に必要な情報が欠損しない | 線形改善が飽和した後の分岐探索 |
| **弱み** | 履歴肥大化でFS探索コスト増大 | 破棄した候補の知見が失われる |
| **AutoEvolve での位置** | Rule 13（FS保持+選択的アクセス）、Rule 32（cross-model検証） | Rule 31（Archive-Based Exploration） |

> 出典: Neural AVB ブログ記事 "Meta-Harness - Automated model harness optimization" (2026-04) の比較分析。AutoEvolve は両方の戦略を状況に応じて使い分ける: 通常改善 → Meta-Harness 方式、飽和検出後 → DGM-H 方式。

## Cross-Domain Transfer Candidates

> Hyperagents (arXiv:2603.19461): ドメイン固有の改善パターンが別ドメインに60-80%転移する。
> `scripts/learner/cross-domain-mapper.py` の出力を手動レビューし、有効な転移候補をここに記録する。

| date | source_domain | target_domain | pattern | status |
|------|--------------|---------------|---------|--------|
| — | — | — | (初期エントリなし。cross-domain-mapper 実行後に追記) | — |

## Meta-Harness Transfer Evidence

> Lee et al. 2026 "Meta-Harness": 単一ハーネスが5つの異なるモデル（Opus 4.6, Sonnet 4.5, Haiku 4.5, GPT-5.4, Gemini 2.5 Pro）に転移し、平均 +4.7pt の改善を達成。

**意味**: 良いハーネス設計は model-agnostic。特定モデルに過学習した最適化は転移しない。

**スキル改善への示唆**:
- A/B テストで +3pp 以上の改善 → 異なるモデルで smoke test を実施（improve-policy Rule 32）
- cross-model delta が -5pp 以上低下 → model-specific 過学習の疑い → revert 検討
- ハーネス設計の改善は「全モデルで使える」ことを目標にする

---

## Archive

60日以上経過したエントリをここに移動する。

<!-- 現時点ではアーカイブ対象なし -->
