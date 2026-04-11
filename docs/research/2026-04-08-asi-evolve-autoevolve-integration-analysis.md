---
source: "ASI-Evolve: AI Accelerates AI (arXiv:2603.29640)"
date: 2026-04-08
status: analyzed
---

## Source Summary

**主張**: AIがAI自身の研究開発を自動化する統合フレームワーク。閉ループ「学習→設計→実験→分析」サイクルで、モデルアーキテクチャ設計・データキュレーション・強化学習アルゴリズム設計において人間SOTAを大幅に超える成果を達成。

**手法**:
- 閉ループ進化サイクル (LDEA: Learn→Design→Experiment→Analyze)
- 認識基盤 (Cognition Store): 学術文献のエンベディング索引で cold start 回避
- 分析器 (Analyzer): 多次元実験結果を意思決定指向レポートに圧縮
- UCB1 サンプリング: 探索/活用バランスで収束速度最適化
- 動機追跡付きデータベース: 候補の動機・結果・分析を永続記録
- 多段階評価: 小規模→大規模の段階的検証で計算効率確保
- 静的検証 + デバッグエージェント: 実行前検証で無駄な計算削減
- ドメイン固有戦略生成: タスク特性に応じた探索戦略の自動適応

**根拠**:
- 線形注意アーキテクチャ設計: 人間SOTA (Mamba2 +0.34pt) の約3倍 (+0.97pt)
- データキュレーション: 3Bモデルで +3.96pt、MMLU +18.64pt
- 強化学習: GRPO超の10アルゴリズム自動発見
- 円パッキング: 17ステップでSOTA (OpenEvolve: 460ラウンド)
- アブレーション: 分析器なし→長期停滞、認識基盤なし→cold startコスト増大

**前提条件**: 大規模計算リソース、高品質な初期文献コーパス、長期実行可能な実験環境

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 閉ループ進化サイクル | Already | AutoEvolve: Analyze→Improve→Garden→Feedback。backlog/winning-direction/proposal-pool で次ランへ注入 |
| 2 | 認識基盤 (Cognition Store) | Already | context-constitution.md + wiki/research/references。ただし CC は統治原則であり知識検索基盤ではない（Codex指摘） |
| 3 | 分析器 (Analyzer) | Already | meta-analyzer + Coverage Matrix + evidence_chain。batch分析中心で即時蒸留が弱い（Codex指摘） |
| 4 | 多段階評価 | Already | S/M/L ワークフロー + structured-test-time-scaling。ただし「昇格基準の厳格化」が未翻訳（Codex指摘） |
| 5 | UCB1 サンプリング | Partial | wiki/meta-evolution.md に概念記載。Ideation-Debate にバンディットスコアリング未実装 |
| 6 | 動機追跡DB | Already | proposals.jsonl (motivation/outcome/outcome_delta)。lineage追跡なし、analysis_snippet null放置（Codex指摘） |
| 7 | 静的検証+デバッグ | Already | change-surface-preflight.md + debugger/codex-debugger agents |
| 8 | ドメイン固有戦略 | Already | task-archetypes/ (auth, db-migration, error-handling, external-api, validation) |
| 9 | アブレーション検証 | Already | A/B gate in autoevolve + skill-benchmarks |
| 10 | AI-for-AI | Already | /improve + autoevolve-core + self-referential improvement |
| 11 | proposal-level 重複排除 | Gap | AP-1 はスキル重複のみ。提案レベルの novelty check なし（Codex追加） |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | AutoEvolve Phase 1.0（前回ラン状態注入） | Learn フェーズ不在ではなく retrieval 品質不足。単発 ingest ではなく毎ラウンドの retrieval が肝 | Phase 1.0 に knowledge retrieval サブフェーズ追加。docs/research/ + docs/wiki/concepts/ から関連知見を注入 | 強化可能 |
| S2 | wiki/research/references (ファイルベース) | CC は統治原則であり知識検索基盤ではない。検索可能な知識インデックスが不在 | knowledge-index.yaml による軽量 retrieval 導入。毎ラウンドで top-3 concept を注入。embedding は後回し | 強化可能 |
| S3 | meta-analyzer (batch分析) | batch 寄りで提案単位の即時蒸留が弱い。merge/revert 後に analysis_snippet が null 放置 | merge/revert 後 hook で micro-analyzer を実行し analysis_snippet を即時充填 | 強化可能 |
| S4 | S/M/L ワークフロー | 論文の多段階はサイズ違いではなく「昇格基準の厳格化」。synthetic eval → holdout → live の翻訳が不足 | 3段ゲート評価: quick synthetic check → targeted holdout → delayed real-use outcome | 強化可能 |
| S5 | proposals.jsonl (motivation/outcome) | DB の本質は保存ではなく parent selection + novelty check + lineage。系譜を辿れない | parent_id, novelty_score, similar_proposal_ids, mutation_type 追加 + outcome backfill 自動化 | 強化可能 |
| S6 | preflight + debugger agents | — | 十分にカバー | 強化不要 |
| S7 | task-archetypes/ (5ドメイン) | — | 十分にカバー | 強化不要 |
| S8 | A/B gate in autoevolve | — | 十分にカバー | 強化不要 |
| S9 | /improve + self-referential improvement | — | 十分にカバー | 強化不要 |

## Phase 2.5: Refine (Codex + Gemini)

### Codex 批評の要点
- Context Constitution ≠ Cognition Store（統治原則 vs 知識検索基盤）
- Database の本質は lineage（parent_id, novelty_score, mutation_type が不在）
- Analyzer に micro-analyzer（即時蒸留）が必要
- 多段階評価は S/M/L ではなく「synthetic → holdout → live」に翻訳すべき
- UCB1 はデータ整備後（P4 に下げるべき）
- proposal-level dedup が新規 Gap

### Gemini 周辺知識の要点
- UCB1 効果は ~10%。サンプル効率の 90% は Cognition Store が説明
- 小規模候補プール（数十件）では UCB1 ≈ Thompson Sampling
- 文献バイアスリスク: 狭い領域で古い手法が過剰注入される → 時間減衰が必要
- File-backed (YAML/JSONL) で十分。Build to Delete に合致
- FunSearch (LLM提案+replay) と OpenEvolve (ロバスト性) のハイブリッドが低リスク

### 修正内容
- #2 (Cognition Store): 強化不要 → 強化可能（Codex: CC≠Cognition Store）
- #3 (Analyzer): 強化不要 → 強化可能（Codex: 即時蒸留が弱い）
- #4 (多段階評価): 強化不要 → 強化可能（Codex: S/M/L≠多段階評価）
- #11 (proposal-level dedup): 新規 Gap 追加（Codex）
- #5 (UCB1): 優先度を P4 に下げ（Codex + Gemini 一致）

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 5 | UCB1 サンプリング | 採用 (P4) | データ整備後に導入。30-50件の outcome データ蓄積が前提 |
| 11 | proposal-level 重複排除 | 採用 (P1) | BM25/trigram で similarity > 0.85 を pre-debate filter |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | Phase 1.0 knowledge retrieval | 採用 (P2) | retrieval 品質不足を解消 |
| S2 | knowledge-index.yaml 軽量 retrieval | 採用 (P2) | S1 と統合して実装 |
| S3 | micro-analyzer + analysis_snippet backfill | 採用 (P0) | Analyzer+DB 閉ループの基盤 |
| S4 | 3段ゲート評価 | 採用 (P3) | multi-stage eval をハーネス文脈に翻訳 |
| S5 | proposals.jsonl lineage 拡張 | 採用 (P0) | DB 閉ループの基盤 |

## Plan

### Wave 1 (P0): Analyzer + Database 閉ループ完結

#### Task 1: proposals.jsonl schema 拡張
- **Files**: `.config/claude/agents/autoevolve-core.md`
- **Changes**: proposals.jsonl スキーマに `parent_id`, `novelty_score`, `similar_proposal_ids`, `mutation_type` フィールド追加。Phase 2 の提案生成時に親提案の ID を記録し、既存提案との類似度を計算
- **Size**: S

#### Task 2: micro-analyzer hook + analysis_snippet 自動 backfill
- **Files**: `.config/claude/agents/autoevolve-core.md`, `.config/claude/agents/meta-analyzer.md`（参照のみ）
- **Changes**: Phase 4 (Feedback Loop) に merge/revert 後の micro-analysis ステップを追加。proposal_id を特定し、outcome/outcome_delta/analysis_snippet を自動更新する手順を定義
- **Size**: S-M

### Wave 2 (P1): Researcher 探索品質

#### Task 3: proposal-level 重複排除
- **Files**: `.config/claude/agents/autoevolve-core.md`
- **Changes**: Phase 2.0 (Ideation-Debate) の候補生成前に、motivation + tags に対する BM25/trigram 類似度チェックを追加。similarity > 0.85 の提案を弾く pre-debate filter。AP-5 として Anti-Patterns に追加
- **Size**: S

### Wave 3 (P2): Knowledge Retrieval

#### Task 4: knowledge-index.yaml + Phase 1.0 knowledge retrieval
- **Files**: `.config/claude/agents/autoevolve-core.md`, `knowledge-index.yaml`（新規、agent-memory/ 配下）
- **Changes**: Phase 1.0 に Knowledge Ingestion サブフェーズ追加。docs/research/ + docs/wiki/concepts/ のインデックス（YAML）を作成し、各ラウンドで改善対象カテゴリに関連する top-3 concept を注入。時間減衰メカニズム付き（Gemini指摘の文献バイアス対策）
- **Size**: M
- **Dependencies**: Task 1（proposals.jsonl に tags があること）

### Wave 4 (P3): Engineer 評価昇格

#### Task 5: 3段ゲート評価
- **Files**: `.config/claude/agents/autoevolve-core.md`, `.config/claude/references/improve-policy.md`
- **Changes**: 現在の A/B gate を3段階に拡張: (1) Quick synthetic check — 修正直後の構文・整合性検証, (2) Targeted holdout — 次の3セッションでの対象スキル実行スコア, (3) Delayed real-use outcome — 10セッション後の outcome_delta 計測。improve-policy に昇格基準を追加
- **Size**: M
- **Dependencies**: Task 2（outcome backfill が機能していること）

### Wave 5 (P4): UCB1 サンプリング

#### Task 6: UCB1 導入
- **Files**: `.config/claude/agents/autoevolve-core.md`
- **Changes**: Phase 2.0 の proposal-pool サンプリングに UCB1 スコアリング追加。カテゴリ別 reward 正規化 + pending 解消率を前提条件とする。Go/No-Go: merged/reverted/declined が 30件以上蓄積していること
- **Size**: M
- **Dependencies**: Task 1, 2, 3（データ整備が完了していること）
- **Go/No-Go criteria**: proposals.jsonl に outcome が filled の提案が 30件以上

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| proposals.jsonl schema 変更で既存データとの互換性問題 | 中 | 新フィールドは optional（null 許容）。既存データは migration 不要 |
| micro-analyzer の実行コスト増 | 低 | merge/revert 時のみ実行。1提案あたりの分析は軽量 |
| knowledge-index の文献バイアス | 中 | 時間減衰（30日で重み半減）+ カテゴリ多様性制約 |
| 3段ゲートの待ち時間（10セッション） | 低 | Delayed outcome は非同期。即時判断は synthetic + holdout で完結 |
| UCB1 の誤学習（データ不足時） | 高 | Go/No-Go criteria（30件以上）を厳守。不足時は既存 ROI 判定を維持 |

## Execution

L 規模のため `docs/plans/` にプラン保存 → Wave ごとに新セッションで `/rpi` 実行を推奨。
Wave 1-2 は同一セッションで実行可能。Wave 3-5 は前 Wave の効果確認後に実行。
