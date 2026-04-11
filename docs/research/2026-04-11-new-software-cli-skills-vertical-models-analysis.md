# "The New Software: CLI, Skills & Vertical Models" — 統合分析

**分析日**: 2026-04-11
**ソース**: "The New Software: CLI, Skills & Vertical Models — In the era of agent experience, performance will become the new competitive advantage for great SaaS companies" (2026-04 頃、Sangeet Choudary 系 SaaS 戦略論)
**ワークフロー**: `/absorb`

## 記事の主張 (Extract)

Agent Experience (AX) 時代の SaaS 戦略として、次の 3 層スタックが必要:

1. **Skill files**: ドメイン専門知識をマークダウンで機械可読化 (what/in what order/constraints/why)
2. **CLI + MCP servers**: 人間ではなくエージェントが直接呼べる composable interface 層
3. **Vertical models**: ドメイン特化 fine-tuned モデルで重み自体に知識を埋め込む

**パフォーマンス (コスト・レイテンシ) が新しい競争優位**。
- FrugalGPT cascade routing で最大 **98% のコスト削減**
- 5-15 tool call の workflow で「全 frontier」 vs 「小モデル中心」= 30s vs 2s の差
- Cursor Composer 2 (Kimi K2.5 ベース fine-tuned): Terminal-Bench 2.0 で 61.7% (Opus 4.6 58.0%) を **$0.50/M** で実現

**Harvey 事例 (反例・重要)**: OpenAI と組んで case law 専用モデルを構築し 97% ユーザー選好を獲得した Harvey が、フロンティアモデルの追い上げでその専用モデルを**廃止**した。教訓: **vertical model の moat は蒸発しうる**。

**対照事例 (Linear)**: embedded agent を作ったが MCP server も CLI も API 露出もしなかった。ユーザーは「外部エージェントから Linear データに接続したい」と言っている。AX の優先順位を間違えた失敗例。

## 記事の前提条件

- SaaS 企業向け戦略論。外部顧客向けの「提供価値としての AX」が主眼
- Enterprise で machine identity が human の 45 倍 (いくつかの組織では 100 倍) という前提
- 「Primary user in 6 months may not be human」という時間軸

## Phase 2 Pass 1 + Pass 2: ギャップ分析

### Gap / Partial / N/A

| # | 手法 | 判定 (Codex 批評後) | 現状 |
|---|------|-------------------|------|
| 1 | FrugalGPT **online cascade** (cheap→judge→escalate/stop) | **Gap** | 静的 tier routing のみ。品質判定 → 昇格/停止 gate は設計にない (Codex 指摘で Partial → Gap 格上げ) |
| 2 | Latency/cost measurement per task | **Partial** | `agent-invocation-logger.py` で Wave 1 計測済み。`docs/plans/2026-04-11-routing-observability-closed-loop.md` の Wave 2 attribution が未完成 |
| 3 | Deterministic routing to code/small models | **Already (強化可能)** | `agent_delegation` に Haiku 行あり。但し決定論的タスクの**契約化**は未実装 (keyword suggestion レベル) |
| 4 | Managed Agents brain/hands/session decoupling | **Already** | `references/managed-agents-*.md` 統合済み |
| 5 | Skill files as practitioner judgment | **Already (強化不要)** | `skill-writing-principles.md` に PostHog $pageview 相当の Good/Bad/Why が既存。Codex 批評で重複と判定 → 強化案削除 |
| 6 | Capability parity / CLI-first | **N/A (再写像で Gap)** | SaaS 原義では N/A。個人文脈: 「運用コスト・可搬性・交換可能性」に写像 |
| 7 | Performance-first routing policy | **Partial** | 暗黙的。明示ポリシー宣言なし。routing-observability と重複 |
| 8 | Vertical models (fine-tuning) | **N/A** | 個人セットアップ不可。Harvey の示唆は「専用モデル作るな」ではなく**「モデル差で勝つ設計を永続資産扱いするな」** |

## Phase 2.5: Codex 批評結果 (Refine)

Codex (`codex-rescue` サブエージェント) の厳しい批評から得た 4 つの補正:

1. **FrugalGPT は観測ではなく online cascade**: 安い試行 → 品質判定 → 昇格/停止。routing-observability plan は観測寄りで昇格条件が薄い。**Gap**に格上げ
2. **routing-observability plan の cover は過大評価**: plan は `proposed/not started` 表記。実装済みは logger の一部のみ
3. **Deterministic routing の Already は甘い**: 現状は keyword suggestion であって決定論的 contract ではない。強化余地大
4. **強化案 (B) skill Pitfall Section は重複**: 既に skill-writing-guide に PostHog 例相当が含まれる。**削除**
5. **Harvey の真の示唆**: 「vertical model を作るな」ではなく「**モデル固有ルールを永続資産として扱うな**」。debt register 化して frontier 追いついたら削除できる構造へ

**Codex の最優先 1 アクション**: 強化案 (A) を新規 reference ではなく、**agent-router/triage-router の decision log と Haiku cascade 昇格条件に直結する最小 patch として設計し直す**。

Gemini 周辺知識補完は省略 (Codex の批評が十分に強く、狙う価値に対し analysis phase 遅延は不要と判断)。

## Phase 3: Triage (選択結果)

ユーザー選択:
- **Cascade promotion gate (S) 推奨** ← 採用
- **Model debt register (S)** ← 採用
- **Deterministic task contract (M)** ← 採用 (今セッションは S 規模のみ実装、M は plan 化して別セッション)

実装方針: **今セッションで S 規模を実装**

## Phase 4: 実装結果

### 1. Cascade Promotion Gate (S) ✅ 完了

- **新規**: `.config/claude/references/cascade-routing.md`
  - `[cascade:<name>/step:<N>]` の convention 定義
  - Promotion criteria (format violation / empty / low confidence / timeout / manual flag)
  - Anti-patterns、Deletion trigger (AutoEvolve が自動化したら削除)

- **パッチ**: `.config/claude/scripts/runtime/agent-invocation-logger.py`
  - `_CASCADE_MARKER_RE` と `_extract_cascade_marker()` を追加
  - 既存 `emit_agent_invocation()` に `cascade_name` と `cascade_step` をマージ
  - 後方互換性: marker 不在時は既存スキーマそのまま
  - スモークテスト: 7 ケース全 OK (正常 2 / 不在 2 / None 1 / 破損 2)

### 2. Model Debt Register (S) ✅ 完了

- **新規**: `.config/claude/references/model-debt-register.md`
  - 4 つの初期エントリ (R-001〜R-004) を登録:
    - R-001: Haiku 委譲の structured output 崩壊ワークアラウンド
    - R-002: Codex 深い推論委譲ルール
    - R-003: Gemini 1M コンテキスト依存
    - R-004: Opus 判断集中ポリシー (`agent_delegation` の存在自体)
  - 各エントリに **削除条件 (Deletion Trigger)** を併記
  - 四半期レビューサイクル (Q3 / Q4) を明示
  - Harvey 示唆への直接的な応答構造
  - **自己参照**: このレジスタ自体も debt として削除条件を持つ (AutoEvolve 成熟時)

### 3. Deterministic Task Contract (M) ✅ Plan 化

- **新規**: `docs/plans/2026-04-11-deterministic-task-contract-plan.md`
  - 6 カテゴリ (contract extraction, validation, metric computation, format conversion, status check, retrieval) の dotfiles 文脈翻訳
  - 6 つの Acceptance Criteria
  - Phase 0 (観測データで問題の実在を確認) → Phase 1 (catalog) → Phase 2 (advisor hook) → Phase 3 (edge case) → Phase 4 (integration test) → Phase 5 (review gate)
  - 撤退条件と反証条件を明示
  - false positive rate < 10% の要求

## 却下された候補 (Anti-patterns 回避)

- **Skill Pitfall Section 強化**: 既に skill-writing-guide に含まれる (Codex 指摘)
- **Latency/cost measurement 新規**: `routing-observability-closed-loop.md` と重複
- **Capability parity (SaaS 原義)**: 外部顧客なし個人セットアップでは意味なし
- **Vertical models (fine-tuning)**: 個人セットアップ不可、Harvey 事例からも非推奨
- **新規 reference `deterministic-task-catalog.md` の即時追加**: Codex 指摘「refs 追加なら装飾」→ hook/log に直結する plan に格下げ

## 記事の「本当の価値」(Refined)

記事全体の 8 割は SaaS 戦略論として N/A だが、個人ハーネスに効く insight は 2 点:

1. **Online cascade > Static tier routing**: 試行→判定→昇格のループを明示的に観測可能にする (実装済み: cascade-routing.md + logger patch)
2. **Model-specific rule は debt**: 永続資産として扱うと Harvey と同じ罠にはまる。削除条件とセットで管理する (実装済み: model-debt-register.md)

これ以外の記事コンテンツは現状のセットアップでカバー済みまたは N/A。

## 学び (このセッションから)

- **Codex 批評の価値**: Claude バイアス (Sycophancy + 過剰 cover 評価) を 2 点補正。特に routing-observability plan の「プラン存在 ≠ 実装完了」の区別は Claude 単独では見落とした
- **`feedback_absorb_already_deepdive.md` の再確認**: Already 判定の Pass 2 (強化チェック) を実施したことで、強化案 (B) が重複と判明。Pass 2 がないと装飾的な変更を加えてしまうところだった
- **「debt register」パターンの発見**: 静的ルールをドキュメントとして持つだけでなく、**削除条件を構造化**することで、ハーネス自体の Build-to-Delete 原則が適用可能になる

## 関連ドキュメント

- **実装物**:
  - `.config/claude/references/cascade-routing.md`
  - `.config/claude/references/model-debt-register.md`
  - `.config/claude/scripts/runtime/agent-invocation-logger.py` (パッチ)
  - `docs/plans/2026-04-11-deterministic-task-contract-plan.md`
- **関連既存**:
  - `.config/claude/references/cascade-parse-strategy.md` (出力パース層)
  - `.config/claude/references/model-expertise-map.md` (能力スコア表)
  - `docs/plans/2026-04-11-routing-observability-closed-loop.md` (計測 → attribution → closed-loop)
- **外部参照**:
  - Chen et al. "FrugalGPT", Stanford 2023 (cascade routing の源流)
