---
source: Master Claude Skills (Module 2: Architecture)
date: 2026-04-02
status: integrated
---

## Source Summary

初〜中級者向けのスキルアーキテクチャガイド。3つの柱を提唱:

1. **scripts/ レイヤー**: インストラクション（推論）とスクリプト（実行）の分離。計算・ファイル処理・外部連携はスクリプトに委譲
2. **マルチスキルオーケストレーション**: テリトリー定義、負の境界（Do NOT use for）、トリガー言語の差別化で衝突を防止
3. **リファレンス最適化**: 選択的ロードでコンテキスト消費を抑制

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | scripts/ レイヤー | Already | scripts/{runtime,policy,lifecycle,learner,lib}/ の4層構造 |
| 2 | 1スクリプト=1責務 | Already | 層別ディレクトリで単一責任を強制 |
| 3 | テリトリー定義 | Already | 30+スキルに Triggers + Do NOT use for。skill-suggest.py hook |
| 4 | 負の境界 | Already | 全スキルに実装済み |
| 5 | トリガー言語の差別化 | Already | description-optimization.md にeval駆動の最適化ループ |
| 6 | 選択的リファレンスロード | Already | CLAUDE.md の `<important if>` 条件付きタグ |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 3 | Triggers + Do NOT use for | 全スキル横断の衝突検出プロセスが未定義 | skill-audit に Full Trigger Conflict Scan モードを追加 |
| 6 | `<important if>` パターン | スキル references/ の予算管理が未明文化 | planning-guide に Reference Budget セクションを追記 |

## Integration Decisions

- [x] skill-audit に Full Trigger Conflict Scan モードを追加（S規模）
- [x] planning-guide に Reference Budget 原則を追記（S規模）

## Changes Made

### 1. skill-audit/SKILL.md — Full Trigger Conflict Scan

既存の Competing Pair Analysis（手動ペア指定）の後に、全スキル横断の自動衝突検出モードを追加:
- `/skill-audit conflict-scan` で起動
- 全 SKILL.md の description から Triggers/Do NOT use for を抽出
- 完全一致・部分包含・排他欠落の3種の衝突を検出
- テリトリーマップで境界を可視化
- 深刻度（High/Medium/Low）でトリアージ

### 2. skill-creator/references/planning-guide.md — Reference Budget

Success Criteria セクションの前に Reference Budget セクションを追加:
- 1 reference ファイル 200 行以下推奨
- 1 スキルあたり references/ 合計 5 ファイル・1000 行以下
- アンチパターン（一括 Read、巨大ファイル、動的情報の混入）
- 判断フロー（SKILL.md 直接記載 vs references/ 分離）
