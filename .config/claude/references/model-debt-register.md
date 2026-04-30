---
status: active
last_reviewed: 2026-04-23
---

# Model Debt Register

> 現在 model-specific なハーネスルールを **debt (負債)** として登録し、各エントリに削除条件を明示する。
> フロンティアモデルが追いついたら即座に削除できる構造を維持することで、Harvey の失敗（vertical model の moat 蒸発）を個人ハーネスの文脈で避ける。
>
> **着想元**: "The New Software: CLI, Skills & Vertical Models" (2026-04) の Harvey 事例。
> Harvey は OpenAI と組んで case law 専用モデルを構築し 97% のユーザー選好を得たが、
> フロンティアモデルが BigLaw Bench で追いつくと、ルーティング型に戻した。
> 教訓: **モデル固有のルールを永続資産として扱うな。削除条件とセットで運用せよ**。

## 運用原則

1. 新しい model-specific ルールを追加するときは、**必ず削除条件 (Deletion Trigger)** を併記する
2. 削除条件は検証可能な指標であること。「frontier が追いついた気がする」は不可
3. 四半期ごと (3月/6月/9月/12月) にこのレジスタを review し、削除条件を満たした項目を削除する
4. レビュー結果は `docs/research/model-debt-review-YYYY-QN.md` に追記する
5. **このファイル自体も debt**: ルーティングが完全にデータ駆動 (AutoEvolve) になったら削除候補

## Registry

### R-001: Haiku 委譲の構造化出力フォーマット崩壊ワークアラウンド

**現状のルール**: `agent_delegation` で Haiku に委譲するタスクは「WebFetch+要約、ファイル内容の抽出、フォーマット変換」等の**軽量**タスクに限定。構造化 JSON 出力が必須のタスクでは `cascade-parse-strategy.md` の 5 段階フォールバックに依存する。

**根拠**: Haiku は frontier より structured output の安定性が低い。2026-Q1 時点で `/absorb` Phase 1 で JSON 抽出がたまに崩れる。

**配置**:
- `.config/claude/CLAUDE.md` `<agent_delegation>` の Haiku 行
- `.config/claude/references/cascade-parse-strategy.md`

**削除条件 (Deletion Trigger)**:
- `agent-invocations.jsonl` で Haiku 呼び出しの parse failure 率が **連続 2 四半期 < 2%** になること
- または Anthropic が Haiku の JSON mode strict 保証を発表すること

**レビュー対象四半期**: 2026-Q3

---

### R-002: Codex への「深い推論」委譲ルール

**現状のルール**: `agent_delegation` の Codex 行で「設計の壁打ち、リスク分析、セカンドオピニオン、コードレビュー」を Codex に委譲。S 規模以上のコード変更は Codex Review Gate を通す。

**根拠**: 2026-Q1 時点で Codex (gpt-5.5) は Claude Opus 4.6 より「狭く深い」推論特性を示し、レビューで見落としが少ないという実証 (`feedback_codex_reasoning.md`)。

**配置**:
- `.config/claude/CLAUDE.md` `<agent_delegation>`, `<review_policy>` 配下
- `.config/claude/references/codex-delegation.md` (rules/)
- `.config/claude/references/model-expertise-map.md` Score Table

**削除条件**:
- `review-findings.jsonl` で Codex と code-reviewer の **false negative 率が直近3ヶ月で同等** (Δ < 0.05) になること
- または Claude の後続バージョン (Opus 5 等) が BigLaw Bench 相当の review benchmark で Codex を上回ること

**レビュー対象四半期**: 2026-Q4

---

### R-003: Gemini の 1M コンテキスト依存

**現状のルール**: `agent_delegation` の Gemini 行で「コードベース全体分析、外部リサーチ、マルチモーダル」を Gemini に委譲。`/gemini` skill は 200K を超える分析で使用。

**根拠**: Claude の context window は 1M mode でも ランダムアクセス精度が Gemini より低い。Google Search grounding は Gemini のみ利用可能。

**配置**:
- `.config/claude/CLAUDE.md` `<agent_delegation>`
- `.config/claude/references/gemini-delegation.md` (rules/)

**削除条件**:
- Claude の 1M mode が「1M context の 80%+ 位置にある事実の正確な recall」で Gemini と同等以上になること (verifiable by lost-in-the-middle test)
- かつ Anthropic が Google Search grounding 相当の web search を stable tool として提供すること

**レビュー対象四半期**: 2026-Q4

---

### R-004: Opus 判断集中ポリシー (agent_delegation の存在自体)

**現状のルール**: 「Opus は判断・計画・統合・ユーザー対話に集中する。実作業はデフォルトで委譲する」 (CLAUDE.md)

**根拠**: 2026-Q1 時点でコストとレイテンシのトレードオフ上、Opus が実装作業をすると (a) 高コスト、(b) context 膨張、(c) 並行性低下。そのため static tier routing を採用。

**配置**:
- `.config/claude/CLAUDE.md` `<agent_delegation>` 全体

**削除条件**:
- Opus のコストが Sonnet と同程度 (Δ < 20%) になり、かつレイテンシが問題にならなくなること
- または cascade promotion gate が AutoEvolve 経由で動的ルーティングを実現し、**static rule が不要になる**こと (ルールが上位の仕組みに吸収される)

**レビュー対象四半期**: 2026-Q4 (AutoEvolve の成熟度次第で前倒し)

---

### R-005: Open-weight bulk delegation Watch (Kimi K2.6 class)

**現状のルール**: 採用しない。実行 routing は不変 (Sonnet / Haiku / Codex / Gemini / Cursor / Managed Agents の carve-out 維持)、open-weight bulk worker (Kimi K2.6 class) を delegation 先に追加しない。

**根拠**: 2026-04 時点で open-weight model (Kimi K2.6 ≈ MIT / $0.60/M / 256k context / 65k output) が低コスト bulk worker の niche を主張するが、独立検証が不十分:
- (a) 公式 SWE-bench Verified は 78.5%、記事の 80.2% は self-correction 込み (Gemini fact-check 2026-04-30)
- (b) 300 並列 swarm 主張は AutoGen / OpenAI Swarm 独立検証で「300超は state conflict + context 汚染で成功率 20% 以下に急落」と逆エビデンス
- (c) 主な訴求 source が skool.com 系 AI コース販売 marketing で signal-to-noise 比が低い ("Scam-pattern" by Gemini)
- (d) per-call cost optimization は dotfiles の "End-to-End Completion > Per-Call Efficiency" 原則 (`model-routing.md`) と衝突

**配置**: このファイルのみ (実装層には未配置 — 採用条件未達のため)。

**Trigger to Activate (採用条件、すべて満たすこと)**:
- 独立 eval (公式 SWE-bench Pro リーダーボード or Anthropic/Moonshot 以外の中立検証) で Codex/Haiku 比 **cost-adjusted win** が確認できること
- かつ dotfiles 内 local task (例: `/absorb` Phase 1 抽出、`edge-case-analysis` 並列実行) で 30 日 trial における failure mode が許容範囲内
- かつ tool-schema retry 率が Anthropic / OpenAI 並 (記事時点では「やや高め」と既知)

**Trigger to Drop Watch (棄却条件)**:
- 90 日 signal なし (新規 evidence なし) — open-weight bulk worker の niche が消えたと判断
- または safety / capability 不一致が判明 (例: tool-schema retry 改善せず、license/governance issue)

**レビュー対象四半期**: 2026-Q4

**由来**: `docs/research/2026-04-30-three-model-stack-absorb-analysis.md` (Kimi K2.6 + Opus 4.7 + GPT-5.5 cheat-code 記事 absorb)。Codex 批評で「全棄却バイアス補正」として watch 行追加を推奨、Gemini fact-check で trigger を独立検証必須に厳格化。

---

## Template (新規追加時)

```markdown
### R-NNN: {短いタイトル}

**現状のルール**: {何をしているか}

**根拠**: {なぜこのモデル固有ルールが必要か。実証データへのポインタ}

**配置**: {どのファイルにルールが書かれているか}

**削除条件**:
- {検証可能な指標 1}
- または {検証可能な指標 2}

**レビュー対象四半期**: YYYY-QN
```

## Related

- `references/model-expertise-map.md` — 能力スコア表 (HACRL 由来)
- `rules/codex-delegation.md`, `rules/gemini-delegation.md` — 具体的な委譲ルール
- `references/cascade-routing.md` — cascade promotion gate の convention
- `docs/plans/2026-04-11-routing-observability-closed-loop.md` — 動的ルーティングへの移行プラン

## 非目標 (Out of Scope)

- **このレジスタは model-specific rule の正当化ではない**。削除を促進するためのチェックリスト
- **コード内のコメントには記載しない**。ルールの配置と debt register を分離することで、debt が可視化される
- **capability score の記録ではない** (`model-expertise-map.md` の担当)
