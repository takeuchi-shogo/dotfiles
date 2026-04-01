---
name: excalidraw
description: >
  テキスト説明から Excalidraw 互換 JSON ダイアグラムを生成し、.excalidraw ファイルとして保存する。
  フローチャート、アーキテクチャ図、マインドマップ、デシジョンツリーに対応。
  Obsidian Excalidraw プラグインでそのまま開ける。
  Triggers: 'Excalidraw', 'ダイアグラム生成', '図を描いて', 'アーキテクチャ図', 'フローチャート', 'マインドマップ'.
  Do NOT use for: スクリーンショット取得 (use Playwright)、AI画像生成 (use /nano-banana)、Mermaid テキスト図。
allowed-tools: Read, Write, Bash, Glob, Grep, Edit
user-invocable: true
argument-hint: [description] | --type flowchart|architecture|mindmap|decision-tree
metadata:
  pattern: generator
  category: generation
  version: 1.0.0
---

# /excalidraw — Excalidraw Diagram Generator

テキスト説明から Excalidraw JSON ダイアグラムを生成し、`.excalidraw` ファイルとして保存する。
Obsidian Excalidraw プラグインで直接開いて編集可能。

## Workflow

### Step 1: 意図の把握

ユーザーの説明から以下を特定する:

1. **図の種類**: flowchart / architecture / mindmap / decision-tree / sequence / free
2. **ノード一覧**: 各ノードのラベルと種類（process/decision/start-end/data）
3. **接続関係**: ノード間の矢印とラベル
4. **方向**: top-to-bottom (TB) / left-to-right (LR)

不明な場合はユーザーに1回だけ確認。推測できるなら確認不要。

### Step 2: レイアウト計算

ノード配置を計算する。**手動で座標を決定する** — ライブラリは使わない。

**グリッドベースレイアウト**:
- 1セルのサイズ: 250w x 150h（余白含む）
- ノード間の最小ギャップ: 80px
- TB の場合: 行ごとにノードを配置、中央揃え
- LR の場合: 列ごとにノードを配置

**ノードサイズの決定**:
- テキスト長 × 10 + 40 = 幅の目安（最小 120px、最大 300px）
- 高さ: 1行なら 60px、2行なら 80px、3行以上なら 100px

**配置ルール**:
- デシジョンノード（diamond）は分岐先を左右に展開
- マインドマップは中央ノードから放射状に配置
- 20ノード超えの場合はグループに分割し、グループ間に 120px の余白

### Step 3: JSON 生成

`references/element-schema.md` を参照して有効な Excalidraw JSON を生成する。

**必須チェック**:
- [ ] 全要素に一意な `id` がある（`node-1`, `arrow-1` 等のプレフィックス形式）
- [ ] 全要素に `seed` がある（ランダムな整数、各要素で異なる値）
- [ ] テキスト要素は対応する図形の中央に配置されている
- [ ] 矢印の `startBinding` / `endBinding` が正しいノード ID を参照している
- [ ] `points` 配列の最初は `[0, 0]`、最後は相対座標

### Step 4: ファイル保存

```
{プロジェクトルート}/{ファイル名}.excalidraw
```

- ファイル名はユーザー指定、未指定なら図の内容から推測（例: `auth-flow.excalidraw`）
- Obsidian Vault への保存を求められた場合は Obsidian MCP の `write_note` を使用

保存後、ユーザーに以下を伝える:
- ファイルパス
- ノード数と接続数
- 「excalidraw.com にペーストするか、Obsidian で開いてください」

## 図の種類別ガイド

### Flowchart
- Start/End: `ellipse` + 緑/赤の背景
- Process: `rectangle`
- Decision: `diamond` + Yes/No ラベル付き矢印
- 方向: デフォルト TB

### Architecture
- コンポーネント: `rectangle` + タイトルテキスト
- 外部システム: `rectangle` + dashed stroke
- データストア: `rectangle` + 下線付きテキスト
- グルーピング: `rectangle`（大きめ、薄い背景色）でコンテナ表現
- 方向: デフォルト LR

### Mind Map
- 中央ノード: `ellipse`（大きめ、強い背景色）
- ブランチ: `rectangle`（丸角）
- リーフ: `rectangle`（小さめ、薄い背景色）
- 接続: `line`（矢印なし）
- 配置: 放射状、12時方向から時計回り

### Decision Tree
- 質問: `diamond`
- 結果: `rectangle` + 背景色で良/悪を表現
- 接続: `arrow` + 条件ラベル

## カラーパレット

| 用途 | 色 |
|------|-----|
| プライマリノード | `#a5d8ff` (淡青) |
| セカンダリノード | `#d0bfff` (淡紫) |
| 成功/開始 | `#b2f2bb` (淡緑) |
| 警告/判断 | `#ffec99` (淡黄) |
| エラー/終了 | `#ffc9c9` (淡赤) |
| コンテナ/グループ | `#f8f9fa` (淡灰) |
| ストローク | `#1e1e1e` (ほぼ黒) |
| 矢印 | `#495057` (暗灰) |

## Anti-Patterns

| # | Don't | Do Instead |
|---|-------|------------|
| 1 | ノードを重ねて配置する | グリッドベースで最小80pxの間隔を確保 |
| 2 | テキストを図形の外に配置する | `containerId` で図形内にバインド |
| 3 | 全ノードを同じ色にする | 種類別にカラーパレットを適用 |
| 4 | 矢印の binding を省略する | `startBinding`/`endBinding` で必ず接続 |
| 5 | seed を固定値にする | 各要素にランダムな seed を割り当て（手書き風の多様性） |
| 6 | 50ノード超えの巨大な図を1ファイルに | サブシステムごとに分割して複数ファイル |

## Skill Assets

- `references/element-schema.md` — Excalidraw JSON の要素定義とプロパティ一覧
