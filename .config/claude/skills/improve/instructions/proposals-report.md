# Proposals & Report (Step 6-7)

## Step 6: カテゴリ別改善提案の生成

Step 4 の分析結果で **改善機会** が見つかったカテゴリに対して、
**Agent ツールで `autoevolve-core` (phase: improve) エージェントを起動** する。

各カテゴリに対して:

```
以下のカテゴリの改善を実施してください:

カテゴリ: {カテゴリ名}
分析結果: {Step 4 の該当カテゴリの分析サマリー}
クロス分析: {Step 5 のクロスカテゴリ相関で関連する知見}

improve-policy.md の方針に従い、autoevolve/* ブランチで変更を実装してください。
```

**注意**:
- 改善機会がないカテゴリは起動しない
- 複数カテゴリに改善機会がある場合は、優先度の高いものから順に起動する
- 1 サイクルで最大 3 ファイルの変更制約を守る（autoevolve-core エージェントの制約）

**スキルカテゴリの検証ゲート（EvoSkill 統合）:**

1. `autoevolve-core (phase: improve)` がブランチで修正を実装
2. 修正結果を `skill_amender.gate_proposal()` で判定（A/B テスト結果がある場合）
3. `experiment_tracker.py record` に `--proposal-type`, `--target-skill` を含めて記録
4. verdict が `pending_review` の場合、Step 7 のレポートに「要レビュー」として表示

## Step 7: レビューレポートの生成

全ステップの結果を統合し、以下のフォーマットでユーザーに報告する:

```markdown
# AutoEvolve 改善サイクル レポート

## データ概況

- エラー: N 件
- 品質違反: N 件
- パターン: N 件
- セッション: N 件

## 実験ステータス

- 進行中: N 件
- 効果測定済み: N 件（成功: N / 改善なし: N）

## 前回 Issue 実施率

| Issue | タイトル | 状態 |
|-------|---------|------|
| #{number} | {title} | {OPEN/CLOSED} |

**実施率: N/M (X%)**

## 分析結果サマリー

### エラーパターン

- {主要な発見}

### 品質違反パターン

- {主要な発見}

### エージェント効率

- {主要な発見}

### スキル改善

- {主要な発見}

### クロスカテゴリ相関

- {カテゴリ間の関連性}

## 知識ベースの健全性

- learnings サイズ: OK / 警告
- insights 数: N 件
- MEMORY.md: N 行 / 200行制限
- 昇格候補: N 件

## 改善提案

### 実施済み（ブランチ作成済み）

- `autoevolve/YYYY-MM-DD-{topic}`: {変更内容}
  - 根拠: {データに基づく理由}
  - 次のアクション: `git merge` or レビュー

### 昇格候補（ユーザー承認待ち）

- [ ] {MEMORY.md への追記提案}
- [ ] {スキル/ルール化の提案}

### Evidence Chain サマリー

| 提案 ID | confidence | data_points | reasoning |
|---|---|---|---|
| {exp_id} | {0.X} | {N} | {reasoning の要約} |

> confidence < 0.5 の提案は **[低信頼度]** フラグ付きで表示する。
> これらの提案はデータ不足のため、追加データ収集を優先すべき。

### Validation Gate Results

| 提案 ID | 対象スキル | Gate 判定 | A/B delta | 理由 |
|---|---|---|---|---|
| {exp_id} | {skill} | {verdict} | {delta} | {reason} |

- `auto_accept`: 低影響ファイルのみ自動採用済み
- `auto_reject`: 自動却下済み（ブランチ削除推奨）
- `pending_review`: 人間レビュー待ち（ブランチ: `autoevolve/...`）

## 次回への申し送り

- {次回の /improve で優先すべき事項}
```
