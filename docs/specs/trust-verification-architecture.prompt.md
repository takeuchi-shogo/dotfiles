---
title: Trust Verification Architecture (TVA)
status: draft
created: 2026-03-27
scope: L
phase_scope: "Phase 1 (Critical) + Phase 2 (High) を実装。Phase 3 は研究記録として保全"
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

## Constraints

- **既存ハーネスとの互換性**: 現行の `/review`、`/autonomous`、completion-gate.py のインターフェースを破壊しない
- **Hook 実装言語**: 新規 hook は Rust（.bin/ 配下のバイナリ）ではなく Python（scripts/policy/）で実装。既存の gaming-detector.py、completion-gate.py と同じパターン
- **パフォーマンス**: hook の実行時間は 1 秒以内。regex パターンマッチのみで LLM 呼び出しなし
- **段階的導入**: 全 hook は advisory（非ブロッキング）で開始。十分なデータ蓄積後にブロッキングへ昇格検討
- **CLAUDE.md への影響最小化**: IFScale 原則に従い、新しい指示は reference に置き、CLAUDE.md からは参照のみ

## Out of Scope

### Phase 3（研究記録として保全。将来の spec で扱う）

以下は研究ドキュメント（`docs/research/2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md`）に完全な分析と統合方針が記録されている:

| ID | ギャップ | テーマ | 将来の方向性 |
|----|---------|--------|-------------|
| G4-1 | ハーネスコンポーネント陳腐化検出 | 自己学習 | Anthropic の「仮定のストレステスト」方法論。モデルリリースごとに各 hook/reference の必要性を re-evaluate |
| G4-2 | QA チューニングフィードバックループ | 自己学習 | review-findings.jsonl → reviewer プロンプト自動改善パイプライン |
| G4-3 | review-findings → AutoEvolve 接続 | 自己学習 | L1 Recovery Tips への自動フィード |
| G1-3 | Blueprint 実運用化 | 品質フロー | /autonomous が blueprint YAML を読み込んで実行 |
| G1-4 | Planner Agent 自動仕様展開 | 品質フロー | 1 文 → 10+ 機能仕様の自動展開（Anthropic v2 の $0.46/4.7min Planner） |
| G5-1 | Scope Up-lifting | 期待超越 | ユーザーが言及していないが価値のある機能を提案する Planner 的役割 |
| G5-2 | Creative Iteration Loop | 期待超越 | 主観的品質の 5-15 回自動反復による creative leap |
| G7-4 | Shared Blind Spot 全合意警告 | 嘘検出 | 全 reviewer が PASS 時に「盲点リスク」を明示警告 |
| G2-4 | Playwright レビュー連携 | レビュー精度 | /review から自動的に Playwright スクリーンショット → 視覚評価 |

**Phase 3 の研究結果は偽りなく保全されている**: 研究ドキュメントに 22 ギャップ全ての分析、統合方針、Anthropic/Stripe の原文引用が記録済み。Phase 1+2 完了後に Phase 3 の spec を別途作成可能。

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
```

### 実装順序（推奨）

```
Wave 1（並列可能）: R-01, R-02, R-03 — hook 2 本 + reference 1 本
Wave 2（Wave 1 完了後）: R-04, R-05 — policy + data format
Wave 3（並列可能）: R-06, R-09 — reference 2 本
Wave 4（Wave 3 完了後）: R-07, R-08, R-10 — /autonomous 統合 + DoD + framing
```

### 変更対象ファイル（予定）

| ファイル | 操作 | 関連 Requirement |
|---------|------|-----------------|
| `scripts/policy/rationalization-scanner.py` | 新規 | R-01 |
| `scripts/policy/derivation-honesty-hook.py` | 新規 | R-03 |
| `references/reviewer-capability-scores.md` | 新規 | R-02 |
| `references/trust-verification-policy.md` | 新規 | R-04 |
| `references/adversarial-evaluation-criteria.md` | 新規 | R-06 |
| `references/definition-of-done-template.md` | 新規 | R-08 |
| `references/context-compaction-policy.md` | 新規 | R-09 |
| `scripts/policy/completion-gate.py` | 修正 | R-04, R-05, R-08 |
| `skills/review/SKILL.md` | 修正 | R-04, R-10 |
| `skills/autonomous/SKILL.md` | 修正 | R-07 |
| `settings.json` | 修正 | R-01, R-03（hook 登録） |
| `references/review-consensus-policy.md` | 修正 | R-02（scores 参照追加） |

## Open Questions

1. **Rationalization Scanner の閾値**: minimization 表現の出現回数がいくつ以上で warning とするか？（初期値: 1 回でも warning → データ蓄積後に調整）
2. **reviewer-capability-scores の初期キャリブレーション**: 定性的判断 vs 過去の review-findings.jsonl から統計的に算出するか？（初期は定性的、Phase 3 で統計的キャリブレーション）
3. **Build-QA ループの QA Agent モデル**: Generator と同じモデル（Opus 4.6）を使うか、異なるモデル（Codex）を使うか？（Anthropic は同一モデルで分離、Stripe は決定論的検証を優先）

## Prompt

以下の仕様に基づいて Trust Verification Architecture (TVA) を実装してください。

**コンテキスト**: Anthropic Harness Design v2、Stripe Minions Part 2、Opus 4.6 の知見を統合し、現行 dotfiles ハーネスの「嘘検出」「レビュー精度」「自律行動」の 3 つの構造的欠陥を解消します。

**核心原則**: 「信頼は検証の関数であり、能力の関数ではない」— モデルがどれほど賢くなっても自己評価を信頼してはいけない。決定論的検証（テスト、lint）を Layer 0 として最優先し、LLM 判断は Layer 1-2 として補完的に使用する。

**実装順序**: Wave 1 → Wave 4 の依存関係に従い、各 Wave 内は並列実装可能。全 hook は advisory（非ブロッキング）で開始。

**技術方針（ハイブリッド）**: 明確なパターン（banned phrases, minimization 表現）は hook で自動検出。判断が必要なもの（品質採点、文脈分析）は agent に委ねる。

**Phase 3 への橋渡し**: R-05 で review-findings.jsonl のデータフォーマットを拡張し、将来の AutoEvolve 接続 + QA チューニングフィードバックループの基盤を準備する。

研究ドキュメント `docs/research/2026-03-27-harness-v2-adversarial-honesty-deep-analysis.md` に Phase 3 の完全な分析が記録されています。Phase 1+2 完了後に参照してください。
