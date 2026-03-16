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
| evaluators | hooks, golden-check patterns | Evaluator accept_rate (TPR) |

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
| evaluators | Evaluator accept_rate（review-feedback） | 10%以上向上 | 低下 |

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

## 現在のフォーカス

全カテゴリを高頻度で改善する（2026-03-10 設定）
