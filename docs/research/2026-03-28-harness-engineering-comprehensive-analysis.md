# Harness Engineering 包括的調査レポート

> 調査日: 2026-03-28
> 対象: 33記事（英語19 + 日本語11 + スライド3）
> 手法: 6並列サブエージェントによるマルチソース統合分析

---

## Executive Summary

Harness Engineering は、2026年初頭に OpenAI の Ryan Lopopolo と Mitchell Hashimoto によって独立に結晶化された、AI エージェント時代のエンジニアリングパラダイムである。その核心は**「エンジニアの仕事はコードを書くことではなく、エージェントが確実に正しいコードを生産する環境を設計すること」**という役割転換にある。

本調査では33記事を横断分析し、以下の構造で知見を統合した:

1. **定義と起源**: Prompt → Context → Harness の3段階進化
2. **構成要素**: 5つの柱（ツールオーケストレーション、ガードレール、フィードバックループ、観測可能性、Human-in-the-Loop）
3. **実践と成果**: 同一モデルでハーネスのみで 42%→78% のスコア変動、LangChain +13.7pp
4. **批評と限界**: レガシー適用困難、制御の幻想、ハーネス負債
5. **日本での受容**: 6週間で紹介→翻訳→独自発展のサイクル完結

---

## 第1章: 定義と起源

### 1.1 「ハーネス」の語源と概念形成

「ハーネス（harness）」は馬具（手綱）のメタファーに由来する。馬の力を制御して有用な仕事に変えるように、AI エージェントの能力を制御し、信頼性の高い成果に変換するための仕組みである。

**概念の結晶化は2つの独立した到達点から:**

| 人物 | 時期 | アプローチ | 規模 |
|------|------|-----------|------|
| **Ryan Lopopolo** (OpenAI) | 2025後半〜2026/2 | 初日から「人間0行」制約で大規模実証 | 3→7人、100万行、1,500 PR |
| **Mitchell Hashimoto** (Ghostty) | 2026/2 | 6段階の漸進的AI導入モデル | 個人開発者 |

**核心哲学（原典から）:**

> "Humans steer. Agents execute."
> "The horse is fast. The harness is everything."
> "The bottleneck is usually not the agent's ability to write code. It's the quality of the environment."
> "Anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent never makes that mistake again." — Hashimoto

### 1.2 Prompt → Context → Harness の進化

| 観点 | Prompt Engineering (2022-2024) | Context Engineering (2025) | Harness Engineering (2026-) |
|------|-------------------------------|---------------------------|----------------------------|
| **核心の問い** | 何を聞くか | 何を渡すか | システム全体をどう設計するか |
| **操作対象** | 単一プロンプト | コンテキストウィンドウ | エージェントの実行環境全体 |
| **時間軸** | 単発リクエスト | 単一セッション | セッション横断・永続的 |
| **人間の役割** | 質問者 | 情報キュレーター | アーキテクト・品質ゲートキーパー |
| **包含関係** | ハーネスの一部 | ハーネスの一部 | 上位概念 |

**メタファーの体系:**

| メタファー | モデル | コンテキスト | ハーネス | 出典 |
|-----------|--------|------------|---------|------|
| コンピュータ | CPU | RAM上のデータ | OS | Hightower |
| 自動車 | エンジン | 燃料・ダッシュボード | ステアリング・ブレーキ | Bouchard |
| オフィス | — | メール+添付 | オフィス設計全体 | Epsilla |
| 馬具 | 馬 | — | 手綱・鞍 | 原義 |

### 1.3 包含構造

```
Harness Engineering（全体概念）
├── Context Engineering
│   ├── Reusable Prompts（CLAUDE.md, AGENTS.md, Rules）
│   ├── Context Interfaces（Tools, MCP, Skills）
│   └── Workspace Files（コードベース自体）
├── Architectural Constraints（リンター、構造テスト、CI）
├── Feedback Loops（自己検証、評価エージェント）
├── Observability（アクションログ、トークン使用量）
├── Human-in-the-Loop（承認ゲート、エスカレーション）
└── Garbage Collection（定期的エントロピー対策）
```

---

## 第2章: 構成要素の詳細

### 2.1 OpenAI の実践（Lopopolo, 5ヶ月・100万行）

#### AGENTS.md 設計
- **ルート**: ~100行（理想60行以下）。「百科事典ではなく目次」
- **サブディレクトリ**: 計88ファイル。各サブシステムに1つ
- **Progressive Disclosure の4原則**: Context Crowding（トークン浪費）、Non-guidance from Over-guidance（過剰指示で指針喪失）、Instant Rot（機械検証不可な記述の即座の腐敗）、Undetectable Drift
- **AGENTS.md 自体も Codex が生成**（ブートストラップ問題を自己解決）

#### カスタムリンターと機械的強制
- レイヤードアーキテクチャ: `Types → Config → Repo → Service → Runtime → UI`
- 依存方向は前方のみ。逆方向は CI でブロック
- **エラーメッセージ = エージェントへの修正指示**: `"Error: Service layer cannot import from UI layer. Move this logic to a Provider. See docs/ARCHITECTURE.md#layers"`
- リンター自体もエージェントが生成

#### ドキュメントガーデニング
- 専用リンターがクロスリンクと構造を検証
- CI がコードとドキュメントの鮮度乖離をチェック
- 定期的「ガーデニングエージェント」が古いドキュメントをスキャン→自動修正 PR

#### Ralph Wiggum Loop（自律バグ修正）
```
バグ再現 → ビデオ記録 → 修正 → 検証 → 2本目ビデオ → PR
→ フィードバック対応 → ビルド修復 → エスカレーション（必要時のみ）→ マージ
```

#### 技術的負債管理
- 初期: 毎週金曜（週20%）を「AI スロップ」清掃に充てたが**スケールしなかった**
- 解決: ゴールデンプリンシプルのエンコード → GC 方式に移行

### 2.2 Anthropic の実践

#### Generator + Evaluator（GAN 着想）

| エージェント | 役割 |
|---|---|
| **Planner** | 1-4文プロンプト → 詳細プロダクト仕様 |
| **Generator** | 仕様に基づくイテレーティブ実装 |
| **Evaluator** | Playwright MCP でライブページをナビゲート・採点 |

> "スタンドアロンの評価者を懐疑的にチューニングする方が、生成者に自己批判させるより遥かに扱いやすい"

**主観的品質の4次元評価**: Design quality, Originality（"AI slop" を明示的にペナルティ）, Craft, Functionality

#### Initializer + Coding Agent 分離
- **Initializer**: 初回セッションのみ。init.sh, progress.txt, feature list JSON を生成
- **Coding Agent**: 以降の全セッション。1セッション1フィーチャー
- **JSON > Markdown**: モデルが不適切に書き換えにくいため
- **コンテキストリセット > コンパクション**: Sonnet 4.5 はコンテキスト限界接近で早期終了行動を示す

### 2.3 LangChain のベンチマーク改善

| 構成 | Terminal Bench 2.0 |
|---|---|
| ベースライン | 52.8% |
| xhigh reasoning のみ | 53.9%（タイムアウト多発） |
| high reasoning のみ | 63.6% |
| **Reasoning Sandwich (xhigh→high→xhigh)** | **66.5%** |

**改善を実現した4手法:**
1. **Self-Verification Loop**: 4フェーズ（計画→構築→検証→修正）+ PreCompletionChecklist
2. **Context Injection Middleware**: 起動時にディレクトリ構造+ツール発見
3. **Loop Detection**: ファイル毎の編集回数追跡、N回後に再考を注入
4. **Reasoning Sandwich**: 計画=xhigh、実装=high、検証=xhigh

### 2.4 Codex App Server のアーキテクチャ

- **MCP を試して却下**: ストリーミング diff・承認フロー・スレッド永続化が MCP に適合せず
- **JSON-RPC 2.0 over stdio (JSONL)** を採用
- 3プリミティブ: **Item**（原子単位）、**Turn**（作業単位）、**Thread**（永続セッション）
- `thread/fork` で `ephemeral: true` の一時分岐が可能
- `personality` パラメータ: `"friendly"` / `"pragmatic"` / `"none"`
- **LSP のエージェント版** として設計

---

## 第3章: 批評的視点と限界

### 3.1 Böckeler の構造的批評（Martin Fowler 系列）

**評価点:**
- 反復的アプローチ（失敗をシグナルとしてハーネスにフィードバック）
- Chad Fowler の "Relocating Rigor"（厳密さの移動先）
- 5ヶ月の持続的投資（安易な「AI で即解決」への反証）

**疑問点:**
| 批判 | 詳細 |
|------|------|
| **機能テスト欠如** | 内部品質に焦点、機能正常性・ユーザー行動検証の記述が**欠落** |
| **前提条件の特殊性** | 100万行・OpenAI自身・ゼロからの構築という理想的条件 |
| **レガシー適用困難** | 後付けハーネス = 未整備プロジェクトへの静的解析 = **アラート洪水** |
| **テンプレートの二の舞** | フォーク・同期問題の再現リスク |
| **テックスタック収束** | 開発者の言語選好が意思決定から排除される世界 |

### 3.2 「制御の幻想」（Illusion of Control）

> "コンテキストエンジニアリングは有用な結果の確率をかなり高めることができる。しかし LLM では何も確実にはできない。確率で考え、仕事に適した人間の監視レベルを選ぶべきだ" — Böckeler

「エンジニアリング」は決定論的結果を連想させるが、LLM ベースのシステムは**本質的に確率的**。

### 3.3 人間-エージェント協調の3モデル（Kief Morris）

| モデル | 人間の位置 | メリット | リスク |
|--------|-----------|---------|--------|
| **Out of the loop** | Why Loop のみ | 成果に集中 | 内部品質崩壊 |
| **In the loop** | 逐一検査 | 直接品質貢献 | ボトルネック化 |
| **On the loop** ★推奨 | ハーネスを設計・管理 | スケーラブル | 初期投資。確率的改善 |

**核心的区別:**
- In the loop: 結果が不満 → **成果物を直接修正**
- On the loop: 結果が不満 → **成果物を生んだハーネスを修正**

### 3.4 Agentic Flywheel（Morris の最も野心的なビジョン）

```
Stage 1: 人間がインタラクティブにレビュー → 改善指示
Stage 2: エージェントが改善提案をバックログに追加 → 人間が優先度判断
Stage 3: リスク/コスト/利益スコア → 基準を満たす提案は自動承認
Stage 4: 「堅牢で、おそらくアンチフラジャイルな、自己改善するシステム」
```

### 3.5 未解決の構造的問題

1. **ブラウンフィールド問題**: 成功事例はすべてグリーンフィールド。レガシーへの適用方法は未確立
2. **ハーネス負債**: ハーネス自体がバグとドリフトを蓄積する（Bouchard）
3. **人間の注意力がボトルネック**: モデル能力でもコストでもなく、監督能力がスケーリング制約
4. **エントロピーの質的差異**: エージェント生成コードのエントロピーは人間のそれと異なる形で蓄積
5. **Bitter Lesson**: モデル能力向上でハーネスの一部が不要になる可能性（剥がす前提の設計）

---

## 第4章: ベストプラクティスと定量データ

### 4.1 統合ベストプラクティス（全33記事横断）

#### アーキテクチャ
| # | プラクティス | 出典 |
|---|---|---|
| 1 | **生成と評価を分離** — 自己評価バイアス排除 | Anthropic |
| 2 | **JSON > Markdown でステート管理** — 書き換え防止 | Anthropic |
| 3 | **Build to Delete** — 次モデルで不要になるコードを前提にモジュラー設計 | Schmid |
| 4 | **コンテキストリセット > コンパクション** | Anthropic |
| 5 | **多層防御**: 型→静的解析→テスト→AIレビュー→人間 | 梶川/TechBowl |

#### AGENTS.md / CLAUDE.md 設計
| # | プラクティス | 出典 |
|---|---|---|
| 6 | **60行以下** — ETH Zurich: 指示増→14-22%推論トークン増、成功率改善なし | HumanLayer |
| 7 | **Progressive Disclosure** — 普遍的指示のみ。条件付きはスキル/フックに分離 | OpenAI, HumanLayer |
| 8 | **ポインタの腐敗は検出可能、記述の腐敗は沈黙** | 逆瀬川 |
| 9 | **IFScale閾値**: 150-200指示でprimacy bias。システムプロンプト~50指示を含む | 逆瀬川 |

#### 評価・検証
| # | プラクティス | 出典 |
|---|---|---|
| 10 | **Reasoning Sandwich**: 計画=xhigh、実装=high、検証=xhigh | LangChain |
| 11 | **PreCompletionChecklist** — モデルは自発的にテストしない | LangChain |
| 12 | **ブラウザ自動化検証** — curl/ユニットテストでは不十分 | Anthropic |
| 13 | **Few-shot でのスコアキャリブレーション** | Anthropic |
| 14 | **Chrome DevTools MCP** — CI合格では検出できないUI動作を確認 | 梶川 |

#### 運用
| # | プラクティス | 出典 |
|---|---|---|
| 15 | **成功は沈黙、失敗のみ出力** — コンテキスト節約 | HumanLayer |
| 16 | **CLI > MCP（既知ツール）** — grep/jq との合成可能性が高い | HumanLayer |
| 17 | **サブエージェントはコンテキストファイアウォール** | HumanLayer |
| 18 | **ループ検出**: stderr正規化→3回でSIGTERM | Tsucchi |
| 19 | **エスカレーションラダー**: 同一違反3回で昇格(L1→L4) | nogataka |
| 20 | **失敗時最大3回リトライ→人間** — 無限ループ防止 | 梶川 |

### 4.2 アンチパターン集

| # | アンチパターン | 理由 | 出典 |
|---|---|---|---|
| 1 | **自己評価バイアス** | 問題を見つけても「大したことない」と自己説得 | Anthropic |
| 2 | **ドゥームループ** | 同一ファイルに10回以上編集を繰り返す | LangChain |
| 3 | **MCP ツール過剰供給** | ツール定義でコンテキスト5-7%消費、指示予算枯渇 | HumanLayer, Tsucchi |
| 4 | **LLM 生成 agentfile** | パフォーマンス悪化+コスト20%増 | ETH Zurich |
| 5 | **巨大制御フロー** | 次モデルで陳腐化。モデルに計画させる | Schmid |
| 6 | **フルテストスイート実行** | 5分超でコンテキスト溢れ→ハルシネーション | HumanLayer |
| 7 | **コードベース概要の注入** | 「ディレクトリ一覧は全く役立たなかった」 | HumanLayer |
| 8 | **過剰防御コード** | 不要なnullチェック等をエージェントが防御的に追加 | 梶川 |
| 9 | **プロンプト言語が出力を束縛** | "museum quality" → 視覚的収束、多様性喪失 | Anthropic |
| 10 | **Markdown 進捗管理** | エージェントがタスク完了を勝手に書き換える | nogataka |

### 4.3 定量データ総覧

| 指標 | 値 | 出典 |
|---|---|---|
| **OpenAI 規模** | 100万行 / 1,500 PR / 5ヶ月 / 3→7人 | Lopopolo |
| PR スループット | 3.5 PR/エンジニア/日 | Lopopolo |
| 推定工期比 | 手作業の約1/10 | Lopopolo |
| AGENTS.md 総数 | ルート1 + サブ88ファイル | Lopopolo |
| **ハーネスによるスコア変動** | **42% → 78%**（同一モデル） | Epsilla |
| Terminal Bench 改善 | 52.8% → 66.5% (+13.7pp) | LangChain |
| **ハーネス vs モデル効果** | ハーネス変更22pt / モデル交換1pt | Morph (via 逆瀬川) |
| ソロ vs ハーネス（コスト） | $9 vs $200（質的飛躍） | Anthropic |
| DAW 実験 | $124.70 / 3h50m | Anthropic |
| agentfile の推論トークン増 | 14-22% | ETH Zurich |
| LLM生成 agentfile コスト増 | 20%+ | ETH Zurich |
| Vercel AGENTS.md 圧縮 | 40KB→8KB、100%パス率維持 | 逆瀬川 |
| Vercel ツール削減 | 80%削除で性能向上 | Schmid |
| ツール定義のコンテキスト消費 | 5-7% | Tsucchi |
| Playwright MCP トークン | 114K tokens | 逆瀬川 |
| agent-browser トークン | 5.5K tokens | 逆瀬川 |
| RAG-MCP ツール精度改善 | 13.62% → 43.13% | Gamo (RAG-MCP論文) |
| TechBowl リポジトリ数 | 158アクティブ | 梶川 |
| GMO ルール数 | 12カテゴリ48ルール | nogataka |
| Manus リファクタ頻度 | 6ヶ月で5回 | Schmid |
| IFScale primacy bias 閾値 | 150-200指示 | 逆瀬川 |

---

## 第5章: 日本での受容と独自の貢献

### 5.1 受容の速度と深度

```
2/11  OpenAI原典公開
  ↓ 16日
2/27  KJR020: 翻訳・批判的解説（最速）
  ↓ 3日
3/02  nogataka: 詳細翻訳（222いいね, PV 54,704）
  ↓ 7日
3/09  逆瀬川: 独自ベストプラクティス（53分読了）
  ↓ 2日
3/11  blog.est.co.jp: SE定石との等価性
  ↓ 5日
3/16  kaeken: 階層的分類
  ↓ 3日
3/19  @IT: 大手メディア報道
  ↓ 5-7日
3/24-25 nogataka入門, Tsucchi実装報告, Aochan0604 Fowler再考, Gamo/梶川スライド
```

**6週間で「紹介→翻訳→実践→独自発展」のサイクルが完結。**

### 5.2 日本独自の解釈フレーム

#### (a)「既知のSEプラクティスの AI 時代版」
blog.est.co.jp と Aochan0604 に共通する脱神話化:
- コンテキストE = ドキュメント整備
- アーキテクチャ制約 = 静的解析
- フィードバックループ = DevOps
- エントロピー管理 = 技術的負債管理

> "名前が付いたことで議論・体系化が可能になった" — naming の価値を認めつつ本質は従来SE

#### (b)「構造の門番 vs 意味の番人」（Aochan0604）
ハーネスは構造的整合性を守るが、ビジネスロジックの正しさ（意味）は保証しない。日本の品質管理文化（ISO内部品質/外部品質の区別）と親和性が高いフレーミング。

#### (c)「剥がす前提の過渡的技術」（Aochan0604）
Bitter Lesson を援用。英語圏の議論ではあまり見られない日本発の独自見解。YAGNI と実用的必要性のバランス。

#### (d)「ローカルオーケストレーター」（Tsucchi）
GHA 依存を脱却した TypeScript 常駐プロセス。Explore/Implement/Review の3フェーズ分割、ループ検出、autoFixable フラグ、launchd 自動化。

### 5.3 日本独自の実装パターン

| パターン | 著者 | 内容 |
|---------|------|------|
| エスカレーションラダー | nogataka | 同一違反3回で L1→L4 昇格 |
| ローカルオーケストレーター | Tsucchi | GHA→TypeScript常駐+launchd |
| 言語別リンター選定ガイド | 逆瀬川 | Oxlint+Biome, Ruff, golangci-lint, Clippy |
| Hooks 4パターン分類 | 逆瀬川 | Safety/Quality/Completion/Observability |
| 5エージェント体制 | 梶川 | TDD/code/perf/spec/task-issue |
| 再現実験リポジトリ公開 | 逆瀬川 | claude-hook-experiment |
| コンテキストE 7要素分類 | Gamo | UI/UX, 推論プリセット, RAG, 分割, 動的取得, 圧縮, キャッシュ |

---

## 第6章: 今後の展望と未解決課題

### 6.1 収束と標準化

- **AGENTS.md / CLAUDE.md**: 事実上の業界標準として収束中
- **MCP**: ツール接続の標準化。Stripe は 400+ ツールを MCP 経由で接続
- **Skills が Slash Commands と Rules を吸収**: 機能数の減少予測（Böckeler: storming → norming）
- **Hooks の普及遅れ**: 最も決定論的だが採用率が最低。Cursor が最近対応開始

### 6.2 フレームワーク層の二分化

> "フレームワーク層は消滅するのではない。分裂する。知性はモデルに移動し、インフラはハーネスに移動する" — Greyling

### 6.3 残された問い

1. **レガシーコードベースへの適用**: 段階的導入、ベースライン確立、スコープ限定は提案されているが実証事例なし
2. **ハーネスの組織横断メンテナンス**: サービステンプレートと同じフォーク・同期問題が再現するか
3. **モデル進化との関係**: ハーネスの各コンポーネントは「モデルが単独でできないことへの仮定をエンコード」している。その仮定はモデル進化で無効化される
4. **テックスタック収束**: 「どの言語で書くか」より「どのスタックのハーネスが充実しているか」が選択基準に
5. **エネルギーコスト**: ハーネスは計算量を増やす（Evaluator、リトライ、検証ループ）。環境コストとのトレードオフ

---

## 第7章: 小さいが価値ある知見（全サブタスク統合）

### 用語・概念

1. **Chad Fowler の "Relocating Rigor"** — 厳密さがコード記述からハーネス設計に移動
2. **Ralph Loop の原義** — 「放置して待つ」ではなく「操舵しながらループ」が本来の意味
3. **「ガベージコレクション」としてのエージェント巡回** — エントロピー対策の日常化
4. **「経験豊富な下請業者」メタファー** — エージェントはジュニアではなく、腕は良いが方向づけが必要な外注先
5. **ハーネスのバズワード化** — 「2週間以内に単純な LLM レビューエージェントを "ハーネス" と呼ぶ」(Böckeler)

### 技術的発見

6. **Codex のモデル・ハーネス共進化** — Codex = Model + Harness + Surfaces。ツール使用は後付けではなくモデルの学習方法の一部
7. **ファイル通信パターン** — Generator-Evaluator 間の通信はファイル経由（一方が書き、他方が読む）
8. **イテレーションの非線形性** — スコアは常に線形改善せず、中間イテレーションが最良の場合あり
9. **Puppeteer MCP の限界** — ブラウザネイティブの alert モーダル処理が困難
10. **フック終了コード規約** — `0` = 沈黙の成功、`2` = エラー表示+再エンゲージ

### 運用ノウハウ

11. **二重基準設計** — 人間には `--no-verify` 許可、エージェントには禁止
12. **サブエージェントの再帰生成リスク** — MCP 経由で孫エージェント生成 → 「伝言ゲーム」
13. **テスト削除禁止の明示的指示** — エージェントへの明示的禁止が必要
14. **実装複雑度のエスカレーション** — ラウンドを重ねるとエージェントが野心的な解に手を伸ばす
15. **初回スキャフォールディングの決定的重要性** — Initializer への投資が後続全体に指数的リターン

### 日本固有

16. **ループ検出の正規化手法** — タイムスタンプ・行番号除去 `.replace(/\d{4}-\d{2}-\d{2}[\sT][\d:.]+/g, '')` (Tsucchi)
17. **spec-reviewer の「過剰防御排除」** — 不要な null チェック等を積極的に除去 (梶川)
18. **deptrac + dependency-cruiser** — PHP/TS で異なる依存チェッカーを使い分け (梶川)
19. **CAG（Context Augmented Generation）** — 小規模ドメインでは RAG より効率的 (Gamo)
20. **NotebookLM でスライド自動生成** — AI ツールで AI 概念を整理するメタ実践 (abenben)

---

## 調査メタデータ

### ソース取得状況

| カテゴリ | 総数 | 完全取得 | メタデータ+補完 | 取得不可 |
|---------|------|---------|----------------|---------|
| 英語一次情報 | 7 | 7 | 0 | 0 |
| 英語補足記事 | 12 | 10 | 1 (Medium paywall) | 1 |
| 日本語記事 | 11 | 9 | 2 (note.com 動的レンダリング) | 0 |
| スライド | 3 | 2 | 0 | 1 (画像のみ) |
| **合計** | **33** | **28** | **3** | **2** |

### 使用モデル

| サブタスク | モデル | 記事数 |
|-----------|--------|--------|
| 1. 起源と定義 | claude -p | 3 |
| 2. 進化史と概念整理 | claude -p | 5 |
| 3. 批評的視点 | claude -p | 3 |
| 4. 実践と定量成果 | claude -p | 8 |
| 5. 日本語記事前半 | claude -p | 5 |
| 6. 日本語記事後半+スライド | claude -p | 9 |
| 7. 横断統合 | 手動統合 | 全体 |

---

## 参考文献（全33ソース）

### 英語一次情報
1. Lopopolo, R. (2026-02-11). "Harness engineering: leveraging Codex in an agent-first world." OpenAI. https://openai.com/index/harness-engineering/
2. Böckeler, B. (2026-02-17). "Harness Engineering." martinfowler.com. https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html
3. Rajasekaran, P. (2026-03-24). "Harness design for long-running application development." Anthropic. https://www.anthropic.com/engineering/harness-design-long-running-apps
4. Anthropic. (2025-11-26). "Effective harnesses for long-running agents." https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
5. Hashimoto, M. (2026-02-05). "My AI Adoption Journey." https://mitchellh.com/writing/my-ai-adoption-journey
6. Guo, C. (2026-02-22). "The Emerging 'Harness Engineering' Playbook." Artificial Ignorance. https://www.ignorance.ai/p/the-emerging-harness-engineering
7. LangChain. (2026-02-17). "Improving Deep Agents with harness engineering." https://blog.langchain.com/improving-deep-agents-with-harness-engineering/

### 英語補足記事
8-19. Bouchard, Greyling, HumanLayer, Schmid, Hightower, nxcode, Willison, Spillwave, Morris, Böckeler(context), OpenAI(app-server), Epsilla

### 日本語記事
20-30. nogataka(2), 逆瀬川, Tsucchi, KJR020, blog.est, note/aiedgerunner, kaeken, Aochan0604, note/m2ai, @IT

### スライド
31-33. Gamo, 梶川, abenben
