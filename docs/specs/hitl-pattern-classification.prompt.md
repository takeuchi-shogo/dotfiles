---
title: HITL Pattern Classification — meta-analyzer Extension
status: draft
created: 2026-04-07
scope: M
research_source: docs/research/2026-04-07-hitl-asymmetric-evaluation-analysis.md
acceptance_criteria:
  - "AC-01: セッション内（タスク間）の HITL 分布を Gini/CV/B/FLI で算出できる"
  - "AC-02: セッション横断（直近 N セッション）の HITL 分布を同 4 指標で算出できる"
  - "AC-03: 4 パターン（集中/分散/フロントローディング/ランダムバースト）に自動分類される"
  - "AC-04: パターン別の改善示唆が insights レポートに含まれる"
  - "AC-05: 時系列トレンド（前期 vs 直近）でパターン遷移を検出できる"
  - "AC-06: セッション < 10 で INSUFFICIENT_DATA を報告する"
---

# HITL Pattern Classification — Prompt-as-PRD

## Context

meta-analyzer の Task #11 に HITL パターン分類の骨格（4 指標の定義と閾値）が定義されているが、
以下が未実装:

1. **セッション内分析**: 単一セッション内のタスク間 HITL 分布の解析
2. **時系列トレンド**: パターンの遷移検出（例: 分散型→集中型への悪化）
3. **計算ロジック**: friction-events.jsonl からの具体的な集計・算出手順

背景: LayerX 澁井氏の HITL 非対称評価分析（2026-04）が提唱する 4 指標分類を
実行可能な分析タスクとして meta-analyzer に組み込む。

## Product Spec

- meta-analyzer が Analyze フェーズを実行すると、insights レポートの「HITL パターン分析」セクションに分類結果が出力される
- パターンが「集中型」の場合、自動化候補のタスクタイプが具体的に特定される
- パターンが「ランダムバースト型」の場合、判断疲労リスクの警告とセッション分割の推奨が出る
- 前期と比較してパターンが悪化している場合、トレンド警告が出る

## Tech Spec

### データモデル

入力データソース:
- `friction-events.jsonl`: `type: "friction_event"` で HITL イベントを抽出。各イベントに `session_id`, `timestamp`, `task_context` を含む
- `session-metrics.jsonl`: セッション単位の統計。HITL イベント数とセッション長を取得

分析は 2 レイヤーで実行:

| レイヤー | 粒度 | 入力 | 指標 |
|---------|------|------|------|
| Session-level | 1 セッション内のタスク間分布 | 当該セッションの friction-events | Gini, CV, B, FLI |
| Cross-session | 直近 N セッション横断 | N セッション分の friction-events 集約 | Gini, CV, B, FLI + トレンド |

### データフロー

```
friction-events.jsonl + session-metrics.jsonl
  → Session-level: セッションごとに 4 指標算出
  → Cross-session: セッション横断で 4 指標算出
  → パターン分類（閾値判定）
  → 前期比較（トレンド検出）
  → insights/analysis-YYYY-MM-DD.md に出力
```

### 主要な技術判断

- **算出は Bash (Python one-liner) で行う**: meta-analyzer は Sonnet + Read/Bash/Glob/Grep の構成。JSONL の集計は Python ワンライナーで実現する（外部ライブラリ不要、標準ライブラリの statistics/json/collections で十分）
- **外部スクリプト分離は不要**: 4 指標の算出は数十行程度。agent プロンプト内の手順記述で完結する
- **N = 20 セッション**: 統計的安定性と直近性のバランス。前期 = その前 20 セッション

## Requirements

| # | 要件 | 詳細 |
|---|------|------|
| R-01 | 4 指標の算出 | Gini 係数、変動係数 CV、Burstiness B、FLI を friction-events から算出 |
| R-02 | Session-level 分析 | 各セッション内のタスク間 HITL 分布を 4 指標で評価 |
| R-03 | Cross-session 分析 | 直近 20 セッション横断の HITL 分布を 4 指標で評価 |
| R-04 | パターン分類 | 閾値判定で 4 パターンに分類（集中/分散/フロントローディング/ランダムバースト） |
| R-05 | 改善示唆の生成 | パターンに応じた具体的な改善提案（自動化候補のタスク特定、セッション分割推奨等） |
| R-06 | トレンド検出 | 前期 20 セッション vs 直近 20 セッションのパターン遷移を検出 |
| R-07 | INSUFFICIENT_DATA | セッション数 < 10 の場合はデータ不足と報告 |

### 指標定義と閾値

| 指標 | 算出方法 | 閾値 |
|------|---------|------|
| **Gini** | HITL 件数のセッション間/タスク間分布の Gini 係数 | > 0.6: 集中型, < 0.3: 均一 |
| **CV** | 標準偏差 / 平均（HITL 頻度のばらつき） | < 1: 分散型（規則的）, > 1.5: 高変動 |
| **B** | (σ - μ) / (σ + μ)、HITL の連続集中度 | > 0.3 かつ CV > 1: ランダムバースト型 |
| **FLI** | セッション前半 50% 内の HITL 件数 / 全 HITL 件数 | > 0.7: フロントローディング型 |

### パターン分類ルール（優先順位順）

1. **フロントローディング型**: FLI > 0.7
2. **ランダムバースト型**: B > 0.3 かつ CV > 1
3. **集中型**: Gini > 0.6
4. **分散型**: 上記いずれにも該当しない

## Constraints

- meta-analyzer の既存タスク（1-10）を壊さない
- 読み取り専用（learnings/ を変更しない）
- Python 標準ライブラリのみ使用（statistics, json, collections）
- Sonnet の maxTurns: 20 内で全タスクが完了する時間配分

## Extensibility Checkpoint

- 新しい指標の追加: 閾値テーブルに行を追加するだけ。既存コードの変更箇所は 1（分類ルール）
- 新しいパターンの追加: 分類ルールに条件を追加。改善示唆テーブルに行を追加
- データソース変更: 入力テーブルの参照先を変えるだけ

## Out of Scope

- friction-events.jsonl の emit ロジック変更（既存の stagnation-detector.py が担当）
- HITL パターンの可視化 UI
- リアルタイム分類（バッチ分析のみ）
- 他の meta-analyzer タスクの変更

## Prompt

以下の仕様に基づいて meta-analyzer の Task #11 を拡張してください:

1. `.config/claude/agents/meta-analyzer.md` の Task #11 セクションを更新:
   - Session-level と Cross-session の 2 レイヤー分析を明記
   - 4 指標の具体的な算出手順（Python ワンライナー例）を追加
   - トレンド検出（前期 20 セッション vs 直近 20 セッション）を追加
   - パターン分類の優先順位ルールを明記
2. insights 出力フォーマットの「HITL パターン分析」セクションを拡張:
   - Session-level サマリー（直近セッションの分類）
   - Cross-session サマリー（全体の分類 + トレンド）
   - 改善示唆（パターン別の具体的提案）
3. 既存タスク（1-10）に影響がないことを確認
