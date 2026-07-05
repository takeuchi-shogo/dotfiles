---
source: "https://zenn.dev/dk_/articles/1f3fbc506827ac"
date: 2026-07-06
status: analyzed
family: self-evolving
adopted: 2
---

## Source Summary

**記事**: Zenn (dk_)「Claude Code Skills でプロジェクト固有の開発フローを強制し自己改善ループを組み込む」

**fetch_metadata**: route=defuddle (C1 オーバーライド、Zenn は trusted 外), received_bytes=19114, trusted=false

**主張**: superpowers プラグインの汎用 skill をプロジェクト固有 skill (dev-flow オーケストレーター) でラップし、開発フロー強制と自己改善ループ (学習抽出 → docs/learnings/) を両輪で回す。

**手法**:
1. dev-flow 規模判定オーケストレーター (小/中/大 → skill チェーン切替)
2. 実装前 ADR 確認 + 中大規模で ADR 作成を強制
3. Adversary モードレビュー (別コンテキストの subagent に「承認ではなく否定から入れ」と指示)
4. test/lint/build の証拠を必須化
5. code-review skill 内で学習を抽出し docs/learnings/*.md に書き、次セッションで参照する
6. PR テンプレートを create-pr で強制
7. 他人 PR 用に Blocking/Important/Minor/LGTM の4段階判定
8. CLAUDE.md 直書きを避け、学びは docs/learnings/ に分離する
9. 自己改善ループはシングルスレッド逐次実行が良い (並列だと学びが捨てられる)
10. REQUIRED SUB-SKILL 宣言で superpowers を参照する

**根拠**: 著者の実プロジェクト運用経験。定量データはなし。

**前提条件**: 単一開発者または小チームでの Claude Code 運用、superpowers プラグイン導入済みが前提。

## Phase 1.5 Saturation Gate

- family: self-evolving (taxonomy 4 族に未登録だが、過去 absorb がこの family として運用されており fable5-14steps 時点で N=10+)
- 直近3件: opik (採用0, light-phase2-only) / fable5-14steps (採用あり, implemented) / sonicgarden (採用2, implemented)
- 採用率 20% 以上 → **PASS (warning)**。連続 reject の傾向はない
- Stale-Plan Audit: 直近2件は implemented 済み、opik は 30日未満のため audit 不要

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 規模判定オーケストレーター | Already | CLAUDE.md ワークフロー表 + workflow-guide.md の多因子判定が、記事の dev-flow より精緻 |
| 2 | 実装前 ADR 確認・作成 | Partial | docs/adr/ 8件 + /decision skill は存在するが、workflow-guide.md「Plan 前の必須チェック」に docs/adr 参照がない (grep で確認) |
| 3 | Adversary モードレビュー | Already | code-reviewer.md:451 に Blind-first Pass 1 + Confirmation Bias 検出 + coldness bias ガードを実地確認済み |
| 4 | 検証証拠の強制 | Already | completion-gate.py (Stop hook) + superpowers:verification-before-completion の二重強制 |
| 5 | code-review 内学習抽出 | Already | review skill が emit_review_finding → learnings/*.jsonl → promote-learnings 昇格ループを備える |
| 6 | PR テンプレート強制 | Already | commands/pull-request.md Step 0 でテンプレート必須反映 |
| 7 | 他人 PR 4段階判定 | Already | code-reviewer の MUST/CONSIDER/NIT/FYI + PASS/BLOCK が機能等価。built-in /review <PR#> が他人 PR をカバーする |
| 8 | CLAUDE.md 直書き回避 | Already | ADR-0007 (thin CLAUDE.md) + claudemd-size-check hook + memory-schema の多層保護 |
| 9 | シングルスレッド逐次論 | N/A | cmux hub-and-spoke conductor 統合を意図的に採用済み。学習抽出は hook 層 (session-learner) で全セッション横断のため、「並列だと学びが捨てられる」という前提が構造的に成立しない |
| 10 | REQUIRED SUB-SKILL ラップ | Already | agents frontmatter の skills: + workflow-guide の superpowers 参照で実践済み |
| 11 | grill-me の実装前フロー配線 (ユーザー提案、記事外) | Partial | grill-interview skill (grill-me のローカル適応版) は存在するが、M/L フローに未配線。統合事例は design-md-init のみ |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S3 | code-reviewer.md の Blind-first Pass 1 | 記事の「否定から入れ」という Adversary フレーミング | Confirmation Bias 検出を否定優先型に寄せる | 強化不要 (記事の提案は coldness bias ガードおよび agency-safety-framework.md:159 と衝突し、採用は設計退化) |
| S10 | REQUIRED SUB-SKILL 宣言 | /rpi・/epd への参照が薄い | superpowers 参照を /rpi・/epd に追加 | 強化不要 (記事に裏付けなし、Sonnet imagination として除外) |

Sonnet が提案した「自動規模判定 hook」(#1 関連) も記事に根拠がなく、同様に除外した。

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 2 | 実装前 ADR 確認 | 採用 | workflow-guide.md に docs/adr 照合が欠けていると Codex が確認。ただし全 M/L 強制は過大なため、harness/architecture/workflow 変更時の照合に限定する |
| 11 | grill-me 配線 | 採用 | Codex 提案どおり全 M/L 必須化はせず、Codex Gate の任意ステップとし、ADR 追加・workflow 変更・不可逆判断の場面で推奨する |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|---|---|---|
| S3 | Adversary モードレビュー | スキップ | 既存の coldness bias ガードと衝突し、強化ではなく設計退化になる |
| S10 | REQUIRED SUB-SKILL 拡張 | スキップ | 記事に根拠なし。/rpi・/epd への追加提案は Sonnet の hallucination |

## Phase 2.5 Refine

**Codex (gpt-5.5, xhigh→high)**: 1回目の `codex exec` バックグラウンド呼び出しがサイレント失敗した (出力0バイト、feedback_codex_bash_tool_unreachable の既知パターン)。cmux 不在で launch-worker.sh は exit 1 のため、短縮プロンプト + stderr 可視の `codex exec` 直呼びでリトライし成功した。

批評内容:
- #2 は実益があるが、全 M/L 強制は過大。harness/architecture/workflow 変更時の照合に限定し、reversible-decisions.md / pre-mortem-checklist.md との重複を避ける
- #11 は全 M/L 必須化せず、Codex Gate の任意ステップとし、ADR 追加・workflow 変更・不可逆判断で推奨にとどめる
- #3 の不採用を追認する。「強化ではなく設計退化」
- 優先度: P1 = #2、P2 = #11

**Gemini**: 実行不可 (IneligibleTierError — individuals sunset、2026-07-05 再確認)。Codex 単独批評で代替した。他プロジェクトの事例や代替手法など、Gemini 側で得られたはずの周辺知識はこのレポートに含まれない。

## Phase 3 Triage

ユーザーは #2 + #11 の両方を採用した (multiSelect)。

不採用確定: #3 (設計衝突)、#9 (deliberate non-adopt)。他は Already。

## Plan

### Task 1: workflow-guide.md に ADR 照合を追記
- **Files**: `.config/claude/references/workflow-guide.md`
- **Changes**: 「Plan 前の必須チェック」節に、harness/architecture/workflow 変更時は docs/adr/README.md を照合する一文を追加
- **Size**: S

### Task 2: workflow-guide.md に grill-interview 推奨ステップを追記
- **Files**: `.config/claude/references/workflow-guide.md`
- **Changes**: 「1.5. Codex Gate」節の末尾に、grill-interview を任意ステップとして追加。ADR 追加・workflow 変更・不可逆判断の場面で推奨する旨を明記
- **Size**: S

実施済み。ブランチ: `feat/absorb-dk-devflow-adr-grill` (worktree)。

## ユーザー起点の観点

- ユーザーの見立て「プラグイン利用が良さそう」→ superpowers はすでに導入・参照済みで、記事の骨格は実践されていると確認した
- ユーザーの見立て「grill-me を合わせると良くなる」→ #11 として採用し、記事外のユーザー提案を absorb に合流させた
