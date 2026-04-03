# Phase 4: Adversarial Gate (Codex 必須)

> 全提案を Codex (gpt-5.4) で敵対的にレビューし、品質を保証する。
> このフェーズをスキップすることは禁止。Codex の実行に失敗した場合はユーザーに報告して中断する。

## 目的

「他の AI に突っ込まれない」レベルの提案品質を保証する。
提案者（Sonnet）とは別のモデル（Codex）が攻撃者として振る舞うことで、
単一視点の盲点を構造的に排除する。

## Codex 実行

`codex exec` を使用して以下のプロンプトを実行する:

```bash
codex exec -m xhigh "
あなたは改善提案の敵対的レビュアーです。
以下の提案それぞれについて、6つの観点から徹底的に攻撃してください。

## レビュー観点

### 1. 原則違反チェック
以下の core principles に反していないか検証:
- KISS: 不必要に複雑ではないか
- YAGNI: 今本当に必要か、将来のための過剰設計ではないか
- DRY: 既存の仕組みと重複していないか
- Build to Delete: 削除コストが高くなる変更ではないか
- Scaffolding > Model: モデル変更で不要になる変更ではないか
- 最小インパクト: 必要以上に広い変更をしていないか

### 2. 考慮漏れ (Blast Radius)
- 提案者が挙げた blast_radius 以外に影響を受けるファイル/システムはないか
- 暗黙の契約（他のスキルやエージェントが依存している前提）を壊さないか
- 間接依存（A→B→C の C への影響）は検討されているか

### 3. 証拠の妥当性
- evidence_chain の data_points は因果関係を示しているか、相関にすぎないか
- サンプルサイズは結論を支持するのに十分か
- 反証（counter_evidence）は誠実に検討されているか、形式的か

### 4. Pre-mortem の深度
- 提案者が挙げた失敗シナリオ以外に、より深刻な失敗モードはないか
- ロールバック計画は実際に機能するか
- 部分的な失敗（変更の一部だけ適用された場合）のリスクは？

### 5. 代替案の検討
- この提案よりシンプルなアプローチはないか
- コードを削除する方向で解決できないか
- 既存の仕組み（hook, rule, agent）で対処できないか

### 6. 汎化テスト (Generalization)
- この提案のきっかけとなった具体的なタスク/エラーが消えた場合でも、この改善には価値があるか
- 特定のメトリクスをゲームするための変更ではないか（rubric hacking）
- 他のドメイン/タスクにも転移可能な改善か、それとも特定ケースへの過適合か

## 判定基準

各提案に以下の判定を付与:

- **ROBUST**: 5観点全てで重大な問題なし。推奨可能
- **VULNERABLE**: 1-2 観点で注意が必要。具体的な弱点と改善方向を明記
- **FATAL_FLAW**: 致命的な問題あり。具体的な理由と、なぜ致命的かを説明

## 入力データ

### 提案一覧
{proposals_json}

### 適用されるべき原則 (CLAUDE.md core_principles)
{core_principles}

### Coverage Matrix 結果
{coverage_matrix_summary}

## 出力フォーマット (JSON)

{
  \"reviews\": [
    {
      \"proposal_id\": \"IMP-xxx\",
      \"rating\": \"ROBUST|VULNERABLE|FATAL_FLAW\",
      \"principle_violations\": [\"具体的な違反内容\"],
      \"missed_blast_radius\": [\"見落とされた影響範囲\"],
      \"evidence_weaknesses\": [\"証拠の弱点\"],
      \"deeper_failure_modes\": [\"より深刻な失敗シナリオ\"],
      \"simpler_alternatives\": [\"よりシンプルな代替案\"],
      \"summary\": \"1-2文の総合評価\"
    }
  ],
  \"overall_blind_spots\": [\"全提案に共通する見落とし\"],
  \"missing_proposals\": [\"提案されるべきだったが欠落している改善\"]
}
"
```

## Propose-Adversarial ループ

### フロー

```
Phase 3: PROPOSE
    ↓
Phase 4: ADVERSARIAL GATE (Codex)
    ↓
    ├── 全提案 ROBUST → Phase 5 へ
    ├── VULNERABLE あり AND iteration < 2:
    │     → REFINE ステップ（下記）→ Phase 4 再実行
    ├── VULNERABLE あり AND iteration >= 2:
    │     → 注意付きで Phase 5 へ
    └── 全提案 FATAL_FLAW:
          → Phase 5 へ（全却下レポート）
```

### REFINE ステップ

VULNERABLE 判定の提案に対して:

1. Codex の指摘内容を autoevolve-core に渡す
2. 各指摘に対する具体的な対応を含めた修正版を生成:
   - 原則違反 → 原則に沿った形に修正 or 正当化の追加
   - blast radius 見落とし → indirect 影響を追記
   - 証拠の弱さ → 追加データ収集 or confidence 引き下げ
   - pre-mortem 不足 → 追加の失敗シナリオ + 対策
   - 代替案指摘 → 代替案との比較表を追加、選択理由を明記
3. FATAL_FLAW 提案は修正せず却下として確定

### ループ制約

- **最大イテレーション**: 2（初回 + 精錬 1 回）
- **FATAL_FLAW は再提案しない**: 根本的に方向性が間違っている提案を修正しても無駄
- **精錬で新規提案は追加しない**: 既存提案の改善のみ
- **Codex の `missing_proposals` は Phase 5 の「次回への申し送り」に記載**: 今回のサイクルでは追加しない（スコープ制御）

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| Codex CLI が未インストール | ユーザーに報告して中断。「Codex CLI が必要です」 |
| Codex 実行がタイムアウト | 1 回リトライ。2 回目もタイムアウトならユーザーに報告 |
| Codex 出力が JSON パース不能 | Codex に再実行依頼（プロンプトに「JSON で出力せよ」を強調） |
| Codex が全提案 ROBUST と判定 | 正常終了。ただしレポートに「Codex review passed」と明記 |

## Phase 5 への出力

以下を Phase 5 (REPORT) に渡す:

```yaml
adversarial_results:
  iteration_count: 1-2
  proposals:
    - id: "IMP-xxx"
      final_rating: "ROBUST|VULNERABLE|FATAL_FLAW"
      codex_review: {上記 JSON の該当エントリ}
      refinement_history: [{iteration_1_feedback, iteration_2_response}]  # ループした場合
  overall_blind_spots: [...]
  missing_proposals: [...]
```
