# Plan: SkillOpt 由来 — objective-lane skill optimization

- **Status**: implemented 2026-07-22 (VO / #1 / #2 完了。#3 は gate 内蔵の rejected-edits.jsonl buffer で drift 非依存部分を実装、旧 rejected-patterns.jsonl の Rule 14 再配線は learned-promotion-loop の category drift 修復待ちで pending)
- **Created**: 2026-06-02
- **Source absorb**: `docs/research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md`
- **Scale**: L (新 reference + 新 script + playbook + 既存3ファイル編集 + drift 訂正)
- **Owner decision**: ユーザーが Triage で全4件 (#1 #2 #3 + Validation-only) を選択。Codex 最小推奨は #1 #2。
- **Guiding constraint**: 旧 `/improve` は復活させない (2026-05-03 retire)。判断系 skill (absorb/review/think) の自動最適化は **block**。objective-checkable lane にだけ SkillOpt 的 strict gate を小さく配線する。

## 背景 (なぜこの plan か)

SkillOpt のコア部品 (bounded edit / held-out gate / rejected buffer / momentum) は dotfiles にほぼ全て**設計済みだが配線が切れている**。さらに「どのスキルを自動最適化してよいか」の入口判別が無く、判断タスクを誤って最適化対象にして /improve が false-positive 死した。本 plan は (a) 入口分類器と (b) objective lane 専用の strict gate を最小実装する。

## 撤退条件 (reversible-decisions)

- #2 の holdout strict gate が、手元の objective lane (例: code-review finding 分類) で baseline 比 +1pp 以上の改善を **3 試行中1回も出せない** 場合 → gate 配線を中止し eligibility classifier (#1, doc のみ) だけ残す。
- #1 の lane 分類が運用で2回以上「どちらの lane か判断不能」を生む場合 → 二分をやめ「objective lane allowlist 列挙」方式 (デフォルト judgement) に縮退。

## 失敗モード (pre-mortem)

- **Goodhart**: objective scorer が代理目的になり、holdout でも測れない品質劣化が起きる → metric diversity (Rule 23) を gate にも適用、2+ 独立指標必須。
- **lane 誤分類**: 判断スキルを objective lane に誤って入れる → #1 で allowlist 明示 + 新規 lane 追加は人間承認必須。
- **drift 再発**: 新 script を /improve のような大ループに育てない。pure-logic + playbook 手動起動に留める (Build to Delete)。

## Tasks

### Task #1: Optimizer Eligibility Classifier (S, 前提)
- **Files**:
  - 新規 `.config/claude/references/optimizer-eligibility.md`
  - ポインタ追記: `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md`, `.config/claude/references/knowledge-pyramid.md`
- **内容**: artifact を 2 lane に分類する基準を codify。
  - `objective-checkable lane` (正解キー照合可): routing 判定 / extraction / classification / code-review finding 分類 / validator 選択 / runnable な hook・script
  - `judgement lane` (人間嗜好・文脈適合): absorb / review / think / 各 design・recipe skill
  - ルール: objective lane のみ #2 strict gate 対象。judgement lane は human-in-loop (`/promote-learnings`) のまま。新規 lane 割当は人間承認必須。
- **検証**: 既存スキル 5-6 個を試験分類し、判断不能ケースが出ないか確認。

### Task #2: Objective-lane held-out strict accept gate (M)
- **Files**:
  - 新規 `.config/claude/scripts/eval/holdout_accept_gate.py` (pure logic: jsonl in → accept/reject JSON out)
  - 新規 `docs/playbooks/objective-lane-optimization.md` (手動起動手順)
- **内容**: `candidate edit → train(search)セットで eval → holdout で strict accept (tie reject)`。
  - 入力: split_holdout.py の `*-train.json` / `*-holdout.json`
  - 判定: holdout pass_rate が **厳密向上** (delta > 0, tie reject) のときだけ accept。Rule 23 の metric diversity (2+ 独立指標) を必須化。
  - **/improve に依存しない**。autoevolve-core も呼ばない。playbook から手動起動。
- **テスト**: 固定 fixture で strict-improve / tie-reject / 空入力 / overfitting (search↑ holdout↓) ケース。
- **依存**: #1。

### Task #3: rejected-edit buffer の per-lane idempotent 再配線 (S〜M)
- **Files**: `.config/claude/references/improve-policy.md` Rule 14 周辺 (概念保持) + #2 gate プロンプト
- **内容**: objective lane ごとに直近 rejected edits を idempotent (SHA1 key) 記録 → gate の候補提案に再注入し再提案を抑制。
- **依存**: #1 + **category drift 修復** (learned-promotion-loop と連動。drift 未修復なら本タスクは pending)。

### Task VO: Validation-only 訂正 (S, 独立実行可)
- **Files**:
  - `docs/research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md`: frontmatter `status: integrated → partially-superseded`、注記「T1/T2/T4 は /improve retire (2026-05-03) で孤児化、qualitative_signals.jsonl 未作成。本 SkillOpt absorb の objective-lane gate へ統合し直す」
  - `.config/claude/references/improve-policy.md` Rule 47: 「SkillOpt (arXiv:2605.23904) が strict-improve + tie-reject を実証」の外部裏付け注記。配線先は新 objective-lane gate (#2)。

## 実行順序

1. **VO** (独立、即実行可) → 2. **#1** (前提) → 3. **#2** (#1 後) → 4. **#3** (#1 + drift 修復後、pending 可)

## 完了の定義

- #1: optimizer-eligibility.md が存在し、既存スキルを lane 分類できる。
- #2: holdout_accept_gate.py が fixture テストを pass し、playbook から手動起動で objective lane の候補編集を strict 判定できる。
- #3: objective lane の rejected edits が idempotent 記録・再注入される (drift 修復済みが前提)。
- VO: 2ファイルの frontmatter/注記が更新済み。
