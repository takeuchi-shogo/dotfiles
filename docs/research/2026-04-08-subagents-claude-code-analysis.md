---
source: "https://claude.com/blog/subagents-in-claude-code"
date: 2026-04-08
status: analyzed
---

# Subagents in Claude Code — 分析レポート

- **ソース**: https://claude.com/blog/subagents-in-claude-code
- **分析日**: 2026-04-08
- **カテゴリ**: Claude Code 公式ベストプラクティス

## Source Summary

**主張**: Claude Code のサブエージェント活用ガイド。5つの使用パターン（リサーチ委譲、並列タスク、フレッシュ視点、コミット前検証、パイプライン）と4つの指示方法（会話、カスタムエージェント、CLAUDE.md、Skills、Hooks）、アンチパターンを提示。

**手法**:
- リサーチ委譲（research delegation, explore）
- 並列独立タスク（parallel subagents, independent）
- フレッシュ視点レビュー（fresh perspective, unbiased review）
- コミット前検証（verification, second opinion）
- パイプラインワークフロー（pipeline, handoff, sequential stages）
- 会話的呼び出し（conversational invocation）
- カスタムエージェント定義（.claude/agents/, description routing）
- CLAUDE.md ポリシー（CLAUDE.md, always use, policy）
- Skills マルチステップ（skills, multi-step, reusable）
- Hooks 自動化（hooks, Stop, automated）
- アンチパターン（anti-patterns, overhead, coordination）

**根拠**: Claude 公式ブログ — 実装経験に基づく推奨パターン集

**前提条件**: Claude Code ユーザー全般。チーム共有・Claude-native surface を前提とした記述も含む

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | built-in type 三分類 (general-purpose, plan, explore) | N/A | モデル別ルーティングの方が細粒度。必要時は既に使用中 |
| 2 | リサーチ委譲 | Already | /research スキル + Explore 委譲、Aggregate → Polish 2段圧縮 |
| 3 | 並列独立タスク | Already | Task Parallelizability Gate + worktree 分離 + Google Research 閾値表 |
| 4 | フレッシュ視点レビュー | Already (強化可能) | /review スキル存在。solo 環境での advisory review は弱い |
| 5 | コミット前検証 | Already | pre-commit hook + completion-gate + Lefthook 三層 |
| 6 | パイプライン | Already | S/M/L 規模別パイプライン + EPD + ゲート条件 |
| 7 | 会話的呼び出し | N/A | hook + skill で自動化済み |
| 8 | カスタムエージェント定義 | Already (強化可能) | 33 agents 定義済み。tools 制限の一貫性未検証、router drift 監視なし |
| 9 | CLAUDE.md ポリシー | Already | agent_delegation ブロック + model 別 + 並行実行方式表 |
| 10 | Skills | Already | 85+ skills + 5パターン分類 + テンプレート構造 |
| 11 | Hooks | Already | 8イベント × 20+ hooks |
| 12 | アンチパターン | Already | failure-taxonomy + conflict-patterns + 研究引用 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | /review スキル | solo 環境で advisory review は弱い。ハーネス変更時に強制レビューがない | completion-gate.py にハーネス変更時 mandatory review block 追加 | 強化可能 |
| S2 | 33 agents (.claude/agents/) | tools 制限の一貫性未検証、router drift 監視なし | validate-agents.sh スクリプト作成（tools 監査）+ agent-router ログ追加 | 強化可能 |

## Integration Decisions

### Gap / Partial

なし（全手法が Already または N/A）

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | completion-gate にハーネス変更時 mandatory review block 追加 | 採用 | Codex 批評「solo 環境でのフレッシュ視点レビューは最も過小評価されたパターン」と一致 |
| S2 | validate-agents.sh + Taskfile タスク追加 | 採用 | 33 agents の router drift 監視は数そのものより本質。ログ追加で可観測性向上 |

## セカンドオピニオン (Codex)

- built-in subagent_type 三分法は gap として過大評価（運用能力は既にある）
- 33 agents は数そのものより router drift 監視が本質
- solo 環境でのフレッシュ視点レビューは最も過小評価されたパターン
- チーム共有前提・Claude-native surface 前提は文脈ミスマッチ

## Plan

### Task 1: completion-gate.py にハーネス変更時 mandatory review block 追加
- **Files**: `.config/claude/scripts/lifecycle/completion-gate.py`, `/review` スキル
- **Changes**: ハーネスファイル（hooks, scripts, settings.json）変更を検出し、レビュー未完了なら block する
- **Size**: M

### Task 2: /review スキルに PASS フラグ書き出し追加
- **Files**: `.config/claude/skills/review/` 関連ファイル
- **Changes**: PASS 判定時に completion-gate が参照できるフラグファイルを出力
- **Size**: S

### Task 3: validate-agents.sh スクリプト作成（tools 監査）
- **Files**: `.config/claude/scripts/` または `.bin/validate_agents.sh`（新規）
- **Changes**: agents/*.md の tools フィールドを検査し、未定義 tool 参照や不整合を検出
- **Size**: S

### Task 4: Taskfile に validate-agents タスク追加
- **Files**: `Taskfile.yml`
- **Changes**: `task validate-agents` コマンドで validate-agents.sh を実行
- **Size**: S

### Task 5: agent-router.py にルーティングログ追加
- **Files**: `.config/claude/scripts/runtime/agent-router.py`
- **Changes**: どのエージェントへルーティングされたか structured log に記録。drift 検出の基盤
- **Size**: S

## 総合評価

記事の 12 手法すべてが Already または N/A。セットアップは公式ガイドの推奨を全面的に超えている。Codex の批評により2項目の強化を実施。統合タスク 5 件は可観測性とレビュー強制の改善に集中しており、いずれも S/M 規模で実装コストは低い。
