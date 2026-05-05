---
date: 2026-05-04
task: T2 — SessionStart Hook 監査 + 剪定
status: integrated
scope: ~/.claude/scripts/runtime/{env-bootstrap.py, sessionstart-audit.py}
references:
  - docs/research/2026-05-04-claude-code-overhead-9patterns-absorb-analysis.md
  - tmp/plans/merry-conjuring-dewdrop.md
---

# SessionStart Hook Audit Report

## 目的

absorb 9-patterns plan の T2。SessionStart で発火する 6 hook の **stdout / stderr / latency** を実測し、cache prefix を破壊する volatile 出力と性能ボトルネックを特定。剪定可能な範囲を実施し、継続監査スクリプトを残す。

## Verification Target (absorb plan T2)

- 各 hook stdout < 200 bytes (cache prefix の対象は stdout のみ)
- 合計 latency < 3 秒

## 重要な発見: stdout / stderr の役割分離

stdout/stderr を分けて測定したところ、**session-load.js の volatile 出力 (`Time: 0.1h ago (2026-05-04T...)`) は stderr のみ** で、cache prefix を破壊しないことが判明。当初の想定 (session-load.js が cache 影響している) は誤りだった。

| 流入経路 | 影響 |
|---------|------|
| **stdout** | additionalContext として system prompt / cache prefix に流入 → volatile 削減必須 |
| **stderr** | UI 表示のみ。cache prefix には影響しない (Claude Code 仕様) |

これに従い session-load.js の修正は本 Plan の scope 外として降格、env-bootstrap.py の stdout に集中した。

## Before / After 実測

### Before (Plan 開始時)

| hook | stdout | stderr | latency | flag |
|------|--------|--------|---------|------|
| session-load.js | 0B | 933B | 0.32s | ok (cache 影響なし) |
| checkpoint_recover.py | 0B | 0B | 0.06s | ok |
| timestamp-write | 0B | 0B | <0.01s | ok |
| **env-bootstrap.py** | **559B** | 0B | **2.57s** | OVER200B (cold cache) |
| memory-integrity-check.py | 198B | 0B | 0.14s | ok (target 圏内) |
| harness-snapshot.py | 0B | 50B | 0.11s | ok |
| **合計 latency** | | | **3.20s** | OVER3s |

### After (本 Plan 適用後、UTF-8 byte 換算)

| hook | stdout | stderr | latency | flag |
|------|--------|--------|---------|------|
| **session-load.js** | 0B | 669B | 0.25s | **VOLATILE-ERR** (新検出 — stderr のみ、cache 影響なし) |
| **checkpoint_recover.py** | **279B** | 0B | 0.03s | **OVER200B + VOLATILE-OUT** (新検出 — F2 として残課題) |
| timestamp-write | 0B | 0B | <0.01s | ok |
| **env-bootstrap.py** | **266B** | 0B | 0.54s | OVER200B (target 未達だが大幅改善) |
| memory-integrity-check.py | 0B | 0B | 0.05s | ok |
| harness-snapshot.py | 0B | 51B | 0.04s | ok |
| **合計 latency** | | | **0.92s** | OK (target 3s 内) |

### 改善量

| 指標 | Before | After | 削減率 |
|------|--------|-------|-------|
| env-bootstrap.py stdout | 559B | 266B | **-52%** |
| env-bootstrap.py latency | 2.57s | 0.54s | **-79%** (warm cache 影響含む) |
| 合計 latency | 3.20s | 0.92s | **-71%** |

注: latency は subprocess startup の cold/warm cache に大きく依存する。複数回測ると 0.58s〜1.5s で揺れる。並列化の効果は warm でも cold でも 6 倍速化が期待される。

## 実施した修正

### `env-bootstrap.py` (2 箇所)

1. **`_detect_runtimes()` の並列化** (`concurrent.futures.ThreadPoolExecutor`):
   - 6 言語の `--version` を直列 → 並列実行
   - 順序は `dict` insertion order + `futures: dict[name, future]` で固定
2. **`_short_version()` 追加** で runtime version を semver token のみに短縮:
   - `go version go1.25.1 darwin/amd64` → `go: 1.25.1`
   - `Python 3.14.3` → `python: 3.14.3`
3. **`_get_top_level_dirs()` 削除**:
   - `Top-level: ` 行は cwd の追加ファイルで drift しやすく、cache prefix 安定性を毀損
   - Project markers が cwd を十分に表現するため代替不要

### `sessionstart-audit.py` (新規)

settings.json の `hooks.SessionStart` を読み、各 hook を 1 回ずつ実行して以下を表で出力:

- stdout / stderr byte 数
- wall-clock latency
- volatile flag (絶対 timestamp / 相対 hour / subsecond duration を regex 検出)
- target 超過は `OVER200B` flag で警告、合計 latency も判定

`python3 ~/.claude/scripts/runtime/sessionstart-audit.py` で単独実行可。CI/cron 化は本 Plan scope 外。

## 残課題 (本 Plan の scope 外)

| ID | 項目 | 優先度 |
|----|------|-------|
| F1 | `env-bootstrap.py` stdout 282B → < 200B (Project markers / Package managers のさらなる短縮) | 中 |
| F2 | `checkpoint_recover.py` の VOLATILE-OUT 検出 (新たに 198B + volatile flag、原因調査) | **高 (cache 観点)** |
| F3 | `memory-integrity-check.py` の stdout が状況依存 (198B / 0B 切替) で監査結果がブレる | 中 |
| F4 | session-load.js の stderr 933B が user 体験として冗長 (cache 影響なし、UX のみ) | 低 |
| F5 | sessionstart-audit.py を CI / cron 化して定期実行 | 低 |

F2 (checkpoint_recover.py の VOLATILE-OUT) は本 Plan の audit script が新たに発見した問題。本 Plan の scope 外だが、cache prefix 観点で次タスクとして優先度高で扱うべき。

## 撤退条件

- env-bootstrap.py の並列化で `Runtimes:` の出力順が変化した場合 → `dict` insertion order が壊れている、要再検証
- `_short_version()` regex が major version のみの runtime (例: `java 14`) で出力を破壊した場合 → 元の split logic に戻す
- 並列化で latency が逆に悪化した場合 → ThreadPoolExecutor を WorkPool 1 (順次) に固定し効果検証

## 計測コマンド

```bash
python3 ~/.claude/scripts/runtime/sessionstart-audit.py
```

期待 exit code: 0 (全 hook が target 内) または 1 (target 超過あり)。本 Plan 適用後は env-bootstrap.py のみが OVER200B で 1。
