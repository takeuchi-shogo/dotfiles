---
source: https://arxiv.org/abs/2603.09022 + https://github.com/openverse-ai/MEMO
date: 2026-03-19
status: analyzed
---

# MEMO: Memory-Augmented Model Context Optimization

## Source Summary

**主張**: マルチターン・マルチエージェント LLM ゲーム評価で、推論時コンテキストを最適化可能なオブジェクトとして扱い、Retention（記憶保持）+ Exploration（探索）を結合することで、勝率と安定性を大幅に改善できる。

**手法**:
- Retention: 永続メモリバンクに self-play トラジェクトリから CRUD 操作（XML タグベース）で構造化インサイトを蓄積し、後続プレイにプライアとして注入
- Exploration: TrueSkill ベース不確実性考慮評価 + 優先度付きリプレイバッファ（逆頻度）+ 5進化戦略（keep-best/random/memory-guided/trajectory-based/crossover）
- 状態レジストリの自己成長: キーワードベース分類 + Gemini Flash による自動分類
- 重複検出: 単語重複率60%閾値

**根拠**: GPT-4o-mini 25.1%→49.5%、Qwen-2.5-7B 20.9%→44.3%（2,000 self-play/task）。交渉・不完全情報ゲームで最大改善。run-to-run variance 低下。

**前提条件**: テキストベースゲーム環境（TextArena）での self-play が可能なこと。完全情報ゲームでは RL の方が有効。

## Gap Analysis

| # | MEMO の手法 | 判定 | 現状 |
|---|-----------|------|------|
| 1 | メモリ CRUD 操作 | Already | memory-archive.py, session_events.py |
| 2 | 進化ループ | Already | AutoEvolve 4層ループ |
| 3 | 状態レジストリ・分類 | Already | stagnation-detector.py, 21ルール |
| 4 | A/B テスト・fitness評価 | Already | skill-audit, experiment_tracker.py |
| 5 | トラジェクトリ分析 | Already | session-learner.py |
| 6 | RL advantage / variance正規化 | Already | rl_advantage.py |
| 7 | gaming 検出 | Already | gaming-detector.py (Rule 20-22) |
| 8 | TrueSkill ベース不確実性考慮評価 | **Gap** | 勝率 delta > +2pp 閾値のみ。試行回数の少なさを考慮した rating なし |
| 9 | 優先度付きリプレイバッファ（逆頻度） | **Partial** | importance_weight あるが逆頻度メカニズムなし |
| 10 | 5戦略プロンプト進化 | **Partial** | 3戦略あるが crossover・trajectory-based なし |
| 11 | インサイト重複検出の定量化 | **Partial** | Garden で重複排除あるが定量閾値なし |
| 12 | 圧縮トラジェクトリ表現 | **Gap** | 生データ保存。構造化圧縮なし |
| 13 | self-play パターン | N/A | ゲーム AI 向け |
| 14 | TextArena 統合 | N/A | ゲーム特化 |

## Integration Decisions

ユーザー判断: **なし**（分析結果のみ保存）。Gap/Partial 5件は将来の改善候補として記録。
