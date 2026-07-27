---
title: "Harness Engineering is not Enough: Why Software Factories Fail (Dex Horthy) — absorb analysis"
date: 2026-07-27
source:
  title: "Harness Engineering is not Enough: Why Software Factories Fail"
  author: Dex Horthy (HumanLayer, founder/CEO)
  venue: AI Engineer
  url: https://www.youtube.com/watch?v=Ib5GBkD555M
  type: conference-talk
  note: "yt-dlp で英語字幕を取得し重複行を畳んで平文化 (4,045 語 / 21,393 字) を一次ソースとして使用"
  trigger: "https://x.com/iwashi86/status/2081220463615938878 のいいね経由 (rank 0)。ツイート自体が詳細な日本語まとめだが第三者要約なので原典を取得した"
status: analyzed
family: "harness-engineering (keyword 閾値未達だが内容は family の前提への反論)"
saturation: "PASS — 登録キーワードは `harness` のみ hit で 3+ 閾値未達。ただし本記事は family の tactic 追加ではなく前提の否定なので、飽和とは別カテゴリとして扱った"
adopted: 2
rejected: 3
degraded: "Phase 2.5 は Codex のみ。Gemini は IneligibleTierError"
---

# Dex Horthy「Harness Engineering is not Enough」— absorb 分析 (採用 2, reject 3)

## 結論

harness-engineering family の 記事だが、tactic を 1 つ足すものではなく **family の前提そのものへの反論**。「harness の loop を増やせば人間のレビューを外せる」が成り立たない理由を、モデルの訓練構造から説明している。

採用は 2 件。どちらも「新しい仕組みを足す」ではなく **既存方針の why を書く** 側の変更になった。

1. `PLANS.md` に `## Program Design（該当時のみ）` — 講演が「agentic coding で最も過小評価されている」と名指しした層
2. `references/why-humans-read-code.md` — "Humans steer, agents execute" の why と**見直し条件**

Codex の指摘で最も効いたのは、講演の射程の切り分け: **これは harness 投資の否定ではなく、harness を品質保証の代替物とみなす前提への反論**。この線引きを reference に表として落とした。

## Source Summary

**主張**: coding model は SWE-bench 系の binary reward (対象テストが通ったか + 他を壊さなかったか) で RL される。この構造には**プログラム設計の劣化にペナルティを与える経路がない**。さらに bad architecture のコスト関数は月〜年で測られるため、その信号を学習時の報酬として遡って伝播させることが極めて難しい。よってこれは scale の問題ではなく model training の問題であり、harness engineering や loop maxing では解けない。現時点では人間が全コードを読む工程を戻す必要がある。ただし事前設計でレビューを軽くできる。

**根拠**:
- **2025 年 7 月に HumanLayer 自社で lights-off を試して失敗**。エージェントが解けない問題に当たり、3 ヶ月読むのをやめたコードベースを掘り返す羽目になった
- Fahros AI のレポート — AI コーディングツール普及後、PR レビュー品質が低下 (コメント増・長文化・無レビュー merge 増)、インシデント増、developer あたりバグ増
- SWE-bench Multilingual の判定構造の具体例 (Fastlane の nil check)。モデルのテストファイル変更を巻き戻して golden test patch を当てる = 「テストを通す」以外の軸がない
- Claude Code が伸びた理由の分析 — 同じツール群を持つ CLI agent は既にあった。差は「model lab が配布先の harness に対してモデルを RL した最初の例」だったこと。OpenAI チームの 11 月の講演も「モデル重みを持たず harness 内で RL できない harness builder は、両方持つ者に対して常に不利」と述べている

**処方 (4 層の upfront planning)**:
1. product review — 何の問題を解くか / 望ましい挙動 / モックアップ
2. system architecture — component contract / データモデル / 制約
3. **program design** — 型 / メソッドシグネチャ / プログラムレイアウト / call stack。「最も過小評価されている。アーキテクチャが決まればモデルが cook できる、と思われているが違う」。Cloudflare の Dylan Mullroy が call graph を planning に使っている例を挙げる
4. vertical slices — 実装順序 / multi-repo 調整 / 各段でどう検証するか

**前提条件**: 複雑で長期運用されるコードベース。**vibe coding は対象外と明言** (Addy Osmani の引用を verbatim で使用)。境界は 10 年物レガシーではなく「**3〜6 ヶ月**でエージェントは苦しみ始める」。

**留保 (講演自身が付けている)**: フロンティアは徐々に良くなっている (SWE Marathon / DeepSuite / Frontier Code)。ただし**モデルが品質を judge できる範囲には限界がある** — モデルが良いコードを分かっているなら最初からそう書くはずだから。

## Phase 1.5 Saturation Gate

`references/topic-family-saturation.md` の `harness-engineering` は `harness`, `hook`, `scaffold`, `agent platform`, `harness everything` のうち 3 つ以上で判定。本講演の hit は `harness` のみ (+ HumanLayer の自己紹介が "AI IDE and collaboration platform") で**閾値未達 → PASS**。

ただし MEMORY.md は harness-engineering family を飽和領域として記録している。形式上 PASS でも、飽和 family の N+1 として警戒すべきかを検討した結果、**別カテゴリとして扱った**: 本講演は family の tactic を 1 つ足すものではなく、family の前提 (harness を厚くすれば人間を外せる) を否定する反論であり、飽和判定の対象になる「同じ角度の再パッケージ」ではない。

## Phase 2 判定

| # | 手法 | Pass 1 | Pass 2 判定 |
|---|---|---|---|
| 1 | **program design 層** (アーキテクチャより下・実装より上で型/シグネチャ/レイアウト/call graph を事前設計) | **not_found** — `PLANS.md:32-81` の必須セクションは Goal/Success Criteria/Scope/Constraints/Unknowns/Validation/Steps/Progress/Surprises/Decision Log/Outcome で型・シグネチャ粒度を要求しない。近接の `improve-codebase-architecture/LANGUAGE.md` (Module/Interface/Depth/Seam/Adapter) は**既存コードの診断用**で事前設計ではない | **採用** |
| 5 | **RL 報酬の構造的限界の明記** (人間が読み続ける根拠) | **not_found** — `docs/agentic-ai-textbook/20-environments-benchmarks.md:51` に「テストが通れば報酬1」の一行はあるが、論旨に接続されていない | **採用** |
| 2 | vertical slices (実装順序 + 境界検証 + multi-repo) | **partial** — `skills/prd-to-issues/SKILL.md:18-153` に tracer-bullet スライス分解 + Acceptance Criteria、`references/pr-splitting-patterns.md:37-70` に vertical/horizontal/grid 分割。境界検証の明示と multi-repo はカバー外 | **Reject** — multi-repo は単一リポジトリに N/A、境界検証は既存 `Validation` と重複。有益部分は Program Design 節に「各変更単位と検証」として回収 (Codex 提案) |
| 3 | upfront planning の ROI を「レビュー時間の節約」として明示 | **not_found** — DORA データ (`docs/research/2026-05-26-google-eng-practices-deep-dive.md:439-442`) はあるが言い回しなし | **Reject** — mechanism を伴わない rationale。#1 の目的として 1 文あれば足りる (Codex 同意) |
| 4 | 「PR が多すぎるのではなく悪い PR が多すぎる」再フレーム | **not_found** | **Reject** — 行動を変えないスローガン (Codex 同意)。ただし reference の Gotchas に 1 文だけ残した |

## Phase 2.5 Refine

**Gemini: 実行不能** (`IneligibleTierError`)。周辺知識補完は未取得。

**Codex (gpt-5.6-terra, xhigh, read-only)** — 4 点すべて採用。

| Codex 指摘 | 反映 |
|---|---|
| #1 の発動条件は S/M/L の規模ではなく**変更の性質**にすべき: 複数モジュールに跨る interface/ownership 変更 / caller が複数ある public API / 状態・並行性・失敗意味論の変更。`PLANS.md` に optional な `## Program Design (when required)` を置き、該当時だけ型・主要シグネチャ・データ所有者・call graph・変更順を書くのが最小 | 採用。この 3 条件をそのまま発動条件として書いた |
| #5 の詳細根拠は新規 reference に置き、**CLAUDE.md は一文 + リンク**に留める。core principle には「現行 verifier は長期保守性を十分に測れないため人間の読解を残す。代表変更で設計劣化を高い再現率で検出できる verifier が実証されたら見直す」程度。**特定ベンチ名は撤退条件ではなく観測対象**にする | 採用。見直し条件を「代表的な変更に対して設計の劣化を高い再現率で検出できる verifier が実証されたとき」と書き、SWE Marathon / DeepSuite / Frontier Code は「観測対象」として別扱いにした |
| #2 の有益部分は Program Design 内に「各変更単位と検証」を書かせれば回収できる | 採用 |
| **講演は harness 投資そのものの否定ではなく、harness を品質保証の代替物とみなす前提への反論**。dotfiles での具体的修正点は「`ralph-loop`/max-loop の完走、binary completion gate、reviewer の `ok=true` を人間レビュー不要の根拠に昇格させない」「成功率・テスト通過率だけで harness を改善しない」。逆に探索・計画・検証証跡・レビューを読みやすくする harness は全行レビューを可能にする投資なので講演と整合する | **採用。この切り分けが今回の中核**。reference に「やってはいけない」4 行の表として落とし、整合する側も明記した |

## 実施済

- ブランチ: `fix/careful-freeze-description-drift` (継続)
- `PLANS.md` — `## Program Design（該当時のみ）` を Validation の前に追加。発動条件 3 つ + 「当たらなければ節ごと省く」+ reference リンク
- `.config/claude/references/why-humans-read-code.md` (新規) — 報酬構造の説明 / harness を代替物にしない線引き表 / 4 層の対処 / **見直し条件** / Gotchas
- `.config/claude/CLAUDE.md` — 条件付きブロック `<important if="you are about to implement, investigate, or review code">` に 1 行追加。常時ロードの `<core_principles>` には入れていない (IFScale / `feedback_claudemd_length.md`)。CLAUDE.md は 122 行
- 検証: `task validate-configs` exit=0 / `task validate-symlinks` exit=0 / `why-humans-read-code` の参照が CLAUDE.md と PLANS.md の双方に結線されていることを確認
- 未実施: commit / PR

## 未取得・未検証

- **Gemini 周辺知識補完**: 実行不能
- **Fahros AI のレポート原典**: 講演の言及のみ。数値も「way down / way up」で具体値は述べられていない
- **講演が挙げた新ベンチマーク 3 件の実体**: SWE Marathon (Abundant AI) / DeepSuite (Data Curve) / Frontier Code (Cognition) — いずれも未確認。reference には「観測対象」として名前のみ記録し、見直し条件そのものには使っていない
- **字幕の精度**: 自動生成字幕なので固有名詞に誤りの可能性がある (例: "Farosai" / "Fahros AI"、"John Austerhood" は John Ousterhout、"VBOV" は不明)。引用として使った箇所は主張の骨格のみで、固有名詞に依存する採用判断はしていない
- **関連二次資料**: Addy Osmani の "Software Factories, Light and Dark"、Hacker News スレッド (item?id=49023019) は未読
