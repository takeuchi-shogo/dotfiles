# SkillNet 5D 評価・関係グラフ統合 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** SkillNet の 5 次元スキル評価と 4 種関係タイプを既存の skill-audit, skill-creator, skill-inventory.md に統合する

**Architecture:** 新規ファイルは作成しない。既存 3 ファイル（skill-inventory.md, skill-audit/SKILL.md, skill-creator/SKILL.md）のドキュメント拡張のみ。テストは変更後の grep/目視確認で検証。

**Tech Stack:** Markdown（SKILL.md frontmatter + テーブル + チェックリスト）

**Spec:** `docs/superpowers/specs/2026-03-18-skillnet-5d-evaluation-integration-design.md`

---

## File Map

| ファイル | 責務 | 変更内容 |
|---------|------|---------|
| `.config/claude/references/skill-inventory.md` | スキル分類・関係定義 | 関係テーブル拡充、arXiv 更新、ガイダンス更新 |
| `.config/claude/skills/skill-audit/SKILL.md` | スキル品質監査ワークフロー | Step 0: 5D Quality Scan 追加、audit report テンプレート拡張 |
| `.config/claude/skills/skill-creator/SKILL.md` | スキル作成パイプライン | 5D Quality Check セクション追加、arXiv 更新 |

---

## Task 1: skill-inventory.md — 関係テーブル拡充

**Files:**
- Modify: `.config/claude/references/skill-inventory.md:81-114`

### Step 1: arXiv 参照更新

- [ ] **Step 1.1: arXiv 番号を更新**

`.config/claude/references/skill-inventory.md` line 83 を変更:

```diff
-スキル間の形式的関係。arXiv:2603.11808 SkillNet ontology に基づく。
+スキル間の形式的関係。[arXiv:2603.04448](https://arxiv.org/abs/2603.04448) SkillNet ontology に基づく。
```

### Step 2: 既存テーブルのリネーム

- [ ] **Step 2.1: `depends-on` → `depend_on` にリネーム**

ヘッダーのみ変更。テーブル内容はそのまま:

```diff
-### depends-on
+### depend_on
```

- [ ] **Step 2.2: `conflicts-with` → `conflicts_with` にリネーム**

```diff
-### conflicts-with
+### conflicts_with
```

- [ ] **Step 2.3: `is-a-subset-of` → `belong_to` にリネーム**

```diff
-### is-a-subset-of
-
-| Subset | Superset | 備考 |
+### belong_to
+
+| Child | Parent | 備考 |
```

### Step 3: 新規テーブル追加

- [ ] **Step 3.1: `similar_to` テーブルを `conflicts_with` の後に追加**

```markdown
### similar_to

機能的に等価で置換可能。同時使用は可能だが冗長。

| Skill A | Skill B | 理由 |
|---------|---------|------|
| codex-review | review | どちらもコードレビュー。100行超では codex-review を先行 |
| senior-frontend | react-best-practices | React 最適化は両方カバー。深度が異なる |
```

- [ ] **Step 3.2: `compose_with` テーブルを `similar_to` の後に追加**

```markdown
### compose_with

独立だが頻繁に連携。出力→入力の関係。

| Source | Target | 理由 |
|--------|--------|------|
| spec | spike | spec で仕様定義 → spike で実験実装 |
| research | absorb | research で調査 → absorb で統合 |
| skill-creator | skill-audit | 作成後に品質監査 |
```

### Step 4: ガイダンスセクション更新

- [ ] **Step 4.1: 既存ガイダンスを更新し、新関係タイプを追加**

既存の「ガイダンス追記」セクション（line 109-113）を以下に置換:

```markdown
### ガイダンス

- **`conflicts_with`** 関係にあるスキルを同時に有効にしない
- **`depend_on`** 関係がある場合、upstream スキルを先に実行する
- **`belong_to`** 関係にある場合、parent の方を優先検討する
- **`similar_to`** 関係にあるスキルは、ユースケースに応じて使い分ける（同時使用は可能だが冗長）
- **`compose_with`** 関係にあるスキルは、連鎖実行を検討する
- **`similar_to` と `conflicts_with` の違い**: similar は同時使用可能だが冗長、conflicts は同時有効化が禁止（設計指針が矛盾）
```

### Step 5: 検証・コミット

- [ ] **Step 5.1: 検証**

Run: `grep -c '### depend_on\|### conflicts_with\|### belong_to\|### similar_to\|### compose_with' .config/claude/references/skill-inventory.md`
Expected: `5`

Run: `grep '2603.04448' .config/claude/references/skill-inventory.md`
Expected: 1 行ヒット

Run: `grep '2603.11808' .config/claude/references/skill-inventory.md`
Expected: 0 行（旧参照が残っていないこと）

- [ ] **Step 5.2: コミット**

```bash
git add .config/claude/references/skill-inventory.md
git commit -m "📝 docs(skills): update skill-inventory with SkillNet 5-relation types (arXiv:2603.04448)"
```

---

## Task 2: skill-audit — 5D Quality Scan 追加

**Files:**
- Modify: `.config/claude/skills/skill-audit/SKILL.md`

### Step 1: Step 0 セクションを挿入

- [ ] **Step 1.1: Workflow セクションの Step 1 の前に Step 0 を追加**

`## Workflow` の `Execute the following steps in order:` の直後、`### Step 1: Select target skills` の直前に以下を挿入:

```markdown
### Step 0: 5D Quality Scan

A/B ベンチマーク（重い）を回す前に、対象スキルの SKILL.md を 5 次元で静的スクリーニングする。

#### 手順

1. 対象スキルの SKILL.md + references/ + scripts/ を読む
2. 以下の 5 次元それぞれを Good/Average/Poor で判定する
3. いずれかが Poor → audit report の「Improve」セクションに `(5D)` 注記付きで分類
4. 結果を audit report Summary テーブルの 5D 列に記録

#### 5 次元の定義（SkillNet arXiv:2603.04448 prompts.py 準拠）

| 次元 | Good | Average | Poor |
|------|------|---------|------|
| **Safety** | 破壊的操作をデフォルト回避、安全チェック含む、スコープ制限明示 | 良性ドメインだがリスク操作のセーフガード言及なし | 危険なアクション(delete/reset等)をガードなしで言及 |
| **Completeness** | 目標+手順+入出力が明確、前提条件を記載 | 目標は明確だが手順/前提/出力が不十分 | 曖昧すぎて行動不能、核心的手順欠如 |
| **Executability** | 具体的アクション/コマンド/パラメータ。指示のみスキルは明確ガイダンスで OK | 概ね実行可能だが曖昧ステップあり | 実行不能な曖昧指示 |
| **Maintainability** | 狭いスコープ、モジュール性、明確な入出力、低結合 | 再利用部分はあるが境界が不明確 | スコープ広すぎ or 密結合 |
| **Cost-awareness** | 軽量タスクは低コスト。重量タスクはバッチ/制限/キャッシュを明示 | コスト制御なしだが無駄もない | 無駄なワークフローを限度なく推奨 |

#### 追加ルール

- `allowed_tools` が必要以上に広い場合 → Safety を 1 レベル下げ
- コア式/アルゴリズムの致命的エラー → Completeness を最大 Average（通常 Poor）
- トリビアルなスクリプト（echo のみ等）→ Executability を最大 Average
```

### Step 2: audit report テンプレートを更新

- [ ] **Step 2.1: Audit Report Format セクションの Summary テーブルを拡張**

既存テーブル（line 162-165 付近）:

```diff
-| Skill   | Quality (with) | Quality (baseline) | Delta | Recommendation |
-| ------- | -------------- | ------------------ | ----- | -------------- |
-| skill-a | 7.5            | 6.0                | +1.5  | Keep           |
-| skill-b | 5.0            | 5.5                | -0.5  | Retire         |
+| Skill   | Safety | Comp. | Exec. | Maint. | Cost | Quality (with) | Quality (baseline) | Delta | Recommendation |
+| ------- | ------ | ----- | ----- | ------ | ---- | -------------- | ------------------ | ----- | -------------- |
+| skill-a | Good   | Good  | Avg   | Good   | Good | 7.5            | 6.0                | +1.5  | Keep           |
+| skill-b | Avg    | Poor  | Good  | Avg    | Good | —              | —                  | —     | Improve (5D)   |
```

### Step 3: Step 0 と A/B の優先順位ルールを追加

- [ ] **Step 3.1: audit report テンプレートの直後に判定ルールを追加**

```markdown
#### 5D と A/B の判定ルール

5D 結果は A/B ベンチマーク結果を上書きしない。独立した判断軸として並記する:
- 5D で Poor あり → Recommendation に `(5D)` 注記を付与し「Improve」以上に分類
- A/B Delta が Keep でも 5D Poor があれば `Keep (5D: Improve)` と表記
- 5D のみ実行した場合（A/B 省略）: Quality/Delta 列は `—` とし、5D 結果のみで判断
- 最終判断は人間が両方を見て決定する
```

### Step 4: 検証・コミット

- [ ] **Step 4.1: 検証**

Run: `grep -c 'Step 0' .config/claude/skills/skill-audit/SKILL.md`
Expected: `1` 以上

Run: `grep 'Safety.*Comp.*Exec.*Maint.*Cost.*Quality' .config/claude/skills/skill-audit/SKILL.md`
Expected: 1 行ヒット（拡張テーブルヘッダー）

Run: `grep 'Step 1: Select target skills' .config/claude/skills/skill-audit/SKILL.md`
Expected: ヒット（既存ステップが破壊されていないこと）

- [ ] **Step 4.2: コミット**

```bash
git add .config/claude/skills/skill-audit/SKILL.md
git commit -m "✨ feat(skill-audit): add Step 0 5D Quality Scan based on SkillNet (arXiv:2603.04448)"
```

---

## Task 3: skill-creator — 5D Quality Check 追加

**Files:**
- Modify: `.config/claude/skills/skill-creator/SKILL.md`

### Step 1: arXiv 参照更新

- [ ] **Step 1.1: Quality Gate セクションの arXiv 参照を更新**

line 77 付近:

```diff
-Reference: arXiv:2603.11808 Extraction Quality Criteria
+Reference: arXiv:2603.04448 SkillNet Extraction Quality Criteria
```

### Step 2: 5D Quality Check セクション追加

- [ ] **Step 2.1: Security Scan セクション（line 136）の直前に 5D Quality Check を挿入**

`### Security Scan` の直前に以下を追加:

```markdown
### 5D Quality Check

SKILL.md 初稿を SkillNet の 5 次元で確認する（[arXiv:2603.04448](https://arxiv.org/abs/2603.04448)）。
いずれかが Poor の場合、修正してから Security Scan に進む。Average は注記のみ。

1. **Safety**: 破壊的操作にガードがあるか？allowed_tools が必要最小限か？
2. **Completeness**: 前提条件・入出力・失敗モードが明示されているか？
3. **Executability**: 手順が具体的か？指示のみスキルの場合、ガイダンスが明確か？
4. **Maintainability**: スコープが狭く、モジュール性があり、他スキルと低結合か？
5. **Cost-awareness**: トークン効率を意識しているか？無駄なループや大量読み込みがないか？

詳細な Good/Average/Poor の境界条件は `skill-audit` の Step 0: 5D Quality Scan を参照。
```

### Step 3: Security Scan セクションの arXiv 参照も更新

- [ ] **Step 3.1: Security Scan セクション内の arXiv 参照を更新**

line 151 付近:

```diff
-Reference: arXiv:2603.11808 Four-Stage Verification Pipeline (G1-G4)
+Reference: arXiv:2603.04448 Four-Stage Verification Pipeline (G1-G4)
```

### Step 4: 検証・コミット

- [ ] **Step 4.1: 検証**

Run: `grep '5D Quality Check' .config/claude/skills/skill-creator/SKILL.md`
Expected: 1 行ヒット

Run: `grep -n 'Security Scan\|5D Quality Check' .config/claude/skills/skill-creator/SKILL.md`
Expected: 5D Quality Check の行番号 < Security Scan の行番号

Run: `grep '2603.11808' .config/claude/skills/skill-creator/SKILL.md`
Expected: 0 行（旧参照が残っていないこと）

- [ ] **Step 4.2: コミット**

```bash
git add .config/claude/skills/skill-creator/SKILL.md
git commit -m "✨ feat(skill-creator): add 5D Quality Check gate based on SkillNet (arXiv:2603.04448)"
```

---

## Task 4: 最終検証

- [ ] **Step 1: AC 全項目チェック**

| AC | 検証コマンド | 期待値 |
|----|-------------|--------|
| AC-1 | `grep -c '### depend_on\|### conflicts_with\|### belong_to\|### similar_to\|### compose_with' .config/claude/references/skill-inventory.md` | `5` |
| AC-1 | `grep '2603.04448' .config/claude/references/skill-inventory.md` | ヒット |
| AC-2 | `grep 'Step 0' .config/claude/skills/skill-audit/SKILL.md` | ヒット |
| AC-3 | `grep '5D Quality Check' .config/claude/skills/skill-creator/SKILL.md` | ヒット |
| AC-5 | `grep 'Step 1: Select target skills' .config/claude/skills/skill-audit/SKILL.md` | ヒット |
| AC-5 | `grep 'Quality Gate' .config/claude/skills/skill-creator/SKILL.md` | ヒット |
| AC-6 | `grep 'Safety.*Comp.*Exec.*Maint.*Cost.*Quality' .config/claude/skills/skill-audit/SKILL.md` | ヒット |
| AC-7 | `grep '2603.11808' .config/claude/skills/skill-creator/SKILL.md` | 0 行 |
| AC-8 | `grep 'depend_on\|belong_to' .config/claude/references/skill-inventory.md` | 複数ヒット |

- [ ] **Step 2: symlink 検証**

Run: `cd /Users/takeuchishougo/dotfiles && task validate-symlinks 2>/dev/null || echo "SKIP: Taskfile not available"`
