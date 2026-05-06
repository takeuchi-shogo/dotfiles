---
title: Memory Vector Hint - Phase C (Stop hook で memory write 検知 → 増分 reindex)
status: draft
created: 2026-05-07
parent_spec: docs/specs/2026-05-06-memory-vector-hint-spike.md
references:
  - docs/specs/2026-05-06-memory-vector-redactor-phase-a.md     # Phase A: redactor wrapper (S, complete)
  - docs/specs/2026-05-06-memory-vector-hint-spike.md           # Phase B: vector spike (PASS, AC 5/5)
  - .claude/worktrees/spike+memory-vector/tmp/spike-memory-vec/spike.ts  # 流用元 (cmdIndex)
acceptance_criteria:
  - Stop hook が settings.json に 1 件追加され、session 終了時に発火する (matcher は "*" で session_id ベース絞り込み不要)
  - hook が ~/.claude/skill-data/memory-vec/index.db の mtime と memory/*.md の latest mtime を比較し、index が古い場合のみ reindex を起動する
  - reindex は background subprocess (fire-and-forget) で起動され、hook 自体は 100ms 以内に exit 0 で返る (session 終了体験を阻害しない)
  - reindex は spike.ts の cmdIndex と同じ全 rebuild 戦略 (DROP+CREATE+全件 embed) で動作する
  - reindex 中に embed する各 file body は Phase A wrapper (redact_for_embedding) を通る (defense-in-depth)
  - reindex 完了で index.db が touch される (mtime 更新)、これが「最後の reindex 完了時刻」の sentinel になる
  - reindex 失敗時は ~/.claude/logs/memory-vec.log に追記され、hook は exit 0 を維持する (session 終了を block しない)
  - memory/*.md の mtime は reindex 前後で不変 (read-only 不変条件、Phase A AC4 と同じ)
scope: M
---

# Memory Vector Hint - Phase C: Stop hook で memory write 検知 → 増分 reindex

## Context

Phase B spike で「memory/*.md を sqlite-vec に embed すると semantic search が grep より明確に勝る」
ことを確認した (AC 5/5 PASS、5 query 中 4 で grep 0 hit、semantic 5 hit)。

現状の運用課題:
- index.db は spike 実行時に手動構築されたまま、memory/*.md が更新されても古いまま
- 手動 `npm run spike index` で再構築は可能だが、運用負荷が高い

Phase C は Stop hook で memory write を検知し、session 終了時に index.db を自動更新する。
**source of truth は file-based MEMORY.md 系のまま**で、index.db はあくまで hint layer (親 spec の絶対遵守事項)。

## Tech Spec

### データフロー

```
[memory/*.md への Write/Edit]
        ↓ (session 内に何度発生してもよい)
[Stop event 発火]
        ↓
[memory-vec-stop-hook.py]
   1. memory/*.md の latest mtime を取得
   2. ~/.claude/skill-data/memory-vec/index.db の mtime と比較
   3. index が古い場合のみ → subprocess.Popen で background reindex
   4. hook は 100ms 以内に exit 0
        ↓ (background)
[memory-vec-reindex.ts]
   1. spike.ts の cmdIndex と同じ手順で全 rebuild
   2. ただし embed の前に Phase A wrapper (redact_for_embedding) を通す
   3. 完了時に index.db を touch (sentinel 更新)
   4. 失敗時は ~/.claude/logs/memory-vec.log に追記、exit 0
```

### state 管理

- **明示的な state ファイル不要** — index.db ファイル自身の mtime を「最後の reindex 完了時刻」の sentinel として使う
- 起動条件: `max(mtime(memory/*.md)) > mtime(index.db)` のみ
- `.dirty` フラグや別 sentinel ファイルを作らない (KISS)

### redactor 統合方法

reindex.ts の embed loop 内で:
```ts
const raw = readFileSync(path, "utf8");
const clean = await redactSubprocess(raw);  // python3 で Phase A wrapper を呼ぶ
const emb = await embed(clean.slice(0, 2000));
```

`redactSubprocess` は `python3 -c` で stdin 経由 stdout 受け取り。child_process.execFileSync で同期実装。

### 主要な技術判断

- **全 rebuild vs 差分**: 全 rebuild を採用 (50 files / 5-7s / state 管理不要)。差分は rowid 同期・部分失敗 recovery で複雑化、現状規模では不要 (KISS)
- **同期 vs 非同期**: 非同期 (subprocess.Popen + close stdin/stdout/stderr) を採用。session 終了体験を阻害しない、reindex の 5-7s をユーザーに待たせない
- **Python vs TS hook**: hook 本体は Python (既存 runtime hook と統一)、reindex は TS (spike.ts 流用)
- **エラー扱い**: silent + log。hook 失敗で session 終了を block するのは過剰

## Requirements

### R1. Stop hook script

- `.config/claude/scripts/runtime/memory-vec-stop-hook.py` を新規追加
- stdin で hook payload を受け取る (session_id, transcript_path 等は使わない、matcher で絞り込まない)
- memory/*.md の最新 mtime を `pathlib.Path.stat().st_mtime` で取得
- index.db (`~/.claude/skill-data/memory-vec/index.db`) が存在しない場合は mtime=0 として扱う (初回起動扱い)
- 比較で reindex 必要なら `subprocess.Popen([node, reindex_script], stdin/stdout/stderr=DEVNULL, start_new_session=True)` で fire-and-forget
- hook 全体は exit 0 (例外時も log + exit 0)
- timeout 100ms を超えたら自動 exit (内部 timeout)

### R2. Reindex script

- `.config/claude/scripts/runtime/memory-vec-reindex.ts` を新規追加
- spike.ts の cmdIndex 関数のロジックをそのまま流用 (DROP+CREATE+全件 embed)
- 各 file body を embed する直前に Phase A wrapper (`redact_for_embedding`) を通す
- 完了時に `Path(DB_PATH).touch()` 相当で mtime 更新 (Node では `utimesSync`)
- 失敗時は `~/.claude/logs/memory-vec.log` に `{timestamp, error, traceback}` を JSON line として追記
- exit code は常に 0 (hook 側で監視しない)

### R3. settings.json への hook 登録

- `.config/claude/settings.json` の `hooks.Stop` 配列に 1 件追加
- 既存の Stop hook と並べる形 (順序依存なし)
- matcher: `"*"` (session 全体)
- type: `"command"`, command: `".config/claude/scripts/runtime/memory-vec-stop-hook.py"`

### R4. 依存関係

- Phase A wrapper (memory_redactor.py) が `~/.claude/skill-data/memory-vec/lib/memory_redactor.py` または等価 path に配置されている必要がある
- Reindex.ts が import path を解決できる前提
- ※worktree 内 (`tmp/spike-memory-vec/memory_redactor.py`) は spike 専用で本実装からは見えない → **本実装で別 path にコピーする (R4.1)**

#### R4.1. wrapper の配置

- `~/.claude/skill-data/memory-vec/lib/memory_redactor.py` に Phase A wrapper をコピー (恒久化)
- このファイルは `~/.claude/skill-data/` 配下なので git 管理外、削除で完全戻し可
- 元の `.config/claude/scripts/lib/redactor.py` への sys.path 解決は本実装で再調整 (worktree 前提が消える)

## Constraints

- **memory/*.md の write 禁止** (read-only 不変、Phase A から継続)
- **source of truth ≠ hint layer 境界** (親 spec の絶対遵守、Codex 警告の中核)
- **hook 性能**: Stop hook は 100ms 以内に exit 0、subprocess.Popen で background 化必須
- **reindex 性能**: 50 files で 5-7s 以内 (Phase B spike 実測ベース)、100 files で 15s 以内が許容上限
- **harness 変更検知**: settings.json への hook 追加は Codex Review Gate 対象 → /review 必須
- **既存 Stop hook との競合禁止**: 既存 hook の挙動を破壊しない、`task validate-configs` PASS 維持
- **API key 等の依存禁止**: embedding は @xenova/transformers (local model)、外部 API 呼び出しなし

### 検証方法

- 動作確認: memory/MEMORY.md を `touch` した後、session を終了 → 数秒後に index.db の mtime が更新される
- mtime 不変確認: reindex 前後で `find memory -newer <ts>` が 0 件
- hook 性能: `time .../memory-vec-stop-hook.py < /dev/null` で <100ms
- 失敗系: index.db が壊れた状態で reindex → log にエラー、hook は exit 0
- bench 再実行: `npm run spike bench` で Phase B と同等の semantic recall を確認

## Extensibility Checkpoint

- **embedding model 変更**: reindex.ts の `EMBED_MODEL` 1 行変更で対応 (DIM も連動)
- **chunking 戦略変更**: 現状 file 全体を 1 vector (body.slice 0-2000)。chunk 化は cmdIndex 内の loop 改造のみで対応
- **対象拡大** (memory 以外も index 化): Stop hook の glob を拡張するだけ。reindex 側はそのまま
- **incremental reindex への昇格**: docs テーブルに `mtime` カラム追加 + 比較ロジック改造で実現可。現 spec はインターフェース不変
- 想定される cascading rewrite: なし

## Out of Scope

- SessionStart での hint 注入 (Phase D で別 spec)
- 増分 reindex (Phase D 後に必要なら別 spec)
- vector index 内容の auto-injection (Codex 警告の中核、絶対やらない)
- query / bench 機能の本実装化 (CLI として残す、本実装では index 更新のみ)
- 別 vault (Obsidian など) への対象拡大
- mem0 / Qdrant への移行 (本実装で sqlite-vec 安定運用できているなら不要)

## Prompt

以下の仕様に基づいて Phase C を実装してください:

1. `~/.claude/skill-data/memory-vec/lib/memory_redactor.py` に Phase A wrapper をコピー (worktree 外で完結させる)
2. `.config/claude/scripts/runtime/memory-vec-stop-hook.py` を新規作成:
   - stdin payload 受け取り、memory/*.md と index.db の mtime 比較
   - 必要なら `subprocess.Popen([node, reindex.ts], DEVNULL, start_new_session=True)` で background 起動
   - 100ms 内 exit 0 を保証 (内部 timeout 含む)
3. `.config/claude/scripts/runtime/memory-vec-reindex.ts` を新規作成:
   - spike.ts の cmdIndex を流用
   - embed 直前に Python redactor を subprocess で呼ぶ (`execFileSync("python3", ["-c", "..."], {input: text})`)
   - 完了時に index.db を utimes で touch
   - 失敗時 `~/.claude/logs/memory-vec.log` に追記、exit 0
4. `.config/claude/settings.json` の `hooks.Stop` に 1 件追加 (matcher "*"、command 上記 hook)
5. 検証:
   - `task validate-configs` PASS
   - memory/MEMORY.md を touch → session 終了 → 数秒後に index.db mtime 更新を確認
   - reindex 前後で memory/*.md の mtime が変化しないことを stat で比較
   - bench 再実行 (`npm run spike bench`) で Phase B と同等結果
6. 完了報告には:
   - 追加 hook の発火確認 log (1 セッション分)
   - reindex の実測 latency (50 files でかかった秒数)
   - settings.json の diff (hook 1 件追加のみ)

実装は最小限。embedding ロジックや query 機能は触らない (Phase B 流用に徹する)。
