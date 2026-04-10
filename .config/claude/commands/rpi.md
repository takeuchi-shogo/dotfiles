---
name: rpi
description: "Research → Plan → Implement の3フェーズで体系的にタスクを実行する"
allowed-tools: Agent, Read, Write, Edit, Bash, Glob, Grep, EnterPlanMode, ExitPlanMode, TaskCreate, TaskUpdate, TaskList, WebSearch, WebFetch
user-invocable: true
---

# RPI ワークフロー: Research → Plan → Implement

以下のタスクを RPI ワークフローで実行してください:

**タスク**: $ARGUMENTS

---

## Phase 1: Research (調査)

5つのステップで構造的に調査する。詳細チェックリストは `references/research-checklist.md` を参照。

### Must Contract (毎回照合)

- [ ] 意図が曖昧なら Step 1 で質問した（implement に入る前）
- [ ] タスク規模を S/M/L で宣言した（workflow-guide.md 参照）
- [ ] 既存コード内の類似実装を Grep/Glob で最低 1 回検索した（search-first 原則）
- [ ] 影響範囲ファイルのうち変更対象を Read した

### Important (Standard 深度以上で照合)

- [ ] 既存テストと命名規約を確認した
- [ ] 依存関係の import chain を辿った
- [ ] ギャップ・矛盾チェック（Step 4）を実施した

### Step 1: 意図の明確化

タスクの意図が曖昧なら、実装に入る前に質問する。
→ `rules/common/overconfidence-prevention.md` の原則に従う。
→ 調査深度に応じて追加ルールの適用を判定する（`references/research-checklist.md` Step 2.5）。

### Step 2: 深度決定

タスク規模（S/M/L）を判定し、調査深度を決める。
→ `references/workflow-guide.md` の多因子タスク規模判定・深度レベル表を参照。

| 深度 | 調査範囲 |
|---|---|
| **Minimal** (S) | 対象ファイルのみ確認。Step 3-4 は軽量に |
| **Standard** (M) | モジュール単位で調査。Step 3-4 を実施 |
| **Comprehensive** (L) | Brownfield 分析テンプレートを使用。Step 3-4 を網羅的に実施 |

### Step 3: コードベース調査

Explore エージェントで関連ファイル・パターン・依存関係を特定する。

- 関連ファイルと変更対象の特定
- 既存パターン・類似実装の確認
- 依存関係と影響範囲の把握
- **L 規模**: `references/brownfield-analysis-template.md` に従って体系的に分析

### Step 4: ギャップ・矛盾チェック

要件の欠落や既存コードとの矛盾がないか検証する。

- 要件で言及されていないエッジケースの特定
- 既存の規約・パターンとの矛盾確認
- 技術的制約（互換性、パフォーマンス）の洗い出し
- 矛盾を発見した場合 → ユーザーに確認してから Plan フェーズへ

### Step 5: 調査サマリー

調査結果を構造化してユーザーに共有する。深度に応じたフォーマットは `references/research-checklist.md` を参照。

## Phase 2: Plan (計画)

EnterPlanMode を使って実装計画を立てる:

1. 調査結果に基づいて具体的な実装ステップを設計
2. 変更対象ファイルと影響範囲を明示
3. リスクや代替案がある場合は提示
4. ユーザーの承認を得てから次のフェーズへ

### Must Contract (毎回照合)

- [ ] 変更対象ファイルのパスを全て列挙した
- [ ] 影響範囲（他ファイルへの波及）を明示した
- [ ] M/L 規模なら撤退条件を 1 つ以上定義した（reversible-decisions.md 参照）
- [ ] ユーザー承認を得た

### Important

- [ ] 代替案を 1 つ以上検討した
- [ ] エッジケース・異常系パスを 1 つ以上列挙した
- [ ] テスト戦略を記述した

## Phase 3: Implement (実装)

承認された計画に基づいて実装する:

1. 計画のステップに従ってコードを実装
2. テストを実行して動作を確認
3. 変更規模に応じたコードレビューを実施（CLAUDE.md のレビュースケーリングに従う）
4. 検証が完了したらユーザーに報告

### Must Contract (毎回照合)

- [ ] 計画のステップ順に実装した（逸脱時は即報告）
- [ ] 1 ファイル編集につき関連ファイルを最低 1 つ Read してから書いた
- [ ] `task validate-configs` または該当 lint/test を最低 1 回実行した
- [ ] verification-before-completion に従い、完了宣言前に検証コマンドを実行した

### Important

- [ ] テストを追加/更新した
- [ ] 変更規模に応じて /review スキルを起動した
- [ ] エラーメッセージは生データで分析した（要約しない）

---

## 重要な原則

- **各フェーズをスキップしない**: 簡単に見えるタスクでも、Research で予期しない制約が見つかることがある
- **調査と計画の分離**: Research は事実収集、Plan は意思決定。混ぜない
- **計画承認後に実装**: ユーザーの承認なしに実装を開始しない
- **search-first**: 既存の解決策やライブラリがないか必ず確認する
