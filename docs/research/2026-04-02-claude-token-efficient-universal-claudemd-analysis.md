---
source: https://github.com/drona23/claude-token-efficient
date: 2026-04-02
status: skipped
---

## Source Summary

**主張**: 8行の Universal CLAUDE.md で出力トークンを 63% 削減（465→170 words）
**手法**: preamble 排除、簡潔出力、targeted edit、再読み込み禁止、完了前検証、sycophancy 排除、シンプル設計、ユーザー指示優先。coding/agents/analysis/benchmark の 4 プロファイル付き
**根拠**: 5 プロンプトのベンチマーク。n=5、再現なし、モデル/温度/試行回数未記載、統計的検定なし。"directional indicator only" と著者自身が認めている
**前提条件**: 出力量が多い反復タスクでのみ net savings。短いやり取りでは CLAUDE.md の入力トークン増でマイナス

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Eliminate preamble | N/A | CC システムプロンプトに既存 |
| 2 | Concise output | N/A | CC システムプロンプトに既存 |
| 3 | Targeted edits | Already (強化不要) | `最小インパクト` + CC システムプロンプト |
| 4 | Single read-through | N/A | CC 内部キャッシュで対応。過制約リスク |
| 5 | Validation before completion | Already (強化不要) | completion-gate + Review Gate |
| 6 | No sycophantic closing | N/A | CC システムプロンプト + 認知バイアス対策済み |
| 7 | Simple solutions | Already (強化不要) | KISS + YAGNI + 3回ルール |
| 8 | User instruction priority | Already (強化不要) | CC 標準動作 |
| 9 | Code first, explanation after | Partial | `修正時の3点説明` はあるが出力順序の明示なし |
| 10 | Plain formatting | Gap | em dash / smart quotes 禁止ルールなし |
| 11 | No narration | N/A | サブエージェントは独立コンテキスト |
| 12 | Hallucination prevention | Already (強化不要) | TVA 4層信頼検証 |
| 13 | Structured-only output | N/A | エージェント定義で個別制御 |

**13 手法中: Already 5 / N/A 6 / Partial 1 / Gap 1**

## Integration Decisions

全項目スキップ。理由:
- Gap/Partial の 2 件（コード先出力順序、plain formatting）は効果が小さく IFScale コスト（指示あたり +1-2% 推論オーバーヘッド）に見合わない
- 既存セットアップが CC システムプロンプト + core_principles + hooks/skills で同等以上をカバー済み
- ベンチマークの方法論が弱く（n=5、再現なし）、63% 削減の主張を根拠に設定変更する合理性がない
