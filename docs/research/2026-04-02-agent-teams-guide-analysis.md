---
source: "You Probably Don't Need Claude Agent Teams (But Here's When You Do)" (Reddit/blog article)
date: 2026-04-02
status: integrated
---

## Source Summary

**主張**: Agent Teams は大半のタスクでは不要（3-4xトークンコスト）だが、並列コードレビュー・競合仮説デバッグ・クロスレイヤー機能開発では代替不可能な価値がある。

**手法**:
1. Green/Yellow/Red シグナルフィルター — タスクの Agent Teams 適性を3段階分類
2. Delegate Mode — Lead はコード書かず計画・委譲に専念（Shift+Tab）
3. Teammate Briefing — コンテキスト非継承→spawn prompt に明示的ブリーフィング必須
4. Domain Separation — ファイル衝突防止のためドメイン分離厳格化
5. 5-6 tasks per teammate max — 小分け実行
6. Active Monitoring — set and forget せず積極的モニタリング
7. Read-only first — 初心者は読み取り専用タスクから開始
8. Bias isolation in review — 単一エージェントのアンカリングバイアス防止のため分離
9. Competing hypothesis + falsification — 仮説ごとにエージェント分離＋相互反証指示
10. Session ephemeral — /resume なし、セッション死亡でチーム消滅

**根拠**:
- アンカリングバイアス: 最初の発見が後続レビュー全体を歪める
- Context bias: デバッグ時、1つの証拠で他の仮説調査が弱まる
- Anthropic C compiler: 16 agents, ~2000 sessions, ~2B input tokens, <$20K
- 3-5 teammates が実用上限（それ以上は coordination overhead が利益を食う）

**前提条件**: タスクが並列分解可能、ドメイン分離可能、3-4xトークンコスト許容

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Green/Yellow/Red シグナルフィルター | Partial | Task Parallelizability Gate あり、Teams 固有分類なし |
| 2 | Delegate Mode 運用ガイド | Gap | 言及なし |
| 3 | 5-6 tasks per teammate max | Gap | セッション数上限はあるが teammate タスク数上限なし |
| 4 | Read-only first（入門ステップ） | N/A | 運用者が既に熟練 |
| 5 | Competing hypothesis debugging | Gap | systematic-debugging にはあるが Teams 分離パターンなし |
| 6 | Session ephemeral 警告 | Gap | /resume なしの注意書きなし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| A | Context Inheritance Policy | spawn prompt の明示的ブリーフィング不足 | Teams 用 briefing テンプレート追加 |
| B | Domain Separation | — | 強化不要（worktree + ファイル分割で十分） |
| C | Bias isolation in review | アンカリングバイアスの理論的根拠が未明示 | 根拠追記 |
| D | Active Monitoring | Lead が自分で実装する anti-pattern 未記載 | Anti-patterns テーブルに追加 |

## Integration Decisions

全 Gap/Partial 5項目 + Already 強化 3項目（A, C, D）を統合。#4 Read-only first は N/A でスキップ。

## Plan (実行済み)

`references/subagent-delegation-guide.md` の Agent Teams セクションに以下を追加:
- T1: Green/Yellow/Red 適性フィルターテーブル
- T2: Lead 運用ガイド（Delegate Mode + Active monitoring）
- T3: Teammate タスク上限（5-6/teammate）
- T4: 競合仮説デバッグパターン（仮説分離 + 相互反証）
- T5: Session ephemeral 警告（ライフサイクルセクション）
- T6: Briefing テンプレート（チェックリスト）
- T7: Bias isolation 理論根拠（Green フィルターに統合）
- T8: Anti-patterns 3行追加（Lead implements, spawn prompt 省略, タスク過剰投入）
