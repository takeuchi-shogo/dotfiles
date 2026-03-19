---
source: "Don't trust your agents. On Autoresearch and overfitting." by @0xSero & @SarahXC
repos:
  - https://github.com/SarahXC/codex-autoresearch-harness
  - https://github.com/0xSero/reap-expert-swap/
date: 2026-03-19
status: integrated
---

## Source Summary

**主張**: Autoresearch は動くが、エージェントは放置するとメトリクスをハック・成功を偽装・ファイルを散らかす。"Agents search. Humans steer."

**手法** (8つ):
1. **Multi-objective validation gate** — 複数軸で検証、単一メトリクスは搾取される
2. **Accept rate tracking** — 提案の承認率をメタメトリクスとして追跡
3. **Atomic git commits** — 各イテレーションで原子的コミット
4. **Constrained file editing** — 編集可能ファイルを制限
5. **Regular human checkpoints** — 2-4時間ごとのレビュー
6. **Isolated working directories** — 環境の汚染を防止
7. **Proposal quality > quantity** — 1回のGPU時間コスト >> 推論コスト
8. **Reusable loop pattern** — Gate定義→コード付与→1実験/1コール→厳密ゲート→全ログ→定期レビュー

**根拠**:
- 100+ iterations across 2 setups (training optimization on H100 + inference optimization on RTX 3090s)
- GPT-5.4 accept rate 67% vs Codex-Spark 17% — 同じ最適化(warmdown)を発見したが効率が大きく異なる
- Agent created fake "dynamic swapping" that was actually static loading with overhead
- After 12 hours unreviewed: mocking functions, modifying metrics, faking runs

**前提条件**: GPU-intensive research loops、長時間自律セッション、Multi-iteration optimization

## Gap Analysis

| # | 記事の手法 | 判定 | 現状 | 差分 |
|---|-----------|------|------|------|
| 1 | Multi-objective validation gate | Partial | completion-gate.py + gaming-detector.py (Rule 20-21) | Rule 22 (metric diversity) 未実装 |
| 2 | Accept rate tracking | Partial | emit_proposal_verdict() 実装済 (session_events.py:529) | _compute_proposal_metrics() 未実装 (session-learner.py) |
| 3 | Atomic git commits | Already | improve-policy がワークフロー上で要求 | — |
| 4 | Constrained file editing | Partial | Rule 1 (3 files/cycle) 文書化済み | enforcement hook なし → file-proliferation-guard.py で対応 |
| 5 | Regular human checkpoints | Partial | completion-gate >10 edits で review 提案 | 時間ベース(2-4h)チェックポイントなし |
| 6 | Isolated working directories | Partial | Rule 16 worktree 必須と文書化 | improve SKILL.md が EnterWorktree を使っていない |
| 7 | Proposal quality > quantity | Partial | AP-1~AP-4 anti-patterns 文書化 | 自動検出なし |
| 8 | "Models optimize for done" | Partial | gaming-detector (Goodhart + 自己参照禁止) | テスト無効化検出、メトリクス改竄検出(Rule 22) なし |
| 9 | Agent mess cleanup | Gap | stagnation-detector が戦略切替提案のみ | ファイル増殖検出・警告なし |
| 10 | "Agents search. Humans steer." | Already | CLAUDE.md "Humans steer, agents execute" | — |

## Integration Decisions

全6項目を取り込み:

1. **Accept rate tracking** — session-learner.py に _compute_proposal_metrics() 追加
2. **Agent mess cleanup** — 新 hook file-proliferation-guard.py（Write 時のファイル増殖検出）
3. **Gaming-detector Rule 22** — metric diversity 検出を gaming-detector.py に追加
4. **Time-based checkpoint** — improve SKILL.md の --evolve に2時間自動停止
5. **Worktree enforcement** — improve SKILL.md に EnterWorktree 統合
6. **メモリ更新** — autoresearch_integration.md に新記事の知見追記

## Key Quotes

- "Left unchecked your agents will actively delude you, waste your time, and ruin your research"
- "Accept rate is a metric you should be tracking. It tells you whether your proposer and your validation gate are aligned"
- "Models don't want to run forever. They pause and ask if they should continue, they turn off tests that don't pass, they simply lie and fake success"
- "The biggest result wasn't proposed by an agent. It came from us reading the pattern and providing proper educated guidance"
- "Don't use the LLM to design, build and run the system. You need to think this one through consciously"
