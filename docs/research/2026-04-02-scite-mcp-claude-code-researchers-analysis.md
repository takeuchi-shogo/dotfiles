---
source: "Claude Code for Researchers (Scite blog)"
date: 2026-04-02
status: integrated
---

## Source Summary

**主張**: Scite MCP は学術文献の Smart Citations（引用コンテキスト＝支持/反論/中立）と citation graph を AI ツールに統合し、研究ワークフローを peer-reviewed literature で根拠づける。Claude Code との組み合わせで予想外のユースケースが生まれている。

**手法**:
1. Bibliography verification — 参考文献一括検証（サポート率/矛盾フラグ/撤回状態）
2. Citation lineage tracing — 引用系譜の可視化
3. Research gap detection — 低サポート率/高矛盾率クレームからギャップ発見
4. Fact-checked lit review — 文献レビュー+即時検証
5. Contradiction report — 仮説への反証論文体系的収集
6. Citation confidence visualization — 引用数 vs サポート率プロット
7. Method validation — 最も検証された方法論の特定と実装
8. Statistical method reproduction — 論文メソッドのコード実装
9. Analytical choice sanity-check — 手法選択の学術的妥当性検証
10. Structured research brief — 構造化リサーチブリーフ生成

**根拠**: 90%の研究者が AI を週次使用。Smart Citations で引用の質を定量化。

**前提条件**: Scite サブスクリプションが必要（7日無料トライアルあり）。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Scite MCP 統合 | **Gap** | `.mcp.json` に未設定 |
| 2 | Bibliography verification | **Gap** | 引用品質の定量評価なし |
| 3 | Citation lineage tracing | **Gap** | alphaxiv は単一論文 lookup のみ |
| 4 | Research gap detection | **Partial** | `/research` でトピック調査可能だが引用品質シグナルなし |
| 5 | Fact-checked lit review | **Gap** | クレームごとの学術的検証手段なし |
| 6 | Contradiction report | **Gap** | 体系的な矛盾検出なし |
| 7 | Citation confidence visualization | **Gap** | 可視化なし |
| 8 | Method validation | **Partial** | `/research` で調査可能だが引用品質ランキングなし |
| 9 | Statistical method reproduction | **N/A** | Claude Code 自体がコード実装可能 |
| 10 | Structured research brief | **Partial** | `/research` でレポート生成可能だが Scite データなし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 1 | `/research` スキル | Web 検索ベース、引用品質シグナル未活用 | Scite MCP をデータソースとして統合 |
| 2 | `/alphaxiv-paper-lookup` | 単一論文取得のみ | Scite MCP と併用で信頼度定量評価可能 |

## Integration Decisions

- **採用**: Scite MCP 導入 + `/research` スキル強化
- **スキップ**: 個別ユースケースの専用スキル化（Scite MCP 導入で全て利用可能になるため不要）

## Plan

1. `.mcp.json` に Scite MCP サーバー追加 (`https://api.scite.ai/mcp`, HTTP)
2. `/research` スキルにモデル割り当てテーブル・ツール・Polish ステップで Scite 統合
3. 分析レポート保存

## Technical Notes

- **MCP エンドポイント**: `https://api.scite.ai/mcp` (Streamable HTTP, JSON-RPC 2.0)
- **認証**: OAuth 2.1 または API キー
- **ヘルスチェック**: `https://api.scite.ai/mcp/health`
- **主要 API**: 検索 (`/api_partner/search`), Smart Citations (`/tallies/{doi}`), 引用グラフ (`/api_partner/citations/citing/{doi}`)
