---
source: |
  - https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://cognition.ai/blog/dont-build-multi-agents
date: 2026-03-23
status: integrated
---

## Source Summary

3つのソースからマルチエージェントシステムの設計指針を統合分析した。

### Google Research: "Towards a Science of Scaling Agent Systems"

**主張**: マルチエージェントの効果はタスク特性に依存する。一律に「増やせば賢くなる」は誤り。

**定量データ**:
- 独立並列（通信なし）: エラー **17.2倍** 増幅
- 中央集権型: エラー **4.4倍** に抑制
- 並列可能タスク（Finance-Agent）: **+81%** 改善
- 逐次推論タスク（PlanCraft）: **-39〜70%** 劣化
- 予測モデル精度: R^2 = 0.513、最適戦略の正答率 87%

**ベンチマーク**: Finance-Agent, BrowseComp-Plus, PlanCraft, Workbench の4種。

### Anthropic: "Building Effective Agents"

**主張**: 最もシンプルなアプローチから始めよ。最も成功した実装は複雑なフレームワークを使っていなかった。

**手法**: Orchestrator-Workers, Prompt Chaining, Routing 等のパターンを定性的に解説。

**注意**: 具体的なベンチマーク数値や性能比較は含まれていない。設計ガイダンスのみ。

### Cognition AI: "Don't Build Multi-Agents"

**主張**: マルチエージェントは脆弱。2025年時点ではシングルエージェントが信頼性で優る。

**推奨**: シングルスレッド線形実行 + 会話履歴の圧縮。サブエージェントは「明確に定義された質問」にのみ。

**注意**: 定量データなし。Cognition は Devin（シングルエージェント製品）の開発元であり、ポジショントークの側面がある。

## Fact Check (投稿の主張に対する検証)

| 主張 | 判定 | 詳細 |
|------|------|------|
| エラー17.2倍増幅 | 正確 | Google Research に明記 |
| Anthropicの90.2%改善 | 出典不一致 | Anthropic記事に数値なし。Google側に80.9%あり、混同の可能性 |
| トークン消費15倍 | 出典不明 | 3ソースのいずれにも記載なし |
| Cognition「Don't Build Multi-Agents」 | 正確 | タイトル・内容ともに一致 |
| 「業界の結論: シングルから始めよ」 | 過度に単純化 | Google の結論はタスク特性依存 |

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | シングルエージェントファースト | Already | subagent-delegation-guide.md に明記済み |
| 2 | コンテキスト境界で分割 | Already | 情報の重複/ハンドオフコスト/発見の影響で判定 |
| 3 | 中央集権型オーケストレーション | Already | /review の親統合モデル |
| 4 | Depth-1 ルール | Already | agency-safety-framework.md |
| 5 | タスク特性ベースの戦略選択 | Partial -> Integrated | Task Parallelizability Gate を追加 |
| 6 | エラー増幅の検出・抑制 | Partial -> Integrated | Error Amplification Guard を追加 |
| 7 | 会話履歴の構造化圧縮 | Partial | suggest-compact.js + context pressure で部分対応。構造化圧縮は未実装 |
| 8 | マルチエージェントのコスト意識 | Gap -> Integrated | 「分割のコスト」セクションを追加 |

## Integration Decisions

- #5 統合: `subagent-delegation-guide.md` に Task Parallelizability Gate を追加
- #6 統合: `agency-safety-framework.md` に Error Amplification Guard を追加
- #8 統合: `subagent-delegation-guide.md` に「分割のコスト」セクションを追加
- #7 スキップ: 現状の suggest-compact.js + context pressure levels で実用上十分。構造化圧縮は将来課題として保留
