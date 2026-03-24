---
name: review
description: >
  コード変更のレビューを実行。変更規模に応じてレビューアーを自動選択・並列起動し、結果を統合する。
  コード変更後の Review 段階で使用、または /review で手動起動。
  言語固有チェックリストは references/review-checklists/ に配置。code-reviewer のプロンプトに注入して使用。
  Triggers: 'レビューして', 'review', 'コードレビュー', 'セルフレビュー', 'check my code'.
  Do NOT use for: 直近の差分確認のみ（use git diff）、100行超の Codex レビュー（use /codex-review）、Product 観点の検証（use /validate）。
allowed-tools: Read, Bash, Grep, Glob, Agent
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: prompt
          prompt: >
            [REVIEW GUARD] /review スキルのレビューフェーズ（Step 1〜4: 分析・起動・統合・出力）が
            現在進行中の場合のみブロックしてください。
            レビュー結果の報告が完了した後、またはユーザーが「修正して」「直して」等の指示を出した後は
            Edit/Write を許可してください。
            判定基準: レビュー統合レポートがまだ出力されていない → ブロック。出力済み → 許可。
metadata:
  pattern: reviewer
  version: 1.0.0
  category: quality
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

## Step 1.3: Impact Pre-scan（30行以上の変更）

diff を見る**前に**、変更された関数・型の呼び出し元を特定する。
表面上は安全な変更でも、呼び出し元を考慮すると破壊的変更になるケースを防ぐ。

1. `git diff --name-only HEAD` で変更ファイルを取得
2. 各ファイルの diff から、**追加・削除・シグネチャ変更された export 関数/型** を抽出
3. `Grep` で各 export の呼び出し元を検索（上位5件まで）
4. 結果を以下の形式でまとめ、Step 3 で各レビューアーのプロンプトに含める:

```
### Impact Context
- `funcX()` in file_a.ts → called by: file_b.ts:15, file_c.ts:42
- `TypeY` in file_a.ts → referenced by: file_d.ts:8
```

- 10行以下の変更・export のないファイルのみの変更ではスキップ
- PRE_ANALYSIS モードの `cross-file-reviewer` と異なり、ここでは**簡易版**（Grep 1回/export）に留める

## Step 1.5: Design Rationale Check（M/L のみ）

M/L 規模の変更では、レビュー開始前に Design Rationale の存在を確認する（S は免除）。

確認項目（`references/comprehension-debt-policy.md` 参照）:
1. **What**: この変更は何を解決するか — 記述があるか
2. **Why this approach**: なぜこのアプローチか（却下した代替案含む）— 記述があるか
3. **Risk mitigation**: 何が壊れうるか、どう防いでいるか — 記述があるか

- Plan ファイル、コミットメッセージ、または PR 説明に含まれているか確認
- 不十分な場合はレビュー冒頭で `must:` として指摘し、記述を求める

## Step 2: Scaling Decision

### レビュアー構成（行数ベース）

| 変更規模 | 構成                                                                                                       | 最大N |
| -------- | ---------------------------------------------------------------------------------------------------------- | ----- |
| ~10行    | レビュー省略（Verify のみ）                                                                                                       | 0 |
| ~30行    | `code-reviewer`（言語チェックリスト注入）+ `codex-reviewer`                                                                        | 2 |
| ~50行    | 上記 + `edge-case-hunter` + `cross-file-reviewer`（2+ファイル時のみ）                                                              | 4 |
| ~200行   | 上記 + `golang-reviewer`（Go変更時）+ **Gemini セキュリティレビュー**                                                              | 6 |
| 200行超  | 上記全て + スペシャリスト（3-way: Claude + Codex + Gemini）                                                                        | 8 |

> **Scaling Note**: レビューア数の増加は合意コスト（矛盾の検出・解決）を増大させる。
> 上限を超えるスペシャリスト候補がある場合、コンテンツシグナルの強さでトリアージし上限内に収める。
> 詳細: `references/review-consensus-policy.md`

### 言語固有チェックリスト（プロンプト注入）

`code-reviewer` のプロンプトに、**cross-cutting + 該当言語**のチェックリストを Read して注入する:

| 拡張子              | 参照ファイル                                  |
| ------------------- | --------------------------------------------- |
| **全レビュー共通**  | `references/review-checklists/cross-cutting.md` |
| `.ts/.tsx/.js/.jsx` | `references/review-checklists/typescript.md`  |
| `.go`               | `references/review-checklists/go.md`          |
| `.py`               | `references/review-checklists/python.md`      |
| `.rs`               | `references/review-checklists/rust.md`        |
| 複数言語混在        | 該当する全チェックリストをプロンプトに含める  |

> **cross-cutting.md は常時注入する。** 言語固有チェックリストは追加で注入する。

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
| L規模/API境界変更  | `longevity-reviewer`    | 200行以上の変更、または API 境界ファイル（handler, controller, api, endpoint, route, server）の変更 |

### Gemini セキュリティレビュー（3-way レビュー、~200行以上）

~200行以上の変更では、Codex(深さ) + Claude(幅) に加えて **Gemini(セキュリティ・エコシステム)** を投入する。
3つの独立した視点で盲点を最小化する（claude-octopus の 3-way review パターン）。

**Gemini への起動方法**: Agent ツールで `gemini-explore` エージェントを他レビューアーと並列起動。プロンプト例:

> Review the following git diff from a security and ecosystem perspective.
> Check: dependency risks, known CVE patterns, OWASP Top 10 violations,
> better alternatives in the ecosystem, and community anti-patterns.
> Output: [CRITICAL/HIGH/MEDIUM] file:line - description

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

1. **セマンティック重複排除**: 同一ファイル ±10行以内 + 同一 failure_mode の指摘は最高信頼度の1件に統合。統合元は「(他 N 件のレビューアーも同様の指摘)」と注記
2. **信頼度ブースト**: 複数の独立したレビューアーが同じ問題を指摘した場合、信頼度を `max(scores) + 5`（上限100）に引き上げ
3. **対立検出**: 同じ箇所で矛盾する指摘がある場合、両方残して `[CONFLICT]` タグを付与
4. **重要度順**: Critical → Important → Watch の順に整理
5. **アクション明示**: 各指摘に対して「修正必須」「検討推奨」「要注意」を付与
6. **判定**: Critical が1件以上 → BLOCK。Important が3件以上 → NEEDS_FIX。それ以外 → PASS。Watch は判定に影響しない
7. **信頼度フィルタ**: confidence < 60 の指摘を除外
8. **既存コード除外**: diff の追加行以外への指摘を除外
9. **linter 重複除外**: フォーマッター・linter が検出すべき問題を除外
10. **戦略的整合性**: spec file 存在時、product-reviewer の「spec 不整合」指摘は Critical として扱う
11. **合意率メトリクス**: `agreement_rate = 1 - (conflict_count / total_findings)`。conflict_count は同一ファイル+-5行で矛盾する指摘の組数。レポートの Agreement Rate フィールドに記入する。算出は全レビュー構成で実施（3-way に限定しない）
12. **収束停滞検出**: 以下のいずれかで `[CONVERGENCE STALL]` フラグを立て、verdict を `NEEDS_HUMAN_REVIEW` にする: (a) Critical 矛盾（2+レビューアが同一箇所で PASS vs BLOCK）、(b) Verdict 分裂（PASS と NEEDS_FIX が同数）、(c) Agreement Rate < 70%。詳細: `references/review-consensus-policy.md`
13. **外れ値検出**: 1体のレビューアの指摘が他と 20% 未満しか重ならない AND 指摘数が平均の 3x 以上の場合、`[OUTLIER]` タグを付与し verdict 計算から除外（情報は保持）。ただし codex-reviewer の深い推論に基づく指摘は `[DEEP_REASONING]` として保持。詳細: `references/review-consensus-policy.md`
14. **Capability-Weighted Synthesis**: 3体以上のレビュー構成時、`references/reviewer-capability-scores.md` の capability score でレビューアーの指摘を重み付けする。`effective_weight = capability_score[reviewer][domain] * severity_multiplier` (Critical=3, Important=2, Watch=1)。同一指摘が複数レビューアーから出た場合は重みを合算。合成レポートの指摘一覧を effective_weight 降順でソートする。2体以下では等価扱い。詳細: `references/review-consensus-policy.md` Section 6

### Coverage Check

レビューの網羅性を検証し、見落としを防ぐ。

1. **ファイルカバレッジ**: 変更ファイル数 vs レビューで言及されたファイル数の比率を算出し、レポートに `File Coverage: N/M (X%)` として出力
2. **大規模変更警告**: 100 行超の変更で全ファイルに言及がない場合、`[LOW COVERAGE]` 警告を付与
3. **comprehension_confidence スコア**: レビュー全体の理解度を 1-5 で評価し、レポート末尾に出力

```
## Comprehension Confidence
comprehension_confidence: ?/5
```

- 5: 全変更の意図・影響を完全に理解してレビュー
- 4: ほぼ全体を理解、一部不明箇所あり
- 3: 主要な変更は理解、周辺の影響は未確認
- 2: 部分的にしか理解できていない
- 1: 変更の意図が不明確

## Step 5: Review-Fix Cycle

Step 4 の verdict に応じて、修正→再レビューのサイクルを実行する。

```
Review → verdict 判定
  ├─ PASS           → Step 6 (Findings Persistence) → タスク完了をユーザーに報告
  ├─ NEEDS_FIX      → 指摘を修正 → 差分のみ再 Review → verdict 再判定
  ├─ BLOCK          → 指摘を修正 → フル再 Review → verdict 再判定
  └─ NEEDS_HUMAN_REVIEW → ユーザーに判断を委ねる
```

### サイクルルール

1. **PASS**: 修正不要。Step 6 に進み、完了をユーザーに報告する
2. **NEEDS_FIX**: Important 指摘を修正後、**修正差分のみ**を対象に再レビューする（レビューアー構成は修正行数で再スケーリング）
3. **BLOCK**: Critical 指摘を修正後、**全変更**を対象にフルレビューを再実行する
4. **NEEDS_HUMAN_REVIEW**: レビュー結果をユーザーに提示し、判断を委ねる
5. **最大サイクル数**: 3回。3回で PASS にならない場合はユーザーにエスカレーションする
6. **修正なし判定**: 再レビューで新規指摘がゼロなら PASS に昇格する

### 完了報告

サイクルが PASS で終了したら、ユーザーに以下を報告する:
- 変更サマリ（何を変えたか）
- レビュー結果（PASS + 主要な確認ポイント）
- 次のアクション提案（commit / 追加作業など）

## Step 6: Findings Persistence（フィードバックループ）

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

## Data Storage

レビュー結果のサマリを `~/.claude/skill-data/review/` に蓄積します。
蓄積データは AutoEvolve と連携し、頻出する指摘パターンの分析に使用します。

### 保存先
- `~/.claude/skill-data/review/reviews.jsonl` — レビュー結果サマリ (append-only)

### フォーマット (1行1JSON)
```json
{"date": "2026-03-18", "project": "dotfiles", "files": 5, "findings": 3, "severity": {"critical": 0, "warning": 2, "info": 1}, "reviewers": ["code-reviewer", "codex-reviewer"]}
```

### 使い方
1. レビュー完了後、上記フォーマットで結果を追記
2. AutoEvolve が定期的に分析し、頻出パターンを rules/ に反映
3. `/review` 実行時に過去の指摘傾向を参考にフォーカスエリアを調整

## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | レビューアーを直接 Skill ツールで起動する | Agent ツールで1メッセージに並列起動する |
| 2 | 行数だけでスペシャリストを判断する | コンテンツシグナルも分析して選定する |
| 3 | レビュー結果をそのまま列挙する | 統合・重複排除して構造化する |
| 4 | 10行以下の変更に対してフルレビューを実行する | Verify のみで十分 |
| 5 | findings の保存を省略する | `review-findings.jsonl` に保存してフィードバックループを維持する |

## Gotchas

- **staged vs unstaged の混同**: `git diff --cached` はステージ済みのみ、`git diff` は未ステージのみ、`git diff HEAD` は両方を含む。レビュー対象に応じて使い分けること
- **レビュアー起動の順序依存**: Agent ツールで並列起動する際、全レビュアーを1メッセージにまとめないと逐次実行になる
- **言語チェックリストの Read 忘れ**: code-reviewer にチェックリストを注入し忘れると、汎用レビューしか行われない。Step 2 の言語判定を省略しないこと
- **信頼度フィルタの閾値**: confidence 80未満のフィルタが厳しすぎると、有効な指摘も消える。初回は閾値なしで実行し、ノイズを見てから調整
- **codex-reviewer との重複**: code-reviewer と codex-reviewer が同じ指摘をすることがある。Synthesis ステップで重複排除すること

## Skill Assets

- 統合レポートテンプレート: `templates/synthesis-report.md`
- diff 統計抽出: `scripts/extract-diff-stats.sh` — `sh scripts/extract-diff-stats.sh [ref]` で JSON 出力
