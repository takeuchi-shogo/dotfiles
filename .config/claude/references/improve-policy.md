# AutoEvolve 改善ポリシー

> このファイルは karpathy/autoresearch の program.md に相当する概念的ガイドである。
> AutoEvolve エージェントが設定を改善する際の方針・制約・優先度を定義する。
> ユーザーがこのファイルを編集することで、改善の方向性を操作できる。

## 改善の優先度

以下の順序で改善を優先する:

1. **精度向上** — プロジェクトごとの規約・パターンを正しく適用できるようにする
2. **エラー削減** — 繰り返し発生するエラーの根本原因を解消する
3. **コンテキスト効率** — 同じタスクにかかるトークン消費を削減する
4. **速度向上** — hook の実行時間、エージェントの応答時間を改善する

## 改善対象

### 優先的に改善して良いもの

- `references/error-fix-guides.md` — エラーパターン→修正マップの追加
- `rules/common/*.md` — 品質ルールの追加・改善
- `references/golden-principles.md` — 自動検証パターンの追加
- `agents/*.md` — エージェント定義のプロンプト改善
- `skills/*/SKILL.md` — スキルの手順改善

### 慎重に扱うべきもの（差分を小さく）

- `scripts/{runtime,policy,lifecycle,learner}/*.py|*.js` — hook スクリプトの変更
- `settings.json` — hook 登録の追加・変更
- `CLAUDE.md` — コア原則の変更

### 変更禁止

- API キー・トークン・パスワードに関する設定
- `permissions` セクション（allow/deny リスト）
- `model` 設定の変更
- 他人のプロジェクト固有の設定

## 実験カテゴリ

| カテゴリ | 変更対象 | スコアリング基準 |
|---------|---------|----------------|
| errors | `references/error-fix-guides.md` | 同一エラーの再発回数 |
| quality | `references/golden-principles.md`, `rules/` | 同一ルール違反の頻度 |
| agents | `agents/*.md` | タスク完了までのターン数 |
| skills | `skills/*/SKILL.md` | skill-executions.jsonl の平均スコア (Failing→Healthy) |
| evaluators | hooks, golden-check patterns | Evaluator TPR/TNR + Rogan-Gladen corrected rate |
| comprehension | `rules/common/comprehension-debt.md`, review coverage | design_revision_rate, repeated_investigation_count |

## 実行条件

- **最小セッション数**: 1（v1 では 3）
- **実行頻度**: 毎日（cron）またはオンデマンド（`/improve`）
- **並行実験**: 改善余地のある全カテゴリで同時実行

## 制約

### 安全ルール

1. **1回の改善サイクルで変更は最大3ファイル** — 大きな変更は分割する
2. **必ずブランチで作業** — `autoevolve/YYYY-MM-DD-{topic}` ブランチを作成
3. **master への直接変更禁止** — 必ずユーザーレビューを経由
4. **既存テストを壊さない** — 変更後に `uv run pytest tests/` を実行して確認
5. **ロールバック可能な変更のみ** — 不可逆な変更は提案のみ
6. **スキル改善は実行データ5回以上** — データ不足での改善は行わない
7. **retire は段階的** — まず `[DEPRECATED]` 付与、次回 audit で改善なければ削除提案
8. **修正後の A/B delta が +2pp 未満なら merge しない** — SkillsBench 研究 (7,308 runs) でノイズマージンが ±2pp と判明。それ以下の改善は統計的に有意でない
9. **スキル修正後は必ずベースラインテスト** — 修正前にスキルなし性能を測定し、修正後も同テストを実行。delta を定量化してから merge 判断
10. **LLM 自動生成の修正は人間レビュー必須** — SkillsBench で LLM 自己生成スキルは平均 -1.3pp。`skills/*/SKILL.md` および `agents/*.md` の変更は自動マージ条件から除外。`gate_proposal()` が `auto_accept` を返しても、これらのファイル変更は `pending_review` に格下げ
11. **Brevity Bias 対策** — エージェント定義のドメイン知識セクション（Symptom-Cause-Fix テーブル、コードパターン、failure modes）は簡潔化の対象外。ACE 研究 [Zhang+ 2026] で反復最適化がプロンプトを汎用的に崩壊させる傾向が確認されている。行動指示（tools, permissions, format）のみ簡潔化対象
12. **Knowledge Embedding 比率維持** — エージェント定義の内容比率は「ドメイン知識 ≥ 50%、行動指示 ≤ 50%」を目安とする。`/improve` サイクルでこの比率を下回る変更は discard
13. **フィードバック履歴 H の注入制限** — Proposer への H 注入は直近 20 件 + 対象スキルフィルタに制限。60 日以上前のエントリはサマリー化。`build_proposer_context()` のデフォルト引数に従う
14. **Proposer Anti-Patterns 遵守** — `autoevolve-core.md` の AP-1〜4 に従う。violation する提案は却下
15. **--evolve コスト上限** — デフォルト iterations=3、最大=5。1 イテレーション=1 スキル。2 イテレーション連続 auto_reject で早期終了。コスト上限: 30 LLM 呼び出し/実行
16. **--evolve は worktree 隔離必須** — イテレーティブループの Builder フェーズは worktree 上で実行。master ブランチへの直接変更禁止
17. **ドリフトガード: 連続 reject 上限** — `--evolve` ループで 3 イテレーション連続 `revert` が発生した場合、ループを即時停止しユーザーにエスカレーションする。autoresearch 記事: "12時間放置でエージェントが別の問題を解き始めた"。連続 reject = 目的から逸脱のシグナル
18. **ドリフトガード: 目的メトリクス後退検出** — `--evolve` ループの各イテレーションで、ベースラインスコアからの累積改善を追跡する。3 イテレーション経過後にベースラインを下回っている場合はループを停止し「戦略を再検討」を推奨する
19. **単一変更規律** — `--evolve` ループの各イテレーションでは SKILL.md への変更を **1箇所のみ** に制限する。仮説を明記し、changelog に記録する。revert された仮説は同一表現で再試行しない。autoresearch 記事: "proposal quality dominates total cost" — 少数の精度の高い変更が多数の探索的変更に勝る
20. **Proxy Metric 乖離検出（Goodhart 警告）** — skill 改善時にスコアが +5pp 以上上昇した場合、自動で「Why did score increase?」の説明を要求する。以下を追加チェック: (1) テスト難易度が下がっていないか（テスト行数の減少）、(2) assertion 数が減っていないか、(3) スコープが狭まっていないか（対象ファイル数の減少）。Goodhart's Law: 指標が目標になると指標としての機能を失う。検出は `scripts/policy/gaming-detector.py` が実行
21. **Self-referential Improvement 禁止** — AutoEvolve が自身の評価基準（`improve-policy.md`, `skill-benchmarks.jsonl`, `benchmark-dimensions.md`）を直接変更することを禁止する。評価基準の変更は必ず人間の承認を必要とする。Bengio 論文: エージェントが自身の報酬関数を変更できる場合、reward tampering が最適戦略になり得る
22. **Metric Diversity 要件** — skill 改善の評価は単一メトリクスではなく最低2つの独立指標で判定する。例: 実行時間 + ユーザー満足度、テスト通過率 + コードレビュースコア。単一メトリクスへの過度な最適化は specification gaming の温床になる
23. **Self-Edit Justification (3-Question Gate)** — 改善提案時に以下の3質問に必ず回答する: (1) What problem does this solve?（具体的に。"might be better" は不可）、(2) How do we measure if it worked?（定量指標に紐づける）、(3) What if it breaks?（ロールバック計画、regression の blast radius）。いずれかが曖昧・欠落なら提案を draft に留める
24. **Knowledge Pyramid Tier 要件** — 学習データには `tier`（Raw/Exploratory/Benchmark/Doctrine）と `score`（0.0-1.0）を付与する。L3 (Rules) への昇格には Tier 2 (Benchmark) 以上、L4 (Golden Principles) には Tier 3 (Doctrine) を必須とする。詳細は `references/knowledge-pyramid.md` を参照
25. **Contradiction Mapping** — Garden フェーズで同一トピックに対する方向性の逆転（矛盾）を検出する。検出時は `boundary_condition` フィールドを付与して適用条件を明示するか、低品質側を降格する。自動解決は行わずユーザーに判断を委ねる。詳細は `references/contradiction-mapping.md` を参照
26. **Governance Levels** — カテゴリごとに自律性レベル（0:Observe / 1:Review / 2:Auto-Merge / 3:Trusted）を設定する。デフォルトは Level 1（現在の動作維持）。Level 2 以上への昇格は承認率・CQS に基づく。Level 3 は opt-in 必須。詳細は `references/governance-levels.md` を参照
27. **Stepwise Change Budget** — 1サイクル内の変更は段階的に保守的にする。1st change: epsilon=0.2（通常の変更幅）、2nd change: epsilon=0.15（やや保守的）、3rd change: epsilon=0.1（最も保守的）。根拠: HACRL Stepwise Clipping — 後半ほど保守的にしてドリフトを防止。`scripts/lib/rl_advantage.py` の `stepwise_clip_ratio()` で計算
28. **Acceleration Guard** — 直近3サイクルの accept_rate が前3サイクル比で +30pp 以上上昇した場合、警告を発行し人間レビューを要求する。Hyperagents 論文 (arXiv:2603.19461) の「加速的改善カーブ」は真の改善を示す場合もあるが、評価基準の緩み（Rule 20 Goodhart 警告に類似）やテスト難易度低下の可能性もある。`compute_cqs()` の verdict 分布と合わせて判断する

### 品質基準

- 変更はシンプルで、意図が明確であること
- 変更理由が learnings データに裏付けられていること（「なんとなく」は NG）
- 既存の設計パターンに従うこと（新しいパターンを導入しない）

## 評価指標（定量）

各カテゴリに定量メトリクスと判定閾値を定義する。
autoresearch の「val_bpb が下がった → keep」に倣い、二値判定を基本とする。

| カテゴリ | メトリクス | keep 条件 | discard 条件 |
|---------|----------|----------|-------------|
| errors | 同一エラーの再発回数（直近 5 セッション） | 20%以上減少 | 増加 or 変化なし |
| quality | 同一ルール違反の頻度（直近 5 セッション） | 20%以上減少 | 増加 or 変化なし |
| agents | タスク完了までの平均ターン数 | 15%以上減少 | 増加 |
| skills | skill-executions 平均スコア + A/B delta | 20%以上のスコア向上 AND A/B delta > +2pp | スコア低下 or A/B delta < -2pp |
| evaluators | Evaluator TPR/TNR（review-feedback）+ Rogan-Gladen 補正 | TPR/TNR 両方 5%以上向上 | いずれか低下 |
| comprehension | design_revision_rate（レビュー指摘で設計変更が必要になった割合） | 20%以上減少 | 増加 or 変化なし |
| comprehension | repeated_investigation_count（同一コード領域の複数セッション調査） | 減少 | 増加 |
| comprehension | spec_slop_detection_rate（Spec Slop 検出頻度） | 減少 | 増加 |

- `experiment_tracker.py measure <exp-id>` で自動計測する
- 判定は `measure_effect()` の ±20% 閾値に準拠
- データ不足（before_count=0）の場合は `insufficient_data` とし、次サイクルまで待機

## 複雑さ予算（Simplicity Criterion）

autoresearch の原則: 「0.001 の改善 + 20 行の追加 → 不採用」「コードを消して同等 → 必ず keep」

- 改善効果が小さい（<10% 改善）のに複雑さが増す変更 → discard
- コード・設定を削除して同等以上の効果 → 必ず keep
- 設定行数は「全体で増やさない」を原則とする
- 1 つの改善に 20 行以上の追加が必要なら、設計を再考する
- 既存のパターンを流用できる場合、新しいパターンを導入しない

## 自動マージ条件（低リスクカテゴリのみ）

以下の **全て** を満たす場合、autoevolve ブランチを自動マージ可能:

1. 変更対象が `references/error-fix-guides.md` のみ（追記のみ、`skills/*/SKILL.md` は対象外）
2. テストが全て pass
3. 定量メトリクスが keep 条件を満たす
4. 変更行数が 10 行以下
5. 既存パターンのフォーマットに従っている

上記以外は引き続き人間レビュー必須。

## 実験履歴の可視化

`experiment_tracker.py export-tsv` で全実験の俯瞰ビューを出力する。
autoresearch の results.tsv に倣い、1 行 1 実験のフラットな TSV 形式。

## インフラメトリクス

Knowledge-to-Code Ratio やメンテナンスコストなど、インフラ全体の健全性を追跡する指標。
Codified Context 論文のベンチマーク（24.2%、~1-2時間/週）を参考値として使用。

| メトリクス | 計測方法 | 参考値 |
|----------|---------|--------|
| Knowledge-to-Code Ratio | `(agents + references + rules 行数) / プロジェクトコード行数` | 24.2% |
| Agent ドメイン知識比率 | `ドメイン知識行数 / エージェント総行数` | ≥ 50% |
| Spec Staleness | `/check-health` の陳腐化警告数 | 0 |
| Maintenance Cost | セッション中の spec 更新時間 | ~5分/セッション |

これらは `/improve` サイクルのダッシュボードに含め、傾向を追跡する。
Agent の挙動が不安定なときは spec の欠落・陳腐化のシグナルとして扱う。

## 累積品質スコア (CQS)

改善サイクル全体の効果を定量追跡する複合スコア。
`experiment_tracker.py compute-cqs` または `status` で確認可能。

| verdict | スコア |
|---------|--------|
| keep | +10 * abs(change_pct) / 100 |
| discard | -15 |
| neutral | -2 |

- merged 実験 5 件未満では `insufficient_data`（信頼性不足）
- CQS が負の場合、改善戦略の見直しを推奨
- `/improve` のダッシュボードに CQS を含める
- ベンチマーク次元の詳細は `references/benchmark-dimensions.md` を参照

## ロールバック改善ゲート

merged 実験が後続の品質悪化を引き起こした場合に検出する仕組み。
`experiment_tracker.py check-regression <exp-id>` で実行。

| 条件 | アクション |
|------|-----------|
| merged 後 learnings イベント数 +20% (measure_effect verdict=discard) | ロールバック提案を出力 |
| 同カテゴリ discard 2件以上 | ロールバック提案を出力 |

- 提案は `[ROLLBACK SUGGESTED] exp-id: reason` 形式で出力
- 自動実行はしない。`/improve` ダッシュボードに表示し、ユーザーが判断
- merged 後 3 セッション未満は安定化待ちとして判定をスキップ
- Phase 3 Garden の Quality Gate が全 merged 実験に対して実行

## 知識蒸留パイプライン

学習データを段階的に抽象化・昇格する5レベルのパイプライン。

| Level | 名前 | 保存先 | 例 |
|-------|------|--------|-----|
| L0 | Raw events | `learnings/*.jsonl` | エラーイベント、品質違反 |
| L0.5 | Review findings | `learnings/review-findings.jsonl` | レビュー発見事項（R-11 入力） |
| L1 | Recovery tips | `learnings/recovery-tips.jsonl` | error→recovery ペア |
| L2 | Error fix guides | `references/error-fix-guides.md` | パターン化された修正手順 |
| L3 | Rules | `rules/common/*.md` | 自動検証ルール |
| L4 | Golden principles | `references/golden-principles.md` | プロジェクト横断の原則 |

### 追加入力ソース（Phase 3 TVA）

| スクリプト | 入力 | 出力 | 実行タイミング |
|-----------|------|------|--------------|
| `findings-to-autoevolve.py` (R-11) | `review-findings.jsonl` | `recovery-tips.jsonl` への L1 昇格 | `/improve` 実行時 |
| `qa-tuning-analyzer.py` (R-12) | `review-findings.jsonl` + telemetry | reviewer 改善提案 advisory | `/improve` 実行時 |
| `staleness-detector.py` (R-13) | `logs/hook-telemetry.jsonl` | 陳腐化レポート advisory | `/improve` 実行時 |

### 昇格条件

| 遷移 | 条件 |
|------|------|
| L0 → L1 | 同一 error_pattern が 2 回以上 + recovery_action が有効 |
| L1 → L2 | 同一パターンが 3 回以上 + recovery 成功率 > 50% |
| L2 → L3 | 5 回以上の再発 + 自動検出可能なパターン |
| L3 → L4 | 複数プロジェクトで有効 + 例外なく適用可能 |

- 逆方向の降格も許容: ルール違反が増加した場合は L3 → L2 に差し戻す
- 各レベルの件数は Garden フェーズでモニタリングする

## Tournament Mode

CQS が停滞（0.0-2.0）し通常の improve が neutral を返す場合、
複数戦略を並列比較する tournament mode を使用できる。
手順は `skills/improve/instructions/tournament-mode.md` を参照。

| ルール | 内容 |
|--------|------|
| 最大バリアント数 | 3 |
| バリアントあたり最大ターン | 10 |
| 1サイクルあたり最大回数 | 1 |
| 勝者判定 | review-dimensions.md の加重平均スコア最高 |
| タイブレーク | 差 < 0.5 なら Conservative 優先（KISS） |
| テスト失敗 | 自動除外 |

## RL-Inspired 評価指標

Policy Gradient の手法を離散最適化に適応した指標群。
`scripts/lib/rl_advantage.py` に実装。

### RLOO / GRPO Advantage

K variant（K>=3）のスキル設定を並行評価し、
各 variant の相対的な優劣を定量化する。

- **RLOO**: Leave-One-Out baseline。
  自身を除く平均との差分。ノイズに強い
- **GRPO**: グループ z-score 正規化。
  variant 間の相対位置を標準化

`aggregate_benchmark.py --variants v1.json v2.json v3.json`
で RLOO/GRPO advantage を含むレポートを生成。

### Importance Sampling (IS)

設定バージョンが変わった過去データの重みを割り引く。
`config_version`（SHA-256 先頭12文字）で追跡し、
`importance_weight()` で指数減衰の重みを計算。

- 同一 config_version → weight=1.0（完全に有効）
- 異なる version → `exp(-decay_rate * change_count)`

### Clipping

PPO スタイルの変更比率クリッピング。
`clip_ratio(after, before, epsilon=0.2)` で
スコア変動を ±20% に制限。

`skill_amender.gate_proposal()` で自動適用。
クリップ発動時は reason に `[CLIP WARNING]` を追記。

### Stepwise Clipping

HACRL の Stepwise Clipping に着想。1サイクル内で複数変更を重ねる場合、
更新回数に応じて許容変更幅を段階的に狭める。

`stepwise_clip_ratio(after, before, step)` で計算。
step=0 は通常の clipping、step が進むごとに epsilon が step_decay 分だけ減少（下限 0.05）。

`skill_amender.gate_proposal()` で step 番号を渡して自動適用。

### Per-step Credit Assignment

セッション outcome をスキル呼び出し回数に比例配分。
`step_credit()` で計算、`skill-credit.jsonl` に記録。

outcome スコア: clean_success=1.0, recovery=0.6, failure=0.2

## 仮定ストレステスト（Assumption Stress-test）

> 出典: Anthropic "Harness Design for Long-Running Apps" (2026-03)
> "every component in a harness encodes an assumption about what the model can't do on its own, and those assumptions are worth stress testing."

ハーネスの各コンポーネントは「モデルが単独ではできないこと」を仮定している。
モデル改善に伴い、その仮定が陳腐化する可能性がある。

### 実行タイミング

- `/improve` の Garden フェーズで**四半期に1回**実施
- 新しいモデルリリース後（Opus/Sonnet のメジャーアップデート時）

### 方法論

1. **コンポーネント一覧の作成**: `agent-harness-contract.md` の Hook 閾値サマリから対象を列挙
2. **仮定の明文化**: 各コンポーネントが前提とする「モデルの能力限界」を1文で記述
3. **除去テスト**: 1コンポーネントを無効化し、同一タスクを実行。品質・速度・コストの変化を計測
4. **判定**:
   - 品質低下なし → コンポーネントは **scaffolding**（除去候補）
   - 品質低下あり → コンポーネントは **load-bearing**（維持）
   - 品質向上 → コンポーネントが**悪影響**（即時除去）
5. **記録**: 結果を `insights/assumption-stress-test.md` に記録

### 制約

- 1回のテストで除去するのは **1コンポーネントのみ**（交互作用を排除）
- テスト環境は worktree で隔離
- 除去候補でも即削除せず、`[DEPRECATED]` 付与 → 次回テストで再確認 → 削除提案

## 現在のフォーカス

全カテゴリを高頻度で改善する（2026-03-10 設定）
