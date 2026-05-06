---
title: Memory Vector Hint - Phase A (redactor pre-processing layer)
status: draft
created: 2026-05-06
parent_spec: docs/specs/2026-05-06-memory-vector-hint-spike.md
references:
  - .config/claude/scripts/lib/redactor.py        # 流用する既存 redactor (read-only)
  - .config/claude/scripts/tests/test_redactor.py # 既存テスト (拡張せず参照)
  - docs/specs/2026-04-17-memory-schema-retention.md  # memory scope の境界定義
acceptance_criteria:
  - redact_for_embedding(text: str) -> str が memory_redactor.py に存在し、既存 redactor.redact() を delegate する薄い wrapper として動作する
  - .config/claude/scripts/lib/redactor.py は一切変更されない (git diff で確認、行数も同一)
  - 既知 secret fixture (sk-token, ghp_PAT, AKIA, Bearer, JWT eyJ..) を含む文字列を wrapper に渡すと全て [REDACTED] 化される
  - memory/*.md 全件に対し wrapper を通した sample run 実行後、各ファイルの mtime が変化しない (read-only 確認)
  - sample run が tmp/spike-memory-vec/redact-report.json に各ファイル単位で {path, bytes_in, bytes_out, redaction_count} を書き出す
  - redact-report.json の人間レビューで「明らかな false positive」(技術用語・コードフェンス内のサンプル等) が確認できる程度の情報粒度がある
scope: S
---

# Memory Vector Hint - Phase A: redactor pre-processing layer

## Context

親 spec `2026-05-06-memory-vector-hint-spike.md` は memory/*.md を embed して semantic
search を試す spike だが、embed 対象に万一 secret が混入していた場合に SQLite vector
index に平文で書き込まれるリスクがある (memory には現状 secret は記録されない運用だが、
ユーザー操作ミスで一時的に紛れ込む可能性は残る)。

Phase A は Phase B (embedding/index) を走らせる前の **前処理層** を最小コストで用意する。
スコープを「既存 `redactor.redact()` を embedding 用途に再利用するための薄い wrapper を
spike worktree 内に置く」だけに絞り、redactor 本体・運用 hook・恒久ファイル配置には
一切手を出さない。

Codex 警告 (親 spec) で示された境界「source of truth と hint layer を混ぜない」を守るため、
本層は **memory/*.md 自体を書き換えない**。redact 後の文字列は呼び出し側 (Phase B) が
embedding 入力としてのみ消費する。

## Requirements

### R1. Wrapper API

- `tmp/spike-memory-vec/memory_redactor.py` に以下を定義する:
  ```python
  from typing import NamedTuple
  def redact_for_embedding(text: str) -> str: ...
  def redact_with_stats(text: str) -> RedactStats: ...   # 観測用 (R4 で使用)
  ```
- `redact_for_embedding` は既存 `.config/claude/scripts/lib/redactor.redact` をそのまま
  呼ぶ。新規パターン追加・heuristic 変更は禁止。
- `RedactStats` は最低 `text: str`, `bytes_in: int`, `bytes_out: int`,
  `redaction_count: int` を持つ。`redaction_count` は `[REDACTED]` の出現数を後処理で数える。

### R2. redactor 本体の不変性

- `.config/claude/scripts/lib/redactor.py` を変更しない。
- `git diff HEAD -- .config/claude/scripts/lib/redactor.py` が空であることを完了時に確認する。
- 新規 import は `from redactor import redact` (sys.path 調整は memory_redactor.py 内に局所化)。

### R3. memory/*.md の read-only 保証

- wrapper は memory/*.md を **書き戻さない**。
- sample run スクリプト (R4) は `Path.read_text(encoding="utf-8")` のみを呼び、open(..., "w") を含まない。
- 完了基準: sample run 前後で `find ~/.claude/projects/-Users-takeuchishougo-dotfiles/memory -name "*.md" -newer <timestamp>` が 0 件。

### R4. Sample run + 観測ログ

- `tmp/spike-memory-vec/run_sample.py` を作成し、以下を行う:
  1. `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/*.md` を glob で列挙
  2. 各ファイルを read_text で読み、`redact_with_stats` を適用
  3. 結果を `tmp/spike-memory-vec/redact-report.json` に append (file 単位の list)
  4. summary を stdout に出す: 総ファイル数 / 総 redaction_count / max redaction を持つ top-3 ファイル
- log の `redaction_count > 0` のファイルは Phase B 着手前に人間が目視レビュー可能な形にする
  (path と一緒に redact 後の差分要約を含めることまではしない、過剰実装回避)。

### R5. 既知 secret fixture テスト

- `tmp/spike-memory-vec/test_memory_redactor.py` を作成し、以下を検証:
  - `redact_for_embedding("sk-XXXXXXXXXXXXXXXXXXXXXXXXXX")` の戻り値に `[REDACTED]` が含まれる
  - 同様に `ghp_<36 chars>`, `AKIA<16>`, `Bearer <token>`, `eyJ...eyJ...XXX` (JWT) を全件カバー
  - false positive 観測テスト: 通常の technical prose ("Codex Review Gate", "subagent",
    "MEMORY.md") を渡しても `[REDACTED]` が出ないことを確認 (これが出たら redactor 本体の
    既知の FP を Phase A で表面化させる材料になる)

## Constraints

- **redactor.py 本体への変更禁止** (Track A2 の責任範囲、本 spec のスコープ外)
- **memory/*.md の write 禁止** (親 spec の絶対遵守事項)
- **新規依存追加禁止** (stdlib のみで実装可能)
- **設定ファイル (settings.json / hooks) 触らない** (Stop hook 統合は次フェーズ以降)
- **runtime 性能要件なし** (本層は spike 内でのみ呼ばれ、hook path に乗らない)
- **検証方法**: 既知 secret fixture テスト + memory/*.md sample run の mtime 不変確認

## Extensibility Checkpoint

- **新 secret パターン追加**: redactor.py 本体に追加 → wrapper は自動で恩恵を受ける (variable 追加なし)
- **embedding model 切替**: wrapper は文字列 in/out なので embedding 側の変更で影響なし
- **適用範囲拡大** (memory 以外の md も対象化): wrapper は触らず、呼び出し側 (Phase B 以降) の
  glob パターンを拡張すればよい。本層が拡張点として機能する
- 想定される cascading rewrite: なし (薄い wrapper の利点)

## Out of Scope

- redactor.py 本体への新パターン追加・heuristic 改良 (別 spec で扱う)
- Phase B 範囲: file loader / chunking / embedding / SQLite vector index 構築
- transcripts (`~/.claude/projects/*/*.jsonl`) への post-hoc redactor 適用
  (memory schema retention spec の future work、別 PR)
- Stop hook / SessionStart hook への統合 (vector spike 成功確定後に別 spec)
- Vault (`obsidian-vault/**/*.md`) など memory 以外の md への適用
- redaction 結果の永続化 (sample run の report.json のみ、本番経路には乗せない)

## Prompt

以下の仕様に基づいて Phase A を実装してください:

1. worktree `.claude/worktrees/spike+memory-vector/` 内に作業する
2. `tmp/spike-memory-vec/` ディレクトリを作成し、以下 3 ファイルを作る:
   - `memory_redactor.py` — `redact_for_embedding(text)` と `redact_with_stats(text)` の wrapper
   - `run_sample.py` — memory/*.md 全件を glob し redact_with_stats を流して `redact-report.json` を出力
   - `test_memory_redactor.py` — 既知 secret fixture と FP チェック
3. `redact-report.json` フォーマット例:
   ```json
   [
     {"path": "/Users/.../memory/MEMORY.md", "bytes_in": 12345,
      "bytes_out": 12345, "redaction_count": 0},
     ...
   ]
   ```
4. 検証:
   - `pytest tmp/spike-memory-vec/test_memory_redactor.py -v` が PASS
   - `python tmp/spike-memory-vec/run_sample.py` 実行後、memory/*.md の mtime が
     実行前と変化していないことを確認 (実行前に `stat -f "%m %N" memory/*.md` を取って比較)
   - `git diff -- .config/claude/scripts/lib/redactor.py` が空である
5. 完了報告には以下を含める:
   - sample run の summary (総ファイル数 / 総 redaction_count / top-3)
   - false positive と疑われる行が出ていれば該当 path のみ列挙 (内容の表示は最小限に)
   - Phase B (embed/index 構築) に進める判定

実装は最小限に保ち、abstraction は導入しないこと (S 規模)。
