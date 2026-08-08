# Review Consensus Policy

レビューアー間の合意形成・対立解消・外れ値処理のポリシー。
review SKILL.md Step 4 (Synthesis) から参照される。

## Section 0: Finding 出力契約

統合側 (Synthesis) が要求するスキーマをここで定義する。レビューアーごとの語彙は
各 agent 定義に残したまま、統合の入口でこの表に写す。

### canonical severity

verdict 計算が使う値は **Critical / Important / Watch** の 3 つだけ (Section 7 の
severity_multiplier と同一)。各レビューアーの表記はここで写す。

| レビューアー表記 | canonical | 出典 |
|-----------------|-----------|------|
| `MUST` / `CRITICAL` / `critical` / `必須` / 🔴 Critical / 🔴 Must Fix | **Critical** | code-reviewer, security-reviewer, silent-failure-hunter, test-analyzer, product-reviewer, design-reviewer, simplify |
| `HIGH` | **Critical** | security-reviewer, silent-failure-hunter (セキュリティの HIGH は BLOCK 相当として扱う) |
| `CONSIDER` / `consider` / `SHOULD` / `MEDIUM` / `important` / `Important` / `重要` / 🟡 Warning / 🟡 Should Fix / 「問題点 (修正推奨)」 | **Important** | code-reviewer, security-reviewer, test-analyzer, product-reviewer, design-reviewer, simplify, type-design-analyzer |
| `NIT` / `ASK` / `FYI` / `LOW` / `Watch` / `推奨` / `参考` / 🔵 Suggestion / 🔵 Consider / 「改善提案 (optional)」 | **Watch** | code-reviewer, security-reviewer, test-analyzer, product-reviewer, design-reviewer, simplify, type-design-analyzer |
| `PLAN` (Plan 批評) / `RETRACTED` (撤回済み) | **severity ではない** → `severity` 欄に入れず `status` 欄に入れる。canonical severity は別途付ける | codex-plan-reviewer, 撤回運用 |

表に無い値が来たら canonical に写さず `[UNMAPPED SEVERITY: <値>]` を付けてレポートに残し、
**verdict 計算には乗せない**。写せない値を勝手に Critical/Important に寄せてはいけない。

`PLAN` (codex-plan-reviewer の Plan 批評) と `RETRACTED` (撤回済み) は severity ではない。
severity 欄に入れず `status` 欄に入れる。

### confidence_kind

confidence は 1 種類ではない。統一せず種別を区別する。

| kind | 意味 | 数値フィルタ |
|------|------|-------------|
| `subjective` | レビューアーの自己申告確度 0-100 (code-reviewer, cross-file-reviewer, edge-case-hunter) | Section 2 の閾値を適用する |
| `evidence` | Source / Control / Sink・Reachability・Counterevidence・Proof 欄の充足で決まる (security-reviewer、`agents/security-reviewer.md:188`) | **適用しない**。証拠充足型の finding を数値で落としてはいけない |

### 欠落時の扱い

- severity 欠落 / canonical に写せない → `[UNMAPPED SEVERITY]` を付けて残し、verdict 計算から除外
- confidence 欠落 (kind も不明) → `[UNSCORED]` を付けて残し、verdict 計算と自動修正の入力から除外
- どちらも「情報は保持、判定には使わない」。Section 6 の `[OUTLIER]` と同じ扱いにする
- **欠落を黙って 0 や Watch に丸めない**。丸めると欠落が観測できなくなる

### 終端マーカー

各レビューアーは出力の末尾に `Coverage: complete | partial | unknown` を必ず置く
(`agents/security-reviewer.md:185` が既にこの形)。dispatch したレビューアーのうち
このマーカーを返さなかったものがあれば、そのレビューは完走したと見なせない。
判定は SKILL.md Step 4 の Layer 0 に置く。

### 書き込み時の検証

`review-findings.jsonl` への書き込みは `scripts/lib/session_events.py` の
`emit_review_finding()` が canonical severity / location / confidence_kind を検証し、
違反を **例外で拒否**する。正規化して書かない。

> 背景: 検証を入れる前の実測で `review-findings.jsonl` 157 件のうち severity 欠落 121 件
> (77%)、残り 36 件が 15 値に散っていた。`append_to_learnings` が検証せず書くため、
> 欠落が無言で通り続けた。

## Section 1: セマンティック重複排除

同一ファイル ±10行以内 AND 同一 failure_mode の指摘を1件に統合する。

- 統合時は最高 confidence のレビューアーの指摘を代表とする
- 統合元は「(他 N 件のレビューアーも同様の指摘)」と注記
- ±10行の判定は diff の行番号基準（ファイル全体の行番号ではない）

## Section 2: 合意の扱い (confidence は加算しない)

複数のレビューアーが同一問題を指摘した場合、**合意は優先順位の補助にのみ使う**。

- `agreeing_reviewers` を finding に記録し、Section 7 の並び順で同 `effective_weight` の
  タイブレークに使う
- **confidence 値そのものを加算しない**。閾値 (下記) の判定には各レビューアーの元の値を使う
- 数値フィルタは `confidence_kind = subjective` の finding にのみ適用し、閾値は 60 とする
  (`confidence < 60` を除外)。`evidence` 型と `[UNSCORED]` は Section 0 の規定に従う

> 理由: 加算式 (旧 `max(scores) + 5 * (agreeing - 1)`) は、同じ diff・同じ注入プロンプト・
> 似た rubric を読むレビューアーを独立試行として扱っていた。相関した誤検知を増幅するため、
> 合意を確度の根拠に使うのをやめる (2026-08-06 Codex 批評)。

## Section 3: 対立検出と解消

同一箇所で矛盾する指摘が出た場合:

1. 両方残して `[CONFLICT]` タグを付与
2. 各レビューアーの capability_score で重み付けし、高い方を「推奨」とする
3. 重み差が 2x 以上 → 高い方を採用、低い方を「参考」に格下げ
4. 重み差が 2x 未満 → 両方残して verdict は `NEEDS_HUMAN_REVIEW`

## Section 4: Codex 指摘の必須対応

codex-reviewer の指摘は特別扱い:

- `[DEEP_REASONING]` タグを常時付与
- Critical/Important は個別に対応を明記
- 「他レビューアーが指摘していない」は無視の理由にならない
- verdict 計算から除外してはならない
- Outlier 判定の対象外

## Section 5: 収束停滞検出

以下のいずれかで `[CONVERGENCE STALL]` → verdict を `NEEDS_HUMAN_REVIEW` に:

| 条件 | 閾値 |
|------|------|
| Critical 矛盾 | 2+ レビューアが同一箇所で PASS vs BLOCK |
| Verdict 分裂 | PASS と NEEDS_FIX が同数 |
| 低合意率 | Agreement Rate < 70% |

Agreement Rate の算出:

```
agreement_rate = 1 - (conflict_count / total_findings)
```

- conflict_count: 同一ファイル ±5行で矛盾する指摘の組数
- 全レビュー構成で実施（3-way に限定しない）

## Section 6: 外れ値検出

codex-reviewer **以外** のレビューアーを対象に:

1. 他レビューアーとの指摘重複率 < 20%
2. AND 指摘数が平均の 3x 以上

→ `[OUTLIER]` タグを付与し verdict 計算から除外（情報は保持）

codex-reviewer は常に `[DEEP_REASONING]` として verdict に含める。

## Section 7: Capability-Weighted Synthesis

全レビュー構成（2体以上）で適用:

```
effective_weight = capability_score[reviewer][domain] × severity_multiplier
```

severity_multiplier:
- Critical: 3
- Important: 2
- Watch: 1

同一指摘が複数レビューアーから出た場合は重みを合算。
合成レポートの指摘一覧を effective_weight 降順でソートする。

capability_score の値は `reviewer-capability-scores.md` を参照。
