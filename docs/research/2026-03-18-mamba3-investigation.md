# Mamba-3: Improved Sequence Modeling Using State Space Principles — 調査レポート

> **調査日**: 2026-03-18
> **ソース**: arXiv 2603.15569 (論文)、GitHub state-spaces/mamba (実装)、Tri Dao ブログ (著者解説)
> **分析モデル**: Claude (アーキテクチャ・ベンチマーク)、Gemini (エコシステム・外部動向)、Codex gpt-5.4 (戦略分析)
> **著者**: Aakash Lahoti, Kevin Y. Li, Berlin Chen, Caitlin Wang, Aviv Bick, J. Zico Kolter, Tri Dao, Albert Gu
> **公開**: OpenReview 2026-01-26、最終更新 2026-03-11、ICLR 2026 Oral

---

## Executive Summary

Mamba-3 は SSM (State Space Model) の第3世代アーキテクチャで、**推論ファースト (inference-first)** の設計思想に基づき3つの革新を導入した: (1) 指数台形離散化、(2) 複素数値 SSM + RoPE 統合、(3) MIMO (Multi-Input, Multi-Output) SSM。これらは**状態サイズを変えずに表現力を最大化**するアプローチであり、シーケンス長 16K で Transformer 比 85.6% 高速な推論レイテンシを実現する。ただし正確な情報検索タスクでは Transformer に及ばず、著者自身が **linear layers + global self-attention のハイブリッドが将来の主流**と予測している。

---

## 1. 背景: SSM の進化

| 世代 | 離散化 | 値の型 | 入出力構造 | 設計思想 |
|------|--------|--------|-----------|---------|
| **Mamba-1** (S6, 2023) | ZOH (零次ホールド) | 実数 | SISO | 選択的 SSM の提案 |
| **Mamba-2** (SSD, 2024) | ZOH | 実数 | SISO (ヘッド並列) | 学習効率最適化 (training-first) |
| **Mamba-3** (2026) | **指数台形** | **複素数** | **MIMO** | **推論効率最優先 (inference-first)** |

Mamba-2 は SSD (State Space Duality) フレームワークにより SSM と線形注意の双対性を示し GPU 効率を改善したが、推論時の表現力は犠牲にしていた。Mamba-3 は「推論はメモリバウンドであり、演算増加は許容できる」という認識に基づき、SSM の中身自体を強化する方向に舵を切った。

---

## 2. アーキテクチャ革新

### 2.1 指数台形離散化 (Exponential-Trapezoidal Discretization)

**変更点**: ZOH → 指数台形離散化

```
# ZOH (Mamba-1/2): 入力をステップ間で定数と仮定
B̄ = (exp(ΔA) - I) A⁻¹ B

# 指数台形 (Mamba-3): 区間両端の平均を取る
B̄ = (exp(ΔA) + I) / 2 · ΔB
```

**設計動機**: 古典制御理論の台形離散化 (Tustin/Bilinear transform) は ZOH より高精度で連続ダイナミクスを保存する。入力の線形変化を近似するため、同じ状態サイズでより豊かなダイナミクスを表現できる。

**効果**: 状態遷移の表現力向上 + A-安定性 + 短い因果畳み込みの除去根拠

### 2.2 複素数値 SSM + RoPE 統合

**変更点**: 実数値 SSM → 複素数値 SSM

```
A = diag(a₁, ..., aₙ),  aₖ = rₖ · exp(iθₖ)  # 極形式
Āₖ = exp(Δ·rₖ) · exp(iΔθₖ)
      ↑ 減衰       ↑ 回転 (= RoPE 相当)
```

**設計動機**: 実数対角 A は指数減衰のみ。複素数にすることで**減衰 + 回転 (振動)** を同時に表現でき、周期的パターンの追跡が可能になる。RoPE が SSM の遷移に内包されるため、別モジュールとしての位置エンコーディングが不要に。

**効果**: 同じ状態サイズで表現力が実質倍増 + アーキテクチャ簡潔化

### 2.3 MIMO (Multi-Input, Multi-Output) SSM

**変更点**: SISO (B ∈ ℝ^{N×1}) → MIMO (B ∈ ℝ^{N×P})

**設計動機**: SISO では各ヘッドの状態が入力の1次元分しか受け取れない。MIMO では同じ状態サイズ N で P 次元の入力を同時に受け取り、次元間混合を実現する。

**核心的洞察**: 推論 (decode) は**メモリバウンド** (H100 で約 2.5 ops/byte) であり、GPU の演算器が遊んでいる。MIMO は状態の read/write 量を増やさず FLOPs だけ増やすため、decode レイテンシを保ったまま品質向上が可能。

| 項目 | 学習 (training) | 推論 (decode) |
|------|----------------|---------------|
| FLOPs | 増加 (~R倍) | 微増 (メモリ隠蔽) |
| レイテンシ | 増加 | **ほぼ一定** |
| 状態サイズ | 同一 | 同一 |

### 2.4 その他の改良

- **QKNorm (BCNorm)**: B, C パラメータの正規化で学習安定性を確保
- **短い因果畳み込みの除去**: BCNorm 後のバイアス + 指数台形離散化で代替。SSM の外側→内側に統合
- **カーネル簡潔化**: 畳み込み除去でカーネル融合が容易に

### 2.5 3革新の相乗効果

```
指数台形離散化 ──→ 入力取り込み高精度化 ──→ 畳み込み不要化
       ↓
複素数値 SSM ────→ 減衰+回転の表現 ────→ RoPE 不要化
       ↓                                    ↓
MIMO ────────────→ 次元間混合 ─────────→ 状態効率最大化
       ↓
[全体] 同じ推論コストで大幅な品質向上 + アーキテクチャ簡潔化
```

3つの革新は**すべて「状態サイズ N を変えない」制約の下で表現力を最大化**する方向で統一されている。

---

## 3. ベンチマーク・性能分析

### 3.1 推論レイテンシ (1.5B, H100 GPU)

| シーケンス長 | Mamba-3 SISO | Mamba-2 | GDN | vLLM (Transformer) | **vs Transformer** |
|---:|---:|---:|---:|---:|---:|
| 512 | **4.39s** | 4.66s | 4.56s | 4.45s | **1.4% 高速** |
| 4,096 | **35.11s** | 37.22s | 36.41s | 58.64s | **40.1% 高速** |
| 16,384 | **140.61s** | 149.02s | 145.87s | 976.50s | **85.6% 高速** |

**スケーリング特性**: SSM 系はシーケンス長に線形 (O(L))。Transformer は超線形 (512→16K で 219.4 倍に膨張)。

### 3.2 言語モデリング性能序列

| 順位 | アーキテクチャ | 備考 |
|---:|---|---|
| 1 | **Transformer (Llama-3)** | KV-cache による完全注意。検索・長距離依存に最強 |
| 2 | **Mamba-3 MIMO** | 1B スケールで SISO 比 +1pt 以上。状態サイズ増加なし |
| 3 | **Mamba-3 SISO** | 全 SSM 中最良 |
| 4 | **Gated DeltaNet** | Mamba-2 と競合 |
| 5 | **Mamba-2** | 安定した性能 |

### 3.3 検索タスク

SSM は固定サイズ状態による構造的限界あり。Mamba-3 MIMO は SISO より改善するが、Transformer の KV-cache には原理的に及ばない。

### 3.4 適性マトリクス

| ユースケース | 適合度 | 根拠 |
|---|:---:|---|
| 長文コンテキスト推論 (16K+) | ★★★★★ | Transformer 比 85.6% 高速 |
| リアルタイムストリーミング | ★★★★★ | 固定メモリ・O(1) per-step decode |
| エッジデバイス展開 | ★★★★☆ | KV-cache 不要で省メモリ |
| Agent ワークロード | ★★★★☆ | 多段推論の総コスト削減 |
| 正確な情報検索 (RAG代替) | ★★☆☆☆ | 固定状態サイズの構造的限界 |
| Few-shot ICL | ★★★☆☆ | プロンプト内例示の正確な参照で劣る |
| コード生成 (長距離参照) | ★★☆☆☆ | 関数定義-呼び出しの追跡が課題 |

---

## 4. Transformer との比較: 設計思想の対比

| 観点 | Transformer | Mamba-3 |
|------|------------|---------|
| 推論計算量 (per step) | O(L) — KV-cache 読み出し | O(N) — 固定状態更新 |
| メモリ (推論時) | O(L×d) — シーケンス長に線形増加 | O(N) — 一定 |
| 情報アクセス | 完全 (全トークンへのランダムアクセス) | 圧縮 (固定状態に集約) |
| 長所 | 精度・検索・ICL | 推論速度・メモリ効率・スケーリング |
| 弱点 | 長シーケンスでコスト爆発 | 正確な検索・長距離依存の追跡 |

**Codex の分析**: Mamba-3 を見るべき軸は "Can it beat Transformers on average?" ではなく **"Can it deliver more capability per unit of deployed inference budget?"** _(ソース: Codex gpt-5.4)_

---

## 5. 「推論ファースト」設計思想の戦略的意義

### 5.1 なぜ今、inference-first なのか

業界の競争軸が pretraining → **post-training/RL/agentic workflows** に移行:

1. **RL/Reasoning モデルの普及**: test-time compute で性能が伸びる時代
2. **Agentic workflows の多段化**: 1リクエスト = planner→worker→critic→tool caller の連鎖
3. **運用規模の拡大**: 学習は一度、推論は毎日
4. **長文脈の常態化**: KV-cache がボトルネック

**戦略的含意**: Mamba-3 の inference-first は「重みより推論ループが価値を作る時代のアーキテクチャ設計思想」_(ソース: Codex gpt-5.4)_

### 5.2 古典制御理論への回帰

Mamba-3 は linear attention のトレンドに乗らず、古典制御理論に回帰。理由:
- **離散化誤差と安定性**: 数値解析・制御の領域
- **複素固有値の回転ダイナミクス**: attention の代数では見えにくい
- **MIMO**: signal processing/control の標準概念

**評価**: LLM 全体のパラダイムシフトではなく、**非二次層の設計思想におけるパラダイムシフト** _(ソース: Codex gpt-5.4)_

---

## 6. エコシステムと実装

### 6.1 リポジトリ

- **GitHub**: [state-spaces/mamba](https://github.com/state-spaces/mamba) — 17.4k stars, v2.3.1 (2026-03-10)
- **モデル**: 130M / 370M / 790M / 1.4B / 2.8B (300B tokens, Pile)
- **依存**: PyTorch 1.12+, CUDA 11.6+, causal-conv1d >= 1.4.0

### 6.2 カーネルスタック

| レイヤー | 用途 | 特徴 |
|---------|------|------|
| **Triton** | 標準アーキテクチャ開発 | 制御されたタイリングとカーネル融合 |
| **TileLang** | MIMO prefill カーネル | メモリ階層の粒度制御 |
| **CuTe DSL** | Hopper GPU decode カーネル | テンソルレイアウトとワープ特殊化の低レベル制御 |

### 6.3 フレームワーク対応状況

| フレームワーク | サポート状況 | 備考 |
|--------------|-------------|------|
| HuggingFace | モデルカード公開 | togethercomputer/mamba-3-* |
| vLLM | v0.18.0+ nightly | Triton ベース高速カーネル |
| TGI | 最新版でサポート | — |
| Axolotl | マルチ GPU/FSDP2 対応 | 大規模学習向け |
| Unsloth | Triton 専用カーネル | 学習 2-5x 高速化 |

> **クロスバリデーション注記**: フレームワーク対応状況は Gemini (Google Search grounding) による調査結果。個別の対応状況は公式ドキュメントで要確認。

---

## 7. 競合 SSM との位置づけ

| モデル | 設計系譜 | 強み | Mamba-3 との差 |
|--------|---------|------|---------------|
| **RWKV-7** | Recurrent pragmatism | 多言語、open ecosystem、3B 実証 | Mamba-3: 理論設計の一貫性 + inference co-design |
| **Gated DeltaNet** | Delta rule + linear attention | KV 関係の保持 | Mamba-3: 1.5B で +0.6pt (SISO), +1.8pt (MIMO) |
| **RetNet** | Attention continuity | 学習並列性と推論効率のバランス | Mamba-3: 状態遷移の設計空間が広い |
| **xLSTM** | Gated memory revival | 7B で Mamba 系より高速効率を主張 | Mamba-3: 最速の座は自明でない。complex dynamics + MIMO がユニーク |
| **Griffin** | Hybrid (Attention+RNN) | Transformer に近い安定性 | Mamba-3: ハイブリッド化で弱点解消可能 |

**Mamba-3 の独自ポジション**: SSM camp の最も戦略的な再設計。**control-theoretic, inference-co-designed SSM** の代表 _(ソース: Codex gpt-5.4)_

---

## 8. ハイブリッドアーキテクチャの将来

### 8.1 Mamba-3 チームの予測

> "linear layers will be predominantly used in conjunction with global self-attention layers in the future"

### 8.2 既存ハイブリッド実装

| モデル | 構成 | 特徴 |
|--------|------|------|
| **Jamba** (AI21 Labs) | Transformer + Mamba 交互配置 | KV-cache 削減、256K コンテキスト |
| **Zamba 2** (Zyphra) | Shared Attention + Mamba | パラメータ効率、オンデバイス AI |
| **Nemotron-3** (NVIDIA) | Mamba + Attention + MoE | 100万トークン長文推論 |

### 8.3 含意

- **Transformer-only ecosystem**: attention は消えないが、**高価な特殊機能**に変わる
- **ハードウェア**: KV-cache 偏重からの脱却 + heterogeneous kernel の共存が必要
- **インフラ**: recurrent/chunked/attention の混成実行 + serving-aware な選定

---

## 9. 推奨導入戦略

段階的導入が最も合理的:

1. **hybrid backbone から始める**: 純 Mamba への全面置換は時期尚早
2. **SISO から評価**: インフラ複雑性を抑制
3. **H100/H200 世代で decode-bound なら MIMO を検討**: MIMO の利得はハード依存性が高い
4. **評価指標を変更**: perplexity より `cost per solved task`、`latency under agent loop` を重視

---

## 10. リスクと未解決点

| リスク | 深刻度 | 詳細 |
|--------|:------:|------|
| スケール外挿未確定 | 高 | 主戦場は 1.5B 級。数十B 級の frontier 実証はない |
| Hopper GPU 依存 | 中 | MIMO の economics は H100 的 compute/memory バランスに強く依存 |
| kernel stack 複雑化 | 中 | Triton/TileLang/CuTe の跨ぎで production portability に課題 |
| hybrid 設計の未成熟 | 中 | norm placement すら直感的でないと論文が認めている |
| 固定状態サイズの根本限界 | 高 | retrieval weakness は軽減できても完全には消えない |
| 競合の反撃余地 | 中 | RWKV、xLSTM、DeltaNet 系は高速に進化中 |

---

## 11. クロスモデル分析

### 合意点 (全モデルが一致)
- Mamba-3 の推論効率は SSM クラスで最良
- Transformer との精度ギャップは存在するが縮小傾向
- 固定状態サイズによる検索タスクの構造的限界
- ハイブリッドアーキテクチャが将来の主流

### 相違・注意点
- **Gemini**: Nemotron-3 と Mamba-3 を密接に関連付けているが、Nemotron-3 が Mamba-3 を直接採用しているかは論文で明示されていない
- **Gemini**: 産業採用事例 (Mercedes-Benz、Siemens、FANUC) は具体的だが、一次ソースの検証が必要
- **Codex**: 論文の OpenReview 公開日は 2026-01-26 (arXiv の 2026-03-17 とは異なる)。ICLR 2026 の accepted paper として採択済み
- **Codex**: xLSTM 7B が Mamba 系より高速効率を主張している点を指摘 — Mamba-3 の「最速」主張には留保が必要

---

## ソース・参考文献

### 一次ソース
| ソース | URL | 用途 |
|--------|-----|------|
| Mamba-3 論文 (arXiv) | https://arxiv.org/pdf/2603.15569 | アーキテクチャ・ベンチマーク |
| Mamba GitHub | https://github.com/state-spaces/mamba | 実装・モデル |
| Tri Dao ブログ | https://tridao.me/blog/2026/mamba3-part1/ | 設計動機・直感的解説 |
| Mamba-3 OpenReview | https://openreview.net/forum?id=HwCvaJOiCj | 査読・最終版 |

### 関連論文
| 論文 | URL |
|------|-----|
| Mamba-2 (SSD) | https://arxiv.org/abs/2405.21060 |
| RetNet | https://arxiv.org/abs/2307.08621 |
| xLSTM | https://arxiv.org/abs/2405.04517 |
| RWKV-7 | https://arxiv.org/abs/2503.14456 |

---

> **分析手法**: マルチモデル並列リサーチ。Claude (技術解説・ベンチマーク構造化)、Gemini (Google Search grounding によるエコシステム調査)、Codex gpt-5.4 (reasoning_effort=high による戦略分析) を並列実行し、結果を集約・クロスバリデーション。
