---
date: 2026-08-31
status: implemented
source: https://www.pospome.work/entry/2026/08/24/223309
author: pospome (カミナシ VPoE)
title: 優秀なエンジニアが書く Design Doc は何が違うのか?
family: design-doc-review (新設, N=1)
adopted: 4

# pospome「優秀なエンジニアが書く Design Doc は何が違うのか?」absorb 分析

## Source Summary

Design Doc は「開発前に不確実性を可視化 & 排除する」もの。完璧な設計は必須ではなく、
どこまで詰めるかは開発対象に依存する。レビュー時に見るのは 3 点:

1. **代替案** — 採用しなかった選択肢とトレードオフの言語化。引き出しの多さが分かる
2. **懸念点** — 2 種類ある。(a) 決めたが不安が残るもの (b) 分からないから助けてほしいもの。思考の深さが分かる
3. **未決定事項** — 「なぜ今は決めないか」「いつ誰が決めるか」を明記。承認後にチケット化。
   リードタイム短縮 + タスク漏れ防止。不確実性を左右するポイントの嗅覚が分かる

記載量の多寡ではなく、対象に応じて何をどう言語化するかが要。

取得経路: `defuddle` (C1 オーバーライド、WebFetch の Haiku 要約を回避)。

## Phase 1.5: Saturation Gate

taxonomy 4 族いずれにも非該当 (harness 0 / hook 0 / obsidian 0 / tips 0 hit)。
`docs/research/_index.md` に Design Doc レビュー観点の absorb 実績なし。N=0 → **PASS (新分野)**。
family `design-doc-review` を N=1 として記録する。

## Phase 2 → 2.5 判定 (Codex 批評で 4 箇所修正)

Gemini は `IneligibleTierError` を 2026-08-31 に再確認 → **Phase 2.5 は Codex 単独 = degraded**。
Codex は `gpt-5.6-terra` が `requires a newer version of Codex` で 400 を返したため `gpt-5.5` (xhigh) で実行。

| # | 手法 | 初回 | 最終 | 根拠 |
|---|------|------|------|------|
| — | 設計時にユーザーに考えさせる | Gap | **Gap (最重要)** | `grill-interview` は `disable-model-invocation: true` + workflow-guide 上も任意。通常 M/L では割り込みが 0 |
| 5 | 未決定事項 | Gap | **Gap** | 断片的な `lifecycle: deferred` はあるが design-time の first-class ではない。`spec` の Open Questions は「実装前に解決が必要」で意味が逆 |
| 2-3 | 代替案 | Partial | Partial (**根拠訂正**) | 「置き場が無い」は誤り。`workflow-guide.md:238` に `決定/代替案/却下理由/影響範囲` が実在。真因は二重定義 drift + **ADR 8/8 件で記載ゼロ** |
| 4 | 懸念点の 2 分類 | Partial | Partial (**根拠訂正**) | 「置き場が無い」は誤り。`pre-mortem-checklist.md` が Known/Assumptions/High-impact unknowns/Blind spots + 5 項目でカバー。欠落は 2 分類の分離のみ |
| 1 | 不確実性の可視化 | Already | **Partial に降格** | pre-mortem が別 reference に逃げており PLANS.md の required ではない |
| 6 | 「何年持つか」逆算 | N/A | **翻訳可** | 個人 harness にスケール逆算は不適だが Build to Delete / 撤回条件に対応 |
| 7 | 対象依存の言語化 | Already | **Already 維持** | Codex の降格提案 (S/M/L はサイズ分類) は `reversible-decisions.md` の可逆性 gate 見落としのため退けた |

### Codex の中核指摘 (verbatim)

> 人間が Design Doc を書く前提では、空欄は思考を促します。AI が書く前提では、空欄はもっともらしく埋められます。
> したがって翻訳すべき点は「書式」ではなく「割り込み」です。

> 必要なのは、AI に全部書かせた後でレビューする仕組みではなく、Plan 確定前に AI が自分で決めてはいけない判断を
> 1-3 個だけユーザーへ戻す仕組みです。特に「価値判断」「不可逆」「後で高くつく」「複数案が同程度」のものだけ聞く。
> 全部聞くと運用が死にます。

Codex は「PLANS.md に大きな新セクションを足す案は推しません。AI が埋めて終わるだけです」とも述べ、
grill-interview / decision の強化 + PLANS.md は薄い接続のみを推奨した。この方針を採った。

## 採用 4 件 (全 S、実装済)

| T | ファイル | 内容 |
|---|---------|------|
| T1 | `.config/claude/references/workflow-guide.md` | `### 1.4. Design Gate` を Codex Gate の直前に新設。M/L で Plan 確定前に **最大 3 件だけ** `AskUserQuestion` でユーザーに戻す。選定条件は 価値判断 / 不可逆 / 後で高くつく / 複数案が同程度。0 件なら質問せず判断を Plan に 1 行残す。質問軸を記事の 3 本柱に対応づけ、Plan の書き戻し先を明示 |
| T2 | `docs/adr/template.md` | `## Rejected Alternatives` を追加 (代替案 / 却下理由 / 再検討の条件)。既存 8 件への遡及記入はしない |
| T3 | `PLANS.md` | `## Decision Log` を `重要な判断と理由` の 1 行から `決定 / 代替案 / 却下理由 / 残る懸念 / 延期事項` のテーブルに変更し、`workflow-guide.md:238` と一本化 (instruction DRY 違反の解消) |
| T4 | `.config/claude/skills/decision/SKILL.md` | `残る懸念` (決めたが不安) と `延期判断` (何を/なぜ今決めない/いつ誰が) を任意欄として追加 |

強制力は**ユーザー判断で instruction のみ** (hook 化はしない)。
長い instruction はターン距離とともに減衰する (arXiv:2607.25398, absorb 済) ため、発火しない日が出うる点は承知の上。

## 副産物: 既存の配線 drift を 1 件検出・修正

`workflow-guide.md:338` は「Codex Gate の前に `/grill-interview` でプランをストレステストする」と
**Claude 自身が実行する書き方**をしていたが、`grill-interview/SKILL.md` は `disable-model-invocation: true` で
セッションの skill 一覧に載らず、Claude からは起動できない。到達不能な skill を名指す instruction だった。

T1 の一部として「ユーザーに `/grill-interview` の実行を促す (自分で呼ぼうとしない)」に修正した。

教訓: **記事が「AI に決めさせるな」と言ったので配線を見に行ったら、そもそも呼べない skill を呼べと書いてあった。**
`feedback_dormant_artifact_edits.md` の「休眠 artifact への実装は実効性ゼロ」と同型で、
今回は skillOverrides ではなく `disable-model-invocation` が休眠源だった。

## Validation-only Follow-up (スコープ外・未修正)

`task validate-configs` が `ask tier が 8 件出現。deny-rules-catalog.md に ASK セクションを追加して同期せよ` で落ちる。
`git stash` した clean HEAD でも同一に落ちるため **本変更とは無関係の先行 drift**。
`settings.json` の ask tier と `references/deny-rules-catalog.md` が非同期。別途対応する。

`task validate-symlinks` は ok。
