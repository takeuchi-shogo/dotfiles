---
status: active
last_reviewed: 2026-04-23
---

# MR-Search: エージェント探索のためのメタ強化学習と自己省察 深掘り調査

**調査日**: 2026-03-17
**論文**: arXiv:2603.11327 "Meta-Reinforcement Learning with Self-Reflection for Agentic Search"
**著者**: Teng Xiao, Yige Yuan, Hamish Ivison, Huaisheng Zhu, Faeze Brahman, Nathan Lambert, Pradeep Dasigi, Noah A. Smith, Hannaneh Hajishirzi (Allen Institute for AI, University of Washington)
**リソース**: [GitHub](https://github.com/tengxiao1/MR-Search) (コード 2026-03-21 公開予定) | [arXiv](https://arxiv.org/abs/2603.11327)

---

## Executive Summary

MR-Search は「エージェントの検索行動を複数エピソードにわたるメタ学習で最適化する」フレームワーク。
従来の RL ベースの検索エージェント（Search-R1, ReSearch 等）が**各エピソードを独立に扱い、疎な結果報酬のみで学習**していたのに対し、MR-Search は**エピソード間の自己省察を明示的に構造化**し、過去の試行から学ぶ「学び方を学ぶ」アプローチを採用。

**核心的知見**: 外部の Process Reward Model なしで、自己省察そのものが dense なプロセス報酬として機能する。8つのベンチマークで 9.2%〜19.3% の相対改善。

**dotfiles ハーネスへの示唆**: エージェントの自己省察ループ、クロスエピソード学習、ターンレベル信用割当は、我々の AutoEvolve / session-learner / completion-gate に直接適用可能なパターンを含む。

---

## 1. 問題設定と動機

### 1.1 従来手法の限界

| 課題 | 詳細 |
|------|------|
| **疎な報酬** | 結果報酬はトラジェクトリ完了時のみ → 中間ステップへの信用割当が曖昧 |
| **非効率な探索** | 初期段階で探索が不十分 → 局所最適に陥りやすい |
| **エピソード独立性** | 各検索試行が独立 → 過去の失敗から学べない |
| **外部 PRM の限界** | Process Reward Model はアノテーションが高コスト、タスク変更時に再利用不可、reward hacking のリスク |

### 1.2 MR-Search の着想

> "Model limitations often stem from insufficient exploration within a single trajectory rather than inadequate reasoning capacity."

2つの洞察:
1. **探索不足問題**: 単一トラジェクトリでの探索が不十分なことが性能ボトルネック（推論能力自体の問題ではない）
2. **LLM の自己省察能力**: LLM は強い in-context 学習能力を持ち、過去のインタラクションから推論時に適応できる

→ Meta-RL のフレームワークで「自己省察を通じた探索の改善」を構造化

---

## 2. MR-Search フレームワーク

### 2.1 アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                     Meta-Episode                             │
│                                                              │
│  ┌──────────┐   Reflect   ┌──────────┐   Reflect   ┌──────┐│
│  │Episode 0 │────────────→│Episode 1 │────────────→│Ep. N ││
│  │Think→Act │  Self-      │Think→Act │  Self-      │...   ││
│  │→Obs→Ans  │  Reflection │→Obs→Ans  │  Reflection │→Ans  ││
│  └──────────┘             └──────────┘             └──────┘│
│       ↓                        ↓                       ↓    │
│    r(a₀,o*)               r(a₁,o*)                r(aₙ,o*) │
│                                                              │
│  ← 各エピソードの報酬で RLOO アドバンテージを推定 →             │
└─────────────────────────────────────────────────────────────┘
```

**従来 (Search-R1)**: `a₀ ~ π(·)`, `a₁ ~ π(·)` — 各エピソードが**独立**
**MR-Search**: `a₀ ~ π(·)`, `a₁ ~ p(·|a₀)`, `aₙ ~ p(·|a₀,...,aₙ₋₁)` — 過去の全履歴に**条件付き**

### 2.2 ReAct パラダイムとの統合

各エピソード内の構造:
```
a = (τ₀, α₀, x₀, τ₁, α₁, x₁, ..., τ_{T-1})
```
- `τ`: 内部思考 (Think)
- `α`: 外部アクション (Search query)
- `x`: ツール観測 (Search results)
- 最終 `τ_{T-1}` に Answer を含む

### 2.3 メタレベル目的関数

```
J_meta(π_θ) = E_y~π_θ [Σ_{n=0}^{N-1} γⁿ f_verifier(oₙ, o*)]
```

- `γ=1` (デフォルト): 全エピソードを均等に重み付け
- `γ=0` のとき大幅に性能低下 (46.0→43.8%) → 中間エピソードの情報も重要

### 2.4 Multi-Turn RLOO アドバンテージ推定

**RLOO (Leave-One-Out)**:
```
r̃_{i,n} = r(s_{i,n}, a_{i,n}) - mean_{j≠i} r(s_{j,n}, a_{j,n})
```

**割引ターンレベルアドバンテージ**:
```
A_{i,n} = Σ_{n'=n}^{N} γ^{n'-n} r̃_{i,n'}
```

**PPO スタイルの最適化** (clipped surrogate objective):
- Critic-free（価値関数不要）
- ツール出力トークンはロスからマスク

**なぜ RLOO が優れるか**:
| 手法 | 平均精度 | 特徴 |
|------|---------|------|
| MR-Search (RLOO) | **46.0%** | 不偏ベースライン、critic-free |
| MR-Search w/ MT-GRPO | 44.3% | 過信のリスク (Bereket & Leskovec, 2025) |
| MR-Search w/ PPO | 42.0% | 価値関数のオーバーヘッド |
| MR-Search w/ γ=0 | 43.8% | 将来依存を無視 |

### 2.5 拡張: Exploration vs Exploitation

```
A_{i,n} = Σ_{n'=n}^{N} γ^{n'-n} r̃_{i,n'} · m_{n'}
```
- `m_n ∈ {0,1}`: exploitation(1) or exploration(0)
- 探索エピソードの報酬をゼロにマスク → 長期的な文脈適応を優先
- ASearcher（複雑タスク）で特に有効

### 2.6 拡張: Step-Level Meta-RL

- 各ツール呼び出しステップを micro-episode として扱う
- ステップごとに中間回答を生成・評価 → より密な supervision
- Search-R1 を上回るが、フル MR-Search には及ばない

---

## 3. 実験結果

### 3.1 メイン結果 (Table 1)

| データセット | NQ | TriviaQA | PopQA | HotpotQA | 2Wiki | Musique | Bamboogle | 平均 |
|---|---|---|---|---|---|---|---|---|
| **Qwen2.5-3B** |
| Direct Inference | 10.6 | 28.8 | 10.8 | 14.9 | 24.4 | 2.0 | 2.4 | 13.4 |
| Search-R1 | 46.2 | 62.2 | 45.6 | 32.6 | 31.0 | 7.7 | 17.6 | 34.7 |
| **MR-Search** | **47.7** | **63.5** | **46.0** | **41.9** | **40.1** | **16.5** | **34.4** | **41.4** |
| **Qwen2.5-7B** |
| Search-R1 | 45.9 | 63.2 | 44.9 | 43.9 | 38.7 | 18.1 | 40.0 | 42.1 |
| PPRM (外部PRM) | 45.8 | 61.0 | 43.7 | 38.6 | 35.5 | 14.7 | 35.5 | 39.3 |
| StepResearch | 47.3 | 63.6 | 43.1 | 43.9 | 41.8 | 20.5 | 43.5 | 43.4 |
| **MR-Search** | **50.2** | **66.6** | **47.2** | **46.8** | **43.6** | **22.1** | **45.2** | **46.0** |

**相対改善**: 3B で **+19.3%**、7B で **+9.2%** (vs Search-R1)

### 3.2 重要な知見

1. **小さいモデルほど効果大**: 3B での改善幅 (19.3%) > 7B (9.2%)。探索不足が小モデルのボトルネックであることを示唆
2. **Multi-Hop QA で特に効果的**: Musique (+114% on 3B), Bamboogle (+95% on 3B) — 複雑な推論が必要なタスクほど自己省察の恩恵が大きい
3. **外部 PRM を不要化**: PPRM (39.3%) や StepResearch (43.4%) を上回る — 自己省察がプロセス報酬を代替
4. **Test-Time Scaling**: 訓練時 3 ターン → 推論時 6+ ターンに外挿可能。Search-R1 は外挿で改善しないが MR-Search は急勾配で改善

### 3.3 ASearcher (長期ホライズンタスク)

| 指標 | Search-R1 | MR-Search | 改善率 |
|------|-----------|-----------|-------|
| EM | 36.9% | 41.3% | +10.2% |
| F1 | — | — | +9.5% |

長期的なツールインタラクションが必要なタスクでも効果を発揮。

### 3.4 コンテキスト管理のトレードオフ

| 手法 | 平均精度 | メモリ |
|------|---------|-------|
| Full history (全履歴) | **46.0%** | O(N) |
| Short context (直前のみ) | 45.2% | O(1) |

→ 直前エピソードのみで **96%** の性能を維持。実用的なトレードオフ。

---

## 4. 関連手法との比較

### 4.1 Search-R1 (Jin et al., 2025)

MR-Search のベースライン。ReAct パラダイムで LLM を RL 訓練し検索クエリを自律生成。
- **限界**: 各エピソード独立、疎な結果報酬のみ、中間ステップへの信用割当なし
- **MR-Search との差**: エピソード間の条件付き + 自己省察 + ターンレベル報酬

### 4.2 Reflexion (Shinn et al., 2023)

プロンプティングベースの自己省察。環境フィードバックを言語化しメモリに保存。
- **限界**: 推論時のみの手法（モデル重みは更新されない）、外部フィードバック依存
- **MR-Search との差**: RL で自己省察能力そのものを訓練、ground-truth 不要

### 4.3 MRT (Qu et al., 2025)

テスト時計算をメタ RL で最適化。出力ストリームを複数エピソードと見做し、累積 regret を最小化。
- **共通点**: メタ RL のフレームワーク、テスト時スケーリング
- **差異**: MRT は数学推論向け dense progress bonus、MR-Search はツール使用エージェント向け自己省察

### 4.4 ポジショニングマップ

```
                    訓練時学習 ←───────────→ 推論時のみ
                         │                      │
  外部報酬    PPRM ──────┤                      │
  モデル      StepResearch┤                      │
                         │                      │
  自己生成    MR-Search ──┤              Reflexion┤
  報酬                   │          Self-Refine──┤
                         │                      │
  結果報酬    Search-R1 ──┤     Self-Consistency──┤
  のみ        ReSearch ──┤                      │
```

---

## 5. 技術的貢献の評価

### 5.1 強み

| 貢献 | 評価 | 詳細 |
|------|------|------|
| メタ RL 定式化 | ★★★★★ | 独立エピソード → 条件付きメタエピソードへの再定式化は理論的に美しい |
| RLOO アドバンテージ | ★★★★☆ | Critic-free で unbiased、計算コストは Group size G に依存 |
| 自己省察 = プロセス報酬 | ★★★★★ | 外部アノテーション不要で PRM を代替する発想は実用性が高い |
| Test-Time Scaling | ★★★★☆ | 訓練ターン数を超えて外挿可能は強力だが、コンテキスト長制約あり |
| Short Context (96%性能) | ★★★★☆ | 実用的なスケーラビリティ解決策 |

### 5.2 限界

| 限界 | 影響度 | 詳細 |
|------|--------|------|
| ツール多様性 | 高 | Wikipedia 検索のみ。Web検索、ブラウジング、コード実行等は未検証 |
| スケール | 中 | 3B/7B のみ。フロンティアモデルでの検証なし |
| 長文生成 | 中 | QA タスクのみ。レポート生成等の長文出力は未対応 |
| 計算コスト | 中 | G=5 のメタエピソードサンプリング → 訓練コスト 5x |
| コード未公開 | 低 | 2026-03-21 公開予定 |

---

## 6. dotfiles ハーネスへの適用分析

### 6.1 活かせるもの (直接適用可能)

#### A. 自己省察ループの構造化 — `completion-gate.py` 強化

**現状**: completion-gate は未完了ステップ検出・テスト実行で Stop を制御
**MR-Search からの知見**: 各試行の結果を次の試行に明示的にフィードバックする構造化された省察ループ

**具体的改善案**:
```python
# completion-gate.py に reflection prompt 注入
# テスト失敗時、前回の試行結果を additionalContext に構造化して含める
reflection_context = {
    "previous_attempt": {
        "action": "テスト実行",
        "result": "2/5 失敗",
        "failures": [...],
        "reflection": "前回の修正は X を見落とした。Y の観点から再検討が必要"
    },
    "attempt_number": n,
    "max_attempts": MAX_RETRIES
}
```

**効果**: 単なるリトライではなく、前回の失敗を踏まえた構造化された改善を促進

#### B. AutoEvolve セッション学習への Cross-Episode パターン

**現状**: `session-learner.py` がセッション終了時に learnings を記録
**MR-Search からの知見**: エピソード間の累積コンテキストが性能を大幅に改善

**具体的改善案**:
- セッション開始時に前セッションの learnings サマリを注入（Short Context 方式 — 直前セッションのみで 96% 効果）
- `session-load.js` で前回セッションの「振り返り」を自動生成して提供

#### C. ターンレベル信用割当 — Review 信頼度スコアの改善

**現状**: `/review` の信頼度スコアは指摘単位の confidence (0-100)
**MR-Search からの知見**: RLOO 方式の相対ベースライン — 他のサンプルとの比較で信頼度を推定

**具体的改善案**:
- 同じコードに対する複数レビューアーの指摘を RLOO 的に比較
- 単独のレビューアーのみが指摘 → 信頼度低め
- 複数のレビューアーが一致 → 信頼度高め（既存の信頼度フィルタ 80 に加えて）

#### D. Exploration vs Exploitation — Agent Router 改善

**現状**: `agent-router.py` がタスクの性質に基づいてエージェントを選択
**MR-Search からの知見**: 明示的な探索・活用の分離が複雑タスクで有効

**具体的改善案**:
- 複雑なタスク（Multi-Hop 相当）では最初の試行を「探索モード」として扱う
- 探索モードの結果は直接採用せず、活用モードへの入力として使う
- `/spike` スキルとの親和性が高い（プロトタイプ = 探索、本実装 = 活用）

### 6.2 改善すべきもの

#### A. Reflection Prompt のテンプレート化

**MR-Search の Reflection Prompt**:
> "Reflect on your current answer to the question and provide another answer by searching for additional external information using search engines. You must conduct reasoning inside <think> and </think> first every time you get new information. After reasoning, if you find you lack some knowledge, you can call a search engine..."

**改善対象**: `completion-gate.py` のリトライ時、`error-to-codex.py` のエラー分析時
- 現在は「テストが失敗しました」+ エラー出力のみ
- MR-Search 式の構造化 reflection prompt を追加: 「前回の試行を振り返り、不足していた知識を特定し、別のアプローチで再試行せよ」

#### B. Session Metrics の Dense 化

**現状**: session-metrics.jsonl にセッション単位のメトリクスを記録
**改善**: ツール呼び出し単位（Step-Level）のメトリクスを追加

```jsonl
{"session_id": "...", "step": 3, "tool": "Bash", "result": "error", "recovery": "self-corrected", "turns_to_fix": 2}
```

- MR-Search の Step-Level Meta-RL に相当
- AutoEvolve の分析精度が向上（どのステップで失敗しやすいかの統計）

#### C. コンテキスト管理の最適化

**MR-Search の知見**: 直前エピソードのみで 96% の性能（Short Context）
**改善対象**: `output-offload.py` と `PreCompact` hook

- 現在の Half-Clone（PreCompact 時に要約を保存）を拡張
- 「直前の重要なツール結果のみ保持、それ以前はサマリ化」戦略
- MR-Search が示した「全履歴 vs 直前のみ」のトレードオフ比率 (96%) を参考に

### 6.3 覚えておくべきもの

#### 1. 「探索不足が推論能力不足より大きなボトルネック」

> エージェントの失敗の多くは「考える力が足りない」のではなく「見るべきものを見ていない」ことに起因する。

→ recall > precision の原則（CLAUDE.md の「探索は広く、理解は深く」と一致）
→ エージェントの改善で「推論の質」より「探索の幅」を優先すべき場面が多い

#### 2. 「自己省察はプロセス報酬を代替できる」

> 外部のアノテーションや評価モデルなしで、エージェント自身の省察が中間報酬として機能する。

→ AutoEvolve で外部評価に依存せず、エージェント自身の振り返りを学習信号にできる
→ `/review` で外部 LLM Judge を使わずとも、自己省察ベースの品質推定が可能

#### 3. 「小さいモデルほど自己省察の恩恵が大きい」

> 3B で 19.3% 改善 vs 7B で 9.2% 改善

→ サブエージェント（haiku 等の小モデルを使う場合）に自己省察パターンを導入すると効果大
→ Codex/Gemini への委譲時、reflection step を明示的に含めることで品質向上の余地

#### 4. 「テスト時スケーリングは訓練と推論の設計を統一すべき」

> Search-R1 + 推論時省察 = 改善なし。MR-Search（訓練時から省察）+ 推論時省察 = 急勾配で改善。

→ 「後付けの省察」は効果薄。**訓練/設計段階から省察を組み込む**必要がある
→ harness の hook/skill は「最初から省察を前提とした設計」であるべき

#### 5. 「RLOO は GRPO より安全で PPO より軽量」

> GRPO は過信のリスク、PPO は価値関数のオーバーヘッド。RLOO は unbiased で critic-free。

→ 複数レビューアーの統合時、「Leave-One-Out」方式（1つを除いた平均と比較）が robust
→ review 信頼度スコアの新しい計算方式として検討可能

#### 6. 「Context Window の 96% ルール」

> 全履歴を保持する必要はない。直前のエピソードのみで 96% の性能。

→ コンテキスト圧縮の設計指針: 直前の重要イベントを高忠実度で保持、それ以前はサマリ
→ `output-offload.py` の閾値設計、`PreCompact` の保持対象選定に活用

---

## 7. 現行ハーネスとのギャップ分析

dotfiles の自己改善アーキテクチャを精査した結果、MR-Search が解決する問題と直接対応する **5つのギャップ** を特定した。

### 現行アーキテクチャの強み（MR-Search と既に一致している部分）

| MR-Search の概念 | 現行ハーネスの対応物 | 状態 |
|-----------------|-------------------|------|
| Cross-episode learning | AutoEvolve 4層ループ (session→daily→cron→on-demand) | ✅ 実装済み |
| Process reward signals | GP-001〜011 による inline feedback (golden-check.py) | ✅ 実装済み |
| Error→Recovery pairs | session-learner.py の recovery-tips extraction | ✅ 実装済み |
| Failure mode taxonomy | FM-001〜015 (session_events.py) | ✅ 実装済み |
| Pattern codification | continuous-learning skill + MEMORY.md elevation | ✅ 実装済み |
| Test-based completion gate | completion-gate.py (MAX_RETRIES=2) | ✅ 実装済み |

### 特定されたギャップ（MR-Search が示唆する改善点）

| # | ギャップ | MR-Search の対応概念 | 影響度 |
|---|--------|---------------------|--------|
| **G-1** | **明示的な省察プロンプトがない** — リトライ時に生のエラー出力のみ注入。「何が不足していたか」「次に何を変えるか」の構造化された内省を促していない | Reflection Prompt (§3.2) | 高 |
| **G-2** | **失敗履歴に基づく適応的プロンプティングがない** — 同一セッション内で failure history を活用したプロンプト調整が行われていない | Meta-Episode conditioning (a_n conditioned on a₀...a_{n-1}) | 高 |
| **G-3** | **マルチステップ間の信用割当がない** — イベントは記録されるが、因果関係（どのステップの判断が最終失敗の原因か）はモデル化されていない | Turn-level RLOO advantage (§3.3) | 中 |
| **G-4** | **テスト時推論の最適化がない** — completion-gate は全テスト実行。ターゲット回帰テスト選択や段階的検証がない | Test-Time Scaling (§4.3) | 中 |
| **G-5** | **セッション中の自己パフォーマンス内省がない** — タスク完了時の retrospective はあるが、実行中の mid-task reflection がない | In-context adaptation across episodes | 低 |

### ギャップ→施策マッピング

```
G-1 (省察プロンプトなし)
  → Phase 1: completion-gate.py に Reflection Prompt テンプレート注入
  → Phase 1: error-to-codex.py にも同様のパターン適用

G-2 (適応的プロンプティングなし)
  → Phase 1: session-load.js で前セッション learnings の Short Context 注入
  → Phase 2: completion-gate リトライ時に前回失敗コンテキストを構造化注入

G-3 (信用割当なし)
  → Phase 2: Step-Level メトリクス + session_events.py に因果チェーン記録
  → Phase 3: RLOO 式レビュー信頼度（複数レビューアーの Leave-One-Out 比較）

G-4 (テスト最適化なし)
  → Phase 2: completion-gate で変更ファイルに関連するテストのみ優先実行
  → Phase 3: 段階的検証（unit → integration → e2e の順）

G-5 (mid-task 内省なし)
  → Phase 3: 長時間タスク（30分超）で自動 checkpoint + 進捗自己評価
```

---

## 8. 実装ロードマップ

### Phase 1: Quick Wins (S サイズ) — G-1, G-2 対応

| 施策 | 対象ファイル | 効果 |
|------|------------|------|
| Reflection prompt テンプレート追加 | `completion-gate.py` | リトライ時の修正精度向上 |
| 前セッション learnings の注入 | `session-load.js` | Cross-episode 学習の実現 |
| RLOO 式レビュー信頼度 | `review` skill | 偽陽性フィルタの改善 |

### Phase 2: Medium Effort (M サイズ)

| 施策 | 対象ファイル | 効果 |
|------|------------|------|
| Step-Level メトリクス記録 | `session_events.py` | AutoEvolve 分析精度向上 |
| 探索/活用モード分離 | `agent-router.py` | 複雑タスクの成功率向上 |
| Short Context 戦略 | `output-offload.py`, PreCompact hook | トークン効率改善 |

### Phase 3: Strategic (L サイズ)

| 施策 | 対象ファイル | 効果 |
|------|------------|------|
| 構造化 Meta-Episode ループ | `autonomous` skill | 自律実行の品質向上 |
| Self-Reflection 評価器 | `autoevolve-core` | 省察品質の定量評価 |

---

## 8. 参考文献（論文内の重要引用）

| 論文 | 貢献 | arXiv |
|------|------|-------|
| Search-R1 (Jin et al., 2025) | RL ベースの検索エージェント訓練の基盤 | 2503.09516 |
| RL² (Duan et al., 2016) | In-context meta-RL の元祖 | 1611.02779 |
| Reflexion (Shinn et al., 2023) | 言語エージェントの自己省察 | — |
| Self-Refine (Madaan et al., 2023) | 自己フィードバックによる反復改善 | — |
| RLOO (Kool et al., 2019; Ahmadian et al., 2024) | Leave-One-Out ベースラインの理論的基盤 | — |
| MRT (Qu et al., 2025) | テスト時計算のメタ RL 最適化 | 2503.07572 |
| ReSearch (Chen et al., 2025) | 検索と推論のインターリーブ訓練 | 2503.19470 |
| Algorithm Distillation (Laskin et al., 2023) | In-context RL のアルゴリズム蒸留 | — |
| GRPO 過信問題 (Bereket & Leskovec, 2025) | GRPO の overconfidence リスク | 2508.11800 |

---

## 9. 結論

MR-Search は「エージェントの自己省察を訓練可能な構造として定式化する」という、シンプルだが強力なアイデアを提示した。この論文の最大の価値は、自己省察が外部報酬モデルを代替できることの実証的証明にある。

dotfiles ハーネスへの最大の示唆は:
1. **completion-gate のリトライを「構造化された省察ループ」に昇格**
2. **AutoEvolve のセッション間学習に Cross-Episode パターンを導入**
3. **「96% ルール」に基づくコンテキスト管理の最適化**

これらは既存の harness アーキテクチャに自然に統合可能であり、特に Phase 1 の Quick Wins は即時実装が可能。
