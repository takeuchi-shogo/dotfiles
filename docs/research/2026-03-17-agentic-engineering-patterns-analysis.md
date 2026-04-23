---
status: active
last_reviewed: 2026-04-23
---

# Simon Willison "Agentic Engineering Patterns" 深掘り調査レポート

**調査日**: 2026-03-17
**ソース**: https://simonwillison.net/guides/agentic-engineering-patterns/
**関連**: [HN Discussion](https://news.ycombinator.com/item?id=47243272), [Substack](https://simonw.substack.com/p/agentic-engineering-patterns)

---

## 1. ガイド概要

Simon Willison（Django 共同開発者、datasette 作者）による、コーディングエージェント時代のエンジニアリングパターン集。全13チャプター、6セクション構成。Claude Code・OpenAI Codex・Gemini CLI などのコーディングエージェントから最大の成果を得るための実践的パターンを収録。

### ガイド構造

| セクション | チャプター | 概要 |
|---|---|---|
| **Principles** | 1-5 | 定義、コストモデル変化、知識の蓄積、品質向上、アンチパターン |
| **Getting Started** | 6 | エージェントの仕組み（LLM + system prompt + tools in a loop） |
| **Testing & QA** | 7-9 | Red/Green TDD、テスト先行、手動テスト |
| **Understanding Code** | 10-11 | Linear Walkthroughs、Interactive Explanations |
| **Annotated Prompts** | 12 | GIF最適化ツール（実例付きプロンプト解説） |
| **Appendix** | 13 | 再利用可能プロンプト集 |

---

## 2. 全チャプター詳細分析

### Ch.1: What is Agentic Engineering?

**核心定義**: "コーディングエージェントの支援を受けてソフトウェアを開発する実践"

- **エージェント = LLM + system prompt + tools in a loop**
- コード実行能力が決定的差異 — 実行できなければ LLM の出力は限定的価値しかない
- Vibe Coding（Karpathy, 2025年2月）とは明確に区別: Vibe Coding = レビューなしのプロトタイプ品質、Agentic Engineering = プロダクション品質への意図的洗練
- **人間の役割**: 何を作るか決める、トレードオフを判断する、ツールを提供する、結果を検証する、指示を更新する
- **重要な洞察**: "LLM は過去のミスから学ばないが、エージェントは学べる — 我々が意図的に指示とツールハーネスを更新すれば"

### Ch.2: Writing Code is Cheap Now

**核心主張**: コード生産コストの劇的低下がソフトウェアエンジニアリングの前提を覆す

- **マクロレベル**: プロジェクトの設計・見積もり・計画の前提が変わる
- **ミクロレベル**: リファクタリング・ドキュメント・テスト・ツール作成のコスト判断が変わる
- **"良いコード"の9特性**: (1)機能的正確性 (2)検証可能性 (3)問題整合性 (4)エラーハンドリング (5)シンプル・最小 (6)テスト保護 (7)最新ドキュメント (8)将来変更の親和性(YAGNI尊重) (9)品質属性(a11y,セキュリティ,テスト可能性,スケーラビリティ,可観測性,信頼性,保守性,ユーザビリティ)
- **マインドセット転換**: "作る価値がない" と直感が言ったら、非同期エージェントセッションでプロンプトを投げる。最悪10分後にトークンの無駄だったと分かるだけ

### Ch.3: Hoard Things You Know How to Do

**核心パターン**: 動くコード例の個人リポジトリを構築し、エージェントの入力素材にする

- Blog、TIL（Today I Learned）、GitHub リポジトリ、単一ページ HTML ツールで蓄積
- **"一度解決すれば二度と解く必要がない"** — エージェントが過去の解決策を再利用
- **ケーススタディ**: PDF.js + Tesseract.js を組み合わせてブラウザ内 OCR ツールを数分で構築
- エージェントはインターネット、ローカルファイル、公開リポジトリから既存パターンを発見・適用できる

### Ch.4: AI Should Help Us Produce Better Code

**核心主張**: AI で低品質コードを速く出すのは意図的な選択。むしろ「より良いコード」を出すために使うべき

- **エージェントに最適なタスク**: API リデザイン、命名規則統一、重複排除、大ファイル分割 — "シンプルだが時間がかかる" 作業
- **コスト-便益シフト**: 改善コストが激減 → 軽微なコードスメルへのゼロトレランス態度が可能に
- **Compound Engineering パターン** (Every社): 各プロジェクト完了時に「何がうまくいったか」を記録し、将来のエージェント実行に活用。反復改善が複利的に効く
- **探索的プロトタイピング**: Redis の負荷テストなど、複数ソリューションを同時テストして技術選定の判断材料を低コストで取得

### Ch.5: Anti-patterns: Things to Avoid

**唯一のアンチパターン（現時点）**: レビューしていないコードを協力者に押し付ける

- 数百〜数千行のエージェント生成コードをレビューなしで PR するな
- **品質PRの4要件**: (1)動作確信 (2)適切なスコープ（小さなPR複数が望ましい） (3)コンテキスト説明 (4)PR説明文の検証
- **デューデリジェンスの証拠**: 手動テストノート、実装選択のコメント、スクリーンショット/動画

### Ch.6: How Coding Agents Work

**技術的基盤の解説**: LLM + system prompt + tools in a loop

- **LLM**: テキスト補完エンジン。トークンベース。ステートレス（毎回全会話履歴を再送）
- **トークンキャッシュ**: 繰り返しプレフィックスの計算を再利用してコスト最適化
- **ツール/Function Calling**: 特別なプロンプト構文でツールを定義し、結果をプロンプトにフィードバック
- **System Prompt**: 数百行の隠しプロンプトで動作を制御（OpenAI Codex の system prompt が例示）
- **Reasoning/Thinking**: 2025年の新機能。応答前の拡張処理時間でデバッグ等に有効

### Ch.7: Red/Green TDD

**核心パターン**: "red/green TDD" の一言でエージェントに TDD を指示

- **Red フェーズ**: テストが失敗することを確認（スキップすると「既に通るテスト」のリスク）
- **Green フェーズ**: 実装でテストを通す
- **2つのリスク軽減**: (1)壊れたコード生成の防止 (2)不要コード生成の防止
- プロンプト例: "Build a Python function to extract headers from a markdown string. Use red/green TDD."

### Ch.8: First Run the Tests

**核心パターン**: 既存プロジェクトでのセッション開始時、最初にテストを実行する

- **古い言い訳はもう通用しない**: テスト作成が高コスト・書き直しが面倒 → エージェントが数分で対応
- **3つの目的**: (1)テストスイートの存在を知らせる (2)テスト数でプロジェクト規模を把握 (3)テストファースト思考を確立
- プロンプト例: "First run the tests" / "Run 'uv run pytest'"

### Ch.9: Agentic Manual Testing

**核心原則**: テストに通っても意図通りに動くとは限らない。手動テストで補完

- **Python**: `python -c "..."` でエッジケースを素早くテスト
- **Web API**: `curl` でJSON APIを叩く。"explore" と指示して包括的テストを促す
- **ブラウザ自動化**: **Playwright**（最強）、agent-browser（Vercel、CLI wrapper）、Rodney（Willison作、Chrome DevTools Protocol）
- **Showboat**: テストワークフローを Markdown 文書にキャプチャするツール（note / exec / image コマンド）
- **統合パターン**: 手動テストで問題発見 → red/green TDD で修正 → 永続的テストカバレッジ確保

### Ch.10: Linear Walkthroughs

**核心パターン**: エージェントにコードベースの構造化ウォークスルーを作成させる

- **3つのユースケース**: (1)学習が必要な既存コード (2)時間が経った自分のコード (3)Vibe Coding で作ったコード
- **Showboat アプローチ**: `showboat note`（Markdownコメント）+ `showboat exec`（シェルコマンド実行・記録）
- **重要**: コード引用は `sed/grep/cat` で取得させる（手動コピーはハルシネーションリスク）
- **学習効果**: "SwiftUI アプリの構造と Swift 言語の詳細について多くを学んだ" — AI 時代でもスキル構築は可能

### Ch.11: Interactive Explanations

**核心概念**: **認知的負債** (Cognitive Debt) — コードの動作原理を理解できない負担

- AI が書いたコードの内部動作を理解できなくなると、将来の機能計画への自信を失う
- **解決策**: エージェントにインタラクティブな説明ツールを作らせる
- **ケーススタディ**: Word Cloud のアルゴリズム（アルキメデス螺旋配置）をアニメーション付き HTML で可視化
  - フレーム単位アニメーション、衝突検出の可視化、再生制御、PNG エクスポート
- **推奨**: 複雑なアルゴリズムの理解には、技術文書よりインタラクティブ可視化が効果的

### Ch.12: GIF Optimization Tool (Annotated Prompt)

**実例付きプロンプト解説**: Gifsicle を WebAssembly にコンパイルしたブラウザ内GIF最適化ツール

- **プロンプト設計の要点**:
  - ファイル名指定 (`gif-optimizer.html`) でリポジトリコンテキストを暗黙活用
  - "Compile gifsicle to WASM" の一文が複雑なツールチェーンを起動
  - UI パターン（ドラッグ&ドロップ）を既存ツールから借用
  - Rodney でブラウザ自動化テスト → CSS specificity バグを発見・修正
- **エージェントへの信頼**: 30年の歴史を持つ Gifsicle は名前だけで十分識別可能。エージェントの「審美眼」もプリセット選択に活用
- **フォローアッププロンプト**: ビルドスクリプト整理、WASM バンドル含有、適切な帰属表示

### Ch.13: Prompts I Use

**3カテゴリの再利用プロンプト**:

1. **Artifacts** (HTML/JS プロトタイピング):
   - React 回避、vanilla JS + CSS、最小依存
   - `* { box-sizing: border-box; }` で開始
   - 16px フォント、Helvetica、2スペースインデント
   - 理由: アーティファクトからコードをコピーして静的ホスティングに配置可能にするため

2. **Proofreader** (校正):
   - 6項目チェック: スペル、文法、用語反復、論理/事実エラー、弱い論拠、空リンク
   - **厳格な境界**: 意見表明や一人称のコンテンツは著者が書く。LLM はコードドキュメントのみ更新可

3. **Alt Text** (アクセシビリティ):
   - Claude Opus を使用（"alt text のセンスが極めて良い"）
   - スクリーンショット内の全テキストを逐語的に含める
   - モデル生成 alt text は必ず人間がレビュー・編集

---

## 3. HN コミュニティ議論の要点

### 合意点

| トピック | コミュニティの見解 |
|---|---|
| **コードレビューがボトルネック** | Willison 自身も "最も興味深い問題の1つ" と認める。未解決 |
| **テスト/検証は非交渉** | "検証方法がなければループは迷走する" — テストが主要品質ゲート |
| **計画 > コード** | 詳細な仕様・計画を先行させるほど良い結果。"ドラフト文書でのイテレーションに時間を使う" |

### 論争点

| トピック | 賛成派 | 反対派 |
|---|---|---|
| **コードが安くなったら品質基準を下げるべきか** | Willison は試みに示唆 → 直後に自己否定 | "見えないバグは何年も残る" — 品質ゲート必須 |
| **人間の理解は必須か** | 生成コードも理解して "保証" すべき | コードは使い捨て、理解不要 |
| **エージェント開発は本当に速いか** | "ほとんどコードを書かなくなった" | "90%は知識で10%がコーディング" — 知識部分は変わらない |

### 追加パターン（HN発）

- **Proportional Review Governance**: リスクベースの PR ルーティング（認証変更は厳格、設定変更は軽量）
- **Spec-Heavy Workflows**: Living requirement documents をエージェントが繰り返し参照
- **Agent-Driven QA (StrongDM パターン)**: 自律テストエージェントがステージング環境を継続的にテスト
- **Tautological Testing 問題**: LLM が "定義上通る" テストを生成するリスク — ハードコード期待値、論理的に無意味なアサーション

---

## 4. 当ハーネスとの比較分析

### 既に実装済み（強い一致）

| Willison パターン | 当ハーネスの対応 | 状態 |
|---|---|---|
| **Red/Green TDD** | `superpowers:test-driven-development` スキル | 完全一致 |
| **テスト先行** | `completion-gate.py` (Stop hook) がテスト自動検出・実行 | 強化版（自動強制） |
| **エージェント = LLM + prompt + tools** | harness contract 全体がこの前提 | 完全一致 |
| **コードレビュー必須** | `/review` スキル + 並列レビューアー | 強化版（規模スケーリング） |
| **知識の蓄積** | AutoEvolve + MEMORY.md + /eureka + /continuous-learning | 強化版（自動学習ループ） |
| **Compound Engineering** | `/improve` (AutoEvolve) — セッション学習の複利的改善 | 完全一致 |
| **Anti-pattern: レビューなし PR** | `review` 自動起動 + PR セルフレビュー | 自動化済み |
| **仕様先行** | `/spec`, `/spike`, `/epd` | 強化版（EPD統合フロー） |
| **Proportional Review** | 変更規模スケーリング (S/M/L) | 完全一致 |
| **品質属性リスト** | GP-001〜011 + rules/ + references/ | 強化版（自動検出hook付き） |

### 部分的に実装（改善余地あり）

| Willison パターン | 当ハーネスの状態 | ギャップ |
|---|---|---|
| **Manual Testing** | `ui-observer` (Playwright) で部分対応 | curl/python -c による軽量手動テストの体系化が不足 |
| **Linear Walkthroughs** | なし（Explore agent で部分代替） | Showboat 的な構造化ウォークスルー生成の仕組みがない |
| **Interactive Explanations** | なし | 認知的負債の概念と対策が未整備 |
| **Tautological Testing 防止** | `test-analyzer` agent が存在するが限定的 | "定義上通る" テストの自動検出メカニズムが弱い |

### 未実装（新規導入候補）

| Willison パターン | 説明 | 優先度 |
|---|---|---|
| **Cognitive Debt 対策** | AI 生成コードの理解支援（インタラクティブ可視化） | M |
| **Showboat 統合** | ウォークスルー + テスト記録の構造化文書生成 | L |
| **Agent-Driven QA** | ステージング環境での自律テスト（StrongDM パターン） | L |
| **Artifact プロンプト標準化** | vanilla JS + CSS のプロトタイピング規約 | S |

---

## 5. 活かせるもの（即座に適用可能）

### 5-1. "First Run the Tests" をセッション開始プロトコルに組み込む

**現状**: `SessionStart` hook は `session-load.js` のみ。テスト実行は completion-gate（終了時）で強制。
**改善**: セッション開始時に既存テストスイートを実行し、ベースラインを確立するプロンプト注入を検討。

```
推奨アクション: session-load.js の additionalContext に
"If this project has tests, run them first to establish a baseline" を追加
```

### 5-2. Tautological Testing 検出の強化

**現状**: `test-analyzer` agent は存在するが、"定義上通るテスト" の自動検出が弱い。
**改善**: テスト品質チェックに以下のパターンを追加:
- ハードコードされた期待値がソース値と同一
- `assert True` / `assert 1 == 1` 的な無意味アサーション
- テストが実装と同一ロジックを再実装している

### 5-3. "Hoard" パターンの体系化

**現状**: `/eureka` でブレイクスルーを記録、`/continuous-learning` でパターンを蓄積。
**改善**: 「動くコード例のライブラリ」として `references/` に解決済みパターンのインデックスを追加。エージェントが新タスク着手前に参照可能にする。

### 5-4. Manual Testing プロンプトの標準化

**現状**: `ui-observer` は Playwright ベースだが、軽量テスト（curl, python -c）の体系化が不足。
**改善**: `references/` に言語/フレームワーク別の手動テストパターンを追加:
- Python: `python -c "..."` パターン
- Web API: `curl` パターン
- CLI: `/tmp` にデモファイル作成パターン

---

## 6. 改善すべきもの（既存機能の強化）

### 6-1. Cognitive Debt の可視化・管理

Willison の "Interactive Explanations" は、我々のハーネスに欠けている視点。AI 生成コードが増えるほど認知的負債が蓄積する。

**提案**:
- `linear-walkthrough` コマンド/スキルの新設 — エージェントにコードベースの構造化ウォークスルーを生成させる
- 複雑なアルゴリズム実装後に、インタラクティブ説明の生成を推奨するプロンプトヒント

### 6-2. PR 品質のデューデリジェンス証拠

Willison の "手動テストノート・スクリーンショット・実装選択コメント" は、我々の `/github-pr` スキルで強化可能。

**提案**:
- PR テンプレートに "Testing Evidence" セクションを必須化
- `ui-observer` のスクリーンショットを PR 説明に自動添付するワークフロー

### 6-3. "Good Code" の 9 特性チェックリスト

Willison の9特性は GP（Golden Principles）と重複するが、より包括的。特に以下が GP に不足:
- **問題整合性** (正しい問題を解いているか) — Product Reviewer が部分的にカバーだが、spec なしの場合に弱い
- **将来変更の親和性** (YAGNI 尊重しつつ脆くない) — 明示的なチェックがない

---

## 7. 覚えておくべきもの（設計哲学・洞察）

### 7-1. "LLM は学ばないが、ハーネスは学ぶ"

> "LLMs don't learn from their past mistakes, but coding agents can, provided we deliberately update our instructions and tool harnesses."

これは当ハーネスの AutoEvolve の設計根拠そのもの。Willison も同じ結論に到達している。**ハーネスエンジニアリングの正当性を強く裏付ける外部検証**。

### 7-2. Vibe Coding ≠ Agentic Engineering

Willison は明確に区別している。Vibe Coding（Karpathy）= "コードの存在を忘れてプロンプトする"。Agentic Engineering = "意図的にプロダクション品質に洗練する"。我々のハーネスは Agentic Engineering 側に位置する。

### 7-3. コードレビューは未解決問題

HN 議論で Willison 自身が認めた通り、AI 生成コードの大量レビューには確立された解がない。我々の並列レビューアー + 規模スケーリングは先進的だが、根本的な課題（レビューアーも AI）は残る。

### 7-4. Tautological Testing は実際のリスク

HN コミュニティで指摘された "LLM が定義上通るテストを生成する" 問題は、`completion-gate.py` のテスト通過だけでは検出できない。テストの「質」を評価する仕組みが必要。

### 7-5. Spec-Heavy Workflows は効果的

HN の実践者報告: "ドラフト文書でのイテレーションに有意義な時間を使う" ほど成果が良い。我々の `/spec` → `/spike` → `/validate` フローはこの方向に整合している。

### 7-6. "一度解決すれば二度と解く必要がない"

Willison の "Hoard" パターン。これは memory + eureka + continuous-learning の組み合わせで実現可能だが、「動くコード例」のインデックス化がまだ弱い。

### 7-7. コスト感覚の転換

"作る価値がない" → "プロンプト投げてみろ" への転換。非同期エージェントセッションの最悪ケースは「トークンの無駄」。このマインドセットは `/spike` の設計思想と一致する。

---

## 8. アクションアイテム

| # | アクション | 規模 | 優先度 | 対応先 |
|---|---|---|---|---|
| A-1 | session-load.js に "First run the tests" ベースライン確立を追加 | S | High | scripts/lifecycle/ |
| A-2 | test-analyzer に tautological testing 検出パターンを追加 | M | High | agents/test-analyzer.md |
| A-3 | references/ に手動テストパターン集を追加 | S | Medium | references/manual-testing-patterns.md |
| A-4 | "Hoard" パターンの解決済みコード例インデックス検討 | M | Medium | references/ or eureka/ |
| A-5 | linear-walkthrough スキル/コマンドの新設検討 | M | Low | skills/ |
| A-6 | PR テンプレートに Testing Evidence セクション追加 | S | Medium | skills/github-pr/ |
| A-7 | GP に "問題整合性" と "将来変更親和性" の観点追加検討 | S | Low | references/golden-principles.md |

---

## 9. Sources

- [Agentic Engineering Patterns Guide](https://simonwillison.net/guides/agentic-engineering-patterns/)
- [Writing about Agentic Engineering Patterns (Blog)](https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/)
- [Agentic Engineering Patterns (Substack)](https://simonw.substack.com/p/agentic-engineering-patterns)
- [Hacker News Discussion](https://news.ycombinator.com/item?id=47243272)
- [Simon Willison Mastodon (12th chapter)](https://fedi.simonwillison.net/@simon/116235613299250435)
- [Showboat](https://github.com/simonw/showboat)
- [Rodney](https://github.com/simonw/rodney)
- [agent-browser (Vercel)](https://github.com/vercel-labs/agent-browser)
- [Playwright](https://playwright.dev/)
