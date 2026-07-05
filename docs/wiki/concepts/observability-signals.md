---
title: 観測可能な信号設計
topics: [harness, tooling, decision]
sources:
  - 2026-04-26-workflow-trellis-absorb-analysis.md
  - 2026-05-04-sessionstart-audit.md
updated: 2026-07-05
confidence: emerging
source_count: 2
last_validated: 2026-07-05
---

# 観測可能な信号設計

## 概要

エージェント/hook が出す信号は、診断や次のアクションに使えなければ実質的に価値がない。この概念は、信号を「どこに流れるか（stdout/stderr）」「誰がどう反応すべきか（interrupt/batch/escalate/hide/shut up）」の2軸で設計し、実測によって裏付けることを指す。SessionStart hook監査は、cache prefixに影響する経路（stdout）と影響しないUI表示（stderr）を実測で切り分け、Workflow Trellisのフレームワークは注意配分を5つの動詞に分解した。

## 主要な知見

- stdoutはadditionalContextとしてシステムプロンプト/cache prefixに流入するため揮発的な出力を避ける必要があるが、stderrはUI表示のみでcache prefixには影響しない。当初「session-load.jsの揮発出力がcacheを壊す」と想定していたが、実測でstderr経由と判明し前提が覆った [EXTRACTED, conf=90]
- 5つの注意配分動詞（interrupt/batch/escalate/hide/shut up）を信号タイプごとに一意に割り当てるdecision tableが有効。同一信号に2動詞を割り当てない、hideは暗黙ではなく明示的に選択する、連続してPASSが続く信号はescalate→batch→hideの順に自動降格させる、という運用ルールが伴う [EXTRACTED, conf=85]
- 実測ベースの監査スクリプト（stdout/stderrバイト数、wall-clock latency、揮発性フラグを1回の実行で計測）を導入した結果、hook合計latencyが3.20秒から0.92秒へ71%削減された [EXTRACTED, conf=90]
- Relief Pressure（負担軽減の圧力）とControl Demand（統制要求）の2軸フレームは、個人開発の文脈ではControl Demandが薄く、Relief Pressure最大化が設計の主軸になる。SaaSチーム設計を前提にした枠組みをそのまま個人harnessに持ち込むと過剰設計になる [EXTRACTED, conf=75]
- Markus Meister 2024年の査読論文（人間の意識的情報処理帯域は毎秒10ビット程度）が、「shut up」動詞の必要性やメモリファイルの行数上限といった簡潔性原則の学術的根拠として使える [EXTRACTED, conf=70]
- 信号の監査は「何が起きたか」の計測と「それがcache prefixにどう波及するか」の因果分析を分けて扱う必要がある。両者を混同すると、影響のない揮発出力まで過剰に削減対象にしてしまう [INFERRED, conf=70]

## 実践的な適用

dotfilesでは `references/observability-signals.md` に注意配分の5動詞×信号タイプのdecision tableを追加し、`references/stage-transition-rules.md` にはS規模でもGateを強制すべきケース（auth変更・不可逆操作・harness変更・breaking change）を明文化した。継続監査は `scripts/runtime/sessionstart-audit.py` で単独実行できる。

## 関連概念

- [harness-engineering.md](harness-engineering.md) — hookやscaffoldingの設計原則という上位概念
- [quality-gates.md](quality-gates.md) — 信号を受けた後の検証チェックポイント設計

## ソース

- [Workflow Trellis (2x2フレームワーク) absorb分析](../../research/2026-04-26-workflow-trellis-absorb-analysis.md) — 2軸ワークフロー設計論を分析、3件を既存参照に統合
- [SessionStart Hook監査レポート (absorb 9patterns T2)](../../research/2026-05-04-sessionstart-audit.md) — SessionStartフック6個を実測監査、latency 71%削減実施
