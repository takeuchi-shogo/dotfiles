---
source: "https://x.com/leopardracer/status/2108142806451507542 (画像内プロンプト, 作者 @quantprimate)"
date: 2026-10-09
status: integrated
family: none
---

<!--
family は Phase 1.5 で agentic-instruction-following と agent-runtime-state のどちらとも読めたため、
topic-family-saturation.md の「判断が割れたら分類しない」に従い none とした。
-->

## Source Summary

**主張**: Opus 5.5 を「24/7 クオンツ調査デスク」として長時間動かすための XML 構造化プロンプト。
ツイートは「Andrej Karpathy が公開した」と書くが、画像下端に "Prompt by @quantprimate" とあり、
Karpathy とは無関係。顔写真と肩書きで本人作に見せる構成になっている。元記事
"How to Build a 24/7 Quant Trading Desk with Opus 5.5 (FULL GUIDE)" は、パイプラインは未構築、
実売買なし、成績は未再現と自ら書いている。

**手法** (クオンツ固有の layer_2/3 を除く汎用部分):
- T1 証拠のない値は `unknown` / `not_calculated` と明示する (layer_5_review)
- T2 "Prose alone is not a boundary" — tool rules / sandbox で強制する (layer_4)
- T3 publish / send / spend の前に確認する (layer_4)
- T4 危険な変更の前に復元可能な版を残す (layer_4)
- T5 別 reviewer が checks.md に pass/fail と修正リストを残す (layer_5)
- T6 最小 effort で始め、曖昧な判断だけ深くする。設定比較は同一タスク・同一 acceptance checks で (layer_6)
- T7 completion checklist の各項目に観測可能な証拠を付ける。詰まったら partial で返す (layer_7)
- T8 progress.md と workspace に残ったファイルの一致を確認する (layer_7)
- T9 保存状態を見て bounded step を 1 つ進め、checkpoint、LIMIT で止まるループ (execution_loop)
- T10 新しい理由なしに同じ失敗アプローチを繰り返さない (execution_loop)
- T11 handoff ノート: Task / Outputs / Completed / Decisions / Open issues / Next action (handoff)
- T12 delivery で checked / passed / unresolved を述べ、結果を prompt から推測しない (delivery)

**根拠**: なし (テンプレートの提示のみ。効果の測定や事例はない)

**前提条件**: 単一エージェントが長時間・多段で調査パイプラインを組む用途

## Gap Analysis (Pass 1: 存在チェック)

Pass 1 は Sonnet Explore。T3 / T4 は Opus が Pass 2 で、Phase 2.5 の Codex 指摘を受けて判定を変えた。

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| T1 | unknown ラベル | Partial (低優先) | CLAUDE.md:108「未確認と明示」は会話上の断定のみ。ただし `commands/security-review.md:211-229` の Coverage `unknown`、`skills/edge-case-analysis` の証拠分類が必要な場面には入っている |
| T3 | publish/send/spend 前の確認 | Already | `references/cli-discovery.md:49` の external side-effect ティア (明示承認)。spend は該当操作面なし |
| T4 | 復元可能な版 | Already | 本体の checkpoint/rewind + worktree+PR 運用。外部副作用が戻せない点は `skills/checkpoint/SKILL.md` Anti-Patterns に既記載 |
| T6 | 同一条件での設定比較 | Partial | `references/model-routing.md:101-109` の effort 表はあるが、比較手順の規定はない。skill-audit の A/B で足りるため不採用 |
| T8 | progress と workspace の一致 | Partial | `resume-anchor-lint` は形のみ検査と契約に明記 (意図的)。意味の一致検査は誤検知が大きい |
| T11 | handoff スキーマ | Partial | checkpoint HANDOFF に「未検証・未解決」欄がない。escalation スキーマには 3.7 検証済み事実 / 未検証仮説がある |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | CLAUDE.md:23 Static-checkable → mechanism (T2) | 同じ原則 | なし | 強化不要 |
| S2 | code-reviewer Verdict 契約 + review findings 永続保存 (T5) | checks.md というファイル名 | 複製不要 | 強化不要 |
| S3 | completion-gate + verification-before-completion (T7) | 項目ごとの証拠リンク | Codex は残差と指摘。Success Criteria は機械検証可能と規定済みで追加しない | 強化不要 |
| S4 | ralph-loop / blueprint の max_iterations (T9) | tools budget | iteration 上限で足りる | 強化不要 |
| S5 | resource-bounds.md Doom-Loop Recovery (T10) | 同じ原則 | なし | 強化不要 |
| S6 | output-modes「何を検証し、何が通り、何が落ちたか」(T12) | 同じ原則 | なし | 強化不要 |

## Phase 2.5

- Codex (gpt-5.6-terra, xhigh, read-only, `project_doc_max_bytes=0`) の結論行 (verbatim):
  `VERDICT: 既存アンカーに「status・evidence path・unknown」を最小追加し、progress.md/checks.md は採用しない`
  - T3 を N/A → Already (cli-discovery.md:43-50)。T6 を Already → Partial。T1/T8 は低優先。残差は HANDOFF の Decisions/Evidence/Unresolved 契約の弱さ
  - T4 の Partial 指摘は不採用。根拠に挙げた checkpoint SKILL.md:170-172 自体が残差をカバーしている
- Gemini (agy, grounding): 出典は文書名のみで URL なし。採用した指摘は 2 点
  - unknown を許すと導出可能な値まで放棄する怠けの逃げ道になる (T1 を一般ルール化しない根拠)
  - 進捗 Markdown より git commit / テスト状態を正にする代替 (HANDOFF の Context Files は既に git 由来)

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| T11 | checkpoint HANDOFF に `## Unresolved` 節 | 採用 | escalation スキーマの 3.7 に揃える。What Didn't Work (試して失敗) と未検証 (まだ確かめていない) は別情報 |
| T1 | unknown ラベルの一般ルール化 | スキップ | 必要箇所 (security-review Coverage 等) に既存。一般化は逃げ道になる (Gemini) |
| T6 | 設定比較の手順 | スキップ | skill-audit A/B で足りる |
| T8 | progress と workspace の一致検査 | スキップ | 形のみ検査は意図的な設計。意味検査は誤検知大 |

## Plan (実施済み)

### Task 1: checkpoint HANDOFF スキーマに Unresolved 節 (S)
- **Files**: `.config/claude/skills/checkpoint/SKILL.md`, `.config/claude/commands/checkpoint.md`, `scripts/lifecycle/resume-anchor-lint.sh`, `.config/claude/references/resume-anchor-contract.md`
- **Changes**: テンプレート 2 コピーに節を追加、lint の CHECKPOINT_SECTIONS に追加、contract の表と重点説明を更新

### Validation-only Follow-up (Codex Review Gate で発見)
- `resume-anchor-lint.sh` の hollow 判定がテンプレート注記「（なければ「特になし」）」を中身として数えていた。
  未編集のテンプレートのまま `What Didn't Work` が `ok` になる既存バグ。注記の完全一致除去で修正
  (汎用パターン `（なければ[^）]*）` は本文の括弧書きまで消すため Codex が差し戻し → 完全一致に変更)
- Review Gate 判定 (verbatim): 1 回目 `VERDICT: NEEDS_FIX` → 2 回目 `VERDICT: NEEDS_FIX` → 3 回目 `VERDICT: PASS`
- 範囲外として残したもの: 見出しの前方一致 (`## Unresolved Notes` も受理)、節の順序未検査。既存 6 節すべて同じ設計
