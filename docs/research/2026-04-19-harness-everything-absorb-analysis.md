---
source: "Harnesses are everything. Here's how to optimize yours." (Baseten blog)
date: 2026-04-19
status: integrated
---

# Harnesses Are Everything — Absorb 分析レポート

- **取り込み日**: 2026-04-19
- **ソース**: 外部記事「Harnesses are everything. Here's how to optimize yours.」(Baseten blog 想定)
- **分析フロー**: /absorb Phase 1-4

## 1. 記事の主張

**主張**: LLM の品質差異は「モデル選択」よりも「ハーネス設計」に依存する（協調プロトコル選択が44%、モデル選択は~14%）。System prompt を lean .md files で構成し、R.P.I (Research → Plan → Implement) フレームワークで順序付け、subagents で並列実行することで品質が大幅に向上する。

**手法**:
- lean .md files: system prompt を薄く保ち、参照ファイルで詳細を分離する
- R.P.I framework: Research → Plan → Implement の順序強制
- Subagents: 並列 fan-out と sequential pipelines の使い分け
- Instruction budget: 常時露出する指示の総量を意識的に管理する
- Dumb zone 回避: 指示過多による判断能力の低下を防ぐ
- Progressive disclosure: CLI → Skills → MCP の段階的発見
- Harness commit: ハーネスを安易に切り替えない安定性の確保

**根拠**: 協調プロトコル選択が品質差異の44%を説明、モデル選択は~14%

**前提条件**: 中〜大規模のエージェント活用環境、複数モデル・ツールを組み合わせる場合

## 2. ギャップ分析 (Phase 2)

### Gap / Partial / N/A テーブル

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | lean .md files (system prompt 分離) | Already | CLAUDE.md → references/ → rules/ の Progressive Disclosure 設計済み |
| 2 | Human-written 明示方針 | Partial | system-prompt-policy.md が未整備。人間が書いた部分と自動生成部分の区別が明示されていない |
| 3 | CLI progressive disclosure | Partial | `--help` ファーストの方針が CLAUDE.md に明記されていない |
| 4 | R.P.I framework | Already | `/spec`→`/spike`→`/validate`→`/epd` + `/rpi` スキル実装済み |
| 5 | Subagents 並列 fan-out | Already | dispatch/Agent 委譲パターン実装済み。ただし効果測定は未整備 |
| 6 | Instruction budget 管理 | Partial | token-audit.py はあるが「常時露出総量」の計測が未整備（本文行数のみ） |
| 7 | reviewer calibration | Gap | レビューアーの判断精度（TPR/TNR）を追跡するメトリクスが未存在 |
| 8 | Dumb zone 回避 | Already | IFScale + CLAUDE.md 圧縮ポリシーで対処済み |
| 9 | Harness commit (安定性) | Partial | AutoEvolve に安全機構はあるが「30日評価なしに捨てない」の明文化がない |
| A | 総量 instruction budget 指標 | Gap | description + hook注入 + MCP tool定義 を含む真の総量計測スクリプト未存在 |
| B | dead-weight scan | Gap | references/skills/agents の増殖チェック（使われていないファイル検出）が未実装 |

### Already 項目の強化分析テーブル

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| MCP 選別 | enableAllProjectMcpServers=false + connector-inventory | 記事は選別の重要性を強調するが既に制御済み | 追加対応不要 | 強化不要 |
| 並列 fan-out | dispatch/Agent 委譲パターン | 「ある」が「効いている」証拠が薄い | reviewer calibration で測定 | 強化可能 |

## 3. セカンドオピニオン (Phase 2.5)

### Codex 批評（要約）

- **見落とし**: instruction budget は本文行数でなく「常時露出+description+hook注入+MCP tool定義」の総量で測るべき → Gap A として新規追加
- **過大評価**: MCP 選別は enableAllProjectMcpServers=false + connector-inventory で既に制御済み → Partial → Already (強化不要) に格下げ
- **過小評価**: 並列 fan-out は「ある」が「効いている」証拠が薄い → reviewer calibration による測定が必要
- **前提誤り**: 個人 dotfiles で「切り替えない」を強くしすぎると実験速度を殺す → 「30日評価なしに捨てない」に弱める
- **優先度**: (1) references/skills/agents 増殖 dead-weight scan (2) connector-inventory drift 解消 (3) reviewer calibration

### Gemini 周辺知識

- **Active Harness トレンド**: HumanLayer の人間承認フロー埋込による制御点の明示化
- **Stanford Lost in the Middle**: 2000トークン超で指示遵守率 20-30% 低下 → instruction budget 管理の重要性を裏付け
- **R.P.I 限界**: Plan Drift（計画と実装の乖離）/ Over-computation（過剰な Research フェーズ）
- **Subagent failure パターン**: Parallel=断片化リスク、Sequential=エラー増幅リスク
- **State-Graph (LangGraph) への移行**: 動的ルート変更が可能だが dotfiles 規模では過剰

### 修正反映

1. MCP 選別: Partial → Already (強化不要)
2. 並列 fan-out: Already 強化不要 → Already 強化可能 (reviewer calibration)
3. 新規 Gap A: 総量 instruction budget 指標（description + hook注入 + MCP tool定義 含む）
4. Harness Commit: 「切り替えない」→「30日評価なしに捨てない」に弱める

## 4. 選別結果 (Phase 3)

ユーザー選択: 6 項目全部採択 (A, B, 9, 2, 3, 7)

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | 総量 instruction budget 計測 | 採用 | Stanford 研究が裏付け。真の露出量が不明な状態は盲点 |
| B | dead-weight scan | 採用 | 増殖ファイルは instruction budget を消費する。AutoEvolve との統合で自動化可能 |
| 9 | Harness Commit 弱めた版明文化 | 採用 | 「30日評価なしに捨てない」として実験速度を殺さずに安定性を確保 |
| 2 | Human-written 明示方針 | 採用 | 自動生成部分との区別がない状態は品質保証の盲点 |
| 3 | CLI progressive disclosure 明記 | 採用 | `--help` ファーストは既存ポリシーと整合、1行追記で完了 |
| 7 | reviewer calibration メトリクス | 採用 | TPR/TNR 未測定のままでは「レビューが効いているか」不明 |

却下:
- adversary pipeline stage: reviewer calibration 測定後に判断
- LangGraph/State-Graph 移行: dotfiles 規模では過剰

## 5. 統合プラン (Phase 4)

| # | タスク | 規模 | 依存 | 成果物 |
|---|--------|------|------|--------|
| Q1 | Task 9: Harness Commit 弱めた版明文化 | S | - | references/harness-stability.md + CLAUDE.md 条件付きブロック |
| Q2 | Task 2: Human-written 明示方針 追記 | S | - | references/system-prompt-policy.md |
| Q3 | Task 3: CLI progressive disclosure 追記 | S | - | CLAUDE.md に1行 + references/cli-discovery.md |
| M1 | Task A: 総量 instruction budget 計測スクリプト | M | - | scripts/policy/measure-instruction-budget.py + golden-check 拡張 |
| M2 | Task B: dead-weight scan 実測タスク化 | M | - | scripts/lifecycle/dead-weight-scan.py + AutoEvolve Phase 1 統合 |
| L1 | Task 7: reviewer calibration メトリクス | L | M2 | scripts/learner/reviewer-calibration.py + メトリクス JSONL |

実行順: Wave 1 (Q1→Q3) → Wave 2 (M1+M2 並列) → Wave 3 (L1)

## 6. 却下・保留事項

- **adversary pipeline stage 追加**: reviewer calibration 測定後に判断 (Codex 提案)
- **LangGraph/State-Graph 移行**: dotfiles の規模では過剰 (Gemini 紹介)

## 7. 統合プラン

詳細: docs/plans/active/2026-04-19-harness-everything-absorb-plan.md
