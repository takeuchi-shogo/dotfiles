---
status: reference
last_reviewed: 2026-05-14
---

# Decision Tables Index

dotfiles 内に散在する決定表 (decision tables) を 1 ページから一覧できる索引。
「どの表を見れば、この判断が決められるか」を最短経路で解決する。

## Routing 系（どのモデル / skill / agent を選ぶか）

| 決定 | 表の場所 | 概要 |
|---|---|---|
| モデル選択 (Claude / Codex / Gemini) | [`references/model-routing.md`](model-routing.md) | タスク特性別の推奨モデル |
| cwd-aware skill 起動 | [`references/cwd-routing-matrix.md`](cwd-routing-matrix.md) | 作業ディレクトリごとの skill 自動発火 |
| 委譲 vs メイン実行 | [`references/subagent-delegation-guide.md`](subagent-delegation-guide.md) | subagent へ逃がす閾値 |
| **Advisor 相談 (escalation)** | [`references/advisor-strategy.md`](advisor-strategy.md) | Executor 主導の困難判断相談（後述「Drive 主体逆転」も参照） |
| Worker (cmux) 使い分け | [`references/subagent-vs-cmux-worker.md`](subagent-vs-cmux-worker.md) | 長時間 / 並列 / マルチモデル |

### Drive 主体逆転（Top-Down 委譲 vs Bottom-Up Escalation）

同じ「複数モデルを使う」状況でも、**判断の起点（drive 主体）** によって採用パターンが分かれる。両者を混同すると「Opus が毎回 advisor を呼ぶだけの self-preference amplifier」になるので、**起点の方向で選び分ける**:

| Drive 主体 | パターン | 表 | 典型シナリオ |
|---|---|---|---|
| **Top-Down (Opus 主導の委譲)** | Opus が判断・計画・統合し、Sonnet/Haiku/Codex/Gemini に scoped task を委譲 | [`model-routing.md`](model-routing.md) + [`subagent-delegation-guide.md`](subagent-delegation-guide.md) | 探索・実装・レビューの分業、長時間タスク |
| **Bottom-Up (Executor 主導の escalation)** | Sonnet/Haiku Executor が困難判断時のみ Opus advisor に相談 | [`advisor-strategy.md`](advisor-strategy.md) | アーキテクチャ判断・セキュリティ未確実領域の単発相談 |

> 出典: "Distribution vs Escalation: When to Use Subagents or Advisors" (2026-05-02) absorb / `docs/research/2026-05-04-distribution-vs-escalation-absorb-analysis.md`

## Workflow 系（どの流れで進めるか）

| 決定 | 表の場所 | 概要 |
|---|---|---|
| タスク規模 S/M/L | `.config/claude/CLAUDE.md` の「ワークフロー」表 | 各規模の必須段階 |
| /rpi vs /spike | `.config/claude/skills/*/SKILL.md` description 群 | 仕様確定度 × 規模 |
| 深度レベル (Minimal/Standard/Comprehensive) | [`references/workflow-guide.md`](workflow-guide.md) | 調査深度の判定 |
| stage transition | [`references/stage-transition-rules.md`](stage-transition-rules.md) | 各 phase の完了条件 |

## Impact 系（何と併せて見るか）

| 決定 | 表の場所 | 概要 |
|---|---|---|
| 変更面ごとの併見ファイル | [`references/change-surface-matrix.md`](change-surface-matrix.md) | change × validation |
| 変更面の preflight | [`references/change-surface-preflight.md`](change-surface-preflight.md) | 変更前の事前確認 |
| エラー → 修正マップ | [`references/error-fix-guides.md`](error-fix-guides.md) | 既知 error pattern |
| 出力フォーマット (markdown / HTML / Mermaid / playground / excalidraw) | [`references/output-format-decision-table.md`](output-format-decision-table.md) | 「どのフォーマットで作るべきか」 |

## Mechanism 系（instruction vs mechanism）

| 決定 | 表の場所 | 概要 |
|---|---|---|
| hook vs instruction 境界 | [`docs/reports/determinism-boundary-analysis.md`](../../../docs/reports/determinism-boundary-analysis.md) | 決定論でやる vs プロンプトでやる |
| Skills vs Hooks vs Subagents | [`references/skill-invocation-patterns.md`](skill-invocation-patterns.md) | 使い分け原則 |
| linter config protection | ADR-0004 (`docs/adr/0004-linter-config-protection.md`) | .eslintrc/.biome 等は保護対象 |
| Routine prompt 6 要素 | [`references/routine-prompt-rubric.md`](routine-prompt-rubric.md) | role/task/process/output/error/constraints + Pre-flight Checklist |
| trellis 4 象限 → mechanism | (本表に内蔵) | ambient=hook 自動 / control surface=Gate / human-led=`/think` `/decision` / nobody cares=silent skip |

## Classification / Hierarchy 系

| 決定 | 表の場所 | 概要 |
|---|---|---|
| Memory type (user/feedback/project/reference) | `~/.claude/CLAUDE.md` auto memory セクション | どのタイプで保存するか |
| Knowledge Pyramid L0-L4 | [`references/knowledge-pyramid.md`](knowledge-pyramid.md) | 学習データの蒸留階層 |
| Doc status (active/reference/archive) | [`references/doc-status-schema.md`](doc-status-schema.md) | ドキュメント frontmatter |
| Governance Level (0-3) | [`references/governance-levels.md`](governance-levels.md) | 自律性レベル |

## Evaluation / Gate 系

| 決定 | 表の場所 | 概要 |
|---|---|---|
| Skill 改善の keep / discard | [`references/improve-policy.md`](improve-policy.md) §評価指標 | +/-/neutral の閾値 |
| Review dimensions | [`references/review-dimensions.md`](review-dimensions.md) | Codex / code-reviewer の 7 観点 |
| Pre-mortem checklist | [`references/pre-mortem-checklist.md`](pre-mortem-checklist.md) | 失敗モード列挙 |
| Reversible decisions | [`references/reversible-decisions.md`](reversible-decisions.md) | 撤退条件の明文化 |
| MCP plugin 導入時の audit checklist | `scripts/policy/mcp-audit.py` 上部コメント | plugin+standalone 重複登録による prefix collision 確認 (SocratiCode absorb 由来) |

## 運用

- **新規追加**: 新しい decision table を作ったら本索引に 1 行追記
- **陳腐化**: 索引に列挙している table のうち dead-weight-scan で flagged されたものは再検討
- **階層**: 索引 > 個別表 > 本文 の三層。本索引は階層の入口
- **関連**: `_index.md` (過去に何を取り込んだか) とは別目的。ここは「何を決定できるか」
