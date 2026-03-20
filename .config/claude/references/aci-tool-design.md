# ACI (Agent-Computer Interface) ツール設計原則

> API は人間向けに設計されている。Agent 向けのインターフェースは別の設計原則が必要。

## 3世代のツール設計

| 世代 | アプローチ | 問題 |
|------|-----------|------|
| 1st | API を直接ラップ | 粒度が細かすぎ、Agent が複数ツールを協調する必要 |
| 2nd | ACI: Agent の目標単位でツールを設計 | 1回の呼び出しで1つの目標を達成 |
| 3rd | 動的発見 + コード編排 + 実例付き | コンテキスト消費を最小化しつつ精度向上 |

## ツール定義のチェックリスト

### 1. 説明は路由条件として書く

- **Use when**: いつ使うか（具体的なシナリオ）
- **Don't use when**: いつ使わないか（類似ツールとの境界）
- **Output**: 何を返すか

```markdown
# Good
search_code: コードベース内のパターン検索。grep/rg の代替。
Use when: 関数定義、変数参照、パターンの出現箇所を探す時。
Don't use when: ファイル全体を読みたい時（→ read_file を使う）。
Output: マッチした行と行番号のリスト。

# Bad
search_code: コードを検索するツール。
```

### 2. パラメータで防錯する

- パラメータ名と description で制約を明示
- 相対パス vs 絶対パスの混乱を防ぐ
- enum で選択肢を制限できる場合は制限する

```markdown
# Good
absolute_path: "絶対パスで指定（例: /home/user/project/src/main.ts）"

# Bad
path: "ファイルパス"
```

### 3. エラーメッセージに修正提案を含める

```markdown
# Good
Error: ファイルが見つかりません: /src/main.ts
提案: 絶対パスを使用してください。候補: /home/user/project/src/main.ts

# Bad
Error: File not found
```

### 4. Tool Use Examples を付ける

各ツールに 1-5 個の実際の呼び出し例を添える。JSON Schema だけでは呼び出し方を伝えきれない。

```markdown
## Examples

### 関数定義を探す
input: { "pattern": "def calculate_", "path": "/project/src" }
output: "src/math.py:15: def calculate_tax(amount, rate):\n..."

### 特定ファイル内の TODO を探す
input: { "pattern": "TODO|FIXME", "path": "/project/src/api" }
output: "api/handler.py:42: # TODO: rate limiting\n..."
```

### 5. ツール数を抑制する

- 5 MCP サーバーで約 55,000 tokens のツール定義オーバーヘッド
- ツールが多すぎると単一ツールへの注意力が希釈される
- Shell で処理できるもの、静的知識で済むもの、Skill で代替できるものには新ツール不要
- **推奨上限: 同時 3 サーバー ≈ 33K tokens** — 詳細は `references/mcp-toolshed.md` を参照

### 6. 返回フォーマットをパラメータ化する

Agent が必要な粒度だけを取得できるようにする:

```markdown
response_format:
  - "summary": パスと1行要約のみ
  - "full": コード片を含む完全な結果
  - "count": マッチ数のみ
```

## デバッグ時の優先順位

Agent がツールを選び間違える場合、**まずツール定義を疑う**。多数の選択ミスはモデル能力ではなく説明の不正確さが原因。

1. ツール説明の Use when / Don't use when を見直す
2. 類似ツール間の境界を明確にする
3. パラメータの description を具体化する
4. 実例を追加する
