---
status: reference
last_reviewed: 2026-04-27
related: paper-analysis/SKILL.md (Step 3.5), provenance-tagging.md
---

# Concept Relation Extraction — 概念ペア関係の構造化抽出

論文群から **概念ペア間の関係** を構造化 JSON で抽出する。Step 1 (論文間関係) と Step 3 (概念系譜) を補完し、graph 化可能な (subject, predicate, object) トリプルを得る。

> 出典: graphify (https://github.com/safishamsi/graphify) の Claude subagent 並列抽出パターンを paper-analysis 文脈に翻訳。
> 関係タイプ列挙は GraphRAG (Microsoft, 2024) の relation taxonomy を参考。

## 関係タイプ定義 (Closed Vocabulary)

`predicate` は以下 6 種から選ぶ。Closed vocabulary により下流の集計・可視化が安定する。

| predicate | 意味 | 例 |
|-----------|------|-----|
| `cites` | A が B を引用・参照 | "Transformer cites Attention" |
| `extends` | A が B の延長・拡張 | "RLHF extends RL from Human Preferences" |
| `contradicts` | A と B が直接対立 | "Hard Attention contradicts Soft Attention" |
| `depends_on` | A の主張が B の前提に依存 | "Chain-of-Thought depends_on In-Context Learning" |
| `refines` | A が B を改良・精緻化 | "GQA refines MQA" |
| `unifies` | A が複数概念 B,C を統合 | "Mixture-of-Experts unifies Sparse Routing + Conditional Compute" |

vocabulary 外の関係を見つけた場合は `unifies` か `depends_on` のどちらかに最も近づける。それも難しければ `extends` でフォールバックし、`notes` フィールドに自然文で記述する。

## 出力スキーマ

```json
{
  "concepts": [
    {"id": "c1", "name": "Transformer", "first_paper": "Vaswani 2017"}
  ],
  "relations": [
    {
      "subject": "c1",
      "predicate": "extends",
      "object": "c2",
      "evidence_paper": "Vaswani 2017",
      "evidence_section": "Section 3.1",
      "provenance": "EXTRACTED",
      "confidence": 90,
      "notes": "Transformer drops recurrence from Bahdanau 2014 attention"
    }
  ]
}
```

各フィールド:

- `provenance`: `EXTRACTED` (本文から直接) / `INFERRED` (合理的に推論) / `AMBIGUOUS` (本文では断定不能)。詳細は `provenance-tagging.md`
- `confidence`: 0-100 整数。provenance とは直交軸 (provenance=出所、confidence=確度)
- `evidence_section`: 必ず指定。指定不能なら `provenance: AMBIGUOUS` か relation 自体を捨てる

## 抽出パターン (Sonnet/Haiku 並列委譲)

1論文あたり 1 サブエージェントで並列実行。10 論文 = 10 並列。各サブエージェントへの指示:

```
以下の論文から、他の論文または既知の概念との関係を抽出してください。

[論文タイトル + Abstract + 抽出済み概念リスト]

ルール:
1. 関係は (subject, predicate, object) のトリプル形式
2. predicate は relation-extraction.md の closed vocabulary から選ぶ
3. evidence_section を必ず指定 (Section 番号 or ページ)
4. 推論を含む場合は provenance: INFERRED とし、根拠を notes に明記
5. 本文と矛盾しない範囲で AMBIGUOUS は積極的に使ってよい (false 抽出より良い)
6. 1 論文あたり最大 8 関係。重要度上位のみ
7. JSON で返す。散文禁止
```

## 集約 (Opus)

並列出力された JSON を Opus が集約:

1. 同一概念のエイリアス統合 (`Transformer` と `transformer architecture`)
2. 同一トリプルの重複排除 (subject, predicate, object 完全一致)
3. 矛盾する関係の検出 (`A contradicts B` と `A extends B` が共存 → AMBIGUOUS に降格)
4. confidence の高い順にソート

## レポート出力

`paper-analysis-report.md` の `## Step 3.5: Concept Relations` セクションに以下を記載:

```
| # | A | predicate | B | provenance | conf | evidence |
|---|---|-----------|---|-----------|------|----------|
| 1 | Transformer | extends | Bahdanau Attention | EXTRACTED | 90 | Vaswani 2017 §3.1 |
| 2 | RLHF | depends_on | Reward Model | INFERRED | 75 | Christiano 2017 §2 |
```

下流で `compile-wiki` がこの表を読み、概念グラフを構築可能にする。

## Anti-Patterns

| NG | 理由 |
|----|------|
| 全関係を `cites` で埋める | predicate 多様性が崩壊し集計が無意味化 |
| evidence_section 不明のまま EXTRACTED とする | provenance の信頼性が崩れる |
| 1 論文から 20+ 関係を抽出 | ノイズが信号を上回る (上限 8 を守る) |
| 自然文の `notes` に長文を書く | JSON が散文化、下流処理が困難に |
| `inferred` を避けて全部 EXTRACTED にする | サイレント断定。AMBIGUOUS 含めて使い分ける |

## Chaining

- `compile-wiki` が relations を読んで concept graph を構築
- `provenance-tagging.md` で provenance × confidence の組み合わせ運用ルールを参照
- `graphify` 本体は採用していない (CRG + paper-analysis で代替)
