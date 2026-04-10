# Mixture of Experts Explained — 分析レポート

**記事**: "Mixture of Experts Explained" (Amit Shekhar / Outcome School)
**分析日**: 2026-04-11
**フェーズ**: /absorb Phase 4 (成果物記録)

---

## 1. Summary

本記事は LLM 内部の MoE (Mixture of Experts) アーキテクチャを教育目的で解説したもの。Router が Top-k Expert を選択するスパース活性化の仕組み、Load balancing loss による Expert collapse 回避、Mixtral 8x7B・DeepSeek-V2/V3 等の実例を取り上げている。ハーネスへの直接統合タスクは少ないが、**MoE 概念とマルチエージェント設計の analogical mapping** を行うことで既存実装の棚卸しができた。加えて Gemini リサーチが 2025-2026 の粒度崩壊研究と MoA (Mixture of Agents) 論文を持ち込み、analogy が崩壊する境界点を明示したことで、安全なガードレール設計への変換に成功した。

---

## 2. Article Claims

- MoE は Router + 小型 Expert ネットワーク群でスパース活性化し、巨大モデルを低コストで実現する
- 専門 Expert は手動でなく **学習によって** 特化する (Router の勾配が Expert を分化させる)
- Router は小型 NN (Linear + softmax) で Top-k を選択し、k 個の Expert 出力を加重平均する
- Load balancing loss (Switch Transformer / GShard) が特定 Expert への集中 = Expert collapse を防ぐ
- Mixtral 8x7B: 総パラメータ 47B、推論時の活性化は 13B のみ
- DeepSeek-V2/V3 等、現代の高性能 LLM の中核アーキテクチャとして普及済み

---

## 3. Analogical Mapping to Harness

| MoE 概念 | ハーネス対応 | 既存実装 | 判定 |
|---|---|---|---|
| Router | CLAUDE.md agent_delegation + triage-router | `.config/claude/agents/triage-router.md` | exists |
| Expert | 33 種の専門サブエージェント | `.config/claude/agents/*.md` | exists |
| Top-k selection | Task Parallelizability Gate + Reviewer Scaling Upper Bound | `references/subagent-delegation-guide.md`, `references/review-consensus-policy.md` | exists |
| Sparse activation | 「Opus でやるべきか先に問う」否定フィルタ | `CLAUDE.md` agent_delegation | exists |
| Load balancing | Heterogeneous Signal Priority + submodular_selection.py | `references/diversity-selection-guide.md` | partial |
| Expert capacity | Context Pressure 3 段階閾値 | `references/resource-bounds.md` | exists |
| Output combination | review-consensus Agreement Rate + capability scores | `references/review-consensus-policy.md`, `references/reviewer-capability-scores.md` | exists |
| Expert collapse 検出 | skill-audit Usage Tier + dead-weight-scan | `skills/skill-audit/SKILL.md` (update 済), `references/dead-weight-scan-protocol.md` | exists+ |
| Router 学習 | autoevolve + race-outcomes | `agents/autoevolve-core.md`, `references/model-expertise-map.md` | partial |

**partial 項目の注記**: Load balancing と Router 学習は対応概念の参照先は存在するが、実測で閉ループしていない。後述の Codex 指摘を参照。

---

## 4. Codex Critique

Codex は調査の大半を完了後 web search でハング (操作エラーによりキャンセル) したが、core critique を捕捉した。

**主な指摘**:

- 「名前だけで `exists` と言っている箇所がかなりある。ファイルが存在することと、その機能が実際に効いていることは別の話」
- 「存在と有効性は別。特に capability weighting と routing 学習は典型的な "参照はあるが実測閉ループなし" パターン」
- 「partial のままにしておくなら、何がないと partial なのかを明示すべき」

→ 今回のスコープでは対処しない。capability weighting と routing 学習の実測閉ループ化は、この記事とは独立した **observability 改善タスク** として記録し、`docs/plans/` での別 plan 化を推奨する。

---

## 5. Gemini Research (2025-2026 知見)

### 既存フレームワークの MoE 類推採用

| フレームワーク | MoE 類推 |
|---|---|
| LangGraph | Router Node + Semantic Router |
| CrewAI | Manager Agent as Router + Top-K selection |
| Microsoft Agent Framework | Dynamic Group Chat + Sparse Activation |

### 2025-2026 MoE 進歩 (記事未言及)

- **Fine-grained Experts**: Expert をさらに細粒度に分割し専門性を高める方向
- **Shared Experts**: 全 Expert 共通の知識層を分離 (DeepSeek-V2 で採用)
- **Latent MoE** (NVIDIA Nemotron 3): 潜在空間でのルーティング
- **Auxiliary-Loss-Free Balancing**: Load balancing loss を使わずに安定化する手法

### Mixture of Agents (MoA) — ハーネス設計の本命

Wang et al. "Mixture-of-Agents Enhances LLM Capabilities" (ICLR 2025 Spotlight) が提案する 2 層構造:

- **Proposers** (並列 LLM 群): 独立して応答草案を生成
- **Aggregators** (統合洗練): 複数草案を合成・洗練

**MoE vs MoA の粒度差**:

| | MoE | MoA |
|---|---|---|
| 粒度 | トークン / ミリ秒 | レスポンス / 秒 |
| 単位 | FFN の Expert | LLM インスタンス |
| ハーネス類推 | token-level routing | agent-level delegation |

Self-MoA (Li et al. 2025-02) は単一モデルの複数サンプリングで同様の効果を得る follow-up。

### 粒度崩壊の失敗事例

| 失敗モード | 内容 | ハーネスへの示唆 |
|---|---|---|
| **Contextual Fragmentation** | トークン単位で切り替えすぎると論理的一貫性が崩壊 | 最小粒度は「思考ステップ」に設定する必要 |
| **Gradient Blackout** | Top-k で選ばれないエージェントに学習信号が流れない | autoevolve での勾配相当の更新が届かないエージェントが存在しうる |
| **Latency Cascade** | 細かく呼び出しすぎると 5 秒以内のレスポンス維持困難 | 並列呼び出し数に上限を設ける根拠 |

### ハーネスレベルの真のパターン (Gemini 推奨)

- **Intent-Based Gating**: 難易度 × ドメイン Tier 分類による事前フィルタ
- **Expert Pool Specialization**: MCP ツール分離 + 必要時ロード
- **Dynamic Throttling**: 思考回数・並列数の動的制御
- **Orthogonality Control**: エージェント役割の直交性管理

---

## 6. Triage 結果 (案 B)

| # | 候補 | 種類 | 採用 | 理由 |
|---|---|---|---|---|
| I | Contextual Fragmentation 対策 | 新規ルール | ✅ 採用 | 最小粒度ルールをガードレール化。失敗事例に実証的根拠あり |
| F | Expert collapse 両方向検出 | 既存強化 | ✅ 採用 | skill-audit に Dominant tier 追加。過負荷検出の双方向化 |
| J | Orthogonality (出力種別) | 既存強化 | ✅ 採用 | Agent Consolidation Scan を出力種別軸に拡張 |
| L | MoA 論文を別途 /absorb | メタ判断 | 🟡 deferred | 次セッションで Wang et al. ICLR 2025 を /absorb |
| B | Expert 自動特化 | — | ❌ | marginal。autoevolve 既存実装で実質カバー済み |
| G | Routing accuracy eval | — | ❌ | Codex 指摘の observability 改善タスクに統合 |
| H | Intent-Based Gating (動的 Tier) | — | ❌ | M-L 規模の変更。別 plan 化が必要 |
| K | Auxiliary-Loss-Free Balancing | — | ❌ | 過剰。ハーネスレベルの実態と乖離が大きい |

---

## 7. 実装済み変更

### 変更 1: `subagent-delegation-guide.md` — 最小ルーティング粒度ガードレール

**ファイル**: `.config/claude/references/subagent-delegation-guide.md`
**箇所**: Task Parallelizability Gate の直後に新セクション追加

追加内容:

- "Minimum Routing Granularity (Contextual Fragmentation Guard)" セクション
- 3 層の最小粒度ルール: (1) 思考ステップ、(2) フェーズ (調査/設計/実装)、(3) タスク
- 粒度崩壊失敗モード表 (Contextual Fragmentation / Gradient Blackout / Latency Cascade の 3 行)

**変更の根拠**: Gemini リサーチが示した Contextual Fragmentation の実証事例。トークン粒度での切り替えは論理一貫性を破壊することが 2025 年の複数フレームワーク実験で確認されている。

### 変更 2: `skill-audit/SKILL.md` — Dominant tier + Expert Collapse 検出

**ファイル**: `.config/claude/skills/skill-audit/SKILL.md`
**箇所**: Step 0.5 Usage Tier Classification

追加内容:

- `Dominant` tier 新設: 全実行の 40% 以上 → Expert Collapse 兆候
- "Over-Use (Expert Collapse)" セクション: 役割重複 / 過剰委譲 / 代替不在を判定フロー
- Dominant + 5D + Unused 共存パターンの判断ガイド

**変更の根拠**: MoE の Load balancing loss が Expert collapse を防ぐのと同様に、ハーネスでも特定エージェントへの過集中を検出する機構が必要。既存の "Unused" 検出に対して "Dominant" の双方向化で対称性を確保。

### 変更 3: `skill-audit/SKILL.md` — Orthogonality Check

**ファイル**: `.config/claude/skills/skill-audit/SKILL.md`
**箇所**: Agent Consolidation Scan

追加内容:

- "Orthogonality Check (出力種別の直交性)" 手順
- 主な出力種別: review-report / observation-report / plan / spec / implementation-patch / research-summary
- 2 軸空間 (出力種別 × ドメイン) で同セル重複するエージェントをフラグ

**変更の根拠**: Gemini の Orthogonality Control 推奨に対応。出力種別が重複するエージェントは統合候補であり、MoE の Expert 分化原則 (各 Expert が異なる入力パターンに特化) の類推。

---

## 8. Deferred / Next Session

### 候補 L: MoA 論文の /absorb

- **対象**: Wang et al. "Mixture-of-Agents Enhances LLM Capabilities" (ICLR 2025 Spotlight)
- **対象**: Self-MoA follow-up (Li et al. 2025-02)
- **理由**: MoA の 2 層 (Proposers + Aggregators) は現在の review-consensus と直接対応する可能性が高く、設計の再評価価値あり
- **アクション**: 別セッションで `/absorb` 実行

### Codex 指摘 (独立タスク): capability weighting と routing 学習の閉ループ化

- **内容**: `partial` 判定の 2 項目 — Load balancing と Router 学習が実測で閉ループしていない
- **理由でスコープ外**: この記事の教育目的に由来する問題ではなく、ハーネス全体の observability 改善課題
- **推奨アクション**: `docs/plans/` に独立した plan を作成して追跡

---

## 9. Meta-observation

**analogical mapping の教訓**:

LLM 内部アーキテクチャ概念 (MoE) をハーネス設計に類推適用する際、**粒度の乖離が 6 桁以上**ある点が最大の罠。MoE はトークン単位 (ミリ秒)、ハーネスはタスク単位 (秒〜分) で動作する。この差を無視して単純に適用すると Contextual Fragmentation を引き起こす。

今回 Gemini リサーチが 2025 年の粒度崩壊研究を持ち込み、analogy の崩壊点を定量的に明示した。これにより「概念は借用するが粒度は変換する」という安全な変換ルールを設計できた。

**記事単体の評価**:

| 次元 | 評価 |
|---|---|
| 記事単体の直接タスク生成力 | 低 (LLM 教育記事でハーネス直結タスクは少ない) |
| analogical mapping 価値 | 中 (既存実装の棚卸しに有効) |
| Phase 2.5 (Refine / Gemini) の追加価値 | 高 (MoA 概念と粒度崩壊モードが分析を救った) |

**抽象教訓**:

> LLM アーキテクチャ記事の /absorb は、概念直輸入ではなく「失敗モードの逆輸入」として設計する。何が崩壊するかを先に調べてから、何を借用するかを決める。

---

*生成: /absorb Phase 4 — 成果物記録*
