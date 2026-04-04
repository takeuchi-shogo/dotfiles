---
source: https://speakerdeck.com/soudai/designing-for-reversible-decisions
date: 2026-04-04
status: integrated
---

## Source Summary

曽根壮大「失敗できる意思決定とソフトウェアとの正しい歩き方」。技術選定を含む意思決定において、「正解を探す」のではなく「失敗してもやり直せる設計にする」ことで素早く決断できるフレームワークを提示。

**主張**: 判断（情報で解ける）と決断（情報不足で決める）を区別し、決断には「失敗できる状態」を先に作る。ゆっくり考えて素早く実行する。

**手法**:
- 判断 vs 決断の区別フレーム
- 失敗できる3要素: やり直し可能、学べる、素早く試せる
- 4段階アプローチ: 条件整理 → 小さく失敗 → 知見収集 → 先送り
- 参照クラス予測法（類似事例からの見積もり補正）
- 反証の積極的探索（確証バイアス回避）
- インチストーン（最小検証可能単位）
- One change at a time（変数最小化）
- 後に変更可能な設計（コンテナ、REST、CQRS、認証/認可分離）

**根拠**: 失敗プロジェクト = 素早く考えてゆっくり動く、成功プロジェクト = ゆっくり考えて素早く動く。プロジェクト期間が長いほどブラック・スワンリスク増大。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 撤退条件の明確化 | Partial | rollback 概念は migration-guard 等にあるが、Plan/Spec テンプレートに撤退条件フィールドがなかった |
| 2 | 判断 vs 決断の区別 | Gap | 意思決定の分類フレームワークが未定義 |
| 3 | 参照クラス予測法 | Gap | variation-operators.md に言及があるが Plan フローに未組込 |
| 4 | Plan 前チェックリスト | Partial | brainstorming スキルが探索を促すが構造化チェックリストではなかった |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す視点 | 強化案 |
|---|-------------|---------------|--------|
| A | Build to Delete 原則 | 交換可能な設計 | 強化不要 |
| B | KISS 原則 | Simple ≠ Easy | 強化不要 |
| C | /spike スキル | 素早く試せる環境 | 強化不要 |
| D | experiment-discipline.md | One change at a time | 強化: 変数最小化の原則文を追加 |
| E | Adversarial gate | 反証探索 | 強化: Plan 策定時にも反証探索を促す |

## Integration Decisions

全5項目を統合:
1. `references/reversible-decisions.md` を新規作成 — 判断vs決断フレーム、Plan前チェックリスト、反証探索ステップ
2. `skills/spec/templates/prompt-as-prd-template.md` に Exit Criteria セクション追加
3. `references/experiment-discipline.md` に One change at a time 原則を明示追加
4. `CLAUDE.md` の planning セクションに reversible-decisions reference へのポインタ追加

## Plan

- [x] Task 1: references/reversible-decisions.md 作成
- [x] Task 2: Spec テンプレートに撤退条件追加
- [x] Task 3: experiment-discipline.md 補強
- [x] Task 4: CLAUDE.md に参照追加
