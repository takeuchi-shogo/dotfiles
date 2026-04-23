---
status: reference
last_reviewed: 2026-04-23
---

# Repair Routing Table

> 失敗・問題発生時に「何を直すか」を判定するためのルーティングテーブル。
> AutoEvolve の学習ループと接続して使用する。

## ルーティング原則

1. **症状ではなく原因のレイヤーを直す** — コードのバグはコードを直す。繰り返す判断ミスは reference/rule を直す
2. **修復は最小レイヤーで** — CLAUDE.md を直すのは最後の手段。まず references/ や rules/ で対応
3. **2回説明したら書き下ろせ** — 同じ知識をセッション横断で繰り返し説明している場合は codify する

## 障害種別 → 修復先マッピング

| 障害種別 | 症状例 | 修復先レイヤー | 修復アクション |
|---------|--------|---------------|--------------|
| **繰り返しコードエラー** | 同じパターンのバグを2回以上 | `references/error-fix-guides.md` | エラーパターン→修正マップを追加 |
| **判断ミスの繰り返し** | 不適切なツール選択、間違った戦略 | `references/situation-strategy-map.md` | 状況→戦略マップにエントリ追加 |
| **パイプライン違反** | ステップのスキップ、順序逆転 | `rules/common/*.md` | 違反パターンのルール追加 |
| **エージェント品質低下** | レビュー漏れ、不適切な委譲 | `agents/*.md` | エージェント定義のプロンプト改善 |
| **スキル手順の不備** | スキル実行時の失敗、手順漏れ | `skills/*/SKILL.md` | スキルの手順改善 |
| **Hook の誤検出/未検出** | false positive/negative の頻発 | `scripts/{policy,runtime}/*.py` | 検出ロジックの調整（慎重に） |
| **コア原則の矛盾** | 原則同士が衝突する場合 | `CLAUDE.md` | 原則の優先順位を明確化（最後の手段） |
| **ドメイン知識の不足** | 特定領域で繰り返し間違える | `references/task-archetypes/` | 領域別リファレンスの追加・更新 |
| **specification gaming** | テスト通過のためのハック | `scripts/policy/gaming-detector.py` | 検出パターンの追加 |
| **ドキュメント陳腐化** | 実装と乖離した参照 | 該当ドキュメント | `/check-health` で検出し直接更新 |

## 修復先の優先順位

```
高頻度・低リスク ← 優先的に修正
  1. references/ (error-fix-guides, situation-strategy-map, task-archetypes)
  2. rules/common/
  3. agents/
  4. skills/*/SKILL.md

低頻度・高リスク ← 慎重に修正
  5. scripts/ (hook ロジック)
  6. settings.json (hook 登録)
  7. CLAUDE.md (コア原則)
```

## AutoEvolve との接続

- `session-learner.py` が障害パターンを検出 → この表を参照して修復先を特定
- `continuous-learning` スキルが修復先に応じた改善提案を生成
- `/improve` 実行時にこの表に基づいて修復先の優先度を判断
