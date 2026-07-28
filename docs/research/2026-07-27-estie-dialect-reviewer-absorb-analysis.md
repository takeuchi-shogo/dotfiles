---
title: "estie の7年分レビュー履歴から「自社方言レビュアー」を作った話 — absorb analysis"
date: 2026-07-27
source:
  title: "estieの7年分のコードレビュー履歴をAIに食わせて、自社の方言が分かるレビュアーを作った話"
  author: estie (@tiwanari)
  url: https://zenn.dev/estie/articles/f0f114389662ba
  type: company-engineering-blog
  note: "zenn は trusted 外のため defuddle 経由で full markdown 取得 (18,330 bytes)"
  trigger: "https://x.com/tiwanari のいいね経由 (rank 92)"
status: analyzed
family: code-review-best-practices
adopted: 2
rejected: 3
degraded: "Phase 2.5 は Codex のみ。Gemini は IneligibleTierError"
---

# estie「自社方言レビュアー」— absorb 分析 (採用 2, reject 3)

## 結論

記事の中核 (GitHub API で 7 年分のレビューコメントを収集 → 集計 + AI による意味集約 → 言語別「レビュー規約」Markdown に蒸留 → 6 役割並列レビュアーで参照) は **team 前提**で、単一ユーザーの dotfiles には元データがない。複数リポジトリ・複数レビュアー・7 年の履歴という前提が揃わない。

採用したのは、記事が「今回の工夫」と「正直な限界」として書いた 2 点。どちらも dotfiles の learned 昇格ループに直接当たる。

**特に効いたのは限界の方**。記事は「レビューが形骸化していたらデータを集めても意味のある規約は抽出できない」と書いているが、dotfiles ではこの失敗が既に現実化している — memory の記録によれば improve-policy の Friction→Eval Loop の producer が停止していた (errors.jsonl 16 日 / friction 25 日)。枯れたログから「もっともらしい learned」を昇格できる状態になっている。

## Source Summary

**主張**: 汎用 AI レビューツール (CodeRabbit / Copilot Code Review) は言語ごとの定石と既知のアンチパターンには強いが、会社の方言 (命名の癖、設計の好み、何を blocker にして何を nit に留めるか) は自社のレビュー履歴だけが知っている。その差を埋める。

**主な手法**:

1. 収集 — GitHub API で PR / 変更ファイル / レビューコメントを JSONL 化。GraphQL は期間を半年ずつに区切り、レート制限で途中再開できるように
2. 分析 — ①集計だけで見えるもの (カテゴリ振り分け、prefix の使われ方、コメント長、疑問形の割合、suggestion 提示率) と ②AI にコメント本文を読ませる意味集約 (言語ごとの頻出パターンを件数つきで抽出) を分ける
3. 蒸留 — 集計結果を Claude Code の skill に読ませて言語別「レビュー規約」Markdown に変換。定型 4 項目 = 指摘する条件 / 指摘の強さ / コメント例 / 根拠(過去 N 件)。最終的に全言語共通 + 言語別で 7 ファイル
4. レビュー — 変更ファイルの言語に対応する規約を読ませる。1 プロンプトで全部より観点ごとの担当分けの方が精度が出た
5. 6 役割並列 + モデル振り分け — リポジトリ規約準拠(Sonnet) / バグスキャン(Opus) / git履歴・依存(Sonnet) / 過去PRコメント突合(Sonnet) / コード内コメント整合性(Haiku) / レビュー規約チェック(Sonnet)
6. 統一 JSON 出力 (path / line / severity / category / confidence / comment / reason)
7. confidence 0-100 + カテゴリ別重み + 閾値足切り → Judge 役が行番号・変数名の正確性 / 修正案の具体性 / blocker 過剰でないか / 重複を検証 → 残ったものだけコメント。**広く拾って厳しく絞る二段構え**
8. データ扱いの事前決定 — 個人名・顧客名・障害対応の経緯・未公開仕様が混ざる。対象リポジトリ / AI に渡してよい情報 / トークン権限を先に確認。bot・自己レビュー・単なる LGTM は除外。1 リポジトリ・数か月分から小さく試す

**根拠 (自社データ)**: コメント長の中央値 約 55 文字、疑問形が約 3 割、日英混在が約 8 割。規約項目には「過去のレビューコメント 18 件」のような実績件数を添付。

**CodeRabbit との比較 (6 PR、サンプル小と明記)**:

| 指標 | estie 製 | CodeRabbit |
|---|---|---|
| 指摘件数 | 30 | 10 |
| 実行可能性 | 41% | 90% |
| 誤検知率 | 0% | 10% |
| カバレッジ | 73% | 42% |
| must 率 | 7% | 40% |

**一致率 14%** — 同じ PR を見ても指摘の 8 割以上が重ならない。結論は「相補的」で、CodeRabbit → 対応 → 自作 (対応済みは除外) → 人間は設計判断 の順序を推奨。

**正直な限界 (記事自身が明記)**: レビュー文化が形骸化していたら意味がない / トークンをかなり使う重いレビュアー / 「実プロダクトで劇的なバグを仕留めた派手な実績があるわけでもない」/ 精度は規約の質しだいで継続的な手入れが前提。

## Phase 2 判定

| # | 手法 | 判定 | 現状 |
|---|---|---|---|
| 1 | 規約の各項目に「実績◯件」を必須添付 | **Gap** | `scripts/learner/extract-promotion-candidates.py:34-45,69-90` は `importance` (float, 既定 0.5) の降順のみ。観測回数フィールドなし。`patterns.jsonl` の `confidence` / `consecutive_reads` は 1 レコード内の値で集計件数ではない。近接の `code-reviewer.md:135-136`「同一カテゴリの NIT が 3 件以上 → CONSIDER 昇格」は severity 昇格の閾値で別物 |
| 4 | 抽出元データが「学ぶに値するか」の事前検査 | **Gap** | `auto-triage` は候補ごとの分類で source 全体の質を問わない。`improve-policy.md:367-369` の "garbage in, garbage out" 言及は improve ループ内の話。`session-learner.py` / `extract-promotion-candidates.py` に pre-check なし |
| 2 | MUST/blocker を実バグ+破壊的変更に限定、設計の好みは 1 段下げる | **Partial → Reject** | `code-reviewer.md:113-119` の 5 段ラダー (MUST=security・bug・GP違反 / CONSIDER=設計改善 / NIT=スタイル) で設計の好みは既に 2 段下。ただし dotfiles の MUST は estie 版より**広い** (GP 違反・security を含む) |
| 3 | 最上位 severity に修正コード必須 | **Partial → Reject** | `code-reviewer.md:447` で BLOCK verdict (MUST≥1) は「MUST 箇所を file:line で列挙 + suggestion block」を義務化済。severity 別の差別化はないが現行で足りる |
| 5-8 | 6 役割並列 / 統一 JSON / confidence 足切り / Judge 検証 | **Already** | 10+ reviewer agent の tier 別選択、`review-output.md` の形式強制、`reviewer-routing.md:209-213` の confidence<60 自動除外、`testing-evaluation.md:138` の judge 独立性。dotfiles の方が精緻 |
| — | レビュー履歴マイニング本体 | **N/A** | team 前提。単一ユーザーに元データがない |

## Phase 2.5 Refine

**Gemini: 実行不能** (`IneligibleTierError`)。

**Codex (gpt-5.6-terra, xhigh, read-only)** — 4 点すべて採用。

| Codex 指摘 | 反映 |
|---|---|
| #1/#4 は「一つの昇格ゲート」だが**実装責務は分ける**。観測件数と source health は決定論的な入力メタデータなので `extract-promotion-candidates.py` で算出し、`promote-learnings` で昇格停止・例外承認を判断する。`auto-triage` は dry-run 専用なので同じ値を表示するだけで唯一のゲートにはしない | 採用。プランを 3 層 (算出 / 判断 / 表示のみ) に分けた |
| #2 の Reject は妥当 — 現行 MUST は security / bug / GP 違反であり、設計上の破綻を「好み」に落とすと安全側の契約を壊す。#3 も追加対応は不要寄りで、全 severity に無差別にコード修正を強制するより現行が適切 | 採用。Reject 確定 |
| 閾値は「180 日以内に独立観測 3 件以上かつ 2 セッション以上」を既定に。2 件は 60 日失効付き provisional、1 件は security 境界・再現済み破壊的障害など強い因果証拠がある場合のみ例外昇格。**件数は `importance` に混ぜず根拠として併記** | 採用。team 実数 (estie の 18 件) を持ち込まず単一ユーザー前提の閾値にした |
| source health は件数ではなく (a) upstream producer の鮮度・継続性 (b) 候補から生ログの時刻・ID・根拠へ遡れること (c) リトライ重複でない独立性 + 受容・解決などの結果シグナル を見る。さらに各 source の少数サンプルを人手監査して欠損・parse error・単一 emitter 偏重を測る | 採用。4 項目の表としてプランに入れた。d は自動化しない |

## Phase 3 Triage 結果

| ID | タスク | 規模 | 判定 |
|---|---|---|---|
| E1 | 観測件数の算出と付与 (`extract-promotion-candidates.py`) | M | **採用 (プラン化)** |
| E2 | source health の事前検査 + 昇格閾値 (`promote-learnings/SKILL.md`) | M | **採用 (プラン化)** |
| — | MUST を実バグ+破壊的変更に限定 | — | **Reject** (security escalation を弱める) |
| — | 最上位 severity に修正コード必須 | — | **Reject** (BLOCK で実装済) |
| — | レビュー履歴マイニング本体 | — | **Reject / N/A** (team 前提、元データなし) |

プラン: `docs/plans/active/2026-07-27-learned-promotion-evidence-gate-plan.md`

## 今回は実装しない判断

**gate 文言 (E2) を先に入れてはならない**。観測件数と source health を算出する側 (E1) がないまま `promote-learnings` に「3 件以上なら昇格」と書くと、参照先のフィールドが存在しない gate になる。

これは同日 #17 (Claude Cookbook) で codify した失敗モードそのもの — 「検証手順に特定の手段を指定すると、それが環境に無いとき検査が silently に飛び、気にしていた検査が一度も走らない」(`skill-creator/instructions/testing-evaluation.md` の Rubric authoring)。自分で入れたルールを同じセッションで破らない。

実装順序は P1 (算出) → P3 (source health) → P2 (閾値の gate)。

## 副次的な検証 (採用に数えない)

**一致率 14%** — estie 製と CodeRabbit が同じ 6 PR で指摘の 8 割以上重ならなかった。dotfiles は `references/review-consensus-policy.md` §1 Heterogeneous Signal Priority で異種 reviewer の併用を既定にしており、その設計判断を支持する外部データ点になる (サンプル 6 PR と記事自身が断っているため強い証拠ではない)。

**記事の誠実さ自体が calibration 材料**: 「実プロダクトで劇的なバグを仕留めた派手な実績があるわけでもない」「網羅的だけど重い」と自ら書いている。同種の harness を作った記事が成果を誇張しない例として、`references/reference_brevity_tradeoff_research.md` 系の「隠れたトレードオフ」記録に近い価値がある。ただし新規 artifact は作らない。

## 未取得・未検証

- **Gemini 周辺知識補完**: 実行不能
- **記事の数値の再現性**: 6 PR というサンプルサイズは記事自身が「製品一般の優劣を決めるものではない」と断っている。指標定義 (実行可能性 = 修正コードを含む指摘の割合 等) も estie 独自
- **E1/E2 の実装**: 未着手。`patterns.jsonl` の実スキーマと `extract-promotion-candidates.py` の内部構造は Pass 1 の報告 (行番号ベース) 以上には確認していない。実装時に要確認
