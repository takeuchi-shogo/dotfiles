---
name: review
description: >
  コード変更のレビューを実行。変更規模に応じてレビューアーを自動選択・並列起動し、結果を統合する。
  コード変更後の Review 段階で使用、または /review で手動起動。
  言語固有チェックリストは references/review-checklists/ に配置。code-reviewer のプロンプトに注入して使用。
allowed-tools: Read, Bash, Grep, Glob, Agent
---

# Code Review Orchestrator

コード変更に対して、適切なレビューアーを自動選択・並列起動し、結果を統合するオーケストレーター。

## Workflow

```
1. Pre-analysis  → git diff で変更を分析
2. Scaling       → 行数・内容からレビュアー構成を決定
3. Dispatch      → Agent ツールで1メッセージに並列起動
4. Synthesis     → 結果を統合し templates/review-output.md 形式で出力
```

## Step 1: Pre-analysis

```bash
git diff --stat HEAD
git diff --name-only HEAD
```

以下を特定する:

- **変更行数**: insertions + deletions の合計
- **言語**: 変更ファイルの拡張子
- **コンテンツシグナル**: diff 内容からスペシャリストの必要性を判定

## Step 2: Scaling Decision

### レビュアー構成（行数ベース）

| 変更規模 | 構成                                                                                                       |
| -------- | ---------------------------------------------------------------------------------------------------------- |
| ~10行    | レビュー省略（Verify のみ）                                                                                |
| ~50行    | `code-reviewer`（言語チェックリスト注入）+ `codex-reviewer`（2並列）                                       |
| ~200行   | `code-reviewer`（言語チェックリスト注入）+ `codex-reviewer` + `golang-reviewer`（Go変更時、3並列）          |
| 200行超  | `code-reviewer`（言語チェックリスト注入）+ `codex-reviewer` + `golang-reviewer`（Go変更時）+ スペシャリスト |

### 言語固有チェックリスト（プロンプト注入）

`code-reviewer` のプロンプトに、該当言語のチェックリストを Read して注入する:

| 拡張子              | 参照ファイル                                  |
| ------------------- | --------------------------------------------- |
| `.ts/.tsx/.js/.jsx` | `references/review-checklists/typescript.md`  |
| `.go`               | `references/review-checklists/go.md`          |
| `.py`               | `references/review-checklists/python.md`      |
| `.rs`               | `references/review-checklists/rust.md`        |
| 複数言語混在        | 該当する全チェックリストをプロンプトに含める  |

### コンテンツベースのスペシャリスト自動検出

行数に関係なく、diff の内容にマッチするスペシャリストを追加する。
ただし **50行以上の変更** でのみ適用（10行以下はレビュー自体を省略）。

| diff 内のシグナル  | スペシャリスト          | 検出パターン                                                       |
| ------------------ | ----------------------- | ------------------------------------------------------------------ |
| エラーハンドリング | `silent-failure-hunter` | `catch`, `recover`, `fallback`, `retry`, `on.*error`, `try {`      |
| 新しい型定義       | `type-design-analyzer`  | `type `, `interface `, `struct `, `enum ` の追加行                 |
| テスト変更         | `pr-test-analyzer`      | `_test.go`, `.test.ts`, `.spec.ts`, `__tests__/` のファイル変更    |
| コメント大量変更   | `comment-analyzer`      | `/** */`, `///`, `# ` のブロック追加（10行以上）                   |
| nil/ポインタ操作   | `nil-path-reviewer`     | `*`, `nil`, `Option`, `.Get()`, ポインタ型フィールドの追加/変更    |
| spec file 存在     | `product-reviewer`      | `docs/specs/*.prompt.md` がリポジトリに存在                        |
| UI 変更            | `design-reviewer`       | `.tsx`, `.css`, `.scss`, `.html`, `.vue`, `.svelte` のファイル変更 |

### 戦略的整合性チェック（"On the Loop" レビュー）

"The Self-Driving Codebase" の知見: 「技術的に正しいが戦略的に間違っている」変更を検出する。

**spec file が存在する場合** (`docs/specs/*.prompt.md`):
- `product-reviewer` を**必須**レビューアーとして追加（行数に関わらず、50行以上で適用）
- プロンプトに spec file のパスを含め、acceptance criteria との整合性を検証

**product-reviewer への追加指示**:
- 変更が spec の acceptance criteria を満たしているか
- スコープクリープ（spec にない機能の追加）がないか
- spec が意図する問題を実際に解決しているか
- 技術的に正しくても、ユーザー課題の解決から外れていないか

## Step 3: Dispatch

**Agent ツールで1メッセージに全レビューアーを並列起動する。**

#### フレーミング注入

各レビューアーの prompt 先頭に **Sync フレーミング**（`references/subagent-framing.md`）を付加する:

> あなたはサブエージェントです。結果は親エージェントに返され、統合されます。
> 要点を簡潔にまとめてください。詳細な説明より、発見事項と推奨アクションを優先してください。

各エージェントへのプロンプトには以下を含める:

- レビュー対象の git diff
- 変更ファイルのパス一覧
- プロジェクトの CLAUDE.md（存在する場合）

詳細なルーティング情報は `references/reviewer-routing.md` を参照。

## Step 4: Synthesis

全レビューアーの結果を `templates/review-output.md` のフォーマットに従って統合する。

統合ルール:

1. **重複排除**: 同じファイル・行への指摘が複数ある場合、最も具体的なものを残す
2. **重要度順**: Critical → Important → Suggestion の順に整理
3. **アクション明示**: 各指摘に対して「修正必須」「検討推奨」「参考」を付与
4. **判定**: 全体として修正が必要かどうかを明示する
5. **信頼度フィルタ**: confidence < 80 の指摘を除外
6. **既存コード除外**: diff の追加行以外への指摘を除外
7. **linter 重複除外**: フォーマッター・linter が検出すべき問題を除外
8. **戦略的整合性**: spec file 存在時、product-reviewer の「spec 不整合」指摘は Critical として扱う

## Step 5: Findings Persistence（フィードバックループ）

Step 4 の統合後、最終レポートに含まれる各指摘を `review-findings.jsonl` に保存する。
これにより、後続の git commit 時に `review-feedback-tracker.py` hook が
指摘の受入/却下を自動判定し、レビューアーの精度追跡が可能になる。

**保存方法**: Bash ツールで以下の Python スクリプトを実行する:

```bash
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts/lib')
from session_events import emit_review_finding
import json, hashlib, datetime

findings = json.loads(sys.stdin.read())
for f in findings:
    emit_review_finding(f)
print(f'{len(findings)} findings saved')
" <<'FINDINGS_JSON'
[
  {
    "id": "rf-{date}-{seq:03d}",
    "reviewer": "{reviewer_agent_name}",
    "file": "{file_path}",
    "line": {line_number},
    "confidence": {confidence_score},
    "failure_mode": "{FM-XXX or empty}",
    "finding": "{指摘の要約}",
    "failure_type": "generalization"
  }
]
FINDINGS_JSON
```

**ID生成ルール**: `rf-YYYY-MM-DD-NNN` (例: `rf-2026-03-12-001`)

**failure_mode マッピング**: `references/failure-taxonomy.md` を参照し、指摘内容に最も近い FM-XXX を付与する。
マッチしない場合は空文字列。

## Anti-Patterns

- レビューアーを直接 Skill ツールで起動する（Agent ツールで並列起動すること）
- 行数だけでスペシャリストを判断する（コンテンツシグナルも見ること）
- レビュー結果をそのまま列挙する（統合・重複排除すること）
- 10行以下の変更に対してフルレビューを実行する
- findings の保存を省略する（フィードバックループが機能しなくなる）
