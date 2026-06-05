# RSI Governance Frontier Plan (A+B+C)

- **Date**: 2026-06-05
- **Source**: `docs/research/2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md`
- **Scale**: L (A=S, B=M, C=M / 計 6+ ファイル)
- **Thesis**: harness は「実行の自己改善」に重投資済。Anthropic 再帰的自己改善記事が照らす未踏領域 =「判断の計測」と「メタ安全層の保護」「検証の自己改善」。この非対称を埋める。

## 撤退条件 (reversible-decisions)

- A: decision-duel ログが 30 日で 5 件未満 → 計測機会が薄く費用対効果なし、hook 撤去
- B: 保護ティアが正当な AutoEvolve 改善を 3 回以上ブロック → ティア定義が過剰、対象を絞る
- C: 捕捉率計測が 30 日で signal を出さない (review がそもそも発火していない) → 計測対象を再定義

## Pre-mortem (失敗モード)

- A が「両論併記の記録」を儀式化し誰もスコアしない → 月次スコアを `/timekeeper` Q に組み込み強制
- B の保護ティアを AutoEvolve がメタ改変で回避 (保護リスト自体を編集) → 保護リストを hook 内ハードコード + git protected path で二重化
- C が捕捉率を gaming (簡単な問題だけ review に回す) → `gaming-detector.py` の既存パターンに接続

---

## Task A: 判断 frontier 計測ループ (S)

記事の Mythos 51%→64% の個人版。AI の方針判断が人間に追いついているかを時系列で観測可能にする。

- **A1**: `scripts/lib/` or `scripts/policy/` に `decision-duel-logger.py` — AutoEvolve/tech-researcher が方針提案し、ユーザーが別案を選んだ局面を `~/.claude/agent-memory/decision-duels.jsonl` に両論併記で append (proposer案 / human案 / context / timestamp / outcome=pending)
  - **Files**: `scripts/policy/decision-duel-logger.py` (新規), `.config/claude/settings.json` (hook 登録、`protect-linter-config.py` の登録パターンに倣う)
- **A2**: 月次スコアリング — `timekeeper` skill の review サブモードに「pending な decision-duel を `outcome=human_right/ai_right/tie` で裁定する」Q を追加
  - **Files**: `.config/claude/skills/timekeeper/SKILL.md` (Q 追加)
- **A3**: 集計 — `/decision` skill か簡易 script で「直近 N 件の ai_right 率」を出す (Mythos 64% に相当する自分の数値)
  - **Files**: `.config/claude/skills/decision/` に集計ロジック追記 or `scripts/lib/decision-duel-stats.py`
- **Verify**: ダミー duel を 3 件記録 → 裁定 → ai_right 率が出ることを確認

## Task B: メタ安全層の自己改変防御 (M)

記事 #6「世代跨ぎで misalignment が複利化、制御喪失まで気づかない」の個人版。

- **B1**: 保護ティア hook — AutoEvolve (`autoevolve-runner.sh` / `autoevolve-core` agent) が安全機構ファイルを Edit/Write 対象にしたら block。対象 = `improve-policy.md` (Rule 17-19 含む), `completion-gate.py`, AutoEvolve guardrails, この保護 hook 自身
  - **Files**: `scripts/policy/protect-meta-safety.py` (新規、`protect-linter-config.py` と同型), `.config/claude/settings.json` (PreToolUse 登録)
  - **二重化**: 保護対象リストを hook 内にハードコード (メタ改変で外部設定を書き換えられないように)
- **B2**: 累積 drift audit — 3ファイル/サイクル制限では見えない緩慢な drift を検出。AutoEvolve 由来コミットを N サイクル分まとめてベースラインと diff し、安全機構の段階的弱体化を検知
  - **Files**: `scripts/lifecycle/autoevolve-drift-audit.sh` (新規、cron か autoevolve-runner.sh 末尾に接続)
- **B3**: グローバル circuit-breaker — `freeze` skill は session Edit ガードで cron を止めない。AutoEvolve cron + session learner を一括停止するフラグ (`~/.claude/agent-memory/AUTOEVOLVE_FROZEN`) を `autoevolve-runner.sh` 冒頭でチェック
  - **Files**: `scripts/autoevolve-runner.sh` (冒頭ガード追加), `scripts/policy/session-learner.py` (同フラグチェック), 新規 `/freeze-evolution` トグル or `freeze` skill 拡張
- **Verify**: 保護ファイルへの Edit を AutoEvolve コンテキストで試行 → block 確認。FROZEN フラグ設置 → cron が no-op 確認

## Task C: 検証側の自己改善 (M)

記事 #7「人間レビューが速度ボトルネック、自動レビューが本番バグの1/3捕捉」。生成と検証の自己改善を対称化。

- **C1**: 捕捉率計測 — Codex Review Gate / code-reviewer が捕えた問題 vs すり抜けて後で発覚した問題を集計。`post-test-analysis.py` (既存) に「review が捕捉 / すり抜け」のラベル付け append を追加
  - **Files**: `scripts/policy/post-test-analysis.py` (集計拡張), `~/.claude/agent-memory/review-catch-rate.jsonl` (新規ログ)
- **C2**: チェックリスト自己改善 — 捕捉率が閾値を下回ったら、すり抜けた問題のパターンを review チェックリスト (`skills/review/references/review-checklists/`) の改善候補として AutoEvolve の Analyze フェーズに渡す
  - **Files**: `.config/claude/agents/autoevolve-core.md` (Analyze 対象に review-catch-rate.jsonl 追加), review skill の checklist
- **C3**: gaming ガード — 「簡単な問題だけ review に回して捕捉率を上げる」評価ゲーミングを `gaming-detector.py` の既存パターンに接続
  - **Files**: `scripts/policy/gaming-detector.py` (パターン追加)
- **Verify**: 既知バグを review に通す → 捕捉/すり抜けが記録される。捕捉率低下で checklist 改善候補が Analyze に上がることを確認

---

## 依存関係 / 実行順

1. **A 先行** (S、独立、即実装可) — 計測機構は他に依存しない
2. **B** (M) — AutoEvolve safety の理解が前提。A の後でも並行でも可
3. **C** (M) — review gate と post-test-analysis 理解が前提。B と独立

A → (B ∥ C) の順を推奨。各タスクは独立 PR 可。

## 検証 (全体)

- `task validate-configs`, `task validate-symlinks` (settings.json / 新規 hook 追加のため)
- 各新規 hook は Codex Review Gate を通す (harness 変更)
