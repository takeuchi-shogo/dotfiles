# Data Analysis Patterns

CSV/スプレッドシートなどの構造化データを Claude Code で分析するためのプロンプトパターン集。

## 前提

Claude Code では Bash tool 経由で Python を実行できる。データ分析は以下の流れで行う:

1. データファイルを Read で確認（ヘッダー + 数行）
2. 分析方針を決定
3. Python スクリプトを Bash で実行
4. 結果を解釈してユーザーに報告

## パターン 1: パターン発見

**用途**: データの中に隠れた傾向・相関・クラスタを見つける

```
このデータを分析して、以下を教えてください:
1. 最も強い相関関係（正・負それぞれ上位3つ）
2. 明確なクラスタやグループ分け
3. 時系列トレンド（時間データがある場合）
4. 予想外のパターン（「これは変だ」と思うもの）

データ: [ファイルパスまたはデータ貼り付け]

分析は Python (pandas + matplotlib) で実行してください。
グラフは保存して表示してください。
```

### 実行例

```bash
python3 << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
print("=== 基本統計 ===")
print(df.describe())
print("\n=== 相関行列（上位） ===")
corr = df.select_dtypes(include='number').corr()
# 上三角のみ取得して絶対値ソート
import numpy as np
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
top_corr = corr.where(mask).stack().abs().sort_values(ascending=False).head(6)
print(top_corr)
EOF
```

## パターン 2: セグメント比較

**用途**: グループ間の違いを明確にする

```
以下のデータを [セグメント列] でグループ分けして比較してください:
1. 各セグメントの基本統計（平均、中央値、分散）
2. セグメント間の最大の違い
3. 統計的に有意な差があるか（t検定 or カイ二乗検定）
4. 各セグメントの「典型的なプロファイル」

データ: [ファイルパス]
セグメント列: [列名]
```

### 実行例

```bash
python3 << 'EOF'
import pandas as pd
from scipy import stats

df = pd.read_csv('data.csv')
segment_col = 'category'

for name, group in df.groupby(segment_col):
    print(f"\n=== {name} (n={len(group)}) ===")
    print(group.describe().round(2))
EOF
```

## パターン 3: 異常検出

**用途**: 外れ値・異常パターン・データ品質の問題を見つける

```
このデータの品質と異常値を調べてください:
1. 欠損値の分布（列ごとの欠損率）
2. 外れ値の検出（IQR法 + Zスコア）
3. データ型の不整合（数値列に文字列が混在など）
4. 重複行の有無
5. 各異常の「なぜこれが問題か」の説明

データ: [ファイルパス]
```

### 実行例

```bash
python3 << 'EOF'
import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

print("=== 欠損値 ===")
missing = df.isnull().sum()
print(missing[missing > 0].sort_values(ascending=False))

print("\n=== 外れ値 (IQR) ===")
for col in df.select_dtypes(include='number').columns:
    Q1, Q3 = df[col].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
    if len(outliers) > 0:
        print(f"{col}: {len(outliers)} outliers")

print(f"\n=== 重複行: {df.duplicated().sum()} ===")
EOF
```

## Tips

- **大きなファイル**: 100MB+ のファイルは先頭 1000 行で試してから全体に適用
- **日本語データ**: `pd.read_csv('file.csv', encoding='utf-8')` を明示
- **可視化**: matplotlib の日本語表示には `japanize-matplotlib` が必要
- **結果の保存**: 分析結果は `/note` で Obsidian に保存、または `/digest summarize` でブリーフ化
