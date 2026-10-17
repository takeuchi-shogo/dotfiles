---
title: "Anthropic「Solving code review at Anthropic」absorb"
date: 2026-10-17
source:
  title: "Solving code review at Anthropic"
  author: Anthropic (Claude Code team)
  url: https://claude.dev/blog/solving-code-review-at-anthropic/
  type: blog-post
  fetched: defuddle (20,948 bytes, 全文取得成功)
status: integrated
family: code-review-best-practices
adopted: 4
plan: tmp/plans/review-content-bound-pass.md (使い捨て、commit body に畳む)
---

# Anthropic「Solving code review at Anthropic」— レビューの承認をコンテンツに束縛する

## Source Summary

**主張**: Claude Code チームは 6〜9 月に merged PR が 2 倍超になり、revert 率は 40% 超減った。レビューを廃止したのではない。読む作業の大半を機械に移して人間の注意をリスクに集中させ、失敗を速く戻せるようにした。

**手法**:
- PR 前の検証: 実行できるチェックを渡して出力を見せる。fresh-context の subagent にレビューさせる。繰り返される指摘は skill / lint / CLAUDE.md で発生源を直す。owner が短い REVIEW.md を書く
- 全 PR への AI レビュー: 並列 finder と別グループの投票で検証する。style-only は落とす。Important / Nit / Pre-existing のタグを付け、全 finding に応答義務を課す
- block できる security review と、block する CI。PR テンプレに Testing と How to undo を置く
- リスク tier は author でなく change が決める。CI workflow など常に人間が要るパスを持つ。agent の approval は人間の代わりにならない。approval は特定コミットに束縛する
- merge queue / flag / 段階リリース、速い検出と rollback
- レビュアーの改善: incident を eval 化し、prompt / tool / model の変更時に再採点する。ノイズは著者の反応 (fixed / wrong / intentional / didn't matter) と、known-clean PR での誤検知で測る
- 収束: 一晩で 50 ラウンドを超えた PR があった。git blame で見ると、再指摘の約 59% は初回レビュー時点から存在したコードだった。対策はラウンド上限 3 で方針を再考、数巡後は diff-only、バグのクラスで指摘、既出の再掲禁止

**根拠**: 社内の merged PR 数と revert 率の推移、収束しなかった PR の git blame 分析。

**前提条件**: 多人数チームで owner が面ごとに分かれ、merge queue や段階リリースの基盤がある。人間は方向性・高リスクコード・アーキテクチャ・証拠を読むこと・結果の責任に残る。

## Phase 1.5 Saturation Gate

family は code-review-best-practices、N=13 (baseline 13 + 新規 0 + skip 0)。採用率は少なくとも 5/13 (openclaw 初回 / 6-stages / agentic-code-review / openclaw 3rd / stopped-reviewing) で 20% を超えるため、PASS (warning)。直近 2 件は連続 reject ではない。

Step 7 の Stale-Plan Audit では、直近 3 件のうち monotaro (2026-08-06) が `status: planned` のまま 72 日経っていたので棚卸し対象にした。ユーザーの指示で実態を確認した結果は narrowed (partially-superseded)。T1/T2 は有効、T3/T5 は pr-autofix-routine の #259 退役で消失、T4 は Codex Gate が BLOCK のまま未完。詳細は monotaro レポート末尾の「棚卸し」節に書いた。

## Phase 2 判定 (Phase 2.5 補正後)

| # | 手法 | 判定 | 詳細 |
|---|---|---|---|
| 1 | Pre-existing タグ | Partial | `review/SKILL.md` 統合ルール 8 が diff 外の指摘を黙って除外していた → 採用 |
| 2 | 再レビューの収束 (再掲禁止・バグクラス) | Partial | 上限 3・diff-only・振り子検出はあるが、前回指摘の ledger が無い。monotaro T3 の ledger は消費者ごと消えた → 採用 |
| 3 | instruction ファイルの light tier 抜け道 | 降格 (Already) | 当初は `reviewer-routing.md` の `**/*.md`=Low を問題視した。しかし `review-tier.py:80-126` の `_is_agent_instruction_md` が既に除外していた (Codex 指摘で訂正)。routing 表の記述ずれは validation-only |
| 4 | PR テンプレ Risk / How to revert | Gap | → 採用 |
| 5 | incident 由来 eval / モデル変更時の再採点 | Partial | tuple は合成のみで最終実行は 2026-03-16。clean 対照の追加に絞って採用。provenance と FP 指標はランナー不在のため follow-up |
| 6 | 全 finding 応答義務 | Partial (Codex 指摘のみ) | 見送り |
| 7 | 件数先頭の要約 | Already | Codex 指摘で `synthesis-report.md:7-11` にあると訂正 |
| 8 | CLAUDE.md 陳腐化検出 | Partial | 見送り (`doc-garden-check` が別にある) |
| 9 | owner 別 REVIEW.md | N/A (単一 owner) | Codex は「面ごとの失敗定義・skip path・nit 上限は個人 harness にも合う」と指摘した。将来の検討材料 |
| 10 | merge queue / flag / 段階リリース / nightly review / human-time 指標 | N/A | 個人 repo に基盤が無い |
| 13 | 合議フィルタ | Already → Partial | Codex 指摘: 合意は重複除去と順序付けであり、別グループによる finding ごとの検証ではない |
| 16 | 著者反応によるノイズ測定 | Already → Partial | 記録は NEEDS_FIX / BLOCK 時のみで、未回答は deferred 扱い |
| New | approval のコンテンツ束縛 | Gap | `harness_review_flag.py` が変更ファイル名集合の md5 を鍵にしており、PASS 後に同じファイルを編集してもフラグが有効なまま。`completion-gate` の docstring は逆のことを主張していた → 最優先で採用 |

New は記事の「approval は特定コミットに束縛」を lens にして、Codex が見つけた。Opus が最初に作った表には無かった。

## Phase 2.5

Codex (gpt-5.6-terra, xhigh, read-only, `project_doc_max_bytes=0`) の verdict 行は次のとおり。

> Verdict: Strong analysis, but revise #3, #7, #11, #13, and #16; prioritize content-bound review validity over team-scale process.

優先順は (1) PASS をコンテンツに束縛する、(2) cycle-local な prior-findings ledger、(3) clean 対照と model provenance。日次 eval は単一 owner には不要とした。#3 と #7 は実ファイルで反証され、判定を Already に降格した。

Gemini (agy) は、出典 URL の多くがトップページのみで引用元としての信頼度が低いと指摘した (Meta RADAR の arXiv 番号も未確認)。論点として次の 3 つを採用した。

- CodeRabbit 式に、既存の課題を非ブロッキングの情報提供として分離する → 項目 1
- 行数・ファイル種別の静的分類器は、1 行の設定変更を低リスクと誤判定する → 項目 3 の懸念 (実装側は除外済みと確認)
- 著者反応ベースのノイズ測定には、「反論しても無駄」と黙って無視する生存者バイアスがある → 項目 16 の Partial 判定に反映

## Phase 3-4 採用結果

ユーザーが 4 件を選んだ。A PASS フラグをコンテンツに束縛、B 再レビュー ledger + `[OUT-OF-DIFF]`、C reviewer eval に clean 対照、D PR テンプレに Risk・How to revert。monotaro の Step 9 (cargo test + Codex Gate) も今回取得した。

### A. PASS フラグをコンテンツに束縛

- `lib/harness_review_flag.py` に `fingerprint()` を追加した。sha256 で、"v2" タグ・repo toplevel・HEAD・`git diff --binary --no-textconv --no-ext-diff --no-renames HEAD` の bytes・untracked ハーネスファイルのパスと中身を、各要素を長さ前置で連結する
- `completion-gate` は lib を import して実装を単一にした。重複していた markers / flag dir / key を削除した
- fingerprint の失敗と lib の読込失敗は block する (fail closed)
- untracked ファイルは fingerprint にだけ入れ、gate の発火条件には入れない
- Review Gate で追加修正した。retry 安全弁 (`:1419`) が harness gate より先に return するため、2 回 block されたあとは未レビューのまま通過できた (master から存在)。安全弁でも harness gate を先に確認し、harness block では retry カウンタを増やさないようにした。lib 自身もマーカー対象に加えた

### B. 再レビューの ledger と `[OUT-OF-DIFF]`

- `SKILL.md` 統合ルール 8 を `[OUT-OF-DIFF]` 保持に変えた。サイクルルール 2/6/9 に ledger を置いた。key は file + failure_mode、evidence を持ち、status は open / fixed / dismissed:<理由>。新しい evidence の無い再指摘は破棄し、指摘にはバグクラスを名指しさせる
- `reviewer-routing.md` のプロンプトと除外リスト、`review-output.md` を整合させた。confidence 60 未満の除外は subjective のみ
- 「pre-existing」と名乗らないのは、base に存在したことを証明していないため

### C. reviewer eval に clean 対照

- `case_kind=clean` の tuple 6 件を追加した (eval-031〜036、TS / Go / Python 各 2 件)。既存 defect tuple の修正版 near-miss にしてある
- `split_holdout` で train / holdout の両方に入ることをテストで確認した

### D. PR テンプレ

- `commands/pull-request.md` に Risk / How to revert 節を足した

### 検証

- pytest 445 passed。新しい回帰テストは旧 lib で 6/7 failed、安全弁テストは旧ロジックで 2 failed (識別力を確認)
- `validate-configs` / `validate-symlinks` は exit 0
- cargo test 58 passed

## Gate 記録 (verbatim)

- Plan Gate (Codex): "VERDICT: NEEDS_FIX" → fingerprint 仕様、失敗契約、import 位置、ledger 定義、C の範囲縮小を spec に反映した
- Review round 1: Codex "VERDICT: BLOCK" / code-reviewer "PASS [NITS_REMAIN: 2 NIT, 3 FYI]" (code-reviewer は Coverage で新規テスト本体は未読と自己申告)
- Review round 2: Codex "VERDICT: BLOCK" (安全弁は修正済みと確認。lib 自身のマーカー漏れと、60 未満の無条件除外を指摘)
- Review round 3: Codex "VERDICT: PASS" (「今回の修正で導入された新規の Critical / Important / Watch はありません」。pytest は sandbox で再実行せず、ローカルの 445 passed を前提にした)
- pre_tool.rs (monotaro T4) Codex Gate: "VERDICT: BLOCK"

サイクルルール 5 の上限 3 回以内で収束した。

## Follow-up

- `pre_tool.rs` の一括 add hook に残る、未文書化の回避 4 経路 → [#281](https://github.com/takeuchi-shogo/dotfiles/issues/281)
- untracked のみのハーネス変更では gate が発火しない → [#282](https://github.com/takeuchi-shogo/dotfiles/issues/282)
- reviewer eval のランナーと、model / prompt の provenance・FP 指標 (未 Issue 化)
- `review-findings.jsonl` が 2026-08-31 以降 47 日間書き込まれていない (原因未確認、未 Issue 化)

## Validation-only Follow-up (採用件数に数えない)

- `reviewer-routing.md` の `**/*.md`=Low が、`review-tier.py` の実装 (instruction md 除外) とずれている
- `completion-gate` の docstring が「編集でフラグが無効になる」と、実装と逆のことを書いていた (今回修正)

## 教訓

- 記事の「承認は 1 コミットに束縛」を lens にすると、自分の gate が「何を承認したか」を覚えていないことが出た。存在するゲートが十分とは限らない
- Codex Review Gate の round 1 の Critical は master から続く問題で、今回入れた `[OUT-OF-DIFF]` の実例そのものだった。diff 外を黙って捨てていたら見逃していた
- absorb の棚卸しで、skill 退役 (#259) が過去 absorb の採用タスク (T3/T5) を黙って消していたことが分かった。退役時に inbound の採用タスクを照合する仕組みは無い
