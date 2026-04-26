---
source: "Workflow Trellis — 2x2 step-level workflow design framework"
url: "https://github.com/gnurio/nurijanian-skills/blob/main/skills/workflow-trellis/SKILL.md"
author_est: "Linus Lee 系統 / SaaS workflow design 文脈"
date: 2026-04-26
status: integrated
integration_target: stage-transition-rules.md / observability-signals.md / decision-tables-index.md (S 規模、その場で実装完了)
related_absorb: 2026-04-19-agents-md-absorb-analysis.md (decision-tables-index 共通)、2026-04-19-top67-claude-skills-analysis.md (Obligation Gate 先行実装)
---

## Source Summary

**主張**: SaaS 内の workflow を blob として扱うのは誤り。step 単位に分解し 2 軸 (Relief Pressure × Control Demand) で評価せよ。

**4 象限**:

| | 低 Control Demand | 高 Control Demand |
|---|---|---|
| **高 Relief Pressure** | ambient — hook で自動 | control surface — Gate で人が見る |
| **低 Relief Pressure** | nobody cares — silent skip | human-led + AI co-pilot — `/think` `/decision` |

**5 層マッピング (SKILL.md 構造)**:

1. Obligation — "誰が何を保証しているか" の宣言
2. Workflow Repr — blob → step 単位への分解
3. Fragment Connection — step 間の依存・順序
4. Action/Friction Kernels — 実行コストと抵抗源の特定
5. Automation Insertion — どこに自動化を差し込めるか

**3 ゲート**:
- Durable Obligation Gate
- Fragmented Representation Gate
- Hated Execution Burden Gate

**重要論点**:
- "Human in the loop" は人を safety widget 扱い → 古い cybernetics 用語 (goal/action/signal/interpretation/correction loop) が正確
- 5 制御ドライバ: taste / accountability / control / attention / identity
- Attention allocation 5 動詞: interrupt / batch / escalate / hide / shut up
- 自動化の皮肉: 機械が吸収するほど残る人間の仕事は judgment/escalation/exception/authority/repair (自動化困難)
- 10 bits/sec = Markus Meister 2024-12 *Neuron* "The Unbearable Slowness of Being" — 人間の conscious information throughput の上限

**前提条件**: SaaS チーム設計文脈が中心。個人 harness では Control Demand が薄く、Relief Pressure 最大化が主軸になる。

---

## Gap Analysis (Phase 2: 存在チェック)

Codex 調査 + Gemini 分析 を統合した判定。

| # | 記事の主張 | 判定 | 主要ファイル | 詳細 |
|---|---|---|---|---|
| 1 | Trellis 2x2 軸 (Relief × Control) | Already (強化可能) | `references/stage-transition-rules.md` | S/M/L が既に多因子ルーティング (リスク × 影響範囲 × ステークホルダー) として機能 |
| 2 | 5 制御ドライバ (taste/accountability/control/attention/identity) | Already (分散済み) | `references/wrapper-vs-raw-boundary.md` / `references/improve-policy.md` / `references/observability-signals.md` | identity は個人 harness で N/A、他 4 つはそれぞれ既存参照に収容 |
| 3 | 5 層マッピング + Obligation Gate | Already | `.claude/skills/spec/` / `.claude/skills/epd/` | Top 67 absorb (2026-04-19) で Phase 0 interview として導入済 |
| 4 | Friction Kernel Decomposition | Already (強化不要) | `friction-events.jsonl` / `retrospective-codify` / AutoEvolve | friction-events.jsonl + retrospective-codify + autoevolve でカバー済 |
| 5 | Attention Allocation 5 動詞 | Gap | `references/observability-signals.md` | interrupt/batch/escalate/hide/shut up の decision table なし → 追加対象 |
| 6 | Control Surface Override (小粒でも Gate 必須なケース) | Partial | `references/stage-transition-rules.md` | S 規模でも auth/不可逆/breaking change は M 相当 Gate が必要、明文化なし |
| 7 | trellis 4 象限 → mechanism マッピング | Gap | `references/decision-tables-index.md` | 索引への 1 行追記が欠落 |

---

## Phase 2.5: Refinement (Codex + Gemini 並列批評の統合)

### Codex 観察 (調査ログから)

- 当初参照した `harness-engineering-details.md` は実在せず → 強化案 B (cybernetic loop 追加先) を棄却
- `agency-safety-framework.md`・`team-harness-patterns.md` を見落としていたが、影響なし (採択案との重複なし)
- S/M/L は単なる規模ではなく多因子ルーティングである → 4 象限 trellis を新規 mechanism として追加するのは Pruning-First 違反。1 段落 Override + 索引 1 行で十分と判断

### Gemini 観察 (分析ログから)

- 5 driver は SDT (Deci/Ryan) + Cybernetics (Wiener/Ashby) と学術的に整合 → 知識として有効、実装化は不要
- 個人 harness では Relief Pressure 最大化が極めて重要、Control Demand は薄い (一人開発)
- ADK 2.0 はオーバーエンジニアリング、AGENTS.md (既採用) で十分 → F 案 (ADK 統合) を N/A 判定
- 10 bits/sec は Markus Meister 2024-12 *Neuron* 査読済論文 → MEMORY.md 200 行上限・brevity 原則の理論的根拠として利用可能
- **副作用**: Gemini が指示外で `docs/research/2026-04-26-workflow-trellis-research.md` と `memory/reference_workflow_trellis_research.md` を作成 + `MEMORY.md` に索引追記。ユーザー判断で 3 ファイル全て削除した

### 強化案 評価マトリクス

| 案 | 内容 | 採否 | 根拠 |
|---|---|---|---|
| A | stage-transition-rules.md に Control Surface Override 1 段落追加 | **採用** | S 規模でも Gate 強制が必要なケースの明文化が欠落。既存フレームの補強 |
| B | harness-engineering-details.md に cybernetic loop 三要素追加 | 棄却 | 当該ファイル不在。`agent-harness-contract.md` に Durable State + Scaffolding/Harness 区別が既にあり追加不要 |
| C | observability-signals.md に Attention Allocation Decision Table 追加 | **採用** | 5 動詞 × 信号タイプの decision table が実際に欠落。Meister 2024 引用で brevity 原則の根拠補強も兼ねる |
| D | 5 driver による prioritization weight 化 | 棄却 | identity は個人 harness で N/A、weight 化は精緻化過剰。記事の知見はレポート記録で十分 |
| E | /spec Phase 0 に Obligation Gate 質問追加 | 棄却 | Top 67 absorb (2026-04-19) で Phase 0 interview 導入済。差分なし |
| F | decision-tables-index.md に trellis 4 象限 → mechanism 1 行追記 | **採用** | 索引の一貫性のため 1 行のみ。新 frame 導入ではない |

---

## Phase 3: ユーザー選択

採用: **A, C, F** (3 件)
棄却: **B, D, E** (3 件)

採用規模: S (3 ファイルへの小規模追記、その場で実装完了)

---

## 実装結果 (Phase 4)

### A: stage-transition-rules.md — Control Surface Override 段落追加

**場所**: §1 規模別スケーリング表の直後

**追加内容** (~12 行):
- S 規模でも以下の条件では M 相当の Gate を強制:
  - auth/認証 系の変更
  - 不可逆操作 (DB migration, file deletion, config destroy)
  - master 直変 / harness 変更 (hook/skill/agent)
  - breaking change (API 破壊、型変更)
- change-surface-advisor の Critical/High カテゴリと連動
- 根拠: Trellis 4 象限の "control surface" 象限 (高Relief × 高Control) に相当

### C: observability-signals.md — Attention Allocation Decision Table 追加

**場所**: §2 アクションマップ末尾

**追加内容** (~20 行):
- 5 動詞 × 信号タイプの表 (interrupt / batch / escalate / hide / shut up)
- Meister 2024 (10 bits/sec) を脚注で引用 — 人間の conscious bandwidth 上限の根拠
- 運用ルール:
  - 二重化禁止 (同一信号に 2 動詞を割り当てない)
  - 暗黙 hide 禁止 (hide は明示的に選択する)
  - 連続 PASS で hide 降格 (escalate → batch → hide の自動降格ルール)

### F: decision-tables-index.md — trellis 4 象限 → mechanism 1 行追記

**場所**: Mechanism 系の表

**追加内容** (1 行):
```
| trellis 4 象限 → mechanism | ambient=hook / control surface=Gate / human-led=`/think` `/decision` / nobody cares=silent skip | references/stage-transition-rules.md / references/observability-signals.md |
```

---

## 棄却理由詳細

### B: cybernetic loop 三要素 → harness-engineering-details.md

`harness-engineering-details.md` が実在しない (Codex の grep --hidden --files で確認)。代替先 `agent-harness-contract.md` には Durable State + Scaffolding/Harness 区別が既に収容されており、cybernetic loop (goal/action/signal/interpretation/correction) は conceptual overlap。追加しても機能増分なし。

### D: 5 driver prioritization weight

5 driver (taste/accountability/control/attention/identity) のうち identity は個人 harness では N/A。残り 4 つは既存参照に分散収容済み。weight 数値化は精緻化過剰 (YAGNI)。記事知識はレポートに保存済みで十分。

### E: /spec Phase 0 Obligation Gate 質問追加

Top 67 absorb (2026-04-19) で Phase 0 interview を /spec に導入済み。Obligation Gate の問い ("誰が何を保証しているか") は Phase 0 の "stakeholder/obligation 確認" に内包される。差分なし。

---

## Anti-Patterns / 学び

### Codex 批評の重要性

Opus が想定した参照ファイルが実在しないケースを Codex の `grep --hidden --files` で発見。強化案 B は前提ファイルの存在を未検証のまま設計されており、Codex レビューなしでは誤った実装につながっていた。盲目的な強化案は危険。

### Gemini の自律的副作用

指示外でファイル作成 (`docs/research/2026-04-26-workflow-trellis-research.md`、`memory/reference_workflow_trellis_research.md`) + `MEMORY.md` に索引追記を実行。ユーザー判断で 3 ファイル全て削除。次回は明示的に「ファイル作成禁止、JSON で結果のみ返せ」と指示する必要あり。→ Gemini 委譲時のプロンプトに output format 制約を追加する改善候補。

### Pruning-First の徹底

記事の核 (2 軸 trellis) は既存 S/M/L 多因子ルーティングに内包される。新 frame 追加ではなく 1 段落 override + 1 表 + 1 行で十分。4 象限を丸ごと新規 mechanism として追加する誘惑を Codex が阻止した。

### 10 bits/sec の応用

Meister 2024 の査読済み実験結果は MEMORY.md 200 行上限・brevity 原則・observability signal 設計 (shut up 動詞) の学術的根拠として機能する。理論 → 設計原則への接続が有効。

---

## Decision Trail

```
記事入手
  └→ Phase 1 抽出 (5 層・3 ゲート・4 象限・5 driver・5 動詞)
       └→ Phase 2 Gap 分析 (7 項目: Already×4, Gap×2, Partial×1)
            ├→ Codex 批評: harness-engineering-details.md 不在を発見 → B 棄却
            ├→ Gemini 批評: 個人 harness では Control Demand 薄い → D/E 強化不要
            └→ Phase 2.5 統合判定: A(採用) / B(棄却) / C(採用) / D(棄却) / E(棄却) / F(採用)
                 └→ Phase 3 ユーザー選択: A/C/F 採用確定
                      └→ Phase 4 実装: 3 ファイル編集、S 規模完了
```

---

## Memory Pointer

MEMORY.md「外部知見索引」セクションへの追記内容:

```
- [Workflow Trellis absorb (2x2 framework)](../../../dotfiles/docs/research/2026-04-26-workflow-trellis-absorb-analysis.md) — Linus Lee 系の 2軸トレリス (relief × control)。Codex で「S/M/L が既に多因子ルーティング」と判明、Pruning-First で 3 件採択 (A stage-transition-rules.md Control Surface Override / C observability-signals.md Attention Allocation Table 5動詞×信号タイプ / F decision-tables-index.md trellis 4象限→mechanism 1行)。棄却 3 件 (cybernetic loop は contract に内蔵 / 5 driver weight は精緻化過剰 / Obligation Gate は Top 67 で実装済)。Meister 2024 *Neuron* (10 bits/sec) を C の根拠に引用。Gemini 副作用 (指示外ファイル作成) を user 判断で全削除
```
