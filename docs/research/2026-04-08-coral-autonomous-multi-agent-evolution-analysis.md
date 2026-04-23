---
status: active
last_reviewed: 2026-04-23
---

# CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended Discovery

- **Paper**: arXiv:2604.01658
- **Authors**: MIT, NUS, Stanford, McGill, SambaNova, Meta, Amazon, Microsoft
- **Repository**: https://github.com/Human-Agent-Society/CORAL (⭐367, Python, MIT)
- **Date Analyzed**: 2026-04-08

## 主張

固定進化探索（FunSearch/AlphaEvolve）の PROPOSE のみ LLM 関与から脱却し、探索プロセス全体（Retrieve/Propose/Evaluate/Update）をエージェントに委ねる「自律進化」が、全11ベンチマークで固定進化を上回る。間接協調（共有メモリ）による知識拡散が協進化の鍵。

## 手法

1. ファイルシステムベース共有永続メモリ（attempts/notes/skills の3カテゴリ）
2. 非同期マルチエージェント間接協調（直接通信なし、共有メモリ経由 = stigmergy）
3. Heartbeat介入（Reflect=毎評価, Consolidate=10回毎, Pivot=5回非改善）
4. Git worktree ベース隔離ワークスペース + symlink 共有
5. 自律進化パラダイム（全フェーズをエージェント自律判断）
6. クロスエージェント知識転移（36%の試行が他エージェント親を使用）
7. 評価関数ベース進化ループ
8. Warm-start（コーディング前リサーチフェーズ）
9. 停滞検出と自動ピボット（5回非改善でトリガー）
10. 知識の構造化蓄積と再利用（notes→skills への昇格）

## 定量結果

- 全11ベンチマークで単一自律エージェントが全ベースライン超過、8タスクで新SOTA
- 改善率 3〜10倍（例: Signal Processing で 30.3% vs OpenEvolve 11.8%）
- 4エージェント協進化: カーネル工学 1350→1103サイクル（18.3%改善）
- 知識アーティファクト削除で 18.6% 低下（因果的寄与の実証）
- クロスエージェント: 36%の試行が他エージェント親を使用、17%改善率

## ギャップ分析

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 | 優先度 |
|---|------|------|------|--------|
| 1 | 共有永続メモリ — attempts formalization | Partial | experiment-registry.jsonl で部分的 | 中 |
| 2 | 非同期間接協調 (stigmergy) | N/A | シングルユーザー順次実行では不要 | — |
| 6 | クロスエージェント知識転移（系譜的） | Partial | git history がカバー。ROI低い | 低 |
| 8 | Warm-start リサーチフェーズ | Partial | search-first あるが制度化されていない | 低 |
| 11 | 実行可能コード片としての skills | Gap | 宣言的 skills のみ | 低 |
| 12 | Population Diversity 管理 | Partial | マルチモデルルーティングあるが意識的活用弱い | 低 |

### Already 項目の強化分析

| # | 既存の仕組み | 強化案 | 優先度 |
|---|---|---|---|
| 3/9 | stagnation-detector.py（反応的） | Consolidate heartbeat 追加 | 最優先 |
| 10 | 4層蒸留パイプライン | 蒸留品質の因果検証メカニズム | 中 |
| 4 | worktree 規定 | 強化不要 | — |
| 5 | AutoEvolve ゲート設計 | 要観察（探索効率への影響計測） | — |
| 7 | 多次元スコアリング | 強化不要 | — |

## セカンドオピニオン（Codex 批評）

### 前提の不一致（重要）
- CORAL は数値最適化（高速評価・多数試行）向き。当セットアップはハーネス設計改善（低速評価・少数試行）
- 安全制約の非対称性: CORAL は失敗許容、当セットアップは master 直変禁止・3ファイル上限
- エージェント数: CORAL は同種4エージェント並行、当セットアップは異種3モデル順次

### 過小評価の指摘
- Consolidate heartbeat は最も価値が高い（成功パスからの知識蓄積の欠損を埋める）
- 蒸留パイプラインの「強化不要」判定は楽観的（因果検証が欠如）
- ゲート付き設計の代償（探索効率の制限）は要観察

### 過大評価の指摘
- stigmergy はシングルユーザー文脈では不要 → N/A に変更
- 系譜的知識転移は git history でカバー → 優先度下げ

## 統合プラン

### Wave 1（最優先）
- T1: Consolidate heartbeat の導入 — stagnation-detector.py に成功時定期介入を追加
- T2: attempts 構造の formalization — experiment-registry.jsonl スキーマ拡張

### Wave 2（Wave 1 効果確認後）
- T3: 蒸留品質の因果検証メカニズム — Garden フェーズに自己検証能力追加
- T4: Warm-start リサーチフェーズの制度化

### Wave 3（将来検討）
- T5: クロスエージェント知識転移の強化
- T6: 実行可能コード片としての skills 蓄積
- T7: Population Diversity の意識的管理

### Go/No-Go 基準
- Wave 1→2: Consolidate heartbeat が5セッション以上で誤検知なく動作
- Wave 2→3: 因果検証で蒸留効果が確認
