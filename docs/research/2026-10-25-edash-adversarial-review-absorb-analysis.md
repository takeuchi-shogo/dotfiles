---
title: "実務において敵対的レビューはどの程度有効なのか (e-dash) absorb"
date: 2026-10-25
source:
  title: "実務において敵対的レビューはどの程度有効なのか"
  author: jellyfish1129 (e-dash Tech Blog)
  url: https://zenn.dev/edash_tech_blog/articles/4577f7d4780bef
  type: zenn-article
  fetched: WebFetch (全文取得成功)
  intro: "https://x.com/nwiizo/status/2113669279727898810"
status: integrated
family: code-review-best-practices
adopted: 0
---

# e-dash 敵対的レビュー記事 — 採否

## Source Summary

**主張**: 敵対的レビュー（通常レビューに加え「誤った結果やエラーを起こす入力・状況」を探すレーンを並列し、指摘を実コードで確かめてから確定する）は、重大指摘の検出では Claude Code 標準の code-review より強いが、token と運用コストが高い。スピード優先の場面では必須ではなく、データの更新・計算ロジック・認可など危険度で使い分ける。

**手法（記事本文）**:
- 正統 2 + 敵対 4 + 役割 2 の計 8 レーンを並列実行し、観測ファイルに件数を残す
- 正統・敵対の指摘は本体が実コードで確かめ、割れた点は Fable にまとめて判定させる。役割レーンは別枠
- 交差検証後に **YAGNI レーン**で「従わないと、いま実際にどんな誤動作やデータの不整合が起きるか」を示せない指摘を棄却または降格
- 指摘の帰属を「この差分が持ち込んだもの / 変更前からあるもの / 仕様の欠落」に分け、修正対象は前者だけ
- レビューと自動修正のループに周回上限を固定する
- 検証: 差分 85 件・レビュー 99 回。確定 357 件（重大 138）。code-review が拾った重大は 100 件中 7 件。token は記録のある 2 回で敵対約 140〜150 万 vs code-review 約 17 万

**紹介ポスト** (@nwiizo): 「指摘が増えるだけでは評価できない。コードで確かめ、不要な修正を落とす工程にもコストがかかる。差分の行数より変更対象の危険度で使い分ける〔…〕」（原文はこのあと「考え方は、品質と速度を両立する手掛かりになる。」と続き、ハッシュタグと記事リンクがある。引用は途中まで）

**前提**: 業務差分での自前 skill。個人 harness とはレビュー規模が違う。

## Phase 1.5 Saturation Gate

family: `code-review-best-practices`（先行: agentic-code-review / monotaro / Anthropic solving-code-review / stopped-reviewing 等）。採用率は既に 20% 超のため PASS (warning)。連続 reject ではない。

## 既存レビュー系との照合

| 記事の手法 | 既存 | 判定 |
|---|---|---|
| 複数レーン並列（バグ・セキュリティ・設計など） | `/review` の tier 別並列レビューアー（code-reviewer / codex-reviewer / edge-case-hunter / security-reviewer 等） | Already |
| 指摘を実コードで確かめる（PR 説明や要約を根拠にしない） | Evidence-Based Feedback + Codex Review Gate | Already |
| 交差検証・合議 | `review-consensus-policy.md`（合意はタイブレーク、対立は CONFLICT） | Already |
| 割れた判定を Fable に渡す | `model-routing.md`（設計=Fable） | Already（レビュー仲裁専用レーンとしては未分離 → 新規レーンは作らない） |
| Pre-existing / 帰属の分離 | 統合ルール 8 `[OUT-OF-DIFF]`、Anthropic absorb の Pre-existing 系 | Already |
| 自動修正ループの周回上限 | Anthropic absorb の再レビュー収束（上限・diff-only・再掲禁止） | Already |
| 行数でなく危険度で敵対レビューを当てる | review tier（light / standard / deep）と変更内容ルーティング | Already |
| 8 レーン常時の敵対的レビュー一式 | 記事自身が token 約 9 倍・500 行未満で確定 0 が珍しくないと報告 | Reject |
| **YAGNI レーン**（実害を示せない指摘の棄却・降格） | 信頼度フィルタ・verbosity・Watch はあるが、「いまの誤動作/データ不整合を示せ」という実害ゲートは無い | **Reject**（当初 Adopt 案だったが、ユーザー判断で取り消し） |

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|---|---|---|
| 1 | 8 レーン敵対的レビューの常時導入 | Reject | 記事の計測でコストが大きく、既存の並列レビュー＋ tier で危険度切り分けは足りる |
| 2 | Fable 仲裁レーンの新設 | Reject | モデル役割は既存。レビュー専用の追加レーンはトークン増のみ |
| 3 | YAGNI フィルタ（実害一文） | **Reject** | **ユーザー判断で最小限にした**（2026-10-25 16:58 JST:「#304 は AGENTS.md の1行とルール19を両方外して、最小限にして」）。`/review` の挙動は変えない。参考: レビューで指摘されたとおり、実害を示せない指摘を落とすルールは Codex Critical/Important の必須対応（統合ルール 15）と衝突しうる |

### 採用した変更

なし（`adopted: 0`）。YAGNI フィルタ（ルール 19 / `synthesis-yagni`）は branch から外し、base と同じ `/review` に戻した。

## 取得できたもの / 読めなかったもの

| ソース | 結果 |
|---|---|
| Zenn 記事本文 | 全文取得・判定に使用 |
| X 紹介 (`nwiizo/2113669279727898810`) | 取得。記事の結論（危険度で使い分け・確かめと棄却のコスト）の要約に留まり、手法の追加情報はなし |
