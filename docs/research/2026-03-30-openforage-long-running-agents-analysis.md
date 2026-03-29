---
source: "How To Solve Problems Of Long Running, Autonomous Agentic Engineering Workflows (OpenForage)"
date: 2026-03-30
status: integrated
---

## Source Summary

**主張**: 長時間自律エージェントの失敗は「怠慢（corner-cutting）」と「混乱（stupidity）」の2つに集約される。ネイティブツール（Claude Code, Codex）だけでは不十分で、独自オーケストレーション層が必要。

**手法**（7つの失敗パターン + 3つの構造的対策）:

1. **Pre-Task 矛盾チェック**: 着手前に不完全・矛盾情報を体系的にチェック。伝播防止
2. **Planning 全ファイル網羅**: 計画前に関連ファイルを全網羅、リポジトリに矛盾情報がないことを保証
3. **N個プラン生成 → 別エージェント選択**: N=5 プランを生成し、保守性・クリーンコード基準で別エージェントが選択
4. **スマートセッションハンドオフ**: リポジトリ構造理解に基づくカスタムコンパクション、context fidelity の最大化
5. **早期・頻繁な計画逸脱検証**: 計画通りに実装されているか早期に検証、カスケード障害（A→A'問題）防止
6. **複雑タスクの極限分解**: 100行以下の小タスクに分解し500個連結、activation energy をゼロに
7. **専用エージェントによる fresh context 検証**: 検証計画を立てる専用エージェント、本番同等の動作確認
8. **セッション後 blast radius クリーンアップ**: fresh context エージェントで矛盾解消・デッドコード除去・ドキュメント同期
9. **独立オーケストレーション層**: タスクの外にアルゴリズム契約と独立検証エージェント
10. **ハーネステレメトリ + rubric 評価**: プロンプト・トレース・結果の収集と rubric ベース品質判定

**根拠**: 著者の長年のエージェント実務経験。RL による複雑性忌避、エージェント心理学は人間と同型（productivity coaching の手法が有効）。

**前提条件**: 長時間（マルチセッション）自律エージェント運用。バニラセットアップでは不十分な複雑さ。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 3 | N個プラン生成 → 別エージェント選択 | **Gap** | `/debate` はあるが Plan フェーズへの自動組み込みなし |
| 8 | セッション後 blast radius クリーンアップ | **Partial** | `doc-gardener`, `cross-file-reviewer`, `/refactor-session` は手動起動のみ |
| 10 | ハーネステレメトリ + rubric 評価 | **Partial** | `session_events.py` でデータ収集はあるが rubric ベース品質評価なし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|---|---|---|
| 1 | `/check-health` + `contradiction-mapping.md` | 矛盾情報はタスク着手前に検出しないと伝播する。現状 advisory のみ | `workflow-guide.md` の Plan フェーズで M/L タスクに check-health 必須化を追記 |
| 4 | `session-protocol.md` + `HANDOFF.md` + `context-compaction-policy.md` | 自前コンパクションが provider より優れる | **強化不要** — `pre-compact-save.js` + `HANDOFF.md` テンプレート + Fallback トリガーで十分カバー |
| 5 | `plan-lifecycle.py` + `golden-check.py` | early and often で検証しないとカスケード障害（A→A'問題） | `workflow-guide.md` に中間検証ポイント（L タスクで 3 ステップ完了ごとに計画突合）を追記 |
| 6 | `/autonomous` + S/M/L 分類 | 100行以下に分解、activation energy をゼロに | `/autonomous` のタスク分解ガイドラインに上限追記 |
| 7 | `verification-before-completion` + subagent reviewers | 本番同等の動作確認 | **強化不要** — subagent + `/webapp-testing` + Playwright MCP でカバー |
| 9 | hooks 4層 + `completion-gate.py` | アルゴリズム契約 + 独立検証 | **強化不要** — ハーネス自体がこのアーキテクチャ |
| 2 | 「探索は広く、理解は深く」原則 | 計画前に関連ファイル全網羅 | **強化不要** — 原則として明示済み |

## Integration Decisions

全6項目を取り込み:

1. [Gap] N個プラン生成 → 別エージェント選択 — `workflow-guide.md` に L タスクの Plan フェーズで複数プラン生成の手順追記
2. [Partial] セッション後 blast radius クリーンアップ — `session-protocol.md` に自動推奨ルール追記
3. [Partial] ハーネステレメトリ rubric — 将来タスクとして記録（現時点は `improve-policy.md` の session metrics で代替）
4. [強化] check-health を M/L の Plan で必須化 — `workflow-guide.md` 追記
5. [強化] 中間検証ポイント — `workflow-guide.md` 追記
6. [強化] /autonomous のタスク分解に 100行ガイドライン — `autonomous/SKILL.md` 追記

## Plan

### Task 1: workflow-guide.md に3つの強化を統合 (S)

**ファイル**: `.config/claude/references/workflow-guide.md`

変更内容:
- Plan フェーズに「M/L タスクでは `/check-health` を Plan 前に実行すること」を追記
- L タスクに「複数プラン生成」オプションを追記（N=3 プラン → 保守性・拡張性・シンプルさで選択）
- L タスクに「3 ステップ完了ごとに計画突合チェック」を追記

### Task 2: session-protocol.md にセッション後クリーンアップ推奨 (S)

**ファイル**: `.config/claude/references/session-protocol.md`

変更内容:
- Session End セクションに「L タスクのセッション終了時は blast radius チェックを推奨」を追記
- 具体的な推奨: `doc-gardener` でドキュメント同期、`cross-file-reviewer` で影響範囲確認

### Task 3: autonomous SKILL.md にタスク分解ガイドライン追記 (S)

**ファイル**: `.config/claude/skills/autonomous/SKILL.md`

変更内容:
- Step 2: Plan セクションに「1タスクあたり 100行以下を目安に分解。複雑性恐怖を防ぎ activation energy を最小化する」を追記

### Task 4: ハーネス rubric 評価を将来タスクとして記録 (S)

**ファイル**: MEMORY.md にポインタ追記のみ。`improve-policy.md` の session metrics が現時点の代替。
本格的な rubric 体系は別セッションで設計。
