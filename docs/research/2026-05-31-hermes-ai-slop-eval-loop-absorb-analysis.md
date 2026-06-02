---
source: "How To Fix AI Slop (Using Hermes)"
author: "Hermes (vendor marketing, anonymous)"
date: 2026-05-31
status: reference-only
adoption: 0
family: eval-loop-quality-gate (unregistered, N=1)
related:
  - docs/research/2026-05-30-hermes-harness-architecture-absorb-analysis.md
  - .config/claude/references/observability-signals.md
  - .config/claude/references/improve-policy.md
---

# How To Fix AI Slop (Using Hermes) — Absorb 分析

> **結論: Reference-Only / 採用 0 件**。3 者一致 (Opus 分析 + Codex 批評 + Gemini grounding)。
> dotfiles の eval 基盤は Hermes より成熟しており、記事が最も強く推す auto-close-loop (failure→test 自動化) は
> `/improve` として 2026-05-03 に false-positive 多発で **意図的に retire 済み**。記事の主張は dotfiles の判断と逆行する。

## Source Summary

**主張**: AI slop は prompt 問題ではなく **systems 問題**。欠けているのは出力を出荷前/後に標準と照合する
**eval loop（品質ゲート）層**。「good を定義 → 0-1 数値化 → 全出力をスコアリング → threshold 未満を gate →
failure を new test case に変換して quality floor を自動上昇」。Hermes (open-source agent) の skills/memory/cron/
approval button で実装する 6 ムーブを提示。

**手法 (10 項目)**:
1. eval loop の 3 配置 — before-ship regression test / runtime guardrail / production continuous sampling
2. benchmark 3 要素 — test cases + ground truth / metric (0-1) / threshold (0.7)
3. content rubric 4 基準 — specific / accessible / structured / novel + bookmark meta-criterion
4. product metric をタスクに合わせる — exact match / validator / semantic similarity + judge
5. LLM-as-judge を再利用可能な skill 化 (procedural memory)
6. gold standard (お手本 20-50 件) を memory に格納
7. eval suite を skill 化 (spreadsheet ではなく versioned)
8. regression gate + approval button + score delta vs baseline
9. production cron 監視 + 品質低下 alert
10. failure → new test case 自動追加 (thumbs-down → 恒久テスト、floor 自動上昇)

**根拠**: 「nous found agents with 20+ self-created skills finish 40% faster」「score 0.82→0.61 はデバッグ可能、
vibe はデバッグ不可」(いずれもベンダー自社主張、評価バイアス前提)。

**前提条件**: Hermes (telegram/slack approval、/goal、multi-agent kanban、built-in cron) を導入し、
かつ **content production / productized AI feature** を出荷する用途。個人 harness 文脈とは前提が異なる。

## Gap Analysis (Pass 1: 存在チェック / Sonnet Explore)

dotfiles は 10 手法のうち 70% を既存実装。`scripts/eval/` (run_reviewer_eval.py / aggregate_benchmark.py /
regression-gate.py / split_holdout.py) + `references/benchmark-dimensions.md` + 5 reviewer agent +
`skill-audit` / `empirical-prompt-tuning` + `scripts/learner/` パイプラインが該当。

## Integration Decisions (Pass 2 + Phase 2.5 修正後)

Phase 2.5 で Codex (gpt-5.5, read-only) + Gemini (Google Search grounding) を並列起動。
Codex が Opus Phase 2 の **Already 過大評価を 3 件修正** (採用判断は不変)。

| # | 手法 | 最終判定 | 理由 |
|---|------|---------|------|
| 1 | eval loop 3 配置 | **Partial** | (a)regression-gate.py + (b)error-rate-monitor.py 実装。(c) prod 成果物品質サンプリングは observability-signals.md §3 Gap として既知追跡 |
| 2 | benchmark 3 要素 | **Partial** (当初 Already) | ground truth tuple + threshold は存在するが、継続運用される benchmark **loop** までは含まない (Codex 指摘) |
| 3 | content rubric | **Already** | adversarial-evaluation-criteria.md(4D)/skill-audit 5D/routine-prompt-rubric。個人 dotfiles で content-business 用 rubric 追加価値は薄い |
| 4 | product metric | **Partial** | exact match + validator 実装、semantic judge 汎用 library 未標準化 |
| 5 | LLM-as-judge skill 化 | **Already** ("より高度" は削除) | 5 reviewer agent + review-consensus-policy。ただし同 policy 自身が reviewer 増加の劣化・合意不信を明記 → 「Hermes 単一 judge より常に上」は言い過ぎ (Codex 指摘) |
| 6 | gold standard を memory | **N/A** | 少数 exemplar 思想は improve-policy.md に存在するが、「お手本 20-50 件」は content business 前提。/improve retire 後で今採る話でない |
| 7 | eval suite skill 化 | **Already** | skill-audit (A/B orchestration) + empirical-prompt-tuning + versioned JSON suite |
| 8 | regression gate + delta | **Partial** (当初 Already) | regression-gate.py は tuple shape/reviewer 名を検証するだけで agent 出力を再評価していない。aggregate_benchmark は結果実行済み前提 (Codex 指摘) |
| 9 | prod cron 監視 + alert | **Partial** | error-rate-monitor + session-observer + friction-weekly-digest 実装。品質低下の自動閾値 escalation は Gap 1/3 として既知追跡 |
| 10 | failure → auto test | **N/A (再導入禁止寄り)** | failure-clusterer→eval-generator パイプラインは存在するが `/improve` retire (2026-05-03, false-positive 多発) で意図的切断。Hermes 流回帰は後退 |

**採用**: なし (0 件)。**スキップ**: 全 10 項目。

## Phase 2.5 Refine — Codex + Gemini 批評

### Codex (gpt-5.5, read-only) — 分析批評
- 結論「**採用 0 件で妥当**」に同意。ただし Opus 判定は楽観的で、Already のうち #2/#8 は「設計・構造はあるが
  実行型 eval loop としては未接続」へ降格すべき (#2 Already→Partial, #8 Already→Partial, #5 "より高度" 削除)。
- **見落とし指摘**: 記事の核心は「rubric がある」ではなく「失敗を再実行して閾値で止める」。regression-gate.py は
  tuple shape 検証止まりで agent 出力を再評価していない。prod sampling も成果物品質ではなく Bash error spike 中心。
- **鋭い meta 指摘**: 「個人 dotfiles では "output slop" より **"harness false-positive / cognitive load /
  stale signal"** の方が支配的」。記事の前提フレーム (出荷物の slop) がこのユーザーの harness の支配的失敗モードと
  噛み合っていない。
- **優先度**: Hermes 由来ではなく既存 Gap の消化 (Gap 1 CFS realtime warning / Gap 2 failure-clusters 読み手接続) が筋。

### Gemini (Google Search grounding) — 周辺知識補完
- **成功事例** (LLM-as-judge eval loop): Airbnb (移行 1.5 年→6 週、97% 自動化) / DoorDash (検索評価 TAT 98% 削減) /
  Instacart (eval データで小型モデル学習、推論コスト 99% 削減)。ただし全て productized AI feature 文脈。
- **auto-close-loop の落とし穴** (記事が触れない): **Self-Preference Bias** (自系統出力を過大評価し低品質を正解化) /
  **Model Collapse** (合成データを ground truth にし続けると多様性喪失) / **Oracle 問題** (外部審判不在だと
  バグが「仕様」として回帰テストに lock-in)。→ `/improve` retire 判断を裏付ける。
- **2025-26 動向**: 単一 judge → **PoLL (Panel of LLM evaluators, 異種 family 合議)** が主流 / PRM (Process Reward
  Models) / 特化型評価モデル (Prometheus 2/Luna-2) / 分類器カスケード。HITL calibration をどこに差すかに議論集中。
  → dotfiles の review-consensus-policy (heterogeneous judge) は PoLL を既に体現。AskUserQuestion ゲートは HITL。

## Validation-only Follow-up (採用ではないが actionable な気づき)

| 対象 | 露出した事実 | 訂正/対応方針 |
|------|------------|-------------|
| 自己分析の Already 判定 | Opus Phase 2 が `scripts/eval/` 群を一律 "Already" と過大評価。実体は構造検証止まりで live eval loop は未接続 (regression-gate.py は再評価せず tuple shape のみ検証) | 本レポートで Partial へ降格済み。observability-signals.md §3 Gap 1/2 と同根。**新規作業はしない** (/improve retire の教訓: auto-loop 再接続は false-positive/認知負荷リスク)。記録のみ |

## 棄却理由まとめ

1. **基盤成熟度の逆転** — dotfiles の eval 基盤 (5 reviewer agent + consensus policy + benchmark-dimensions 6次元 +
   skill-audit + scripts/eval/) は Hermes が提示する primitive より成熟。記事は新規 capability を加えない。
2. **前提フレームの不一致** — 記事は content business / productized AI feature 前提。個人 dotfiles の支配的失敗モードは
   output slop ではなく harness false-positive / cognitive load / stale signal (Codex)。
3. **最重要 move (#10 auto-close-loop) は意図的後退済み** — `/improve` を false-positive 多発で 2026-05-03 retire。
   Gemini の Self-Preference Bias / Model Collapse / Oracle 問題も再導入リスクを裏付ける。
4. **ベンダーマーケティング** — 数値主張 (40% faster, 0.82→0.61) は自社訴求、評価バイアス前提。Hermes 記事 2 件目
   (前日の harness-architecture も同傾向)。

## メタ学習

- Phase 2.5 が機能した好例: Codex が Opus の Already 過大評価を 3 件是正 (採用判断は不変だが、レポートの正確性向上)。
  bias mitigation の価値を再確認。
- Codex 初回呼び出し (`2>/dev/null` + xhigh reasoning) が**サイレント失敗** (stdout "prompt ready" のみで終了)。
  stderr 捕捉 + medium reasoning で再試行して成功。memory `feedback_codex_casual_use.md` の既知パターン再現。
  教訓: Codex 分析批評では `2>/dev/null` を避け stderr を捕捉する。
- Gemini grounding が「記事が触れない落とし穴」を 3 つ提示し、棄却根拠 (auto-loop リスク) を独立に補強。
