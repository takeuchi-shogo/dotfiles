---
title: Memory Vector Hint - Phase D (SessionStart hook で関連 memory path を hint 提示)
status: complete
created: 2026-05-07
implemented: 2026-05-08
parent_spec: docs/specs/2026-05-06-memory-vector-hint-spike.md
references:
  - docs/specs/2026-05-06-memory-vector-redactor-phase-a.md     # Phase A: redactor (complete)
  - docs/specs/2026-05-06-memory-vector-hint-spike.md           # Phase B: spike (PASS)
  - docs/specs/2026-05-07-memory-vector-phase-c-stop-hook.md    # Phase C: Stop hook reindex
  - .claude/worktrees/spike+memory-vector/tmp/spike-memory-vec/spike.ts  # 流用元 (semanticTopK)
acceptance_criteria:
  - SessionStart hook が settings.json に 1 件追加され、新規 session 起動時に発火する
  - hook が cwd の ./HANDOFF.md を読み込み、最後 1000 文字を query として semantic top-K を取得する
  - HANDOFF.md が存在しない / 空の場合は hint を skip する (no-op、stdout 何も出さない)
  - ~/.claude/skill-data/memory-vec/index.db が存在しない場合は hint を skip する
  - top-K (K=5、distance < 1.5 の閾値あり) の path 一覧を additionalContext として stdout に出力する
  - 出力には file body を一切含めない (path のみ)、auto-inject 禁止の境界を機械的に強制する
  - 出力 format: "[Memory Hint] HANDOFF intent から関連 memory:\n- path1 (rel: 0.42)\n- path2 ..." + 末尾に "Read tool で必要時に展開してください"
  - hook 全体 latency が warm start ~500ms / cold start ~2000ms 程度 (model load + ONNX init による下限。SessionStart の許容範囲内)
  - HANDOFF.md / memory/*.md / index.db の mtime が hook 実行前後で不変 (read-only)
  - 失敗時 (embedding error 等) は ~/.claude/logs/memory-vec.log に追記、hook は exit 0 で空出力 (session 起動を阻害しない)
scope: M
---

# Memory Vector Hint - Phase D: SessionStart hook で関連 memory path を hint 提示

## Context

Phase B spike で「semantic 検索が grep より明確に勝る」ことを実証 (5 query 中 4 で grep 0 hit)、
Phase C で index.db の自動更新パイプラインを spec 化した。

Phase D はこの index を **session 起動時に自動的に活用** する。
ユーザーが意図 (HANDOFF.md) を残していれば、関連性の高い memory ファイルの path を提示し、
Claude が必要に応じて Read で開けるようにする。

### 設計境界 (絶対遵守、親 spec の Codex 警告を再掲)

> 「最大の罠 = MEMORY.md を semantic layer で置換 → source of truth と hint の境界を壊す」

Phase D はこの罠を回避するため:
- **path のみ提示**、file body は hook output に絶対含めない
- **既存 SessionStart の MEMORY.md auto-inject 経路を変更しない** (現行通り MEMORY.md は自動注入)
- hint は「補助的提案」として additionalContext に出すだけ、Claude が読むかは判断に委ねる

## Product Spec

### ユーザー体験

1. ユーザーが `/checkpoint` で前 session 終了時に HANDOFF.md を残す
2. 翌日 / 別タスクで session を起動する
3. SessionStart 時に Claude が以下を見る:
   - 既存の MEMORY.md auto-inject (現行通り)
   - **新規**: `[Memory Hint] HANDOFF intent から関連 memory:` + path 5 件 (本 spec の追加分)
4. Claude は path 一覧を見て、必要と判断したら Read tool で展開
5. ユーザーは何も追加操作不要、自動的に「過去の関連知見」へのリンクが手元に来る

### エラー時の挙動

- HANDOFF.md なし → hint なし (静か、何も出さない)
- index.db なし → hint なし
- embedding 失敗 → hint なし + log 追記
- 結果が distance threshold (1.5) を超える → 該当ファイルだけ除外、残りを提示
- 全件除外された → hint なし

## Tech Spec

### データフロー

```
[SessionStart event 発火]
        ↓
[memory-vec-hint-hook.py]
   1. cwd/HANDOFF.md を read (なければ exit 0、空出力)
   2. 最後 1000 文字を抽出 → query
   3. ~/.claude/skill-data/memory-vec/index.db 存在確認 (なければ exit 0)
   4. node child_process で semanticTopK(query, 5) 呼び出し
   5. distance < 1.5 でフィルタ
   6. 出力 format に整形して stdout
        ↓ (Claude additional context として注入)
[Claude が SessionStart 時にコンテキスト受領]
   - 通常の MEMORY.md auto-inject (既存)
   - [Memory Hint] block (本 spec)
        ↓
[必要時に Claude が Read tool で path を展開]
```

### 出力形式 (固定)

```
[Memory Hint] HANDOFF intent から関連 memory (top-5):
- /Users/.../memory/codex_attention_depth.md (rel: 1.08)
- /Users/.../memory/feedback_codex_reasoning.md (rel: 1.13)
- /Users/.../memory/subagent_patterns.md (rel: 1.14)

Read tool で必要時に展開してください。本 hint に file 内容は含まれません。
```

末尾の「内容は含まれません」明示は、Codex 警告の境界を Claude にも伝える教育的役割。

### 主要な技術判断

- **query 抽出**: 「HANDOFF.md 最後 1000 文字」を採用。HANDOFF は append-style ではないので構造化抽出は過剰、tail 1000 chars で latest intent を捕捉
- **top-K = 5**: token 予算 ~300 (path 5 件 + format)、Claude context への影響最小化。spike の bench で 5 件は relevance 順に十分絞れることを確認
- **distance threshold = 1.5**: 実 distribution は概ね 1.08-1.20 の範囲に top-5 が収まる (全 50 file に対する all-MiniLM-L6-v2 の相対距離)。1.0 では top-5 全件落ちて hint が空になるため、1.5 で実用 5 件を確保しつつノイズ (distance > 1.5) は弾く
- **既存 SessionStart hook と並列**: 新規 hook 追加で既存挙動 (env-bootstrap、MEMORY.md auto-inject 等) は不変
- **同期 vs 非同期**: SessionStart は session 起動を待つ blocking event、ここで非同期化はできない。実測 latency 内で完結
- **embedding model のロードコスト**: warm start ~500ms / cold start ~2000ms。SessionStart は session ごとに 1 回だけなので許容範囲

## Requirements

### R1. SessionStart hook script

- `.config/claude/scripts/runtime/memory-vec-hint-hook.py` を新規追加
- stdin で SessionStart payload (cwd, source 等) を受け取る
- cwd 配下の `HANDOFF.md` を `Path("HANDOFF.md").read_text(errors="ignore")` で読む
- 最後 1000 文字を `text[-1000:]` で抽出 (空 / なし → exit 0、空出力)
- index.db (`~/.claude/skill-data/memory-vec/index.db`) 存在確認、なければ exit 0
- `subprocess.run([node, query.ts, query], capture_output=True, timeout=5.0)` で semantic 取得
- 結果を「## R3 出力 format」に整形して stdout に出力
- exit 0 を保証 (例外時も log + 空出力)

### R2. Query script

- `~/.claude/skill-data/memory-vec/query.ts` を新規追加
  (Phase C reindex.ts と同じ理由: node_modules と同じ dir に置くことで ESM resolver が
   `@xenova/transformers` と `sqlite-vec` を解決できる)
- spike.ts の `semanticTopK` 関数のみ抽出して書き出す
- argv[2] を query として受け取り、JSON 配列で stdout 出力:
  `[{"path": "...", "name": "...", "distance": 1.08}, ...]`
- distance threshold 適用は呼び出し側 (hook script) が行う

### R3. 出力 format

```
[Memory Hint] HANDOFF intent から関連 memory (top-5):
- {abs_path1} (rel: {distance1:.2f})
- {abs_path2} (rel: {distance2:.2f})
...

Read tool で必要時に展開してください。本 hint に file 内容は含まれません。
```

末尾改行 1 個。distance は小数点 2 桁まで。

### R4. settings.json への hook 登録

- `.config/claude/settings.json` の `hooks.SessionStart` 配列に 1 件追加
- 既存 SessionStart hook (env-bootstrap 等) と並べる、順序依存なし
- matcher: `"startup"` (resume / clear ではなく新規 startup のみ)
- type: `"command"`, command: `"python3 $HOME/.claude/scripts/runtime/memory-vec-hint-hook.py"`
- timeout: 10 (cold start ~2000ms に対し余裕を持たせる)

### R5. 依存関係

- Phase C の reindex によって index.db が新鮮であること (古い index でも動作はする、relevance が下がるだけ)
- Phase A wrapper はここでは使わない (read-only 経路、redact 不要)
- `~/.claude/skill-data/memory-vec/` で `pnpm install` 済み (Phase C と共有)

## Constraints

- **HANDOFF.md / memory/*.md / index.db すべて read-only** (Phase A から継続)
- **file body を hook output に含めない** (auto-inject 境界、Codex 警告遵守)
- **既存 SessionStart hook を破壊しない** (env-bootstrap、MEMORY.md auto-inject 等)
- **hook 性能**: warm ~500ms / cold ~2000ms (model load + ONNX init 由来の下限)。これを超える失敗時は subprocess timeout (5s) で skip
- **token 予算**: hook output は最大 ~500 token (path 5 件 + format)、Claude context 圧迫を最小化
- **harness 変更**: settings.json への hook 追加は Codex Review Gate 対象 → /review 必須
- **session source**: matcher を "startup" のみにし、resume / clear では発火させない (resume は前 session の context を引き継ぐので hint 重複)

### 検証方法

- 動作確認: HANDOFF.md がある repo で `claude` 起動 → 初回 prompt 前に [Memory Hint] block が context に含まれる
- HANDOFF.md なし: 起動しても hint なし (silent)
- mtime 不変: hook 前後で HANDOFF.md / memory/*.md / index.db の mtime が変化しない
- 性能: `time .../memory-vec-hint-hook.py < /dev/null` で warm <1000ms / cold <3000ms
- Codex 警告遵守確認: hook output を grep して file body fragment が含まれていないこと (path 文字列のみ)
- bench 連携: Phase C reindex 直後に hint を取れば、最新 memory が反映されている

## Extensibility Checkpoint

- **K の変更**: hook script の `TOP_K = 5` を変更するだけ。format への影響なし
- **threshold の変更**: hook script の `DISTANCE_THRESHOLD = 1.5` を変更するだけ
- **query source の追加**: HANDOFF.md 以外 (e.g., git branch 名) を補助的に concat したくなった場合は hook 内の query 構築部 1 関数のみ改造
- **format の改造**: 出力 format は hook script 内の 1 関数。Claude 側の解釈は path 列挙の寛容な前提なので影響なし
- 想定される cascading rewrite: なし (hook + query script の 2 ファイルに収束)

## Out of Scope

- **file body の inject** (絶対やらない、Codex 警告の中核)
- HANDOFF.md 構造の変更 (現行 /checkpoint 出力に従う)
- query source の動的選択 UI (本 spec では HANDOFF.md 固定、別 spec で議論)
- hint 結果の persistence (今回 hint は揮発、別 spec で履歴化議論)
- vault (Obsidian) や他 directory への対象拡大 (Phase B/C と同じく memory/*.md のみ)
- mem0 / Qdrant への移行
- chat history からの query 抽出 (UserPromptSubmit hook 別 spec で議論)

## Implementation Notes (post-implementation 追記、2026-05-08)

- distance threshold は spec 当初 1.0 だったが、実 distribution が 1.08-1.20 に集中していたため
  全件 hint 0 になり 1.5 に緩和。経験値で運用調整可能
- subprocess timeout は spec 当初 2.0s だったが cold start (model load) で超過するため 5.0s に拡大
- query.ts の配置を spec 当初 `.config/claude/scripts/runtime/` から `~/.claude/skill-data/memory-vec/`
  に変更 (Phase C reindex.ts と同じ理由 — ESM resolver の node_modules 探索)
- spec 当初の latency target 300ms は cold start を考慮していなかった。実装で warm 500ms / cold 2s に
  改定 (SessionStart は session 1 回限りのため許容)

## Prompt

以下の仕様に基づいて Phase D を実装してください:

1. `.config/claude/scripts/runtime/memory-vec-hint-hook.py` を新規作成:
   - stdin payload 受け取り、cwd/HANDOFF.md を tail 1000 chars 抽出
   - HANDOFF.md / index.db いずれかなければ exit 0 (空出力)
   - `subprocess.run([node, "~/.claude/skill-data/memory-vec/query.ts", query], timeout=5.0)` で semantic top-5 取得
   - distance < 1.5 でフィルタし、Requirements R3 の format で stdout 出力
   - 例外時は ~/.claude/logs/memory-vec.log に追記、exit 0 で空出力
2. `~/.claude/skill-data/memory-vec/query.ts` を新規作成:
   - spike.ts の `semanticTopK` を切り出して JSON 出力する CLI
   - argv[2] を query として受け、`[{path, name, distance}]` を stdout
3. `.config/claude/settings.json` の `hooks.SessionStart` に matcher "startup" で 1 件追加
4. 検証:
   - `task validate-configs` PASS
   - HANDOFF.md がある cwd で `claude` 起動 → 初回 prompt 前に [Memory Hint] block 出力確認
   - HANDOFF.md なしで `claude` 起動 → hint なし、stdout 空
   - hook output を `grep` で file body 片が混入していないことを確認 (path 文字列のみ)
   - `time` で warm <1000ms / cold <3000ms
5. 完了報告には:
   - hint output のサンプル (1 セッション分、path 5 件含む)
   - hook latency 実測値 (cold/warm 両方)
   - settings.json の diff (hook 1 件追加のみ)
   - Codex 警告遵守の証跡 (output に file body なしの確認方法)

実装は最小限。query 強化や source 追加 (git branch 等) は別 spec で扱う (本 spec は HANDOFF.md 固定)。
