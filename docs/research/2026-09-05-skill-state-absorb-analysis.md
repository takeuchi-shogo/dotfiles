---
date: 2026-09-05
source: "arXiv:2608.26263 — SKILL.state: Scalable Long-Horizon Agent Skills"
authors: "Sanket Badhe, Priyanka Tiwari, Jonghyun Chung"
url: https://arxiv.org/abs/2608.26263
type: absorb-analysis
status: implemented
family: agent-runtime-state (新規、N=1)
---

# SKILL.state absorb 分析

## 記事の主張

append-only の会話履歴を、明示的で mutable な実行 state に置き換える。各ステップでモデルが
受け取るのは不変の skill 仕様 P、構造化 state Σ_t、直近 observation O_t の 3 点だけ。モデルは
`{state_patch, action}` を返し、runtime が patch を検証してから null-deletion semantics の
merge operator で適用する。中間 reasoning は検証通過後に即破棄する。

プロンプト footprint は O(1)、累積トークンは baseline の O(T²) に対し O(T)。

## 手法と根拠

| 手法 | 論文の根拠 |
|------|-----------|
| 履歴を state で置換 (P, Σ, O のみ) | Warehouse T=200 で accuracy 0.94 対 stateful baseline 0.88、累計 122k 対 5.04M tokens |
| reasoning trace の即時破棄 | 同上。プロンプトが実行履歴とともに伸びない |
| `state_patch` JSON delta + null-deletion merge | Appendix A.4 の出力契約: `{"state_patch": {...}, "action": "..."}` の 2 キー固定 |
| runtime 側での決定的検証 + rollback-retry | Algorithm 1 line 6。invalid patch は rollback-retry cycle を起動 |
| schema は domain 単位で 1 回 | "Schemas are authored once per domain rather than per task." InterCode CTF は 100 タスクに 5-field 固定 schema |
| 構造化 > 圧縮 (同一予算) | budget-matched ablation ~1,800 tokens: sliding window 0.18 / LLMLingua 0.22 / SKILL.state 0.94 |

公開ベンチ: InterCode CTF 54.2% 対 ReAct 43.2%、τ-Bench Retail 58.3% 対 48.2%、Airline 32.4% 対 21.8%。
モデルは Gemini-3-Flash (主) / Gemma-4-31B-it / Qwen-3-8B-it。

## 前提条件 (著者自身の Limitations、verbatim 要約)

state が将来実行の *sufficient statistic* であることを前提とする。以下 3 条件で破綻する。

1. schema が事前に決まらず、実行中に動的に発見する必要がある場合
2. ある観測の関連性が後になって判明し、観測時点で state に commit されなかった場合
3. タスクの目的が履歴そのものである場合 (監査、provenance のデバッグ、過去行動の説明)

## Phase 2 判定 (Codex 批評で修正後)

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | 履歴を state で置換 | **Partial (resume domain のみ)** | Claude Code の会話ループは本 repo の制御外。ただし論文も InterCode 100 タスクに固定 5-field schema を使っており、「汎用コーディングに schema は無理」から「resume state にも無理」は飛躍 (Codex 指摘で N/A から格上げ) |
| 2 | reasoning の即時破棄 | N/A (投影は可) | raw CoT の破棄は runtime 制御外。`output-offload.py` は tool output の退避で別物。決定・根拠・dead end・invariant への投影は `handoff-template.md` に素材がある |
| 3 | `state_patch` delta merge | N/A (YAGNI) | state artifact は markdown で Edit tool により部分更新済み = 実質 delta。JSON merge operator の利得なし |
| 4 | 検証 + rollback-retry | **提案撤回** | 当初 `memory-integrity-check.py` の block 化を提案したが対象違い。同 hook の `MEMORY_DIRS` は `~/.claude/projects/*/memory` のみで anchor を見ていない。加えて削除・縮小での block は正当な retirement を止め、文字数は意味保存を測らない (Codex 指摘) |
| 5 | schema は domain 単位 | **Partial** | `resume-anchor-contract.md` は scope/location/lifetime/owner の規約であって anchor 内容の機械検証 schema ではない。2026-09-04 の `success_criteria` scalar/list drift が実証 (Already 強化不要から格下げ) |
| 6 | 3 失敗条件を検査軸に | **Gap (条件付き)** | 条件 (2)「未記録」は静的検査で証明できない。遅延関連性を含む resume fixture でしか評価できない |
| 7 | 構造化 > 圧縮 | **Already (強化可能)** | `pre-compact-save.js` は git / active_plans / offloads を構造化 JSON で渡すが、環境から導けない知識 (棄却した approach、発見した不変条件、決定の理由) は MUST KEEP の散文指示に委ねられている。ablation はまさにその経路が弱いと示す |

### Codex が覆した判定

Phase 2.5 は **Codex のみの degraded 実行**。Gemini は verbatim で
`IneligibleTierError: This client is no longer supported for Gemini Code Assist for individuals.`
を返したため周辺知識補完は未取得。

Codex verdict (要旨): 「全面採用は N/A で正しいが、1・3・5 を N/A/Already と切るのは早い。
実態は局所採用可能な Partial、4 は Already ではなく Partial」。

指摘のうち以下 3 件を実地検証して採用した。

- `RUNNING_BRIEF.md` は `.gitignore:58` で除外 (`git check-ignore -v` で確認)。git 履歴も rollback も監査もない
- `memory-integrity-check.py:24` の `MEMORY_DIRS` は memory/ のみ。anchor は監視対象外
- `doctor-stale.sh` は既存の stale-state inventory で、スキャン節は codex job state と backup residue の 2 つのみ

## 中核の発見

`resume-anchor-contract.md` は 3 anchor に寿命と owner を定義しているが、**owner は書き込み経路で
あって、寿命切れの検出者ではない**。検出者は 3 分の 2 しか存在しなかった。

| Anchor | 寿命 | 検出者 (修正前) |
|--------|------|----------------|
| Plan | 完了まで永続 | `plan-close-detector.py` (nightly) |
| HANDOFF.md | 次セッション開始まで | `session-save.js` が `Stop` で削除 = ターン毎 (寿命を満たさない) |
| RUNNING_BRIEF.md | プロジェクト寿命 | **なし** |

実害: `RUNNING_BRIEF.md` が 104 日 stale。`orphan-artifact-scan.sh` は worktree / branch 専用で
対象外、`.gitignore` 対象で git からも追えないため、どの経路でも観測されなかった。

論文の貢献はここでは実装ではなく **検査軸** だった。「state は将来実行の十分統計量か」を
既存 anchor に当てると、契約が定義しているのに配線がない箇所が出た。

### HANDOFF.md も壊れていた (Codex Review Gate で発覚)

T1/T2 実装後のレビューで Codex が「HANDOFF の契約記述が実装と違う」と指摘し、検証したところ
契約より深刻だった。`session-save.js` は `settings.json` の **`Stop`** に matcher なしで
配線され、`cleanupHandoff()` を無条件で呼ぶ。`Stop` はアシスタントのターン毎に発火するため、
`/checkpoint` が書いた HANDOFF.md は**そのターンの終了時点で削除される**。契約の寿命
「次セッション開始まで」に対し、実際にはセッションを跨げない (Issue #243)。

**修正案の第一版も間違っていた**。`SessionEnd` に移せば直ると考えたが、Codex が
「`session-load.js` は `SessionStart` で HANDOFF を読む設計なので、`SessionEnd` で消すと
次セッションが読む前に消える」と指摘。実地確認して事実だった (`loadHandoff()` が true を
返すと state 復元をスキップする)。正しい配置は**読み手**で、`session-load.js` が読了直後に
retire する。`Stop` は「書いた直後に消える」、`SessionEnd` は「読まれる前に消える」で、
どちらも寿命を満たさない。

### HANDOFF のスキーマが 2 つあった

T4 の lint を書く過程で判明。`references/handoff-template.md` は番号付き 1-5 節
(3.5 Dead Ends / 3.7 検証済み事実を含む) だが、`/checkpoint` が実際に書くのは
`## Goal / Progress / What Worked / What Didn't Work / Next Steps / Context Files`
(`skills/checkpoint/SKILL.md`)。lint を前者だけに向けていたため、実際に生成される
HANDOFF は全節 MISSING になる状態だった。

同じ lens (契約と実装の照合) で、3 anchor 全部に乖離が出たことになる。RUNNING_BRIEF は
検知経路なし、HANDOFF は配線が寿命と不整合かつスキーマが二重、Plan は
`success_criteria` の読み取りが片形式のみ (2026-09-04 に別途修正済み)。

## 採用 (T1-T5 すべて実装済み)

プラン: `docs/plans/completed/2026-09-05-resume-anchor-lifetime-plan.md`

- **T1 (実装済み)**: `doctor-stale.sh` に `[resume anchors]` 節。RUNNING_BRIEF / HANDOFF の
  mtime を既存の `STALE_DAYS` 閾値で報告。プランは `plan-close-detector.py` の所管なので
  再スキャンしない旨を出力に明記
- **T2 (実装済み)**: `resume-anchor-contract.md` の anchor テーブルに「寿命切れの検出者」列
- **T3 (実装済み、対象を変更)**: 当初案の `doc-status-audit.py` は**どこからも呼ばれて
  いない**ため休眠 artifact になる。実害が出る `completion-gate.py` (Stop フック) に移した。
  `success_criteria or COMPLETION_PROMISE` が汎用 env 値を黙って代入し plan 由来のように
  表示していたのを、出所ラベルと欠落警告に置き換え。テスト 4 件追加 (計 12)、
  分岐順の変異で 2 件が赤くなることを確認
- **T4 (実装済み)**: `scripts/lifecycle/resume-anchor-lint.sh` + `task resume-anchor-lint`、
  `/checkpoint` 手順 5 から起動。2 スキーマを判別して MISSING / HOLLOW / ok を判定。
  射程は「形が揃っているか」まで — 「未記録であること」は静的に決定不能なので、
  pass を「再開できる」の根拠にしない旨をスクリプト冒頭と契約に明記
- **T5 (実装済み)**: HANDOFF の retire を読み手 (`session-load.js`) に移動

## Validation-only Follow-up

記事由来の新規ルールではないが、この lens で露出した実態。

1. **`docs/plans/active/` に 31〜137 日未更新のプランが 24 本**。T1 の初回実行で判明。
   当初「`plan-close-detector.py` は完了済みプランしか見ないので未検出」と書いたが誤り。
   Codex 指摘で `plan-close-detector.py:179` を確認したところ `stale_days >= stale_threshold`
   で `Verdict("STALE", 3)` を返しており、24 本は**検出済み**。ただし Tier 3 は report-only で
   自動 PR 対象外なので、報告が nightly に出続けているのに誰も処理していない状態。
   検出の欠落ではなく、報告の消費者不在
2. **`RUNNING_BRIEF.md` の残存項目の退避** (削除前の salvage、他に追跡先がないもの):
   - `init-install.sh` のうち nix-darwin に吸収できる部分の切り分け (377 行は CLI setup と
     symlink のみで `defaults write` は不在と判明済み)。親プランは completed
   - B2.2 の `home.activation.shareSkills` を `home.file` の動的生成 (`builtins.readDir`) に
     置換するか。親プランは completed
   - `docs/inventory/` の secret 漏洩 scan (`defaults read` 出力に token 混入の有無)
   - memory-vec top-K の noise 検証 (top-3 までは概ね関連、top-5 後半に false positive)
   
   追跡先が既にある項目は退避不要と判断した: memory-vec 次フェーズ → Issue #100、
   REVIEW GUARD の session 境界 → Issue #52、Codex CLI 到達不能 → Issue #55。
   Phase C/D 系の Open Questions は親プラン 4 本がすべて `docs/plans/completed/` にあり、
   移行終了時点で暗黙に取り下げられている。

## 不採用と理由

- **runtime アーキテクチャの全面移植**: Claude Code の会話ループは本 repo の制御外。加えて
  著者の Limitation (1)(2) が汎用コーディングセッションに直撃する
- **`memory-integrity-check.py` の block 化**: 対象 artifact 違い + 正当な retirement を止める +
  文字数は意味保存を測らない
- **`state_patch` JSON merge operator の導入**: markdown を Edit で部分更新している時点で
  実質 delta が成立しており、機構を足す利得がない

## 数値の扱い

論文の error analysis「Premature State Overwrite / Deletion 68%」は **open-weight モデル
(Gemma-4-31B-it / Qwen-3-8B-it) の失敗分析** であり、主実験の Gemini-3-Flash や本環境の
Opus の失敗率ではない。state 破壊を最頻失敗モードとして扱う根拠には使えるが、
閾値設計の根拠には使えないため割り引いた。
