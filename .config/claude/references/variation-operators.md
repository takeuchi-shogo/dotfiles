# Variation Operators — 段階的戦略切替ガイド

> EvoX メタ進化 (arXiv:2602.23413) の適応的変異選択に基づく。
> stagnation-detector.py が参照し、停滞時の提案メッセージに組み込む。

## フェーズ判定基準

| フェーズ | 条件 | 推奨オペレータ |
|---------|------|--------------|
| Early (探索) | セッション序盤・エラー少 | free-form variation |
| Mid (構造変更) | パターン確立・部分的成功 | structural variation |
| Late (洗練) | 大筋完成・微調整段階 | local refinement |
| Stagnation (停滞) | 閾値超過 | 1段階上に戻る |

## オペレータ定義

### free-form variation (探索的変異)

- 全く異なるアプローチ、ライブラリ、アーキテクチャを試す
- 例: 既存の正規表現パーサーを AST パーサーに切り替え
- 適用: gemini-research で代替案を調査、WebSearch で先行事例を検索

### structural variation (構造的変異)

- 有効だったパターンの再構成・組み合わせ
- 例: 動作する関数をモジュールに分離、インターフェース変更
- 適用: codex-debugger で構造的な根本原因分析

### local refinement (局所洗練)

- 既存コードの微調整、パラメータ変更、エッジケース対応
- 例: 閾値の調整、条件分岐の追加
- 適用: 直接編集で対応

## 停滞時のエスカレーション

1. local refinement で停滞 → structural variation に切替
2. structural variation で停滞 → free-form variation に切替
3. free-form variation で停滞 → 人間に判断を委譲
