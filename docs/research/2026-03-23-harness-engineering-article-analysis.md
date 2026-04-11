---
source: https://qiita.com/miruky/items/155f3b5a0dcde72fcd10
date: 2026-03-23
status: integrated
---

## Source Summary

**主張**: ハーネスエンジニアリングは Prompt → Context → Harness というパラダイム進化の最新段階。複数セッションにまたがるエージェントの一貫性・品質維持のための環境・制御・フィードバック設計。

**手法**:
1. イニシャライザーエージェント + コーディングエージェントの2エージェント構成
2. フィーチャーリスト（JSON + passes フラグ）で進捗を構造化管理
3. init.sh でセッション開始時に環境を確実に復元
4. claude-progress.txt で時系列の進捗ログを追記
5. 「1セッション1機能」ルールでコンテキスト喪失を防止
6. セッション終了時の「クリーン状態」定義（mainマージ可能レベル）
7. 4層フィードバック（コンパイル → ユニットテスト → E2E → CI）
8. コードベース自体をコンテキストとして設計（DDD、命名統一）
9. 技術的負債のエージェントによる指数関数的増幅の認識 + 定期リファクタリング
10. 3プリミティブ: 分離（worktree）・分解（スコープ明確化）・協調（役割ではなく権限）
11. 強い型付け = 品質ゲート
12. JSON > Markdown（構造化データのエージェント改変耐性）

**根拠**: Anthropic「Effective harnesses for long-running agents」(2025-11)、Reddit r/ClaudeAI 52日350Kライン事例

**前提条件**: 長時間（マルチセッション）のエージェント駆動開発。単発タスクや小規模修正には過剰。

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | イニシャライザーエージェント | Already | `/init-project` スキル |
| 2 | フィーチャーリスト（JSON + passes） | Gap | PLANS.md + タスク管理で代替中 |
| 3 | init.sh（環境復元） | Partial | Taskfile.yml がビルド・検証を担当 |
| 4 | claude-progress.txt | Partial | checkpoint + memory で代替 |
| 5 | 1セッション1機能ルール | Gap | S/M/L 表はあるが明示的制約なし |
| 6 | クリーン状態定義 | Partial | completion-gate.py + session_events.py |
| 7 | 4層フィードバック | Already | hooks 4層 + lefthook |
| 8 | コードベース=コンテキスト | Already | Progressive Disclosure |
| 9 | 技術的負債増幅対策 | Partial | /review, /simplify あるが定期化なし |
| 10 | 3プリミティブ | Already | worktree + subagents + agent teams |
| 11 | 強い型付け | Already | Go + TypeScript + lefthook |
| 12 | JSON > Markdown | N/A | Markdown frontmatter で安定動作中 |

## Integration Decisions

全 Gap/Partial 項目（#2, #3, #4, #5, #6, #9）を統合対象として選択。

## Plan

`docs/plans/2026-03-23-harness-engineering-integration.md` 参照。
