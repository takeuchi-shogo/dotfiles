# AlphaEvolve 知見の AutoEvolve 統合プラン

> Source: [AlphaEvolve Analysis](../research/2026-04-07-alphaevolve-autoevolve-analysis.md)
> 規模: L（7タスク、4+ ファイル横断）
> 撤退条件: Layer 1 完了後に Tournament Mode で合成ベンチマーク付き 5 バリアント実行を検証。候補数増加が提案品質向上に寄与しなければ Layer 2 以降を見送り

## 概要

AlphaEvolve の「進化的コーディングエージェント」の設計パターンを AutoEvolve に翻案し、
改善サイクルのフィードバック速度・候補多様性・知識蓄積の質を向上させる。

**重要な前提**: AlphaEvolve (決定的評価 × 数百世代 × アルゴリズム最適化) と AutoEvolve (確率的評価 × 最大5世代 × ハーネス設定最適化) はドメインが根本的に異なる。手法の直接移植ではなく設計パターンの翻案として実装する。

## Layer 構成（依存順）

### Layer 0: Evaluation Foundation

#### Task 1: 二層評価アーキテクチャ [M] — P0
- **対象**: `references/improve-policy.md`, 新規 `references/synthetic-benchmark-spec.md`
- **変更**:
  - 即時評価レイヤーの定義:
    - 構文チェック: SKILL.md のフロントマター・セクション構造の妥当性
    - 一貫性チェック: 変更前後の description と body の整合性
    - 既知パターンマッチ: error-fix-guides/golden-principles との照合
    - スカラー値: 0.0-1.0 の即時スコアを返す
  - 遅延評価レイヤー: 既存の compute_skill_score() をそのまま活用
  - Goodhart 監査:
    - 合成スコアと実使用スコアの相関を 10 ラン毎に計算
    - 相関 < 0.5 で合成ベンチマークの再キャリブレーションをトリガー
    - improve-policy に Rule 26 として追加
- **効果**: Tournament Mode のラウンド内で即時フィードバックが可能に

#### Task 2: 候補DBメタデータ拡充 [S] — P1
- **対象**: `agents/autoevolve-core.md` (proposals.jsonl スキーマセクション)
- **変更**:
  - proposals.jsonl に以下のフィールドを追加:
    ```jsonc
    {
      // 既存フィールドに加えて:
      "parent_id": "IMP-YYYY-MM-DD-NNN | null",  // 親提案（なければ null）
      "mutation_type": "new | edit | merge | revert_fix",  // 変異タイプ
      "diversity_score": 0.0-1.0  // tags overlap の逆数（既存提案との差異度）
    }
    ```
  - proposal-pool.jsonl の選択時に diversity_score を加味:
    - 上位3件サンプリング時、1件は diversity_score 上位から選択（多様性保証）
- **効果**: 進化ループの系譜追跡と多様性管理が可能に

### Layer 1: Evolution Enhancement

#### Task 3: Tournament Mode 拡張 + 即時評価統合 [M] — P0
- **対象**: `agents/autoevolve-core.md` (Tournament Mode セクション), `references/improve-policy.md`
- **依存**: Task 1, Task 2
- **変更**:
  - 候補数を 2-3 → 5-8 に拡張（improve-policy に上限値を明記）
  - 即時評価で候補をフィルタリング:
    - Phase 1: 5-8 バリアントを Sonnet 並列で生成
    - Phase 2: 即時評価（Task 1 の合成ベンチマーク）でスコアリング
    - Phase 3: 上位 3 バリアントを A/B テスト（遅延評価）
  - improve-policy に安全制約を追加:
    - 即時評価スコア < 0.3 のバリアントは自動 discard
    - 全バリアントが < 0.3 なら Tournament 自体を中止
- **効果**: 候補の量と質のバランスを改善。即時フィードバックでイテレーション速度向上

#### Task 4: 差分パッチ生成戦略 [S] — P0-adjacent
- **対象**: `agents/autoevolve-core.md` (Phase 2 修正パターンセクション)
- **依存**: なし
- **変更**:
  - スキル修正時のデフォルトを「差分パッチ」に変更:
    - LLM への指示に「既存の SKILL.md を読み、変更が必要な箇所のみを Edit で修正せよ。全体の書き換えは行わない」を明記
    - 変更行数が元の SKILL.md の 30% を超える場合は警告を出す
  - 全体書き換えが必要な場合は `mutation_type: rewrite` を明示（proposals.jsonl に記録）
  - Rule 20 (1変更1仮説) との統合: 差分パッチ = デフォルト、全体書き換え = 明示オプトイン
- **効果**: 既存の良い部分を保存しつつ局所改善。変更のノイズを削減

### Layer 2: Knowledge & Context

#### Task 5: プロンプト組立の体系化 (Context Assembly) [M]
- **対象**: `agents/autoevolve-core.md` (Phase 1.0 → 新 Phase 1.5: Context Assembly)
- **依存**: Task 2 (メタデータ活用)
- **変更**:
  - Phase 1.0 (ラン初期化) と Phase 2.0 (Ideation-Debate) の間に Phase 1.5: Context Assembly を新設
  - 散在するコンテキスト注入を単一ステップに統合:
    1. improvement-backlog.md → 優先テーマ
    2. winning-direction.md → 前回の方向性
    3. proposal-pool.jsonl → 成功パターン3件（diversity 保証付き）
    4. knowledge-index.yaml → 関連概念3件 × 500 tokens（ASI-Evolve Task 3.1/3.2）
    5. rejected-patterns.jsonl → 避けるべき方向性
  - 出力: `runs/YYYY-MM-DD/assembled-context.md` として保存
  - Phase 2.0 の入力は assembled-context.md のみを参照（散在アクセスを排除）
- **効果**: コンテキスト注入の透明性向上、デバッグ容易化、品質安定

#### Task 6: 島モデル導入 [M]
- **対象**: `agents/autoevolve-core.md` (Tournament Mode セクション)
- **依存**: Task 2, Task 3
- **変更**:
  - Tournament Mode の worktree 並列を「島」として再定義:
    - 各 worktree = 1つの島（独立した改善方向性）
    - 島ごとに異なる mutation_type を指定（new, edit, merge）
  - 島間知識交換 (Migration):
    - 各島の最良提案を proposals.jsonl に parent_id 付きで記録
    - 次世代の Context Assembly (Task 5) で、異なる島の成功提案を cross-pollination
    - migration_interval: 2世代ごと（Tournament 2回実行ごと）
  - 収束検出: 全島の上位提案の tags overlap > 80% なら「収束」として島を再シャッフル
- **効果**: 局所最適への収束を防止、異なるアプローチの交差で新しい改善方向を発見

### Layer 3: Optimization

#### Task 7: 探索/深化トークン予算分離 [S] — P3
- **対象**: `agents/autoevolve-core.md` (Tournament Mode セクション)
- **依存**: Task 3
- **変更**:
  - Tournament Mode 内のモデル割り当てを明示化:
    | フェーズ | モデル | 目的 | トークン予算 |
    |---------|--------|------|------------|
    | 候補生成 (探索) | Sonnet × 5-8 並列 | 多様なアイデアを高速生成 | 各 2K tokens |
    | 即時評価 | スクリプト (合成ベンチマーク) | 自動フィルタリング | — |
    | 精錬 (深化) | Codex (gpt-5.4) | 上位3候補の戦略的改善 | 各 8K tokens |
    | 最終評価 | A/B テスト | 実使用データで検証 | — |
- **効果**: 探索フェーズのコスト削減 + 深化フェーズの品質向上

## 実行順序

```
Session 1: Layer 0 (Task 1 + 2) — Evaluation & Data Foundation
Session 2: Layer 1 (Task 3 + 4) — Evolution Enhancement
Session 3: Layer 2 (Task 5 + 6) — Knowledge & Context
Session 4: Layer 3 (Task 7) — Optimization

効果測定ゲート: Layer 1 完了後、Tournament Mode で合成ベンチマーク付き
5 バリアント実行を 2-3 回テスト。候補数増加が提案品質向上に寄与しなければ
Layer 2 以降を見送り。
```

## 反証・リスク

| リスク | 影響 | 対策 |
|--------|------|------|
| 合成ベンチマークが実使用と乖離 (Goodhart) | 合成スコア高だが実使用で劣化 | 10ラン毎に相関監査、< 0.5 で再キャリブレーション |
| 候補数増加がノイズを増やすだけ | Tournament のコスト増加、提案品質低下 | 即時評価のフィルタ閾値 (0.3) で品質保証 |
| 島モデルの計算コスト | worktree × 5-8 の並列は重い | 島数を3に制限、mutation_type で差別化 |
| 差分パッチが保守的すぎる | イノベーティブな改善が生まれない | 30% 閾値は警告のみ、ブロックしない |
| Context Assembly がボトルネック | 組立に時間がかかりループ速度低下 | 各ソースに読み込み上限を設定（合計 3K tokens） |
| ASI-Evolve 統合プランとの競合 | 同じファイルを別方向に変更 | ASI-Evolve Layer 2-4 と統合して実行 |

## ASI-Evolve 統合プランとの関係

本プランは `docs/plans/2026-04-06-asi-evolve-integration.md` と一部重複する:
- Task 2 (メタデータ拡充) → ASI-Evolve Task 1.1 の拡張
- Task 5 (Context Assembly) → ASI-Evolve Task 3.1/3.2 を包含
- Task 6 (島モデル) → ASI-Evolve には対応なし（新規追加）

実装時は ASI-Evolve プランを本プランで上書き・統合する。
