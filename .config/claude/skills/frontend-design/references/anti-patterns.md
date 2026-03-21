# Frontend Design Anti-Patterns

## Typography
- **NG**: Inter, Roboto, Arial をデフォルトで使用
- **OK**: プロジェクトのトーンに合ったフォント選定

## Colors
- **NG**: 紫グラデーション（AI っぽすぎる）
- **NG**: 彩度100%の原色
- **OK**: トーンに合った制限されたパレット

## Layout
- **NG**: 全要素にボーダーラディウス
- **NG**: 過度なシャドウ
- **NG**: ヒーローで generic SaaS card grid を最初の印象にする
- **NG**: brand が弱く、nav を消すと別ブランドにも見える
- **NG**: dashboard を stacked cards だけで構成する
- **OK**: 意図的な空白と階層

## Motion
- **NG**: 無意味なアニメーション
- **NG**: 300ms超のトランジション
- **OK**: 状態変化を伝える最小限のモーション

## General
- **NG**: "AI が作りました" 感のあるデザイン
- **NG**: section ごとの役割が曖昧で、同じ mood statement を繰り返す
- **NG**: real content がないまま placeholder の勢いで組み切る
- **OK**: 意図的で個性のあるデザイン
