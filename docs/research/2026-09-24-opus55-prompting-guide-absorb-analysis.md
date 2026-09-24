---
source: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5"
date: 2026-09-24
status: integrated
family: none
---

<!--
family は Phase 1.5 で判定。agentic-instruction-following のキーワードは "system prompt" の 1 つしか当たらず (閾値 2)、
他 family にも該当しないため none。隣接する過去 absorb: 2026-05-30-opus48-setup-guide / 2026-06-14-claude-fable5-system-prompt。
-->

## Source Summary

**主張**: Opus 5.5 は Opus 5 より出力が 30% 以上速く、同じタスクを少ないトークンで終える。既存の Opus 5 プロンプトはそのまま動くが、effort・無人ループ・進捗更新・refusal・frontend の既定 style など、観測される症状ごとに調整点がある。

**手法**:
- effort は `medium` (5.5 の既定) から始め、自分の eval で複数 level を測る。xhigh/max は品質向上を測れた仕事に限る。同じ level 名でも 5.5 は Opus 5 より多く考える
- 無人 agent は text-only の end_turn で止まる。チェックリスト + 未完了なら続行を促すメッセージ (blocker が述べられていなければ)、自動続行は 2〜3 回で打ち切る
- 無人用の standing system prompt 段落 (4 種の早期停止を名指し)。セッション開始時から system prompt に置く。human-in-the-loop では入れない
- `reasoning_extraction` refusal が Opus にも適用。応答に推論を再現させる指示を外す
- 進捗更新は `display: "updates"`、沈黙が続いたら turn-scoped system message でリマインド
- multi-agent に経過時間シグナル (`elapsed 340s / 1200s`)
- chat の「よく考えて」指示を外す / 過去の答えを確定扱いにする指示 (agentic では入れない)
- pasted text を `<pasted_content id>` で囲み system prompt で説明
- 図表は 5.5 単体で精度が高い。旧 scaffolding を再テスト、密な入力には crop ツール
- frontend の既定 style (cream/off-white 背景、見出しのイタリック強調語、`01/02/03` ラベル、monospace ラベル、pill ボタン) を名指しで禁じる。「generic を避けろ」は別の default に置き換わるだけ

**根拠**: Anthropic の社内評価 (coding / knowledge work / multi-app automation / agent team の研究タスク)。数値の多くは相対比較のみ。

**前提条件**: API 直利用者向けの記述が多い (`max_tokens`, `thinking.display`, turn-scoped system message)。Claude Code はその一部をハーネス側で既に実装している。

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | effort 較正 | Partial → **前提が変わった** | settings の top-level `effortLevel` (repo `xhigh` / live `high`) は **Opus 5.5 に効かない**。Claude Code docs (model-config「Adjust effort level」): "a top-level `effortLevel` in your user settings file doesn't count for Opus 5.5"。modelSettings も project settings の effortLevel も無いため、Opus 5.5 のメインセッションは実際には `medium` で動いていた。docs 3 箇所がこれと矛盾 |
| 2 | 無人用 standing 段落 | Gap | cmux Claude Worker は task 文を送るだけ |
| 3 | 自動続行 2〜3 回 + blocker | Partial | completion-gate の Ralph Loop は上限 7、blocker を述べても block し続ける |
| 4 | reasoning_extraction | Partial | `model-routing.md` の予防ルールが Fable 5 限定の記述 |
| 5 | pasted_content | N/A | Claude Code 本体がこの規約と system prompt 文言を既に注入している |
| 6 | 進捗更新・沈黙リマインド | N/A | API クライアント層の話。Claude Code が沈黙リマインドを既に注入 |
| 7 | 経過時間シグナル | 保留 | 速さと引き換えに検証が減りうるとガイド自身が注記 |
| 8 | 過去の答えを確定扱い | N/A | ガイドが agentic / 長い分析では入れるなと明記 |
| 9 | 「よく考えて」指示の除去 | Already | 該当なし (grep 0 件) |
| 10 | 先に広く探す | Already | search-first |
| 11 | 画像 scaffolding の再テスト | Partial (保留) | `gemini-delegation.md` の画像拡張子自動トリガー。再テスト未実施 |
| 12 | stale なモデル名 | Partial | 「現行: Opus 5」が 6 ファイル |
| A | frontend anti-patterns | Already (強化可能) | 5.5 の既定 style 5 種が未記載、曖昧な NG 行のみ |
| B | derivation-honesty「Show Your Work」 | Already (強化不要) | 成果物に根拠を書かせるもので、内部推論の再現要求ではない |

## Phase 2.5 (Refine)

- **Codex** (`gpt-5.6-terra`, read-only, xhigh, `project_doc_max_bytes=0`): 3 回目で取得。1〜2 回目は出力が空。2 回目の stderr に `Reading additional input from stdin...`、終了コード 124 (timeout) — background Bash で stdin が閉じておらず codex exec が待ち続けていた。`< /dev/null` で解消。1 回目は stderr を捨てていたため同原因かは未確認
  - 判定 (verbatim 抜粋): P1 `Change.` / P2 `Change the blocker wording; drop 7→3 for now.` / P3 `Do not merely append it to the task` / P4 `Change.` / P5 `Change.`
  - 反映: P2 の上限変更は見送り (カウンタが global で plan 単位にリセットされないことを `completion-gate.py:36-38,112-127` で確認)。blocker を書いたら gate が止まれるよう `(blocked:` 項目を未完了から除外。P3 は task 文ではなく `--append-system-prompt-file` で system prompt に入れた
- **Gemini** (agy): **未取得**。出力 verbatim: `jetski: no output produced — a tool required the "read_url" permission that headless mode cannot prompt for, so it was auto-denied.` 権限設定の変更は行わず Codex のみで進めた
- **Pass 1 (Sonnet Explore) の誤認 2 件を除外**: `launch-worker.sh` / `collect-result.sh` 不在、`docs/research/*` 不在 — いずれも `.config/claude/` 配下だけを探した誤認。repo root に実在

## Triage (ユーザー選択)

- effort: **medium のまま** (推奨どおり)。重い回は `ultrathink` か `/effort` の `s` (セッション限り)
- 取り込み: P1〜P5 すべて

## 実装

| # | ファイル | 変更 |
|---|---------|------|
| P1 | `references/debug-thinking-summary.md`, `workflow-guide.md`, `cheatsheet.md` | effortLevel が Opus 5.5 に効かないこと、既定 medium、`/effort` の per-model 保存を明記 |
| P2 | `scripts/policy/completion-gate.py` + test 3 件 | `(blocked:` 項目を pending から除外、差し戻し文に blocker の書き方を追加。上限 7 は据え置き |
| P3 | `scripts/runtime/launch-worker.sh` + `scripts/runtime/prompts/unattended-worker-system.md` | cmux Claude Worker にガイドの段落を system prompt として付与。herdr 版は `--dangerously-skip-permissions` で確認手順が無いため対象外 |
| P4 | `references/model-routing.md`, `advisor-strategy.md`, `decision-tables-index.md`, `cheatsheet.md` | reasoning_extraction を Opus 5.5 に拡張、「現行: Opus 5」→ 5.5 |
| P5 | ~~`skills/frontend-design/references/anti-patterns.md`~~ | 取り下げ。5.5 の既定 style 5 種を名指しする追記だったが、#259 で frontend-design skill ごと退役 (同名プラグインに一本化) したため追記先が無い |

## 検証

- `pytest tests/test_completion_gate_*.py`: 58 passed (新規 3 件は実装前に RED を確認)
- `bash -n launch-worker.sh`: OK。`claude -p --append-system-prompt-file <file>` で段落が system prompt に入ることを確認
- `task validate-configs` / `task validate-symlinks`: exit 0 (WARN 1 件は既存の `silent-failure-hunter` frontmatter で今回の差分外)
- **Review Gate: 未実施**。reviewer 7 体 (code / codex / security / edge-case / cross-file / test / gemini) が全員 HTTP 429 (`You've hit your session limit`) で判定を返さず、ユーザー指示で再実行を省略

## Follow-up (今回は実装しない)

- Ralph Loop のカウンタを plan 単位にする。そのうえで上限を 3 に下げる (ガイドの 2〜3 回)
- 画像の Gemini 自動委譲 (`rules/gemini-delegation.md`) を Opus 5.5 単体と比較して再評価
- 無人 worker での早期停止頻度を観測し、standing 段落の効果を確かめる
- Claim Verification Gate が `/` を含むブランチ名 (`chore/...`, `origin/master`) をパスと誤認した
