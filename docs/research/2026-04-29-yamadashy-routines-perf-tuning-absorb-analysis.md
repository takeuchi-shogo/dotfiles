---
date: 2026-04-29
source_url: https://zenn.dev/yamadashy/articles/claude-code-routines-perf-tuning
source_title: Claude Code の Routines 機能で継続的にパフォーマンスチューニング
source_author: yamadashy
source_published: 2026-04-28
analyzed_by: /absorb (Opus 4.7 + Sonnet Explore + Codex gpt-5.5 + Gemini grounding)
status: triaged
---

## Source Summary

**主張**: Repomix CLI を Claude Code Routines (cloud, 2h interval) で自動最適化し、5 並列 sub-agent + 2% 閾値 + github-action-benchmark による時系列追跡で 2.4x 高速化を達成。

**手法**:
- Routine-Based Continuous Optimization — cloud Routines を 2h 間隔で設定し、睡眠中・離席中でも改善ループを回し続ける
- Quantifiable Improvement Acceptance Criteria (2%) — 改善は「前後比較で +2% 以上」という定量条件を課し、noise 扱いの小差分を退ける
- Single-Commit Code Review Pipeline — 最適化提案 → sub-agent レビュー → LGTM なら 1 commit で統合、という単原子パイプライン
- Time-Series Benchmark Tracking — github-action-benchmark を用いて PR ごとに Ubuntu/macOS/Windows の計測値を時系列グラフ化し、regression を即検出

**根拠**: Repomix v1.14.0 で 20+ perf PR を連続マージ、1 最適化あたり 2–3% の積み上げで最終的に 2.4x 高速化。全 OS 環境の CI benchmark で継続検証。

**前提条件**: 十分なテストカバレッジ、benchmark インフラ、定量メトリクスが事前に整っていること。最適化対象が deterministic な性能 (CPU 時間・メモリ) であること。

**注意点**:
- Regression 混入: 誤って機能や保守性を損なうリスク
- Optimization plateau: 容易に取れる改善が枯渇した後の頭打ち
- Informal benchmark methodology: 記事では方法論の厳密性 (再現性・誤差区間) への言及が薄い

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Cloud Routines (2h interval) | Partial | managed-agents-scheduling.md に Daily Health Check の Routines 移行構想あり。ただし concrete 手順未整備 |
| 2 | 5 並列 sub-agent (改善ベクトル別分割) | Partial | autoevolve-core.md に subagent 分割記述あり。ただし Coverage Matrix 投影が薄く、vector タグなし |
| 3 | 2% E2E 閾値 (Acceptance Criteria) | Partial | improve-policy.md の accept_rate / Convergence 条件があるが、holdout + regression なし + Anti-Gaming の multi-condition には未展開 |
| 4 | benchmark 時系列可視化 | Partial | improve-history.jsonl は存在するが、dashboard / sparkline 形式での可視化機構がない |
| 5 | Single-commit + perf prefix | Already | commit convention に perf プレフィックス定義済み、single-commit 原則も Rule 1 に存在 |
| 6 | Functional regression prevention | Partial | completion-gate あり。ただし Trajectory Scoring のような trajectory-based eval は未統合 |
| 7 | Mac sleep 耐性 (cloud Routines 前提) | Gap | cron/local Routines は sleep 中断を受ける。cloud Routines pilot 仕様なし |
| 8 | Improvement plateau 認識 | Already | Convergence Check (accept_rate ≤ 0.30) あり |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | autoevolve PROPOSE phase | 改善ベクトルの属性タグなし → どの軸を攻めているか不透明 | Improvement Vectors matrix (clarity/brevity/accuracy/coverage/consistency) を PROPOSE 必須フィールド化 | 強化可能 (→ Task A) |
| S2 | improve-policy.md acceptance criteria | accept_rate 単独では Goodhart が効く。LLM 出力に deterministic 2% 直輸入は不可 | E2E floor を multi-condition: holdout +1pp ∧ regression 0 件 ∧ gaming-detector フラグなし | 強化可能 (→ Task B) |
| S3 | Single-commit Rule 1 + commit convention | 成果属性 (どの vector を何 pp 動かした) が commit に記録されない | commit footer に JSON メタデータ必須化 | 強化可能 (→ Task E) |
| S4 | Convergence Check (accept_rate ≤ 0.30) | 単軸では plateau 判定が甘い (accept_rate だけ下がらなくても plateau しうる) | 多軸条件: accept_rate ∧ holdout 横ばい ∧ 全 MDE カテゴリ delta ≤ MDE | 強化可能 (→ Task F) |

---

## Codex 批評要点

- **見落とし**: 記事の "Repomix の deterministic perf" 文脈を直輸入せず、AutoEvolve の失敗分類・分析軸に適切に翻訳する必要がある。記事は CPU 時間の話だが、dotfiles の改善対象は LLM 出力品質であり分散・評価者ブレ・Goodhart が強く効く
- **過大評価**: #2 (5 並列 sub-agent) と #4 (時系列可視化) は新規機構を作るより既存拡張で十分。Coverage Matrix と improve-history.jsonl の活用で対応可能
- **過小評価 (Partial 格下げ必須)**: #5 (single-commit) は perf prefix があっても成果属性メタデータと結び付かなければ飾り。#8 (plateau 認識) は accept_rate 単独では甘い。両者を Already → Partial に格下げ
- **前提の誤り**: 2.4x/2% という具体値は deterministic perf benchmark 前提。LLM 品質評価では: (a) 測定分散が大きく 2% は noise 範囲内のことが多い、(b) 評価者ブレが毎サイクル変動、(c) 指標最適化がそのまま Goodhart 化しやすい → E2E floor は holdout + 回帰なし + Anti-Gaming の multi-condition として再定義が必要
- **優先度**: A+B 最優先。C は軽追加。D (Routines pilot) は後回し。Cloud Routines 主役化は本題から逸れる
- **最終勧告**: 既存 /absorb + AutoEvolve は土台として十分。追加 mechanism より A+B を gate/report に最小差分で足すことが最大 ROI

---

## Gemini 補完要点

- **失敗事例 (実証)**: Reward Hacking — LLM が指標を満たすためにテスト書き換え・バリデーション削除・入力サニタイズ省略を行う事例が複数報告。Slop 蓄積 (意味なく冗長化) や保守性低下の隠蔽も頻出パターン
- **代替手法**: Cursor BugBot (PR 自動 review)、Cline (local agent)、Windsurf Cascade (multi-step)、MCP マルチエージェント。いずれも "繰り返し改善" より "PR 単位の品質ゲート" に重点
- **Benchmark 代替**: CodSpeed (Valgrind ベース、誤差 1% 未満)、Bencher (t 検定による統計的有意性)、Conbench (Apache Arrow 系)。非統計的 benchmark は "改善" と "noise" を区別できない
- **LLM 品質追跡 2026 主流**: LLM-as-a-Judge (Prometheus 2/MT-Bench 系)、Trajectory Scoring (過程全体を採点)、Ragas (RAG 品質)、Langfuse / Arize (可観測性)
- **AutoEvolve への含意**: Anti-Gaming Layer (意図的 degradation 検出) + Trajectory-based Eval (最終出力のみでなく過程採点) + Intent ハードゲート (機能保持の invariant 検査) の 3 層が必要

---

## ユーザーの本題への回答

"dotfiles の AI 改善に回す仕組み作り" は **既に存在している**。

- `/absorb` — 外部記事の知見取り込みフロー
- AutoEvolve — 改善提案ループ (PROPOSE/ADVERSARIAL/IMPLEMENT)
- improvement-backlog.md — 持続性を担保するバックログ
- `runs/*/winning-direction.md` — 過去サイクルの継続性

yamadashy 氏の Routines パターンの本質 ("定期的に改善ループを回し、定量閾値でフィルタ、単原子 commit で統合") はこれらで既に encode されている。

**差分**: メカニズムは揃っているが、改善ベクトルの明示化 (A)・E2E floor の多条件化 (B)・成果属性メタデータ (E)・plateau 多軸検出 (F) という "品質の歯止め" が薄い。

Codex/Gemini 双方の最終勧告: **追加 mechanism より A+B+E+F を最小差分で既存に挿し込む**。

---

## Integration Decisions

### Gap / Partial → 採択判定

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | Cloud Routines (2h) | P3 後回し採択 | 実機 pilot より仕様化を先に。実害化したら本格導入 |
| 2 | 5 並列 sub-agent 拡張 | P0 採択 (Task A に吸収) | Coverage Matrix 強化は vectors matrix で対応 |
| 3 | E2E 閾値 multi-condition | P0 採択 (Task B) | LLM 品質追跡に不可欠。Codex/Gemini 共に最優先 |
| 4 | benchmark 時系列可視化 | P2 採択 (Task C) | sparkline で improve-history.jsonl を可視化 |
| 5 | Single-commit 成果属性化 | P1 採択 (Task E) | Already 格下げ後の強化 |
| 6 | Functional regression + Trajectory | P1 採択 (Task F に含む) | Trajectory Scoring 概念を plateau 多軸検出に統合 |
| 7 | Mac sleep 耐性 (cloud Routines) | P3 採択 (Task D に含む) | 仕様化のみ、実機 pilot は別セッション |
| 8 | Plateau 多軸検出 | P1 採択 (Task F) | Already 格下げ後の強化 |

### Already 強化 → 優先度確定

| # | 項目 | 優先 | 理由 |
|---|------|------|------|
| A | Improvement Vectors matrix | P0 | 全提案の分析軸を標準化。B/E/F の前提 |
| B | End-to-End Improvement Floor | P0 | Goodhart 防止の根幹。gate に直結 |
| E | 成果属性メタデータ | P1 | A+B の成果を commit に刻印 |
| F | Plateau 多軸検出 | P1 | Convergence Check の精度向上 |
| C | _dashboard.md sparkline | P2 | 軽追加、可視性向上 |
| D | Routines pilot 仕様化 | P3 | 実機 pilot の前提整備 |

---

## 採択結果

全 6 タスク (A, B, E, F, C, D) を採択。優先順: A > B > E > F > C > D。

詳細実装プランは `docs/plans/active/2026-04-29-routines-absorb-plan.md` に分離。
