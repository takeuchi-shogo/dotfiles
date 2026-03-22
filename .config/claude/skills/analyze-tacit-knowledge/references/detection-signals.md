# Detection Signals - Stage 2

セッションログから認識齟齬を検出するためのシグナル定義。

## Signal Categories

### 1. 明示的修正指示 (Explicit Correction)

ユーザーが直接的にAIの出力を否定・修正する発言。

**検出キーワード:**
- 否定: 「違う」「そうじゃない」「そうではなく」「ではなくて」「じゃなくて」
- 修正要求: 「〜に変えて」「〜にして」「〜に修正して」「直して」「やり直して」
- 不一致: 「イメージと違う」「求めてるのは」「そういうことじゃない」

**confidence:** 0.9（明示的修正は暗黙知の直接的な表出）

### 2. やり直し (Redo)

同一ファイルへの複数回 Edit がユーザーフィードバックを挟んで発生。

**検出方法:**
- 同一ファイルパスに対する Edit/Write tool_use が2回以上
- 間にユーザーメッセージ（type: "user", content: string）が存在
- tool_result ではなく、ユーザーの自発的なメッセージであること

**confidence:** 0.8

### 3. 方針転換 (Direction Change)

ユーザーがアプローチの変更を指示。

**検出キーワード:**
- 「やっぱり」「こっちのアプローチで」「方針変更」「別の方法で」
- 「前のやつに戻して」「最初の案で」

**confidence:** 0.7（方針転換は暗黙知の場合もあるが、単なる試行錯誤の場合もある）

### 4. 不満・苛立ち (Frustration)

ユーザーが繰り返しの修正に苛立ちを示す。

**検出キーワード:**
- 「毎回」「何度も言ってる」「さっきも言った」「同じことを」
- 「いつも」「また同じ」

**confidence:** 0.95（繰り返しの修正は高確度で暗黙知のギャップを示す）

### 5. 早期中断 (Early Interruption)

ユーザーが assistant の出力途中で割り込み。

**検出方法:**
- assistant メッセージの直後に、tool_result ではないユーザーメッセージ
- assistant メッセージの stop_reason が "end_turn" ではない、または出力が短い

**confidence:** 0.6（中断の理由は様々なので低め）

### 6. 追加説明 (Supplementary Explanation)

ユーザーが長い補足説明を追加。AIの前提理解が不足していた兆候。

**検出方法:**
- ユーザーメッセージの文字数が 200 文字以上
- 直前に assistant の出力がある（初回の指示ではない）
- メッセージ内に背景説明、前提条件、コンテキストの補足が含まれる

**confidence:** 0.65

## Detection Output Format

各検出ポイントは以下の構造で Stage 3 に渡す:

```yaml
- signal_type: "explicit_correction"
  confidence: 0.9
  context:
    before: "assistant の直前の出力（関連部分を抜粋）"
    user_message: "ユーザーの修正指示（全文）"
    after: "修正後の assistant の出力（あれば）"
  session_id: "session-xxx"
  timestamp: "2026-03-22T10:30:00Z"
```
