---
status: reference
last_reviewed: 2026-05-30
---

# Retired Concepts Registry

退役した概念 (skill / command / agent / hook / 設計用語) を 1 箇所で台帳化する。
目的は **auditability** — 「削除済みのものへ先祖返りで言及していないか」を legible にする
(claude-code-harness の `deleted-concepts.yaml` に相当する設計、Negative Constraints パターン)。

## 使い方 / 検出ルール

- `doc-garden-check.py` (PostToolUse モード) が、編集された live doc
  (`CLAUDE.md` / `AGENTS.md` / `references/`) 中に **status=確定** の `id` が現れたら advisory warn を出す。
- **status=曖昧 は documented-only** — 検出対象にしない。実体 (skill/command/agent) がまだ残存していたり、
  「廃止」と「現存ファイル」が矛盾しているケースで、断定を避けて事実だけを記録する。
- 本ファイル自身と `docs/research/*` 等の historical doc は検出対象外
  (前者は id を列挙するため、後者は退役前の事実を保存する性質のため)。
- single source は registry の表。`id` はリテラル文字列として substring 一致で照合する (正規表現にしない)。

## Registry

| id | retired-date | replacement | rationale | status |
|----|--------------|-------------|-----------|--------|
| `gleam-practice` | 2026-05-10 | (なし、削除) | commit 1e6e388「remove 3 unused language skills」で削除。Gleam は実運用言語でなく利用実績なし。skills-lock.json からも除外済 | 確定 |
| `moonbit-practice` | 2026-05-10 | (なし、削除) | commit 1e6e388「remove 3 unused language skills」で削除。MoonBit は実運用言語でなく利用実績なし。skills-lock.json からも除外済 | 確定 |
| `/improve` | 2026-05-03 | `/audit` + 各 review skill | `improve-policy.md` frontmatter は `status: deprecated` (5 サイクル連続 false-positive)。ただし `commands/improve.md` (Tidy Orchestrator) + `improve` skill 登録 + `autoevolve-core.md` の参照群が現存し、「廃止」と実体が矛盾する。断定せず事実を記録 | 曖昧 |
| `autoevolve-core` (直接呼び出し) | 2026-05-03 | (なし、保守用 legacy) | `/improve` command retire に伴い新規呼び出し非推奨。agent 定義自体は `scripts/learner/*` 連携の保守用として現存 | 曖昧 |
| `memory-archive.py` | 2026-06-01 (削除予定 2026-07-01) | `claudemd-size-check.py` の MEMORY.md 検知 + `docs/playbooks/memory-pruning.md` (手動 pruning) | dead script (呼び出し0/テスト0/hook未登録)。archive ロジックが「ファイル位置=古さ」を仮定するが MEMORY.md はトピック別構造のため、実行すると前半のコア知識を archive し肥大化した外部知見索引を残す逆効果 (2026-05-31 検出)。determinism boundary により archive 判断は judgment、検知のみ mechanism 化 (Codex+Opus C 案)。deprecation 中で実体現存のため status=曖昧 | 曖昧 |

## エントリ追加の指針

- skill/command/agent/hook を削除したら、relocate (改名・command 化) でない限りここに **確定** で 1 行追加する。
- relocate の場合は replacement 列に移転先を書き、status は relocate 元名が live で参照され続けるなら **曖昧** とする
  (誤検出ノイズを避けるため。例: live 参照が多い `senior-*` 系は意図的に未登録)。
- 退役日は `git log --diff-filter=D -1 --format=%ad --date=short -- <path>` で確認する。
