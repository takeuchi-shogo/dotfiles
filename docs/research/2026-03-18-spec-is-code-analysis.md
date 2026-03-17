---
source: https://haskellforall.com/2026/03/a-sufficiently-detailed-spec-is-code
date: 2026-03-18
status: integrated
---

# "A Sufficiently Detailed Spec Is Code" — 分析レポート

## Source Summary

### 主張

仕様書を AI コード生成に十分な精度まで精密化すると、仕様書自体がコードに収束する。
これにより仕様書を書く労力の節約効果が消失する。

### 手法・パターン

1. **Borges の地図問題**: 仕様書と実装が 1:1 対応になる限界点の認識
2. **Spec slop 検知**: AI 生成の仕様書が「形式は整っているが中身が空虚」になる問題
3. **精度天井の判断**: 擬似コード・DB スキーマ・条件分岐の網羅的記述が spec に入ったら、コードを書くべきサイン
4. **仕様書 = 思考ツール**: 仕様書は agent への入力ではなく、人間の思考整理が第一目的

### 根拠

- Symphony プロジェクトの SPEC.md 分析（実装の 1/6 サイズで既にコードライク）
- 著者自身の Haskell 実装実験（spec からの生成が失敗）
- Dijkstra の「narrow interfaces」原理（形式的精密さには形式的記号が必要）
- YAML 仕様書の事例（詳細な仕様 + 適合テストでも非準拠が横行）

### 前提条件

- agentic coding（AI によるコード生成）を仕様書駆動で行う文脈
- 仕様書を「労力節約ツール」として位置づけている場合に最も relevant

## Gap Analysis

| # | 記事の知見 | 判定 | 現状 |
|---|-----------|------|------|
| 1 | 仕様書は思考ツールであり労力節約ツールではない | Partial | `/spec` が「agent 向け実行可能仕様書」フレーミング |
| 2 | 精密すぎる仕様書はコードに収束する | Gap | 精度天井のガイダンスなし |
| 3 | 急いだ仕様書は slop になる | Partial | overconfidence-prevention に spec 品質チェックなし |
| 4 | 不確実なときは仕様書よりプロトタイプ | Already | `/spike` が exactly これ |
| 5 | Dijkstra の narrow interfaces | Already | 質問プロトコルで曖昧さ排除 |
| 6 | 仕様書→コード生成は信頼できない | Already | EPD の Spike→Refine 反復 |
| 7 | spec 内の擬似コードの扱い | Gap | Prompt セクションのガイドラインなし |
| 8 | 小さな変更は直接コードを書くべき | Already | S 規模は Implement → Verify のみ |

## Integration Decisions

全 Gap/Partial 項目を取り込み:

1. **Spec 目的のリフレーミング** → `skills/spec/SKILL.md` に Philosophy セクション追加
2. **精度天井ガイドライン** → `skills/spec/SKILL.md` に Precision Ceiling セクション追加
3. **Spec slop 検知** → `rules/common/overconfidence-prevention.md` に検知ルール追加

## 変更ファイル

- `.config/claude/skills/spec/SKILL.md` — Philosophy + Precision Ceiling + Anti-Patterns 強化
- `.config/claude/rules/common/overconfidence-prevention.md` — Spec Slop Detection セクション追加
