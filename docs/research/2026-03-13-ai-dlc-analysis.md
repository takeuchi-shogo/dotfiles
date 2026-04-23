---
status: active
last_reviewed: 2026-04-23
---

# AI-DLC（AI-Driven Development Life Cycle）調査レポート

- **調査日**: 2026-03-13
- **ソース数**: 12+（AWS公式ブログ、re:Invent セッション、企業事例、コミュニティ）
- **リポジトリ分析**: `awslabs/aidlc-workflows` v0.1.6（全ファイル読了）

---

## 1. AI-DLC とは

AWSが2025年7月に提唱した**次世代ソフトウェア開発方法論**。従来の「人間がAIに指示する」モデルを反転し、**「AIが開発を主導し、人間が意思決定・レビュー・承認に集中する」**パラダイムシフト。

> "A methodology for the era of AI-driven software development — built from first principles, not retrofitted from the past"
> — ai-dlc.dev

Agile/Scrum の改造版ではなく、**第一原理から設計**されている。反復コストがほぼゼロになった AI 時代に最適化されたフローを目指す。

---

## 2. 背景にある問題（2つのアンチパターン）

re:Invent 2025（DVT214セッション、Anupam Mishra 氏 / Raja 氏）にて、100+ の顧客実験から特定された問題：

| アンチパターン | 説明 | 結果 |
|---|---|---|
| **AI-Managed**（丸投げ） | 複雑な問題をそのまま AI に投げる | 過剰なコード生成、低い信頼度、デプロイ遅延 |
| **AI-Assisted**（小タスク限定） | リファクタ・セキュリティレビュー等に限定 | 知的重労働は人間のまま、速度改善が限定的 |

### 生産性パラドックス

- 開発者は「AIで **23% 生産性向上**した」と感じる
- しかし実際の分析では「AI使用チームは **20% 非生産的**」（Meter.org調査、2025年前半）
- 原因: 方法論なしに AI ツールを導入しても、構造的な改善にならない

---

## 3. 3つのフェーズ

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  INCEPTION   │ →  │ CONSTRUCTION │ →  │  OPERATIONS  │
│  何を作るか   │    │  設計・実装    │    │  デプロイ・運用 │
└─────────────┘    └──────────────┘    └──────────────┘
```

### Inception（要件定義）

- AI が対話を通じて仕様書・ユーザーストーリーを生成
- **Mob Elaboration**: PM・開発者・QA・Ops が同席し、AI との対話で要件を詰める（4時間〜半日）
- 従来四半期かかるアライメントが 1 セッションに圧縮

### Construction（設計・実装）

- AI が設計・コード・テストを自律的に生成
- 人間が検証・承認
- **Bolt**（時間〜日単位の高速サイクル）で反復

### Operations（運用）

- AI が監視・分析を実施
- 人間が最終判断・意思決定

### 9つの適応ステージ

3フェーズの中に **9つの適応ステージ** があるが、全プロジェクトで全ステージが必要なわけではない。AI が状況に応じて**スキップすべきステージを推奨**する（バグ修正 vs 新規開発で異なる）。

---

## 4. 核心的な概念

### 用語の置換

| 従来 | AI-DLC | 説明 |
|---|---|---|
| Sprint（2週間） | **Bolt**（時間〜日単位） | より短く集中的な作業サイクル |
| Epic / Story | **Unit of Work** | AI が分割・管理する作業単位 |
| 仕様書バトンタッチ | **Mob Elaboration** | 全員同席での AI 対話型要件定義 |
| 人間主導 | **AI 主導 / 人間承認** | 主導権の反転 |

### 帽子ベースのアプローチ（ai-dlc.dev コミュニティ版）

| 帽子 | 役割 |
|---|---|
| **Planner** | ステップと依存関係を設計 |
| **Builder** | 計画を実行し、コードを書く |
| **Reviewer** | 品質を検証し、要件適合性を確保 |

セキュリティ・設計・テスト・デバッグの専門帽子も利用可能。

### Adaptive Workflows（適応型ワークフロー）

- 全プロジェクトに同じプロセスを適用しない
- AI 自身がプロジェクトの性質に応じて必要なステージを推奨
- **Steering rules** として実装し、AI コーディングツールに読み込ませる

### IDEA-INTENT-UNIT-BOLT の階層

```
IDEA（アイデア）
  └── INTENT（意図・目的）
        └── UNIT（作業単位）
              └── BOLT（実行サイクル）
```

仕様（Specification）と実装（Implementation）を分離する設計思想。

---

## 5. 重要なプラクティス

### 開発者向け

| プラクティス | 説明 |
|---|---|
| **コードオーナーシップ** | コミットする全行を理解する責任を持つ |
| **Semantics-Per-Token 比** | 「builder pattern でリファクタ」のように少ない単語で多くの意味を伝える |
| **タスク分解** | 「EC サイト構築」→「認証モジュールの SQL インジェクションチェック実装」 |
| **コンテキスト管理** | 大きなウィンドウ≠良い結果。不要な履歴はクリア |
| **参照ベース学習** | 口頭説明より既存コードパターンを指し示す |

### 組織向け

| イネーブラー | 説明 |
|---|---|
| **フロー保護** | 「午後は会議なし」ポリシー（Amazon 実践済み） |
| **Dev 環境投資** | AI 高速生成のボトルネックがテスト環境になる |
| **CI/CD 成熟度** | 高速コード生成がパイプラインの非効率を増幅する |
| **MCP 管理** | 不要な MCP サーバーがコンテキストの 60-70% を消費 |

### AI の扱い方

> "Think of AI as a Junior Developer — not a senior engineer. AI confidently states incorrect information. Developers must question and guide — they remain owners."

---

## 6. 計測フレームワーク

ゲーム化されやすいメトリクス（コード行数、ベロシティポイント）を避け、以下を重視:

1. **Velocity + Quality**（ペアメトリクス）
2. **Predictability**: commit-to-delivery 比率（~20% → 80%+ を目標）
3. **Business value delivery**: 決定からローンチまでの時間

ベースライン比較: AI 有/無での「decision-to-launch」タイムラインを測定。

---

## 7. ツールとオープンソース

### 公式リソース

| リソース | URL |
|---|---|
| **公式ワークフロー（OSS）** | https://github.com/awslabs/aidlc-workflows |
| **サンプル** | https://github.com/aws-samples/sample-aidlc-workflows |
| **Kiro 連携サンプル** | https://github.com/aws-samples/sample-aidlc-kiro-power |
| **AWS DevOps Blog** | https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/ |
| **AWS Japan Blog** | https://aws.amazon.com/jp/blogs/news/ai-driven-development-life-cycle/ |

### コミュニティリソース

| リソース | URL |
|---|---|
| **ai-dlc.dev（公式サイト）** | https://ai-dlc.dev/ |
| **Claude Code プラグイン** | https://github.com/ijin/aidlc-cc-plugin |
| **コミュニティ実装** | https://github.com/msifoss/ai-dlc |
| **帽子ベースワークフロー** | https://github.com/TheBushidoCollective/ai-dlc |

### セットアップ例（Kiro CLI）

```bash
mkdir -p .kiro/steering
git clone https://github.com/awslabs/aidlc-workflows.git
cp aidlc-workflows/aidlc-rules/aws-aidlc-rules/core-workflow.md .kiro/steering/
kiro-cli chat
# プロンプト: "Using AI-DLC, [プロジェクト説明]"
```

Steering rules は Kiro / Cursor / Claude Code 等、任意の AI コーディングツールで利用可能。

---

## 8. 実績・事例

### 海外事例

| 組織 | 内容 | 成果 |
|---|---|---|
| **Wipro** | 3チーム分散、ヘルスケアモジュール | 20時間（5日×4h）で数ヶ月分を完成。「速いだけでなく、より良い構築方法」 |
| **Dun（fintech）** | 株取引アプリ | 2ヶ月計画を 48時間で構築、翌週リリース |
| **CallHero** | AWS サーバーレスアプリ | 25 Bolt、216テスト、200+ セキュリティ指摘、9日でゼロ→本番 |

### 日本国内事例

| 組織 | 内容 | 成果 |
|---|---|---|
| **Gaudiy** | Web/モバイル/バックエンドのプロダクト | 4名×約2ヶ月でほぼ完成。α Construction のプロトタイプ反復で手戻りほぼゼロ |
| **食べログ** | AI-DLC Unicorn Gym（3日間ワークショップ） | 動作するプロトタイプ完成。企画・エンジニア間の知識共有促進 |
| **東京海上日動システムズ** | 金融業界初の AI-DLC Unicorn Gym | 従来 2週間の Agile Sprint を日〜半日の Bolt に圧縮 |
| **サーバーワークス** | Kiro CLI で CLI ツール開発 | 5-6時間で 47ファイル/2,705行。70+ の質問・承認ポイント |

### Gaudiy のカスタムフロー

```
Inception → α Construction（プロトタイプ）→ Inception Refining（2-3回反復）→ β Construction（本番実装）
```

- Claude Code プラグイン `aidlc-kit` として実装
- コマンド: `setup`, `inception-new`, `inception-fix`, `alpha-design`, `prototype`, `design-overview`, `design-unit`, `task`

---

## 9. 課題と批判

### 共通課題

| 課題 | 詳細 |
|---|---|
| **レビューボトルネック** | AI の出力速度に人間のレビューが追いつかない（全事例で共通） |
| **承認ポイントの多さ** | 70+ の質問・承認が発生。バイブコーディング感覚では進められない |
| **モデル訓練の限界** | 訓練データに少ないパターン（例: Go で DDD）は AI 性能が低下 |
| **大規模コードベース** | セマンティックコンテキスト構築（コールグラフ等）が前提 |
| **ツール依存** | 特定 AI ツールへのロックインリスク |
| **チーム展開の難しさ** | 用語・カスタムフローの学習コスト |
| **コンテキストウィンドウ** | 長時間セッションでトークン消費が激しく、セッション分割が必要 |

### 戦略的考慮

- **技術的負債の再評価**: AI 加速により、パッチ vs 全書き直しの判断基準が変わる
- **チーム構成の変化**: Mob Elaboration が前提のため、個人開発への適用は限定的
- **AIは Junior Developer**: 自信を持って誤情報を述べる。開発者は常に疑い、導く必要がある

---

## 10. 既存設定（dotfiles）との関連分析

現在の `.config/claude/` 設定体系は AI-DLC の思想と高い親和性を持つ:

| AI-DLC 概念 | 既存設定の対応 | ギャップ |
|---|---|---|
| Adaptive Workflows | `workflow-guide.md` の S/M/L スケーリング | ステージの自動推奨は未実装 |
| Mob Elaboration | `/spec`, `/spike` による要件詰め | 複数人同席の仕組みは対象外 |
| Steering Rules | `CLAUDE.md` + `rules/` + `references/` | ほぼ同等の構造 |
| Code Ownership | `/review` の必須化 | 信頼度スコアで補完済み |
| Bolt（高速サイクル） | EPD の Spec→Spike→Validate→Build→Review | Bolt 単位の計測は未導入 |
| Unit of Work | タスク分解は手動 | Unit 管理の自動化余地あり |
| 9 適応ステージ | ワークフローガイドの段階 | AI による自動ステージ選択は未実装 |

### 統合の可能性

1. `aidlc-workflows` の steering rules を `references/` に配置し、既存ワークフローと共存
2. `/spec` → `/spike` → `/validate` フローを Inception → Construction にマッピング
3. Bolt 単位の計測を AutoEvolve の metrics に追加

---

## 11. awslabs/aidlc-workflows リポジトリ深層分析

### 11.1 リポジトリ概要

- **バージョン**: v0.1.6（2026-03-05）
- **ライセンス**: MIT-0
- **Stars**: 710 / Forks: 145
- **構造**: `aidlc-rules/` 配下に `aws-aidlc-rules/`（コアルール 1 ファイル）+ `aws-aidlc-rule-details/`（詳細ルール 20+ ファイル）

```
aidlc-rules/
├── aws-aidlc-rules/
│   └── core-workflow.md          # メインエントリポイント（539行）
└── aws-aidlc-rule-details/
    ├── common/                   # 共通ルール（8ファイル）
    │   ├── process-overview.md       # ワークフロー全体像 + Mermaid図
    │   ├── terminology.md            # 用語集（Phase/Stage/Unit等）
    │   ├── depth-levels.md           # 適応的深度の説明
    │   ├── welcome-message.md        # ウェルカムメッセージテンプレート
    │   ├── question-format-guide.md  # 質問フォーマット（多肢選択式）
    │   ├── session-continuity.md     # セッション再開手順
    │   ├── content-validation.md     # コンテンツ検証ルール
    │   ├── error-handling.md         # エラーハンドリング・復旧手順
    │   ├── overconfidence-prevention.md  # 過信防止ガイド
    │   ├── workflow-changes.md       # ワークフロー変更管理
    │   └── ascii-diagram-standards.md
    ├── inception/                # Inception フェーズ（7ファイル）
    │   ├── workspace-detection.md    # ワークスペース検出
    │   ├── reverse-engineering.md    # リバースエンジニアリング（Brownfield）
    │   ├── requirements-analysis.md  # 要件分析（適応的深度）
    │   ├── user-stories.md           # ユーザーストーリー
    │   ├── workflow-planning.md      # ワークフロー計画
    │   ├── application-design.md     # アプリケーション設計
    │   └── units-generation.md       # Unit of Work 分解
    ├── construction/             # Construction フェーズ（6ファイル）
    │   ├── functional-design.md      # 機能設計（per-unit）
    │   ├── nfr-requirements.md       # NFR要件（per-unit）
    │   ├── nfr-design.md             # NFR設計（per-unit）
    │   ├── infrastructure-design.md  # インフラ設計（per-unit）
    │   ├── code-generation.md        # コード生成（per-unit）
    │   └── build-and-test.md         # ビルド＆テスト
    ├── operations/
    │   └── operations.md             # プレースホルダー
    └── extensions/
        └── security/baseline/
            ├── security-baseline.md      # SECURITY-01〜15（OWASP Top 10対応）
            └── security-baseline.opt-in.md  # オプトインプロンプト
```

### 11.2 アーキテクチャ設計の核心

#### Progressive Disclosure パターン

AI-DLC は **コンテキストウィンドウを意識した段階的ロード** を採用:

1. **常時ロード**: `core-workflow.md`（539行）のみ — 全ステージの概要とルーティング
2. **ステージ進入時ロード**: 該当する `rule-details/*.md` をオンデマンドで読み込み
3. **Extensions**: `*.opt-in.md`（軽量）のみ先にスキャン → ユーザーがオプトインした場合のみ本体をロード

これは我々の **Progressive Disclosure 設計**（CLAUDE.md → references/ → rules/）と同じ原理。

#### 適応的実行モデル

```
┌─────────────────────────────────────────────┐
│  core-workflow.md が全体を統括               │
│                                             │
│  各ステージに対して:                         │
│  1. ALWAYS / CONDITIONAL 判定               │
│  2. CONDITIONAL → 多因子分析で EXECUTE/SKIP  │
│  3. EXECUTE → rule-details をロード → 実行   │
│  4. 深度は Minimal/Standard/Comprehensive    │
│  5. 全ステージで承認ゲートを設置             │
└─────────────────────────────────────────────┘
```

**4つの適応軸**:
1. **ステージ選択**（binary）: 実行するか / スキップするか
2. **深度レベル**: Minimal / Standard / Comprehensive
3. **Brownfield/Greenfield**: 既存コードの有無で分岐
4. **Extensions**: セキュリティ等のオプトイン/アウト

### 11.3 全ステージ詳細マッピング

#### INCEPTION フェーズ（7ステージ）

| # | ステージ | 実行条件 | 主要成果物 | 承認ゲート |
|---|---|---|---|---|
| 1 | **Workspace Detection** | ALWAYS | `aidlc-state.md`（状態追跡） | なし（自動進行） |
| 2 | **Reverse Engineering** | Brownfield のみ | `architecture.md`, `code-structure.md`, `api-documentation.md`, `component-inventory.md`, `technology-stack.md`, `dependencies.md`, `code-quality-assessment.md` | 明示的承認必須 |
| 3 | **Requirements Analysis** | ALWAYS（深度は適応） | `requirements.md`, `requirement-verification-questions.md` | 明示的承認必須 |
| 4 | **User Stories** | CONDITIONAL（多因子分析） | `stories.md`, `personas.md` | 明示的承認必須 |
| 5 | **Workflow Planning** | ALWAYS | `execution-plan.md`（Mermaid図付き） | 明示的承認必須 |
| 6 | **Application Design** | CONDITIONAL | `components.md`, `component-methods.md`, `services.md`, `component-dependency.md` | 明示的承認必須 |
| 7 | **Units Generation** | CONDITIONAL | `unit-of-work.md`, `unit-of-work-dependency.md`, `unit-of-work-story-map.md` | 明示的承認必須 |

#### CONSTRUCTION フェーズ（6ステージ、Unit ループあり）

| # | ステージ | 実行条件 | 主要成果物 | 承認ゲート |
|---|---|---|---|---|
| 8 | **Functional Design** | CONDITIONAL（per-unit） | `functional-design.md` | 2択（変更要求 / 次へ） |
| 9 | **NFR Requirements** | CONDITIONAL（per-unit） | `nfr-requirements.md` | 2択 |
| 10 | **NFR Design** | CONDITIONAL（per-unit） | `nfr-design.md` | 2択 |
| 11 | **Infrastructure Design** | CONDITIONAL（per-unit） | `infrastructure-design.md` | 2択 |
| 12 | **Code Generation** | ALWAYS（per-unit） | 実際のコード + テスト + ドキュメント | 2択 |
| 13 | **Build and Test** | ALWAYS | `build-instructions.md`, `*-test-instructions.md`, `build-and-test-summary.md` | 明示的承認 |

**Per-Unit ループ**: Unit が複数ある場合、ステージ 8-12 を各 Unit ごとに繰り返す。全 Unit 完了後にステージ 13（Build and Test）を実行。

#### OPERATIONS フェーズ

現時点では**プレースホルダー**。将来的にデプロイ・モニタリング・インシデント対応を含む予定。

### 11.4 質問・承認メカニズム

AI-DLC の最も特徴的な設計要素:

#### 質問はチャットに書かない

```
❌ チャットで直接質問
✅ .md ファイルに多肢選択式で記述 → ユーザーが [Answer]: タグで回答
```

**フォーマット例**:
```markdown
## Question 1
What database technology will be used?

A) Relational (PostgreSQL, MySQL)
B) NoSQL Document (MongoDB, DynamoDB)
C) NoSQL Key-Value (Redis, Memcached)
X) Other (please describe after [Answer]: tag below)

[Answer]:
```

- 最低 2 つの意味ある選択肢 + 必ず "Other" を最後に配置
- 回答後は矛盾・曖昧さを検出し、必要なら clarification-questions.md で追加質問
- **全曖昧さが解消されるまで次ステージに進まない**

#### 過信防止（Overconfidence Prevention）

AI-DLC は初期バージョンで AI が質問を省略しすぎる問題を発見。対策:

- **旧**: 「必要な場合のみ質問」
- **新**: 「疑わしければ質問。過信は悪い結果を生む」
- 各ステージの "Skip entire categories" 指示を撤廃
- 曖昧な回答（"depends", "mix of", "not sure"）は必ずフォローアップ

#### 承認ゲートの統一フォーマット

```markdown
> **📋 REVIEW REQUIRED:**
> Please examine [artifact] at: `aidlc-docs/[path]/`

> **🚀 WHAT'S NEXT?**
> **You may:**
> 🔧 **Request Changes** - Ask for modifications
> ✅ **Approve & Continue** - Proceed to **[Next Stage]**
```

Construction フェーズでは必ず **2択**（変更要求 / 次へ）に制限。3択以上の「創発的行動」は明示的に禁止。

### 11.5 状態管理とセッション継続性

#### 2つの状態ファイル

| ファイル | 役割 |
|---|---|
| `aidlc-docs/aidlc-state.md` | ワークフロー全体の進捗状態。再開時のエントリポイント |
| `aidlc-docs/audit.md` | 全ユーザー入力の生ログ（ISO 8601タイムスタンプ付き） |

**重要ルール**: `audit.md` は **追記のみ**。上書きは厳禁（`Edit` で append、`Write` で全体上書きは NG）。

#### セッション再開

1. `aidlc-state.md` の存在を検出
2. 前回ステージのアーティファクトを段階的にロード（Smart Context Loading）
3. ユーザーに現在状態を表示し、「続行 / 前ステージのレビュー」を選択させる
4. 再開時も全質問は `.md` ファイル経由（チャットでは聞かない）

#### Plan-Level Checkbox 追跡

```
- [ ] ステップ未完了
- [x] ステップ完了
```

**2階層のチェックボックス管理**:
- **Plan-Level**: 各ステージ内の詳細ステップ（`*-plan.md`）
- **Stage-Level**: ワークフロー全体の進捗（`aidlc-state.md`）

「完了したら即座にチェック」が必須。同じインタラクション内で更新する。

### 11.6 Extensions システム

#### 現時点で提供されているもの

- **Security Baseline** (`SECURITY-01` 〜 `SECURITY-15`): OWASP Top 10 2025 にマッピング

#### Extension のライフサイクル

```
1. ワークフロー開始時: extensions/ 配下の *.opt-in.md のみスキャン（軽量）
2. Requirements Analysis 中: opt-in プロンプトをユーザーに提示
3. ユーザーがオプトイン → 本体ルールファイルをロード
4. ユーザーがオプトアウト → 本体は一切ロードしない（コンテキスト節約）
5. 有効化された Extension は全ステージで blocking constraint として強制
6. N/A の場合はコンプライアンスサマリーに記録（blocking ではない）
```

#### Security Baseline の15ルール

| ID | 概要 | OWASP マッピング |
|---|---|---|
| SECURITY-01 | 保管時・転送時の暗号化 | — |
| SECURITY-02 | ネットワーク中間者のアクセスログ | — |
| SECURITY-03 | アプリケーションレベルの構造化ログ | — |
| SECURITY-04 | HTTP セキュリティヘッダー | — |
| SECURITY-05 | 全 API パラメータの入力検証 | — |
| SECURITY-06 | 最小権限アクセスポリシー | — |
| SECURITY-07 | 制限的ネットワーク構成 | — |
| SECURITY-08 | アプリケーションレベルのアクセス制御 | A01:2025 Broken Access Control |
| SECURITY-09 | セキュリティ硬化・設定ミス防止 | A02:2025 Security Misconfiguration |
| SECURITY-10 | ソフトウェアサプライチェーンセキュリティ | A03:2025 Supply Chain Failures |
| SECURITY-11 | セキュアデザイン原則 | A06:2025 Insecure Design |
| SECURITY-12 | 認証・資格情報管理 | A07:2025 Authentication Failures |
| SECURITY-13 | ソフトウェア・データ整合性検証 | A08:2025 Integrity Failures |
| SECURITY-14 | アラート・モニタリング | A09:2025 Logging & Alerting Failures |
| SECURITY-15 | 例外処理・フェイルセーフデフォルト | A10:2025 Exceptional Conditions |

#### 独自 Extension の追加方法

```
extensions/
└── my-category/
    └── my-rules/
        ├── my-rules.md          # ルール本体（Rule ID + Verification 必須）
        └── my-rules.opt-in.md   # オプトインプロンプト
```

### 11.7 マルチプラットフォーム対応

| プラットフォーム | ルール配置先 | 詳細配置先 |
|---|---|---|
| **Kiro** | `.kiro/steering/aws-aidlc-rules/` | `.kiro/aws-aidlc-rule-details/` |
| **Amazon Q Developer** | `.amazonq/rules/aws-aidlc-rules/` | `.amazonq/aws-aidlc-rule-details/` |
| **Cursor** | `.cursor/rules/ai-dlc-workflow.mdc` | `.aidlc-rule-details/` |
| **Cline** | `.clinerules/core-workflow.md` | `.aidlc-rule-details/` |
| **Claude Code** | `CLAUDE.md` or `.claude/CLAUDE.md` | `.aidlc-rule-details/` |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.aidlc-rule-details/` |

core-workflow.md 内のパス解決ロジック:
```
Check in order, use first that exists:
1. .aidlc-rule-details/   (Cursor, Cline, Claude Code, Copilot)
2. .kiro/aws-aidlc-rule-details/   (Kiro)
3. .amazonq/aws-aidlc-rule-details/   (Amazon Q)
```

### 11.8 Tenets（信条）

1. **No duplication**: 真実の源は一箇所。複数フォーマットが必要なら生成する
2. **Methodology first**: AI-DLC はツールではなく方法論。インストール不要
3. **Reproducible**: 異なるモデルでも同様の結果を出すほど明確なルール
4. **Agnostic**: IDE・エージェント・モデルに非依存
5. **Human in the loop**: 重要な決定には明示的なユーザー確認が必須

### 11.9 エラーハンドリングと復旧

4段階のエラー重大度:
- **Critical**: ワークフロー続行不可（必須ファイル欠損等）
- **High**: フェーズ完了不可（矛盾する回答等）
- **Medium**: ワークアラウンドで続行可
- **Low**: 進行に影響なし

復旧パターン:
- **部分完了**: plan ファイルの最後の `[x]` から再開
- **状態ファイル破損**: バックアップ → ユーザーに現在フェーズを確認 → 再生成
- **アーティファクト欠損**: 該当ステージに戻って再実行
- **フェーズ再開**: アーカイブ作成 → チェックボックスリセット → 再実行

### 11.10 ワークフロー変更管理

8種類の中間変更パターンに対応:

1. **スキップしたフェーズの追加**: 依存関係チェック → 実行
2. **計画フェーズのスキップ**: 影響説明 → 明示的確認 → SKIPPED
3. **現在ステージの再開**: アーカイブ → リセット → 再実行
4. **前ステージの再開**: カスケード影響を評価 → 全依存ステージを再実行
5. **深度変更**: Minimal ↔ Standard ↔ Comprehensive
6. **ワークフロー一時停止**: チェックポイント保存 → session-continuity で再開
7. **アーキテクチャ決定の変更**: 早期 = 低コスト、後期 = 高コスト
8. **Unit の追加/削除/分割**: 影響範囲を評価 → 該当 Unit のみ再設計

---

## 12. 既存設定（dotfiles）との詳細比較

リポジトリの全ファイルを読了した上での精緻な比較:

### 設計思想の一致点

| 概念 | AI-DLC の実装 | 我々の実装 | 類似度 |
|---|---|---|---|
| **Progressive Disclosure** | core-workflow.md → rule-details/ → extensions/ | CLAUDE.md → references/ → rules/ | ★★★★★ |
| **適応的実行** | ALWAYS/CONDITIONAL + 深度3段階 | S/M/L ワークフロー | ★★★★☆ |
| **状態管理** | aidlc-state.md + audit.md | PLANS.md + session checkpoints | ★★★☆☆ |
| **承認ゲート** | 全ステージで REVIEW REQUIRED | verification-before-completion | ★★★★☆ |
| **セキュリティ** | SECURITY-01〜15 Extension | security-reviewer + rules/ | ★★★★☆ |
| **過信防止** | overconfidence-prevention.md | harness hooks（golden-check等） | ★★★☆☆ |
| **セッション継続** | session-continuity.md + aidlc-state.md | session-load.js + checkpoints | ★★★★☆ |

### AI-DLC にあって我々にないもの

| 機能 | 価値 | 導入優先度 |
|---|---|---|
| **質問の .md ファイル化** | チャット外に質問を構造化。チーム共有可能 | 中（個人開発では低い） |
| **多因子ステージ判定ロジック** | コアルール内で判定基準を明文化 | 高（workflow-guide に組込可能） |
| **Unit of Work 分解と per-unit ループ** | 大規模開発の並列化基盤 | 中（/autonomous で部分対応済み） |
| **Brownfield リバースエンジニアリング** | 既存コードベースの自動ドキュメント化 | 高（/rpi の前段として有用） |
| **Extension opt-in/out システム** | コンテキスト節約しつつオプション拡張 | 中（rules/ で部分対応済み） |
| **audit.md（全入力の生ログ）** | 完全な監査証跡 | 低（AutoEvolve learnings で代替） |

### 我々にあって AI-DLC にないもの

| 機能 | 価値 |
|---|---|
| **AutoEvolve（自動学習ループ）** | セッション横断の自動改善。AI-DLC は手動改善のみ |
| **Hook ベースの自動検出** | PostToolUse/PreToolUse での自動ガバナンス。AI-DLC は ルールベースのみ |
| **マルチモデル連携** | Codex/Gemini への委譲。AI-DLC は単一モデル前提 |
| **EPD 統合** | Product/Design レビュー軸。AI-DLC は Engineering 軸のみ |
| **信頼度スコア** | レビュー指摘のフィルタリング |
| **Background Agents** | GitHub Actions ベースの自律実行 |

---

## 13. ijin/aidlc-cc-plugin 詳細分析

### 13.1 概要

| 項目 | 値 |
|---|---|
| **リポジトリ** | `ijin/aidlc-cc-plugin` |
| **バージョン** | 0.1.0（2026-02-03 初リリース） |
| **ライセンス** | MIT-0 |
| **ベース** | `awslabs/aidlc-workflows` を Claude Code プラグインシステムに適応 |
| **エントリポイント** | `/aidlc:start [intent]` スキル |

### 13.2 プラグインアーキテクチャ

```
aidlc-cc-plugin/
├── .claude-plugin/
│   ├── plugin.json          # プラグインメタデータ（name, version, author）
│   └── marketplace.json     # マーケットプレイス登録情報
├── skills/
│   └── start/
│       ├── SKILL.md          # スキル定義（disable-model-invocation: true）
│       └── rule-details/     # ステアリングルール（全30ファイル）
│           ├── core-workflow.md
│           ├── common/       # 11ファイル
│           ├── inception/    # 7ファイル
│           ├── construction/ # 6ファイル
│           └── operations/   # 1ファイル
├── README.md
├── CHANGELOG.md
└── LICENSE
```

**重要な設計判断**: `disable-model-invocation: true` により、スキルはユーザーの明示的な `/aidlc:start` コマンドでのみ起動。意図しない自動起動を防止。

### 13.3 オリジナルからの変更点（10ファイル / 30ファイル中）

#### 変更カテゴリ A: Q&A メカニズムの根本的転換

**最大の変更**。オリジナルの「ファイルベース Q&A」を「チャットベース Q&A」に全面置換。

| 観点 | オリジナル（awslabs） | プラグイン（ijin） |
|---|---|---|
| **質問の提示方法** | `.md` ファイルに質問を書き出し | `AskUserQuestion` ツールで対話的に提示 |
| **回答方法** | ファイル内の `[Answer]:` タグに記入 | チャットで選択肢をクリック or テキスト入力 |
| **回答の記録** | 質問ファイル自体が記録 | `aidlc-docs/{phase}/questions-summary.md` に別途記録 |
| **ユーザー設定** | なし（ファイル一択） | `aidlc-preferences.md` に好みのスタイルを保存 |
| **2つのモード** | — | Interactive UI（ボタン選択）/ Text responses（テキスト入力） |

**影響を受けたファイル**:
- `common/question-format-guide.md` — **完全書き換え**（482行）。Section A（AskUserQuestion）と Section B（テキスト）の2部構成に
- `common/session-continuity.md` — preference ロードステップ追加、ファイルベース指示をチャットベースに変更
- `common/process-overview.md` — 「[Answer]: タグ」→「会話で直接回答」
- `common/welcome-message.md` — 「Answer questions」→「Answer questions in conversation」
- `inception/requirements-analysis.md` — Extension opt-in 削除 + AskUserQuestion 使用に変更
- `inception/user-stories.md` — `[Answer]:` タグ → AskUserQuestion ツール
- `core-workflow.md` — 全ステージの質問指示をチャットベースに変更

**設計評価**: Claude Code は `AskUserQuestion` ツールを持つため、この適応は合理的。ただし、ファイルベースの「質問自体がアーティファクトとして残る」利点は失われている。`questions-summary.md` で補完する設計。

#### 変更カテゴリ B: Extensions システムの完全削除

**2番目に大きな変更**。`extensions/` ディレクトリとそのライフサイクル全体を削除。

削除された要素:
- `extensions/` ディレクトリ（security-baseline.md, security-baseline.opt-in.md）
- core-workflow.md の「MANDATORY: Extensions Loading」セクション全体（~30行）
- requirements-analysis.md の「Step 5.1: Extension Opt-In Prompts」
- aidlc-state.md の Extension Configuration テーブル

**影響**: セキュリティルール（SECURITY-01〜15）や将来の Extension が使えない。ユーザーが独自の CLAUDE.md ルールで補う必要がある。

**設計評価**: コンテキストウィンドウ節約としては妥当。Claude Code は `rules/` ディレクトリで同等のことが実現可能。ただし opt-in/out の動的メカニズムは失われた。

#### 変更カテゴリ C: パス解決の簡素化

**オリジナル**: 3パスを順番にチェック（マルチプラットフォーム対応）
```
1. .aidlc-rule-details/   (Cursor, Cline, Claude Code, Copilot)
2. .kiro/aws-aidlc-rule-details/   (Kiro)
3. .amazonq/aws-aidlc-rule-details/   (Amazon Q)
```

**プラグイン**: 固定パス `rule-details/`（スキルディレクトリ相対）

全ステージの「Load all steps from `inception/xxx.md`」→「Read the file `rule-details/inception/xxx.md` and follow all steps」に統一。

#### 変更カテゴリ D: フロントエンド固有ルールの削除

- `construction/code-generation.md`: フロントエンドコンポーネント生成セクション削除、`data-testid` 自動化ルール削除
- `construction/functional-design.md`: フロントエンドコンポーネント設計セクション削除

**設計評価**: Claude Code の典型的ユースケース（バックエンド/CLI 中心）を考慮した合理的な簡素化。

#### 変更カテゴリ E: その他の微調整

- `inception/application-design.md`: 統合ドキュメント生成ステップ削除
- `common/error-handling.md`: テキストの並び替え（minor、おそらくコピーミス）
- `core-workflow.md`: 空白修正（trailing whitespace）

### 13.4 変更されなかったもの（重要な保持要素）

以下は**一切変更なし**で保持:

- `common/overconfidence-prevention.md` — 過信防止ルール
- `common/depth-levels.md` — 3段階深度（Minimal/Standard/Comprehensive）
- `common/content-validation.md` — コンテンツ品質基準
- `common/terminology.md` — 用語定義
- `common/ascii-diagram-standards.md` — 図表フォーマット
- `common/workflow-changes.md` — 8種類の中間変更パターン
- `inception/workspace-detection.md` — Greenfield/Brownfield 判定
- `inception/reverse-engineering.md` — 12ステップリバースエンジニアリング
- `inception/workflow-planning.md` — 11ステップスコープ分析
- `inception/units-generation.md` — Unit of Work 分解
- `construction/nfr-requirements.md` — 非機能要件
- `construction/nfr-design.md` — 非機能設計
- `construction/infrastructure-design.md` — インフラ設計
- `construction/build-and-test.md` — テスト指示
- `operations/operations.md` — Operations プレースホルダー

**20ファイル / 30ファイルが完全一致** = 方法論のコア部分は忠実に保持されている。

### 13.5 プラグインの初期化シーケンス

```
1. Welcome Message 表示（rule-details/common/welcome-message.md）
2. セッション再開チェック（aidlc-docs/aidlc-state.md 存在確認）
3. Q&A スタイル選択（AskUserQuestion で Interactive UI / Text responses）
4. コアルールロード（core-workflow.md + 4つの common ルール）
5. ワークスペース初期化（aidlc-docs/ + aidlc-preferences.md）
6. Inception Phase 開始（Workspace Detection）
7. core-workflow.md のオーケストレーションに従う
```

**オリジナルとの差分**: ステップ 3（Q&A スタイル選択）が追加。ステップ 4 で Extensions ロードがスキップ。

### 13.6 総合評価

| 評価軸 | スコア | コメント |
|---|---|---|
| **方法論の忠実度** | ★★★★☆ | コアロジックは完全保持。Extensions 削除は大きい |
| **プラットフォーム適応** | ★★★★★ | Claude Code の AskUserQuestion を活用した自然な適応 |
| **コンテキスト効率** | ★★★★★ | Extensions 削除 + パス簡素化で大幅軽量化 |
| **拡張性** | ★★☆☆☆ | Extensions がないため独自ルール追加の仕組みがない |
| **コード品質** | ★★★☆☆ | error-handling.md にコピーミスあり |

---

## 14. dotfiles への AI-DLC 統合 PoC 設計

### 14.1 統合の動機

AI-DLC の方法論と dotfiles の既存設定は設計思想が高度に一致している（セクション12参照）。統合により以下が期待できる:

1. **構造化された Inception フェーズ**の導入（現状の `/rpi` は Plan から始まり、要件定義が弱い）
2. **適応的ステージ判定**の強化（S/M/L の3段階 → 13ステージの多因子判定）
3. **Brownfield リバースエンジニアリング**の体系化（既存コードベース分析のテンプレート化）
4. **監査証跡**の充実（audit.md パターンの導入）

### 14.2 統合アプローチの選択肢

#### Option A: ijin プラグインをそのまま導入

```bash
/plugin marketplace add ijin/aidlc-cc-plugin
/plugin install aidlc@aidlc-cc-plugin
```

**メリット**: 即座に利用可能、アップデート追従が容易
**デメリット**: 既存ワークフロー（/rpi, /epd, /spec 等）と完全に分離。Extensions なし。dotfiles のハーネス（hooks, AutoEvolve）と連携不可

#### Option B: AI-DLC ルールを dotfiles のスキルとして再実装

```
.config/claude/skills/aidlc/
├── SKILL.md                    # /aidlc スキル（エントリポイント）
├── rule-details/               # awslabs からコピー + 適応
│   ├── core-workflow.md        # dotfiles 固有の適応版
│   ├── common/
│   ├── inception/
│   ├── construction/
│   └── operations/
└── extensions/                 # dotfiles の rules/ と統合
    └── security/
```

**メリット**: 完全なカスタマイズ、既存設定との深い統合
**デメリット**: メンテナンス負荷高、upstream 追従が困難

#### Option C: ハイブリッド — AI-DLC の「方法論」を既存スキルに注入（推奨）

既存の `/rpi`, `/epd`, `/spec` スキルに AI-DLC の**具体的なプラクティス**を取り込む。方法論全体の導入ではなく、価値の高い要素をチェリーピック。

```
取り込む要素:
├── 多因子ステージ判定ロジック     → workflow-guide.md に追加
├── Brownfield リバースエンジニアリング → /rpi の前段に組込
├── 過信防止ルール               → rules/common/ に追加（既に部分的に存在）
├── Unit of Work 分解パターン    → /epd の Construction フェーズに組込
├── 適応的深度（3段階）          → S/M/L に統合
└── audit.md パターン            → AutoEvolve learnings と統合
```

**メリット**: 既存ワークフローとの自然な統合、必要な部分だけ導入、メンテナンス負荷最小
**デメリット**: AI-DLC の「一貫したフロー」としての体験は得られない

### 14.3 推奨: Option C を段階的に実施

#### Phase 1: 多因子ステージ判定の導入

現状の S/M/L 判定は行数ベースだが、AI-DLC の多因子判定をマージする:

```markdown
# 現状（workflow-guide.md）
| 規模 | 例             | 判定基準 |
|------|----------------|----------|
| S    | typo修正       | 1行変更  |
| M    | 関数追加       | 複数行   |
| L    | 新機能         | 複数ファイル |

# AI-DLC 統合後
| 規模 | 判定因子 |
|------|----------|
| S    | 変更規模:小 AND リスク:低 AND 影響範囲:単一ファイル |
| M    | 変更規模:中 OR リスク:中 OR 影響範囲:複数ファイル |
| L    | 変更規模:大 OR リスク:高 OR アーキテクチャ影響あり |
```

#### Phase 2: Brownfield リバースエンジニアリング テンプレートの追加

AI-DLC の12ステップ分析を `/rpi` の Research フェーズに組み込む:

```markdown
# /rpi Research フェーズに追加するチェックリスト
- [ ] パッケージ構造の分析
- [ ] ビジネスロジック概要の生成
- [ ] API エンドポイント一覧
- [ ] データモデルの図解
- [ ] 外部依存関係のマッピング
- [ ] コーディング規約の検出
```

#### Phase 3: 過信防止ルールの強化

AI-DLC の `overconfidence-prevention.md` の知見を `rules/common/` に追加:

```markdown
# 追加ルール
- 「疑わしければ質問する」を明示的にルール化
- 曖昧な回答（"depends", "not sure"）には必ずフォローアップ
- 複数ステージにまたがる判定は人間に確認を求める
```

#### Phase 4: audit.md パターンの実験的導入

AutoEvolve の learnings と AI-DLC の audit.md を融合:

```markdown
# aidlc-docs/audit.md ← 各プロジェクトに生成
## [ISO timestamp] — Stage: Requirements Analysis
- **Input**: ユーザーの意図「認証機能を追加」
- **Decision**: OAuth2 + JWT を選択（理由: 既存 API との整合性）
- **Artifacts**: requirements.md 生成
```

### 14.4 実装ロードマップ

| Phase | 変更対象 | 作業量 | 依存関係 |
|---|---|---|---|
| **Phase 1** | `references/workflow-guide.md` | S | なし |
| **Phase 2** | `/rpi` スキル + テンプレート | M | Phase 1 |
| **Phase 3** | `rules/common/overconfidence-prevention.md` | S | なし |
| **Phase 4** | AutoEvolve 連携 | M | Phase 1, 3 |

---

## 15. AWS ホワイトペーパー全文分析

**正式名称**: "AI-Driven Development Lifecycle (AI-DLC) Method Definition"
**著者**: Raja SP, Amazon Web Services
**URL**: https://prod.d13rzhkk8cj2z0.amplifyapp.com/
**形式**: PDF（JS SPA でホスト、Playwright MCP で描画取得）

### 15.1 ドキュメント構成

| セクション | 内容 |
|---|---|
| I. CONTEXT | AI-Assisted → AI-Driven への進化の文脈 |
| II. KEY PRINCIPLES | 10の設計原則 |
| III. CORE FRAMEWORK | アーティファクト、フェーズ＆儀式、ワークフロー |
| IV. AI-DLC IN ACTION: Green-Field | グリーンフィールド開発の具体例 |
| V. AI-DLC IN ACTION: Brown-Field | ブラウンフィールド開発の具体例 |
| VI. ADOPTING AI-DLC | 導入戦略 |
| APPENDIX A | AI との対話プロンプト集 |

### 15.2 10の設計原則（KEY PRINCIPLES）

これらはステアリングルールの**設計根拠**であり、リポジトリのルールファイルには直接記載されていない。

| # | 原則 | 要旨 | dotfiles との関連 |
|---|---|---|---|
| 1 | **Reimagine Rather Than Retrofit** | Agile の改造ではなく第一原理から設計。Sprint は週単位→Bolt は時間〜日単位 | 我々も Agile フレームワークに依存しない独自設計 |
| 2 | **Reverse the Conversation Direction** | AIが会話を主導し、人間が承認。Google Maps のアナロジー（人間は目的地を設定、AIがナビ） | 同一思想（harness hooks が自動検出→agent が実行） |
| 3 | **Integration of Design Techniques** | DDD/BDD/TDD を方法論のコアに統合。Scrum のように「チームに任せる」としない | **新知見**: AI-DLC は DDD フレーバーが基本。BDD/TDD フレーバーも計画中 |
| 4 | **Align with AI Capability** | AI-Assisted（人間がメイン）でも AI-Managed（丸投げ）でもなく、AI-Driven（AIが主導＋人間が監督） | 同一思想（Human in the loop） |
| 5 | **Cater to Building Complex Systems** | 複雑なシステム構築を対象。シンプルなものは low-code/no-code で | S/M/L 判定で対応（Sは軽量フロー） |
| 6 | **Retain What Enhances Human Symbiosis** | User Stories やリスクレジスタなど、人間-AI 共生に有用な既存アーティファクトは保持 | 既存アーティファクト（PLANS.md 等）を活用 |
| 7 | **Facilitate Transition Through Familiarity** | 1日で習得可能。連想学習のため既存用語との対応を明示（Sprint→Bolt 等） | `/rpi`, `/epd` 等の既存ワークフローとの整合 |
| 8 | **Streamline Responsibilities** | AI により専門化サイロ（フロントエンド/バックエンド/DevOps/セキュリティ）を統合 | マルチモデル連携で部分的に実現 |
| 9 | **Minimise Stages, Maximise Flow** | 最小限の段階で継続的フロー。人間の検証は**損失関数**として機能 | **重要メタファー**: 各承認ゲートは loss function |
| 10 | **No Hard-Wired Workflows** | 開発パスごとに固定ワークフローを処方しない。AIが意図に応じた Level 1 Plan を提案 | ALWAYS/CONDITIONAL ステージ判定の理論的根拠 |

### 15.3 アーティファクトの形式的定義

ホワイトペーパーにはリポジトリの terminology.md より**精密な定義**が記載:

| アーティファクト | 定義 | 既知との差分 |
|---|---|---|
| **Intent** | ビジネスゴール・機能・技術的成果をカプセル化した高レベルの目的宣言。AI駆動分解の起点 | terminology.md と一致 |
| **Unit** | Intentから導出された、測定可能な価値を提供する凝集的・自己完結的な作業要素。DDDのサブドメインまたはScrumのエピックに類似。**疎結合**で自律開発・独立デプロイ可能 | **新情報**: DDD サブドメインとの明示的対応 |
| **Bolt** | Unit内の最小反復。Sprint のリブランディングだが、時間〜日単位。Unit を1つ以上の Bolt で実行（並列・逐次） | **新情報**: 並列 Bolt の明示 |
| **Domain Design** | インフラ非依存のビジネスロジックモデル。DDD原則（aggregate, value object, entity, domain event, repository, factory）を使用 | **新情報**: DDD タクティカルパターンの明示的使用 |
| **Logical Design** | Domain Design を NFR とアーキテクチャパターン（CQRS, Circuit Breaker 等）で拡張。ADR を AI が作成 | **新情報**: ADR 自動生成 |
| **Deployment Unit** | パッケージ済みコード（コンテナイメージ、Lambda等）+ 設定（Helm Chart等）+ インフラ（Terraform/CFN）。機能テスト・セキュリティテスト・負荷テスト済み | terminology.md にない詳細 |

### 15.4 フェーズと儀式（Rituals）

ホワイトペーパーでは**儀式**という概念が詳細に定義されている（リポジトリのルールファイルには反映されていない）:

#### Mob Elaboration（Inception Phase の儀式）

```
参加者: Product Owner + Developers + QA + その他ステークホルダー（= "the mob"）
場所: 単一の部屋、共有スクリーン、ファシリテーター主導
AI の役割: Intent → User Stories + Acceptance Criteria + Units の初期分解を提案
人間の役割: over/under-engineering の調整、現実世界の制約との整合

出力:
  a) PRFAQ
  b) User Stories
  c) Non-Functional Requirement (NFR) 定義
  d) リスク記述（組織のリスクレジスタとマッチ）
  e) ビジネスインテントにトレース可能な測定基準
  f) Bolt の提案

効果: 週〜月の逐次作業を数時間に圧縮
```

#### Mob Construction（Construction Phase の儀式）

```
参加者: 全チームが単一の部屋にコロケーション
活動: ドメインモデル段階で統合仕様を交換、意思決定、Bolt のデリバリー
```

**重要な発見**: AI-DLC は単なるツール/ワークフローではなく、**物理的なコロケーションを伴う儀式**を規定している。これはリポジトリのステアリングルールには反映されておらず、ホワイトペーパーでのみ定義されている。

### 15.5 ワークフローの理論的構造

```
Intent（意図）
  ↓ AI が Level 1 Plan を生成
  ↓ 人間が検証・承認
  ↓
各ステップを再帰的に分解:
  Level 1 Plan → Level 2 (subtasks) → ...
  各レベルで人間が監督（= loss function）
  ↓
全アーティファクトを永続化（= "context memory"）
  - 前方・後方トレーサビリティ
  - AI が各段階で最適なコンテキストを取得
```

**Loss Function メタファー**:

> "Each step serves as a strategic decision point where human oversight functions like a loss function — catching and correcting errors early before they snowball downstream"

これは AI-DLC の最も洗練された概念。各承認ゲートは機械学習の損失関数のように、下流の無駄を早期に刈り込む。

### 15.6 Brownfield 固有の追加ステップ

ホワイトペーパーでは Brownfield（既存システム変更）に対する追加ステップが明示:

1. **コードの意味的モデルへの昇格**: 既存コードをより高い抽象レベルの表現に変換
   - **静的モデル**: コンポーネント、記述、責務、関係
   - **動的モデル**: 重要なユースケースを実現するコンポーネント間相互作用
2. 開発者とPMが静的/動的モデルをレビュー・検証・修正
3. 以降は Greenfield と同一フロー

→ これはリポジトリの `reverse-engineering.md`（12ステップ分析）として実装されている。

### 15.7 導入戦略

| アプローチ | 概要 | 具体例 |
|---|---|---|
| **Learning by Practicing** | ドキュメントや研修ではなく、実際のシナリオでの儀式の実践。AWS SA が支援 | **AI-DLC Unicorn Gym**（食べログ等が参加） |
| **Developer Experience Tooling への埋め込み** | 組織のSDLCツールにAI-DLCを組み込み、開発者がシームレスに実践 | FlowSource（Cognizant）, CodeSpell（Aspire）, AIForce（HCL） |

### 15.8 Appendix A: プロンプトテンプレート

ホワイトペーパーには**具体的なプロンプト**が含まれている。これがステアリングルールの原型:

| フェーズ | プロンプトの役割指示 | 核心パターン |
|---|---|---|
| Setup | フォルダ構造の定義 | `aidlc-docs/` ディレクトリ構造 |
| User Stories | "expert product manager" | Plan → Review → Approve → Execute（チェックボックス）|
| Units | "experienced software architect" | 疎結合・高凝集の分解 |
| Domain Model | "experienced software engineer" | DDD 原則によるコンポーネントモデル |
| Code Generation | "experienced software engineer" | コンポーネント設計からの実装 |
| Architecture | "experienced Cloud Architect" | AWS サービスへのマッピング |
| Build IaC/APIs | "experienced software engineer" | Flask API 等の実装 |

**共通パターン**: 全プロンプトが以下の構造を持つ:
1. `Your Role:` — 役割の指定
2. `plan ... with checkboxes` — 計画の作成
3. `If any step needs my clarification` — 不明点は確認
4. `Do not make critical decisions on your own` — 独断禁止
5. `ask for my review and approval` — 承認ゲート
6. `mark the checkboxes as done` — 進捗追跡

→ これがそのまま `core-workflow.md` の各ステージの構造に発展した。

### 15.9 ホワイトペーパーとリポジトリの差分

| 観点 | ホワイトペーパー | リポジトリ実装 |
|---|---|---|
| **DDD の明示** | コアに統合、タクティカルパターン列挙 | 暗黙的（functional-design.md で言及のみ） |
| **儀式（Rituals）** | Mob Elaboration, Mob Construction を定義 | 未実装（個人 AI セッション前提） |
| **PRFAQ** | Inception の出力アーティファクトに含む | 未実装 |
| **ADR 自動生成** | Logical Design の出力 | 未実装 |
| **リスクレジスタ** | Inception の出力に含む | 未実装（Extensions でカバー） |
| **Bolt の並列実行** | 明示的に記述 | 未実装（per-unit ループは逐次） |
| **測定基準** | ビジネスインテントへのトレース | 未実装 |
| **損失関数メタファー** | 理論的根拠として明示 | 暗黙的（approval gate の設計意図） |
| **Level 1/2 Plan 階層** | 再帰的分解を定義 | workflow-planning.md で部分的に実装 |

**結論**: ホワイトペーパーは理論的ビジョンを示し、リポジトリはそのサブセットを実用的なステアリングルールとして実装している。特に**儀式（物理的コロケーション）、DDD タクティカルパターン、PRFAQ、ADR、並列Bolt** はまだ実装されていない。

---

## 16. 深層比較: 活かせるもの・改善すべきもの

AI-DLC のホワイトペーパー（10原則）、リポジトリ（30ファイル）、プラグイン（30ファイル）の知見と、dotfiles の現行設定（CLAUDE.md, workflow-guide.md, 13 rules, 8 GP, 10 constraints, 30+ scripts, 60+ skills/agents）を照合した深層分析。

### 16.1 活かせるもの（現行の強み — 維持・強化すべき）

#### A. 我々が AI-DLC より優れている点

| # | 領域 | dotfiles の実装 | AI-DLC の状況 | 優位性の根拠 |
|---|---|---|---|---|
| **S-01** | **Hook ベースの機械的強制** | `golden-check.py`, `completion-gate.py`, `protect-linter-config.py` 等 25+ hooks | ルールベースのみ（LLM の自主遵守に依存） | ルールは「忘れうる」。hook は「忘れない」。Determinism Boundary の核心 |
| **S-02** | **3軸レビュー** | Engineering + Product + Design（`product-reviewer`, `design-reviewer`） | Engineering 軸のみ | ホワイトペーパー原則8「Streamline Responsibilities」に反するが、品質は上 |
| **S-03** | **AutoEvolve 自動学習** | session-learner → autolearn → autoevolve の4層ループ | 手動改善のみ。学習の仕組みなし | AI-DLC は「人間が改善する」前提。我々は「AIが自己改善する」仕組み |
| **S-04** | **マルチモデル連携** | agent-router.py → Codex(設計/推論) + Gemini(1M分析/リサーチ) | 単一モデル前提 | AI-DLC 原則4「Align with AI Capability」を超えて実装 |
| **S-05** | **Failure Taxonomy** | FM-001〜010 + specification/generalization 分類 + 帰納的検証 | なし | エラー分析の体系化は AI-DLC に存在しない |
| **S-06** | **Constraints Library** | C-001〜010 のプロンプト注入用ソフト制約 | Extensions（opt-in/out だが動的制御は硬い） | 制約ライブラリはより柔軟でプラグマティック |
| **S-07** | **Spike → Validate パターン** | `/spike`（worktree 隔離）→ `/validate`（acceptance criteria 照合） | なし（直接 Construction） | プロトタイプ検証は AI-DLC にない「探索的」フェーズ |
| **S-08** | **Background Agents 基盤** | GitHub Actions ベースの自律実行 + worktree 隔離 | なし | AI-DLC はインタラクティブセッション前提 |

#### B. 設計思想が高度に一致している点（相互強化可能）

| # | 概念 | dotfiles | AI-DLC | 相互強化の方向 |
|---|---|---|---|---|
| **A-01** | Progressive Disclosure | CLAUDE.md → references/ → rules/ | core-workflow.md → rule-details/ → extensions/ | AI-DLC のオンデマンドロード戦略を参考に、references の遅延ロードを検討 |
| **A-02** | 適応的実行 | S/M/L でスケール | ALWAYS/CONDITIONAL + Minimal/Standard/Comprehensive | AI-DLC の多因子判定を S/M/L に統合（後述: I-01） |
| **A-03** | 承認ゲート | verification-before-completion + completion-gate.py | 各ステージの REVIEW REQUIRED | AI-DLC の Loss Function メタファーで設計根拠を明文化（後述: I-08） |
| **A-04** | セッション継続 | session-load.js + checkpoint | aidlc-state.md + Smart Context Loading | AI-DLC のチェックボックス追跡を Plan ファイルに統合 |
| **A-05** | セキュリティ | security-reviewer (OWASP) + rules/common/security.md | SECURITY-01〜15 Extension | AI-DLC の15ルールを security-reviewer のチェックリストとして取り込み可 |
| **A-06** | 過信防止 | golden-check.py（コード品質面） | overconfidence-prevention.md（質問省略面） | 相互補完: コード品質 + 質問省略の両面をカバー（後述: I-04） |

### 16.2 改善すべきもの（AI-DLC から取り込むべき知見）

#### I-01: タスク規模判定の多因子化（優先度: 高）

**現状の問題**:
```
S/M/L の判定基準が暗黙的。
「1行変更 = S」「複数ファイル = L」程度の粒度で、リスク・影響範囲・ステークホルダーが考慮されていない。
```

**AI-DLC の知見**: 多因子判定（ALWAYS/CONDITIONAL 各ステージで独立評価）+ 深度3段階（Minimal/Standard/Comprehensive）

**改善案**:
```markdown
# workflow-guide.md に追加する判定マトリクス

## タスク規模判定（多因子）

| 因子 | S | M | L |
|---|---|---|---|
| 変更規模 | 1-10行 | 11-200行 | 200行超 |
| リスク | 低（型安全、テスト済み） | 中（新ロジック追加） | 高（アーキテクチャ影響） |
| 影響範囲 | 単一ファイル | 単一モジュール | 複数モジュール/API境界 |
| 既存コード複雑度 | 自明 | 理解に調査必要 | ドメイン知識必要 |
| ステークホルダー | 自分のみ | チーム内 | チーム外/外部API |

**判定ルール**: 最も高い因子に合わせる（例: 変更10行でもリスク高 → L）

## 深度レベル（各段階内の深さ）

| 深度 | Plan | Test | Review |
|---|---|---|---|
| Minimal (S) | 1行の方針 | 修正箇所のみ | 省略可 |
| Standard (M) | 構造化 Plan | ユニット+統合 | 2並列 |
| Comprehensive (L) | 詳細 Plan + Decision Log | 3層テスト | 4並列+スペシャリスト |
```

**変更対象**: `references/workflow-guide.md`
**作業量**: S

#### I-02: 構造化された要件分析の導入（優先度: 高）

**現状の問題**:
```
/rpi の Research フェーズは「Explore エージェントで調査」だけ。
「何を調べるか」の構造がない。要件の明確化プロセスが欠如。
```

**AI-DLC の知見**: 9ステップ要件分析（Intent 分析 → 深度判定 → 現在要件評価 → 質問生成 → 回答分析 → 矛盾検出 → フォローアップ → 要件ドキュメント生成 → 承認ゲート）

**改善案**: `/rpi` の Research フェーズに要件分析チェックリストを追加:

```markdown
# Research フェーズ・チェックリスト（AI-DLC inspired）

## 1. Intent 分析
- [ ] ユーザーの意図を1文で要約できるか
- [ ] Greenfield（新規）か Brownfield（既存変更）か

## 2. 深度判定
- [ ] S/M/L 判定（多因子マトリクス参照）

## 3. 既存コード調査（Brownfield の場合）
- [ ] 関連モジュールの構造把握
- [ ] 影響を受けるAPIエンドポイント/インターフェース
- [ ] 既存テストのカバレッジ確認
- [ ] コーディング規約の検出

## 4. 要件の明確化
- [ ] 不明点があれば質問（過信せず質問する）
- [ ] 非機能要件（パフォーマンス、セキュリティ）の確認
- [ ] スコープ外の明示

## 5. リスク評価
- [ ] 既知のリスクと制約の列挙
- [ ] 影響範囲の図示（必要な場合）
```

**変更対象**: `commands/rpi.md` または `skills/rpi/SKILL.md`
**作業量**: M

#### I-03: Brownfield リバースエンジニアリングの体系化（優先度: 高）

**現状の問題**:
```
既存コードベースへの変更時、構造把握が Explore エージェント任せ。
「何を分析すべきか」のチェックリストがない。
```

**AI-DLC の知見**: 12ステップの体系的分析（パッケージ構造 → ビジネスロジック概要 → API ドキュメント → データモデル → 外部依存 → コーディング規約 → インフラ構成 → テスト戦略）+ 8つの出力アーティファクト

**改善案**: `references/` に Brownfield 分析テンプレートを追加

```markdown
# references/brownfield-analysis-template.md

## Brownfield 分析チェックリスト

### 必須（M/L タスク）
- [ ] パッケージ/モジュール構造の把握
- [ ] 変更対象のビジネスロジック概要
- [ ] 影響する API エンドポイント一覧
- [ ] データモデル/スキーマの確認

### 推奨（L タスク）
- [ ] 外部依存関係マッピング
- [ ] コーディング規約の検出（命名、パターン）
- [ ] テスト戦略と現在のカバレッジ
- [ ] 静的モデル（コンポーネント関係図）
- [ ] 動的モデル（主要ユースケースのシーケンス）
```

**変更対象**: 新規 `references/brownfield-analysis-template.md`
**作業量**: S

#### I-04: 過信防止ルールの導入（優先度: 高）

**現状の問題**:
```
golden-check.py はコード品質の逸脱を検出するが、
「AIが仕様の不明点を質問せずに推測で進める」過信は検出しない。
AI-DLC の初期バージョンで最大の問題だったのがこれ。
```

**AI-DLC の知見**:
- 旧: 「必要な場合のみ質問」→ AI が質問を省略しすぎた
- 新: 「疑わしければ質問。過信は悪い結果を生む」
- 曖昧な回答（"depends", "mix of", "not sure"）には必ずフォローアップ
- 各ステージの "Skip entire categories" 指示を撤廃

**改善案**: `rules/common/overconfidence-prevention.md` を新設

```markdown
# 過信防止ルール（AI-DLC overconfidence-prevention.md inspired）

## 原則: Default to Asking

疑わしければ質問する。推測で進めない。

## 質問すべき状況
- ユーザーの意図が複数の解釈を持つ場合
- 技術的選択肢が複数あり、どちらが適切か不明な場合
- 非機能要件（パフォーマンス、セキュリティ）が未指定の場合
- スコープが曖昧な場合

## 曖昧回答のフォローアップ
以下のキーワードが含まれる回答には必ず明確化を求める:
- 「場合による」「depends」
- 「混合」「mix of」
- 「わからない」「not sure」
- 「たぶん」「maybe」「probably」

## 禁止事項
- 要件が曖昧なまま実装に入ること
- ユーザーの意図を推測して確認なしに進めること
- 「シンプルだから質問不要」と判断すること（シンプルに見えても確認する）
```

**変更対象**: 新規 `rules/common/overconfidence-prevention.md`
**作業量**: S

#### I-05: ワークフロー変更管理の導入（優先度: 中）

**現状の問題**:
```
Plan を途中で変更する場合の手順が未定義。
「plan を更新する」とだけ記載されている。
影響範囲の評価や、依存ステップの再実行判断がない。
```

**AI-DLC の知見**: 8種類の中間変更パターン（スキップ、追加、再開、深度変更、一時停止、アーキテクチャ変更、Unit追加/削除、前ステージ再開）

**改善案**: `workflow-guide.md` にワークフロー変更管理セクションを追加:

```markdown
## ワークフロー変更管理

Plan 実行中に方針変更が必要になった場合:

| 変更パターン | 対処 |
|---|---|
| ステップのスキップ | 影響を評価 → ユーザーに確認 → Plan に SKIPPED マーク |
| ステップの追加 | 依存関係をチェック → Plan に挿入 → ユーザーに確認 |
| 前ステップの再実行 | カスケード影響を評価 → 依存する後続ステップも再評価 |
| スコープ変更 | Plan の Goal/Scope を更新 → 全ステップを再評価 |
| 一時停止 | /checkpoint → 再開時に状態を復元 |
| アーキテクチャ変更 | 早期 = 低コスト、後期 = 高コスト → ユーザーに影響を説明 |

**原則**: 変更は Decision Log に記録する。暗黙に変更しない。
```

**変更対象**: `references/workflow-guide.md`
**作業量**: S

#### I-06: Decision Log の AI-DLC 形式への強化（優先度: 中）

**現状の問題**:
```
Plan テンプレートに Decision Log は含まれるが、フォーマットが弱い。
「何を決めたか」は記録されるが「なぜ」「何を捨てたか」が抜けやすい。
```

**AI-DLC の知見**: audit.md に全決定をタイムスタンプ + 代替案 + 却下理由で記録

**改善案**: Plan テンプレートの Decision Log を強化:

```markdown
## Decision Log

| 日時 | 決定 | 代替案 | 却下理由 | 影響範囲 |
|---|---|---|---|---|
| 2026-03-13T12:00 | JWT 認証を採用 | Session-based, OAuth2 | Session: スケーラビリティ懸念、OAuth2: 現時点で過剰 | API 全体 |
```

**変更対象**: `references/workflow-guide.md` の Plan テンプレート部分
**作業量**: S

#### I-07: Security Baseline チェックリストの取り込み（優先度: 中）

**現状の問題**:
```
security-reviewer エージェントは OWASP Top 10 ベースだが、
AI-DLC の SECURITY-01〜15 のような「ステージごとに適用するルールの構造化」がない。
```

**AI-DLC の知見**: 15セキュリティルール（SECURITY-01〜15）、各ルールに Rule ID + Verification Steps + Blocking/Non-Blocking 分類

**改善案**: `references/review-checklists/security-baseline.md` として AI-DLC の15ルールを取り込み、security-reviewer のプロンプトに注入

**変更対象**: 新規 `references/review-checklists/security-baseline.md`
**作業量**: M

#### I-08: Loss Function メタファーの明文化（優先度: 低）

**現状の問題**:
```
verification-before-completion, completion-gate.py 等が承認ゲートとして機能するが、
「なぜこれらのゲートが重要か」の設計根拠が未明文化。
```

**AI-DLC の知見**:

> "Each step serves as a strategic decision point where human oversight functions like a loss function — catching and correcting errors early before they snowball downstream"

**改善案**: `workflow-guide.md` の冒頭に設計根拠セクションを追加:

```markdown
## 設計根拠

各承認ゲート（Plan承認、Test、Review、Verify、Security）は ML の**損失関数**として機能する。
早期に誤りを検出し、下流の無駄な作業を刈り込む。
後工程ほど修正コストが高いため、前工程のゲートほど重要。
```

**変更対象**: `references/workflow-guide.md`
**作業量**: S

#### I-09: AI-DLC SECURITY-01〜15 と既存 security ルールの統合（優先度: 中）

**現状と AI-DLC の対応表**:

| AI-DLC | dotfiles 既存 | ギャップ |
|---|---|---|
| SECURITY-01: 暗号化 | ✅ rules/common/security.md | なし |
| SECURITY-02: アクセスログ | ⚠️ 部分的（構造化ログは error-handling.md） | アクセスログの明示なし |
| SECURITY-03: アプリケーションログ | ✅ error-handling.md | なし |
| SECURITY-04: HTTP セキュリティヘッダー | ❌ なし | **ギャップ** |
| SECURITY-05: 入力バリデーション | ✅ GP-002 + security.md | なし |
| SECURITY-06: 最小権限 | ✅ security.md（AI Agent Era セクション） | なし |
| SECURITY-07: ネットワーク構成 | ❌ なし（インフラ範囲外） | 対象外で妥当 |
| SECURITY-08: アクセス制御 (OWASP A01) | ✅ security-reviewer | なし |
| SECURITY-09: セキュリティ硬化 (OWASP A02) | ⚠️ 部分的 | 設定ミス防止が弱い |
| SECURITY-10: サプライチェーン (OWASP A03) | ✅ GP-003 + C-002 | なし |
| SECURITY-11: セキュアデザイン (OWASP A06) | ⚠️ 暗黙的 | 明示的ルールなし |
| SECURITY-12: 認証 (OWASP A07) | ✅ security.md | なし |
| SECURITY-13: データ整合性 (OWASP A08) | ❌ なし | **ギャップ** |
| SECURITY-14: ログ・モニタリング (OWASP A09) | ⚠️ 部分的 | アラート基準なし |
| SECURITY-15: 例外処理 (OWASP A10) | ✅ GP-004 + error-handling.md | なし |

**ギャップ**: SECURITY-04（HTTPヘッダー）、SECURITY-13（データ整合性）、SECURITY-09/11（セキュアデザイン/硬化）

### 16.3 改善ロードマップ

| 優先度 | ID | 改善項目 | 変更対象 | 作業量 | 依存 |
|---|---|---|---|---|---|
| **高** | I-01 | 多因子タスク規模判定 | workflow-guide.md | S | なし |
| **高** | I-02 | 構造化要件分析 | rpi.md / SKILL.md | M | I-01 |
| **高** | I-03 | Brownfield 分析テンプレート | 新規 reference | S | なし |
| **高** | I-04 | 過信防止ルール | 新規 rule | S | なし |
| **中** | I-05 | ワークフロー変更管理 | workflow-guide.md | S | なし |
| **中** | I-06 | Decision Log 強化 | workflow-guide.md | S | なし |
| **中** | I-07 | Security Baseline 取込 | 新規 checklist | M | なし |
| **低** | I-08 | Loss Function 明文化 | workflow-guide.md | S | なし |
| **中** | I-09 | セキュリティギャップ対応 | security.md | M | I-07 |

**Phase 1（即座に実施可能）**: I-01, I-03, I-04, I-05, I-06, I-08 — 全て S 作業量、依存なし
**Phase 2（Phase 1 後）**: I-02 — /rpi の構造変更
**Phase 3（Phase 1 後、独立）**: I-07, I-09 — セキュリティ系

### 16.4 取り込まないもの（意図的に除外）

| AI-DLC の機能 | 除外理由 |
|---|---|
| **ファイルベース Q&A** | Chat-based が優れている。Claude Code の AskUserQuestion で十分 |
| **Mob Elaboration / Mob Construction** | 物理的コロケーション前提。個人開発者には不適 |
| **PRFAQ** | `/spec` の acceptance_criteria で代替。PRFAQ は企業向けアーティファクト |
| **aidlc-state.md（専用状態ファイル）** | Plan ファイルのチェックボックスで代替。専用ファイルは過剰 |
| **audit.md（全入力の生ログ）** | AutoEvolve learnings で代替。生ログは個人開発では過剰 |
| **Unit of Work の厳密な分解** | `/autonomous` の task_list.md で部分対応済み。厳密な Unit 定義は大規模チーム向け |
| **DDD タクティカルパターンのコア統合** | 方法論レベルでの統合は過剰。必要時に reference として参照する方が適切 |
| **Bolt（Sprint のリブランディング）** | 用語変更のみで実質的な改善なし |

---

## 17. 追加調査候補

| 項目 | 優先度 | 理由 |
|---|---|---|
| Kiro CLI vs Claude Code 比較 | 中 | AWS 専用ツールの機能差 |
| Peter Tilsen 批判記事（Medium） | 中 | 403 でブロック。批判的視点 |
| Gaudiy `aidlc-kit` プラグイン構造 | 中 | カスタムフロー（α/β Construction）の実装パターン |
| dotfiles 統合 Phase 1 実装 | 高 | I-01, I-03, I-04 の即時実施 |

---

## Sources

- [AWS DevOps Blog: AI-Driven Development Life Cycle](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)
- [AWS Japan Blog: AI駆動開発ライフサイクル](https://aws.amazon.com/jp/blogs/news/ai-driven-development-life-cycle/)
- [Open-Sourcing Adaptive Workflows for AI-DLC](https://aws.amazon.com/blogs/devops/open-sourcing-adaptive-workflows-for-ai-driven-development-life-cycle-ai-dlc/)
- [Building with AI-DLC using Amazon Q Developer](https://aws.amazon.com/blogs/devops/building-with-ai-dlc-using-amazon-q-developer/)
- [re:Invent 2025 DVT214 セッションレポート](https://dev.to/kazuya_dev/aws-reinvent-2025-introducing-ai-driven-development-lifecycle-ai-dlc-dvt214-32b)
- [AWS re:Post: Why AI Coding Assistants Make Developers Slower](https://repost.aws/articles/ARWSOgROfUTFq4vv5y2hTglw/why-ai-coding-assistants-make-developers-slower-and-how-ai-dlc-delivers-10-x-velocity)
- [Gaudiy Tech Blog: AI-DLC 3ヶ月実践](https://techblog.gaudiy.com/entry/2025/12/15/114820)
- [食べログ Tech Blog: AI-DLC Unicorn Gym](https://tech-blog.tabelog.com/entry/aws-ai-dlc-unicorn-gym)
- [東京海上日動システムズ AI-DLC 事例](https://aws.amazon.com/jp/blogs/news/tokio-marine-ai-dlc/)
- [サーバーワークス: Kiro CLI + AI-DLC](https://blog.serverworks.co.jp/kiro-cli-aidlc-experience)
- [NashTech Blog: AI-DLC Revolution](https://blog.nashtechglobal.com/ai-dlc-the-next-revolution-in-software-development-when-ai-becomes-the-true-leader/)
- [ai-dlc.dev 公式サイト](https://ai-dlc.dev/)
- [awslabs/aidlc-workflows GitHub](https://github.com/awslabs/aidlc-workflows)
- [ijin/aidlc-cc-plugin GitHub](https://github.com/ijin/aidlc-cc-plugin)
