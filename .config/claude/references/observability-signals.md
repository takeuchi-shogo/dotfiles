---
status: reference
last_reviewed: 2026-04-23
---

# Observability Signals

> エージェント実行の観測信号とアクション定義。
> 信号収集は `scripts/lib/session_events.py`、分析は `scripts/learner/` パイプラインが担当。

## 1. 信号カタログ

> **owner 列の意味**: 誰がこの信号を読み、アクションに変換する責任を持つか。`unassigned` は読み手不在（Gap として §3 で追跡）。

| 信号 | ソース | 出力先 | owner | 接続状態 |
|------|--------|--------|-------|---------|
| エラーイベント | `session_events.py` `emit_event("error", ...)` | `~/.claude/agent-memory/learnings/errors.jsonl` | `error-rate-monitor.py` | 接続済 |
| GP 違反 | `session_events.py` `emit_event("quality", ...)` | `learnings/quality.jsonl` | `code-reviewer` | 接続済 |
| friction イベント | `session_events.py` `emit_event("pattern", ...)` | `learnings/patterns.jsonl` | `pre-mortem-checklist` トリガ (B1) | 接続予定 |
| スキル実行 | `session_events.py` `emit_event("skill", ...)` | `learnings/skill-executions.jsonl` | `/improve` Garden phase | 接続予定 |
| エラーレートスパイク | `scripts/runtime/error-rate-monitor.py` | stderr 警告 + negative-knowledge.md | `negative-knowledge.md` updater | 接続済 |
| サブエージェント完了 | `scripts/runtime/subagent-monitor.py` | `logs/subagent-metrics.jsonl` | `unassigned` (Gap 4) | 記録のみ |
| Agent routing 判定 | `scripts/policy/agent-router.py` | additionalContext 注入 | `unassigned` (Gap 5) | 接続済(ログなし) |
| セッション集計 | `scripts/learner/session-learner.py` | `metrics/session-metrics.jsonl` | `autoevolve-core` | 記録のみ |
| 失敗クラスタ | `scripts/learner/failure-clusterer.py` | `clusters/failure-clusters.json` | `/improve` Phase 1 (Gap 2 解消) | 接続予定 |
| proposal verdict | `session_events.py` `emit_event("proposal", ...)` | `learnings/proposal-verdicts.jsonl` | `autoevolve-core` | 記録のみ |
| 改善採用率 + cycle time | `/improve` 実行 | `metrics/improve-history.jsonl` | `/improve` Garden phase (< 0.3 で alert) | 接続予定 |
| セッション統計 | `scripts/lifecycle/session-stats.sh` | `~/.claude/session-stats.json` | `unassigned` (Gap 6) | 記録のみ |

## 2. アクションマップ

### 接続済み

| 信号 | 閾値条件 | アクション | escalation (action 失敗時) | 実装状態 |
|------|---------|-----------|---------------------------|---------|
| エラーレートスパイク | 同 FM が 5分ウィンドウで 3回以上 | stderr `[ERROR_RATE_SPIKE]` 警告 + negative-knowledge.md 追記 | session 停止 → 手動 triage | 実装済 |
| Agent routing | UserPromptSubmit のキーワードマッチ | additionalContext でモデル推奨を注入 | 推奨採用率を `/improve` で監視 | 実装済 |
| 失敗セッション | outcome = failure/recovery | negative-knowledge.md 追記 + Playbook 更新 | 同パターン 3 回再発 → pre-mortem-checklist トリガ | 実装済 |
| Change Surface 検出 | Edit/Write のファイルパスがパターンにマッチ | アドバイスメッセージ出力（advisory） | violation 検出時は PreToolUse hook で block | 実装済 |

### 未接続（推奨アクション）

| 信号 | 閾値条件 | 推奨アクション | escalation | 優先度 |
|------|---------|--------------|-----------|--------|
| CFS (Critical Failure Step) | importance ≥ 0.7 のエラー後に correction なし | stderr 警告 + 再プラン促進 | 連続 3 回で session 強制 STOP | High |
| failure-clusters Top-N | 同 FM が cluster 内で 5件超 | `/improve` 候補として自動提案 (Gap 2 解消) | 改善 reject 連続 → pre-mortem-checklist へ昇格 | High |
| improve-history 採用率低下 | 直近5回の adoption_rate < 0.3 | 改善提案の品質見直しアラート | 連続 2 サイクルで Critic 強化 | Medium |
| subagent 失敗 | exit_code ≠ 0 or エラー検出 | re-dispatch 候補として通知 | 同 task で 2 回失敗 → 手動 escalate | Medium |
| friction 集中 | 同 friction_class が 3セッション連続 | pre-mortem-checklist トリガ + situation-strategy-map 追加提案 | 5 連続で Plan 必須化 | Low |
| routing ログ未記録 | (常時) | `emit_event("telemetry", {type: "routing_suggestion", ...})` を追加 | — (実装タスク) | Low |

### Attention Allocation Decision Table

人間の意識的処理は約 10 bits/sec に制限される (Meister 2024, *Neuron* "The Unbearable Slowness of Being")。
信号は流量に応じて 5 動詞のいずれかで配分する。「全部見せる」は rubber-stamp (見ているふり) を招き、accountability を毀損する。

| 動詞 | 想定信号タイプ | 出力先 | 判定基準 |
|------|--------------|--------|---------|
| **interrupt** | CFS、Critical change-surface、Block 級 review verdict | stderr `[BLOCK]` で同期割込 | 続行で被害が拡大、かつ unique な人間判断が必要 |
| **batch** | friction イベント、failure-clusters、改善提案候補 | `learnings/*.jsonl` 追記、`/improve` で集約処理 | 単発では弱信号、集積で意味が出る |
| **escalate** | NEEDS_FIX 連続、subagent 失敗連鎖、未回答の AskUserQuestion | `AskUserQuestion` or 上位エージェントへ通知 | 自律解決の試行回数を超過 |
| **hide** | 接続済 gate の routine pass、deduplicate 済の重複信号 | silent log (記録のみ、UI 露出なし) | 過去 N 件で人が action を取らなかったパターン |
| **shut up** | 確定的 mechanism (linter/hook) で自動修正完了したもの | 出力しない (no-op) | mechanism で確定論的に処理可能 |

**運用ルール**:
- 同じ信号タイプを 2 動詞で同時出力しない (interrupt + batch の二重化を禁止)
- "未接続" 状態は黙認 = 暗黙の `hide` ではない。§3 の Gap として明示する
- escalation で人間が 3 連続で同一判断 (例: PASS) を返したら、その signal を `hide` 候補に降格する

## 3. 未接続ギャップ

優先度順。いずれもこの Wave では「推奨」として記述し、実装は含まない。

### Gap 1: CFS が記録のみ（High）
- **現状**: `learnings/critical-failure-steps.jsonl` に記録されるが、リアルタイムフィードバックなし
- **影響**: 重大エラー後に無自覚で作業を続け、カスケード障害を招く
- **推奨**: `error-rate-monitor.py` と同様の stderr 警告を CFS 検出時に追加

### Gap 2: failure-clusters の読み手なし（High）
- **現状**: `failure-clusterer.py` がクラスタを更新するが、読み取り側のコンポーネントなし
- **影響**: 繰り返しパターンの自動検出が機能していない
- **推奨**: `/improve` 実行時に Top-N クラスタを候補ソースとして参照

### Gap 3: improve-history の閾値アクションなし（Medium）
- **現状**: adoption_rate を記録するが、低下時のアクションなし
- **影響**: 品質が低下した改善提案が繰り返し生成される
- **推奨**: 連続低採用率で改善戦略の自動見直しを促す

### Gap 4: subagent 品質未接続（Medium）
- **現状**: 完了は記録するが、結果の品質（exit_code、エラー有無）を評価しない
- **影響**: 失敗 Worker の re-dispatch が手動判断に依存
- **推奨**: SubagentStop 時に品質メトリクスを `subagent-metrics.jsonl` に追加

### Gap 5: agent-router routing ログ欠如（Low）
- **現状**: routing 判定を additionalContext に注入するが、ログを残さない
- **影響**: どのモデルが推奨されたか、採用されたかの追跡不能
- **推奨**: `emit_event("telemetry", {type: "routing_suggestion", ...})` を追加

### Gap 6: session-stats 分散（Low）
- **現状**: `session-stats.sh` と `session-metrics.jsonl` が別々に統計を記録
- **影響**: セッション統計の全体像が把握しにくい
- **推奨**: `session-metrics.jsonl` に統合し、`session-stats.sh` を段階的に廃止

## 4. ステージ遷移信号

`stage-transition-rules.md` の各ステージで emit すべき信号。

| ステージ遷移 | 信号 | 用途 |
|-------------|------|------|
| Plan → Implement | `task_start` (task_type, approach, estimated_size) | アプローチ別成功率の計測 |
| Implement 中 | `change_surface_detected` (category, risk) | 変更面のカバレッジ追跡 |
| Test 結果 | `test_outcome` (pass/fail, duration) | テスト信頼性の追跡 |
| Review 結果 | `review_verdict` (PASS/NEEDS_FIX/BLOCK, round) | レビュー効率の計測 |
| Review → Verify | `review_rounds_to_pass` (count) | 品質傾向の追跡 |
| Verify → Commit | `task_complete` (outcome, total_duration) | 全体スループットの計測 |
| EPD Decide | `epd_decision` (proceed/pivot/abandon) | EPD の有効性計測 |

---

**データ蓄積先**: `~/.claude/agent-memory/`
