---
status: reference
last_reviewed: 2026-04-27
related: skills/paper-analysis/, skills/compile-wiki/, skills/research/
origin: graphify absorb (2026-04-27) — GraphRAG 由来の業界標準
---

# Provenance Tagging — 三値タグと confidence の併記運用

知識抽出における **出所 (provenance)** と **確度 (confidence)** を直交軸として併記する。
graphify (2026) と Microsoft GraphRAG (2024) で採用された業界標準パターン。

## なぜ confidence だけでは不十分か

`confidence: 85` は確度を表すが、**その確度がどう得られたか** を表さない。

- 本文から直接抽出された「85」と、推論で得た「85」は意味が違う
- 本文に直接書いていない関係も、合理的推論なら高確度になりうる
- ただし、推論を本文抽出と区別しないと、下流の検証コストが膨らむ

→ provenance (出所) と confidence (確度) を **直交軸** として併記する。

## 三値 Provenance

| タグ | 意味 | 例 |
|------|------|-----|
| `EXTRACTED` | 本文・図表・参照リストに直接記載されている | "論文§3.1 で『Transformer は Attention に依存』と明記" |
| `INFERRED` | 本文に直接記載はないが、複数の根拠から合理的に推論できる | "§2 と §4 を組み合わせると依存関係が成立" |
| `AMBIGUOUS` | 本文では断定できない、または解釈が分かれる | "用語の定義が不明確で関係が確定しない" |

### 判定フロー

```
1. 本文・参照リストに直接記載があるか?
   YES → EXTRACTED
   NO  → 2.

2. 複数の根拠を組み合わせれば論理的に導出可能か?
   YES → INFERRED (notes に根拠箇所を併記)
   NO  → 3.

3. AMBIGUOUS (関係を捨てるか、ambig として残す)
```

## 表記ルール

### インライン (散文中)

```
Transformer は Attention に依存している `[EXTRACTED, conf=90]`
RLHF は Reward Model を前提とする `[INFERRED, conf=75]`
TPU と GPU の優位性は文脈依存 `[AMBIGUOUS, conf=50]`
```

### テーブル (構造化抽出)

| # | claim | provenance | conf | evidence |
|---|-------|-----------|------|----------|
| 1 | A → B | EXTRACTED | 90 | paper §3.1 |
| 2 | B → C | INFERRED | 75 | paper §2 + §4 |

### JSON (relation-extraction.md 等)

```json
{
  "subject": "A", "predicate": "depends_on", "object": "B",
  "provenance": "EXTRACTED",
  "confidence": 90,
  "evidence_paper": "Vaswani 2017",
  "evidence_section": "§3.1"
}
```

## 直交軸の組み合わせ

| provenance | conf | 意味 | 下流の扱い |
|-----------|------|------|-----------|
| EXTRACTED | 90+ | 直接抽出・高確度 | 信頼して利用 |
| EXTRACTED | 60-89 | 直接抽出だが解釈余地あり | 採用、ただし要再確認 |
| INFERRED | 75+ | 推論だが根拠が強い | 採用、notes 必読 |
| INFERRED | 40-74 | 弱い推論 | 採用前に追加検証 |
| AMBIGUOUS | * | 確定不能 | 集計から除外、ambig 列に残す |

confidence 50 未満の項目は `AMBIGUOUS` に降格するか、抽出自体を捨てる。

## 適用箇所

| 場所 | 適用方法 |
|------|---------|
| `paper-analysis/templates/paper-analysis-report.md` | Step 2 (Contradictions), Step 3 (Citation), Step 3.5 (Concept Relations), Step 5 (Gaps), Step 9 (Assumptions) のテーブルに provenance + conf 列を追加 |
| `compile-wiki/templates/concept-article.md` | 主要な知見セクションのキーポイントに `[provenance, conf=NN]` をインライン併記 |
| `research/SKILL.md` | citation merge 時に provenance を保持 |

## Anti-Patterns

| NG | 理由 |
|----|------|
| すべて `EXTRACTED` でラベリング | INFERRED/AMBIGUOUS を避けると誠実性が崩れ、provenance タグの意味が消滅 |
| `INFERRED` で confidence=95+ を多用 | 推論で 95+ は通常成立しない。根拠 5 つ以上揃わない限り 80 が上限の目安 |
| confidence のみ、provenance なし | 既存の confidence 表記の後退。直交軸で必ず併記 |
| AMBIGUOUS を抽出から除外する | 「不確定であること」を記録することに価値がある。集計からは除外、ただし表には残す |
| evidence_section を省略して EXTRACTED | EXTRACTED の根拠は必ず特定可能でなければならない |

## Chaining

- `paper-analysis/references/relation-extraction.md` — 概念ペア関係抽出での provenance 利用
- `paper-analysis/references/analysis-prompts.md` — 既存抽出 prompt への provenance 注入
- `compile-wiki/templates/concept-article.md` — wiki 概念記事への展開
