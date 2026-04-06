---
source: https://zenn.dev/takuyanagai0213/articles/harness-engineering-intro-8months
date: 2026-04-06
status: integrated
---

## Source Summary

**主張**: ハーネスエンジニアリング（AIエージェントの周辺環境設計）は、モデル改善より出力品質への影響が大きい。CLAUDE.md 0行→420ファイルの8ヶ月実践記録から5原則を導出。

**手法**:
1. Progressive Disclosure — CLAUDE.md をエントリポイントに絞り、詳細は rules/docs/ に分離
2. 判断基準(Why) > 手順書(How) — Why があればエージェントが How を導出。ルール寿命が延びる
3. 共進化 — ハーネス作成過程で人間のドメイン理解も深化。一方的制御ではなく相互学習
4. Garbage Collection — 月次レビューで未使用削除。92→74個。使用頻度3段階分類（週1/月1/未使用）
5. 設計者と消費者の分離 — 全員が Skill 設計者になる必要はない。組織展開の鍵

**補助手法**:
- 「同じ指摘を2回した」をルール化トリガーに
- ペルソナ導入（レビュー指摘の出所を声のトーンで区別し可読性向上）
- Hooks（ガードレール）
- ライフサイクル全体マッピング（個別最適→全体最適）

**根拠**: 8ヶ月の実データ（コミット推移3→189/月、チーム波及効果）

**前提条件**: 日常的にAIエージェント（Claude Code等）を使用する開発者/チーム

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 設計者と消費者の分離 | N/A | 個人 dotfiles リポジトリ。チーム展開の文脈なし |
| 2 | ライフサイクル全体マッピング | Already | workflow-guide.md + CLAUDE.md ワークフローテーブルで全段階カバー |

### Already 項目の強化分析

| # | 既存の仕組み | 記事の知見 | 強化余地 |
|---|-------------|-----------|---------|
| 1 | Progressive Disclosure（ADR 0002、条件タグ） | CLAUDE.md 3000行→110行、glob match | 強化不要 — 条件タグで同等以上 |
| 2 | 判断基準 > 手順書（existence-vs-sufficiency ルール） | Why ベースでルール寿命延長 | 強化不要 — core_principles が Why ベース |
| 3 | 共進化（continuous-learning, eureka, analyze-tacit-knowledge） | ルール作成で人間も学ぶ | 強化不要 — Diff-Distill トリガーは記事にない独自機能 |
| 4 | Garbage Collection（skill-audit 5D品質スキャン） | 使用頻度3段階分類で棚卸し | **強化可能** — 使用頻度ベースの定期棚卸しが未実装 |
| 5 | 「2回指摘→ルール化」（continuous-learning トリガー） | 同じ指摘2回でルール化 | 強化不要 — 完全カバー |
| 6 | ペルソナ（persona スキル、4種の output-styles） | レビュー指摘の出所を声で区別 | **強化可能** — レビューアーエージェントに未適用 |
| 7 | Hooks（4層分離、agent-harness-contract） | リンター/セキュリティチェック | 強化不要 — 記事を大幅に超える体系 |
| 8 | ライフサイクル全体マッピング（workflow-guide.md） | 全段階マッピングで全体最適 | 強化不要 — 全段階定義済み |

## Integration Decisions

- **取り込み**: #4 使用頻度ベース棚卸し、#6 レビューアーペルソナ
- **スキップ**: 他6項目（既に同等以上の実装が存在）

## Plan

### 強化1: skill-audit に使用頻度棚卸しステップ追加 (S)

- `.config/claude/skills/skill-audit/SKILL.md` に Usage Tier Classification ステップを追加
- skill-executions.jsonl から過去30日の実行回数を集計
- Weekly(4+)/Monthly(1-3)/Unused(0) の3段階分類
- Unused を retire 候補としてレポート出力

### 強化2: レビューアーに声のトーンを付与 (S)

- `agents/reviewer-ma.md` に声のトーン定義を追加（簡潔・直接的）
- `agents/reviewer-mu.md` に声のトーン定義を追加（建設的・教育的）
- レビュー出力で指摘の出所が一目でわかるようにする
