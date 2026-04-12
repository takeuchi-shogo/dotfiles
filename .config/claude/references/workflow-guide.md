# ワークフロー詳細ガイド

CLAUDE.md から参照される詳細ドキュメント。タスク実行時に必要に応じて読み込む。

## Agent Micro-Loop（ターンレベルの実行規律）

> 出典: Claude Code 内部 `query.ts` の 5-phase iteration pattern を harness レベルの実行規律として抽出。

スキルやエージェントの各ターンは以下の5段階で実行する:

| Phase | 名称 | 内容 | 失敗時 |
|-------|------|------|--------|
| 1 | **Intake** | タスクのスコープ確認、前提条件チェック | スコープ不明なら AskUserQuestion |
| 2 | **Explore** | Read/Grep/Glob で現状把握。recall 重視 | Exploration Spiral 閾値(5回)で STOP |
| 3 | **Act** | Edit/Write/Bash で実装 | Edit Loop 閾値(3回/10min)で再プラン |
| 4 | **Verify** | テスト実行、diff 確認、期待値との突合。**事前宣言と比較** | 失敗は Explore に戻る |
| 5 | **Summarize** | 成果の要約。次ターンへの引き継ぎ情報を整理 | — |

> **Verify の強化ルール（Karpathy "Goal-Driven Execution"）**: Act フェーズに入る前に「この変更で何が変わるべきか」を1-3行で宣言する。Verify フェーズではその宣言と実際の結果を突き合わせる。宣言と結果が乖離した場合は Explore に戻る。

マクロワークフロー（Plan→Implement→Test→Review→Verify）の各ステップ内部で、このマイクロループが繰り返される。

---

## 設計根拠

各承認ゲート（Plan承認、Test、Review、Verify、Security）は ML の**損失関数**として機能する。
早期に誤りを検出し、下流の無駄な作業を刈り込む。後工程ほど修正コストが高いため、前工程のゲートほど重要。

> "Each step serves as a strategic decision point where human oversight functions like a loss function — catching and correcting errors early before they snowball downstream"
> — AI-DLC Method Definition (Raja SP, AWS)

### 非対称損失の原則

損失関数は**対称ではない**。見逃し（HITL すべきだったのにスルー）と過検出（不要な HITL）のコストは質的に異なる:

- **見逃し（下振れ）**: 損害は**指数的**に拡大する（本番 DB 破壊、セキュリティ侵害等）
- **過検出（上振れ）**: 損害は**線形**で予測可能（不要な確認の人件費）

> 見逃しによるインシデント 1 件の損害は、不要な HITL 10 件分のコストを容易に超える。

この非対称性に基づき、ゲートの厳格度は変更のリスクカテゴリで調整する:

| リスクカテゴリ | 対象例 | 方針 | Recall 重視度 |
|---------------|--------|------|---------------|
| **High** | セキュリティ、DB migration、本番設定、secrets | 見逃し許容度ゼロ。Recall 最大化（Fβ β≥3 相当） | 極高 |
| **Medium** | ビジネスロジック、API、hook/script | バランス（Fβ β=2 相当） | 中 |
| **Low** | ドキュメント、テスト、コメント、typo | Precision 重視。不要な HITL を減らす（Fβ β=1 相当） | 低 |

> 出典: 澁井祐介 "AIエージェントのHuman-in-the-Loop評価を深化させる" (LayerX, 2026-04)

---

## ワークフロー構造の判断基準

### "When Static is Enough" 3 条件テスト

以下の 3 条件が**同時に**成立する場合、静的ワークフロー（固定パイプライン）で十分。
1 つでも崩れたら動的適応を検討する。

| 条件 | 説明 | dotfiles での例 |
|------|------|----------------|
| **制約された演算子空間** | 使える操作（ツール、エージェント）が限定的で安定 | S 規模タスク: Edit + Test のみ |
| **信頼できる評価** | 成否判定が自動化・信頼可能 | unit test + lint が通れば完了 |
| **反復的デプロイ** | 同種タスクが繰り返し発生する | typo 修正、定型バグ修正 |

> 出典: Yue et al. 2026 "From Static Templates to Dynamic Runtime Graphs" §7.1

### Plasticity Spectrum（動的適応の度合い）

動的にする場合、**最小限の plasticity** を選ぶ:

```
select → generate → edit
(軽い)            (重い)
```

| レベル | いつ使う | dotfiles での実装 |
|--------|---------|------------------|
| **select** | タスクは似ているが難易度やツールが異なる | agent-router.py がタスク規模で reviewer 数を選択 |
| **generate** | タスク種類自体が異なり、異なる構造が必要 | `/autonomous` が DAG を生成し worktree 並列実行 |
| **edit** | 実行中に予期せぬ情報が現れ構造変更が必要 | hook がエラー時にルート変更（error-to-codex 等） |

**判断フロー**: タスク異質性が低い → select、異質性が高い → generate、実行中の対話性が高い → edit

### Harness Module Addition Gate（"More Structure ≠ Better"）

> 出典: Pan et al. 2026 "Natural-Language Agent Harnesses" RQ2 — SWE-bench で6モジュールを段階的に追加した結果、構造追加は単調な改善ではなく solved-set replacer として機能した。

ハーネスにモジュール（hook, agent, skill, reference）を追加する前に、以下の3点を確認する:

| チェック | 質問 | NG シグナル |
|---------|------|-----------|
| **ROI** | このモジュールの追加で、コスト増加に見合うスコア改善があるか？ | 行動は変わるがスコアは変わらない（プロセス装飾） |
| **受理整合** | ローカル検証の成功が最終受理と整合するか？ | 内部 verifier は PASS だが外部評価は FAIL（乖離リスク） |
| **境界ケース集中** | 効果は全体に均一か、少数の境界ケースに集中するか？ | 110/125 件は影響なし、15件だけ flip（効果の過大評価リスク） |

**判断**: 3点すべてクリアなら追加。1点でも NG なら、既存モジュールの強化を優先する。

> **Self-evolution が最高 ROI**: 同論文で唯一コスト右シフトなしでスコアを改善したモジュール。retry ループの規律化は新モジュール追加より先に検討すべき。

---

## 6段階プロセス（詳細）

すべての非自明なタスクは以下の6段階で進める:

### Plan 前の必須チェック

- **M/L タスク**: Plan 作成前に `/check-health` を実行し、関連ドキュメントの矛盾・陳腐化を検出する。矛盾情報は Plan に伝播し、下流の全実装を汚染する（OpenForage: "Pre-Task Contradiction Check"）
- **L タスク — 複数プラン生成（任意）**: 不確実性が高い場合、N=3 の異なるアプローチを列挙し、保守性・拡張性・シンプルさの 3 軸で比較して選択する。`/debate` を活用してもよい

### Plan 実行中の中間検証（L 規模）

L 規模タスクでは、Plan の **3 ステップ完了ごと** に計画突合チェックを行う:

1. 完了した実装が Plan のステップ定義と一致しているか確認
2. 逸脱がある場合は Decision Log に記録し、Plan を更新するか差し戻す
3. カスケード障害（A を作るべきところ A' を作り、下流が全て A' 前提になる）を早期に防止する

> Ref: OpenForage "Planning Deviations" — "verify early and often that the solution is implemented in accordance with your expectations"

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

> **スパン圧縮の理論** (Tu 2026): 線形チェーン (S=Theta(W)) を DAG 化すると S=Theta(log_k W) に圧縮され、
> 誤り複合が指数的に削減される (e^(-eta*W) -> e^(-eta*D))。Unit 分解は「並列化」だけでなく「信頼性スケーリング」の手段。
> 詳細: `references/structured-test-time-scaling.md` §1

### 反復 Build-QA パターン（長時間タスク向け）

> 出典: Anthropic "Harness Design for Long-Running Apps" (2026-03) — DAW 構築で 3 ラウンドの Build→QA で残存バグが収束

数時間規模の長時間タスクでは、Build → QA → Build → QA の反復ループで品質を収束させる。
`/epd` の Build→Review に相当するが、自動化された反復を前提とする。

```
Build Round 1 → QA Round 1（残存バグ一覧）
  → Build Round 2（バグ修正 + 未実装補完） → QA Round 2
  → Build Round 3（仕上げ） → QA Round 3（最終確認）
```

#### 適用条件

- タスク推定時間 > 2時間
- `/autonomous` スキルまたは Agent SDK での長時間実行
- QA は agent-browser CLI 等で実際の UI を操作して検証

#### QA ラウンドの注意

- FM-018 (Evaluator Rationalization) に注意: QA が問題を見つけた後に rationalize して承認しないよう、adversarial framing を適用
- 各ラウンドの QA 結果は構造化アーティファクト（ファイル）で次の Build に引き継ぐ

### タスクレベル Self-Evolution（M/L 規模向け）

> 出典: Pan et al. 2026 "Natural-Language Agent Harnesses" RQ2 — Self-evolution モジュールが6モジュール中最高の ROI (75.2→80.0, コスト右シフトなし)

タスクの solve ループ全体に規律的な retry を適用する。Review の NEEDS_FIX ループ（コードレビュー段階の retry）とは異なり、**Plan→Implement→Test の全体**を反省→軸変更→再試行する。

```
Attempt 1: 通常の Plan → Implement → Test
  ↓ 失敗 or 部分的成功
Reflect: 具体的な失敗シグナル（テスト出力、エラーログ）に基づいて反省
  ↓
Attempt 2: prompt / tool / workflow のいずれかの軸を変更して再試行
  - Attempt 1 の反省が Attempt 2 に明示的に反映されていること
  ↓ 失敗 or 部分的成功
Attempt 3: さらに軸を変更
  ↓
Cap 到達: 未完了として報告（最終 attempt が通ったふりをしない）
```

#### 適用条件

- **M/L 規模**のタスクで、最初の attempt が失敗または部分的に成功した場合
- **Cap**: デフォルト 3（コスト制約。論文は cap=5 だが実務では 3 で十分）
- **不適用**: S 規模（typo 修正等）、既に review retry ループ内にいる場合

#### 軸変更の例

| 軸 | Attempt 1 | Attempt 2 での変更 |
|---|---|---|
| **Prompt** | 仕様解釈を変える | エラーメッセージから仕様を再解釈 |
| **Tool** | 使うツール/ライブラリを変える | 別の API やアプローチを試す |
| **Workflow** | 分解粒度や実行順序を変える | 問題を小さな単位に分割して逐次解決 |

#### 反省テンプレート

```
## Attempt N 反省
- 失敗シグナル: {テスト出力 or エラーログの要点}
- 根本原因の仮説: {なぜ失敗したか}
- Attempt N+1 の軸変更: {prompt/tool/workflow のどれを、何から何に変えるか}
```

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
| **ステップの追加** | 依存関係をチェック → **エラー複合コスト評価**（`resource-bounds.md` §エージェント設計系）→ Plan に挿入 → ユーザーに確認 |
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

## Permission Progressive Trust（段階的信頼構築）

> 出典: Claude Code 内部 7段階 Permission Pipeline の設計思想。

新規ユーザーや新プロジェクトでは、以下の段階で信頼を構築する:

| 段階 | Permission Mode | 適用場面 | settings.json |
|------|----------------|---------|---------------|
| 1 | `default` | 初回利用。すべてのアクションを都度承認 | デフォルト |
| 2 | `acceptEdits` | ファイル編集は自動承認。Bash は都度確認 | `"permissions": {"allow": ["Edit", "Write"]}` |
| 3 | カスタム allow | 安全なコマンド（git, npm test 等）を自動承認 | `"permissions": {"allow": ["Bash(git *)", "Bash(npm test)"]}` |
| 4 | `bypassPermissions` | すべて自動承認。十分な信頼構築後のみ | 注意: deny rules は引き続き有効 |

**原則**: binary allow/deny ではなく spectrum。安全性と速度のバランスをユーザーが段階的に調整する。

### Trust Level マッピング（パーミッションモード選択ガイド）

タスクのリスクに応じて Claude Code のパーミッションモードを選択する。信頼レベルが高いほど自動化が進むが、リスクも上がる。

| Trust Level | パーミッションモード | 用途 | リスク |
|-------------|-------------------|------|--------|
| **L1: Read-only** | `plan` (`EnterPlanMode`) | コードベース調査、レビュー、プラン作成 | 最低 — 書き込み不可 |
| **L2: Supervised** | `default` | 通常の実装作業。全ツール呼び出しをユーザーが承認 | 低 — 人間がゲートキーパー |
| **L3: Semi-trusted** | `acceptEdits`（settings.json の `allowedTools` で制御） | 信頼済みリファクタ、テスト追加。ファイル編集は自動承認、シェルコマンドは承認必要 | 中 — 編集は自動、実行は手動 |
| **L4: Autonomous** | `bypassPermissions`（CI/自動化専用） | CI パイプライン、`/autonomous` スキル、バックグラウンドエージェント | 高 — 人間のゲートなし |

**選択の原則**: デフォルトは L2。L3 以上に上げるにはタスクが well-defined であること（仕様が明確、blast radius が限定的）。L4 は人間が直接セッションを監視しない自動化専用。

> 出典: "How to Vibe Code" (Mistral AI, 2026) — Agent modes matching trust to task

### Auto-Accept 判定

Plan 承認後の変更実行時は `references/auto-accept-policy.md` の判定マトリクスに従う:
- **Auto-Accept**: docs/tests のみ、単一ファイル、追加のみ → 確認なしで実行
- **Confirm**: 2ファイル超、scripts/hooks 変更 → ユーザー確認
- **Never**: settings.json, CLAUDE.md, セキュリティ、破壊的操作 → 常に確認必須

### 1.3. プロジェクト俯瞰 — M/L 規模のみ

大規模な変更では、コードを書く前にプロジェクトのアーキテクチャ的信念を構築する:

1. **config/registry ファイルを最優先で読む** — モジュール接続情報の源泉
2. **エントリポイント / オーケストレーターを特定** — データフローの全体像を把握
3. **発見した依存関係と不変条件を明示的にメモ** — コンテキスト圧縮時にも保持される

根拠: Theory of Code Space 論文 (arXiv:2603.00601) — config 優先戦略は Random の 3倍の効率。構造化マップの保持で依存関係理解が +14 F1 改善。

### 1.5. Codex Gate: Spec/Plan 批評 — M/L 規模のみ

Spec/Plan 作成後、実装前に Codex(gpt-5.4) で批評するゲート。
旧 Risk Analysis を統合し、Spec 批評 + Plan 批評 + リスク分析を1回の Gate で行う。

**設計思想**: Claude(Opus) の「注意の幅」（創造）と Codex の「注意の深さ」（批評）を分離する。

| タスク規模 | Spec/Plan Gate | reasoning_effort |
|---|---|---|
| **S** | skip | — |
| **M** | `codex-plan-reviewer` 起動 | xhigh |
| **L** | `codex-plan-reviewer` 起動 | xhigh |

**起動方法**:
- `codex-plan-reviewer` エージェントを dispatch する

**Gate フロー**:
1. Codex 実行（xhigh, read-only）
2. Claude が指摘を精査:
   - **修正すべき**と明確に判断できるもの → Claude が自動修正 → 修正内容をユーザーに報告 → 修正箇所のみ再レビュー
   - **迷う**もの（トレードオフ・複数の選択肢・確信なし）→ ユーザーに選択肢を提示 → ユーザーが判断
3. ユーザー承認で Implement に進む

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

### 4. Review（レビュー）— Review-Fix Cycle

`/review` スキルのワークフローに従う。スケーリング・言語検出・スペシャリスト選択・結果統合の詳細はスキル内の `skills/review/references/reviewer-routing.md` と `skills/review/templates/review-output.md` を参照。

#### リスクカテゴリ別レビュー方針

変更対象のリスクカテゴリ（「非対称損失の原則」参照）に応じてレビューの厳格度を調整する:

| リスク | レビュー方針 | 具体的な振る舞い |
|--------|------------|-----------------|
| **High** | 見逃し許容度ゼロ | security-reviewer 必須。edge-case-hunter 追加。NEEDS_FIX は全件対応 |
| **Medium** | バランス | 標準の reviewer 構成。NEEDS_FIX は確信度で判断 |
| **Low** | 過検出を減らす | 最小構成（code-reviewer のみ）。軽微な指摘は PASS 扱い可 |

リスクカテゴリの判定基準:
- **High**: セキュリティ関連、DB migration、本番設定、secrets、認証/認可
- **Medium**: ビジネスロジック、API 変更、hook/script、エージェント定義
- **Low**: ドキュメント、テスト、コメント、typo、設定のフォーマット変更

#### Codex Review Gate の修正判断

Codex Review Gate の指摘に対する修正判断は、重要度ラベルではなく Claude の確信度で決定する:

| 判断者 | 条件 | アクション |
|--------|------|-----------|
| Claude が自動修正 | 修正すべきと明確に判断できるもの（重要度問わず） | 修正 → 修正内容をユーザーに報告 → 修正箇所のみ再レビュー |
| ユーザーに判断を委ねる | トレードオフがある・方向性に複数の選択肢がある・確信が持てない | 選択肢を提示 → ユーザーが決定 |

#### Review-Fix サイクル

```
Review → verdict 判定
  ├─ PASS              → Verify に進む → タスク完了をユーザーに報告
  ├─ NEEDS_FIX         → 指摘を修正 → 修正差分のみ再 Review → verdict 再判定
  ├─ BLOCK             → 指摘を修正 → フル再 Review → verdict 再判定
  └─ NEEDS_HUMAN_REVIEW → ユーザーに判断を委ねる
```

| verdict | 再レビュー対象 | 最大サイクル |
|---------|---------------|-------------|
| PASS | なし | - |
| NEEDS_FIX | 修正差分のみ（修正行数で再スケーリング） | 3回 |
| BLOCK | 全変更（フルレビュー再実行） | 3回 |
| NEEDS_HUMAN_REVIEW | ユーザー判断 | - |

- 3回で PASS にならない場合はユーザーにエスカレーション
- 再レビューで新規指摘ゼロなら PASS に昇格
- `/codex-review` は手動で個別に使うスキル。自動レビューフローでは `/review` スキルの Agent 並列起動に統一する

### 5. Verify（検証）

- `verification-before-completion` スキルで完了前検証
- ビルド・テスト・lint を実際に実行し、出力を確認してから完了宣言
- 仮定に基づく「問題ありません」は禁止
- **Evidence-Backed Answering（M/L 規模推奨）**: 最終回答・パッチ・完了宣言の前に、根拠をまとめた standalone evidence を残す。evidence は Plan ファイルや Decision Log 内のセクションでよい。以下を含める:
  - 問題の観察事実（ログ、テスト出力）
  - 根本原因の特定根拠
  - 候補解の選定理由と棄却した代替案
  - 残存する不確実性
  > 出典: Pan et al. 2026 "Natural-Language Agent Harnesses" — evidence-backed answering はプロセス品質（監査性、ハンドオフ規律、トレース品質）を改善する

### 5.5. Pre-commit Security Self-check（M/L 規模）

Verify と Security Check の間に、AI 自身がコミット対象コードをセキュリティ観点で自己レビューする軽量ステップ。
専門の security-reviewer に委譲する前の一次フィルタとして機能する。

**自問チェックリスト**（変更した各ファイルに対して）:
1. ユーザー入力をサニタイズせずに使っていないか？（SQLi, XSS, コマンドインジェクション）
2. 秘密情報（API キー、トークン、パスワード）をハードコードしていないか？
3. 認証・認可チェックをバイパスするパスがないか？
4. AI が提案した依存パッケージが実在するか確認したか？（slopsquatting リスク）
5. エラーメッセージに内部情報（スタックトレース、DB スキーマ）を露出していないか？

問題を検出した場合は Implement に戻って修正する。問題なしの場合のみ Security Check に進む。

> 出典: "How to Vibe Code" (Mistral AI, 2026) — "After the agent generates code, prompt it to review its own output for security vulnerabilities before you do."

### 6. Security Check（セキュリティ）

- `/security-review` コマンドでセキュリティチェック
- security-reviewer エージェントに OWASP Top 10 ベースの分析を委譲
- Critical/High の指摘は必ず修正してからコミット

```
Plan -> Codex Spec/Plan Gate -> Edge Case Analysis(M/L) -> Implement -> Test -> Codex Review Gate -> Verify -> Security Check -> Commit

失敗時のループ:
- Spec/Plan Gate で指摘 → Claude が修正 or ユーザー判断 → 修正箇所のみ再レビュー
- テスト失敗             → Implement に戻る
- レビュー NEEDS_FIX     → 修正 → 修正差分のみ再 Review（最大3回）
- レビュー BLOCK         → 修正 → フル再 Review（最大3回）
- 検証失敗               → Implement に戻る
- セキュリティ指摘       → Implement に戻る
```

---

## タスク規模による段階スケーリング

全タスクで6段階を律儀に踏む必要はない。規模に応じてスケールする:

| 規模            | 例                                | 必須段階                         | スキップ可能                           |
| --------------- | --------------------------------- | -------------------------------- | -------------------------------------- |
| **S（軽微）**   | typo修正、1行変更、設定値変更     | Implement → Codex Review Gate → Verify                              | Spec Review, Plan, Spec/Plan Gate, Test, Security |
| **M（標準）**   | 関数追加、バグ修正、小機能        | Spec Review → Plan → Codex Spec/Plan Gate → Edge Case Analysis → Implement → Test → Codex Review Gate → Verify | 4並列レビューは1-2エージェントに縮小可           |
| **L（大規模）** | 新機能、リファクタリング、API設計 | Spec Review → Checkpoint → Plan → Codex Spec/Plan Gate → Edge Case Analysis → 全段階（Codex Review Gate 含む） | なし                                             |

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
| Codex Spec/Plan Gate     | `codex-plan-reviewer`        | Spec/Plan 批評 + リスク分析を1回で行う実装前ゲート     |
| Codex レビュー           | `codex-reviewer`             | Codex による深い推論レビュー（並列起動）                |
| Codex デバッグ           | `codex-debugger`             | Codex による深いエラー分析・根本原因特定                |
| ドキュメントメンテナンス | `doc-gardener`               | 陳腐化ドキュメント検出・修正                            |
| コード品質スキャン       | `golden-cleanup`             | ゴールデンプリンシプル逸脱スキャン                      |
| UI 観察                  | `ui-observer`                | agent-browser による UI 状態確認（サブエージェント限定）   |
| 並列リサーチ             | `/research` スキル           | マルチエージェント並列調査、レポート生成                |
| 自律実行                 | `/autonomous` スキル         | 長時間タスクのセッション跨ぎ自律実行                    |
| ブレイクスルー記録       | `/eureka` スキル             | 技術的発見の構造化記録、INDEX 管理                      |
| Cursor Agent             | `/cursor` スキル             | マルチモデル比較、Cloud Agent 非同期タスク              |

### ハンドオフフォーマット

エージェント間でタスクを引き継ぐ際、以下の情報を spawn prompt や SendMessage に構造化して含める。
暗黙の前提に依存せず、受け手が自己完結的に作業できる粒度で渡す。

```markdown
## Handoff Packet
- **Goal**: 何を達成すべきか（1文）
- **Context**: 前工程で判明した事実・制約（箇条書き）
- **Artifacts**: 参照すべきファイルパス・diff・ログ
- **Acceptance Criteria**: 完了の判定基準
- **Not in Scope**: 明示的にやらないこと
```

> 出典: Multi-Agent Autoresearch Lab — ロール間通信テンプレートを AGENTS.md に定義し、引き継ぎプロトコルを明示

### ルーティングルール

1. レビューは `/review` スキルに委譲（スケーリング・言語検出・スペシャリスト選択を自動実行）
2. 開発系エージェント（golang-pro, typescript-pro）はレビューアーとは別の役割
3. セキュリティが関わるコード変更は、通常レビューに加えて `security-reviewer` を追加
4. アーキテクチャ判断はアーキテクト系エージェントに委譲
5. 大規模コードベース分析・外部リサーチ・マルチモーダル処理は `gemini-explore` に委譲
6. 通常の `debugger` で困難なエラー分析は `codex-debugger` に委譲（Codex の深い推論を活用）
7. ドキュメントの陳腐化が疑われる場合は `doc-gardener` に委譲
8. コード品質の網羅的スキャンは `golden-cleanup` に委譲
9. UI の状態確認・バグ再現は `ui-observer` に委譲（agent-browser をサブエージェント内に閉じ込め、メインコンテキストを保護）
10. マルチモデル比較や Cloud Agent（非同期長時間タスク）は `/cursor` スキルに委譲
11. **Agent Creation Heuristic (G5)** — デバッグが膠着したら、専門エージェントを作成して再起動する方が速い

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

#### Agent = Context Control Primitive

エージェントは「委譲プリミティブ」ではなく「コンテキスト制御プリミティブ」。何を別エージェントに切るかは**タスクサイズ**ではなく**コンテキストノイズ**で判断する。

| 状況 | 判断 | 理由 |
|------|------|------|
| リサーチが編集対象ファイルを探索済み | **Continue** (SendMessage) | コンテキストに必要ファイルが既にある |
| リサーチは広範だが実装は狭い | **Spawn fresh** | 探索ノイズを持ち込まない |
| 失敗の修正・直近作業の延長 | **Continue** | エラーコンテキストがある |
| 別 worker が書いたコードの検証 | **Spawn fresh** | 実装の仮定を引き継がない |
| 最初のアプローチが完全に間違い | **Spawn fresh** | 失敗パスへのアンカリング回避 |

Worker プロンプトの鉄則:
- 「Based on your findings」「Based on the research」は禁止 — リサーチ結果を自分で合成してから具体スペック（パス+行番号+型）を渡す
- Worker は親の会話が見えない — すべてのプロンプトは自己完結

#### Agent Teams（協調タスク向け）

エージェント間で中間発見を共有し、動的に調整が必要な場合に使用。

| 判断 | サブエージェント | Agent Teams |
|---|---|---|
| 作業が embarrassingly parallel | ✅ | |
| 発見を他エージェントに即共有したい | | ✅ |
| 依存関係が動的に変化する | | ✅ |

#### Skill ↔ Subagent 合成パターン

Skills と Subagents は相互参照可能。方向によって用途が異なる。

| パターン | 仕組み | 使い所 |
|----------|--------|--------|
| **Agent → Skills** (`skills:` frontmatter) | エージェント起動時にスキル内容をコンテキストに注入 | ロール定義: 常に同じドメイン知識が必要なエージェント |
| **Skill → Agent** (`context: fork` + `agent:`) | スキル内容をサブエージェントのタスクプロンプトとして隔離実行 | タスク隔離: 冗長な出力でメインコンテキストを汚染させたくないとき |

**判断基準**:
- **ロールを定義する** → Agent に `skills:` を付与（例: `debugger` に `systematic-debugging`）
- **タスクを隔離する** → Skill に `context: fork` を設定（例: `prompt-review`）
- **新規作成** → まずエージェントファイルを作る。`context: fork` は既存スキルを隔離実行したいときの後付けオプション

**注意**: `context: fork` はタスク指示を含むスキルでのみ有効。ガイドライン系スキルを fork してもサブエージェントに actionable なプロンプトが渡らず空振りする。

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
- **Retrieval Budget**: メモリ/参照の検索は取得数 3 件前後が最適。取得数が閾値を超えると注意が分散し性能が低下する（非単調パターン）。根拠: MemCollab (arXiv:2603.23234) — p=3 で全ベンチマーク最高性能、p>5 で一貫して低下。セッション中に大量の memory/reference を読み込む場合は、タスクカテゴリに最も関連する 3 件に絞ること

### Plan と checkpoint の関係

- checkpoint は session 再開用の runtime state
- plan は goal、scope、validation、decision を残す作業記録
- 長時間タスクでは両方を使う
- checkpoint だけで plan を代用しない

---

## Effort Level 使い分け

| effort | 用途 | コスト影響 |
|--------|------|-----------|
| **medium** | 単純な修正、定型タスク、read-only 調査 | thinking トークン節約 |
| **high** | 通常の開発作業（デフォルト） | 標準 |
| **max** | 高リスク判断、セキュリティレビュー、複雑なアーキテクチャ設計、デバッグの最終手段 | thinking トークン大量消費 |

- グローバル設定は `"effortLevel": "high"`。スキル/エージェント単位で `effort` frontmatter でオーバーライド可能
- "max" は Opus 4.6 専用。Sonnet では効果が限定的
- 1日の "max" 使用は 3-5 回を目安に。コスト: thinking トークンが output 単価 ($25/M for Opus) で課金される

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
- `python3 scripts/runtime/token-audit.py` でファイル別トークン消費量を分析し、犯人を特定できる

### セッション分離

- **1セッション1タスク**を原則とする。無関係なタスクを同じセッションで混ぜない
- 異なるタスクの文脈が混ざると、autocompact 後も前タスクの仮定が残留し、後半の品質が下がる
- タスク完了後は `/compact` または新セッションで切り替える
- 例外: 密接に関連するタスク（同一機能のフロント + バック等）は同一セッションでOK

### Context Management Ladder

コンテキスト圧力に応じた段階的対応。Anthropic の知見: Sonnet 4.5 はコンテキスト限界接近で早期終了行動を示す。**Compaction よりも Clean Session が安定**。

| Pressure | Action |
|----------|--------|
| 80% | Subagent 委譲を検討。新規の大きな Read/Grep を避ける |
| 90% | Compaction 実行。不要なツール出力を手動削除 |
| 95%+ | New Session 推奨。checkpoint を保存してから切り替え |
| Compaction 3回後 | Session 切り替え必須。これ以上の Compaction は品質劣化を招く |

Compaction は最大3回/セッションを上限とする。Reset > Compaction が原則。

### Loop Monitoring（Build-QA ラウンド監視）

Build-QA ラウンドを反復する際、以下のメトリクスを各ラウンド終了時に確認する:

- **テスト通過率**: 単調増加すべき。前ラウンド比で低下したら approach 再考
- **Lint 警告数**: 単調減少すべき。増加は regression のシグナル
- **ビルド時間**: 前ラウンド比 2x 超は異常。不要な依存追加の疑い
- **編集回数/ラウンド**: 完了に近づくにつれ減少すべき。増加は doom loop の兆候

2ラウンド連続で改善が見られない場合 → approach 変更 or 新セッションに切り替え。
Morris の On the loop モデル: 結果が不満なら成果物ではなく**ハーネスを修正**する。

### Escalation Ladder（違反蓄積と自動昇格）

同一カテゴリの警告が蓄積した場合、対応レベルを自動昇格する:

| 出現回数 | レベル | 対応 |
|---------|--------|------|
| 1回 | L1: Document | CLAUDE.md/rules に明記 |
| 2回 | L2: AI Check | hook/skill で自動検出 |
| 3回 | L3: Tool Enforce | リンター/CI で機械的ブロック |
| 4回+ | L4: Structure Test | アーキテクチャテストで構造的に不可能に |

nogataka「3回ルール」: 同一違反が3セッションで再発したら、次レベルへの昇格を検討。

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

---

## Correctness Oracle（機能正確性の統合判定）

> Qoder: E2E/QA/Review が個別に存在するだけでは不十分。統合 oracle が必要。

### 3層検証モデル

| 層 | 検証内容 | ツール | 判定 |
|---|---|---|---|
| **Static** | lint + type check | 言語固有ツール（`tsc`, `go vet` 等） | PASS/FAIL |
| **Dynamic** | unit test + E2E | `/autocover`, `webapp-testing` | PASS/FAIL |
| **Semantic** | code review + product validation | `/review`, `/validate` | PASS/NEEDS_FIX/BLOCK |

### 統合判定基準

| Static | Dynamic | Semantic | Overall |
|---|---|---|---|
| PASS | PASS | PASS | PASS — タスク完了 |
| FAIL | any | any | FAIL — Static 修正が最優先 |
| PASS | FAIL | any | FAIL — テスト修正 |
| PASS | PASS | NEEDS_FIX | NEEDS_FIX — レビュー指摘対応 |
| PASS | PASS | BLOCK | BLOCK — 設計変更が必要 |

### 既存スキルとのマッピング

新規スクリプトは不要。既存スキルの組み合わせで統合判定を実現する:

- **Static**: `completion-gate.py` が lint/type check を自動実行
- **Dynamic**: `/autocover` がカバレッジ分析 + テスト生成、`webapp-testing` が E2E
- **Semantic**: `/review` が並列レビュー、`/validate` が仕様整合性

ワークフローの Verify 段階で、3層すべてが PASS であることを確認してからタスク完了とする。

---

## Visibility → Trust → Autonomy（可視性の設計原則）

> 出典: Claude Code の terminal UI 設計思想。

エージェントの作業を可視化することで信頼が生まれ、信頼が自律性を拡大する:

```
可視性 → 信頼 → 自律性 → 有用な作業
```

statusline はこの原則の実装:
- **コンテキスト使用率**: ユーザーがトークン化を理解せずとも残容量を直感的に把握
- **モデル名・コスト**: 透明性がコスト意識を育てる
- **references/memory/skill 数**: 何がロードされているかの可視化

可視性が不十分だとユーザーは慎重になり、許可を絞り、エージェントの有用性が下がる悪循環に入る。
