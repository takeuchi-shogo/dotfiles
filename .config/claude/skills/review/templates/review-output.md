# Review Output Template

レビュー結果の統合出力フォーマット。Step 4 (Synthesis) で使用する。

---

## 出力フォーマット

```markdown
## レビュー結果

**変更概要**: {変更行数}行 / {ファイル数}ファイル / {言語リスト}
**レビューアー**: {起動したレビューアーのリスト}
**除外**: {n} 件 (low-confidence {a} / outside-diff {b} / linter-duplicate {c} / reviewer {k}) / unknown: {reviewer 名 or none}

### Critical（修正必須）

- **[{score}]** **[{レビューアー名}]** `{file}:{line}` — {指摘内容}
  → {推奨修正}

### Important（検討推奨）

- **[{score}]** **[{レビューアー名}]** `{file}:{line}` — {指摘内容}
  → {推奨修正}

### Suggestion（参考）

> confidence ≥ 80 の指摘のみ表示。

（該当する指摘がある場合のみ表示）

### Watch（要注意 — 参考情報）

> confidence 60-79 の指摘。判定 (PASS/NEEDS_FIX/BLOCK) には影響しない。
> フィードバックにより将来の閾値調整に活用される。

- **[{score}]** **[{レビューアー名}]** `{file}:{line}` — {指摘内容}
  → {推奨修正}

（該当する指摘がある場合のみ表示）

### 判定

{PASS / NEEDS_FIX / BLOCK}

- **PASS**: Critical・Important の指摘なし。Watch のみ、または指摘なし
- **NEEDS_FIX**: Important が3件以上。修正後に再レビュー推奨
- **BLOCK**: Critical が1件以上。修正必須
```

## 統合ルール

### 重複排除

同じファイル・行への指摘が複数レビューアーから上がった場合:

1. 最も具体的な指摘を残す（「問題がある」より「NullPointerException の可能性」）
2. 重要度が異なる場合は高い方を採用
3. 排除された指摘は「(他 N 件のレビューアーも同様の指摘)」と注記

### 重要度マッピング

各レビューアーの出力を統一的な重要度にマッピングする:

| レビューアーの表現                       | 統合後の重要度 | スコア条件 |
| ---------------------------------------- | -------------- | ---------- |
| MUST, Critical, CRITICAL, 90-100         | **Critical**   | ≥90        |
| CONSIDER, Important, HIGH, 80-89         | **Important**  | ≥80        |
| NIT, ASK, FYI, Watch, MEDIUM, 60-79     | **Watch**      | ≥60        |
| （60未満はフィルタ済みのため出力しない） | —              | <60 除外   |

> **ASK/FYI の扱い**: `ASK`（設計意図の質問）と `FYI`（参考情報）は修正を要求しないため、
> スコアに関わらず **Watch** にマッピングする。判定（PASS/NEEDS_FIX/BLOCK）には影響しない。

### 除外の集計

`**除外**:` 行は 0 件でも省略しない。`## Filtered` 節を出力契約に持つ reviewer (code-reviewer / codex-reviewer) ごとに、
節に行あり → その件数、`(none)` → 0、節なし → `unknown` に名前を出す。unknown を 0 に寄せない。
契約に節を持たない reviewer は数えず、unknown にも載せない。中身の保存は `references/findings-and-feedback.md` Step 6。

### 指摘がない場合

```markdown
## レビュー結果

**変更概要**: {変更行数}行 / {ファイル数}ファイル / {言語リスト}
**レビューアー**: {起動したレビューアーのリスト}
**除外**: {n} 件 (low-confidence {a} / outside-diff {b} / linter-duplicate {c} / reviewer {k}) / unknown: {reviewer 名 or none}

指摘なし。

### 判定

PASS
```
