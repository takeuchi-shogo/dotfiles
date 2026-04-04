---
name: improve
description: >
  AutoEvolve のオンデマンド改善サイクルを実行。学習データの分析 → 知識整理 → 設定改善提案を一括で行う。/improve で起動。
  Triggers: '/improve', '改善提案', '設定見直し', 'autoevolve', 'optimize setup'.
  Do NOT use for: 外部記事の統合（use /absorb）、スキル個別の改善（use /skill-creator）、コードベース監査（use /audit）。
allowed-tools: Read, Bash, Grep, Glob, Agent
metadata:
  pattern: pipeline
disable-model-invocation: true
---

# AutoEvolve v2 — Codex-Backed Adversarial Quality Pipeline

蓄積されたセッション学習データを分析し、Claude Code の設定改善提案を生成する。
**Codex (gpt-5.4) による深掘り分析と敵対的レビューを必須とし、
Propose → Adversarial ループで提案を精錬してから報告する。**

## パイプライン全体像

```
Phase 1: COLLECT (+ backlog/winning-direction 読み込み)
    ↓
Phase 2: ANALYZE (Sonnet meta-analyzer + Codex Deep)
    ↓
Phase 3: PROPOSE (Ideation-Debate → Codex ROI 判定 → 勝者で提案生成)
    ↓
Phase 4: ADVERSARIAL GATE (Codex 必須) ←─┐
    ↓                                      │
    ├── All ROBUST → Phase 5               │
    ├── VULNERABLE → REFINE ───────────────┘ (max 2 iterations)
    └── FATAL_FLAW → Phase 5 (却下記載)
    ↓
Phase 5: REPORT (+ per-run artifacts + backlog 更新)
```

## オプション

- `--deep`: Phase 2b で Teacher-Student 比較も実行（コスト高）
- `--evolve`: Phase 5 後にイテレーティブ進化ループを追加実行
- `--iterations N`: evolve ループ回数（デフォルト: 3、最大: 5）
- `--skills skill1,skill2`: 対象スキルを手動指定
- `--single-change`: 1 イテレーション 1 変更に制限

## Phase 1: COLLECT

**詳細: `instructions/data-collection.md` を Read**

データ収集を 4 ステップに統合:

1. **データ可用性チェック** — `learnings/*.jsonl`, `metrics/`, `traces/` の存在と件数確認
2. **Git Context 収集** — `git log --oneline -30` で直近の変更傾向を把握。learnings が少なくてもここから仮説を立てる
3. **タスク成果追跡** — `learnings/` から `type: "feature_completion"` エントリを抽出し、成功/失敗パターンを集計する。`feature_list.json` が存在する場合はカテゴリ別の完了率・所要セッション数も参照。「推奨→実行→結果」の因果チェーンを構築し、Phase 2 の分析入力とする
4. **Open Coding（任意）** — ユーザーに「気になるパターンは？」を聞く。スキップ可

前回 /improve の Issue 棚卸し（`gh issue list --label autoevolve`）もここで実行。

5. **Negative Knowledge 参照** — `references/negative-knowledge.md` を Read し、直近の failure パターンを分析候補に追加する。テーブルが空ならスキップ。Phase 3 の提案生成時にこれらのパターンに該当する提案を回避する。

### Convergence Check（自動）

`~/.claude/agent-memory/metrics/improve-history.jsonl` の直近5件を確認:

```bash
tail -5 ~/.claude/agent-memory/metrics/improve-history.jsonl 2>/dev/null | jq -r '.adoption_rate'
```

- 5件の平均 adoption_rate ≤ 0.30: **CONVERGENCE DETECTED** — プラトー警告を表示:
  「改善余地が縮小しています。`/audit`, `/refactor-session`, `/improve --deep` を検討してください」
- 5件未満: スキップ（データ蓄積中）
- 5件の平均 > 0.30: 通常通り Phase 2 へ進む

4. **前回ラン状態の読み込み** — `~/.claude/agent-memory/improvement-backlog.md` と最新の `runs/*/winning-direction.md` を Read。存在しない場合はスキップ（初回実行時）。Phase 3 の autoevolve-core プロンプトに注入する。

## Phase 2: ANALYZE — Coverage Matrix + Codex Deep

**品質の根幹。2段構成で網羅性と深度を両立する。**

### Phase 2a: Coverage Matrix Analysis (meta-analyzer, Sonnet)

**`references/coverage-matrix.md` を Read** し、全カテゴリの必須問いに回答する。

- 各カテゴリに定義された必須問いに `ANSWERED` / `INSUFFICIENT_DATA` / `NOT_APPLICABLE` で回答
- **「問題なし」と「データ不足」を絶対に混同しない**
- データ要件を満たさないカテゴリも `INSUFFICIENT_DATA` で全問い埋める（スキップ禁止）

Agent ツールで `meta-analyzer` を起動し、Coverage Matrix を完成させる:

```
references/coverage-matrix.md に定義された全必須問いに回答してください。
データディレクトリ: ~/.claude/agent-memory/
各問いに ANSWERED / INSUFFICIENT_DATA / NOT_APPLICABLE で回答し、
ANSWERED の場合は具体的な evidence（件数, session_id, ファイル名）を含めてください。
```

### Phase 2b: Codex Deep Analysis（必須）

Phase 2a の Coverage Matrix 結果を **Codex (gpt-5.4)** に渡し、分析を深掘りする。

`codex exec` を使用:

```bash
codex exec -m xhigh "
以下の Coverage Matrix 結果を検証し、補強してください。

## 検証観点
1. ANSWERED 項目の深度チェック: 根本原因が浅い分析を指摘
2. 見落としパターン: Matrix に含まれない重要な分析観点の追加
3. クロスカテゴリ構造: 複数カテゴリにまたがる構造的問題の検出
4. 分析品質レーティング: 各カテゴリを THOROUGH / ADEQUATE / SHALLOW で判定

## Coverage Matrix 結果
{coverage_matrix_results}

## 出力
JSON で以下を返してください:
{
  \"category_ratings\": {\"errors\": \"THOROUGH|ADEQUATE|SHALLOW\", ...},
  \"shallow_reasons\": {\"category\": \"理由\"},
  \"missed_patterns\": [\"見落としパターン\"],
  \"cross_category_insights\": [\"構造的問題\"],
  \"deepened_root_causes\": [{\"original\": \"...\", \"deeper\": \"...\"}]
}
"
```

**SHALLOW 判定のカテゴリ**: Codex の指摘を踏まえて meta-analyzer に追加分析を依頼してから Phase 3 に進む。

## Phase 3: PROPOSE

**詳細: `instructions/proposals-report.md` を Read**（Phase 3 セクション）

Phase 2a + 2b の統合結果を入力として、autoevolve-core (Sonnet) が改善提案を生成。

autoevolve-core 起動時のプロンプトに以下を含める:
- 「Phase 2.0 Ideation-Debate を実行し、3候補から Codex で ROI 最大を選定してから提案生成せよ」
- Phase 1 で読み込んだ `improvement-backlog.md` と `winning-direction.md` の内容（存在する場合）

**全提案に以下の必須フィールド** を含めること（欠落した提案は Phase 4 に進めない）:

```yaml
proposal:
  id: "IMP-YYYY-MM-DD-NNN"
  summary: "提案の1文要約"
  
  serves_principles:      # どの core principle を推進するか
    - "KISS: ..."
  tension_with:           # どの principle と緊張関係にあるか（なければ空）
    - "YAGNI: ..."
  
  pre_mortem: "この提案が失敗する場合、最も可能性が高い原因は..."
  
  blast_radius:
    direct: ["変更対象ファイル"]
    indirect: ["間接的に影響を受けるファイル/システム"]
  
  evidence_chain:
    data_points: 7
    confidence: 0.8
    specific_refs: ["session-xxx:line42", "errors.jsonl:entry15"]
    reasoning: "X のデータから Y が示唆される、なぜなら Z"
    counter_evidence: "ただし W の可能性も排除できない"
  
  rollback_plan: "復旧手順"
```

## Phase 4: ADVERSARIAL GATE（Codex 必須）

**詳細: `instructions/phase4-adversarial-gate.md` を Read**

全提案を Codex (gpt-5.4) に渡し、5 観点（原則違反, 考慮漏れ, 証拠の弱さ, Pre-mortem の甘さ, 代替案の欠如）で敵対的レビュー。

各提案に判定を付与:
- **ROBUST**: 5 観点全てで重大な問題なし → 推奨
- **VULNERABLE**: 1-2 観点で注意が必要 → REFINE ステップへ
- **FATAL_FLAW**: 致命的な問題 → 即時却下

### Propose-Adversarial ループ

```
Phase 3 → Phase 4 → VULNERABLE? → REFINE → Phase 4（再実行）
                                           ↑ max 2 iterations
```

- VULNERABLE 提案: Codex の具体的な指摘を反映して autoevolve-core が修正版を生成 → 再度 Phase 4
- **最大 2 イテレーション**（初回 + 精錬 1 回）
- 2 回後も VULNERABLE なら注意付きでレポートに含める
- FATAL_FLAW は再提案しない（根本的な方向性の問題）
- 精錬で新規提案は追加しない（スコープ制御）

## Phase 5: REPORT

**詳細: `instructions/proposals-report.md` を Read**（Phase 5 セクション）

### レポート構造

```markdown
# /improve レポート — YYYY-MM-DD

## TL;DR — Top Actions

> ROBUST 判定の提案のみ。3 件以下に絞る。

1. [ROBUST] {提案概要} — 根拠: {1文} / 効果: {1文}
2. ...

## 前回 /improve からの変化

- 前回提案の実施状況: N/M 完了
- 効果測定結果: ...

## Coverage Matrix 結果

| カテゴリ | Codex 品質判定 | ANSWERED | INSUFFICIENT | 主要 findings |
|---------|---------------|----------|-------------|--------------|
| errors | THOROUGH | 4/5 | 1/5 | ... |
| ... | ... | ... | ... | ... |

## 全提案一覧

| ID | 提案 | Serves | Tension | Codex Rating | Loop | Action |
|----|------|--------|---------|-------------|------|--------|
| 001 | ... | KISS | - | ROBUST | 1/1 | 推奨 |
| 002 | ... | DRY | YAGNI | VULNERABLE→ROBUST | 2/2 | 推奨(精錬済) |
| 003 | ... | - | KISS | FATAL_FLAW | 1/1 | 却下 |

## Adversarial Review 詳細

{各提案の Codex レビュー全文。精錬履歴も含む}

## Blind Spot Declaration

以下の領域は今回の分析でカバーできていません:
- {INSUFFICIENT_DATA だったカテゴリと理由}
- {Codex が指摘した missing_proposals}

## 次回への申し送り

- {Codex の missing_proposals}
- {INSUFFICIENT_DATA の解消に必要なデータ}
- {VULNERABLE のまま残った提案の追加検証事項}
- → 詳細は `~/.claude/agent-memory/improvement-backlog.md` を参照
```

### Per-run アーティファクト出力

Phase 5 完了時に `~/.claude/agent-memory/runs/YYYY-MM-DD/` に書き出す:

| ファイル | 内容 |
|---------|------|
| `candidates.md` | Ideation-Debate の3候補 |
| `debate-log.md` | Codex ROI 判定理由 |
| `winning-direction.md` | 選ばれた方向性と根拠 |
| `run-summary.json` | メトリクス（提案数, ROBUST/VULNERABLE/FATAL_FLAW 数, backlog 更新有無） |

### improvement-backlog.md の更新

`~/.claude/agent-memory/improvement-backlog.md` を更新する:
- **次ラン優先テーマ**: ROBUST だが未実施の提案、VULNERABLE のまま残った提案
- **却下された方向性**: FATAL_FLAW + Ideation-Debate 敗退候補（理由付き）
- **データ不足で保留中**: INSUFFICIENT_DATA カテゴリの追跡項目

## --evolve モード

Phase 5 完了後にイテレーティブ進化ループを実行する。
**詳細: `instructions/evolve-mode.md` を Read**

evolve モードでも Adversarial Gate は各イテレーションで適用される。

## Outcome Validation（複利ループ）

ROBUST 提案が実施された後、次回 `/improve` 実行時に効果を検証する。
「推奨→実行→結果」の因果チェーンを閉じ、改善の複利効果を生む。

### 検証タイミング

- Phase 1 Step 3（タスク成果追跡）で自動的に前回提案の実施状況を確認
- Phase 5 レポートの「前回 /improve からの変化」セクションに結果を記載

### 検証方法

各実施済み提案について以下を記録（`templates/experiment-log.md` を使用）:

| 項目 | 内容 |
|------|------|
| **提案 ID** | IMP-YYYY-MM-DD-NNN |
| **実施日** | YYYY-MM-DD |
| **Before 指標** | 提案時の evidence_chain.data_points |
| **After 指標** | 実施後に同じ指標を再計測 |
| **効果判定** | POSITIVE / NEUTRAL / NEGATIVE |
| **学習** | 何が効いた/効かなかったか（1文） |

### 蓄積と活用

- 結果は `~/.claude/agent-memory/metrics/improve-history.jsonl` に追記
- POSITIVE な提案パターンは次回の Phase 3 Ideation-Debate で優先候補に
- NEGATIVE な提案パターンは `references/negative-knowledge.md` に追加し、同種の提案を回避
- 3サイクル以上の蓄積で「効果が出やすい改善カテゴリ」が可視化される

## Skill Assets

- Coverage Matrix: `references/coverage-matrix.md`
- Adversarial Gate 手順: `instructions/phase4-adversarial-gate.md`
- 分析カテゴリ判断基準: `references/analysis-categories.md`
- 改善レポートテン��レート: `templates/improvement-report.md`
- 実験ログテンプレート: `templates/experiment-log.md`

## Anti-Patterns

| NG | 理由 |
|----|------|
| Codex 実行をスキップする | 単一モデルの分析は盲点を見逃す。Codex は必須 |
| データなしで改善提案する | 学習データに基づかない提案は的外れになる |
| 1 サイクルで 10 件以上変更する | 消化不良。1 サイクル最大 3 ファイル |
| Adversarial Gate なしで提案する | 品質保証なしの提案は信頼性が低い |
| FATAL_FLAW を精錬で救おうとする | 方向性が間違っている提案は捨てる |
| 「問題なし」と「データ不足」を混同する | Coverage Matrix で明示的に区別する |

## 注意事項

- このスキルは **読み取り + 分析 + 提案** が目的。master への直接変更は行わない
- improve-policy.md の全ルールに従う
- データが少ない段階では「データ不足」を正直に報告する（無理に分析しない）
- 各エージェントの実行結果が空・エラーの場合は、その旨をレポートに記載して続行
