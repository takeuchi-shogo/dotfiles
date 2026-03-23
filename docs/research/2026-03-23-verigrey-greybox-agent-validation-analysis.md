---
source: "VeriGrey: Greybox Agent Validation (arXiv:2603.17639)"
date: 2026-03-23
status: implemented
authors: Yuntong Zhang, Sungmin Kang, Ruijie Meng, Marcel Böhme, Abhik Roychoudhury
---

## Source Summary

### 主張

LLM エージェントに対する間接プロンプトインジェクション脆弱性を、ツール呼び出しシーケンスをカバレッジ指標としたグレーボックスファジングで効率的に発見できる。

### 手法

1. **ツール呼び出しシーケンスをフィードバック**: ブランチカバレッジの代わりにツール呼び出し系列を行動カバレッジとして使用
2. **コンテキストブリッジング変異**: 悪意あるタスクをユーザーの本来タスクに文脈接続する変異演算子
3. **エネルギー割り当て**: 新ツール・新遷移・新シーケンスの3指標で変異回数を決定
4. **反復的改良**: LLM を変異演算子として使い、失敗理由を推論して次のプロンプトを生成

### 根拠（実験データ）

| ベンチマーク | VeriGrey ITSR | ブラックボックス ITSR | 差分 |
|-------------|--------------|---------------------|------|
| AgentDojo (GPT-4.1) | 70.7% | 37.7% | +33.0pp |
| AgentDojo (Gemini-2.5-Flash) | 47.4% | 36.8% | +10.6pp |
| AgentDojo (Qwen-3 235B) | 81.7% | 67.6% | +14.1pp |
| Gemini CLI (10 tasks) | 90% | 60% | +30pp |
| OpenClaw + Kimi-K2.5 | 100% (10/10) | 10% (1/10) | +90pp |
| OpenClaw + Opus 4.6 | 90% (9/10) | 10% (1/10) | +80pp |

アブレーション: コンテキストブリッジング除去で -25.8pp、フィードバック除去で -11.1pp（GPT-4.1）。
防御比較: Tool Filter が ITSR を最も下げつつ UTSR への影響が最小（85.0%→81.7%）。

### 前提条件

- エージェントのソースコードにアクセスしてツール計装が必要（完全ブラックボックスでは不可）
- 単一セッション限定（メモリポイズニング・マルチセッション攻撃は対象外）
- インジェクション成功の判定オラクルは手動設計
- 変異に LLM API コストが発生（1キャンペーン最大100エージェント実行）

## Gap Analysis

| # | VeriGrey の知見 | 判定 | 現状 | 差分 |
|---|----------------|------|------|------|
| 1 | Task-scoped Tool Filter | **Partial** | `mcp-audit.py` skill-level MCP scoping (advisory), `settings.json` deny rules | タスク文脈に応じた動的ホワイトリスト未実装 |
| 2 | コンテキストブリッジング攻撃検出 | **Gap** | `prompt-injection-detector.py` は技術パターンのみ | 自然言語による文脈接続型インジェクション未検出 |
| 3 | SKILL.md の3攻撃パターン | **Partial** | `skill-security-scan.py` G1+G2、`security-reviewer` .claude/ 検査 | 自然ステップ偽装・自律性強調・偽使用例が未検出 |
| 4 | ツール呼び出しシーケンス異常検出 | **Partial** | `mcp-audit.py` ログ、`stagnation-detector.py` パターン反復 | 異常シーケンス検出なし |
| 5 | MCP レスポンス内容検査 | **Gap** | `mcp-audit.py` は入力監査のみ | MCP サーバー出力のインジェクション検査なし |

## Integration Decisions

5項目すべてを統合。優先順位: #3 > #2 > #5 > #1 > #4

## Plan

See `docs/plans/2026-03-23-verigrey-integration.md`
