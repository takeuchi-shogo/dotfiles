# /init-project スキル 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** プロジェクトを分析し、最適な Claude Code 構造(S/M/L)を段階的に構築するオーケストレータスキルを作成する

**Architecture:** 薄いオーケストレーション層（SKILL.md）+ 参照ドキュメント（references/）。実際の生成は既存ファクトリエージェント（constitution-factory, context-factory, setup-background-agents）に委譲する。プロジェクト分析と規模判定のロジックはスキル本体に記述。

**Tech Stack:** Claude Code Skills（Markdown）、既存ファクトリエージェント群

**Design Doc:** `docs/plans/2026-03-12-init-project-skill-design.md`

---

### Task 1: スキルディレクトリとメイン SKILL.md 作成

**Files:**
- Create: `.config/claude/skills/init-project/SKILL.md`

**Step 1: ディレクトリ構造を確認**

Run: `ls .config/claude/skills/ | head -5`
Expected: 既存スキルのリストが表示される

**Step 2: SKILL.md を作成**

SKILL.md の構造:

```markdown
---
name: init-project
description: >
  プロジェクトに最適な Claude Code 構造を初期化・適応する。プロジェクト分析 → 規模判定(S/M/L) →
  ファクトリエージェント委譲で CLAUDE.md, .claudeignore, references/, rules/, docs/, Local CLAUDE.md を段階的に生成。
  新プロジェクト初期化、既存プロジェクトへの Claude Code 導入、S→M→L の段階的アップグレードに使用。
  Use when: 'init project', 'setup claude', 'プロジェクト初期化', 'Claude Code 導入',
  'CLAUDE.md 作りたい', 'プロジェクト構造', 'scaffold'.
  Do NOT use for: 既存 CLAUDE.md の修正のみ（claude-md-management を使用）、
  背景エージェントのみ（setup-background-agents を使用）。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---
```

本体の構成:
1. コンセプト（Pandey 5層 + オーケストレータ）
2. Phase 1: Detect（自動検出ロジック → references/detection-rules.md 参照）
3. Phase 2: Generate（レベル別ファクトリ委譲フロー）
4. Phase 3: Verify（整合性チェック）
5. 既存プロジェクト適応（Gap Analysis）
6. アップグレードフロー（S→M→L）

**Step 3: 作成した SKILL.md の構文を確認**

Run: `head -5 .config/claude/skills/init-project/SKILL.md`
Expected: frontmatter が正しく表示される

**Step 4: Commit**

```bash
git add .config/claude/skills/init-project/SKILL.md
git commit -m "✨ feat: add init-project skill skeleton with SKILL.md"
```

---

### Task 2: 検出ルール参照ドキュメント作成

**Files:**
- Create: `.config/claude/skills/init-project/references/detection-rules.md`

**Step 1: 参照ドキュメントを作成**

内容:
1. **シグナルテーブル** — 各シグナル（ファイル数、言語数、CI有無、contributors、フレームワーク、テスト、docs、リスキーモジュール）のスコアリング基準
2. **検出コマンド** — 各シグナルの具体的な検出 bash コマンド
3. **スコアリングロジック** — 加重平均 + 強制ルール（CI + リスキーモジュール2+ → L）
4. **リスキーモジュール検出パターン** — auth/, billing/, migration/, infra/, security/, persistence/ 等

constitution-factory の Phase 1 と重複する部分は「constitution-factory に委譲する」と明記し、init-project 固有の**規模判定ロジック**に集中する。

**Step 2: Commit**

```bash
git add .config/claude/skills/init-project/references/detection-rules.md
git commit -m "📝 docs: add detection rules reference for init-project skill"
```

---

### Task 3: レベル別テンプレート参照ドキュメント作成

**Files:**
- Create: `.config/claude/skills/init-project/references/level-templates.md`

**Step 1: テンプレートドキュメントを作成**

内容:
1. **S テンプレート** — CLAUDE.md + .claudeignore のみ。constitution-factory への委譲パラメータ
2. **M テンプレート** — + references/workflow-guide.md + rules/{lang}.md + docs/architecture.md。constitution-factory + context-factory への委譲パラメータ
3. **L テンプレート** — + .claude/settings.json(hooks) + docs/decisions/ + Local CLAUDE.md + background agents。全ファクトリへの委譲パラメータ

各レベルで:
- 生成するファイルのリスト
- 委譲先ファクトリとそのプロンプトテンプレート
- 並列実行可能なタスクの識別（S は直列、M/L は並列委譲）

**Step 2: Commit**

```bash
git add .config/claude/skills/init-project/references/level-templates.md
git commit -m "📝 docs: add level templates reference for init-project skill"
```

---

### Task 4: Gap Analysis 参照ドキュメント作成

**Files:**
- Create: `.config/claude/skills/init-project/references/gap-analysis.md`

**Step 1: Gap Analysis ドキュメントを作成**

既存プロジェクトに適用する際の分析フレームワーク:

1. **Pandey 5層チェックリスト**:
   - Layer 1 (CLAUDE.md): 存在する？100行以内？WHY/WHAT/HOW を含む？
   - Layer 2 (skills/): .claude/skills/ が存在する？再利用可能なワークフローがある？
   - Layer 3 (hooks/): settings.json に hooks が設定されている？フォーマッタ・テスト・ブロックがある？
   - Layer 4 (docs/): architecture.md がある？ADR がある？runbook がある？
   - Layer 5 (Local CLAUDE.md): リスキーモジュール近くに CLAUDE.md がある？

2. **現在のレベル判定** — 既存の構造が S/M/L のどこに該当するか
3. **ギャップリスト** — 不足している層のリスト
4. **アップグレード提案** — 不足を埋めるために必要なファクトリ委譲

**Step 2: Commit**

```bash
git add .config/claude/skills/init-project/references/gap-analysis.md
git commit -m "📝 docs: add gap analysis reference for init-project skill"
```

---

### Task 5: コマンドファイル作成

**Files:**
- Create: `.config/claude/commands/init-project.md`

**Step 1: コマンドファイルを作成**

```markdown
---
description: プロジェクトに最適な Claude Code 構造を初期化する
---

$ARGUMENTS を引数として受け取る。

引数の解釈:
- 引数なし → 現在のディレクトリでフル初期化
- `--upgrade` → 既存構造の段階的アップグレード
- `--level S|M|L` → レベルを明示指定（自動検出をスキップ）
- `--dry-run` → 生成するファイルのリストのみ表示、実際には生成しない

init-project スキルを使用してプロジェクトの初期化を実行してください。
```

**Step 2: Commit**

```bash
git add .config/claude/commands/init-project.md
git commit -m "✨ feat: add /init-project command"
```

---

### Task 6: SKILL.md 本体の詳細実装

**Files:**
- Modify: `.config/claude/skills/init-project/SKILL.md`

**Step 1: Phase 1 (Detect) セクションを実装**

- プロジェクト分析の具体的な手順
- `references/detection-rules.md` への参照
- ユーザーへの結果提示フォーマット
- override オプション

**Step 2: Phase 2 (Generate) セクションを実装**

- レベル別のファクトリ委譲フロー
- `references/level-templates.md` への参照
- 各ファクトリへのプロンプトテンプレート
- 並列委譲の指示（M: constitution + context 並列、L: 全ファクトリ並列）

**Step 3: Phase 3 (Verify) セクションを実装**

- 生成物の整合性チェックリスト
- CLAUDE.md 行数チェック
- 参照リンクの実在確認
- 次ステップの提案

**Step 4: 既存プロジェクト適応セクションを実装**

- `references/gap-analysis.md` への参照
- 上書き防止のルール
- `--upgrade` フローの詳細

**Step 5: Commit**

```bash
git add .config/claude/skills/init-project/SKILL.md
git commit -m "✨ feat: implement full init-project skill workflow"
```

---

### Task 7: symlink 設定の更新

**Files:**
- Modify: `.bin/symlink.sh`（必要な場合のみ）

**Step 1: symlink 状況を確認**

Run: `grep -n "skills" .bin/symlink.sh | head -10`
Expected: スキルの symlink 設定を確認

**Step 2: 新スキルが自動で含まれるか確認**

`.config/claude/skills/` 配下のスキルは `.config/claude/` → `~/.claude/` の symlink で自動的に含まれるはず。追加の symlink 設定が不要であることを確認する。

Run: `ls -la ~/.claude/skills/init-project/ 2>/dev/null || echo "Not yet linked"`

**Step 3: 必要なら symlink を追加（通常は不要）**

**Step 4: Commit**（変更がある場合のみ）

---

### Task 8: 検証

**Step 1: スキルファイルの構文チェック**

Run: `head -20 .config/claude/skills/init-project/SKILL.md`
Expected: YAML frontmatter が正しいこと

**Step 2: 参照ファイルの存在チェック**

Run: `ls -la .config/claude/skills/init-project/references/`
Expected: detection-rules.md, level-templates.md, gap-analysis.md が存在

**Step 3: コマンドファイルの存在チェック**

Run: `ls -la .config/claude/commands/init-project.md`
Expected: ファイルが存在

**Step 4: 全体の構造確認**

Run: `find .config/claude/skills/init-project -type f`
Expected:
```
.config/claude/skills/init-project/SKILL.md
.config/claude/skills/init-project/references/detection-rules.md
.config/claude/skills/init-project/references/level-templates.md
.config/claude/skills/init-project/references/gap-analysis.md
```

**Step 5: task validate-configs を実行**

Run: `task validate-configs`
Expected: 設定ファイルのバリデーションが通ること

**Step 6: task validate-symlinks を実行**

Run: `task validate-symlinks`
Expected: symlink のバリデーションが通ること

---

## 実行順序と依存関係

```
Task 1 (SKILL.md skeleton)
    ├── Task 2 (detection-rules.md)     ← 並列可
    ├── Task 3 (level-templates.md)     ← 並列可
    └── Task 4 (gap-analysis.md)        ← 並列可
Task 5 (command file)                   ← Task 1 完了後
Task 6 (SKILL.md 詳細実装)             ← Task 2,3,4 完了後
Task 7 (symlink)                        ← Task 6 完了後
Task 8 (検証)                           ← 全タスク完了後
```

## 注意事項

- SKILL.md は 500 行以内に収める（Progressive Disclosure）
- 詳細ロジックは references/ に分離
- 既存ファクトリのプロンプトは「テンプレート」として記述し、ファクトリ側の進化に追従できるようにする
- GP-001（共有ユーティリティ優先）: ファクトリのロジックを複製しない
