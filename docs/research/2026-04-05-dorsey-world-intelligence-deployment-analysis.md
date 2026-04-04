---
source: "How to practically deploy Jack Dorsey's 'world intelligence' today (Single Grain / Neil Patel)"
date: 2026-04-05
status: integrated
---

## Source Summary

Jack Dorsey & Roelof Botha のエッセイ "From Hierarchy to Intelligence" (2026-04-01) の実装体験記。
Single Grain 社が4ヶ月間、Dorsey の4層フレームワーク（Capabilities → World Model → Intelligence Layer → Surfaces）を中小企業で実装した知見。

**主張**: 理論と実装のギャップが最大の事業機会。複利効果は実在するが初期3ヶ月は苦痛。

**手法**:
1. 統一ベクターDB (Single Brain) — 全社データ15分間隔取り込み
2. 専門エージェント艦隊 + World Agent（コーディネーター）
3. エージェント統合トレンド — 多数→少数の高能力エージェント (skill modes)
4. DRI システム — 一時チーム→90日→解散→学習吸収
5. AutoResearch / AutoGrowth — パターンマイニング + 自動A/Bテスト
6. エージェント競合解決 — 複数エージェントの矛盾行動の検出・調停
7. 多層パーミッション (3-tier)
8. 複利効果の設計 — フィードバックループでデータ蓄積 = 堀
9. Surfaces = ユーザーの既存場所
10. Day 1 セキュリティ

**根拠**: 4ヶ月の実運用。具体的失敗事例（エージェントがクライアント財務データを誤送信しかけた等）。

**前提条件**: 継続的データ取り込み、初期3ヶ月は投資期間、エージェント失敗を許容する文化。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 統一ベクターDB (Single Brain) | N/A | 企業全社データの取り込みは個人開発スコープ外。CLAUDE.md + MEMORY.md + agent-memory が共有コンテキスト |
| 3 | エージェント統合トレンド | Partial | 30+エージェント存在。統合・skill modes化は未着手 |
| 4 | DRI 学習吸収 | Partial | /feature-tracker + /autonomous は近い。完了時の自動学習吸収サイクルがない |
| 5 | AutoResearch / AutoGrowth | Partial | AutoEvolve(パターンマイニング)あり。AutoGrowth(自動A/B→フィードバック)なし |
| 6 | エージェント競合解決 | Gap | skill-audit にトリガー衝突検出あり。実行時の矛盾検出・調停は未実装 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 2 | 30+エージェント + triage-router | モデル能力向上で1エージェントが複数専門をカバー可能。管理オーバーヘッド | 定期棚卸しを /skill-audit に統合 |
| 7 | memory scope 3層 + agent契約 | エージェントは創造的にデータアクセスする | 強化不要 — ツール制限でインフラレベル防止 |
| 8 | AutoEvolve学習ループ | タスク成果→推奨改善のループが弱い | /improve Phase 2 に成果追跡ソース追加 |
| 9 | CLI + IDE + Slack/Discord | — | 強化不要 |
| 10 | security hooks + reviewers | — | 強化不要 |

## Integration Decisions

全 Gap/Partial (4件) + Already強化 (2件) を取り込む。

## Plan

### Task 1: Agent Consolidation Audit (#2 + #3)

**規模**: S | **優先度**: 中

`/skill-audit` に「エージェント統合候補の検出」を追加する。

- **変更先**: `.config/claude/skills/skill-audit/SKILL.md`
- **内容**: エージェント一覧を走査し、以下を検出する新セクション追加
  - 同一ドメインの重複エージェント
  - 過去30日で起動ゼロのエージェント
  - skill modes で統合可能な候補ペア
- **依存**: なし

### Task 2: Agent Runtime Conflict Guard (#6)

**規模**: M | **優先度**: 高（唯一の Gap）

並列エージェント実行時の矛盾検出メカニズム。

- **変更先**: `.config/claude/references/` に新規 `agent-conflict-patterns.md`
- **内容**:
  - 矛盾パターンのカタログ（同一ファイルへの矛盾編集、相反する推奨、スケジュール競合）
  - Opus（コーディネーター層）が並列エージェント結果を統合する際の検証チェックリスト
  - `/dispatch` や Agent 並列実行時のプロンプトに注入するガードレール文言
- **注**: hook での自動検出は現時点では過剰。まずはリファレンスドキュメントとして知識を codify し、Opus の判断に委ねる（Build to Delete 原則）
- **依存**: なし

### Task 3: DRI Completion → Learning Extraction (#4)

**規模**: S | **優先度**: 中

`/feature-tracker` の pass/complete フローに学習抽出ステップを追加。

- **変更先**: `.config/claude/skills/feature-tracker/SKILL.md`
- **内容**: `pass` サブコマンド実行時に以下を自動実行
  1. 完了した feature の実装で得た知見を要約
  2. `agent-memory/learnings/` に learning エントリとして保存
  3. 次回の `/improve` で参照可能に
- **依存**: なし

### Task 4: Outcome Tracking in AutoEvolve (#8)

**規模**: S | **優先度**: 中

`/improve` Phase 2 の分析ソースに「過去タスク成果の追跡」を追加。

- **変更先**: `.config/claude/skills/improve/SKILL.md`
- **内容**: Phase 2 のデータソースリストに追加
  - `agent-memory/learnings/` の task completion entries
  - `/feature-tracker` の成功/失敗パターン
  - 「推奨→実行→結果」の因果追跡
- **依存**: Task 3（learning extraction が先に必要）

### Task 5: AutoGrowth — Experimental Validation (#5)

**規模**: M | **優先度**: 低

自動的な A/B 検証ループ。`/spike` の延長として実験結果を自動追跡。

- **変更先**: `.config/claude/skills/improve/SKILL.md` の Phase 3 に実験バリデーションステップ追加
- **内容**:
  - `/improve` で生成された改善提案に対し、適用前後の定量比較を記録
  - `experiment-log.md` テンプレートは既存（`skills/improve/templates/experiment-log.md`）
  - 複数サイクルの結果を蓄積し、「効果があった改善パターン」を学習
- **依存**: Task 4

### 実行順序

```
Task 1 (S) ──┐
Task 2 (M) ──┼── 並列実行可能
Task 3 (S) ──┘
               ↓
Task 4 (S) ── Task 3 に依存
               ↓
Task 5 (M) ── Task 4 に依存
```

**総規模**: M（5ファイル変更）
