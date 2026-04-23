---
status: reference
last_reviewed: 2026-04-23
---

# Governance Levels — 4段階自律性

> AutoEvolve の自律性レベルを4段階で定義する。
> Spark 記事の段階的ガバナンス概念に基づく。

## 概要

カテゴリごとに自律性レベルを設定し、信頼度に応じて段階的に権限を拡大する。
デフォルトは Level 1（現在の動作を維持）。

## 4段階定義

| Level | 名前 | 説明 | 人間の関与 |
|-------|------|------|-----------|
| 0 | Observe | データ収集のみ。提案・変更なし | 不要 |
| 1 | Review | 提案を生成し、人間がレビュー・承認 | 全提案をレビュー |
| 2 | Auto-Merge | 低リスク変更を自動マージ。高リスクは Review | 高リスクのみレビュー |
| 3 | Trusted | 全変更を自動適用。異常時のみ通知 | 異常時のみ |

## デフォルト設定

全カテゴリのデフォルトは **Level 1 (Review)**。
これは現在の AutoEvolve の動作と同一であり、既存の振る舞いを変更しない。

## 昇格条件

| 遷移 | 条件 |
|------|------|
| Level 0 → 1 | カテゴリの初回データ収集が完了（5 セッション以上） |
| Level 1 → 2 | 直近 10 提案の承認率 > 80% かつ CQS > 0 |
| Level 2 → 3 | 直近 20 提案で revert ゼロ かつ 承認率 > 95%（opt-in 必須） |

## 降格条件

| 遷移 | 条件 |
|------|------|
| Level 3 → 2 | revert が 1 件でも発生 |
| Level 2 → 1 | 自動マージ後に品質メトリクスが discard 条件に該当 |
| Level 1 → 0 | ユーザーが明示的に無効化 |

## Level 3 の制約

Level 3 (Trusted) は以下の安全策を伴う:

- **opt-in 必須**: ユーザーが明示的に有効化しない限り到達しない
- **対象制限**: `references/error-fix-guides.md` への追記のみ（既存の自動マージ条件と同等）
- **即時降格**: revert 発生で即座に Level 2 に降格
- **監査ログ**: 全自動変更を `learnings/governance-audit.jsonl` に記録

## カテゴリ別設定

```
governance:
  errors: 1      # デフォルト
  quality: 1     # デフォルト
  agents: 1      # デフォルト
  skills: 1      # デフォルト
  evaluators: 1  # デフォルト
```

設定は `/improve` ダッシュボードで確認・変更可能。

## 既存ルールとの関係

- Rule 3（master 直接変更禁止）は全 Level で維持
- Rule 10（LLM 生成の修正は人間レビュー必須）は Level 2 以下で維持、Level 3 でも skills/agents は対象外
- 自動マージ条件（improve-policy.md L119-129）は Level 2 の低リスク判定基準として再利用
