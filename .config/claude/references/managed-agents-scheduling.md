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

## Routines Pilot: Daily Health Check

> 出典: yamadashy "Claude Code Routines" absorb (2026-04-29) — Task D。
> 本セクションは仕様のみ。実機 pilot は別セッションで実施する。

> **Research Preview 注記** (Boris Tip 28 absorb, 2026-04-30): Claude Code Routines は研究プレビュー機能で、CLI シグネチャ・課金体系・スケジュール仕様が予告なく変更される可能性がある。Pilot 開始時に必ず以下を再確認すること:
> 1. `claude --help` / `claude agents --help` で現時点の Routines/Triggers 関連サブコマンドの存在を確認する。`triggers` サブコマンドは 2026-05 時点では未公開のため、Anthropic 公式 changelog で release タイミングを確認 (CLI-first discovery 原則)
> 2. GitHub trigger を併用する場合は API token のスコープと revocation 手順を別途設計 (token 漏洩時の被害範囲を限定)
> 3. 課金条件 (per-run 上限 / monthly cap / overage 挙動) を Anthropic 公式 changelog で裏取り
> 4. 仕様変更時のフォールバック (local launchd / cron 維持) を Phase 3 まで残す

### Pilot 目標

Daily Health Check を local launchd plist から **cloud Routines** に試験移行し、Mac sleep 中断耐性 / コスト / レイテンシを 1 週間並行運転で実測する。Phase 1 (試行) → Phase 2 (評価) → Phase 3 (本移行) の段階運用。

### (a) Cloud Routines 化コマンド例

```bash
# Routines 作成（2 時間間隔、Daily Health Check 相当）
claude agents create \
  --name "daily-health-routines-pilot" \
  --model claude-sonnet-4-6 \
  --system-prompt "$(cat scripts/runtime/daily-health-check-prompt.md)"

AGENT_ID="<上記出力の id>"

# 2 時間ごとに実行（既存 launchd は 21:07 だが Mac sleep の影響を排除するため interval 化）
claude triggers create \
  --agent-id "$AGENT_ID" \
  --schedule "0 */2 * * *" \
  --timezone "Asia/Tokyo"

# 環境制約 (cost cap)
claude agents config "$AGENT_ID" \
  --max-cost-per-run "1.0" \
  --max-runtime-minutes "10"
```

> **注**: `claude agents` / `claude triggers` の正確な CLI 形は API バージョンに依存する。pilot 開始時に `claude agents --help` で最新仕様を確認すること (CLI-first discovery 原則)。

### (b) 1 週間並行運転時の比較メトリクス

local launchd と cloud Routines を **両方有効**にして 7 日間運転し、以下を記録する:

| メトリクス | local launchd 期待値 | cloud Routines 期待値 | 計測方法 |
|---|---|---|---|
| 実行成功率 | ~92% (Mac sleep で miss あり) | ≥ 99% | `runs/routines-pilot-YYYY-MM-DD.md` の 7 日サマリー |
| P50 遅延 | < 10s | < 30s (cold start 込み) | trigger 時刻と log の time diff |
| P90 遅延 | < 30s | < 60s | 同上 |
| P99 遅延 | < 2min (sleep 復帰時) | < 90s | 同上 |
| コスト/回 | $0 (local API) | $0.10–0.50 | `claude agents usage --since 7d` |
| 月額概算 | $0 | $30–150 | コスト/回 × 30 日 × 12 回/日 |

判定基準: cloud Routines の実行成功率が +5pp 以上向上し、P90 遅延が 60s 以下なら Phase 3 移行候補。

### (c) ロールバック手順

```bash
# Cloud Routines 無効化
claude triggers delete "$AGENT_ID"
claude agents delete "$AGENT_ID"

# local launchd 再有効化（Phase 1 期間中も実行されているはずなので、確認のみ）
launchctl list | grep daily-health-check
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude.daily-health-check.plist
```

部分的失敗時 (Routines 個別実行が timeout 等で失敗): cron を fallback として残し、次回 cron で再実行。Pilot 期間中は **両方稼働** が必須 (片方だけ動いている期間を作らない)。

### (d) 結果記録テンプレート

`runs/routines-pilot-YYYY-MM-DD.md` (新規ファイル) に以下を 7 日間追記する:

```markdown
# Routines Pilot — Daily Health Check

## 実行ログ

| date | trigger_time | runtime | success | cost_usd | notes |
|---|---|---|---|---|---|
| 2026-XX-XX | 09:00 | 12s | ✅ | $0.18 | — |
| 2026-XX-XX | 11:00 | 13s | ✅ | $0.21 | — |
| 2026-XX-XX | 13:00 | — | ❌ | — | Routine timeout |
| ... | ... | ... | ... | ... | ... |

## 並行運転比較サマリー

| 指標 | local launchd | cloud Routines | delta |
|---|---|---|---|
| 実行回数 | N | M | — |
| 成功率 | X% | Y% | +Zpp |
| P90 遅延 | A秒 | B秒 | +Cs |
| 累積コスト | $0 | $D | +$D |

## 判定

- Phase 3 移行: Yes / No
- 理由: ...
```

### Mac sleep 耐性に関する注記

local cron / launchd は `pmset` の sleep 中断を受ける。`pmset -g | grep wakeonlan` が無効、かつ `caffeinate` が動いていない時間帯は実行 miss が発生する。cloud Routines はこの欠点を解消する一方で、ネットワーク依存 (オフライン時に実行不可) という新規欠点を抱える。本 pilot で local が実行 miss する時間帯と cloud が実行できない時間帯を実測比較する。
