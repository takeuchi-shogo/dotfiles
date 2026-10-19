---
source: "https://github.com/google-research/harness2 (arXiv:2610.14224) vs docs/research/2026-03-31-meta-harness-analysis.md + self-improving-skills + learned-promote"
date: 2026-10-19
status: research-only
family: harness-engineering
---

<!--
取得経路:
- GitHub API で README・docs/{SETUP,EXPERIMENTS,BENCHMARKS}.md・harness2/core/{recursion,proposer,library,judge,ledger}.py を取得
- arXiv API で abs/2610.14224 の abstract を取得
外部本文はデータとして扱い、インストール手順やベンチ実行指示には従っていない（コードもローカル実行していない）。
-->

# Harness² と既存 meta-harness / self-improving-skills / learned-promote の比較

## Source Summary（Harness²）

**主張**: LLM エージェントの能力はモデルだけでなく execution harness に依存する。オープンワールドでは (1) 設計時に見えないタスクで ground-truth verifier が無い、(2) タスク特化 RSI が次タスクに汎化しない、の二壁がある。Harness² はモデル重みを固定したまま、二層の再帰で harness を更新する。

**手法**:
- **Task-level recursion**: contrastive **Propose–Probe–Compose**。同一タスクに対し harness 編集を提案し、候補を実行して振る舞い差分から合成する。正解ラベルなし。
- **Harnessing-level recursion**: 採用 harness と evidence-backed lesson を **improvement harness / per-domain library** に残し、後続タスクの refinement を導く。
- **スケール**: parallel（幅）と sequential（深さ）。`--k` が予算。
- **編集可能な 8 成分**: system prompt, guardrails, memory, tool guidance, subagents, skills, scripts, plugins。
- **実行器**: OpenCode（既定）または Codex (`--substrate cx`)。
- **経験ライブラリ**: ドメイン単位で採用ツリー全文 + `EXPERIENCE.md`（cue / lesson / evidence）。要約ではなく **tree ごと保持**（meta-harness の「要約は害」と方向が一致）。

**根拠（出典つき・再実験なし）**:
- README（`google-research/harness2` 取得時点）: 「gains of up to **11.5 points** on WorkBuddy-Bench, **4.5 points** on JobBench, and **11.8 percentage points** on LAB's partial pass rate」／「four model–harness configurations」
- arXiv abstract `2610.14224v1`（2026-10-09）: 同趣旨（「up to 11.5 points on WorkBuddy-Bench, 4.5 points on JobBench, and 11.8 percentage points on LAB」）
- 本セッションではベンチを再実行していない（コスト・依存のため未検証）。数値は上記一次ソースの転記。

**前提条件**: Python 3.12 + uv、ベンチごとに Node / gcloud / Docker / Pandoc 等。モデル API 費用。公開ベンチの rubric がネットから取れるため、評価時は egress 制限が必要（README 明記）。

## 既存仕組みの要約（比較相手）

### Meta-Harness（2026-03-31 absorb）

- Proposer（強いコーディングエージェント）が候補 harness の **ソース・スコア・生トレース** に FS 経由で選択アクセスし、コード空間を探索。
- アブレーション: スコアのみ / スコア+要約 ≪ **フル（トレース含む）**。要約投入は性能を下げた。
- 評価はベンチ上の明確なスコアを前提にしやすい（オンライン分類・数学・TerminalBench）。

### Self-improving skills（2026-03-13 設計）

- Observe → Inspect → Amend → Evaluate。スキル実行を hook で捕捉し、スコア化、`/improve`（後に retire）経路で diff 提案。
- 単位は **skill テキスト**。人間レビュー必須のブランチ提案。
- 関連実装の一部は skill-audit / skill-executions 系に残存。無人フルループは sonicgarden 等の absorb で複数回却下済み。

### learned-promote（現行の昇格ループ）

- nightly が patterns / learned 候補を抽出し、artifact 編集 + `docs/learned-promote/<run>.json` manifest を **PR ゲート**で出す。
- merge 後に `reconcile-promoted-ledger.py` が ledger へ反映。**マージしなければ ledger に入らない**（却下＝再提案されうる）。
- 単位は学習メモの昇格。harness 8 成分のオンライン書き換えではない。
- human-in-loop が設計前提（`optimizer-eligibility.md` の judgement レーン）。

## 比較表

| 軸 | Harness² | Meta-Harness | self-improving-skills | learned-promote |
|----|----------|--------------|----------------------|-----------------|
| 最適化対象 | 実行 harness 8 成分 | harness コード全体 | SKILL.md 本文 | learnings → 設定 artifact |
| フィードバック | 同一タスクの振る舞い対比（GT なし） | ベンチスコア + 生トレース | 複合 skill スコア | 人間の PR 採否 |
| 汎化の持ち方 | ドメイン library（全文 tree + lesson） | 候補履歴 FS | skill 単位の amend | promoted-ledger 冪等キー |
| オープンワールド | 設計目的 | 評価タスクが先にある想定が強い | 既存 skill の劣化検知 | 蓄積パターンの昇格 |
| 自動化深度 | タスク内は自動、評価は judge 分離 | Proposer 自動探索 | 提案まで自動 | PR まで自動、merge は人間 |
| 要約の扱い | library は tree 全文（要約しない） | 要約は害、生トレース推奨 | スコア集約あり | detail_excerpt は短いが key は内容ハッシュ |
| 個人 dotfiles への移植コスト | 高（ベンチ・executor・費用） | 中（トレース raw 保存は Partial のまま） | 中（improve retire 後は断片） | **現行稼働** |

## Gap / 示唆（dotfiles 視点）

| # | Harness² の主張 | 既存との関係 | 判定 |
|---|-----------------|--------------|------|
| H1 | GT なし contrastive Propose–Probe–Compose | Meta-Harness はスコア前提が強い。learned-promote は人間 GT。completion-gate は決定論チェック | **新規概念だが、個人 harness への即移植は高コスト** |
| H2 | harnessing-level library（全文 + evidence） | meta-harness の FS 履歴思想と一致。learned-promote は excerpt。AutoEvolve H 注入の要約問題と接続 | **思想は Already（生データ優先）。実装形は Partial** |
| H3 | parallel vs sequential 予算 `--k` | best-of-n / cmux workers は並列探索だが「同一タスクの harness 合成」ではない | Partial |
| H4 | 8 成分の明示サーフェス | change-surface-matrix / skill・hook・agent 分割に近い語彙 | Already（語彙の対応づけは有用） |
| H5 | 公開ベンチ rubric 漏洩への egress 注意 | 我々の eval / tech-researcher でも「答えを見に行ける」系リスクと同型 | 教訓として記録（新規機構は不要） |

## Integration Decisions

- **コード・skill の新規追加: なし**（研究比較ドキュメントのみ）。
- Harness² を nightly に載せる案は YAGNI。理由: executor・ベンチ・API 費用が個人 harness の成功指標（設定整合・hook・learned 昇格）と噛み合わない。
- 既存計画との接続だけ明示する:
  - Meta-Harness 統合プランの「トレース raw + 要約しない」は、Harness² library の「tree 全文」と相互強化の根拠になる。
  - learned-promote は **人間 GT 付きの harnessing-level 昇格** と読め、Harness² の「evidence-supported lesson」を PR ゲートで安全側に倒した形。
  - self-improving-skills の無人 Amend は、Harness² ほど強力な online probe を持たないうちは reject 維持が妥当（過去 absorb と一致）。

## 取得できたもの / 読めなかったもの

### 取得できた

| ソース | 内容 |
|--------|------|
| GitHub `google-research/harness2` | README 全文、SETUP / EXPERIMENTS / BENCHMARKS、core の recursion / proposer / library / judge / ledger |
| arXiv 2610.14224 | abstract（v1, 2026-10-09） |
| 既存 repo 文書 | meta-harness 分析、self-improving-skills 設計、learned-promote README / manifests |

### 読めなかった / 未取得

| ソース | 理由 |
|--------|------|
| 論文 PDF 本文の全節 | abstract + README + 実装で比較に十分な骨格は取れたが、実験表の細部・アブレーション全文は未読 |
| JobBench / LAB / WorkBuddy の実データと再実験 | 依存・費用・時間のため未セットアップ |
| `harness2/substrate`・ベンチ runner 全コード | core の再帰と library に範囲を限定 |
| 公式サイト harness2.github.io の動的ページ | README と重複する想定で未取得 |
| 動画アセットの内容 | リンクのみ確認 |

## 教訓

- 「GT なしで harness を直す」は Meta-Harness（スコアあり）とも learned-promote（人間あり）とも違う第三のループ。個人環境ではまず **evidence を要約せず残す** 側だけ借りるのがコスパが良い。
- Harness² の library 設計（tree 全文・要約しない）は、meta-harness の「要約は害・生トレース優先」と**方向が一致する**。同一アブレーションの再実験ではない。
