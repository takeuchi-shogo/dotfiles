---
status: active
last_reviewed: 2026-04-23
---

# Autoresearch パターン統合 実装プラン

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** autoresearch 記事の3つの改善点（Yes/No チェックリスト、単一変更規律、ライブダッシュボード）を既存の AutoEvolve / skill-creator インフラに統合する

**Architecture:** 既存の eval パイプライン（run_eval.sh → compare.sh → aggregate.py）にチェックリスト評価を追加。`/improve --evolve` に単一変更モードを追加。ダッシュボードは自己完結型 HTML を生成する Python スクリプトで実装。

**Tech Stack:** Python 3, Bash, HTML/CSS/JS (inline), Chart.js (CDN)

---

## Task 1: evals.json に checklist フィールド追加

既存の assertions（自由記述型）に加え、yes/no チェックリスト（二値判定型）をサポートする。

**Files:**
- Modify: `.config/claude/skills/skill-creator/scripts/compare.sh`
- Modify: `.config/claude/skills/skill-creator/scripts/aggregate.py`
- Modify: `.config/claude/skills/skill-creator/SKILL.md` (ドキュメントのみ)

### 設計

**evals.json スキーマ拡張:**

```json
{
  "evals": [
    {
      "id": 1,
      "prompt": "ランディングページのコピーを書いて",
      "assertions": ["既存のアサーション"],
      "checklist": [
        "見出しに具体的な数値や成果が含まれているか？",
        "バズワード（革新的、シナジー等）を使っていないか？",
        "CTAに具体的な動詞フレーズを使っているか？"
      ]
    }
  ]
}
```

**grading.json 拡張（後方互換）:**

```json
{
  "with_skill": {
    "assertion_results": [...],
    "checklist_results": [
      {"question": "見出しに具体的な数値...", "passed": true, "evidence": "..."}
    ],
    "checklist_pass_rate": 0.67,
    "quality_score": 8
  }
}
```

**benchmark.json 拡張:**

```json
{
  "configurations": [
    {
      "name": "with_skill",
      "checklist_pass_rate": 0.83,
      "checklist_pass_rate_stddev": 0.12,
      ...
    }
  ]
}
```

### Steps

- [ ] **Step 1: compare.sh にチェックリスト評価を追加**

  `eval_metadata.json` から `checklist` 配列を読み込み、grader プロンプトにチェックリストセクションを追加。checklist が空/未定義の場合は既存動作をそのまま維持。

  変更箇所: `ASSERTIONS` 読み込みの後に `CHECKLIST` を読み込み、grader プロンプトと JSON 出力スキーマに `checklist_results` を追加。

- [ ] **Step 2: compare.sh の変更をテスト**

  テスト用の eval_metadata.json を作成し、checklist あり/なし両方で compare.sh が正常動作することを確認。

- [ ] **Step 3: aggregate.py にチェックリスト集計を追加**

  `collect_eval_data()` で `checklist_results` と `checklist_pass_rate` を収集。
  `aggregate_configuration()` で `checklist_pass_rate` の mean/stddev を計算。
  `generate_markdown()` でチェックリスト列を Summary テーブルに追加。

- [ ] **Step 4: aggregate.py の変更をテスト**

  checklist あり/なしの grading.json を用意し、集計結果が正しいことを確認。

- [ ] **Step 5: SKILL.md のドキュメント更新**

  evals.json スキーマ説明に `checklist` フィールドを追加。「Step 2: assertions を書く」のセクションにチェックリストの使い分けガイドを追記:
  - 客観的に判定可能 → checklist（決定論的、再現性高い）
  - 主観的/複合的 → assertions（LLM判定、柔軟性高い）

- [ ] **Step 6: コミット**

---

## Task 2: `/improve --evolve` に単一変更モード追加

`--single-change` フラグ（スキル最適化時のデフォルト）で、1イテレーション1変更を強制。Changelog をアーティファクトとして出力。

**Files:**
- Modify: `.config/claude/skills/improve/SKILL.md`
- Modify: `.config/claude/references/improve-policy.md`

### 設計

**動作:**

1. 各イテレーションで autoevolve-core に「1つの変更のみ提案」を指示
2. 変更を仮説として記述（例: "見出しに数値を強制するルールを追加"）
3. A/B テスト → keep/revert
4. `changelog.md` に全試行を記録

**Changelog フォーマット:**

```markdown
# Skill Evolution Changelog: {skill-name}

## Round 1 (2026-03-18)
- **Hypothesis**: 見出しに具体的な数値を含むルールを追加
- **Change**: SKILL.md L42 に "Your headline must include..." を追加
- **Result**: KEEP (checklist_pass_rate: 56% → 72%, delta: +16pp)

## Round 2 (2026-03-18)
- **Hypothesis**: バズワード禁止リストを追加
- **Change**: SKILL.md L50 に "NEVER use: revolutionary..." を追加
- **Result**: KEEP (checklist_pass_rate: 72% → 85%, delta: +13pp)

## Round 3 (2026-03-18)
- **Hypothesis**: ワードカウント制限を 100 語に引き下げ
- **Change**: SKILL.md L35 の word limit を 150→100 に変更
- **Result**: REVERT (checklist_pass_rate: 85% → 78%, delta: -7pp)
```

**早期終了条件（既存に追加）:**
- checklist_pass_rate >= 95% が 3 連続 → 目標達成で終了

### Steps

- [ ] **Step 7: improve/SKILL.md にフラグと単一変更ループを追記**

  `--single-change` オプションを追加。`--evolve` と組み合わせて使う。
  ループフローの Proposer ステップに「1つの変更のみ。仮説を明記」の制約を追加。
  Changelog 生成ステップを各イテレーション末尾に追加。
  目標スコア達成による早期終了条件を追加。

- [ ] **Step 8: improve-policy.md に単一変更ルールを追記**

  Rule 17 として追加:
  - `--single-change` モードでは 1 イテレーション = SKILL.md への 1 変更のみ
  - 変更は仮説として記述し、changelog に記録
  - revert された変更は同じ仮説で再試行しない

- [ ] **Step 9: コミット**

---

## Task 3: ライブダッシュボード

`--evolve` ループ中にブラウザでスコア推移をリアルタイム表示する自己完結型 HTML ダッシュボード。

**Files:**
- Create: `.config/claude/skills/skill-creator/scripts/generate_dashboard.py`
- Modify: `.config/claude/skills/improve/SKILL.md` (ダッシュボード起動手順)

### 設計

**データフロー:**

```
--evolve loop → dashboard-state.json 更新 → generate_dashboard.py → dashboard.html 再生成
                                                                      ↑ ブラウザが10秒で自動リロード
```

**dashboard-state.json:**

```json
{
  "skill_name": "landing-page-copy",
  "started_at": "2026-03-18T10:00:00Z",
  "target_score": 0.95,
  "baseline_score": 0.56,
  "rounds": [
    {
      "round": 1,
      "hypothesis": "見出しに数値を強制",
      "checklist_pass_rate": 0.72,
      "quality_score": 7.5,
      "delta": "+16pp",
      "verdict": "keep",
      "checklist_breakdown": [
        {"question": "数値を含むか？", "passed": true},
        {"question": "バズワードなし？", "passed": false}
      ]
    }
  ],
  "status": "running"
}
```

**HTML ダッシュボード機能:**
- スコア推移チャート（Chart.js CDN、折れ線グラフ）
- チェックリスト項目ごとの pass/fail 推移
- 各ラウンドの仮説と結果（keep/revert）の表
- ステータスバー（running / completed / stopped）
- `<meta http-equiv="refresh" content="10">` で自動リロード

### Steps

- [ ] **Step 10: generate_dashboard.py を作成**

  入力: `dashboard-state.json` のパス
  出力: 同ディレクトリに `dashboard.html` を生成

  自己完結型 HTML（Chart.js は CDN から読み込み）。
  dashboard-state.json が存在しない場合は "Waiting for data..." を表示。

- [ ] **Step 11: generate_dashboard.py のテスト**

  サンプル dashboard-state.json を作成し、HTML が正常に生成されることを確認。
  ブラウザで開いてチャートが表示されることを目視確認。

- [ ] **Step 12: improve/SKILL.md にダッシュボード統合手順を追記**

  `--evolve` ループ開始時に:
  1. ワークスペースに `dashboard-state.json` を初期化
  2. `generate_dashboard.py` で HTML 生成 → `open` でブラウザ起動
  3. 各イテレーション末尾で state 更新 → HTML 再生成
  4. ループ完了時に status を "completed" に更新

- [ ] **Step 13: コミット**

---

## Task 4: メモリ更新

- [ ] **Step 14: MEMORY.md に autoresearch 統合の知見を記録**

  既存の AutoEvolve セクションに追記:
  - checklist-based scoring の設計判断
  - single-change discipline の根拠
  - dashboard の実装方針

---

## 検証

1. **checklist 後方互換**: checklist なしの既存 evals.json で compare.sh / aggregate.py が正常動作
2. **checklist 付き評価**: checklist 付き eval_metadata.json で grading.json に checklist_results が出力
3. **aggregate 集計**: checklist_pass_rate が benchmark.json/md に含まれる
4. **dashboard 生成**: サンプル JSON → HTML 生成 → ブラウザ表示
5. **SKILL.md 構文**: 変更後の SKILL.md に YAML/Markdown の構文エラーがない
