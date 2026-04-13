# Telemetry Coverage Audit — 2026-04-13

## 問題

30日の計測期間 (2026-03-08 〜 2026-04-13) において、以下の非対称失敗が観察される。
1398〜1413 セッション中、実際のエラー記録は極端に少なく、成功が過剰記録されている。

| ログ | 件数 | 問題 |
|------|------|------|
| `errors.jsonl` | 8 件 | 4 件は synthetic (2026-03-08/09)、real error 4 件のみ |
| `friction-events.jsonl` | 3 件 | 全て 2026-04-05 の synthetic fixture |
| `strategy-outcomes.jsonl` | 1235 件 | `clean_success: 1234`, `failure: 1` — 1413 セッション中エラー記録 8 件と両立しない |
| `session-metrics.jsonl` | 1413 件 | `errors_count_sum=8`, `friction_event_count_sum=3` |

---

## Producer マップ

### errors.jsonl

#### Rust Producer: `tools/claude-hooks/src/post_bash.rs`

- **発火条件**: PostToolUse(Bash) hook が発火 → `check_error_to_codex()` が以下 15 パターンのいずれかを output に検出した場合
  - `(?:Error|Exception):\s+\S`, `Traceback`, `panic:`, `FAIL\s+\S`, `npm ERR!`, `error\[E\d+\]`, `cannot find module`, `undefined reference`, `segmentation fault`, `fatal error`, `compilation failed`, `build failed`, `SyntaxError:`, `TypeError:`, `ReferenceError:`
- **除外条件**: `IGNORE_COMMANDS` リスト (`git status`, `ls`, `cat`, `echo`, `codex`, `gemini` 等) で始まるコマンドは skip。output 長 < 20 bytes は skip。`already exists` を含む output は skip
- **emit スキーマ** (current-session.jsonl へのネスト形式):
  ```json
  {"timestamp":"...", "category":"error", "importance":0.5, "confidence":0.8,
   "failure_mode":"FM-007", "failure_type":"generalization", "scored_by":"rule",
   "promotion_status":"pending", "data":{"message":"...", "command":"..."}}
  ```
- **wiring**: `settings.json` PostToolUse Bash → `claude-hooks post-bash` (Rust binary)。**現在 live**
- **dead path 判定**: **Live** (wired + binary 存在確認済み)
- **補足**: 重複排除あり。dedup key は `"error:::TIMESTAMP_SECS"` で、同一秒内の複数エラーは 1 件のみ記録される

#### Python Producer: `.config/claude/scripts/policy/error-to-codex.py`

- **発火条件**: Rust と同じ 15 パターンを Python re で検出
- **emit スキーマ** (current-session.jsonl へのフラット形式):
  ```json
  {"timestamp":"...", "category":"error", "message":"...", "command":"...",
   "importance":0.5, "confidence":0.5, "failure_mode":"", ...}
  ```
- **wiring**: **`settings.json` に配線されていない** — `PostToolUse` に `error-to-codex.py` の記述なし
- **dead path 判定**: **Dead** (配線なし = 本番で発火しない)
- **歴史的経緯**: 2026-03-08 commit `a7e31e5` で PostToolUse に wired。その後 Rust `post_bash` への統合に伴い Python hook は `settings.json` から削除されたが、**ファイル自体は残存**している
- **ファイルパス**: `dotfiles/.config/claude/scripts/policy/error-to-codex.py`

#### Flush Pipeline (session-learner)

- `session-learner.py` (`Stop` hook) が `flush_session()` を呼び `current-session.jsonl` を読み込み、`category=="error"` のイベントを `append_to_learnings("errors", ...)` で `errors.jsonl` に永続化する
- `_normalize_event()` で Rust のネスト形式 (`data` キー) をフラット化してから処理する
- **ファイルパス**: `dotfiles/.config/claude/scripts/learner/session-learner.py:593-596`

#### Synthetic 源の特定

- **entry 1〜4** (2026-03-08/09、`"Error: x"`, `"Error: t"`, `"test TypeError"`):
  - 2026-03-08 commit `a7e31e5` で Python `error-to-codex.py` が `settings.json` の PostToolUse に追加された直後のセッション
  - 当時の `session_events.emit_event` の schema は `{"timestamp":"...", "category":"error", **data}` (importance 等なし) — これが entry 1〜4 の schema (`timestamp, message, command` のみ) と一致する
  - `"Error: x"` 等の短いメッセージは、初期の `error-to-codex.py` が `ERROR_PATTERNS` の `(?:Error|Exception):\s+\S` で一文字コマンド出力を誤検知したもの (例: `echo "Error: x"` 相当)
  - **結論**: 初期の Python hook 配線直後のセッションで発生した real emit だが、コマンドが synthetic テスト的な短い出力 (`npm test` に対して `Error: x` 等)
- **entry 5** (2026-03-16、`"Error: P"`):
  - Rust emit 形式 (`data` nested) で記録されているが、`"Error: P"` は明らかに短い — `mkdir /root/test` の出力から検出
  - `(?:Error|Exception):\s+\S` が `Error: P` (Permission denied の先頭1文字切り取り) にマッチした可能性

---

### friction-events.jsonl

#### Producer: `.config/claude/scripts/policy/stagnation-detector.py`

- **発火条件**: PostToolUse(Bash) → `detect_friction()` が以下 2 パターンを検出した場合
  1. **validation_ping_pong**: 直近 8 コマンド中、`command_family=="validation"` かつ `exit_code_inferred=="error"` が 3 件以上 (`VALIDATION_PING_PONG_THRESHOLD=3`)
  2. **environment_blocker**: 直近 8 コマンド中、同一 `error_class` (permission_denied, file_not_found 等) が 2 件以上 (`ENVIRONMENT_BLOCKER_THRESHOLD=2`)
- **emit パス**:
  1. `detect_friction()` が dict を返す
  2. `emit_event("pattern", {"type": "friction_event", **friction})` を呼ぶ → `current-session.jsonl` に `category="pattern"` で記録
  3. `session-learner.py` が Stop 時に `_extract_friction_events()` でパターンから抽出 → `friction-events.jsonl` に永続化
- **wiring**: `settings.json` PostToolUse Bash → `stagnation-detector.py`。**現在 live**
- **dead path 判定**: **Partially Live** — hook 自体は live だが friction emit は発火しにくい設計

#### 本番で発火しない理由

1. **コマンドシーケンス要件が厳しい**: validation_ping_pong は「直近 8 コマンド中 validation 系が 3 回以上失敗」を要求する。Claude が validation → 修正 → validation を繰り返す場合でも、間に別コマンドが挟まると `recent = history[-8:]` で dilution される
2. **cooldown 共有**: stagnation と 30 秒 cooldown を共有 (`last_suggestion_time`)。stagnation が先に発火すると friction は検出されない
3. **category="pattern" として記録**: friction_event は `category="pattern"` として current-session.jsonl に書かれる。session-learner の `_extract_friction_events()` は `e.get("type") == "friction_event"` でフィルタするが、この判定が `_normalize_event()` 後のフラット形式で動作するかの検証が必要
4. **2026-04-05 の 3 件**: `AUTOEVOLVE_DATA_DIR` を使ったテスト実行またはスクリプト直接実行によって生成された synthetic fixture と推定される (全 3 件が同一 timestamp の小数秒違い)

---

### strategy-outcomes.jsonl

#### Producer: `.config/claude/scripts/learner/session-learner.py`

- **発火条件**: Stop hook → `session-learner.py` → `process_session()` → `total_events > 0` のセッションで全件書き込み
- **emit スキーマ**:
  ```json
  {"timestamp":"...", "project":"...", "task_type":"...", "approach":"...",
   "data_domain":"...", "context":{"error_count":N, ...},
   "outcome":"clean_success|recovery|failure", ...}
  ```
- **wiring**: `settings.json` Stop → `session-learner.py`。**現在 live**

#### `outcome` が `failure` になる条件 (session-learner.py:46-50)

```python
if errors and corrections:
    outcome = "recovery"
elif errors:
    outcome = "failure"
else:
    outcome = "clean_success"
```

- `errors` = `[e for e in events if e.get("category") == "error"]`
- `corrections` = `[e for e in events if e.get("category") == "correction"]`
- **`correction` category の producer が存在しない** — `grep -r 'correction' scripts/` で確認したところ、どのフックも `emit_event("correction", ...)` を呼んでいない (現行コードでは `correction` category のイベントが生成されない)
- よって `failure` になるには errors が 1 件以上必要だが、errors が 0 件のセッションが 1409/1413 件を占める → `clean_success` が 99.9% を占める

#### `failure` がほぼ出ない根本原因

- Rust post_bash の error detection は **output text パターンマッチ依存**であり、exit code 非ゼロだけでは emit しない
- 典型的なセッション (dotfiles 調査・設定変更等) では bash コマンドの出力に上記 15 パターンが現れないことが多い
- → `current-session.jsonl` に `category="error"` イベントが書かれない → `flush_session()` で errors リストが空 → `outcome = "clean_success"`

---

### session-metrics.jsonl (errors_count, friction_event_count)

#### Producer: `session-learner.py:781-799`

```python
metrics = {
    "errors_count": summary["errors_count"],  # len(errors)
    "friction_event_count": friction_count,   # _extract_friction_events() の戻り値
    ...
}
append_to_metrics(metrics)
```

- `errors_count`: `flush_session()` で読んだ events のうち `category=="error"` の件数 — **errors.jsonl の entries 数と同一源**
- `friction_event_count`: `_extract_friction_events()` で `category=="pattern"` かつ `type=="friction_event"` のイベント数 — **friction-events.jsonl の entries 数と同一源**

#### session-metrics vs errors.jsonl の不整合確認

```
session-metrics.jsonl: 1413 entries, errors_count_sum = 8
errors.jsonl: 8 entries
```

**一致している** — 両者は同一の session-learner flush pipeline から生成されるため件数は一致する。
「不整合」ではなく「両者が共に少ない」が正確な問題記述。

```
session-metrics.jsonl: friction_event_count_sum = 3
friction-events.jsonl: 3 entries
```

こちらも**一致**。同様に「両者が共に少ない」。

---

## 観察された不整合

| 比較 | 値 | 解釈 |
|------|---|------|
| errors.jsonl 8 件 vs 1413 セッション | 0.006% のセッションでエラー記録 | パターンマッチ非検出が主因 |
| strategy-outcomes failure 1 件 vs errors 8 件 | strategy-outcomes の方が少ない | 1 セッション分のエラー (3 件 2026-04-04) が strategy-outcomes 1 failure entry に対応 |
| session-metrics.errors_count_sum=8 vs errors.jsonl=8 | **一致** | 不整合なし。両者は同一 pipeline |
| session-metrics 1413 vs strategy-outcomes 1235 | 178 件の差 | **session-learner が `total_events==0` で早期 return するため** strategy-outcomes は書かれないが、metrics は全件書かれる — ただし `total_events==0` のセッションは現在 0 件。別の原因で差がある可能性: 旧形式 session-metrics が strategy-outcomes 以前から書かれていた (metrics の timestamp 範囲: 2026-03-08〜、strategy-outcomes: 2026-03-17〜) |
| doom_loop/spiral 545 件 (MEMORY.md) vs strategy-outcomes | INSUFFICIENT_EVIDENCE: doom_loop は `session-metrics.jsonl` の `type=="stagnation_detected"` イベントから来ている可能性。別 jsonl への記録か、MEMORY.md が古い情報を参照しているか未確認 |

---

## 非対称失敗の根本原因仮説

### 仮説 1: Error detection がテキストパターン依存であり exit code を無視している

**根拠**:
- `post_bash.rs:check_error_to_codex()` は output テキストに 15 パターンのいずれかが含まれる場合のみ emit する
- exit code 非ゼロ (`$?` != 0) の場合でも、エラーメッセージが上記パターンに合致しなければ記録されない
- 実際のセッションでは「コマンドが成功した」「ファイルが見つからなかった」等の一般的なエラーが日本語または非定型メッセージで出力される場合、全て見逃される
- **影響**: errors.jsonl の記録率が実際の失敗率より大幅に低い。`strategy-outcomes` の `failure` 分類にも連鎖

### 仮説 2: Python `error-to-codex.py` が settings.json から除去されたが dead code として残存し、混乱を招いている

**根拠**:
- `dotfiles/.config/claude/scripts/policy/error-to-codex.py` はファイルが存在するが `settings.json` に配線されていない
- 2026-03-08 の `a7e31e5` で wired → その後 Rust post_bash への統合時に unwired
- 将来の `/improve` やコードレビューで「このスクリプトも emit している」と誤認されるリスク

### 仮説 3: `strategy-outcomes.outcome` の `correction` category producer が存在せず、`recovery` 分類が機能していない

**根拠**:
- `session-learner.py:46` の `outcome = "recovery"` 分岐は `corrections and errors` が両方必要
- しかし `correction` category を `emit_event()` するコードは現行スクリプト群に存在しない (grep 確認済み)
- よって `recovery` は実質 dead path。`failure` になる条件は errors のみ存在するケースだが、仮説 1 によりこれも発火しにくい
- **影響**: strategy-outcomes は `clean_success` か `failure` の 2 値になり、グラデーション (recovery) が消える。品質違反や doom_loop 検出とのコリレーションが意味をなさなくなる

---

## 推奨次アクション (Top 3)

### 1. Exit code ベースのエラー記録を追加する

- `post_bash.rs` または `session-learner.py` で bash の exit code 非ゼロを error event として記録する仕組みを追加する
- 実装候補: `post_bash.rs` の `run()` 関数に `data["tool_response"]["exit_code"]` を読む処理を追加し、exit_code != 0 かつ テキストパターン不一致の場合は `emit_event("error", {"exit_code": N, ...})` を呼ぶ
- **確認が必要な点**: hook の `data` 構造に exit code が含まれているか (Claude Code の hook API 仕様確認)

### 2. `correction` category の producer を実装または既存の `quality` イベントで代替する

- `session-learner.py:46` の `recovery` 分岐を動作させるには、correction イベントの producer が必要
- 最も簡単な実装: `post_bash.rs` の `check_review_feedback()` や、成功した修正コマンドの後に `emit_event("correction", ...)` を追加する
- または `outcome` 分類ロジックを見直し、`quality_issues > 0 and errors_count == 0` を `partial_success` 等に分類する

### 3. `error-to-codex.py` の dead code を削除または明示的に deprecated とマークする

- `dotfiles/.config/claude/scripts/policy/error-to-codex.py` はファイル先頭に `# DEAD: Replaced by Rust post_bash check_error_to_codex()` のコメントを追加するか削除する
- `/improve` や将来の調査で混乱を防ぐため、状態を明示する

---

## Appendix: 現状の数値

| ファイル | 件数 | 期間 |
|---------|------|------|
| `errors.jsonl` | 8 entries | 2026-03-08 〜 2026-04-04 |
| `friction-events.jsonl` | 3 entries | 2026-04-05 のみ |
| `strategy-outcomes.jsonl` | 1235 entries | 2026-03-17 〜 2026-04-13 |
| `session-metrics.jsonl` | 1413 entries | 2026-03-08 〜 2026-04-13 |

**errors.jsonl 内訳**:
- entry 1〜4: 2026-03-08/09、schema `{timestamp, message, command}`、Python error-to-codex.py 初期 wiring 時代の記録 (synthetic 相当)
- entry 5: 2026-03-16、Rust emit 形式 (nested `data`)、`mkdir /root/test` の permission error
- entry 6〜8: 2026-04-04、同一セッション、`npm test` で `Cannot find module ./utils` (real error)

**session-metrics.jsonl outcomes**:
- `clean_success`: 1391
- `failure`: 2
- `N/A` (outcome フィールドなし、旧形式): 20

**strategy-outcomes.jsonl outcomes**:
- `clean_success`: 1234
- `failure`: 1 (2026-04-04 の npm module error セッション)

**errors.jsonl 合計 vs session-metrics.errors_count_sum**: 8 = 8 (一致、不整合なし)

---

*調査日: 2026-04-13*
*調査者: Sonnet 4.6 (subagent)*
*調査範囲: dotfiles/.config/claude/scripts/, tools/claude-hooks/src/, ~/.claude/agent-memory/*
