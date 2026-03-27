---
title: Trust Verification Architecture (TVA)
status: implemented
created: 2026-03-27
scope: L
phase_scope: "全 Phase 実装済み（Phase 1+2: commit:fefc275 / Phase 3: Wave 5 実装完了）"
priority_order: "嘘検出/誠実性 > レビュー精度 > 自律行動"
research_source: docs/research/2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md
acceptance_criteria:
  - "AC-01: Rationalization Scanner hook が /review 出力の minimization 表現を検出し [RATIONALIZATION_WARNING] を発出する"
  - "AC-02: reviewer-capability-scores.md が全 reviewer × 全ドメインのスコアを定義し、/review の Capability-Weighted Synthesis が参照する"
  - "AC-03: FM-016 Derivation Honesty hook が banned phrases を自動検出し advisory を発出する"
  - "AC-04: 「嘘をつけない検証者優先」原則が /review と completion-gate に明文化される"
  - "AC-05: 全ドメイン Adversarial Evaluation 基準（Code/API/Doc の 4 次元 + anti-pattern）が reference に定義される"
  - "AC-06: /autonomous が Build-QA 自動ループ（最大 3 ラウンド）を実行する"
  - "AC-07: Definition of Done テンプレートが M/L 規模タスクの Plan 段階で pass/fail 基準を事前定義する"
  - "AC-08: Context Compaction 監視が品質劣化を検知し、fallback reset トリガー条件を定義する"
  - "AC-09: Adversarial Framing がレビュー対象の性質に応じて動的に切り替わる"
  - "AC-10: review-findings.jsonl が AutoEvolve L1 Recovery Tips に自動フィードされ、学習知見として蓄積される"
  - "AC-11: レビュー結果の蓄積データから reviewer プロンプトの改善提案が自動生成される"
  - "AC-12: ハーネスコンポーネント（hook/reference）の必要性を定量評価し、陳腐化したコンポーネントを検出・報告する"
---

# Trust Verification Architecture (TVA) — Prompt-as-PRD

## Context

Anthropic が 2026-03-26 に公開した「Designing Effective Harnesses for Long-Running AI Agents (v2)」で、長時間稼働エージェントの 2 大失敗モード（Context Anxiety + Self-Evaluation Bias）と対策（Context Compaction + Adversarial Evaluation）が実証された。

Anthropic の率直な告白:
- 「Claude は平凡な作品を素晴らしいと自画自賛する」（Self-evaluation bias）
- 「QA エージェントが正当な問題を見つけても大したことないと自分を納得させて承認した」（FM-018 Evaluator Rationalization）
- 「QA チューニングには何ラウンドものイテレーションが必要だった」

Stripe Minions Part 2 の補完的知見:
- 「LLM を contained boxes に入れることが system-wide reliability に compound する」
- 3M+ テストという「嘘をつけない検証者」で品質を保証
- Blueprint パターンで決定論ノード / エージェントノードを明示分離

現行 dotfiles ハーネスの監査で 22 のギャップを発見。本 spec は Critical 5 件 + High 10 件を対象とする。

## Problem Statement

現行ハーネスは Multi-agent レビューと failure taxonomy を持つが、**3 つの構造的欠陥** がある:

1. **嘘の自動検出がない** — FM-016 (Result Fabrication) と FM-018 (Evaluator Rationalization) の検出が手動ルール依存。reviewer が問題を見つけて自己説得で承認する Rationalization パターンを自動検出する hook がない
2. **レビュー精度の基盤が空欄** — reviewer-capability-scores.md が未作成で Capability-Weighted Synthesis が機能していない。Adversarial Evaluation が design-reviewer に限定され、コード/API/ドキュメントに同等の評価基準がない
3. **自律実行の品質保証が弱い** — /autonomous に Build-QA 自動ループがなく、End-state QA（Anthropic v2 の核心機構）に相当する仕組みがない

## Proposed Solution

### Trust Verification Architecture: 4 層信頼検証

```
Layer 0: Deterministic Verification（嘘をつけない検証者）
  lint → type-check → selective-test → full-test
  Pass/Fail の事実。LLM 判断より常に優先

Layer 1: Adversarial Evaluation（敵対的評価）
  Generator ≠ Evaluator の構造的分離
  懐疑的ペルソナ + ドメイン別採点基準 + Rationalization 自動スキャン

Layer 2: Cross-Model Consensus（異種モデル合意）
  Claude + Codex + Gemini の独立評価
  Capability-Weighted Synthesis + Shared Blind Spot 警告

Layer 3: Human Escalation（人間エスカレーション）
  Graduated Completion + CONVERGENCE_STALL → 人間判断
```

## Requirements

### Phase 1: 基盤修復（嘘検出 + レビュー精度の構造的欠陥を解消）

#### R-01: Rationalization Scanner Hook

**ゴール**: レビュー出力に含まれる Rationalization パターンを自動検出する

- PostToolUse hook（Agent ツール）でレビューアー出力テキストをスキャン
- Minimization 表現の検出:
  - 英語: "minor issue", "not critical", "acceptable", "not a big deal", "can be addressed later", "low priority but"
  - 日本語: "軽微", "許容範囲", "大きな問題ではない", "後で対応", "致命的ではない"
- 検出パターン: 「問題の発見 → 深刻度の引き下げ → 承認」の 3 段階シーケンス
- 出力: `[RATIONALIZATION_WARNING]` advisory（additionalContext）
- **技術方針**: hook（明確なパターン）で検出。判断が必要な文脈分析は reviewer agent に委ねる（ハイブリッド）

#### R-02: Reviewer Capability Scores 定義

**ゴール**: Capability-Weighted Synthesis の基盤を作る

- `references/reviewer-capability-scores.md` を新規作成
- 全 reviewer（code-reviewer, codex-reviewer, security-reviewer, design-reviewer, product-reviewer, golang-reviewer, silent-failure-hunter, edge-case-hunter, cross-file-reviewer, comment-analyzer, type-design-analyzer）× ドメイン（security, performance, correctness, style, architecture, UX, documentation）のスコアマトリックス
- スコアは 0.0-1.0、初期値は定性的判断で設定し、review-findings.jsonl のデータ蓄積で将来キャリブレーション
- `/review` SKILL.md の Step 4 Synthesis が参照する形式で記述

#### R-03: FM-016 Derivation Honesty Hook

**ゴール**: Result Fabrication の banned phrases を自動検出する

- PostToolUse hook（Bash/Write/Edit）で出力テキストをスキャン
- Banned phrases（derivation-honesty.md から転載）:
  - "confirmed" / "確認しました" without preceding verification command
  - "this becomes" / "これは〜になります" without intermediate steps
  - "generally" / "一般的には" without project-specific evidence
  - "obvious" / "自明" as justification for step-skipping
- 検出時: `[DERIVATION_HONESTY_WARNING]` advisory
- **技術方針**: regex パターンマッチ（hook 側）。文脈依存の判断は agent 任せ

#### R-04: 「嘘をつけない検証者」優先原則の明文化

**ゴール**: Layer 0（決定論的検証）が Layer 1-2（LLM 判断）より常に優先される原則を制度化する

- `references/trust-verification-policy.md` 新規作成
  - 原則: テスト結果 > レビュー合意 > 自己評価
  - レビューで「問題なし」でもテストが失敗していれば BLOCK
  - 「全 reviewer が PASS でもテスト未実行は PASS とみなさない」
- completion-gate.py に明示的な Layer 0 チェック追加
  - テスト実行済みかの確認を Review Gate より前に配置
- `/review` SKILL.md の Step 4 に Layer 0 優先ルールを追加

#### R-05: Reviewer Capability Score Calibration Feedback Loop（Phase 3 準備）

**ゴール**: 将来のスコアキャリブレーションに必要なデータ構造を定義する

- review-findings.jsonl に `reviewer_id` と `human_verdict`（AGREE/DISAGREE/UNKNOWN）フィールドを追加
- `/review` の findings 出力にこれらのフィールドを含める
- Phase 3 で review-findings → AutoEvolve L1 パイプラインを構築する際の入力フォーマットとして機能

### Phase 2: 品質向上（レビュー精度 + 自律行動の天井を上げる）

#### R-06: 全ドメイン Adversarial Evaluation 基準

**ゴール**: design-reviewer の 4 次元評価をコード/API/ドキュメントに展開する

- `references/adversarial-evaluation-criteria.md` 新規作成
- 3 ドメインの評価基準:

**Code Quality（コード品質）**:
| 次元 | 定義 | Weight |
|------|------|--------|
| Clarity | 意図が読み取れるか。命名、構造、フロー | High |
| Correctness | ロジックが正しいか。エッジケース、nil 安全性 | High |
| Efficiency | 不要な計算・I/O がないか | Standard |
| Maintainability | 変更容易性。結合度、凝集度 | Standard |

**API Design（API 設計）**:
| 次元 | 定義 | Weight |
|------|------|--------|
| Consistency | 命名規則、パラメータ順序、レスポンス形式の統一 | High |
| Discoverability | 使い方が推測可能か。ドキュメントなしで使えるか | High |
| Safety | 不正入力への耐性。型安全性 | Standard |
| Extensibility | 後方互換を保ちつつ拡張可能か | Standard |

**Documentation Quality（ドキュメント品質）**:
| 次元 | 定義 | Weight |
|------|------|--------|
| Accuracy | コードの現状と一致しているか | Critical |
| Completeness | 必要な情報が漏れていないか | High |
| Freshness | 最終更新が妥当か。陳腐化していないか | Standard |
| Navigability | 必要な情報に素早く到達できるか | Standard |

- 各ドメインの **AI Anti-Pattern リスト**（AI Slop 相当）:
  - Code: 過剰な try-catch、意味のないコメント、不要な抽象化
  - API: REST 規約無視、一貫性のないエラー形式、過剰なネスト
  - Doc: コードの繰り返し、実装の 1:1 転記、陳腐化した例

#### R-07: Build-QA 自動ループ（/autonomous 統合）

**ゴール**: /autonomous に Anthropic v2 相当の Generator→Evaluator→Generator ループを統合する

- /autonomous SKILL.md に Build-QA フェーズを追加:
  1. Planner Phase: タスク → フル仕様展開（既存の Plan ステップを活用）
  2. Build Phase: 仕様に基づく実装（既存の実装ステップ）
  3. **QA Phase（新規）**: 専用 Evaluator Agent が成果物を評価
     - Evaluator は懐疑的ペルソナ（"be skeptical, probe edge cases, don't approve easily"）
     - R-06 の評価基準に沿って採点
     - UI 変更時は Playwright MCP でスクリーンショット取得＋視覚評価
     - 具体的なフィードバックを返す
  4. **Iteration（新規）**: Build→QA を最大 3 ラウンド反復
  5. Graduation: 3 ラウンド後も PASS しない場合は Graduated Completion（Partial + handback report）

- QA Agent の起動条件:
  - 変更が 30 行以上（S 規模は skip）
  - `/autonomous` 内での自動実行（対話モードでは `/review` が担当）

#### R-08: Definition of Done テンプレート

**ゴール**: M/L 規模タスクの Plan 段階で binary pass/fail 基準を事前定義する

- `references/definition-of-done-template.md` 新規作成
- Plan 段階で DoD を記述するセクションをテンプレート化:
  ```markdown
  ## Definition of Done
  - [ ] {検証可能な基準 1}（検証方法: {テスト/lint/目視/...}）
  - [ ] {検証可能な基準 2}
  ...
  ```
- completion-gate.py が Plan 内の DoD セクションを検出し、未チェック項目があれば advisory
- DoD は Layer 0（決定論的検証）と Layer 1（主観的評価）の両方を含む
- 適用レベル: **M/L 規模のみ**。S 規模では省略可

#### R-09: Context Compaction 品質監視

**ゴール**: Opus 4.6 の auto-compaction に依存しつつ、品質劣化を検知する

- `references/context-compaction-policy.md` 新規作成
- 監視指標:
  - Compaction 前後の plan/DoD/key decisions の保持率
  - 「さっき言ったことを忘れている」兆候（同じ質問の繰り返し、矛盾する判断）
- Fallback トリガー条件:
  - Compaction 後に Plan のステップが欠落した場合 → context reset（session handoff）
  - 3 回以上の compaction で判断の一貫性が低下した場合 → checkpoint + 新セッション推奨
- session-protocol.md に Compaction 関連ルールを追加

#### R-10: Adversarial Framing 動的切替

**ゴール**: レビュー対象の性質に応じて QA のスタンスを自動調整する

- `/review` SKILL.md の Step 2（Scaling Decision）に Framing 選択ロジックを追加:
  | 対象シグナル | Framing | 根拠 |
  |-------------|---------|------|
  | security 変更 | Adversarial（「脆弱性が存在すると仮定せよ」） | agency-safety-framework.md 既存方針 |
  | UX/デザイン変更 | Skeptical（「AI Slop パターンを疑え」） | Anthropic 4 次元評価の知見 |
  | ロジック/アルゴリズム | Neutral + Edge-case Probe | Adversarial は Valid Consensus 低下リスク |
  | ドキュメント変更 | Accuracy-first（「コードとの乖離を探せ」） | doc-gardener の既存方針と整合 |
- Framing は reviewer 起動時のプロンプトに注入（agent 側で柔軟に適用）

### Phase 3: 自己学習パイプライン（ハーネスが自ら進化する仕組み）

#### R-11: review-findings → AutoEvolve L1 接続

**ゴール**: レビュー発見事項が学習パイプラインに自動フィードされ、知見として蓄積される

- review-findings.jsonl の各 finding を AutoEvolve L1（Recovery Tips）に変換するスクリプト
- 変換ルール:
  - `failure_mode` → L1 カテゴリマッピング（FM-001〜FM-020 → 対応する改善カテゴリ）
  - `severity: critical/important` → L1 に昇格。`severity: watch` → 蓄積のみ（3 回出現で昇格）
  - `reviewer_id` + `human_verdict` → reviewer 信頼度の入力データ（R-05 で定義済みのフォーマット）
- `/improve` 実行時に review-findings.jsonl を入力ソースとして読み込む
- 既存の AutoEvolve improve-policy.md の Rule 構造と整合させる

#### R-12: QA チューニングフィードバックループ

**ゴール**: レビュー結果の蓄積データから reviewer プロンプトの改善提案を自動生成する

- review-findings.jsonl の蓄積データを分析し、以下を検出:
  - **見逃しパターン**: human_verdict=DISAGREE が多い reviewer × failure_mode の組み合わせ
  - **過検出パターン**: 同じ reviewer が繰り返し watch レベルの findings を大量発出
  - **Rationalization パターン**: R-01 の warning 頻度が高い reviewer
- 検出結果から reviewer プロンプト改善提案を生成:
  - 「code-reviewer は FM-003 (Dependency Drift) の見逃しが多い → チェックリストに明示追加を推奨」
  - 「codex-reviewer は style 系 findings の過検出傾向 → style weight を下げることを推奨」
- 提案は `/improve` 実行時に advisory として出力。自動適用はしない（Rule 10: LLM self-generated skills excluded from auto-merge）
- reviewer-capability-scores.md のスコア更新提案も含める

#### R-13: ハーネスコンポーネント陳腐化検出

**ゴール**: 「このコンポーネント（hook/reference）はまだ必要か？」を定量評価し、不要なものを検出する

- Anthropic の核心原則: 「ハーネスの各コンポーネントはモデルの限界への仮定をエンコードしている。仮定は陳腐化する」
- 検出方法:
  - **hook 発火率**: 各 hook の発火回数を追跡。30 日間発火 0 回 → `[STALE_HOOK]` 警告
  - **advisory 採用率**: advisory 出力後にユーザーが実際に行動を変えた割合。採用率 < 10% → 「この advisory は無視されている」
  - **reference 参照率**: agent がレビュー/実装時に実際に参照した reference の頻度
- `/improve` 実行時に陳腐化レポートを出力:
  - 「rationalization-scanner.py: 過去 30 日で 47 回発火、うち 38 回で修正に繋がった → 有効」
  - 「XX-hook.py: 過去 30 日で 0 回発火 → 除去候補」
- 除去はユーザー判断（自動除去しない）。Anthropic の方法論: 「1 つずつ除去して品質への影響を測定」
- 発火ログは `logs/hook-telemetry.jsonl` に蓄積

## Constraints

- **既存ハーネスとの互換性**: 現行の `/review`、`/autonomous`、completion-gate.py のインターフェースを破壊しない
- **Hook 実装言語**: 新規 hook は Rust（.bin/ 配下のバイナリ）ではなく Python（scripts/policy/）で実装。既存の gaming-detector.py、completion-gate.py と同じパターン
- **パフォーマンス**: hook の実行時間は 1 秒以内。regex パターンマッチのみで LLM 呼び出しなし
- **段階的導入**: 全 hook は advisory（非ブロッキング）で開始。十分なデータ蓄積後にブロッキングへ昇格検討
- **CLAUDE.md への影響最小化**: IFScale 原則に従い、新しい指示は reference に置き、CLAUDE.md からは参照のみ

## Out of Scope

以下は研究ドキュメント（`docs/research/2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md`）に分析・方針が記録されているが、この spec では扱わない:

| ID | ギャップ | テーマ | 将来の方向性 |
|----|---------|--------|-------------|
| G1-3 | Blueprint 実運用化 | 品質フロー | /autonomous が blueprint YAML を読み込んで実行 |
| G1-4 | Planner Agent 自動仕様展開 | 品質フロー | 1 文 → 10+ 機能仕様の自動展開（Anthropic v2 の $0.46/4.7min Planner） |
| G5-1 | Scope Up-lifting | 期待超越 | ユーザーが言及していないが価値のある機能を提案する Planner 的役割 |
| G5-2 | Creative Iteration Loop | 期待超越 | 主観的品質の 5-15 回自動反復による creative leap |
| G7-4 | Shared Blind Spot 全合意警告 | 嘘検出 | 全 reviewer が PASS 時に「盲点リスク」を明示警告 |
| G2-4 | Playwright レビュー連携 | レビュー精度 | /review から自動的に Playwright スクリーンショット → 視覚評価 |

## Technical Notes

### 依存関係

```
R-01 (Rationalization Scanner) ──── 独立。即実装可能
R-02 (Capability Scores) ────────── 独立。即実装可能
R-03 (FM-016 Hook) ─────────────── 独立。即実装可能
R-04 (Trust Verification Policy) ── R-02 に軽く依存（policy が scores を参照）
R-05 (Calibration Data Format) ──── R-02 に依存

R-06 (Adversarial Evaluation) ───── 独立。ただし R-07 の QA Agent が参照
R-07 (Build-QA Loop) ───────────── R-06 に依存（QA 基準を使用）
R-08 (Definition of Done) ──────── R-07 と連携（DoD を QA が参照）
R-09 (Context Compaction) ──────── 独立
R-10 (Adversarial Framing) ─────── R-06 に軽く依存（ドメイン別基準を参照）

R-11 (AutoEvolve 接続) ─────────── R-05 に依存（データフォーマット使用）
R-12 (QA チューニング) ─────────── R-11 に依存（蓄積データを分析）+ R-02 に依存（scores 更新）
R-13 (陳腐化検出) ──────────────── R-11 に軽く依存（発火ログ基盤を共有）
```

### 実装順序（推奨）

```
Wave 1（並列可能）: R-01, R-02, R-03 — hook 2 本 + reference 1 本         [Phase 1 ✅ 実装済み]
Wave 2（Wave 1 完了後）: R-04, R-05 — policy + data format                [Phase 1 ✅ 実装済み]
Wave 3（並列可能）: R-06, R-09 — reference 2 本                           [Phase 2 ✅ 実装済み]
Wave 4（Wave 3 完了後）: R-07, R-08, R-10 — /autonomous + DoD + framing   [Phase 2 ✅ 実装済み]
Wave 5（Wave 2 完了後）: R-11, R-12, R-13 — 自己学習パイプライン          [Phase 3 ✅ 実装済み]
```

### 変更対象ファイル（予定）

| ファイル | 操作 | 関連 Requirement | 状態 |
|---------|------|-----------------|------|
| `scripts/policy/rationalization-scanner.py` | 新規 | R-01 | ✅ |
| `scripts/policy/derivation-honesty-hook.py` | 新規 | R-03 | ✅ |
| `references/reviewer-capability-scores.md` | 新規 | R-02 | ✅ |
| `references/trust-verification-policy.md` | 新規 | R-04 | ✅ |
| `references/adversarial-evaluation-criteria.md` | 新規 | R-06 | ✅ |
| `references/definition-of-done-template.md` | 新規 | R-08 | ✅ |
| `references/context-compaction-policy.md` | 新規 | R-09 | ✅ |
| `scripts/policy/completion-gate.py` | 修正 | R-04, R-05, R-08 | ✅ |
| `skills/review/SKILL.md` | 修正 | R-04, R-10 | ✅ |
| `skills/autonomous/SKILL.md` | 修正 | R-07 | ✅ |
| `settings.json` | 修正 | R-01, R-03（hook 登録） | ✅ |
| `references/review-consensus-policy.md` | 修正 | R-02（scores 参照追加） | ✅ |
| `scripts/learner/findings-to-autoevolve.py` | 新規 | R-11 | ✅ |
| `scripts/learner/qa-tuning-analyzer.py` | 新規 | R-12 | ✅ |
| `scripts/learner/staleness-detector.py` | 新規 | R-13 | ✅ |
| `logs/hook-telemetry.jsonl` | 新規 | R-13 | ✅ |
| `references/improve-policy.md` | 修正 | R-11, R-12（入力ソース追加） | ✅ |
| `references/reviewer-capability-scores.md` | 修正 | R-12（スコア更新提案反映） | ✅ |

## Open Questions

1. **Rationalization Scanner の閾値**: minimization 表現の出現回数がいくつ以上で warning とするか？（初期値: 1 回でも warning → データ蓄積後に調整）
2. **reviewer-capability-scores の初期キャリブレーション**: 定性的判断 vs 過去の review-findings.jsonl から統計的に算出するか？（初期は定性的、Phase 3 で統計的キャリブレーション）
3. **Build-QA ループの QA Agent モデル**: Generator と同じモデル（Opus 4.6）を使うか、異なるモデル（Codex）を使うか？（Anthropic は同一モデルで分離、Stripe は決定論的検証を優先）
4. **hook-telemetry.jsonl のローテーション**: ログファイルのサイズ制限・ローテーション方針は？（30 日保持 → 月次アーカイブが妥当か）
5. **QA チューニング提案の適用判断**: 提案は advisory のみか、一定の信頼度を超えたら auto-apply するか？（Rule 10 に従い advisory のみが安全）

## Prompt

以下の仕様に基づいて Trust Verification Architecture (TVA) の Phase 3（自己学習パイプライン）を実装してください。

**前提**: Phase 1+2（R-01〜R-10）は実装済み（commit: fefc275）。R-05 で review-findings.jsonl のデータフォーマット拡張が完了しており、Phase 3 の入力基盤は整っている。

**コンテキスト**: Anthropic Harness Design v2 の核心原則「ハーネスの各コンポーネントはモデルの限界への仮定をエンコードしている。仮定は陳腐化する」に基づき、ハーネス自体が学習・進化する仕組みを構築する。

**核心原則**: 「信頼は検証の関数であり、能力の関数ではない」— モデルがどれほど賢くなっても自己評価を信頼してはいけない。この原則はハーネス自身にも適用される：ハーネスのコンポーネントも定量的に評価し、不要なものは除去する。

**実装対象**: Wave 5（R-11, R-12, R-13）。R-11 → R-12 の依存関係あり。R-13 は R-11 と並列可能だが発火ログ基盤を共有。

**技術方針**:
- 自己学習スクリプトは `scripts/learner/` に配置（既存の `scripts/policy/` と分離）
- 全提案は advisory のみ。自動適用しない（improve-policy Rule 10 準拠）
- 発火ログは `logs/hook-telemetry.jsonl` に蓄積。30 日保持
- 既存の AutoEvolve improve-policy.md の Rule 構造・CQS と整合させる

研究ドキュメント `docs/research/2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md` に TVA 全体の分析が記録されています。
