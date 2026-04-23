---
status: reference
last_reviewed: 2026-04-23
---

# TELOS → AutoEvolve Outcome Mapping

TELOS 目標と AutoEvolve 改善方向の接続を定義する。
proxy indicator は目標そのものではない — 定期的に妥当性を再評価すること。

## 目標→シグナルマッピング

| 期間 | TELOS 目標 | 観測シグナル (proxy) | データソース | 計測方法 |
|------|-----------|---------------------|-------------|---------|
| 短期 | ハーネス安定化・品質向上 | session clean_success 率 | session-metrics.jsonl | 自動集計 |
| 短期 | ハーネス安定化・品質向上 | proposal revert 率 | proposals.jsonl | 自動集計 |
| 短期 | ハーネス安定化・品質向上 | /improve cycle time | improve-history.jsonl | 自動集計 |
| 短期 | 未統合プラン消化 | plans/ の Wave 完了数 | docs/plans/*.md | 手動確認 |
| 中期 | プロダクト開発 | プロダクトリポジトリのコミット頻度 | 外部リポジトリ | 手動報告 (/timekeeper) |
| 中期 | Go/TS エキスパート到達 | 学習セッション頻度・深度 | セッション履歴 | 手動報告 (/timekeeper) |
| 中期 | Rust 実務投入 | Rust コード実装セッション | セッション履歴 | 手動報告 (/timekeeper) |
| 長期 | 持続的収益 | プロダクトのユーザー数・収益 | 外部データ | 手動報告 |
| 長期 | コミュニティ還元 | 公開記事・OSS 貢献 | GitHub/ブログ | 手動報告 |

## AutoEvolve category → TELOS 目標マッピング

AutoEvolve proposals の category は以下の TELOS 目標に紐づく:

| proposals category | TELOS 目標 | alignment |
|-------------------|-----------|-----------|
| errors | ハーネス安定化 | high |
| quality | ハーネス安定化 | high |
| agents | ハーネス安定化 | high |
| skills | ハーネス安定化 | high |
| evaluators | ハーネス安定化 | high |
| comprehension | ハーネス安定化 | medium |
| review-comments | ハーネス安定化 | medium |
| output-diff | ハーネス安定化 | medium |

> 注: 現状の AutoEvolve はハーネス改善に閉じているため、全 category が短期目標に紐づく。
> 中期・長期目標への貢献は /morning や /timekeeper での手動振り返りで評価する。

## TELOS Alignment 判定ルール

/improve の REPORT で proposals に alignment ラベルを付与する:

- **high**: 現在の短期目標の主要シグナルに直接影響する提案
- **medium**: 間接的に貢献する提案（comprehension 改善 → 品質向上 等）
- **low**: 現在の TELOS 目標との関連が薄い提案

> low が過半数を占める場合、改善方向が TELOS 目標から乖離している可能性がある。

## Anti-Goodhart 注記

- proxy の改善は目標達成を保証しない（clean_success 率 100% ≠ ハーネスが完璧）
- proxy 自体の妥当性は /timekeeper の Q7-Q8（信念の変化・未解決の問い）で定期的に問い直す
- 自動計測可能な proxy に偏ると、手動報告ベースの中期・長期目標が軽視される
- TELOS 目標が更新されたら、このマッピング表も更新すること
