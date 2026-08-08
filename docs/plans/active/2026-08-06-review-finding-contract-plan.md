---
date: 2026-08-06
status: active
source: docs/research/2026-08-06-monotaro-makasetaro-review-harness-absorb-analysis.md
scale: L
---

# レビュー finding の出力契約を型付けし、完走判定と投稿前照合を入れる

## Goal

`/review` の findings が「どの語彙で severity を出すか」「confidence が無いとき何が起きるか」「レビュアーが途中で切れたかどうか」を誰も決めていない状態を終わらせる。実測で `review-findings.jsonl` 157 件のうち severity 欠落 121 件 (77%)、残り 36 件が 15 値に散っている。この台帳の上で verdict (Critical 1 件以上 → BLOCK / Important 3 件以上 → NEEDS_FIX) を計算しているので、現状の verdict は語彙のその場対応付けに依存している。

由来は MonotaRO Makasetaro の absorb (T1〜T5)。記事の中核 =「投稿の最終決定をハーネスのコードが行う」は、findings のスキーマが厳密であって初めて成立するという逆読みから、dotfiles 側の穴が出た。

## Success Criteria

- `emit_review_finding()` に canonical 外 severity / severity 欠落 / location 欠落を渡すと **例外で拒否**され、`review-findings.jsonl` に書かれない (pytest で確認)
- `review-consensus-policy.md` に severity 語彙 → canonical tier のマッピング表があり、14 review agent の既存語彙 (`MUST/CONSIDER/NIT/ASK/FYI`, `CRITICAL〜LOW`, `必須/重要/推奨/参考`, 🔴/🟡/🔵, `Watch`, `PLAN`) すべてに行が存在する
- confidence が無い finding を verdict 計算がどう扱うかが policy に明記され、`confidence_kind` (subjective / evidence-sufficiency) が区別されている
- 合意数による confidence 加算 (`max + 5×(n-1)`) が「優先順位の補助」に降格し、confidence 値そのものを膨らませない
- dispatch したレビュアーのうち終端マーカーを返さなかったものがあると verdict が PASS にならず `INCOMPLETE` / `NEEDS_HUMAN_REVIEW` に倒れる
- `pr-autofix-routine` Phase1 の 2 周目以降の review プロンプトに、前ラウンドの finding_id / 対象 SHA / status / 人間の決定理由の ledger が渡る (原文コメントは渡さない)
- `git` の一括 add 判定が、禁止コマンド文字列を**引用しただけの**別コマンド (heredoc 内の説明文など) を block しない。かつ block 時に WHY / FIX を返す
- `cargo test` / `task validate-configs` / `task validate-symlinks` が green

## Scope

触る:

```text
.config/claude/scripts/lib/session_events.py                      # ~ emit_review_finding に検証、emit_review_metrics に終端状態
.config/claude/skills/review/references/review-consensus-policy.md # ~ マッピング表 / 欠落時の扱い / boost 降格
.config/claude/skills/review/references/findings-and-feedback.md   # ~ canonical enum と終端マーカーの書き方
.config/claude/skills/review/SKILL.md                              # ~ Step 4 に INCOMPLETE 判定、Step 6 に契約参照
.config/claude/skills/pr-autofix-routine/SKILL.md                   # ~ 2.2 に前ラウンド ledger 注入、2.6 に ledger 更新
.config/claude/scripts/runtime/agent-invocation-logger.py           # ~ tool_response のキー観測 (discovery のみ)
tools/claude-hooks/src/pre_tool.rs                                  # ~ 一括 add 判定の false positive と deny 文面
.config/claude/scripts/tests/test_session_events.py                 # ~ 契約テストを追記 (新規ファイルは作らない)
```

触らない:

- 14 個の review agent 定義 (`.config/claude/agents/*.md`) — 語彙はマッピング表で吸収する。14 ファイルを書き換えるのは変更面が広く、agent 側の表現を壊す
- 既存 `review-findings.jsonl` 157 行 — 遡及移行しない (履歴として現状維持)
- `ReportFindings` tool の導入 (M4) — findings 喪失が実際に観測されるまで見送り

## Constraints

- `security-reviewer` の証拠充足型 confidence (`security-reviewer.md:188`) を主観スコアに戻してはいけない。2026-07-31 の codex-security absorb の決定 (confidence 1-10 廃止 → 証拠充足) を覆さず、`confidence_kind` で共存させる
- 前ラウンドの PR コメント原文を review プロンプトに入れてはいけない。`REVIEW_TASK.md.tpl:153` が PR 本文・コメントを untrusted と明示している。渡すのは自分が生成した ledger だけ
- `append_to_learnings` の他の呼び出し元 (patterns / quality / telemetry 等) の挙動を変えない。検証は `emit_review_finding` 側に置く
- hook は fail-open のまま (`agent-invocation-logger.py:115` の best-effort) — 観測追加でレビューを止めない
- `pre_tool.rs` の一括 add 禁止そのものを弱めない。誤発火だけを削る

## Unknowns

- **Agent tool の `tool_response` が停止理由を含むか未確認**。`agent-invocations.jsonl` は 1724 行すべて `exit_status: completed` で、実装は `"completed" if tool_response else "unknown"` (`agent-invocation-logger.py:111`) なので truncation を区別できない。よって完走判定は harness 内部に依存させず、レビュアー出力の終端マーカー欠落で判定する。`tool_response` のキー観測は「あるかどうかを知る」ための discovery であって、これに依存した設計にはしない
- canonical tier を 3 値 (Critical / Important / Watch) にするか、`RETRACTED` / `PLAN` のような非 severity 値を別軸 (status) に追い出すかは実装時に決める。実データに `RETRACTED` 1 件・`PLAN` 1 件がある
- 終端マーカーを 14 agent すべてに要求すると、`golang-reviewer` / `typescript-reviewer` は出力フォーマット節を持たないので追記が必要になる。「触らない」に置いた 14 ファイル不干渉と衝突する可能性がある。衝突したら agent 側ではなく dispatch プロンプト (`review/SKILL.md` Step 3 の注入文) に終端マーカー要求を置いて回避する

## Program Design

```text
review/SKILL.md Step 3 dispatch
    Agent(code-reviewer, ...) → markdown report
+     終端マーカー要求を注入文に含める
review/SKILL.md Step 4 synthesis
~   verdict 計算
+     roster 照合: dispatch した reviewer 名 vs 終端マーカーを返した reviewer 名
+     差があれば verdict = INCOMPLETE (PASS に落とさない)
review/SKILL.md Step 6 保存
    emit_review_finding(finding)
+     canonical severity / location / confidence_kind を検証 → 違反は raise
    emit_review_metrics(metrics)
+     reviewers[].terminal_status = complete | missing_marker | error
```

順序と各単位の検証:

1. 契約の定義 (policy markdown) → 表に 15 語彙すべての行があることを目視
2. 検証コード (`session_events.py`) → pytest で拒否を確認
3. dispatch / synthesis 側の接続 (`review/SKILL.md`) → 実際に `/review` を 1 回走らせ、`review-metrics.jsonl` に terminal_status が入るか確認
4. ledger (`pr-autofix-routine`) → dry run で 2 周目プロンプトに ledger が入るか確認
5. hook 修正 (`pre_tool.rs`) → `cargo test` + 実際に禁止文字列を引用した別コマンドが通ることを確認

## Validation

- `cd tools/claude-hooks && cargo test`
- `python3 -m pytest .config/claude/scripts/tests/test_session_events.py -q`
- `task validate-configs` / `task validate-symlinks`
- 実走行: `/review` を 1 回、`pr-autofix-routine` を dry run で 1 回
- Codex Review Gate (`codex exec --sandbox read-only`) — harness 変更なので必須

## Steps

1. canonical severity / confidence_kind / 終端マーカーを policy に定義 (T1 前半)
2. `emit_review_finding` に fail-fast 検証 + テスト (T1 後半)
3. 合意ブーストの降格と confidence 欠落時の扱いを policy に反映 (T1)
4. roster 照合と INCOMPLETE 判定を Step 4 に追加、`emit_review_metrics` に terminal_status (T2)
5. `pr-autofix-routine` に finding ledger の引き継ぎ (T3)
6. `pre_tool.rs` の false positive と deny 文面 (T4)
7. 投稿・自動修正の直前に file/line/snippet 照合 (T5)
8. `tool_response` キー観測の 1 行追加 (discovery)
9. 検証一式 + Codex Review Gate

## Progress

- [x] Step 1 policy 定義 — `review-consensus-policy.md` Section 0 新設（canonical severity 表 / confidence_kind / 欠落時の扱い / 終端マーカー）
- [x] Step 2 fail-fast 検証 + テスト — `validate_review_finding()` 追加、`test_session_events.py` に契約テスト 14 件（81 passed）
- [x] Step 3 boost 降格 / 欠落時の扱い — Section 2 を「合意は優先順位補助のみ」に書き換え、SKILL.md 統合ルール 2 / 4 / 7 を追随
- [x] Step 4 roster 照合 + terminal_status — SKILL.md Layer 0 に Roster 照合、`emit_review_metrics` が `reviewers[].terminal_status` を検証
- [x] Step 5 ledger 引き継ぎ — marker JSON に `findings`、2.2 に既出指摘の注入、2.6 に ledger 更新
- [x] Step 6 hook false positive — **当初の目的 (誤検知解消) は達成せず、方針を fail-closed に転換**。Codex が 5 ラウンドで回避経路を出し続けたため「引用文か実行か」の判別を破棄。引用文も block する代わりに bypass を塞ぐ形にした。副産物で `io.rs` の deny 経路 panic (UTF-8 バイト境界 slice) を修正
- [x] Step 7 投稿前照合 — pr-autofix 2.6 に stale finding チェック（`/review` の表示経路には入れない: Codex 判断）
- [x] Step 8 tool_response 観測 — `response_keys` を記録（判定には使わない）
- [ ] Step 9 検証 + Review Gate — `pytest` 81 passed / `task validate-configs` exit 0 / `task validate-symlinks` exit 0。`cargo test` と Codex Gate 未取得

## Surprises & Discoveries

- `emit_review_finding` / `emit_review_metrics` は既に存在し (`session_events.py:378` / `:387`)、後者の docstring は `reviewers: [{name, duration_s, findings, confidence: {min,max,mean}}]` という名簿つきスキーマを持っていた。M7 で必要なのは名簿の新設ではなく終端状態の追加だった
- `append_to_learnings` (`:360-364`) はスキーマ検証をせず `session_id` / `tier` / `score` を setdefault して書くだけ。severity 77% 欠落が無言で通り続けた原因
- `agent-invocations.jsonl` の `exit_status` は 1724/1724 が `completed`。実装が `"completed" if tool_response else "unknown"` なので、切れた応答も completed になる silent success フィールド
- `pre_tool.rs` の一括 add 判定は生のコマンド文字列への部分一致で、この absorb 中に Codex へ渡すプロンプト内で禁止文字列を**引用しただけ**の Bash が block された。WHY / FIX が返らないため何にマッチしたか分からなかった

## Decision Log

- **T1 は fail fast (ユーザー判断)**: 正規化して書くのではなく拒否する。`CLAUDE.md` の「境界では Fail Fast」「Static-checkable rules は mechanism に寄せる」に沿う。既存 157 行は移行しない
- **14 agent の語彙は統一せずマッピング表で吸収**: 変更面を 14 ファイルに広げない。agent 側の表現 (絵文字・日本語 4 区分) はそれぞれの読み手に合わせて選ばれている
- **confidence は統一しない (Codex 指摘)**: 証拠充足型と主観型を同じ閾値・加算式に通すのが誤りなので、`confidence_kind` で区別する
- **合意ブーストは降格 (Codex 指摘)**: 同じ diff と同じ rubric を読むレビュアーを独立試行として扱うと相関した誤検知を増幅する。合意は優先順位の補助に留める
- **M5 は原文でなく ledger (Codex 指摘)**: PR コメント原文は untrusted。finding_id / SHA / status / 人間の決定理由だけを渡す
- **M4 (ReportFindings) は見送り**: inline 投稿しない現行 `/review` では tool の存在自体が価値を生まない。findings 喪失が観測されてから
- **却下 (組織固有)**: コメント数上限、リアクション比、全 PR 横断コスト分布ダッシュボード、Actioned 指標。個人 harness では運用コストが上回る。observe ログと Knowledge Intake trends が消費者ゼロで撤去された前例に一致
- **M9 (プロンプト内反復) は現状維持**: 引用論文 arXiv:2512.14982 は非 reasoning モデルの結果で、reasoning 前提のレビュアー群に一般化する根拠にならない (Codex 指摘)

## Outcome

T1 / T2 / T3 / T5 は完了。T4 は方針を変えて着地させたが、当初の目的（誤検知の解消）は達成していない。

### 検証結果

| 対象 | 結果 |
|------|------|
| `pytest .config/claude/scripts/tests/test_session_events.py` | 97 passed（契約テスト 25 件追加） |
| `cargo test` (tools/claude-hooks) | 57 passed（bulk-add 回帰テスト 12 件追加） |
| `task validate-configs` / `task validate-symlinks` | どちらも exit 0 |
| release バイナリ直接プローブ | 33 ケース FAILS 0 |
| `qa-tuning-analyzer` の list reviewer / severity 欠落 | 実データ形状で確認済 |

### レビューの状態（PASS は取得していない）

- Codex Review Gate は 5 ラウンド実施し、**最新の受領 verdict は BLOCK**。指摘は毎回実在するもので、都度修正した
- 最終ラウンドの残存 3 件のうち、`git add -n .` の過剰 block は修正済。残る 2 件は (a) 難読化 (`g\it add -A`) = 依頼時に除外した範囲で変更前も通っていた (b) 引用符内 `;` を含む引数でキャプチャが切れる = クォート解釈が必要で、その方向は 3 度試して 3 度とも別の穴を空けた
- `/review` のレビュアー subagent 3 体のうち `code-reviewer` だけが遅れて完全な結果を返した（`Coverage: complete`、verdict BLOCK）。`security-reviewer` と `edge-case-hunter` は idle 通知のみで本文なし = `missing_marker`。**本プランで導入した Roster 照合ルールに照らすと、このレビューは INCOMPLETE**
- `code-reviewer` の MUST（`sudo` / `env` / `time` / `nohup` / `command` / `find -exec` で一括 add が素通りする regression）は round-1/2 時点のコードに対する指摘で、fail-closed 転換で該当関数ごと削除済み。6 経路すべてと、同レビューが「未検出」とした `git add "."` も現在は block することを実バイナリで確認し、指摘されたテスト空白（コマンド修飾子 / `find -exec`）を埋めた
- `code-reviewer` の残る有効な指摘: 終端マーカーの注入を機械的に強制する仕組みがない（dispatch プロンプトからこの一文が落ちると security-reviewer 以外の全レビューが強制的に `NEEDS_HUMAN_REVIEW` に倒れる）。Codex round-2 の Important と同じ論点で、metrics 境界の検証までは実装したが注入側の強制は未着手
- `pr-autofix-routine` の dry run 未実施

### 未解決 — ユーザー判断が要る

Codex の構造的指摘: コマンド文字列に対する正規表現は意味論的な網羅ではない。raw Bash の `git add` を禁止し、明示的なファイル配列だけを受けるラッパー（argv 境界で検証）に寄せるのが構造的な解。日常のワークフローが変わるため着手していない。

### 作業ツリーの状態

別セッションが同じ作業ツリーで作業しており、本作業の一部（12 ファイル）が PR #224「claude-plugins-sync に update モードを足す」に巻き込まれて master に squash merge された（`924a9265`）。その時点の `pre_tool.rs` は deny 経路が panic する状態で、修正は未コミットの作業ツリー側にある。
