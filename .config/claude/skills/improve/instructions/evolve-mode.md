# --evolve モード: イテレーティブ進化ループ

`/improve --evolve` が指定された場合、通常の Step 0-7 完了後に以下のループを実行する。

## 前提条件

- Step 0-7 の通常分析が完了していること
- `skill-executions.jsonl` に失敗データがあるスキルが存在すること

## ダッシュボード（オプション）

ループ開始時にライブダッシュボードを起動できる:

1. ワークスペースに `dashboard-state.json` を初期化（`skill_name`, `baseline_score`, `target_score: 0.95`, `status: "running"`, `rounds: []`）
2. `python3 $HOME/.claude/skills/skill-creator/scripts/generate_dashboard.py <path>/dashboard-state.json` で HTML 生成
3. `open <path>/dashboard.html` でブラウザ起動（10秒ごと自動リフレッシュ）
4. 各イテレーション末尾で `rounds` に結果を追記 → `generate_dashboard.py` 再実行
5. ループ完了時に `status` を `"completed"` に更新 → 最終 HTML 生成

## ループフロー

**各イテレーションで以下を実行:**

1. **対象選定**: `experiment_tracker.py next-target --skills {degraded_skills}` でラウンドロビン選定
2. **失敗収集**: `skill-executions.jsonl` から対象スキルの failure_count >= 3 のパターンを抽出
3. **Proposer**: `autoevolve-core (phase: improve)` を起動。H（`proposer-context --skill {target}`）+ 失敗トレースを注入。AP-1〜4 チェック
   - **単一変更規律 (Rule 20)**: Proposer への指示に以下を含める: 「SKILL.md への変更は **1箇所のみ**。仮説を1文で明記すること。」
   - Proposer は `hypothesis` フィールドを返す（例: "見出しに数値を強制するルールを追加"）
4. **Builder**: Proposer の提案を **worktree 上で** 実装（`autoevolve/*` ブランチ）
5. **検証**: `skill-audit` の A/B パイプライン（`run_eval.sh` → `compare.sh` → `aggregate.py`）→ `gate_proposal()` 判定
   - checklist 付き eval の場合: `checklist_pass_rate` を主要メトリクスとして使用
5b. **Verdict 記録**: 検証結果を `emit_proposal_verdict()` で記録:
    ```python
    from session_events import emit_proposal_verdict
    emit_proposal_verdict(
        skill_name=target_skill,
        hypothesis=proposer_hypothesis,
        verdict="keep" if gate_passed else "revert",
        metric_before=baseline_score,
        metric_after=current_score,
        iteration=current_iteration,
    )
    ```
6. **H 更新**: `experiment_tracker.py record` に全結果を記録
7. **Changelog 更新**: ワークスペースの `changelog.md` に結果を追記

## 早期終了条件

- 2 イテレーション連続で `auto_reject` → ループ終了
- **3 イテレーション連続で `revert` → ドリフト検出。ループ停止しユーザーに報告** (Rule 18)
- **3 イテレーション経過後にベースラインスコアを下回っている → ループ停止** (Rule 19)
- **経過時間が 2 時間を超過 → ループ停止しユーザーに報告** — "Don't trust your agents" 記事: 12時間放置でメトリクス改竄・テスト無効化が発生。2時間は人間レビューの最小安全間隔
- 全対象スキルが healthy に昇格 → ループ終了
- `--iterations` 上限に到達 → ループ終了

## --pareto モード: GEPA 的多候補パレート探索

> 出典: Câmara+ 2026 — GEPA が TextGrad を +0.051 上回った要因は「多様な亜種の並行探索」

`/improve --evolve --pareto` で有効化。通常の greedy 単一候補精錬の代わりに、複数候補を並行生成・パレート淘汰する。

### フロー

1. **候補生成**: 各イテレーションで Proposer が **3つの改善バリアント** を生成する（`hypothesis` + `strategy` が異なる）
   - バリアント A: 保守的改善（既存パターンの微調整）
   - バリアント B: 構造的改善（セクション再構成、ルール統合）
   - バリアント C: 探索的改善（新しいアプローチ、異なる設計原則の適用）
2. **並行評価**: 3バリアントを worktree で A/B テスト（9 LLM 呼び出し/イテレーション）
3. **パレート選択**: 精度 × コスト（トークン数）の2軸でパレートフロンティアを計算。フロンティア上の候補のみ次世代に残す
4. **淘汰**: パレート劣位の候補を破棄。フロンティア候補から次の Proposer 入力を選択（支配頻度に比例した確率選択）
5. **収束判定**: 2イテレーション連続でフロンティアが変化しなければ収束とみなし終了

### 通常 evolve との使い分け

| 条件 | 推奨モード |
|------|-----------|
| 改善方向が明確（特定エラーの修正） | `--evolve`（greedy で十分） |
| 改善方向が不明確、プラトー状態 | `--evolve --pareto`（探索幅が必要） |
| Rule 31 の `saturating` トレンド検出時 | `--pareto` を自動推奨 |

### 制約

- 最大イテレーション: 3（コスト: 3 × 9 = 27 LLM 呼び出し）
- Rule 20 の単一変更規律は各バリアント内で維持
- Rule 22 の評価基準自己変更禁止は引き続き適用

## コスト制御

- 1 イテレーション = 1 スキル
- A/B テスト（通常）: 3 プロンプト × 2 (with/without) = 6 LLM 呼び出し/イテレーション
- A/B テスト（--pareto）: 3 プロンプト × 3 バリアント = 9 LLM 呼び出し/イテレーション
- 最大（通常）: 5 × 6 = 30 LLM 呼び出し/実行
- 最大（--pareto）: 3 × 9 = 27 LLM 呼び出し/実行

## Changelog 生成

各イテレーション完了後、ワークスペースの `changelog.md` を更新する:

```
# Skill Evolution Changelog: {skill-name}

## Round {N} ({date})
- **Hypothesis**: {proposer_hypothesis}
- **Change**: {変更箇所の概要}
- **Result**: {KEEP|REVERT} (metric: {before} → {after}, delta: {delta})
```

Changelog は `--evolve` レポートに全文を含める。

## ループ完了後のレポート

Step 7 のレポートに以下を追加:

| Iter | 対象スキル | 仮説 | Gate 判定 | A/B delta | 累積改善 |
|---|---|---|---|---|---|
| 1 | {skill} | {hypothesis} | {verdict} | {delta} | {cumulative} |

- 実行イテレーション数: N / {max}
- **Accept Rate: {keeps}/{total} ({rate}%)** — autoresearch 記事基準: 50%以上が健全
- 早期終了: {yes/no, reason}
- ドリフト検出: {yes/no}
