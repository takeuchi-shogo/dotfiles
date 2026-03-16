# SWE-CI: 長期メンテナビリティ評価ベンチマーク深掘り調査

**調査日**: 2026-03-17
**論文**: arXiv:2603.03823 "SWE-CI: Evaluating Agent Capabilities in Maintaining Codebases via Continuous Integration"
**著者**: Jialong Chen, Xander Xu, Hu Wei, Chuan Chen, Bing Zhao (Sun Yat-sen University, Alibaba Group)
**リソース**: [GitHub](https://github.com/SKYLENAGE-AI/SWE-CI) | [HuggingFace](https://huggingface.co/datasets/skylenage/SWE-CI)

---

## Executive Summary

SWE-CI は「AIエージェントは長期的にコードを保守できるか？」を初めて体系的に測定したベンチマーク。
従来の SWE-bench 等の「スナップショット」型（1回の修正で評価）と異なり、**CIループを回しながら連続的にコードを進化させる「evolution-based」評価**を採用。

**衝撃的な結果**: 18モデル中、zero-regression rate（全タスクで1度もリグレッションを起こさない割合）が 0.5 を超えたのは **Claude Opus 系の2モデルのみ**。大半のモデルは 0.25 未満。

---

## 1. ベンチマーク設計

### 1.1 核心的な問い

> **an agent's ability to maintain code can only be revealed through long-term evolution, where the consequences of past decisions accumulate over successive changes.**

従来のベンチマークでは、ブリトルな修正も綺麗な修正も同じテストスイートを通過してしまう。
違いが見えるのは、新しい要件が来て、インターフェースが変わり、モジュールを拡張する必要が出てきたとき。
**過去の設計判断のコストは、連続した変更を通じてのみ顕在化する。**

### 1.2 データキュレーション (4段階)

| Step | 内容 | 残数 |
|------|------|------|
| 1. Repository Collection | GitHub 全 Python リポジトリから: メンテ3年以上、★500以上、設定/依存ファイル有、テストスイート有、MIT/Apache | 4,923 |
| 2. Commit Span Extraction | main ブランチの線形コミット列、依存関係不変の最大部分列を抽出、変更 1,000 行未満を除外 | 8,311 |
| 3. Environment Construction | Docker イメージ自動生成、テストスイート実行検証、依存不足の自動修復 | 1,458 |
| 4. Case Filtering | base コードでテスト起動確認、テストギャップ5件以上を要求、時間スパン×コミット数でランク付け | **100** |

**最終構成**: 68リポジトリから100タスク。平均 233日間、71連続コミット、500行以上のソース変更。

### 1.3 Dual-Agent 評価プロトコル

```
┌─────────────┐    high-level    ┌─────────────┐
│  Architect  │───requirements──→│ Programmer  │
│   Agent     │                  │   Agent     │
│             │    CI feedback   │             │
│ Summarize → │←── test report ──│ Comprehend →│
│ Locate →    │                  │ Plan →      │
│ Design      │                  │ Code        │
└─────────────┘                  └─────────────┘
       ↑                                ↓
       └──────── run tests ←────────────┘
                 (CI loop, max 20 iterations)
```

- **Architect**: 失敗テストを Summarize → ソースコードを Locate → 要件を Design（最大5件、高レベル記述）
- **Programmer**: 要件を Comprehend → 実装を Plan → Code
- **テストフレームワーク**: pytest + pytest-json-report、タイムアウト 3600秒
- **最大イテレーション**: 20回

### 1.4 SWE-bench との根本的違い

| 観点 | SWE-bench | SWE-CI |
|------|-----------|--------|
| 評価パラダイム | **スナップショット**（1回の修正） | **evolution-based**（反復的進化） |
| 入力 | GitHub Issue テキスト | CI テスト失敗結果（動的フィードバック） |
| エージェント構成 | 単一 | **Architect + Programmer のデュアル** |
| 過去の判断の影響 | 不可視 | **累積的に顕在化** |
| 測定対象 | 機能的正しさ | **長期メンテナビリティ** |

---

## 2. 評価指標

### 2.1 Normalized Change a(c) ∈ [-1, 1]

```
         ┌ (n(c) - n(c₀)) / (n(c*) - n(c₀))   if n(c) ≥ n(c₀)  (改善)
a(c) =   │
         └ (n(c) - n(c₀)) / n(c₀)               else              (退化)
```

- n(c): コードベース c が通過するテスト数
- c₀: ベースコードベース、c*: オラクル（目標）
- **非対称正規化**: 改善は全ギャップに対する比率、退化は元のテスト数に対する比率
  - a(c) = 1: ギャップ完全解消
  - a(c) = -1: 元々通っていたテストを全て壊した
  - a(c) = 0: 変化なし

### 2.2 EvoScore（未来重み付き平均）

```
e = Σᵢ₌₁ᴺ γⁱ a(cᵢ) / Σᵢ₌₁ᴺ γⁱ     (γ ≥ 1)
```

- γ = 1: 単純平均
- γ > 1: **後半のイテレーションに高い重み** → 長期メンテナビリティを重視
- ISO/IEC 25010 の「メンテナビリティ = 品質を劣化させずに修正できる度合い」に基づく
- **設計思想**: 短期的なスピードを犠牲にしても、クリーンで拡張性の高い設計を選んだエージェントが有利になる

### 2.3 Zero-Regression Rate

> 全メンテナンスプロセスを通じて**一度もリグレッションが発生しなかった**サンプルの割合

- regression = テスト変更前に通っていたテストが変更後に失敗すること
- これが最も厳しい指標: 1回でもリグレッションを起こしたら zero ではない

---

## 3. 実験結果

### 3.1 Zero-Regression Rate（全18モデル、Figure 6）

| モデル | Zero-Regression Rate | 評価 |
|--------|---------------------|------|
| **Claude-opus-4.6** | **0.76** | 圧倒的1位 |
| **Claude-opus-4.5** | **0.51** | 唯一の2番手、0.5超 |
| Kimi-K2.5 | 0.37 | 3位グループ |
| GLM-5 | 0.36 | |
| GPT-5.2 | 0.23 | 中位 |
| Qwen3.5-plus | 0.20 | |
| MiniMax-M2.5 | 0.20 | |
| DeepSeek-V3.2 | 0.20 | |
| MiniMax-M2.1 | 0.15 | |
| Kimi-K2-Thinking | 0.15 | |
| GLM-4.7 | 0.14 | 下位 |
| GLM-4.6 | 0.14 | |
| Kimi-K2-Instruct-0905 | 0.12 | |
| Qwen3-coder-plus | 0.10 | |
| doubao-seed-1-8-251228 | 0.09 | |
| QWen3-Max-2026-01-23 | 0.09 | |
| doubao-seed-2-0-pro-260215 | 0.08 | 最下位グループ |
| QWen3-Max-2025-09-23 | 0.07 | |

### 3.2 主要観察

**Observation 1**: 全プロバイダーで新しいモデルほど EvoScore が高い。2026年以降のモデルは顕著な改善。

**Observation 2**: プロバイダーごとにメンテナビリティへの重点が異なる（γ を変えた分析）:
- **長期志向**: MiniMax, DeepSeek, GPT
- **短期志向**: Kimi, GLM
- **安定**: Qwen, Doubao, **Claude**（γ に関わらず順位が安定）

**Observation 3**: **ほとんどのモデルが zero-regression rate 0.25 未満**。Claude Opus 系のみが 0.5 超。

### 3.3 実験規模

- 総トークン消費: **100億トークン以上**
- テスト対象: 8プロバイダー、18モデル

---

## 4. 失敗原因の分析

### 4.1 なぜ AI エージェントは長期メンテナンスに失敗するのか

| 失敗パターン | メカニズム | 累積効果 |
|-------------|----------|---------|
| **タスクのアトミック処理** | 各変更を独立に扱い、進化するコードベースを全体的に理解しない | 設計の一貫性が崩壊 |
| **テストスイートの不整合** | 即座の要件は満たすが、他箇所の暗黙の依存を壊す | カスケード障害 |
| **状態管理の失敗** | 共有状態を変更する際、下流への影響を追跡しない | データ不整合 |
| **反復的劣化** | 各変更が微小な問題を導入、イテレーション3-5で臨界点 | 回復不能な品質崩壊 |
| **コンテキストウィンドウの制約** | 長いコードベースと履歴が処理容量を超え、断片的な理解に | 情報の欠落 |
| **エラー回復能力の欠如** | regression 発生時に根本原因を診断・修正できない | 負債の上に負債を積む |

### 4.2 技術的負債の蓄積軌跡

```
Phase 1 (iter 1-3): 微小な負債導入、最初の regression 出現
Phase 2 (iter 4-6): 指数的な負債成長、カスケードテスト障害
Phase 3 (iter 6+):  臨界点到達、修正が更なる破壊を招く不可逆状態
```

### 4.3 成功するエージェントの特徴

- **変更前の影響分析** (pre-change impact analysis)
- **包括的テスト検証** (full test suite validation)
- **問題発生時のロールバック能力**
- **適応的な修正戦略** (trial-and-error ではなく systematic)

---

## 5. 既存ハーネスへの示唆

### 5.1 現在カバーできている領域

| SWE-CI 対策 | 既存の仕組み | 有効性 |
|-------------|-------------|--------|
| テスト通過の確認 | completion-gate.py (Stop hook) | テストが存在する範囲で有効 |
| コード品質の維持 | golden-check.py (GP-002〜010) | 個々の品質違反は検出可能 |
| ファイル間整合性 | cross-file-reviewer (2ファイル以上で起動) | diff 内の不整合は検出可能 |
| API 互換性 | C-005 (ソフト制約) | プロンプト注入のみ、自動検出なし |
| テスト保護 | protect-linter-config.py | リンター設定のみ |

### 5.2 ギャップ（カバーできていない領域）

| ギャップ | SWE-CI での重要度 | 提案 |
|---------|------------------|------|
| **diff の外への影響追跡** | 最重要 | regression-guard hook + impact-hint pre-hook |
| **テストカバレッジの後退検出** | 高 | completion-gate への差分カバレッジチェック追加 |
| **セッション横断の品質トレンド** | 高 | AutoEvolve 累積メトリクス |
| **「6ヶ月後も動くか？」観点** | 中 | longevity-reviewer の追加 |
| **公開 API の breaking change 自動検出** | 中 | GP-011 の追加 |

### 5.3 多層防御の設計

```
Layer 1 (静的・即座)     golden-check + regression-guard [★ギャップ]
  ↓
Layer 2 (静的・レビュー)  cross-file-reviewer + longevity-reviewer [★ギャップ]
  ↓
Layer 3 (動的・テスト)    completion-gate (既存テスト実行) [既存]
  ↓
Layer 4 (動的・CI)        lefthook pre-commit + CI パイプライン [既存]
  ↓
Layer 5 (事後・トレンド)  AutoEvolve 累積メトリクス [★ギャップ]
```

### 5.4 優先度付き改善ロードマップ

| 優先度 | 施策 | 工数 | 効果 |
|--------|------|------|------|
| **P0** | C-011: Regression Prevention 制約 | S | autonomous 実行での regression 防止 |
| **P0** | completion-gate: 変更ファイルのテスト存在確認 | M | 保護されていない変更の可視化 |
| **P1** | GP-011: Breaking Change 防止 | M | 公開 API の regression 自動検出 |
| **P1** | impact-hint pre-hook | M | 編集前に影響範囲を情報提供 |
| **P2** | longevity-reviewer | S | 長期メンテナビリティ観点のレビュー |
| **P2** | 累積品質メトリクス | M | セッション横断のトレンド分析 |

---

## 6. ソース

- 論文 PDF: https://arxiv.org/pdf/2603.03823 (直接取得・全ページ分析)
- HuggingFace: https://huggingface.co/datasets/skylenage/SWE-CI (137タスク、395 DL/月)
- GitHub: https://github.com/SKYLENAGE-AI/SWE-CI
- 関連: Lehman's Laws of Software Evolution, ISO/IEC 25010, Brooks "The Mythical Man-Month"
