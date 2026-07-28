---
title: "skill 可観測性の補強 (Gotchas 昇格 / undertriggering 計測 / category 跨ぎ診断)"
date: 2026-07-27
status: planned
scale: M
origin: docs/research/2026-07-27-anthropic-skills-lessons-absorb-analysis.md
---

# skill 可観測性の補強

Anthropic「Lessons from building Claude Code: How we use skills」absorb の採用タスク T2 / T3 / T4。
T1 (careful/freeze の description 修正) はブランチ `fix/careful-freeze-description-drift` で実施済。

3 タスクは独立していて依存関係はない。T4 → T2 → T3 の順に安い。

## T4: category 跨ぎ診断 (S)

**やること**: `skill-audit` に「主用途が 1 つに収まらない skill は分割候補」という診断を 1 項目追加する。

記事の主張は「良い skill は 9 カテゴリのどれか 1 つに収まる。複数に跨る skill は agent を混乱させる」。dotfiles には既に 3 つの taxonomy が並立しているので **4 つ目の分類体系は入れない**。使うのは診断部分だけ。

- 対象: `.config/claude/skills/skill-audit/SKILL.md`
- 判定材料は既存の `metadata.category` enum (`skill-writing-principles.md` の 10 種) を使う。SKILL.md 本文の見出し構成から主用途を推定し、category 宣言と食い違う / 複数用途が同格で並ぶ skill をフラグする
- 出力は既存の audit report に 1 セクション追加するだけ。新ファイルは作らない

**撤退条件**: フラグされた skill が 20 件を超えたら診断が粗すぎる。閾値を締めるか、この項目を削除する (`references/harness-stability.md` の 30 日評価に乗せる)。

## T2: Gotchas 昇格の実行 (M)

**やること**: 既に実装済の `/skill-audit gotchas-scan` を走らせ、優先度上位の skill に `## Gotchas` を追加する。新しい mechanism は作らない — **未実行分の消化**。

現状 coverage は 20/105 = 19%。`skill-audit` の Gotchas Coverage Scan は最優先追加対象を自ら定義している:

- Usage Tier が Dominant または Weekly
- Guard 型 (freeze, careful 等、失敗すると影響大)
- Pipeline 型 (review, absorb 等、複数フェーズで落ちる)

手順:

1. `/skill-audit gotchas-scan` を実行し、Gotchas-less skill と Promotion Backlog (`references/lessons-learned.md` からの昇格候補) を出す
2. 上記 3 条件に該当する skill だけを対象にする。**105 件全部に付けようとしない**
3. Gotchas の中身は `references/lessons-learned.md` の実際の失敗記録と memory の feedback_* から取る。想像で書かない (記事: 「実際の failure point から積み上げる」)
4. 1 skill あたり 1-3 項目。書けるネタがない skill はスキップして「ネタなし」と記録する

**撤退条件**: 昇格候補が `lessons-learned.md` に見つからない skill が対象の半分を超えたら、coverage 率そのものを KPI にするのをやめる。19% という数字は「失敗がまだ観測されていない」ことの反映でもありうる。memory `feedback_skill_audit_conflict_metric.md` と同じ罠 (件数を成否の指標にしない)。

## T3: undertriggering 計測 (M)

**やること**: 「呼ばれるべきだったのに呼ばれなかった skill」を検出する。

記事の原文: skill 使用を PreToolUse hook でログし、popular な skill と **undertriggering** な skill を見つける。dotfiles は前者だけ実装済 — `scripts/policy/skill-tracker.py` が発火した Skill を `~/.claude/agent-memory/learnings/skill-executions.jsonl` に記録し、`skill-audit` の Usage Tier が Dominant/Weekly/Monthly/Unused に分類する。

未発火の検出には期待値の定義が要る。安い版から始める:

- **v1 (安い)**: 各 skill の description の `Triggers:` に列挙された語を辞書化し、セッションの user prompt に出現したのに当該 skill が発火しなかったケースを記録する。既に `Triggers:` フィールドは全 skill が持っているので新しいメタデータは不要
- 出力先は既存の `skill-executions.jsonl` と同じディレクトリに `skill-undertriggers.jsonl` を追加。`skill-audit` の Usage Tier セクションに「Unused だが trigger 語 hit N 回」列を足す
- v1 は語彙一致なので false positive が出る前提。目的は「絶対数」ではなく「同じ skill が繰り返し hit しているのに一度も発火しない」パターンの検出

実在する証拠: memory `feedback_sonnet_cursor_underused.md` が「Sonnet subagent / Cursor CLI をルーチンに組み込む (model-routing.md 経路定義済だが未発火)」を**手で**記録している。mechanism がないから手記録になっている。

**撤退条件**: v1 の false positive が実用に耐えない (週次で 50 件超のノイズ) 場合、期待値を語彙一致でなく明示宣言 (skill 側に `expected_contexts`) に変える案があるが、それは全 skill への metadata 追加になるので **その時点で T3 を retire する**。undertriggering の手記録 (memory) で足りているなら mechanism 化しない方が安い。

## 検証

- T4 / T2: `task validate-configs`
- T3: `scripts/policy/skill-tracker.py` に変更が入るので hook として実際に発火させて確認する (`references/harness-stability.md` / `hook-debugger` skill)。単体実行の成功を発火の証拠にしない
- 全体: `task validate-symlinks`

## 記事から Reject したもの (再検討しないための記録)

- **9-category taxonomy の導入** — 既に 4分類 / 3分類 / 10-enum が並立。4 つ目は instruction DRY 違反
- **Verification skill への engineer-week 投資** — 数百 skill 組織の前提。dotfiles 固有の acceptance contract が繰り返し必要になった時点で既存 archetype を使って小さく 1 件作る
- **marketplace ガバナンス (sandbox → traction → PR)** — 単一ユーザーで自前 marketplace なし
- **`${CLAUDE_PLUGIN_DATA}` への移行** — plugin uninstall で削除される領域。`~/.claude/skill-data/{skill}/` の一律置換は不適切。plugin 化する skill に限り採用
