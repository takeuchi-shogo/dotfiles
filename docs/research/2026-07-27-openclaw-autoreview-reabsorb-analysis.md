---
title: "openclaw/agent-skills autoreview SKILL.md — 再 absorb 分析 (同一ソース 2 回目)"
date: 2026-07-27
source:
  title: "autoreview SKILL.md"
  author: openclaw/agent-skills (@steipete)
  url: https://github.com/openclaw/agent-skills/blob/main/skills/autoreview/SKILL.md
  type: oss-skill-definition
  note: "blob ページを defuddle 取得 (31,834 bytes)。raw URL は text/plain で defuddle 不可、curl は権限 deny"
  trigger: "https://x.com/steipete のいいね経由 (rank 30)「オートレビュー・スキルで新記録を達成。厄介なリファクターで66ラウンド」"
status: analyzed
family: code-review-best-practices
prior-absorb: docs/research/2026-05-28-openclaw-autoreview-absorb-analysis.md
saturation: "同一ソース 2 回目。差分 absorb として実行 (5/28 時点に存在しなかったセクションのみ対象)"
adopted: 2
validation-only: 1
stale-plan-audit: "docs/plans/active/2026-05-28-autoreview-absorb-plan.md を closed に (T7 実装 / T8 実装済判明 / T6・T9 retire)"
degraded: "Phase 2.5 は Codex のみ。Gemini は IneligibleTierError"
---

# openclaw autoreview SKILL.md — 再 absorb 分析 (採用 2 + validation 1 + Stale-Plan Audit)

## 結論

**同一ソースの 2 回目**。2026-05-28 に 35 手法を absorb 済 (9 件採用 / 5 実装 + 4 保留)。今回は「記事から何を採用するか」ではなく **(a) ソースが 5/28 から何を追加したか** と **(b) 保留 4 件はどうなったか** の 2 問として実行した。

(a) の答え: **`## Scope Governor` セクションが新設されている**。レビュー→修正ループが元の依頼を超えて膨らむのを止めるゲートで、当時の 35 手法リストに対応物がない。ツイートの「厄介なリファクターで 66 ラウンド」がまさにこの発散パターンで、サイクル数の上限だけでは止まらないという観測に対応する。Pass 1 の結果、7 概念中 **exists ゼロ / partial 2 / not_found 5** で dotfiles にほぼ無い領域だった。

(b) の答え: 4 件のうち **T8 は既に実装済** (2026-06-13、保留リストが陳腐化)、T7 は今回実装、T6・T9 は retire。Plan を closed にした。

## 差分の同定

5/28 の分析レポートの手法リストと、現在のセクション構成を突き合わせた。

| 現在のセクション | 5/28 の 35 手法に対応物 |
|---|---|
| Auto Review / Contract | あり (helper script bundle, 1-engine/1-bundle/1-result) |
| **Scope Governor** | **なし → 今回の対象** |
| Pick Target | あり (mode 自動分岐: clean local / staged / branch-diff) |
| **Oversized Bundles** | なし (後述、採用 0) |
| Parallel Closeout | あり (format → test ∥ review = T8) |
| Review Panels | あり (panel opt-in) |
| Environment defaults | あり (engine override 禁止 + capacity retry) |
| **Context Efficiency** | 実質あり (no-nested-review = T3 で採用済) |
| Helper | あり |
| Final Report | あり (4 elements = T7) |

新規は Scope Governor / Oversized Bundles の 2 節。Context Efficiency は節としては新しいが中身が既採用の no-nested-review と同じ。

## Scope Governor の Pass 1 結果

| # | 概念 | 判定 | 現状 |
|---|---|---|---|
| 1 | レビュー前に scope baseline 凍結 (元依頼/ブランチ/意図した挙動/owner 境界/変更ファイル/非テスト LOC) | **not_found** | `PLANS.md` の `## Scope` は実装前の plan scope で、レビュー時の基準凍結ではない |
| 2 | finding を修正前に 3 分類 (in-scope blocker / follow-up / stop-and-escalate) | **not_found** | 近接だが軸が違う: `code-reviewer.md` の MUST/CONSIDER/NIT/ASK/FYI は**重大度**軸、`github-pr/review-response.md` の 3 分類は PR コメントの **resolve 状態**軸 |
| 3 | diff 膨張の**相対**ゲート (初期の 2x) | **not_found** | 既存は `references/pr-splitting-patterns.md` の 300 行という**絶対値** |
| 4 | 修正サイクル 2 回未収束で停止し残り全 finding を再分類 | **partial** | `skills/review/SKILL.md:610` に「最大 3 回で人間 escalate」はあるが、**再分類手続きがない** (止まるだけ) |
| 5 | 最善の修正が「canonical contract を先に定義」なら patch 停止 | **not_found** | 該当なし |
| 6 | scope 未確定のまま修正コミットを積んで push しない | **not_found** | 近接: `github-pr/review-response.md` の「合意なく修正に着手しない」。探索的編集をローカルに留める設計ではない |
| 7 | critical 例外の限定列挙 | **partial** | `references/emergency-definition.md` に列挙があるが、発動条件が **Large CL 分割免除**用で review scope 用ではない |

Pass 1 の副産物: `skills/review-loop/` と `skills/implement-loop/` に **SKILL.md の実体がない** (available-skills 一覧には名前が出る)。command 側の定義と思われるが未追跡。

## Phase 2.5 Refine

**Gemini: 実行不能** (`IneligibleTierError`)。

**Codex (gpt-5.6-terra, xhigh, read-only)** の指摘は 4 点すべて採用し、2 点は私の見落としの指摘だった。

| Codex 指摘 | 検証 | 反映 |
|---|---|---|
| #6 の "landing lane" は PR 用語。単一ユーザーでは「未確定な探索編集を intended commit/push に含めない」に縮約すべき | — | 採用。reference の文言をそう書いた |
| #7 は `references/emergency-definition.md` を**唯一の例外定義**として再利用すべき (二重定義を作らない) | ✅ 該当ファイル実在 | 採用。reference §6 は参照のみにして定義を書かなかった |
| 2x と既存 300 行は衝突せず補完関係。ただし小 diff 用の床 `max(2×初期非テスト LOC, 初期 LOC+50)` を置き、2 回未収束後の再分類を経て**既存の 3 回目を「再分類済 in-scope blocker のみ」に制限**すると `:610` と整合する | ✅ `:610` の 3 サイクル上限を確認 | 採用。この統合形をそのまま実装 |
| **T8 は既に 2026-06-13 に完了**しており `skills/github-pr/SKILL.md` に実装済。保留から外すべき | ✅ `## Parallel Closeout: Format → (Tests ∥ Review)` を verbatim 引用付きで確認 | 採用。Stale-Plan Audit で implemented 判定 |
| T6 は suppression 経路も構造化出力も現状ないため実装でなく **N/A retire**、T9 は heartbeat 実装なしの SLA 文言だけでは誤誘導なので retire、T7 は Scope Governor の最終記録に吸収 | ✅ T7 対象の `synthesis-report.md` に Tests Run がないことを確認 (T7 は本当に未実装だった) | 採用 |
| `.codex/config.toml:5` に `review_model = "gpt-5.6-terra"` という**もう 1 つの pin** がある | ✅ 確認。同ファイル `:1` は `model = "gpt-5.6-sol"` | 私の当初の drift 記述を訂正 (下記) |

## 採用 (2 件)

| ID | タスク | 実装 |
|---|---|---|
| S1 | Scope Governor を 1 mechanism として導入 | `references/scope-governor.md` 新設 (7 概念 + Gotchas)。`skills/review/SKILL.md:606` のサイクルルールに **ルール 0** として 1 行参照を追加 |
| S2 (= 旧 T7) | 最終報告に実行したテストを載せる | `skills/review/templates/synthesis-report.md` に `## Tests Run` セクション追加。openclaw の final report 4 要素 (command / tests / findings / clean) のうち未実装だった tests を埋め、findings は既存 Critical/Important/Watch、clean は Summary の Verdict が担うことをコメントで明示 |

Codex の統合案どおり、既存の 3 サイクル上限は残したまま**中身を制限する**形にした:

```
2 サイクル未収束 → 全 finding を §2 で再分類 → 3 回目は再分類後も
in-scope blocker のものだけを対象 → それでも PASS しなければ既存どおり人間 escalate
```

## 採用 0 (Oversized Bundles)

新規セクションだが採用しない。中身が openclaw の helper script の実装仕様 (8 パス上限 / bundle セクションとファイル境界での分割 / 元 diff の全バイトがパス列に厳密に 1 回だけ出現 / injection-safe な source-line 記録) で、dotfiles には chunking helper がない。

転用可能な原則 2 つは既にカバー済:
- 「chunking は大 diff レビューを実用にするが、1 回のモデル呼び出しに全ての cross-file 実装詳細を与えることはできない。アーキ変更では semantic decision surface が 1 パスに収まるブランチ/PR 形状を選べ」 → `references/pr-splitting-patterns.md` の 300 行閾値と PR 分割方針
- 「レビューを縮めるためだけに lockfile / 生成クライアント / policy / manifest / schema を落とすな」 → dotfiles に review 対象からの機械的除外がないため該当する失敗モードがそもそも起きない

## Validation-only Follow-up: レビュー用モデルの分岐 (採用に数えない)

openclaw の autoreview は既定エンジンが **`gpt-5.6-sol` (high reasoning)** で、`gpt-5.6-terra` は「アカウントが Sol にアクセスできない場合の 1 回だけの retry」。

dotfiles の実態:

| 場所 | 値 |
|---|---|
| `.codex/config.toml:1` | `model = "gpt-5.6-sol"` ← 汎用は既に Sol |
| `.codex/config.toml:5` | `review_model = "gpt-5.6-terra"` |
| `agents/codex-reviewer.md:49` | `codex exec -m gpt-5.6-terra` |
| `agents/codex-plan-reviewer.md:40` | 同 |
| `agents/security-reviewer.md:197` | 同 |
| `scripts/runtime/nightly/*` | `NIGHTLY_CODEX_MODEL` 既定 `gpt-5.6-terra` |

つまり dotfiles は「汎用 = Sol / レビュー = terra」、openclaw は「レビュー = Sol、terra は Sol 不可時のみ」で、**レビュー用途で逆向きに分岐している**。

**`gpt-5.6-sol` はこのマシンから実際にアクセス可能**と実測確認した (`codex exec -m gpt-5.6-sol` が応答)。したがって terra 固定はアクセス不能による fallback ではなく、意図的な選択か情報の古さのどちらかである。どちらかを判定できないままレビューの中核モデルを差し替えるのはリスクが高いため、今回は記録のみとした (ユーザー判断: 「調査してから判断」)。

**併せて記録すべき二次的な問題**: `agents/codex-reviewer.md:113` は `gate_model_version` を Verdict に含め「同一 version が 5 レビュー連続した場合は Evaluator Drift の可能性を明記する」と定めている。しかしモデルがハードコードされているため version は常に同一で、警告は自明に発火し続け、かつ切り替え先が設定されていない。**検出機構がハードコードによって無効化されている**状態。Codex は「実モデルを解決して記録する resolver を入れ、5 連続 PASS の意味付けと異モデル再評価の発動条件は別 Issue に分ける」ことを推奨している。

## Stale-Plan Audit (Phase 1.5 Step 7)

`docs/plans/active/2026-05-28-autoreview-absorb-plan.md` が **60 日間 `status: pending`** だった。frontmatter を `status: closed` + `closed: 2026-07-27` + `closed-by` に更新し、本文冒頭に棚卸し結果の表を追記した。

| Task | 判定 |
|---|---|
| T6 security suppression auditability | **retired** — dotfiles に suppression 経路自体がなく実装対象なし |
| T7 synthesis-report の Tests Run | **implemented (今回)** |
| T8 format → test+review 並列 | **already implemented (2026-06-13)** — 保留リストが陳腐化していた |
| T9 codex worker 30 min SLA 文言 | **retired** — heartbeat 実装なしの SLA 文言は誤誘導 |

ファイルは `active/` に置いたまま。`docs/plans/completed/` は存在するが、その中のファイル自身が `status: active` のままで規約が一貫していないため、移動は見送って frontmatter による状態表明に留めた (別途整理の対象)。

## 実施済

- ブランチ: `fix/careful-freeze-description-drift` (継続)
- `.config/claude/references/scope-governor.md` (新規)
- `.config/claude/skills/review/SKILL.md` — サイクルルールに 0 番を追加
- `.config/claude/skills/review/templates/synthesis-report.md` — `## Tests Run` 追加
- `docs/plans/active/2026-05-28-autoreview-absorb-plan.md` — closed + 棚卸し表
- 検証: `task validate-configs` exit=0 / `task validate-symlinks` exit=0 / `scope-governor` 参照が SKILL.md:606 と template:46 に結線されていることを grep で確認
- 未実施: commit / PR

## 未取得・未検証

- **Gemini 周辺知識補完**: 実行不能
- **Sol vs terra のレビュー品質比較**: 未実施。openclaw が Sol を既定にしている根拠 (ベンチマークか経験則か) も未確認
- `skills/review-loop/` `skills/implement-loop/` の実体位置: 未追跡
- **差分同定の方法**: 5/28 の分析レポートの手法リストとの突き合わせで行った。5/28 時点のソース本文そのものは保存されていないため、「セクション名が当時なかった」ことの直接証拠はない (レポートの 35 手法に対応物がないことが根拠)
