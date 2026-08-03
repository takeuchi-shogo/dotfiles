---
title: "Do Context Files Help Coding Agents? A Two-Agent Ablation Study on Real Repositories (absorb 分析)"
date: 2026-08-02
source_url: https://arxiv.org/abs/2607.27250
source_retrieval: "alphaxiv.org の overview.md → abs.md で全文取得 (alphaxiv は trusted domain、Sonnet 委譲で verbatim 引用を保持)"
source_author: "Prakhar Khatri (独立研究者)"
family: agentic-instruction-following (N=2) / context-file クラスタ (N=6) の両方に該当
saturation: "PASS (warning) — taxonomy 登録 4 family は閾値未満だが、未登録の context-file クラスタ (agents-md-* ×3 / 12-rule-claude-md / anthropic-context-engineering / handbook-md) で N=6・採用率 50% 以上。SATURATED ではないため delta 計算は不要"
status: implemented
scale: S ×3
adopted_tasks:
  - "T1: skill-audit の検出力ガイダンス修正 (反復回数 vs 独立タスク数 / 床・天井の事前確認)"
  - "T4': dead-weight-scan-protocol の ablation に検出力の床を明記"
  - "T6: holdout_accept_gate の verdict に sample_sizes を追加"
rejected_tasks:
  - "T2: 放棄済 canary への再挑戦条件追記 (論文固有の数値を別目的の実験に誤移植する)"
  - "T3: 失敗トリアージ軸『事実欠落 vs スキル欠落』の新設 (failure-taxonomy の specification/generalization と Graph-vs-Prompt 診断が先取り済み)"
  - "T5: benchmark-dimensions への turn 非可搬性の注記 (指針として読む consumer が存在しない)"
  - "3-arm ablation / process-cost の主判定昇格 (論文の SELECTIVE arm 自体が corpus 10x-18x で交絡)"
related:
  - docs/research/2026-07-31-handbook-md-instruction-following-absorb-analysis.md
  - docs/research/2026-07-31-boris-cherny-yc-ablation-absorb-analysis.md
  - docs/research/2026-07-25-anthropic-context-engineering-claude5-absorb-analysis.md
---

# Do Context Files Help Coding Agents? — absorb 分析

## Source Summary

### 主張

Claude Code と Codex、実リポジトリ 3 件 (pdm / firebase-admin-python / opshin)、288 評価 run による within-task paired ablation。context 注入戦略 (NONE = `AGENTS.md` 削除 / ALWAYS ON = 毎ターン system prompt 注入 / SELECTIVE = wiki を workspace に置き retrieval hint のみ) は **正答率を測定可能な形で動かさない**。失敗要因は「不足しているリポジトリ知識」ではなく「実装スキル (機能設計・パターン選択・正確な配線)」だった。

### 根拠 (verbatim)

| 項目 | 引用 |
|---|---|
| 規模 | "17 real tasks from 3 repositories (15 shared + 2 Codex-only), and 288 evaluated runs" |
| Claude 正答率 | NONE 53.3% / ALWAYS ON 55.6% / SELECTIVE 55.6%、"Omnibus p 1.000" |
| Codex 正答率 | NONE 58.8% / ALWAYS ON 56.9% / SELECTIVE 52.9%、"Omnibus p 0.66" |
| 同値境界 | "TOST on the task-clustered bootstrap bounds every pairwise strategy difference to <10pp for Claude and <15pp for Codex" |
| 唯一の有意差 | "SELECTIVE uses significantly less cache-creation tokens than NONE (unanimous 11/11 tasks lower; p=0.001, p_Holm=0.012)" |
| 著者の釘刺し | "we read this cache result mechanically rather than as a strategy benefit ... not from context making the agent more capable" |
| Codex 効率 | "All efficiency metrics are flat across strategies: tool calls 32/32/32, output tokens ±3.8%, duration ±3.8% (all \|d_z\|<0.2)" |
| dose-dependent | opshin の blind full-suite 実行が NONE 3.67 → ALWAYS ON 2.44 → SELECTIVE 1.67 (p=0.25, n=4、exploratory 扱い) |
| 検出力 | "MDE at n=17, reps=3: even a large Δ=30pp effect is caught only 57% of the time" |
| 必要規模 | "Detecting Δ=10pp at 80% power requires ∼120–200 tasks" |
| 反復の無力 | "Adding repeats barely helps (n=17, reps 3→10: power increases 13%→58% for Δ=15pp)" |
| 難易度の agent 依存 | "Spearman ρ=0.75, p=0.001"、15 共有タスク中 6 件が片方の agent でだけ borderline |
| manipulation probe | "the real AGENTS.md never converts a near-miss to a pass" (Codex は 18/18 全滅) |

### 前提条件 / 論文が明示する限界 (verbatim)

- **測定対象は散文的 context file**。hook / deny rule / 実行を止める mechanism ではない
- "4. Ecological validity. Our ALWAYS ON condition injects context via system prompt every turn, which is stronger than the natural workflow ... **this is an inference, not a direct measurement.**"
- "5. Selective is our construction, and its corpus is not content-matched" — pdm / firebase の wiki は `AGENTS.md` の 10x / 18x の語数
- "6. Inert-manipulation concern. Our context files are naturalistic (not purpose-built for specific tasks). ... **Whether purpose-built, task-specific context (a fact the agent provably cannot infer) would help remains an open question for future work.**"
- "3. Injection-channel asymmetry. Claude receives context via system prompt; Codex via user-turn prepend"
- "7. Model-version snapshot ... claude-sonnet-4-6 and gpt-5.5"
- Python 限定 3 リポジトリ、root `AGENTS.md` 1 枚、競合する instruction stack なし

## Phase 1.5: Saturation Gate

taxonomy 登録の 4 family (`obsidian-second-brain` / `skill-graphs` / `harness-engineering` / `claude-code-tips`) はいずれも閾値未満。`harness-engineering` は `harness` 1 hit のみで 3 hit に届かない。

ただし未登録の「context-file / instruction-doc」クラスタが実在する (`agents-md-review-skills` / `agents-md-generator` / `agents-md-patterns` / `12-rule-claude-md` / `anthropic-context-engineering-claude5` / `handbook-md`)。**誤分類リスクを安全側に倒し、広い側で数えた**。

- N=6、採用率 ≥ 50% (integrated ×2 + 採用 4 件 ×1 が下限) → **PASS (warning)**
- Step 4.5 連続 reject トレンド: 直近が「採用 4 件」なので不発
- SATURATED ではないため Step 3.7 の delta 計算は不要

### Step 7: Stale-Plan Audit

`docs/research/2026-05-10-12-rule-claude-md-absorb-analysis.md` が 84 日 `status: analyzed` のままだった。採用タスク T1/T2 の実装状況を実ファイルで照合した結果、**全て実装済み** (commit `3f21862e`):

| task | 確認箇所 |
|---|---|
| T1.1 test runner 例外の fail loud 化 | `completion-gate.py:224-229` の `return False, f"test runner exception: {exc}"` |
| T1.2/T1.3 `except: pass` → stderr warning | `checkpoint_manager.py:241-244` / `:253-258` |
| T2.1 Test Intent Rubric | `review-dimensions.md:21-28` |

→ frontmatter を `status: implemented` + `implementation_commit` + `verified_by` に更新。

## Phase 2: Gap Analysis

### Pass 1 / Pass 2 判定

| # | 手法 | 判定 | 現状と根拠 |
|---|---|---|---|
| 1 | context file への投資を correctness 期待で正当化しない | Partial | `dead-weight-scan-protocol.md:59-108` が「振る舞い指示 = default unproven」の極性反転を既に持つ |
| 2 | NONE / ALWAYS ON / SELECTIVE の 3 水準 ablation | Partial → **不採用** | 同 `:89-93` は baseline vs minimal の 2 水準。3rd arm は Phase 2.5 で棄却 (下記) |
| 3 | TOST による bounded null | Partial (理由訂正) | `evaluator_metrics.py:204` の `bootstrap_ci` は**評価器の Rogan-Gladen 補正率の CI** であって処置間 paired difference の等価検定ではない。実装は不要だが「機能代替済み」とは言えない |
| 4 | agent-specific task screening / borderline band | **Gap** | skill-audit の borderline は Step 2 の**プロンプト類型** (ドメイン境界) であって、pass rate が中間帯にあるタスクの選定ではない。別概念 |
| 5 | turn-count metric の非可搬性 | Partial → **不採用** | `model-debt-register.md` と T8 不採用の個別事例のみ。追記先の `benchmark-dimensions.md` に consumer なし |
| 6 | manipulation-validity probe | Partial → **不採用** | `docs/spikes/instruction-compliance-canary-abandoned.md` が既に「baseline が discriminative でない」「単発では距離減衰を測れない」を記録済み |
| 7 | process 効果と outcome 効果の分離 | Already (強化不要) | `evaluator-calibration-guide.md:11-21` "Outcome over Trajectory"、`benchmark-dimensions.md:72-81` で列を分離 |
| 8 | dose-dependent な段階観測 | not_found → **不採用** | #2 に統合。3 水準化の根拠自体が交絡している |
| 9 | Monte Carlo power analysis / MDE | **Gap** | `skill-audit/SKILL.md:513` の「最低 5 回、理想は 10 回以上」は反復回数の目安で、論文の実測と方向が食い違う |
| 10 | portable metric と agent-specific metric の切り分け | Partial → **不採用** | #5 に統合 |
| 11 | 失敗の「知識欠落 vs 実装スキル欠落」トリアージ | Partial → **不採用** | `failure-taxonomy.md:480-492` の specification / generalization と `:604` の Graph-vs-Prompt 診断 ("a better prompt is unlikely to be the real fix") が先取り済み |
| 12 | egress-locked pod による agent 隔離 | N/A (理由訂正) | deny 88 件は実在するが、**worktree は branch/filesystem 分離であって egress lock ではない**。日常 harness に pod は過剰 |
| 13 | gold test / oracle 評価 | Already (表現訂正) | `completion-gate.py` は `task test` を検出して**公開 suite** を実行する。論文の agent 非開示 PR gold test とは別物で、hidden-test evaluation を持つとは言えない |
| 14 | 文書品質のルーブリック自己評価 | N/A | 論文自身が self-assessed と限界に挙げ、かつ**高品質と自己評価した文書でも null だった**。導入は逆方向 |
| 15 | 反復回数より対象数が検出力に効く | **Gap** | #9 に統合 |

## Phase 2.5: Refine (degraded)

**Gemini は利用不能**。verbatim:

```
Error authenticating: IneligibleTierError: This client is no longer supported for
Gemini Code Assist for individuals.
```

cmux も不在 (`[launch-worker] cmux is not available.`) のため、CLAUDE.md 規定の fallback `codex exec --sandbox read-only` で **Codex 2 本を役割分担**して起動した。model-family diversity は Codex 単独のため **degraded**。

- spoke A (分析批評): 判定の見落とし・過大/過小評価・前提の誤り・優先度
- spoke B (配線検証): 追記先が休眠 artifact でないか、参照元が実在するか、既存記述と重複しないか

### spoke A が修正した判定

| 論点 | 修正 |
|---|---|
| 3-arm ablation | **棄却**。dead-weight scan の目的は「残すか消すか」で配送経路の因果分離ではない。加えて論文の SELECTIVE arm は 2/3 repo で corpus が 10x/18x に変わっており、3-arm 化の根拠にむしろ不適 |
| process-cost の主判定昇格 | **棄却**。現行プロトコル `:95-108` が再指示・人間介入・検証実行率・安全判断・token・時間を既に測る。correctness/safety を process cost に置換するのは逆行 |
| T2 (canary 追記) | **棄却**。120-200 と 10-15pp は binary context ablation の数値で、別目的の policy-compliance canary に誤移植になる |
| T3 (トリアージ軸) | **棄却**。既存の specification/generalization と Operational Contract の昇格ゲートで足りる |
| 私の「Limitation 6 で dotfiles は射程外」論法 | **自己都合な逃げ道と判定**。`.config/claude/CLAUDE.md` の大半は委譲・plan・review・DRY といった一般的行動規則で、論文の null が最も直接当たるのはそこ |

### spoke B が止めた追記

- **`improve-policy.md` への追記を阻止** — 同ファイルは `status: deprecated` (`deprecated_at: 2026-05-03`)。現役の skill と退役済み policy に同じ検出力規則を並行追記すると「実行されないのに設定バージョンには混ざる二重の権威」が残る。spoke A は Rule 8 の改称を勧めていたので、**A の勧告を B が潰した**形になる
- **`benchmark-dimensions.md` への注記を阻止** — 内容を指針として読む skill / agent / hook / CLAUDE.md の参照元がゼロ。`gaming-detector.py:55` はファイル名を保護対象文字列として持つだけで本文を読まない
- `skill-audit` は `skillOverrides` 48 件のいずれにも入っておらず**有効** → T1 の追記先は生きている

### 私が実ファイルで反証した主張

- spoke A の「`task nix:switch PROFILE=private` は CLAUDE.md の非推論可能知識ではない」→ **正しい**。`Taskfile.yml:102` に `desc: 'Apply nix-darwin configuration (after bootstrap). Usage: task nix:switch PROFILE=private'` として実在し discoverable
- 私自身の「Rule 8 の MDE が gate に未配線＝バグ」仮説 → **取り下げ**。`holdout_accept_gate.py:250` の `>0` strict-improve + tie-reject は SkillOpt (arXiv:2605.23904) 由来の意図的設計 (`improve-policy.md:311` Rule 47)

## Integration Decisions

### 採用 (3 件、すべて S)

| # | 変更 | ファイル |
|---|---|---|
| T1 | 「最低 5 回、理想 10 回以上」を、反復回数と独立タスク数を分ける記述に置換。増やすなら反復でなくタスク。床/天井張り付きの事前確認を新規 bullet で追加し、Step 2 の borderline プロンプトとは別概念であることを明記 | `.config/claude/skills/skill-audit/SKILL.md:513` |
| T4' | ablation 手順に「手順 3 の比較は集計成功率の検定ではない」を追記。5-10 件では検出力がなく、default=unproven の極性反転と組み合わさると「寄与を示せなかった」が構造的に量産され実質は無条件削除になる。判定は手順 4 の再現失敗に置く | `.config/claude/references/dead-weight-scan-protocol.md:94` |
| T6 | `_verdict()` の返り値に `sample_sizes` を追加。判定ロジックは不変 | `.config/claude/scripts/eval/holdout_accept_gate.py:236` + `tests/scripts/test_holdout_accept_gate.py` |

T6 の動機: strict `>0` accept は「+0.10 の holdout delta」が 1/10 由来か 10/100 由来かを区別せずに出力する。`_check_id_sets` が id 多重集合の一致を保証するため split ごとに 1 数値で正確。サイズガードは `_check_nonempty` のみ。

論文固有の数値 (17×3 / 30pp / 57% / 13%→58%) は**例証として引き、一般則として移植しない**旨を T1 の本文に明記した。

### 不採用

T2 / T3 / T5 / 3-arm / process-cost 昇格 — 理由は Phase 2.5 の表のとおり。

## 副産物 (採用件数に数えない)

### 1. root `tests/` は 128 テストの孤児スイート

| スイート | 件数 | 実行者 |
|---|---|---|
| `scripts/tests/` | 15 | `ci.yml:22`、`task test` |
| `.config/claude/scripts/tests/` | 340 | `ci.yml:25` (`working-directory: .config/claude/scripts`)、`task test` |
| **`tests/`** | **128** | **なし** |

`ci.yml:25` は `uvx pytest tests/ -q` だが `working-directory` が `.config/claude/scripts` なので、root の `tests/` は CI から一度も実行されていない。`task test` も回さず、lefthook pre-commit にも pytest はない。

さらに root `tests/` は現状 **collection error で起動すらしない** — `tests/scripts/test_cross_domain_mapper.py` が参照する `cross-domain-mapper.py` は commit `d2236600` ("delete 11 orphan scripts") で削除されたのにテストが残っている。無視すれば 128 passed。

**T6 で追加したテストもここに着地しており、どのゲートにも守られていない。**

### 2. `uv run pytest tests/` が追跡ファイルを汚染する

worktree で `uv run pytest tests/` を実行したところ、`.config/claude/references/negative-knowledge.md` に fixture 由来のエントリが 11 行書き込まれた:

```
| 2026-08-02 | test-project | [FM-008] TypeError |  | failure |
| 2026-08-02 | tmp77964dww | [FM-006] Permission denied |  | failure |
```

同種の汚染 (`2026-06-29` 付の `tmp1mwmzsk3` / `tmp90cljhcm` / `tmphezuq_kf`) は**既に master にコミット済み**。テストがリポジトリ追跡ファイルに副作用を持っており、それを検出するゲートが (1) の理由で存在しない。今回の diff からは `git checkout --` で除外した。

### 3. deprecated 文書への現役参照

`improve-policy.md` は 2026-05-03 に deprecated だが、live な `optimizer-eligibility.md:58` が「improve-policy.md Rule 10/22 と同趣旨」と現役参照している。Rule 47 (SkillOpt 由来の gate 設計根拠) と Rule 22 (評価基準の自己改変禁止) も同ファイル内にあり、実配線されている gate の設計根拠が退役文書に置かれたままになっている。

## Review Gate

| reviewer | verdict | 内容 |
|---|---|---|
| `codex-reviewer` (agent) | **PASS** | 「追記は既存の default unproven を維持・強化している」「『この論文の数値をそのまま自分の閾値にしない』が誤読を防ぐ guard として機能」。条件は verdict JSON の consumer 確認 |
| `code-reviewer` (agent) | **BLOCK** → 解消 | MUST: `negative-knowledge.md:42-52` にテスト由来のゴミデータ混入。`git checkout --` で除外して解消。`sample_sizes` は既存キー不変で契約を壊さない、追加テストはトートロジーでないと確認 |

両 agent とも初回は tool_uses 20 で打ち切られ最終メッセージを返さず、`SendMessage` での resume 後に verdict を得た。

codex-reviewer の PASS 条件は自分で独立確認した: `evaluate_gate` の verdict JSON を読む側は本体 CLI の `json.dumps` とテストのみ。`objective-lane-optimization.md` は CLI 呼び出しと verdict 表を書くだけでスキーマ検証をしない。

## 検証

```
uv run pytest tests/scripts/test_holdout_accept_gate.py -q  → 21 passed
uv run pytest tests/ -q --ignore=tests/scripts/test_cross_domain_mapper.py  → 128 passed
task validate-configs   → exit 0
task validate-symlinks  → exit 0
```

## 教訓

1. **この論文の null は dotfiles の CLAUDE.md にそのまま当たる。** Limitation 6 (「推論不能な task-specific fact は未検証」) を根拠に射程外と主張するのは、自分の投資を守る側に倒れた読み方だった。CLAUDE.md の大半は委譲・plan・review・DRY といった一般的行動規則で、それは論文が測ったものそのものだ。境界を引くなら、実際に「探索で到達できない環境事実」に該当する記述を名指しできる場合に限る。

2. **spoke を役割で分けると、片方の勧告をもう片方が潰せる。** spoke A は `improve-policy.md` の Rule 8 改称を勧めたが、spoke B が同ファイルの `status: deprecated` を見つけて止めた。批評役と配線検証役を同じエージェントに兼ねさせていたら、退役文書に新ルールを足していた。

3. **absorb 本体より副産物のほうが大きいことがある (再確認)。** 今回の最大の収穫は 3 件の追記ではなく、128 テストの孤児スイート・テストによる追跡ファイル汚染 (master にコミット済み)・deprecated 文書への現役参照の 3 つ。前回 (Boris Cherny absorb) と同じパターンで、これで 2 回連続。

4. **「差がない」を主張するには検出力がいる。** 論文は n=17×3 で 30pp の効果すら 57% しか捕まえられないと自己申告した上で TOST で境界を切った。dotfiles 側の A/B 判断 (skill-audit の「最低 5 回」、dead-weight scan の 5-10 件) は、この基準では「差がない」を主張できる規模にない。だから判定を集計 delta から再現失敗に寄せる。
