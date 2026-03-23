# ワークフロー詳細ガイド

CLAUDE.md から参照される詳細ドキュメント。タスク実行時に必要に応じて読み込む。

## 設計根拠

各承認ゲート（Plan承認、Test、Review、Verify、Security）は ML の**損失関数**として機能する。
早期に誤りを検出し、下流の無駄な作業を刈り込む。後工程ほど修正コストが高いため、前工程のゲートほど重要。

> "Each step serves as a strategic decision point where human oversight functions like a loss function — catching and correcting errors early before they snowball downstream"
> — AI-DLC Method Definition (Raja SP, AWS)

---

## 6段階プロセス（詳細）

すべての非自明なタスクは以下の6段階で進める:

### Plan ファイルの扱い

- root の `PLANS.md` を plan contract として扱う
- 一時 plan は `tmp/plans/` に置ける
- handoff、長時間タスク、または将来参照したい plan は `docs/plans/` に保存する
- plan には最低でも Goal / Scope / Constraints / Validation / Steps / Progress / Decision Log を含める
- plan は作成後も更新し、goal や validation を暗黙に変えない

### Unit of Work 分解（L 規模のみ）

L 規模のタスクでは、作業を疎結合な Unit に分解して並列実行を可能にする。
AI-DLC の Unit of Work 概念に基づく。

#### テンプレート

```markdown
## Units

| Unit | 説明 | 依存 | 担当 | ステータス |
|---|---|---|---|---|
| U-1 | 認証モジュール | なし | worktree-1 | 🔵 未着手 |
| U-2 | API エンドポイント | U-1 | worktree-2 | 🔵 未着手 |
| U-3 | フロントエンド | U-2 | - | 🔵 未着手 |
```

#### Unit 設計の原則

- **疎結合**: 各 Unit は独立してテスト・デプロイ可能
- **高凝集**: 1つの Unit は1つの責務に集中
- **依存の明示**: 依存関係がある場合は DAG として表現
- **並列実行**: 依存関係がない Unit は `/autonomous` + worktree で並列実行

### Decision Log フォーマット

Plan の Decision Log は「何を決めたか」だけでなく「なぜ」「何を捨てたか」を記録する:

```markdown
## Decision Log

| 日時 | 決定 | 代替案 | 却下理由 | 影響範囲 |
|---|---|---|---|---|
| 2026-03-13T12:00 | JWT 認証を採用 | Session-based, OAuth2 | Session: スケーラビリティ懸念、OAuth2: 現時点で過剰 | API 全体 |
```

### ワークフロー変更管理

Plan 実行中に方針変更が必要になった場合、以下のパターンで対処する。変更は Decision Log に記録し、暗黙に変更しない:

| 変更パターン | 対処 |
|---|---|
| **ステップのスキップ** | 影響を評価 → ユーザーに確認 → Plan に SKIPPED マーク |
| **ステップの追加** | 依存関係をチェック → Plan に挿入 → ユーザーに確認 |
| **前ステップの再実行** | カスケード影響を評価 → 依存する後続ステップも再評価 |
| **スコープ変更** | Plan の Goal/Scope を更新 → 全ステップを再評価 → ユーザーに確認 |
| **一時停止** | `/checkpoint` → 再開時に Plan の状態を復元 |
| **アーキテクチャ変更** | 早期 = 低コスト、後期 = 高コスト → ユーザーに影響を説明してから判断 |

### 1. Plan（計画）

- 要件を明確化し、既存コードを調査する
- **`/check-health` を実行** — ドキュメント鮮度・参照整合性を確認する
- **cross-model insight 確認** — 過去のセッションで他モデルが発見した関連知見がないか `references/cross-model-insights.md` を確認する
- `search-first` スキル — 実装前に既存の解決策を検索する
- brainstorming スキルでアイデアを設計に落とす
- writing-plans スキルで実装計画を策定する
- **Best-of-N プランニング（L 規模で推奨）**: 複数モデルに独立してプラン草案を出させ、最良の要素を統合する。手順: (1) Claude / Codex / Gemini にそれぞれ独立にプラン草案を生成させる（`/debate` または個別委譲）、(2) 各プランの強み・弱みを比較表にまとめる、(3) 最良の要素を統合した最終プランを作成する。全モデルが一致する部分は信頼度が高く、分岐する部分はリスク要因として Decision Log に記録する
- **Plan レビュー（M/L 必須）**: Plan 作成後、ユーザーに提示する**前に** `plan-document-reviewer` サブエージェントを dispatch してレビューを実施する。Issues Found なら修正して再レビュー、Approved ならユーザーへ提示する（writing-plans スキルの Plan Review Loop に従う。最大3イテレーション）
- **L規模のみ**: チェックポイントコミットを作成してから着手する（`git add -A && git commit -m "checkpoint: before {task description}"`）

### 1.3. プロジェクト俯瞰 — M/L 規模のみ

大規模な変更では、コードを書く前にプロジェクトのアーキテクチャ的信念を構築する:

1. **config/registry ファイルを最優先で読む** — モジュール接続情報の源泉
2. **エントリポイント / オーケストレーターを特定** — データフローの全体像を把握
3. **発見した依存関係と不変条件を明示的にメモ** — コンテキスト圧縮時にも保持される

根拠: Theory of Code Space 論文 (arXiv:2603.00601) — config 優先戦略は Random の 3倍の効率。構造化マップの保持で依存関係理解が +14 F1 改善。

### 1.5. Risk Analysis（リスク分析）— M/L 規模のみ

Plan 策定後、実装前に潜在リスクを洗い出すゲート。
**設計思想**: Claude の「注意の幅」（プロダクト直感・暗黙の仕様を形にする力）と Codex の「注意の深さ」（潜在リスク・セキュリティ・障害モードを自発的に指摘する力）を組み合わせる。

| タスク規模 | リスク分析の構成 |
|---|---|
| **M** | `edge-case-analysis` + `codex-risk-reviewer` を**並列起動**（幅 + 深さ） |
| **L** | 同上 + Plan 批評（下記「Plan Second Opinion」参照） |

**起動方法**:
- `edge-case-analysis` + `codex-risk-reviewer` を**1メッセージで並列起動**（M/L 共通）

**Plan Second Opinion（L 規模のみ）**:
Plan 策定後に Codex の clean context で批評させる。メモリを持たないエージェントは同じバイアスに囚われないため、Plan の盲点を発見しやすい。

```bash
codex exec --skip-git-repo-check -m gpt-5.4 \
  --config model_reasoning_effort="high" \
  --sandbox read-only \
  "Read the plan at {plan_path} and critique it. What assumptions are wrong? What could go wrong? What's missing?" \
  2>/dev/null
```

**判定**:
- CRITICAL リスクが見つかった場合 → Plan を修正してから Implement に進む
- HIGH リスクが見つかった場合 → Plan に緩和策を追記してから Implement に進む
- MEDIUM 以下のみ → そのまま Implement に進む

### 2. Implement（実装）

- 計画に従い、最小限のコード変更で実装する
- 既存パターンに従う。新しい抽象化は最小限に
- TDD が可能な場合はテストを先に書く

### 3. Test（テスト）

- test-engineer エージェントにテスト作成を委譲
- ユニット → 統合 → E2E の3層で検証
- テストが通らなければ実装に戻る

### 3.1. Eval 優先原則

Agent の出力品質が低下した場合、**まず評測（eval）を疑い、次に Agent を修正する**。

| 状況 | まずやること | やってはいけないこと |
|------|-------------|-------------------|
| テストが不安定 | テスト環境・リソース制約を確認 | Agent のプロンプトを変更 |
| スコアが低下 | 評価基準のドリフトを確認 | モデルを切り替え |
| 新機能で既存テスト失敗 | テストが現仕様と整合しているか確認 | テストを削除 |

**判断フロー**:
1. 評測基盤のエラー率を確認（infra error ≠ Agent error）
2. 評分器のキャリブレーション確認（TPR/TNR — `evaluator-calibration-guide.md` 参照）
3. 基盤に問題なければ Agent の修正に進む

### 4. Review（レビュー）

`/review` スキルのワークフローに従う。スケーリング・言語検出・スペシャリスト選択・結果統合の詳細はスキル内の `skills/review/references/reviewer-routing.md` と `skills/review/templates/review-output.md` を参照。

- 指摘があれば修正してから次へ
- `/codex-review` は手動で個別に使うスキル。自動レビューフローでは `/review` スキルの Agent 並列起動に統一する

### 5. Verify（検証）

- `verification-before-completion` スキルで完了前検証
- ビルド・テスト・lint を実際に実行し、出力を確認してから完了宣言
- 仮定に基づく「問題ありません」は禁止

### 6. Security Check（セキュリティ）

- `/security-review` コマンドでセキュリティチェック
- security-reviewer エージェントに OWASP Top 10 ベースの分析を委譲
- Critical/High の指摘は必ず修正してからコミット

```
Plan -> Risk Analysis -> Implement -> Test -> Review -> Verify -> Security Check -> Commit

失敗時のループ:
- リスク分析で CRITICAL → Plan を修正して再分析
- テスト失敗             -> Implement に戻る
- レビュー指摘           -> Implement に戻る
- 検証失敗               -> Implement に戻る
- セキュリティ指摘       -> Implement に戻る
```

---

## タスク規模による段階スケーリング

全タスクで6段階を律儀に踏む必要はない。規模に応じてスケールする:

| 規模            | 例                                | 必須段階                         | スキップ可能                           |
| --------------- | --------------------------------- | -------------------------------- | -------------------------------------- |
| **S（軽微）**   | typo修正、1行変更、設定値変更     | Implement → Verify                              | Spec Review, Plan, Risk Analysis, Test, Review, Security |
| **M（標準）**   | 関数追加、バグ修正、小機能        | Spec Review → Plan → Risk Analysis → Implement → Test → Verify | 4並列レビューは1-2エージェントに縮小可           |
| **L（大規模）** | 新機能、リファクタリング、API設計 | Spec Review → Checkpoint → 全7段階（Risk Analysis 含む） | なし                                             |

### Spec Review の定義（M/L で必須）

M/L 規模のタスクで実装に入る前に仕様の品質を確認するゲート。S は免除。

1. `rules/common/overconfidence-prevention.md` の 6 つの Spec Slop 指標をパスすること
2. 曖昧な要件が 0 になるまで質問で解消すること
3. Design Rationale（`references/comprehension-debt-policy.md`）の 3 点が記述されていること

### 多因子タスク規模判定

行数だけで判定しない。**最も高い因子に合わせる**（例: 変更10行でもリスク高 → L）:

| 因子 | S | M | L |
|---|---|---|---|
| **変更規模** | 1-10行 | 11-200行 | 200行超 |
| **リスク** | 低（型安全、テスト済み） | 中（新ロジック追加） | 高（アーキテクチャ影響） |
| **影響範囲** | 単一ファイル | 単一モジュール | 複数モジュール/API境界 |
| **既存コード複雑度** | 自明 | 理解に調査必要 | ドメイン知識必要 |
| **ステークホルダー** | 自分のみ | チーム内 | チーム外/外部API |

### 深度レベル（各段階内の深さ）

S/M/L は「どの段階を踏むか」を決める。深度は「各段階をどの程度深くやるか」を決める:

| 深度 | Plan | Research | Test | Review | 条件付きスキップ |
|---|---|---|---|---|---|
| **Minimal** (S default) | 1行の方針 | 対象ファイルのみ | 修正箇所のみ | 省略可 | Plan, Test, Review, Security |
| **Standard** (M default) | 構造化 Plan | モジュール単位 | ユニット+統合 | 2並列 | 既存テスト充実時: Test を Minimal に降格可 |
| **Comprehensive** (L default) | 詳細 Plan + Decision Log | Brownfield 分析テンプレート参照 | 3層テスト | 4並列+スペシャリスト | なし（全段階必須） |

Brownfield（既存コード変更）の場合: `references/brownfield-analysis-template.md` を参照。

### ステージ単位の条件判定

S/M/L はデフォルトの深度を決めるが、個別ステージの深度は状況に応じて上下する:

| ステージ | 降格条件（深度を下げてよい） | 昇格条件（深度を上げるべき） |
|---|---|---|
| **Research** | 変更対象が自明（自分が書いたコード等） | 未知のコードベース、外部ライブラリ |
| **Test** | 既存テストが変更箇所を十分カバー | テストカバレッジが低い、回帰リスクあり |
| **Review** | 変更が既存パターンの踏襲のみ | 新しいパターンの導入、API 境界の変更 |
| **Security** | 内部ロジックのみ、外部入力なし | ユーザー入力処理、認証/認可、暗号化 |

**判定タイミング**: Research フェーズ完了時に、各ステージの深度を最終決定する。
**記録**: 降格/昇格した場合は Plan の Decision Log に理由を記録する。

### レビュースケーリング

`/review` スキルを参照。変更規模に応じて1〜5エージェント並列 + コンテンツベースのスペシャリスト自動検出。

---

## エージェントルーティング

タスクの種別に応じて、最適なエージェントを選択する:

| タスク種別               | 推奨エージェント             | 用途                                                    |
| ------------------------ | ---------------------------- | ------------------------------------------------------- |
| アーキテクチャ設計       | `backend-architect`          | API設計、DB設計、システム構成                           |
| Next.js 設計             | `nextjs-architecture-expert` | App Router、RSC、パフォーマンス                         |
| フロントエンド実装       | `frontend-developer`         | React コンポーネント、UI/UX                             |
| コードレビュー           | `/review` スキルで自動選択   | 変更規模に応じて1〜5視点の並列レビュー + スペシャリスト |
| テスト作成               | `test-engineer`              | テスト戦略、テスト実装                                  |
| デバッグ                 | `debugger`                   | 根本原因分析、バグ修正                                  |
| セキュリティ             | `security-reviewer`          | 脆弱性検出、OWASP準拠                                   |
| ビルドエラー             | `build-fixer`                | 型エラー、コンパイル失敗、依存関係修正                  |
| タスク振り分け           | `triage-router`              | タスク種別判定、最適エージェントへルーティング          |
| Go 開発                  | `golang-pro`                 | Go パターン、並行処理                                   |
| TypeScript 開発          | `typescript-pro`             | 型設計、高度な型推論                                    |
| Git 履歴調査             | `safe-git-inspector`         | 安全な git 履歴調査（読み取り専用）                     |
| DB 調査                  | `db-reader`                  | 安全な DB 読み取り調査（SELECT のみ）                   |
| Gemini リサーチ          | `gemini-explore`             | 1Mコンテキスト分析、外部リサーチ、マルチモーダル        |
| Codex リスク分析         | `codex-risk-reviewer`        | Plan 策定後の潜在リスク・障害モード分析（実装前ゲート） |
| Codex レビュー           | `codex-reviewer`             | Codex による深い推論レビュー（並列起動）                |
| Codex デバッグ           | `codex-debugger`             | Codex による深いエラー分析・根本原因特定                |
| ドキュメントメンテナンス | `doc-gardener`               | 陳腐化ドキュメント検出・修正                            |
| コード品質スキャン       | `golden-cleanup`             | ゴールデンプリンシプル逸脱スキャン                      |
| UI 観察                  | `ui-observer`                | Playwright による UI 状態確認（サブエージェント限定）   |
| 並列リサーチ             | `/research` スキル           | マルチエージェント並列調査、レポート生成                |
| 自律実行                 | `/autonomous` スキル         | 長時間タスクのセッション跨ぎ自律実行                    |
| ブレイクスルー記録       | `/eureka` スキル             | 技術的発見の構造化記録、INDEX 管理                      |

### ルーティングルール

1. レビューは `/review` スキルに委譲（スケーリング・言語検出・スペシャリスト選択を自動実行）
2. 開発系エージェント（golang-pro, typescript-pro）はレビューアーとは別の役割
3. セキュリティが関わるコード変更は、通常レビューに加えて `security-reviewer` を追加
4. アーキテクチャ判断はアーキテクト系エージェントに委譲
5. 大規模コードベース分析・外部リサーチ・マルチモーダル処理は `gemini-explore` に委譲
6. 通常の `debugger` で困難なエラー分析は `codex-debugger` に委譲（Codex の深い推論を活用）
7. ドキュメントの陳腐化が疑われる場合は `doc-gardener` に委譲
8. コード品質の網羅的スキャンは `golden-cleanup` に委譲
9. UI の状態確認・バグ再現は `ui-observer` に委譲（Playwright をサブエージェント内に閉じ込め、メインコンテキストを保護）
10. **Agent Creation Heuristic (G5)** — デバッグが膠着したら、専門エージェントを作成して再起動する方が速い

#### デバッグ膠着の判断基準

以下のいずれかに該当したら「膠着」と判断し、専門エージェント作成を検討する:

| シグナル | 判断 |
|---------|------|
| 同一ドメインで context window exhaustion が発生 | 即座に検討 |
| 同じドメイン知識を 2 セッション以上で再説明 | 強く検討 |
| デバッグセッションが解決なく長時間化 | 検討 |

#### 回復手順

1. **失敗パターンを診断**: 何の知識が不足して膠着したかを特定（例: 座標変換の数式、ネットワーク同期の制約）
2. **専門エージェントを作成**: `skill-creator` スキルでブートストラップ。以下をエージェント定義に埋め込む:
   - ドメイン固有の Symptom-Cause-Fix テーブル（今回のデバッグで判明した内容）
   - コードパターンとアンチパターン（ファイルパス、関数名付き）
   - 既知の failure modes（再発防止）
3. **新セッションで再スタート**: 作成したエージェントを呼び出して同じタスクを再試行

> 論文の知見: 複雑ドメインのエージェントはコンテンツの 65% がドメイン知識。部分的な知識は却ってエラーを招く（Brevity Bias）。エージェントのドメイン知識は 50% 以上が推奨

### 仕様ドキュメントのメンテナンス

コード変更時に関連する仕様ドキュメント（`references/`, `docs/specs/`）を同期更新する。
エージェントは仕様を絶対的に信頼するため、陳腐化した仕様は silent failure を招く。

| タイミング | アクション |
|-----------|----------|
| コード変更時 | 変更したファイルに対応する仕様があれば、同セッション内で更新（~5分） |
| コミット時 | 仕様更新が必要なのに未更新でないか確認 |
| 隔週 | `/check-health` で全仕様の鮮度を一括チェック（30-45分） |

> 論文の実測値: 仕様メンテナンスの総コストは週 1-2 時間。古い仕様が原因で deprecated パスにコードを配線する事故が少なくとも 2 件報告

### ファクトリーエージェント

新プロジェクトのセットアップやドキュメント生成に使用する統合エージェント:

| エージェント       | 用途                                                                      |
| ------------------ | ------------------------------------------------------------------------- |
| `document-factory` | 統合ドキュメント生成（mode: agent / constitution / context で切り替え）    |

`permissionMode: plan` で動作し、生成前にユーザーの承認を得る。

### エージェント委譲パターン

タスクの性質に応じて、サブエージェント（fire-and-forget）と Agent Teams（ongoing coordination）を使い分ける。
詳細は **`references/subagent-delegation-guide.md`** を参照。

#### サブエージェント（独立タスク向け）

| パターン | 方式 | 使い所 | フレーミング |
|---|---|---|---|
| **Sync** | Agent ツール | 結果が次のステップに必要（レビュー、分析、テスト） | 簡潔に返す |
| **Async** | `claude -p` / `run_in_background` | 独立した長時間タスク（リサーチ、自律実行） | 自己完結的に返す |
| **Scheduled** | CronCreate / cron | 将来の特定時刻に実行（日次分析、フォローアップ） | ライブデータ優先 |

**判断基準**: 結果が必要 → Sync、独立タスク → Async、後で → Scheduled、迷ったら → Async

#### Agent Teams（協調タスク向け）

エージェント間で中間発見を共有し、動的に調整が必要な場合に使用。

| 判断 | サブエージェント | Agent Teams |
|---|---|---|
| 作業が embarrassingly parallel | ✅ | |
| 発見を他エージェントに即共有したい | | ✅ |
| 依存関係が動的に変化する | | ✅ |

#### 共通インフラ

- **自動推奨**: `agent-router.py` がキーワードから Async/Scheduled を自動検出し、additionalContext で推奨する
- **成果物追跡**: `task-registry.jsonl` で Async/Scheduled の成果物パスとステータスを追跡（`references/task-registry-schema.md`）
- **フレーミングテンプレート**: `references/subagent-framing.md`
- **分割原則**: コンテキスト境界で分割する（ロールではなく情報の重複度で判断）

---

## メモリシステム

### 3層構造

```
Session（一時）     → 会話内のコンテキスト、自動圧縮で管理
  ↓ 有用なパターン発見時
MEMORY.md（永続）   → プロジェクト横断の知見、デバッグパターン、ユーザー嗜好
  ↓ 十分な実証・信頼度が溜まった場合
Skill（形式知）     → スキルとして形式化、再利用可能なワークフローに昇格
```

### メモリ記録ルール

- 修正を受けたらパターンを memory に記録し、同じミスを防ぐ（`continuous-learning` スキル）
- MEMORY.md は200行以内に保つ。詳細は別ファイルに分離
- 機密情報（token, password, secret）は絶対に保存しない
- 重複記録を避ける。既存のメモリを確認してから書く
- 間違っていた記録は速やかに更新・削除する
- `/memory-status` でメモリの健全性を確認できる
- **Snapshot 制限**: MEMORY.md はセッション開始時に読み込まれる静的スナップショット。セッション中に memory を更新しても、その変更は次のセッションまで system prompt に反映されない。checkpoint/handoff 時は、後続セッションが必要とする情報を plan や checkpoint ファイルにも書くこと

### Plan と checkpoint の関係

- checkpoint は session 再開用の runtime state
- plan は goal、scope、validation、decision を残す作業記録
- 長時間タスクでは両方を使う
- checkpoint だけで plan を代用しない

---

## トークン予算

コンテキストウィンドウの効率的な使用を意識する:

| 使用率 | アクション                                                       |
| ------ | ---------------------------------------------------------------- |
| ~70%   | 通常運用。問題なし                                               |
| 80%    | **警告**: 不要なコンテキストを圧縮検討                           |
| 90%    | **圧縮推奨**: サブエージェントに委譲して新しいコンテキストで作業 |

### Context Placement Strategy（Lost-in-the-middle 対策）

LLM は長いコンテキストの中間部分を見落としやすい（Lost-in-the-middle 現象）。

**配置ルール**:
1. **重要情報は先頭と末尾に** — 中間に埋もれさせない
2. **サブエージェントへの指示は構造化** — 目的 → 制約 → 入力データ → 出力形式の順
3. **長い調査結果は要点を先頭に再掲** — 発見順ではなく重要度順に並べ替え
4. **Persistent Facts Block** — 圧縮されても残すべき事実は MEMORY.md に永続化

**実践パターン**:
- Explore エージェントの結果を受けたら、key findings を先に要約してから詳細に入る
- Plan ファイルの Goal/Constraints は冒頭に置く
- checkpoint 保存時は「次のセッションが最初に知るべきこと」を先頭に

### トークン節約テクニック

- 大きなファイルは必要な部分だけ Read（offset/limit 指定）
- 調査タスクは Explore エージェントに委譲（メインコンテキストを汚さない）
- 長い出力を返すコマンドは `head` や `tail` でフィルタ
- 独立したタスクはサブエージェントに並列委譲
- `/check-context` でセッション状態を確認できる

### セッション分離

- **1セッション1タスク**を原則とする。無関係なタスクを同じセッションで混ぜない
- 異なるタスクの文脈が混ざると、autocompact 後も前タスクの仮定が残留し、後半の品質が下がる
- タスク完了後は `/compact` または新セッションで切り替える
- 例外: 密接に関連するタスク（同一機能のフロント + バック等）は同一セッションでOK

### セッション粒度ルール（L 規模プロジェクト）

`feature_list.json` が存在するプロジェクトでは、**1セッション1機能**に集中する:

- 同一セッションで複数機能を完了させない（コンテキスト喪失のリスク）
- `completion-gate.py` が 2 機能以上の同時完了を検出した場合、advisory 警告を出す
- S/M 規模タスクにはこのルールを適用しない（過剰制約を避ける）
- 詳細は `references/session-protocol.md` を参照

### Worktree 分離

- 並列で別 task を走らせるときは `git worktree` を使って filesystem も分離する
- 片方の task が symlink、formatter、checkpoint、生成物を更新しても、もう片方に影響を漏らさない
- 1 task 1 session に加えて、1 branch 1 worktree を基本とする
- 運用詳細は `docs/playbooks/worktree-based-tasking.md` を参照する

---

## 新モデル追加ランブック

新しい LLM プロバイダ（CLI ツール）を委譲先として追加する際の手順。

1. **委譲ルール作成**: `rules/{model-name}-delegation.md` を作成。テンプレート:
   - 委譲すべきケース（そのモデルの強み）
   - 委譲方法（エージェント / スキル / 直接呼び出し）
   - 委譲しないケース（他モデルの方が適切な場面）
   - 性格傾向バイアス（既知の出力傾向と軽減策）
   - 言語プロトコル
2. **Expertise Map 更新**: `references/model-expertise-map.md` にドメイン別スコアを追加
3. **エージェント作成**（任意）: 専用エージェントが必要なら `agents/{model-name}-*.md` を作成
4. **agent-router.py 更新**: 自動委譲 hook のルーティング条件にモデルを追加
5. **`/debate` 対応**: `skills/debate/SKILL.md` のモデルリストに追加

> 既存の `rules/codex-delegation.md` と `rules/gemini-delegation.md` を参考にする。
> 各ファイルの構造を揃えることで、モデル間の比較・選択が容易になる。

---

## EPD ワークフロー（Engineering, Product & Design）

Harrison Chase "How Coding Agents Are Reshaping EPD" に基づく拡張ワークフロー。
実装コストがゼロに近づいた世界で、**何を作るべきか**と**品質の3軸レビュー**を強化する。

### 新規コマンド

| コマンド    | 用途                                                   |
| ----------- | ------------------------------------------------------ |
| `/spec`     | Prompt-as-PRD 生成（構造化プロンプトとして仕様を記述） |
| `/spike`    | プロトタイプファースト開発（worktree 隔離 → validate） |
| `/validate` | Product Validation（acceptance criteria 照合）         |
| `/epd`      | 統合ワークフロー（Spec → Spike → Build → Review）      |

### EPD フルフロー

```
Spec → Spike → Validate → Decide → Build(/rpi) → Review(3軸) → Commit
                              ↑                        ↓
                              └──── Pivot ─────────────┘
```

### レビュー3軸

| 軸          | エージェント       | 自動起動条件                             |
| ----------- | ------------------ | ---------------------------------------- |
| Engineering | 既存レビューアー群 | 常時（変更規模に応じてスケール）         |
| Product     | `product-reviewer` | `docs/specs/*.prompt.md` が存在する場合  |
| Design      | `design-reviewer`  | `.tsx/.css/.html` 等の UI ファイル変更時 |

### 使い分け

| シナリオ                 | 推奨コマンド         |
| ------------------------ | -------------------- |
| 不確実なアイデアの検証   | `/epd`（フルフロー） |
| 仕様が明確な機能開発     | `/rpi`（従来通り）   |
| 素早いプロトタイプだけ   | `/spike`             |
| 仕様書だけ作りたい       | `/spec`              |
| 実装後の仕様適合チェック | `/validate`          |
