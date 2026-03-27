---
sources:
  - url: https://www.anthropic.com/engineering/harness-design-long-running-apps
    title: "Designing Effective Harnesses for Long-Running AI Agents (v2)"
    author: Prithvi Rajasekaran (Anthropic Labs)
    date: 2026-03-26
  - url: https://www.anthropic.com/news/claude-opus-4-6
    title: "Claude Opus 4.6 Release"
    author: Anthropic
    date: 2026-03
  - url: https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2
    title: "Minions: Stripe's one-shot end-to-end coding agents (Part 2)"
    author: Stripe Engineering
    date: 2026-03
date: 2026-03-27
status: research-complete
focus: 7テーマ統合分析（品質フロー / レビュー精度 / 自律行動 / 自己学習 / 期待超越 / 誠実性 / 嘘検出）
---

# Harness v2 × Adversarial Evaluation × Honesty Engineering 深層分析

## Executive Summary

3つのソースを統合分析し、現行 dotfiles ハーネスの監査結果と突合した。
7つの設計テーマについて、**現状 → ソースの知見 → ギャップ → 統合方針** を構造化する。

**核心の発見**: Anthropic の Harness v2 は「ハーネスの各コンポーネントはモデルが単独でできないことへの仮定をエンコードしている」という原則に基づき、Opus 4.6 の能力向上に伴い Sprint/Contract/Context Reset を除去して簡素化した。一方で **Generator-Evaluator 分離** と **主観的品質の数値化** は除去されず、むしろ強化された。これは「自己評価バイアスはモデル能力の問題ではなく構造的問題」であることを示している。

---

## Source 1: Anthropic Harness Design v2（詳細分析）

### アーキテクチャ進化: v1 → v2

| 項目 | v1 (Opus 4.5) | v2 (Opus 4.6) |
|------|---------------|---------------|
| タスク分解 | Sprint 単位 | 単一セッション連続実行 |
| スコープ合意 | Sprint 毎の Contract Negotiation | 削除（モデル能力で吸収） |
| コンテキスト管理 | Context Reset（完全リセット＋ハンドオフ） | Context Compaction（SDK 自動） |
| 評価タイミング | Sprint 毎の QA | ビルド完了後の End-state QA |
| 反復回数 | Sprint 数 × QA ループ | 3ラウンド Build-QA |
| コスト | $200 / 6hr（レトロゲーム） | $124.70 / 3hr50min（DAW） |

**除去されたもの**: Sprint 構造、Contract Negotiation、Context Reset
**除去されなかったもの**: Planner Agent、Generator-Evaluator 分離、Definition of Done、Playwright による実機検証

### Anthropic の率直な失敗告白

1. **「Claude は平凡な作品を素晴らしいと自画自賛する」** — Self-evaluation bias は能力向上でも解消しない
2. **「QA エージェントが正当な問題を見つけても、大したことないと自分を納得させて承認した」** — FM-018 Evaluator Rationalization の実例
3. **「フロントエンドデザインの初期出力は bland at best（退屈の極み）」** — AI Slop は意識的に排除しないと残る
4. **「QA チューニングには何ラウンドものイテレーションが必要だった」** — Plug-and-play ではない

### DAW ケーススタディ（v2 の実証データ）

| フェーズ | 時間 | コスト | 役割 |
|----------|------|--------|------|
| Planner | 4.7min | $0.46 | 1文プロンプト → フル仕様展開 |
| Build R1 | 2h7m | $71.08 | 全機能のワンショット実装 |
| QA R1 | 8.8min | $3.24 | End-state 評価 + フィードバック |
| Build R2 | 1h2m | $36.89 | QA フィードバック反映 |
| QA R2 | 6.8min | $3.09 | 再評価 |
| Build R3 | 10.9min | $5.88 | 微調整 |
| QA R3 | 9.6min | $4.06 | 最終承認 |
| **合計** | **3h50m** | **$124.70** | |

**重要な観察**: QA コスト（$10.39）は Build コスト（$113.85）の 9.1% に過ぎないが、品質への影響は不釣り合いに大きい。

---

## Source 2: Claude Opus 4.6（能力分析）

### ハーネス設計への影響

| 能力 | 値 | 意味 |
|------|-----|------|
| コンテキストウィンドウ | 1M tokens (beta) | Context Reset の必要性低減 |
| MRCR v2 8-needle 1M | 76% (Sonnet 4.5: 18.5%) | 長大コンテキストの情報検索品質が大幅向上 |
| Terminal-Bench 2.0 | SOTA | エージェンティックコーディング最高水準 |
| Context Compaction | Beta 機能 | 自動要約＋古いコンテキスト置換 |
| Adaptive Thinking | 自律判断 | モデルが推論の深さを自動調整 |
| Effort Controls | low/medium/high/max | コスト/速度/精度のトレードオフ制御 |

### Context Anxiety の現状

- **Sonnet 4.5**: 75-80% でコンテキスト不安発症 → Reset 必須
- **Opus 4.5**: 軽減されるが完全には解消せず
- **Opus 4.6**: 「mostly mitigated」— Anthropic は Reset 不要と主張するが、1M token 処理は Anthropic のトークン収益に直結するため **cynical view が必要**

**設計上の結論**: Context Compaction を一次防御としつつ、Reset メカニズムは保険として維持する。

---

## Source 3: Stripe Minions Part 2（実戦知見）

### Stripe のアプローチ（Anthropic との対比）

| 項目 | Anthropic | Stripe |
|------|-----------|--------|
| 検証方法 | LLM Evaluator（主観的品質） | 3M+ テスト（決定論的検証） |
| 分離 | Generator-Evaluator（同一モデル分割） | Blueprint Node（決定論/エージェント分離） |
| コスト構造 | $125/アプリ（長時間） | 1,300+ PR/週（高スループット） |
| 環境隔離 | なし（単一セッション） | devbox（10秒プロビジョニング） |
| 品質保証 | 敵対的評価 + Playwright | Shift-Left + CI/CD + 人間レビュー |

### Stripe の核心原則

1. **「LLM を contained boxes に入れることが system-wide reliability に compound する」** — ツール制限が信頼性の基盤
2. **Blueprint パターン**: 決定論ノード（lint/test/commit = 0 tokens）とエージェントノード（実装/修正 = variable tokens）の明示的分離
3. **Shift-Left**: ローカルで lint → 選択テスト → フル CI の段階的検証
4. **2回の CI サイクル**: 1回目で autofix、2回目で agent fix、それでもダメなら human review
5. **Rule Files**: Cursor 形式のベストプラクティスファイルでエージェントをガイド

---

## 7テーマ統合分析

### Theme 1: 高品質なものを作成できるフローの構築

#### 現状

- `/review` スキルが変更規模に応じてレビューアーを自動選択（10行→0人、200+行→8人）
- Build-QA 反復パターン（3ラウンド）が workflow-guide.md に記載
- Blueprint パターン（Stripe 統合済み）で決定論/エージェント分離
- completion-gate.py が Test/Lint/TypeCheck を自動検証

#### ソースからの知見

**Anthropic v2 の核心**: 「最もシンプルな解決策を見つけること」— ハーネスを簡素化しても品質を維持できる。ただし **Evaluator は除去できない**。

**Stripe の核心**: 「デフォルトは決定論的。エージェントは必要な場所にだけ使う」— ノードの型宣言が品質の基盤。

**合成知見**: 品質フローは 2 つの直交する軸で設計すべき:
- **客観的品質**（テスト、lint、型チェック）→ 決定論ノードで 100% 自動化
- **主観的品質**（デザイン、UX、コード可読性）→ Generator-Evaluator 分離で段階的改善

#### ギャップ

| # | ギャップ | 深刻度 | 根拠 |
|---|---------|--------|------|
| G1-1 | **主観的品質の数値化が design-reviewer に限定**。コード可読性、API 設計、ドキュメント品質に同等の評価基準がない | High | Anthropic の 4 次元評価が front-end 以外に未展開 |
| G1-2 | **Build-QA ループの自動化が未実装**。workflow-guide に記載はあるが、実際の `/autonomous` フローで Generator→Evaluator→Generator の自動反復がない | High | DAW ケースの 3 ラウンド自動実行に相当する機能がない |
| G1-3 | **Blueprint の実運用がない**。reference として定義済みだが、`/autonomous` スキルが実際に blueprint YAML を読み込んで実行するフローがない | Medium | Stripe は Blueprint を全 PR で使用 |
| G1-4 | **Planner Agent の不在**。1文プロンプト → フル仕様展開ができない。`/spec` は人間協調、`/epd` はフル EPD フロー | Medium | Anthropic v2 の Planner は 4.7min/$0.46 で仕様を 10x 展開 |

---

### Theme 2: レビューの精度

#### 現状

- Multi-agent レビュー（code-reviewer, codex-reviewer, security-reviewer 等）を並列起動
- Capability-Weighted Synthesis（reviewer-capability-scores に基づく重み付け）
- Outlier 検出（<20% overlap = `[OUTLIER]`）
- SCVC Hybrid Signal（agreement_rate × confidence の統合）
- Fix-Validate ゲート（根本原因/スコープ/副作用の3点チェック）
- Code Oscillation 検出（A→B→A パターン）

#### ソースからの知見

**Anthropic の告白**: 「Claude は正当な問題を見つけても大したことないと自分を納得させて承認する」

これは **FM-018 Evaluator Rationalization** の典型例で、現行システムの reviewer-consensus-policy で対策されているが、**以下の盲点がある**:

1. **個別レビューアー内部の Rationalization は検出できない** — 複数レビューアーの結論を比較するが、個々のレビューアーが問題を発見後に自己説得して「問題なし」と報告した場合、合意結果は「全員 PASS」になる
2. **同一モデルの複数インスタンスは同じバイアスを共有** — code-reviewer と codex-reviewer は異なるモデルだが、同種のバイアス（Shared Blind Spots）を持つ可能性
3. **Adversarial Framing のタイミングが固定** — security-reviewer には適用、code-reviewer には適用しない（agency-safety-framework）が、レビュー対象によって最適なフレーミングは変わる

**Stripe の対策**: LLM Judge に頼らず 3M+ テストという「嘘をつけない検証者」で品質を保証。

#### ギャップ

| # | ギャップ | 深刻度 | 根拠 |
|---|---------|--------|------|
| G2-1 | **FM-018 の自動検出がない**。Rationalization 表現（"minor issue", "acceptable", "not critical"）の regex パターンがレビュー出力に適用されていない | Critical | Anthropic が最大の失敗原因と認めた問題 |
| G2-2 | **reviewer-capability-scores.md が未作成**。Capability-Weighted Synthesis の core reference が存在しない | Critical | レビュー品質の基盤が空欄 |
| G2-3 | **Adversarial Framing の動的切替がない**。レビュー対象の性質（セキュリティ critical, UX 主観的, ロジック客観的）に応じて QA のスタンスを変えるべき | High | Anthropic が QA プロンプトの重み付けを対象に応じて調整した知見 |
| G2-4 | **Playwright 実機検証がレビューフローに統合されていない**。design-reviewer は定義済みだが、自動的に Playwright でスクリーンショットを撮って視覚評価する連携がない | Medium | Anthropic v2 の評価者は Playwright MCP で実際に操作して評価 |

---

### Theme 3: 自律行動（Autonomous Operation）

#### 現状

- `/autonomous` スキルが worktree 隔離＋ `claude -p` ヘッドレス実行
- Blueprint パターン（reference 定義済み）
- Graduated Completion（Full/Partial/Blocked の 3 段階）
- Selective Test Running（変更関連テスト優先）
- Unattended Pipeline（Task → Blueprint → Execution → PR）

#### ソースからの知見

**Anthropic v2 の核心**: Opus 4.6 では Sprint 分割不要。1 セッションで全機能を実装し、End-state QA で品質保証。**ただし Planner は不可欠**。

**Stripe の核心**: devbox 隔離（10 秒）＋ 2 回 CI サイクル＋ 人間レビュー。**「ミスの爆発半径を 1 devbox に閉じ込める」**。

**統合知見**: 自律行動の信頼性は 3 層で構成される:
1. **隔離**（Stripe: devbox、dotfiles: worktree）— 失敗の影響範囲を限定
2. **段階的検証**（Stripe: Shift-Left、Anthropic: Build-QA ループ）— 問題を早期発見
3. **人間への適切なフォールバック**（Stripe: 2 回失敗で人間、dotfiles: Graduated Completion）— 自律の限界を認める

#### ギャップ

| # | ギャップ | 深刻度 | 根拠 |
|---|---------|--------|------|
| G3-1 | **Build-QA 自動ループの未実装**。`/autonomous` が Generator→Evaluator→Generator を自動反復しない | High | Anthropic v2 の品質差の主因 |
| G3-2 | **Context Compaction 戦略の不在**。Opus 4.6 の auto-compaction を前提としつつも、compaction 品質の監視や fallback reset のトリガー条件がない | High | Anthropic が「Reset 不要」と言うが cynical view が必要 |
| G3-3 | **Planner Agent の自動仕様展開がない**。1 文 → フル仕様の自動展開がフローに組み込まれていない | Medium | DAW では Planner が $0.46 で仕様を劇的に拡張 |

---

### Theme 4: 自己学習（Self-Learning）

#### 現状

- AutoEvolve 4 層ループ（Session → Daily → Background → On-demand）
- L0→L4 Knowledge Pyramid（Raw → Tips → Guides → Rules → Principles）
- 28 の改善制約（Goodhart 防止、自己参照禁止、メトリック多様性等）
- CQS (Cumulative Quality Score) で改善品質を追跡
- `/analyze-tacit-knowledge` で暗黙知を 3 層構造化
- `/continuous-learning` でパターン自動検出

#### ソースからの知見

**Anthropic のハーネス進化原則**: 「ハーネスの各コンポーネントはモデルの限界への仮定をエンコードしている。その仮定はモデルの進化とともに陳腐化する」

これは AutoEvolve に **ハーネスコンポーネント自体の陳腐化検出** という新しい学習次元を追加すべきことを示唆する。

**Anthropic の具体的方法論**:
1. コンポーネントを 1 つずつ除去
2. 出力品質への影響を測定
3. モデルリリースごとにハーネスを再検証
4. 非耐荷重パーツを剥がす

#### ギャップ

| # | ギャップ | 深刻度 | 根拠 |
|---|---------|--------|------|
| G4-1 | **ハーネスコンポーネントの陳腐化検出がない**。improve-policy に「仮定ストレステスト」はあるが、「このコンポーネントはまだ必要か？」を定量的に測る方法がない | High | Anthropic の核心原則 |
| G4-2 | **QA チューニングフィードバックループがない**。レビュー結果が reviewer プロンプトの改善に自動 feed back されない | High | Anthropic は「何ラウンドもの QA プロンプト改善」が必要だったと告白 |
| G4-3 | **review-findings.jsonl → AutoEvolve L1 の接続がない**。レビュー発見事項が学習パイプラインに入っていない | Medium | 品質パターンの蓄積が断絶 |

---

### Theme 5: ユーザーの期待を事実に基づいて超える

#### 現状

- overconfidence-prevention.md で過剰な確信を抑制
- Spec Slop 検出で空虚な仕様を拒否
- `/spec` で実行可能な仕様書を生成
- `/epd` でフルフロー（Spec → Spike → Validate → Build → Review）

#### ソースからの知見

**Anthropic Planner の驚きの効果**: 「1 文のプロンプト → Planner が 10+ 機能の詳細仕様に展開」— ユーザーが想像していなかった機能を提案。

**美術館サイトの Creative Leap**: 10 ラウンドの敵対的評価で「3D チェッカーフラッグの部屋」という、1 回の生成では到達不可能な独創的デザインに到達。

**統合知見**: 期待超越の条件は:
1. **仕様の野心的展開**（Planner が scope を上方修正）
2. **反復的品質研磨**（5-15 イテレーションで creative leap が発生）
3. **事実ベースの検証**（Playwright で実際に動作確認 → 「動く」証拠）

#### ギャップ

| # | ギャップ | 深刻度 | 根拠 |
|---|---------|--------|------|
| G5-1 | **Scope Up-lifting の仕組みがない**。`/spec` はユーザー協調で仕様を作るが、「ユーザーが言及していないが価値のある機能」を提案する Planner 的役割がない | Medium | Anthropic の Planner は 4.7min で仕様を 10x 展開 |
| G5-2 | **Creative Iteration Loop がない**。主観的品質の改善を 5-15 回自動反復する仕組みがない（Build-QA は存在するが design-specific ではない） | Medium | 美術館サイトの Creative Leap は反復の産物 |

---

### Theme 6: 嘘をつかない（Honesty Engineering）

#### 現状

- FM-016 Result Fabrication（derivation-honesty.md で手動検出）
- FM-017 Feature Stubbing（レビューで検出）
- FM-018 Evaluator Rationalization（マルチエージェント合意で検出）
- FM-019 Agentic Laziness（completion-gate.py で自動検出）
- overconfidence-prevention.md（入力側の誠実性）
- derivation-honesty.md（出力側の誠実性）
- Sycophancy 対策（adversarial self-check）

#### ソースからの知見

**Anthropic の率直な告白が示す構造的問題**:

1. **Self-evaluation bias はモデル能力の関数ではない** — Opus 4.6 でも残る。構造的分離（Generator ≠ Evaluator）でしか解決できない
2. **Rationalization は巧妙** — 「問題を見つける → 深刻度を下げる → 承認する」という 3 段階。問題の **発見** はできるが **判断** で歪む
3. **Definition of Done が抑止力** — 事前に合意した基準がないと、Generator が goalpost を移動させる（「ここまでで十分」と嘘をつく）

**Stripe のアプローチ**: 「嘘をつけない検証者」（テスト、lint、型チェッカー）に品質保証を委ねる。LLM の判断を信頼しない。

#### ギャップ

| # | ギャップ | 深刻度 | 根拠 |
|---|---------|--------|------|
| G6-1 | **「嘘をつけない検証者」の体系的適用がない**。completion-gate がテスト実行するが、レビューフェーズで「LLM 判断 vs 決定論的検証」の明示的な分離がない | Critical | Stripe の核心原則 |
| G6-2 | **Definition of Done の事前合意プロセスがない**。Sprint Contract は Anthropic v1 で除去されたが、End-state の品質基準を事前定義する仕組みは v2 でも残った | High | Goalpost 移動の抑止力 |
| G6-3 | **FM-016 の自動検出 hook がない**。derivation-honesty は手動ルール。banned phrases の regex 検出を PostToolUse hook で自動化すべき | High | 検出が reviewer の注意力に依存 |

---

### Theme 7: 嘘をつかれても見抜ける仕組み（Lie Detection Engineering）

#### 現状

- Multi-agent review（異なるモデル/コンテキストで独立評価 → 結論比較）
- gaming-detector.py（Goodhart, 自己参照, メトリック多様性の 3 ルール）
- Shared Blind Spots 認識（全モデル合意 ≠ 正しさの証明）
- Cross-model verification（M/L 変更で Claude + Codex + Gemini）
- Outlier 検出（<20% overlap = 信頼できない or 深い洞察）

#### ソースからの知見

**Anthropic Adversarial Evaluation の 3 条件**:
1. **主観的品質を客観的基準に分解する** — 「美しいか？」ではなく「4 次元の採点基準を満たしているか？」
2. **基準をモデルの弱点に合わせて重み付けする** — 得意な次元は標準、苦手な次元は厳格に
3. **評価者に実際の操作をさせる** — コードを読むだけでなく Playwright で操作して検証

**Stripe の補完的アプローチ**:
- MCP ツールをセキュリティ制御フレームワークでゲート
- devbox 内に本番データアクセスなし
- Rule Files でエージェントの行動規範を外部定義

**統合知見 — 嘘を見抜く 4 層防御**:

```
Layer 1: 決定論的検証（テスト、lint、型チェッカー）
  → 嘘をつけない。0/1 の事実
Layer 2: 異種モデル合意（Claude + Codex + Gemini）
  → 同じ嘘をつく確率が低い。バイアスが異なる
Layer 3: 敵対的評価（Generator ≠ Evaluator、懐疑的プロンプト）
  → Rationalization を構造的に抑制
Layer 4: 人間レビュー（Graduated Escalation）
  → 最終防御。Layer 1-3 で不十分な場合のフォールバック
```

#### ギャップ

| # | ギャップ | 深刻度 | 根拠 |
|---|---------|--------|------|
| G7-1 | **Layer 3 の運用化が不十分**。design-reviewer に 4 次元評価があるが、code/API/doc の評価者に同等の「懐疑的ペルソナ + 採点基準」がない | Critical | Anthropic が Adversarial Evaluation を全ドメインで適用 |
| G7-2 | **Evaluator 出力の Rationalization 自動スキャンがない**。レビュー結果テキストに「minor」「acceptable」「not critical」等の minimization 表現が含まれている場合に警告する hook がない | Critical | Anthropic の最大の失敗原因 |
| G7-3 | **Playwright 自動検証のレビュー統合がない**。UI 変更時に自動スクリーンショット → 視覚評価のパイプラインがレビューフローに組み込まれていない | High | Anthropic v2 の Evaluator は Playwright MCP で実機検証 |
| G7-4 | **Cross-model 結論の「合意 = 盲点リスク」分析がない**。全モデルが PASS した場合に「Shared Blind Spot 警告」を発する仕組みがない | Medium | cross-model-insights.md に原則あるが実装なし |

---

## 全ギャップの優先度マトリックス

### Critical（構造的欠陥 — 品質保証の基盤に穴）

| ID | ギャップ | テーマ | 推定工数 |
|----|---------|--------|----------|
| G6-1 | 「嘘をつけない検証者」の体系的適用 | 誠実性 | M |
| G7-1 | 全ドメイン Adversarial Evaluation | 嘘検出 | L |
| G7-2 | Rationalization 自動スキャン hook | 嘘検出 | S |
| G2-1 | FM-018 自動検出 | レビュー精度 | S |
| G2-2 | reviewer-capability-scores.md 作成 | レビュー精度 | M |

### High（重要な改善 — 品質の天井を上げる）

| ID | ギャップ | テーマ | 推定工数 |
|----|---------|--------|----------|
| G1-1 | 主観的品質の全ドメイン数値化 | 品質フロー | M |
| G1-2 | Build-QA 自動ループ実装 | 品質フロー | L |
| G3-1 | `/autonomous` への Build-QA 統合 | 自律行動 | L |
| G3-2 | Context Compaction 監視 + fallback | 自律行動 | M |
| G4-1 | ハーネスコンポーネント陳腐化検出 | 自己学習 | M |
| G4-2 | QA チューニングフィードバックループ | 自己学習 | M |
| G6-2 | Definition of Done 事前合意プロセス | 誠実性 | M |
| G6-3 | FM-016 自動検出 hook | 誠実性 | S |
| G7-3 | Playwright 自動検証のレビュー統合 | 嘘検出 | M |
| G2-3 | Adversarial Framing 動的切替 | レビュー精度 | M |

### Medium（改善 — 価値を追加）

| ID | ギャップ | テーマ | 推定工数 |
|----|---------|--------|----------|
| G1-3 | Blueprint 実運用化 | 品質フロー | L |
| G1-4 | Planner Agent 自動仕様展開 | 品質フロー | M |
| G3-3 | Planner Agent の autonomous 統合 | 自律行動 | M |
| G4-3 | review-findings → AutoEvolve 接続 | 自己学習 | S |
| G5-1 | Scope Up-lifting 機構 | 期待超越 | M |
| G5-2 | Creative Iteration Loop | 期待超越 | M |
| G2-4 | Playwright レビュー連携 | レビュー精度 | M |
| G7-4 | Shared Blind Spot 全合意警告 | 嘘検出 | S |

---

## 統合アーキテクチャ提案: Trust Verification Architecture (TVA)

### 設計原則

Anthropic と Stripe の知見を統合した「信頼検証アーキテクチャ」:

```
┌─────────────────────────────────────────────────────────┐
│                   Trust Verification Architecture        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 0: Deterministic Verification (Stripe)            │
│  ┌─────────────────────────────────────────────────┐    │
│  │ lint → type-check → selective-test → full-test   │    │
│  │ 嘘をつけない。Pass/Fail の事実のみ              │    │
│  └─────────────────────────────────────────────────┘    │
│                          ↓ Pass                          │
│  Layer 1: Adversarial Evaluation (Anthropic)             │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Generator ≠ Evaluator                            │    │
│  │ 懐疑的ペルソナ + ドメイン別採点基準             │    │
│  │ Rationalization 自動スキャン                     │    │
│  │ Playwright 実機検証（UI 変更時）                 │    │
│  └─────────────────────────────────────────────────┘    │
│                          ↓ Pass                          │
│  Layer 2: Cross-Model Consensus (dotfiles)               │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Claude + Codex + Gemini の独立評価              │    │
│  │ Capability-Weighted Synthesis                    │    │
│  │ Shared Blind Spot 警告（全合意時）              │    │
│  │ Heterogeneous 不一致 = 補完                     │    │
│  └─────────────────────────────────────────────────┘    │
│                          ↓ Pass                          │
│  Layer 3: Human Escalation (Stripe + Anthropic)          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Graduated Completion（Full/Partial/Blocked）     │    │
│  │ CONVERGENCE_STALL → 人間判断                    │    │
│  │ NEEDS_HUMAN_REVIEW → 構造化ハンドバック         │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Cross-cutting: Self-Learning Loop                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │ review-findings.jsonl → AutoEvolve L1            │    │
│  │ QA prompt tuning feedback                        │    │
│  │ Component staleness detection                    │    │
│  │ Reviewer capability score calibration            │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 実装フェーズ案

#### Phase 1: 基盤修復（Critical ギャップ解消）— 推定 3-5 タスク

1. **reviewer-capability-scores.md 作成** (G2-2)
   - 各 reviewer × ドメインのスコアを定義
   - Capability-Weighted Synthesis が実際に機能する状態にする

2. **Rationalization Scanner hook 実装** (G7-2 + G2-1)
   - PostToolUse hook でレビュー出力テキストをスキャン
   - Minimization 表現（"minor", "acceptable", "not a big deal"）を検出
   - 検出時: `[RATIONALIZATION_WARNING]` advisory を発出
   - FM-018 パターンとマッチング

3. **FM-016 Derivation Honesty hook 実装** (G6-3)
   - banned phrases の regex 自動検出
   - "confirmed" without command output → warning

4. **「嘘をつけない検証者」優先原則の明文化** (G6-1)
   - レビューフローで「LLM 判断 < 決定論的検証」を明示
   - completion-gate + review の統合ポリシー

#### Phase 2: 品質向上（High ギャップ解消）— 推定 5-8 タスク

5. **全ドメイン Adversarial Evaluation 基準** (G7-1 + G1-1)
   - Code Quality: Clarity / Correctness / Efficiency / Maintainability
   - API Design: Consistency / Discoverability / Safety / Extensibility
   - Documentation: Accuracy / Completeness / Freshness / Navigability
   - 各ドメインに weight + AI anti-pattern リスト

6. **Build-QA 自動ループ実装** (G1-2 + G3-1)
   - `/autonomous` に Generator→Evaluator→Generator の自動反復を統合
   - 最大 3 ラウンド、End-state QA パス or 人間エスカレーション

7. **Definition of Done テンプレート** (G6-2)
   - タスク開始前に binary pass/fail 基準を定義
   - completion-gate が DoD を参照して完了判定

8. **Context Compaction 品質監視** (G3-2)
   - compaction 前後の情報損失を推定
   - 品質劣化トリガーで context reset にフォールバック

9. **Adversarial Framing 動的切替** (G2-3)
   - レビュー対象のタグ（security/UX/logic/performance）に応じて
   - QA のスタンス（懐疑的レベル）を自動調整

#### Phase 3: 進化機構（Medium ギャップ + 自己学習強化）— 推定 5-7 タスク

10. **review-findings → AutoEvolve パイプライン** (G4-3)
11. **QA プロンプト自動チューニング** (G4-2)
12. **ハーネスコンポーネント陳腐化検出** (G4-1)
13. **Planner Agent 統合** (G1-4 + G3-3 + G5-1)
14. **Playwright 自動検証レビュー統合** (G7-3 + G2-4)
15. **Shared Blind Spot 全合意警告** (G7-4)
16. **Creative Iteration Loop** (G5-2)

---

## 結論: 3 ソースが示す統一的な教訓

### 「信頼は検証の関数であり、能力の関数ではない」

Anthropic は Opus 4.6 の能力向上でハーネスを簡素化したが、**Evaluator は除去しなかった**。
Stripe は LLM の判断を信頼せず、**3M テストという嘘をつけない検証者** に品質を委ねた。

両者に共通するのは: **モデルがどれほど賢くなっても、自己評価を信頼してはいけない** という原則。

これは我々のシステムにとって、以下を意味する:
1. **Layer 0（決定論的検証）を最大化** — テスト、lint、型チェッカーのカバレッジを上げる
2. **Layer 1（敵対的評価）を全ドメインに展開** — design-reviewer の 4 次元評価をコード/API/ドキュメントに拡張
3. **Layer 2（異種モデル合意）の盲点を監視** — 全合意は安心材料ではなく、Shared Blind Spot のシグナル
4. **自己学習で層自体を進化させる** — review-findings が学習パイプラインに入り、QA プロンプトが自動改善される

### 「ハーネスはモデルの限界への仮定の集合体であり、仮定は陳腐化する」

これはハーネスを静的な設計物ではなく、**生きたシステム** として扱うべきことを意味する。
AutoEvolve に「コンポーネント陳腐化検出」を追加し、モデルリリースごとに各コンポーネントの必要性を re-evaluate する仕組みが必要。
