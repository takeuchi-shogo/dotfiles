# Gemini Context Preparation Guide

## 1M コンテキストの活用

### 含めるべき
- ソースコード（対象モジュール全体）
- 関連する設定ファイル
- テストコード
- ドキュメント（spec, README）

### 除外すべき
- node_modules/, vendor/, .git/
- バイナリファイル
- 生成ファイル（*.min.js, *.map）
- 大きなデータファイル（CSV, JSON > 1MB）

## Approval Modes

| Mode | 用途 |
|------|------|
| plan | Read-only 分析（デフォルト） |
| yolo | ファイル操作を含む実行 |

## Output Routing

- 分析結果: `docs/research/` に保存
- コード提案: diff 形式で出力
