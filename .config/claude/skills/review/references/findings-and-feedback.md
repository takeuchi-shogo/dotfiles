# /review skill — Findings & Feedback Loop 詳細

`/review` skill の Step 6 (Findings Persistence) / Step 6.5 (Explicit Feedback) /
Step 7 (Review Quality Feedback) / Data Storage の詳細実装。
SKILL.md からは要約と本ファイルへの参照のみ残し、詳細フローはここで定義する。

---

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

---

## Step 6.5: Explicit Feedback Collection（指摘精度の明示的フィードバック）

verdict が **NEEDS_FIX** または **BLOCK** の場合のみ実行する。
PASS の場合はこのステップをスキップして Step 7 に進む。

### 目的

レビュー指摘の精度（false positive 率）を追跡するため、ユーザーに各指摘の受入/却下を確認する。
収集したデータは meta-analyzer → AutoEvolve Improve でレビューアープロンプトの改善に活用される。

### フロー

1. Step 6 で保存した findings のうち、Critical/Important の指摘を番号付きリストで表示する
2. AskUserQuestion でバッチ回答を求める
3. 回答を解析し `update_finding_outcome()` で review-findings.jsonl を更新する
4. 回答がない場合（Enter のみ）は全指摘を `deferred` として記録する

### 表示フォーマット

```
## Review Findings Feedback

以下のレビュー指摘について、accept（修正する/妥当）/ reject（誤検知/不要）/ partial（部分的に対応）/ deferred（後で判断）を回答してください。

バッチ形式で回答できます: "1-3: accept, 4: reject, rest: deferred"
Enter のみで全て deferred になります。

1. [rf-2026-04-07-001] `api.go:42` — エラーが握り潰されている (code-reviewer, confidence: 95)
2. [rf-2026-04-07-002] `handler.go:83` — nil チェック漏れ (codex-reviewer, confidence: 88)
3. [rf-2026-04-07-003] `service.go:120` — 排他制御が不足 (code-reviewer, confidence: 72)
```

### 回答の解析と記録

ユーザーの回答を Bash + Python で解析し、各指摘に outcome を設定する:

```bash
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts/lib')
from session_events import update_finding_outcome
import re

response = sys.argv[1]
finding_ids = sys.argv[2:]  # rf-2026-04-07-001 rf-2026-04-07-002 ...

if not response.strip():
    for fid in finding_ids:
        update_finding_outcome(fid, 'deferred', 'explicit')
    print(f'{len(finding_ids)} findings marked as deferred')
    sys.exit(0)

# Parse batch format: '1-3: accept, 4: reject, rest: deferred'
assignments = {}
for part in response.split(','):
    part = part.strip()
    m = re.match(r'(\d+)(?:-(\d+))?\s*:\s*(accept|reject|partial|deferred)', part)
    if m:
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
        outcome = m.group(3)
        for i in range(start, end + 1):
            assignments[i] = outcome
    elif re.match(r'rest\s*:\s*(accept|reject|partial|deferred)', part):
        rest_outcome = re.match(r'rest\s*:\s*(\w+)', part).group(1)
        for i in range(1, len(finding_ids) + 1):
            if i not in assignments:
                assignments[i] = rest_outcome
    elif re.match(r'all\s*:\s*(accept|reject|partial|deferred)', part):
        all_outcome = re.match(r'all\s*:\s*(\w+)', part).group(1)
        for i in range(1, len(finding_ids) + 1):
            assignments[i] = all_outcome

updated = 0
for i, fid in enumerate(finding_ids, 1):
    outcome = assignments.get(i, 'deferred')
    if update_finding_outcome(fid, outcome, 'explicit'):
        updated += 1
print(f'{updated}/{len(finding_ids)} findings updated')
" "{user_response}" {finding_id_1} {finding_id_2} ...
```

### ルール

1. **CONSIDER/Watch 指摘は表示しない**: auto_diff（git commit 時の hook）に委ねる
2. **10件超の場合**: 「MUST のみ表示、残りは auto_diff に委ねます」と案内する
3. **explicit 優先 (R-05)**: ここで記録した outcome は、後の auto_diff で上書きされない
4. **Review-Fix サイクルとの関係**: Step 6.5 は Step 6 の直後に実行する。ユーザーが reject した指摘も Step 5 の修正サイクルには影響しない（修正判断は verdict ベース、フィードバックは精度追跡用）

---

## Step 7: Review Quality Feedback（オプション）

レビュー完了後、ユーザーにレビュー品質のフィードバックを求める。
収集したフィードバックは AutoEvolve の改善サイクルに入力される。

**出力**（合成レポート末尾に追加）:

```
## Review Quality
このレビューは役立ちましたか？ 気になる点があればコメントしてください。
（フィードバックは review-feedback.jsonl に記録され、レビュー品質の改善に活用されます）
```

**フィードバック記録**:
ユーザーからフィードバック（「的外れだった」「Xの指摘が良かった」等）があった場合、
`~/.claude/skill-data/review/review-feedback.jsonl` に記録する:

```json
{"date": "YYYY-MM-DD", "project": "myapp", "feedback": "positive", "detail": "cross-file の影響検出が有用", "reviewer": "cross-file-reviewer"}
```

- 明示的なフィードバックがあった場合のみ記録（毎回質問で中断しない）
- AutoEvolve の `review-comments` カテゴリ（`improve-policy.md`）で改善に活用

---

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
