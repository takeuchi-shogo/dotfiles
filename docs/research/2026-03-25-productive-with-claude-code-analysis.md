---
source: https://neilkakkar.com/productive-with-claude-code.html
date: 2026-03-25
status: analyzed
author: Neil Kakkar (Tano)
---

## Source Summary

**主張**: AI生産性の鍵はAI自体ではなく、ワークフローの摩擦を体系的に排除するインフラ構築。Theory of Constraints を適用し、1つの摩擦を解消すると次のボトルネックが見える。

**手法**:
1. `/git-pr` スキル — PR作成の全自動化（staging→commit→description→push）
2. SWC移行 — ビルド再起動を1分→1秒以下に（フロー維持）
3. Preview機能 — エージェント自身がUIを検証（"done" の条件に含める）
4. Worktree ポート割り当て — worktree ごとに一意のポート範囲を自動付与し、並列開発の衝突排除

**根拠**: 各改善が次の摩擦を露出させ、段階的に生産性が指数関数的に向上。5 worktree 同時運用を実現。

**前提条件**: フロントエンド+バックエンドのWebアプリ開発、マルチポートアーキテクチャ、チーム開発

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | PR作成自動化 (`/git-pr`) | Already | `/commit` + `/pull-request` + `/create-pr-wait` + `/github-pr` で PR ライフサイクル全体をカバー |
| 2 | ビルド速度最適化 (SWC) | N/A | dotfiles リポジトリにアプリビルドなし。原則はworkflowに組み込み済み |
| 3 | エージェントUI自己検証 (Preview) | Already | `/webapp-testing` (agent-browser) + Playwright MCP + `/validate` |
| 4 | Worktree ポート自動割り当て | **Gap** | Worktree は EnterWorktree/ExitWorktree で対応済みだがポート衝突回避なし |
| 5 | Theory of Constraints | N/A | マインドセット。`/improve` (AutoEvolve) が実質同機能 |
| 6 | 実装者→マネージャー変化 | Already | "Humans steer, agents execute" 哲学が全体に浸透 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す視点 | 強化案 |
|---|-------------|---------------|--------|
| 1 | PR ライフサイクル4スキル | PR description が full diff 読みで高品質 | Already (強化不要) — `/create-pr-wait` が CI まで面倒を見る点で記事を上回る |
| 3 | `/webapp-testing` + `/validate` | 「変更はagentがUI検証するまで done ではない」— 検証をゲート条件に | **Already (強化可能)** — `completion-gate.py` にフロントエンド変更時の UI 自己検証 advisory がない |
| 6 | Harness 全体 | manager は agent の grunt work を自動化 | Already (強化不要) |

## Integration Decisions

- [x] **T1**: Worktree ポート自動割り当てスクリプト — 取り込む
- [x] **T2**: completion-gate.py に UI 自己検証 advisory — 取り込む
- [ ] ビルド速度 / ToC / 役割変化 — N/A or Already、スキップ

## Plan

### T1: Worktree ポート自動割り当て (S)

- `scripts/runtime/worktree-port-alloc.sh` 新規作成
  - プロジェクトの `.env` / `docker-compose.yml` からベースポート検出
  - worktree インデックスに応じたオフセット（+100, +200...）で `.env.worktree` 生成
- `references/workflow-guide.md` にポート割り当ての記載追加
- `superpowers:using-git-worktrees` skill から参照可能にする

### T2: completion-gate UI 自己検証 advisory (S)

- `scripts/policy/completion-gate.py` に `_check_ui_verification()` 追加
  - 変更ファイルに `.tsx/.jsx/.vue/.svelte/.css` が含まれるか検出
  - セッション中に `agent-browser` / Playwright 使用マーカーを確認
  - 未検証なら advisory メッセージ出力（ブロックではない）
