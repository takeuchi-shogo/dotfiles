# Excalidraw Element Schema Reference

## Root Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": {
    "gridSize": 20,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

## Common Element Properties

全要素に必須:

```json
{
  "id": "unique-id",
  "type": "rectangle|ellipse|diamond|arrow|line|text",
  "x": 100,
  "y": 200,
  "width": 200,
  "height": 100,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "hachure",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "seed": 12345,
  "version": 1,
  "versionNonce": 1,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "updated": 1700000000000,
  "link": null,
  "locked": false
}
```

### Property Details

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | 一意な識別子。`node-1`, `arrow-1` 等 |
| `seed` | number | 手書き風レンダリングのシード。各要素で異なる値 |
| `roughness` | 0\|1\|2 | 0=シャープ、1=手書き風(default)、2=ラフ |
| `fillStyle` | string | `hachure`\|`cross-hatch`\|`solid` |
| `strokeStyle` | string | `solid`\|`dashed`\|`dotted` |
| `strokeWidth` | number | 線の太さ。1=thin, 2=normal(default), 4=bold |
| `opacity` | number | 0-100 |

## Shape Elements

### Rectangle

```json
{
  "id": "rect-1",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "roundness": { "type": 3 },
  "boundElements": [
    { "id": "text-1", "type": "text" },
    { "id": "arrow-1", "type": "arrow" }
  ]
}
```

- `roundness`: `null`(角丸なし)、`{ "type": 3 }`(角丸あり)

### Ellipse

```json
{
  "id": "ellipse-1",
  "type": "ellipse",
  "x": 100,
  "y": 100,
  "width": 160,
  "height": 80
}
```

### Diamond

```json
{
  "id": "diamond-1",
  "type": "diamond",
  "x": 100,
  "y": 100,
  "width": 160,
  "height": 120
}
```

## Text Elements

### Standalone Text

```json
{
  "id": "text-standalone",
  "type": "text",
  "x": 100,
  "y": 100,
  "width": 80,
  "height": 25,
  "text": "Label",
  "fontSize": 20,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": null,
  "originalText": "Label",
  "autoResize": true
}
```

### Bound Text (Shape 内のテキスト)

```json
{
  "id": "text-in-rect",
  "type": "text",
  "x": 130,
  "y": 125,
  "width": 140,
  "height": 25,
  "text": "Process",
  "fontSize": 20,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "rect-1",
  "originalText": "Process",
  "autoResize": true
}
```

**重要**: `containerId` で親図形を参照する。親図形の `boundElements` にこのテキストの `id` を含める。

### Font Family

| Value | Font |
|-------|------|
| 1 | Virgil (手書き風、デフォルト) |
| 2 | Helvetica |
| 3 | Cascadia (等幅) |
| 5 | Excalifont (新手書き風) |

## Arrow / Line Elements

### Arrow

```json
{
  "id": "arrow-1",
  "type": "arrow",
  "x": 300,
  "y": 140,
  "width": 100,
  "height": 0,
  "points": [[0, 0], [100, 0]],
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "startBinding": {
    "elementId": "rect-1",
    "focus": 0,
    "gap": 1,
    "fixedPoint": null
  },
  "endBinding": {
    "elementId": "rect-2",
    "focus": 0,
    "gap": 1,
    "fixedPoint": null
  }
}
```

### Binding Properties

| Property | Type | Description |
|----------|------|-------------|
| `elementId` | string | 接続先の要素 ID |
| `focus` | number | -1〜1。0=中央、負=上/左寄り、正=下/右寄り |
| `gap` | number | 要素境界からの距離 |

### Arrow with Label

矢印にラベルを付けるには、テキスト要素を矢印の中間点に配置し、`containerId` で矢印を参照:

```json
{
  "id": "arrow-label-1",
  "type": "text",
  "x": 330,
  "y": 120,
  "text": "Yes",
  "fontSize": 16,
  "containerId": "arrow-1",
  "originalText": "Yes"
}
```

矢印の `boundElements` にラベルのテキスト要素を追加:

```json
{
  "id": "arrow-1",
  "boundElements": [{ "id": "arrow-label-1", "type": "text" }]
}
```

### Points Array

- 最初の点は常に `[0, 0]`
- 後続の点は開始点からの**相対座標**
- 直線: `[[0, 0], [dx, dy]]`
- 折れ線: `[[0, 0], [dx1, dy1], [dx2, dy2]]`

**方向別の典型的な points**:
- 右向き: `[[0, 0], [100, 0]]`
- 下向き: `[[0, 0], [0, 100]]`
- L字(右→下): `[[0, 0], [100, 0], [100, 80]]`

## Bidirectional Binding

矢印と図形の接続は**双方向**で設定が必要:

1. **矢印側**: `startBinding.elementId` / `endBinding.elementId` に図形の ID を設定
2. **図形側**: `boundElements` 配列に矢印の `{ "id": "arrow-id", "type": "arrow" }` を追加

```json
// 図形
{
  "id": "rect-1",
  "type": "rectangle",
  "boundElements": [
    { "id": "text-1", "type": "text" },
    { "id": "arrow-1", "type": "arrow" }
  ]
}

// 矢印
{
  "id": "arrow-1",
  "type": "arrow",
  "startBinding": { "elementId": "rect-1", "focus": 0, "gap": 1 },
  "endBinding": { "elementId": "rect-2", "focus": 0, "gap": 1 }
}
```

## Complete Example: 3-Node Flowchart

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "start",
      "type": "ellipse",
      "x": 100,
      "y": 50,
      "width": 140,
      "height": 60,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 1001,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": [
        { "id": "start-text", "type": "text" },
        { "id": "arrow-1", "type": "arrow" }
      ],
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "roundness": null,
      "angle": 0
    },
    {
      "id": "start-text",
      "type": "text",
      "x": 135,
      "y": 67,
      "width": 70,
      "height": 25,
      "text": "Start",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "start",
      "originalText": "Start",
      "autoResize": true,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 1002,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "process",
      "type": "rectangle",
      "x": 95,
      "y": 200,
      "width": 150,
      "height": 70,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 2001,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": [
        { "id": "process-text", "type": "text" },
        { "id": "arrow-1", "type": "arrow" },
        { "id": "arrow-2", "type": "arrow" }
      ],
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "roundness": { "type": 3 },
      "angle": 0
    },
    {
      "id": "process-text",
      "type": "text",
      "x": 120,
      "y": 222,
      "width": 100,
      "height": 25,
      "text": "Process",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "process",
      "originalText": "Process",
      "autoResize": true,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 2002,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "end",
      "type": "ellipse",
      "x": 100,
      "y": 370,
      "width": 140,
      "height": 60,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 3001,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": [
        { "id": "end-text", "type": "text" },
        { "id": "arrow-2", "type": "arrow" }
      ],
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "roundness": null,
      "angle": 0
    },
    {
      "id": "end-text",
      "type": "text",
      "x": 140,
      "y": 387,
      "width": 60,
      "height": 25,
      "text": "End",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "end",
      "originalText": "End",
      "autoResize": true,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 3002,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "arrow-1",
      "type": "arrow",
      "x": 170,
      "y": 110,
      "width": 0,
      "height": 90,
      "points": [[0, 0], [0, 90]],
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "startBinding": { "elementId": "start", "focus": 0, "gap": 1, "fixedPoint": null },
      "endBinding": { "elementId": "process", "focus": 0, "gap": 1, "fixedPoint": null },
      "strokeColor": "#495057",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 4001,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "roundness": { "type": 2 },
      "angle": 0
    },
    {
      "id": "arrow-2",
      "type": "arrow",
      "x": 170,
      "y": 270,
      "width": 0,
      "height": 100,
      "points": [[0, 0], [0, 100]],
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "startBinding": { "elementId": "process", "focus": 0, "gap": 1, "fixedPoint": null },
      "endBinding": { "elementId": "end", "focus": 0, "gap": 1, "fixedPoint": null },
      "strokeColor": "#495057",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "seed": 4002,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false,
      "roundness": { "type": 2 },
      "angle": 0
    }
  ],
  "appState": {
    "gridSize": 20,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```
