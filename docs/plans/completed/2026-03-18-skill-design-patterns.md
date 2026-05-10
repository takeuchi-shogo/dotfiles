---
status: active
last_reviewed: 2026-04-23
---

# Skill Design Patterns Integration — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** スキルシステムに 5 設計パターン分類を導入し、新スキル品質向上と既存スキル可視化を実現する

**Architecture:** `references/skill-patterns.md` を single source of truth とし、skill-creator が参照する Reference-First アプローチ。全スキルの frontmatter に `metadata.pattern` を付与し、skill-inventory.md にパターン列を追加。

**Tech Stack:** Markdown (SKILL.md frontmatter YAML, reference docs)

**Spec:** `docs/specs/2026-03-18-skill-design-patterns-design.md`

---

## Task 1: `references/skill-patterns.md` 新規作成

**Files:**
- Create: `.config/claude/references/skill-patterns.md`

- [ ] **Step 1: ファイル作成**

`references/skill-patterns.md` を以下の構造で作成:

```markdown
# Skill Design Patterns

5つの設計パターンで SKILL.md の内部ロジックを構造化する。

## Pattern Catalog

### Tool Wrapper

**Purpose**: ライブラリ/フレームワークの規約をオンデマンドでロードし適用する
**When to use**: 特定技術のベストプラクティスを適用したい時
**Key structure**:
1. キーワードトリガーで発火
2. `references/` から規約ドキュメントを読み込む
3. コードに対して規約を適用
**Required elements**: `references/` 内のドキュメント、description 内のキーワードトリガー
**Gate conditions**: なし（単純適用）
**Composability**: Generator/Reviewer の前段として使用可能

### Generator

**Purpose**: テンプレートから定型出力を一貫して生成する
**When to use**: 毎回同じ構造の出力が必要な時
**Key structure**:
1. テンプレート (`assets/` or inline) をロード
2. スタイルガイド (`references/`) をロード
3. ユーザーから変数を収集
4. テンプレートを充填して出力
**Required elements**: テンプレート (assets/ or inline)、出力フォーマット定義
**Gate conditions**: なし
**Composability**: Inversion の後段として変数収集後に実行可能

### Reviewer

**Purpose**: チェックリストに基づいてコードや成果物を体系的に評価する
**When to use**: 品質基準に照らした評価が必要な時
**Key structure**:
1. `references/` からチェックリストをロード
2. 対象を各項目に照らして検査
3. 発見を severity (error/warning/info) で分類
4. スコアと推奨事項を出力
**Required elements**: `references/` 内のチェックリスト、severity 分類
**Gate conditions**: なし
**Composability**: Pipeline の最終ステップとして、Tool Wrapper の後段として使用可能

### Inversion

**Purpose**: エージェントがユーザーにインタビューしてから行動する
**When to use**: 要件が曖昧で、先に収集が必要な時
**Key structure**:
1. フェーズを定義（Phase 1: 問題発見, Phase 2: 制約, Phase 3: 合成）
2. 各フェーズで1問ずつ質問、回答を待つ
3. 全フェーズ完了までゲート ("DO NOT proceed until all phases are complete")
4. 収集結果を合成して出力
**Required elements**: フェーズ分け、ゲート条件
**Gate conditions**: "DO NOT start building/designing until all phases are complete"
**Composability**: Generator の前段として使用可能（要件収集 → テンプレート出力）

### Pipeline

**Purpose**: 厳密な順序の多段ワークフローを保証する
**When to use**: ステップの省略や順序変更が許されない時
**Key structure**:
1. 番号付きステップ (`## Step N — 名前`)
2. 各ステップにゲート条件（ユーザー承認、テスト通過等）
3. ゲート未通過で次ステップへの進行を明示的に禁止
4. 失敗時の挙動を明記
**Required elements**: 番号付きステップ、各ステップのゲート条件、失敗時の挙動
**Gate conditions**: "Do NOT proceed to Step N+1 until [condition]"
**Composability**: 最終ステップに Reviewer を含めることが多い

## Decision Tree

スキルの主目的から最適パターンを選ぶ:

    スキルの主目的は？
    ├─ 知識を適用 → Tool Wrapper
    ├─ 定型出力を生成 → Generator
    ├─ コードや成果物を評価 → Reviewer
    ├─ 要件を収集してから行動 → Inversion
    └─ 複数ステップを順序保証 → Pipeline

**複合ケースの判定**: 主目的で1つ選び、副次的な機能を `+` で合成する。
例: 要件収集(主) + テンプレート出力(副) → `inversion+generator`

## Composition Patterns

パターンは合成可能。よくある組み合わせ:

- **Inversion + Generator**: 要件収集 → テンプレート出力 (例: /spec, /timekeeper)
- **Pipeline + Reviewer**: 多段処理の最終ステップで品質チェック (例: /epd)
- **Tool Wrapper + Reviewer**: 規約ロード → 規約に基づくレビュー (例: /review + review-checklists/)
- **Pipeline + Inversion**: 多段処理の初期ステップでインタビュー (例: /skill-creator, /init-project)

## Structure Quality Checklist

パターン別の必須要素。skill-creator の Stage 6 (Test) で検証に使用:

| Pattern | Required Elements |
|---------|-------------------|
| Tool Wrapper | `references/` 内のドキュメント、キーワードトリガー |
| Generator | テンプレート (`assets/` or inline)、出力フォーマット定義 |
| Reviewer | `references/` 内のチェックリスト、severity 分類 |
| Inversion | フェーズ分け、ゲート条件 ("DO NOT proceed until...") |
| Pipeline | 番号付きステップ、各ステップのゲート条件、失敗時の挙動 |

## Frontmatter Schema

SKILL.md の frontmatter に追加:

    metadata:
      pattern: pipeline                 # tool-wrapper | generator | reviewer | inversion | pipeline
      # pattern: inversion+generator    # 合成の場合は + で連結（主目的を先に）
      composable-with: [reviewer]       # optional: 組み合わせ可能なパターン
```

- [ ] **Step 2: 内容を目視確認**

5パターン定義 + Decision Tree + 合成例 + 品質チェックリスト + Frontmatter Schema が揃っていることを確認。

- [ ] **Step 3: コミット**

```bash
git add .config/claude/references/skill-patterns.md
git commit -m "✨ feat(references): add skill design patterns reference"
```

---

## Task 2: `skill-creator/SKILL.md` に Pattern Selection ステージ追加

**Files:**
- Modify: `.config/claude/skills/skill-creator/SKILL.md` (Stage 1.5 挿入, Stage 4・6 修正)
- Modify: `.config/claude/skills/skill-creator/references/planning-guide.md` (パターン判断フロー追加)

- [ ] **Step 1: SKILL.md に Stage 1.5 を挿入**

`### Interview and Research` の直前（`### Quality Gate` の直後）に以下を挿入:

```markdown
### Pattern Selection

After the Quality Gate, determine the skill's design pattern:

1. Load `references/skill-patterns.md` and review the Decision Tree
2. Based on the Capture Intent answers (especially Q1: purpose, Q2: category), recommend the best-fit pattern
3. Present the recommendation to the user:
   - "Based on your description, this skill fits the **[Pattern]** pattern: [1-sentence why]"
   - If composite: "This combines **[Pattern A]** (for [purpose]) with **[Pattern B]** (for [purpose])"
4. Ask the user to confirm or suggest a different pattern
5. Note the selected pattern's Required Elements from the Structure Quality Checklist — these will be verified in the Test stage

The pattern selection will be used in:
- **Write SKILL.md stage**: to add `metadata.pattern` to frontmatter and scaffold pattern-specific structure
- **Test stage**: to verify required elements are present
```

- [ ] **Step 2: Stage 4 (Write SKILL.md) にパターン適用ロジックを追加**

既存の SKILL.md 作成指示に以下を追加:

```markdown
#### Pattern-Aware Scaffolding

When writing the SKILL.md:
- Add `metadata.pattern` to the frontmatter (e.g., `metadata:\n  pattern: pipeline`)
- For composite patterns, use `+` notation (e.g., `inversion+generator`)
- Scaffold the pattern's required structure:
  - **Pipeline**: `## Step N — [Name]` sections with gate conditions
  - **Inversion**: `## Phase N — [Name]` sections with "DO NOT proceed until..." gate
  - **Reviewer**: Reference to checklist file + severity output format
  - **Generator**: Template reference + output format specification
  - **Tool Wrapper**: Reference to conventions file + trigger keywords in description
```

- [ ] **Step 3: Stage 6 (Test) にパターン検証を追加**

テスト項目に以下を追加:

```markdown
#### Pattern Compliance Check

After running test prompts, also verify:
- The SKILL.md contains `metadata.pattern` in its frontmatter
- The required elements for the selected pattern (from `references/skill-patterns.md` Structure Quality Checklist) are present in the skill's instructions
- If a Pipeline, numbered steps with gate conditions exist
- If an Inversion, phase definitions with explicit gating language exist
- If a Reviewer, a checklist reference and severity classification exist

Flag any missing required elements as warnings for the user to address.
```

- [ ] **Step 4: planning-guide.md にパターンセクション追加**

`references/planning-guide.md` の末尾に追加:

```markdown
## Design Patterns

See `references/skill-patterns.md` for the complete pattern catalog.

Quick reference for pattern selection during Capture Intent:

| If the skill primarily... | Pattern |
|---------------------------|---------|
| Teaches library/framework conventions | Tool Wrapper |
| Produces structured documents from templates | Generator |
| Evaluates code/artifacts against criteria | Reviewer |
| Interviews the user before acting | Inversion |
| Enforces a strict multi-step workflow | Pipeline |
```

- [ ] **Step 5: 変更を確認**

skill-creator の全体フローが Stage 1 → Quality Gate → **Pattern Selection** → Interview → Write → Security Scan → Test → Iterate の順序であることを確認。

- [ ] **Step 6: コミット**

```bash
git add .config/claude/skills/skill-creator/SKILL.md .config/claude/skills/skill-creator/references/planning-guide.md
git commit -m "✨ feat(skill-creator): add Pattern Selection stage with pattern-aware scaffolding"
```

---

## Task 3: 全スキルの frontmatter に `metadata.pattern` を付与

**Files:**
- Modify: `.config/claude/skills/*/SKILL.md` (50+ files, frontmatter のみ)

- [ ] **Step 1: 全スキルディレクトリを列挙**

```bash
ls -1 .config/claude/skills/
```

spec の分類マッピングテーブルを参照しつつ、各スキルの frontmatter にのみ `metadata.pattern` を追加する。

- [ ] **Step 2: Core Workflow スキルの frontmatter を更新 (9 skills)**

各 SKILL.md の `---` ブロック内、`description:` の後に `metadata:\n  pattern: <value>` を追加。

マッピング:
- `check-health`: `reviewer`
- `search-first`: `pipeline`
- `review`: `reviewer`
- `verification-before-completion`: `pipeline+reviewer`
- `continuous-learning`: `pipeline`
- `spec`: `inversion+generator`
- `spike`: `pipeline`
- `validate`: `reviewer`
- `codex-review`: `reviewer`

**重要**: 本体の指示テキストは一切変更しない。frontmatter の `---` ブロック内のみ。

- [ ] **Step 3: Cross-Model / Research スキルの frontmatter を更新 (5 skills)**

- `codex`: `tool-wrapper`
- `gemini`: `tool-wrapper`
- `research`: `pipeline`
- `epd`: `pipeline`
- `interviewing-issues`: `inversion`

- [ ] **Step 4: Domain / Specialist スキルの frontmatter を更新 (11 skills)**

- `react-best-practices`: `tool-wrapper`
- `react-expert`: `tool-wrapper`
- `senior-frontend`: `tool-wrapper`
- `senior-backend`: `tool-wrapper`
- `senior-architect`: `tool-wrapper`
- `graphql-expert`: `tool-wrapper`
- `buf-protobuf`: `tool-wrapper`
- `frontend-design`: `generator`
- `ui-ux-pro-max`: `tool-wrapper+generator`
- `web-design-guidelines`: `reviewer`
- `vercel-composition-patterns`: `tool-wrapper`
- `webapp-testing`: `tool-wrapper`
- `edge-case-analysis`: `reviewer`

- [ ] **Step 5: Automation / Meta スキルの frontmatter を更新 (8 skills)**

- `autonomous`: `pipeline`
- `improve`: `pipeline`
- `skill-creator`: `pipeline+inversion`
- `skill-audit`: `reviewer`
- `eureka`: `generator`
- `create-pr-wait`: `pipeline`
- `setup-background-agents`: `generator`
- `ai-workflow-audit`: `reviewer`

- [ ] **Step 6: 残りのスキルの frontmatter を更新**

spec のマッピングを参照:
- `daily-report`: `generator`
- `timekeeper`: `inversion+generator`
- `digest`: `generator`
- `github-pr`: `pipeline`
- `init-project`: `pipeline+inversion`
- `absorb`: `pipeline`
- `debate`: `pipeline`
- `security-review`: `reviewer`
- `obsidian-content`: `generator`
- `obsidian-knowledge`: `tool-wrapper`
- `obsidian-vault-setup`: `generator`
- `fix-issue`: `pipeline`
- `rpi`: `pipeline`
- `checkpoint`: `generator`

マッピングに含まれないスキルは Decision Tree で判断して分類する。

- [ ] **Step 7: 全スキルの frontmatter に pattern が含まれることを検証**

```bash
for f in .config/claude/skills/*/SKILL.md; do
  if ! grep -q 'pattern:' "$f"; then
    echo "MISSING: $f"
  fi
done
```

出力が空であること = 全スキルに pattern が付与済み。

- [ ] **Step 8: 本体ロジックが変更されていないことを確認**

```bash
git diff --stat .config/claude/skills/
```

各ファイルの変更行数が 2-3 行（metadata 追加分のみ）であることを目視確認。大きな差分がないこと。

- [ ] **Step 9: コミット**

```bash
git add .config/claude/skills/
git commit -m "✨ feat(skills): add metadata.pattern to all skill frontmatter"
```

---

## Task 4: `skill-inventory.md` にパターン列を追加

**Files:**
- Modify: `.config/claude/references/skill-inventory.md`

- [ ] **Step 1: 各ティアのリストにパターン情報を追加**

既存のリスト形式を維持しつつ、各スキル名の後にパターンを追記:

```markdown
## Core Workflow

- `check-health` — reviewer
- `search-first` — pipeline
- `review` — reviewer
...
```

全5ティア（Core Workflow, Cross-Model, Domain, Automation, Personal Ops）を更新。

- [ ] **Step 2: パターン分布サマリーを末尾に追加**

```markdown
## Pattern Distribution

| Pattern | Count | Example Skills |
|---------|-------|----------------|
| tool-wrapper | ~12 | codex, gemini, react-expert, senior-* |
| generator | ~9 | eureka, daily-report, digest, frontend-design |
| reviewer | ~10 | review, check-health, validate, skill-audit |
| inversion | ~2 | interviewing-issues |
| pipeline | ~14 | epd, autonomous, research, rpi |
| composite | ~6 | spec (inv+gen), skill-creator (pipe+inv) |
```

- [ ] **Step 3: コミット**

```bash
git add .config/claude/references/skill-inventory.md
git commit -m "📝 docs(inventory): add pattern classification to skill inventory"
```

---

## Task 5: 最終検証

- [ ] **Step 1: Acceptance Criteria を全件チェック**

1. `references/skill-patterns.md` が存在し、5パターン + Decision Tree + 合成例 + 品質チェックリストを含む → `cat .config/claude/references/skill-patterns.md | head -5`
2. `skill-creator/SKILL.md` に Pattern Selection ステージがある → `grep -c "Pattern Selection" .config/claude/skills/skill-creator/SKILL.md`
3. 全スキルの frontmatter に pattern がある → Step 3-7 の検証スクリプト再実行
4. `skill-inventory.md` にパターン情報がある → `grep -c "pattern" .config/claude/references/skill-inventory.md`
5. 既存スキルの本体ロジックが変更されていない → `git diff HEAD~4 --stat` で変更行数確認

- [ ] **Step 2: symlink 検証**

```bash
task validate-symlinks
```

dotfiles の symlink が壊れていないことを確認。

- [ ] **Step 3: メモリ更新**

MEMORY.md に Skill Design Patterns 統合の記録を追加。
