---
name: rpi
description: "Research → Plan → Implement の3フェーズで体系的にタスクを実行する"
allowed-tools: Agent, Read, Write, Edit, Bash, Glob, Grep, EnterPlanMode, ExitPlanMode, TaskCreate, TaskUpdate, TaskList, WebSearch, WebFetch
user-invocable: true
---

# RPI ワークフロー: Research → Plan → Implement

以下のタスクを RPI ワークフローで実行してください:

**タスク**: $ARGUMENTS

---

## Phase 1: Research (調査)

まず Explore エージェントを使って徹底的に調査する:

1. **コードベース調査**: タスクに関連するファイル、パターン、依存関係を特定
2. **既存実装の理解**: 類似機能や関連コードがないか確認
3. **制約の把握**: 技術的制約、互換性要件、パフォーマンス要件を洗い出す

調査結果を簡潔にまとめてユーザーに共有する。

## Phase 2: Plan (計画)

EnterPlanMode を使って実装計画を立てる:

1. 調査結果に基づいて具体的な実装ステップを設計
2. 変更対象ファイルと影響範囲を明示
3. リスクや代替案がある場合は提示
4. ユーザーの承認を得てから次のフェーズへ

## Phase 3: Implement (実装)

承認された計画に基づいて実装する:

1. 計画のステップに従ってコードを実装
2. テストを実行して動作を確認
3. 変更規模に応じたコードレビューを実施（CLAUDE.md のレビュースケーリングに従う）
4. 検証が完了したらユーザーに報告

---

## 重要な原則

- **各フェーズをスキップしない**: 簡単に見えるタスクでも、Research で予期しない制約が見つかることがある
- **調査と計画の分離**: Research は事実収集、Plan は意思決定。混ぜない
- **計画承認後に実装**: ユーザーの承認なしに実装を開始しない
- **search-first**: 既存の解決策やライブラリがないか必ず確認する
