---
source: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/04-quality-security/chaos-engineer.md
date: 2026-04-07
status: integrated
---

## Source Summary

Chaos Engineer サブエージェント定義。制御された障害実験を科学的手法（仮説→実験→学習）で設計・実行し、インシデント前にシステム耐障害性を検証する。

**主張**: 障害は避けられないので、制御された環境で事前に発見する方が安全。
**手法**: 安全性チェックリスト、4ドメイン障害注入（infra/app/data/security）、blast radius 制御、Game Day、CI/CD統合自動化。
**前提条件**: インフラ規模のサービス向け。dotfiles/harness では再解釈が必要。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Chaos Engineer エージェント定義 | Gap | 専用エージェントなし。edge-case-hunter は静的分析のみ |
| 2 | Game Day 計画フレームワーク | N/A | dotfiles/harness コンテキストでは対象外 |
| 3 | CI/CD統合の自動カオステスト | N/A | インフラサービスなし |
| 4 | 仮説→実験→学習の科学的手法 | Partial | `/spike` が仮説検証を持つが構造不十分 |
| 5 | 進捗追跡の構造化JSON | N/A | TaskCreate/TaskUpdate で十分 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事の知見 | 判定 |
|---|-------------|-----------|------|
| 1 | agency-safety-framework.md — blast radius 制御 | rollback < 30s、circuit breaker | 強化不要（既存の方が詳細） |
| 2 | failure-taxonomy.md — FM-001〜FM-021 | 4ドメイン障害カテゴリ | 強化可能 → HFM-001〜004 追加 |
| 3 | edge-case-hunter — 静的コード分析 | 動的障害注入 + 観察 | 強化可能 → ハーネス破壊的変更チェック追加 |
| 4 | `/spike` — worktree 隔離 + validation | 定常状態→仮説→blast radius | 強化可能 → Step 3.5 追加 |

## Integration Decisions

全項目を取り込み:

1. **failure-taxonomy.md**: HFM-001〜004（ハーネス障害モード）を追加。hook 未発火、script crash、設定不整合、symlink 切れを分類
2. **edge-case-hunter.md**: チェック項目 7「ハーネス破壊的変更」を追加。.config/claude/ 配下の変更時に hook/settings/symlink の整合性を検証
3. **spike/SKILL.md**: Step 3.5「Experiment Design」を追加。破壊的変更時に定常状態定義→仮説文書化→blast radius 計画→観察ポイントを明示化

スキップ:
- Chaos Engineer 専用エージェント: 既存の仕組み（safety framework + edge-case-hunter + spike）で十分カバー。専用エージェントは過剰
- Game Day / CI/CD 自動化 / 進捗JSON: dotfiles コンテキストに不適合 (N/A)

## Plan

| # | タスク | ファイル | 規模 | 状態 |
|---|--------|---------|------|------|
| 1 | HFM-001〜004 追加 | `references/failure-taxonomy.md` | S | 完了 |
| 2 | チェック項目 7 追加 | `agents/edge-case-hunter.md` | S | 完了 |
| 3 | Step 3.5 追加 | `skills/spike/SKILL.md` | S | 完了 |
| 4 | 分析レポート保存 | `docs/research/` (本ファイル) | S | 完了 |
