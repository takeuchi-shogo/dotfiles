---
status: reference
last_reviewed: 2026-04-23
---

# Managed Agents Scheduling — 移行検討リファレンス

## 現在のスケジュール実行基盤

| タスク | 基盤 | スケジュール | ファイル |
|--------|------|-------------|---------|
| Daily Health Check | launchd plist | 毎日 21:07 | `scripts/runtime/com.claude.daily-health-check.plist` |
| Patrol Agent | launchd plist | 5分ごと | `scripts/runtime/com.claude.patrol-agent.plist` |
| AutoEvolve | cron | 毎日 03:00 | `scripts/runtime/autoevolve-runner.sh` |

## Managed Agents API での代替

```
# CLI でスケジュール作成（概念）
claude agents create --name "daily-health" --model claude-sonnet-4-6 --system-prompt "..."
claude triggers create --agent-id $AGENT_ID --schedule "0 21 * * *"
```

## 移行候補の評価

| タスク | 移行推奨度 | 理由 |
|--------|-----------|------|
| Daily Health Check | **高** | クラウド実行で Mac スリープ時も確実に実行。コスト低い（短時間） |
| AutoEvolve | **中** | 長時間実行の可能性あり → コスト管理が必要。ただし信頼性向上 |
| Patrol Agent | **低** | 5分間隔はコールドスタート（3-8秒）の影響が大きい。ローカル維持が合理的 |

## コスト設計指針

### ハード予算キャップ（必須）

- **短時間タスク**（Health Check 等）: $1/実行 上限
- **中時間タスク**（AutoEvolve 等）: $5/実行 上限
- **長時間タスク**: $20/実行 上限、かつ段階実行で checkpoint

### コスト見積もり

| タスク | 推定時間 | 推定コスト/回 | 月額概算 |
|--------|---------|-------------|---------|
| Daily Health Check | 2-5分 | $0.10-0.50 | $3-15 |
| AutoEvolve | 10-30分 | $1-5 | $30-150 |

### コスト最適化

1. **Haiku モデルの活用**: 軽量タスクは claude-haiku-4-5 で大幅コスト削減
2. **バッチモード**: 非同期実行でレート制限緩和
3. **条件付き実行**: 変更がない日はスキップ（git diff で判定）

## 移行手順（段階的）

### Phase 1: 試行（1タスク）
1. Daily Health Check を Managed Agents API で作成
2. 1週間並行運転（launchd + Managed Agents 両方実行）
3. 結果比較: 実行成功率、コスト、レイテンシ

### Phase 2: 評価
1. 並行運転の結果を評価
2. コスト/信頼性のトレードオフを確認
3. 移行 Go/No-Go 判断

### Phase 3: 本移行
1. 承認されたタスクを Managed Agents に移行
2. launchd plist を無効化（削除ではなくロールバック可能に）

## リスクと対策

| リスク | 対策 |
|--------|------|
| コスト爆発 | ハード予算キャップ + 日次コストアラート |
| API 障害 | launchd をフォールバックとして維持 |
| レイテンシ増加 | 短時間タスクはローカル維持 |
| ネットワーク依存 | オフライン時は launchd にフォールバック |

## 関連ドキュメント

- `references/managed-agents-hybrid.md` — Hybrid Architecture 全体像
- `references/unattended-pipeline.md` — 既存の無人実行パイプライン設計
- `scripts/runtime/` — 現在のスケジュール実行スクリプト群
