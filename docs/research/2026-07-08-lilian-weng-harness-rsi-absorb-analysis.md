---
title: "Harness Engineering for Self-Improvement (Lilian Weng) — absorb 分析"
date: 2026-07-08
status: light-phase2-only
source:
  title: "Harness Engineering for Self-Improvement"
  author: Lilian Weng (Thinking Machines Lab)
  url: https://lilianweng.github.io/posts/2026-07-04-harness/
  published: 2026-07-04
  via: "@SakanaAILabs 引用ツイート (https://x.com/SakanaAILabs/status/2074489949529776308)"
  type: primary-survey
family: harness-engineering / RSI / meta-evolution
saturation_gate: SATURATED-but-novel (N≫3, 採用率低, delta≈2)
phase_2_5: skipped (light-phase2 + rehash 判定は improve-policy.md verbatim 引用に基づく事実のため self-preference bias 無し。Gemini は IneligibleTierError で degraded)
---

# 要旨

Lilian Weng の一次サーベイ。「RSI (recursive self-improvement) は、モデルが自分の重みを直接書き換える前に、まず **harness (モデルを取り巻く実行系)** の最適化として進む」と論じる。

**absorb 結論**: この記事は dotfiles harness corpus にとって **新規知識の供給源ではなく、既存方針の一次ソースによる validation**。記事が引用する一次文献 (ACE / MCE / Meta-Harness / ADAS / AFlow / DGM / Hyperagents / AutoHarness / GEPA) を corpus は既に名指しで吸収済 (多くは improve-policy.md のルールとして、サーベイより深い実装粒度)。さらに dotfiles は記事が前提とする「重い自己改善機構」を **意図的に退役** させた歴史を持つ (/improve 5サイクル連続 false-positive → 2026-05-03 退役、eval 機構 2026-06-21 削除、人間承認ゲート付き軽量ループへ縮退)。記事の中核主張「evaluator と permission control は進化ループの**外側**に置く」は Rule 22 + RSI governance B1 で先取り済。

# Source Summary (周辺知識)

## 記事のフレームワーク (原文の固有名詞)

### Context Engineering (3層の深さ)
- **ACE** (Zhang+ 2025): context を「進化するプレイブック」として扱う。Generator/Reflector/Curator。構造化 bullet を決定論的マージし context collapse と brevity bias を防ぐ。
- **MCE** (Ye+ 2026): ACE を一段深め「context の管理 (mechanism)」と「context の中身 (content)」を分離した bi-level 最適化。
- **Meta-Harness** (Lee+ 2026): 「どの情報を保存・検索・提示するか決めるコード自体」を最適化。proposer はコーディングエージェント、出力は Pareto frontier 上の harness 候補集合。実行履歴は FS 経由 (grep/cat)。

### Workflow Design
- **AI Scientist** (Lu+ 2026, *Nature*): アイデア→コード→実験→分析→執筆→peer review パイプライン。
- **ScientistOne** (Meng+ 2026): verifiability 中心設計、全主張が evidence source に遡れる Chain-of-Evidence。
- **Autodata** (Kulikov+ 2026): challenger/weak solver/strong solver/verifier で「適切な難易度」の訓練データ合成。限界: strong solver を反復改善できないと「間接蒸留」に留まる。
- **ADAS** (Hu+ 2025): meta-agent search。agent 設計を最適化問題として archive ベースで探索。
- **AFlow** (Zhang+ 2025): workflow をグラフ (ノード=LLM呼び出し, エッジ=コード) 化し MCTS で最適化。

### Evolutionary Search
- **Promptbreeder** (Fernando+ 2023): mutation prompt 自体も進化。
- **GEPA** (Agrawal+ 2025): reflection + evolutionary search。
- **AlphaEvolve** (Novikov+ 2025): `# EVOLVE-BLOCK-START/END` で進化対象コード領域を明示。メタプロンプト共進化。
- **ThetaEvolve** (Wang+ 2025): evolutionary + RL + ICL。
- **ShinkaEvolve** (Lange+ 2025): (1) parent sampling でサンプル効率化 (2) embedding cosine 類似度による code-novelty rejection sampling (3) meta-scratchpad。
- **DGM (Darwin Gödel Machine)** (Zhang+ 2025): agent が自分の harness コードを編集。Claude 3.5 Sonnet ベースで SWE-bench 20→50%, Polyglot 14.2→30.7%。
- **Hyperagents** (Zhang+ 2026): DGM に meta-agent を導入。

### Joint Optimization (harness + weights)
- **STOP** (Zelikman+ 2023): improver $I$ 自体を再帰改善。**cautionary result**: GPT-4 では向上したが GPT-3.5/Mixtral では劣化 — 再帰構造だけでは不十分、ベースモデルが十分 capable である必要。
- **Self-Harness** (Zhang+ 2026): propose-evaluate-accept。(1) weakness mining (verifier-grounded 失敗クラスタ) (2) harness proposal (3) held-in $D_{in}$ + held-out $D_{out}$ **両方で regression が無い時のみ採択**。
- **SIA** (Hebbar+ 2026): harness 改善とモデル重み更新を同一ループに。著者自身「evidence は暫定的」と評価。

## Future Challenges (記事の課題列挙)
1. Weak/fuzzy evaluators — research taste/novelty は測定困難
2. Context/memory lifecycle
3. Negative results — 文献は成功に偏る、失敗試行を保存しやすくすべき
4. Diversity collapse — population が高報酬パターンに collapse
5. Reward hacking — **evaluator と permission control は進化ループの外側に置く** (held-out tests, trace audits, human review at decision points)
6. Long-term success — 最適化ゴールが短期的すぎ、リポジトリの長期健全性 (maintainability/ownership/migration cost) を守れない
7. Role of humans — "Humans should move up the stack, not be removed from the loop"

Trehan & Chopra (2026) の **6 failure modes**: training-default bias / implementation drift / memory degradation / over-optimism ("numerical duct tape", p-hacking and eureka-ing) / insufficient domain intelligence / weak scientific taste

## ベンチマーク (記事末尾)
PaperBench (best ~21%, ML PhD 未満) / CORE-Bench / ScienceAgentBench / RE-Bench (2h で人間の4倍だが 8-32h では人間が上回る) / MLE-bench / KernelBench

# Saturation Gate — per-method 照合台帳 (事実)

| 記事の手法 | verdict | corpus 内照合先 |
|---|---|---|
| ACE | rehash | `2026-03-24-ace-*.md` + improve-policy Rule 11 |
| Meta-Harness | rehash | improve-policy Rule 13/32/38/39 (直接引用) |
| ADAS / AFlow | rehash | improve-policy Rule 45 |
| GEPA | rehash | improve-policy Rule 44 |
| DGM | rehash | `2026-03-29-hyperagents-dgmh-analysis.md` |
| Hyperagents | rehash | improve-policy Rule 29/30/31 |
| AutoHarness | rehash | improve-policy Critic-Refiner 分離原則 |
| diversity collapse | rehash | `diversity-selection.md` |
| reward hacking | rehash | Rule 21-23 + `gaming-detector.py` + RSI gov B1 |
| human up the stack | rehash | ADR 0008 |
| MCE | ambiguous | ACE/Meta-Harness の中間層。bi-level 単体は未名指し |
| ShinkaEvolve/AlphaEvolve/Promptbreeder | ambiguous | `meta-evolution.md` に進化探索知見あり、個別名は薄い |
| STOP cautionary | ambiguous | /improve 退役 (5サイクル false-positive) の外部裏付け |
| ScientistOne | ambiguous | completion-gate Claim Verification Gate に近い |
| **Self-Harness** | **novel** | 該当なし → adopt |
| **6 failure modes** | **novel (verify後に大半却下)** | 下記 |
| **long-term repo health** | **novel** | 該当なし → adopt |
| AI Scientist/Autodata/SIA | novel-but-N/A | 重み更新・訓練データ合成前提。dotfiles は config/skill update のみ |

# Phase 2 Pass 2 判定 (実ファイル照合)

## adopt: Self-Harness の両側 regression gate
- **判定**: novel。live promotion loop の design doc (`docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md`) Wave3 entry requirements に regression gate は無い。
- **取り込み**: 同 design doc に **B4** を追加。held-in + held-out **両方**で regression-free の提案のみ採択、を「Wave3 が非 mechanical 昇格に scope 拡張する場合の precondition」として codify。
- **制約 (事実)**: eval-generator/regression-gate は 2026-06-21 削除済。mechanical 限定の現行 Wave3 では変更が deterministic ゆえ N/A。scope 拡張時に holdout eval harness 再建が前提。overbuild しないため precondition 記載に留めた (機構は今ビルドしない)。

## reject (verify で覆った): 6 failure modes の bulk-add
- failure-taxonomy.md (FM-001〜021) と照合した結果:
  - #4 over-optimism / numerical duct tape / p-hacking → **FM-016 (Result Fabrication) が "Vibe Physics" p-hacking として既にカバー** (rehash)
  - #5 scientific taste / #6 domain intelligence → taxonomy の **binary 判定制約 (9行目) に違反して operationalize 不能**。かつ autonomous research agent 固有 (dotfiles は非該当)
  - #1 training-default bias → FM-003 (Dependency Drift) と overlap
  - #2 implementation drift → FM-011 (Plan Adherence, drift channel) と overlap
  - #3 memory degradation → 対応 FM なしだが per-turn 検出困難
- **結論**: 6件 bulk-add は「記事を無批判に受け入れる」anti-pattern。却下。FM-016 が唯一の clean match で既存。

## adopt: long-term repo health 盲点
- **判定**: 唯一の in-scope な純 novel。per-turn FM ではなく **最適化ループの目的関数の限界**。
- **取り込み**: 同 design doc の未解決事項に追加。目的関数 (agreement rate / mechanical 捕捉率) が単発 artifact の正しさに閉じ、maintainability/ownership/migration cost を測らない盲点を明示 (codify のみ、機構化は YAGNI)。

# Validation-only Follow-up (採用件数に数えない)

| 対象 | 記事が露出させた事実 | 方針 |
|---|---|---|
| /improve 退役決定 | STOP cautionary result (再帰だけでは不十分、base model 依存) が退役判断の外部裏付け | decommission-log の判断根拠として引用可 (今回は codify せず、この report に記録) |
| Rule 22 + RSI gov B1 | 記事「evaluator/permission を進化ループの外側に」を先取り済 | 変更不要。方向一致の確認 |
| RSI gov plan の design doc 参照 | 参照先は `docs/superpowers/specs/` 配下に実在 (drift 無し) | 確認のみ |

# 変更ファイル

- `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md` — Wave3 に B4 (両側 regression precondition) + 未解決事項に long-term repo health 盲点を追加 (additive, 出典明記)

# 教訓

- **飽和 family でも一次サーベイは validation として価値**: 採用 2 件 (+ codify のみ) だが、記事が corpus の既存方針を frontier lab の一次文献で裏付けた。「採用0≠得るものなし」の逆で「採用少≠得るものなし」。
- **Pass 2 verify が事前サマリを覆した**: Phase 1 の楽観的 delta (6 failure modes 取り込み可) が実ファイル照合で「4/6 既存 or 非operationalize」に縮小。absorb の Pass 2 = 実ファイル引用照合の価値を再確認。
- **退役方向との整合**: dotfiles は記事が前提とする重い自己改善機構を意図的に退役済。記事の「adopt this RSI technique」の大半は saturated かつ現行の deliberate direction (人間承認ゲート付き軽量ループ) に逆行する。
