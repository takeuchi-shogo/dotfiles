# Extraction Prompt - Stage 3

Stage 2 で検出した齟齬ポイントから暗黙知を抽出するためのプロンプトテンプレート。

## Prompt Template

以下の齟齬ポイントを分析し、ユーザーの暗黙知を抽出してください。

### Input

{detection_points}

### Instructions

各齟齬ポイントについて、以下の3つの観点で分析してください:

1. **何がズレていたか（gap）**: AIの出力と修正後を比較し、具体的なズレを特定
2. **なぜそう判断したか（knowledge）**: 修正指示の言葉から、ユーザーが持つ暗黙の判断基準を推測
3. **どのドメインか（domain）**: この知見が属するドメインカテゴリを分類

### Domain Categories

以下のカテゴリから選択するか、新しいカテゴリを提案してください:

- `content-creation/tone` — 文章のトーン・表現
- `content-creation/structure` — 文章の構成・構造
- `content-creation/audience` — 読者・受け手への配慮
- `communication/stakeholder` — ステークホルダーとのコミュニケーション
- `communication/information-filtering` — 情報の取捨選択
- `decision-making/priority` — 優先順位の判断
- `decision-making/boundary` — 自動化と人間判断の境界
- `workflow/process` — 作業プロセス・手順
- `quality/standard` — 品質基準・品質の肌感覚

### Grouping Rule

同一セッション内で同じ domain・同じ種類の修正が複数回出現した場合、1つの暗黙知としてグルーピングしてください。confidence はグループ内の最高値を採用し、すべての齟齬ポイントを evidence として含めてください。

### Output Format

```yaml
extracted_knowledge:
  - id: tk-{date}-{seq}
    gap: "{AIの出力とユーザーの期待のズレ}"
    user_correction: "{ユーザーの修正指示の要約}"
    knowledge: "{抽出された暗黙知}"
    domain: "{domain category}"
    confidence: {0.0-1.0}
    evidence:
      - signal_type: "{detection signal type}"
        context: "{齟齬ポイントの要約}"
```
