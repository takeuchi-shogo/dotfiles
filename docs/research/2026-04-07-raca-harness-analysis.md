# RACA: Research Assistant Coding Agent — ハーネス統合分析

- **ソース**: ブログ記事 "RACA: Research Assistant Coding Agent for Ph.D. Students"
- **日付**: 2026-04-07
- **関連プラン**: docs/plans/2026-04-07-raca-integration.md

---

## Phase 1: 構造化抽出

### 主張

Claude Code のハーネスを活用して研究ワークフロー（実験設計→Slurm実行→監視→結果可視化）を自動化。核心的主張は「Knowledge over Code」— バグの根本修正はコードではなくリファレンスドキュメント。LLM が毎回実装を生成できるため、重要なのは「何をすべきか」の知識文書化。Karpathy の LLM Knowledge Base 提案と同方向。

### 手法（10項目）

1. Research Dashboard (HuggingFace Spaces) — 実験・成果物・WandBログ集約
2. Canary Job — 本番前の軽量 e2e テスト
3. Red-teaming — 失敗パターン・不変条件の自動分析
4. Dataset Skills — タスク理解のリファレンスドキュメント化
5. Knowledge over Code — バグ修正→ドキュメント更新
6. Single Workspace — 全プロジェクト集約
7. Rules as Pipeline — .claude/rules/ でパイプラインエンコード
8. Remote Execution (HPC/Slurm/SSH)
9. Agent-Deck + Conductor — マルチセッションオーケストレーション
10. Reward Hacking Detection — 報酬関数の脆弱性検出

### 根拠

- Multiplex Thinking 論文の Figure 6 再現実験（研究計画自動化で成功）
- Countdown タスクの reward hacking バグ発見（\boxed{} bypass）
- Canary job での calibration issue 検出
- 3x の並列研究スレッド管理

### 前提条件

- PhD 研究開発ワークフロー（実験ドリブン）
- HPC クラスタアクセス
- タスク仕様を plain English で厳密に記述可能
- Single author（チームスケールでは breakdown の可能性）

---

## Phase 2 + 2.5: 修正済みギャップ分析

### Gap / Partial / N/A

| # | 手法（リフレーム後） | 判定 | 現状 |
|---|---------------------|------|------|
| 1 | Observability Dashboard（実行・失敗・再試行の観測可能性） | Partial | dispatch_logger, cmux result collection, AutoEvolve 学習ループあり。信号→意思決定の接続が不明確 |
| 2 | Canary Job（変更面に応じた軽量 preflight） | Partial | smoke test ルール + /validate + completion-gate.py あり。変更面ベースの自動 preflight 差し込みなし |
| 3 | Red-teaming 自動起動 | Partial | edge-case-hunter + silent-failure-hunter + /edge-case-analysis あり。高リスク変更での自動起動トリガーなし |
| 4 | Backend Task Archetype Templates | Partial | taxonomy + wiki index + tacit-knowledge pipeline あり。反復領域の canonical schema 未定義 |
| 6 | Single Workspace | N/A | SW開発では repo-local correctness + worktree isolation が優先。現行構造は安全装置 |
| 8 | Remote Execution / HPC | N/A | 用途外 |

### Already（強化分析）

| # | 既存の仕組み | 強化ポイント | 強化案 |
|---|------------|-------------|--------|
| 5 | AutoEvolve + session-learner + continuous-learning + compile-wiki | 失敗時の repair routing が未定義 | repair routing table を references/ に追加 |
| 7 | Progressive Disclosure + EPD + completion-gate.py + golden-check.py | ステージ遷移の end-to-end 機械的結線が不完全 | stage transition rules を明文化 |
| 9 | cmux + dispatch + subagent | stage-aware routing / validate・red-team 自動差し込み / subagent 間裁定 | conductor-level 統合 |
| 10 | gaming-detector.py + memory-safety-policy §4 + CALM | specification gaming 検出範囲が限定的 | gaming-detector の検出パターン拡張 |

### Phase 2.5 での判定変更

- Codex 指摘: #5, #7, #10 を Partial → Already (強化可能) に変更。既存実装の深さを過小評価していた
- Codex 指摘: #9 を Already (強化不要) → Already (強化可能) に変更。基盤は強いが conductor-level 統合が未達
- Codex 指摘: #4 を "Dataset Skills" → "Backend Task Archetype Templates" にリフレーム
- Codex 指摘: #5 を "Knowledge over Code" → "Knowledge with Code" に再解釈（プロダクション開発では code が本体）
- Gemini 補完: Knowledge over Code の最大リスクは Documentation Drift。Industry では "Specification as Tests" が主流

---

## Phase 3: 選択結果

全項目取り込み。

---

## Phase 4: タスクリスト

### Wave 1（高優先度・並列可能）

- T1: Canary Job — 変更面ベース自動 preflight [M]
- T2: Red-teaming 自動起動 [M]
- T3: Repair Routing Table [S]

### Wave 2（中優先度）

- T4: Backend Task Archetype Templates [M]
- T5: Stage Transition 結線 [M]
- T6: Observability Dashboard [M]

### Wave 3（低優先度）

- T7: Conductor 統合 [M]
- T8: gaming-detector 拡張 [S]

詳細: docs/plans/2026-04-07-raca-integration.md
