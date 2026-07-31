---
date: 2026-07-31
status: implemented
source_type: video-talk
family: claude-code-tips / harness-engineering
saturation_gate: PASS (warning) — N>=3, delta=10/11
phase_2_5: Codex only (Gemini sunset, IneligibleTierError)
---

# Boris Cherny @ YC Startup School 2026 — "We Cut 80% of Claude Code's Prompt"

## Source

- 動画: <https://youtu.be/qyPCVqFUyDo> (Y Combinator, 2026-07-27, 約 25 分)
- 紹介ポスト: <https://x.com/oikon48/status/2083106854398267455>
- 話者: Boris Cherny (Claude Code 作者, Anthropic)
- 取得経路: `yt-dlp --write-auto-sub` で字幕 VTT を取得 → プレーンテキスト化 (36,592 字)。
  x.com は WebFetch が HTTP 402 を返すため r.jina.ai 経由

## 主張

モデル世代ごとに harness を捨てて作り直せ。Opus 5 は過去モデル向けの矯正指示を必要としない。
人間の仕事は「少し難しすぎるタスク + 検証手段 + 撤退条件」を渡して手を引くこと。

## 根拠 (原文より)

- Bun (JavaScript ランタイム、10万行超) を Zig → Rust に **11 日**で全面書き換え。dynamic workflow 1 本 + steering。本番投入済で、現在の Claude Code が動いている基盤
- Claude Desktop の Electron → Swift 移植が **15 日連続稼働中**。プロンプトは「Electron 版を VM で動かしてスクリーンショットを撮り、Swift 版とピクセル単位で比較しろ。終わるまで止まるな」の 4 文。Claude は自発的に Slack チャンネルを作って進捗を live blog した
- OpenCV を渡すと Opus 5 は絵を描く。描画は訓練していない (elicitation gap の実例)
- 「evals は harness より少し長生きするが、1〜3 世代でサチる」

## 前提条件

Anthropic 内部の大規模コードベース + 網羅的なテストスイート (Bun/Node の既存テストが正解判定を担った)。
製品層の system prompt は特定モデル・toolset・eval 分布を統制した最適化であり、
個人の global harness とは load path も寿命も違う。

## Phase 1.5: Saturation Gate — PASS (warning)

family `claude-code-tips` / `harness-engineering` は N>=3 だが、採用率 >= 20% のため PASS。

per-method 照合台帳 (全 11 手法):

| # | 手法 | verdict | matched_prior |
|---|------|---------|---------------|
| M1 | 世代交代トリガーの全削除→line-by-line 復元 ablation | novel | — |
| M2 | `CLAUDE_CODE_SIMPLE=1` / `--system-prompt` での ablation | novel | — |
| M3 | eval は 1-3 世代でサチる | novel | — (`2026-07-04-coding-benchmarks-misaligned` は eval **設計**の欠陥論で時間軸の主張なし) |
| M4 | task + guardrails + exit criteria のみ渡す | ambiguous | `2026-07-27-anthropic-skills-lessons-absorb-analysis.md` 手法6「Railroading 回避」/ 過剰指定回避の核は同等。ただし「難易度を意図的に上げる」は未検討 |
| M5 | verification path が長時間自走の単一最重要条件 | ambiguous | `2026-06-20-loop-engineering-essay-absorb-analysis.md` "Six parts (trigger/isolation/context/tool-reach/verifier/state)" / verifier 自体は同等。「最重要」の格付けは未検討 |
| M6 | product overhang / unhobbling | novel | (近縁の Knowledge Overhang は「モデル内部の潜在知識」で対象が違う → rehash にしない) |
| M7 | dynamic workflows = agent algebra | **rehash** | `2026-06-03-dynamic-workflows-absorb-analysis.md` / 参照元記事が完全一致 (同一記事・同一日付) |
| M8 | loops/routines で日次自己保守 (abstraction police) | ambiguous | `references/managed-agents-scheduling.md` Daily Health Check + `docs/playbooks/codex-janitor-workflow.md` / ループ機構は同等。タスクセットは未検討 |
| M9 | injection 3層防御で harness 防御前提が変わる | novel | (`2026-03-25-3-layer-prompt-injection-defense` は harness 側で 3 層を組む話で因果が逆) |
| M10 | モデルを生き物扱いする経験主義 | novel | — |
| M11 | 残る苦手 = deep systems / distributed / pixel UI | novel | — |

delta = 10 (novel 8 + ambiguous 3 のうち M4/M5/M8 を計上、M7 のみ rehash)。

## Phase 2 + 2.5: 判定 (Codex 批評で修正済み)

| # | 初期判定 | 最終判定 | 根拠 |
|---|---------|---------|------|
| M1 | Partial | **運用 Gap (最優先)** | 既存機構は方向が逆。現行 = 「死んでいる証明後に削除」、記事 = 「必要な証明ができたものだけ残す」 |
| M2 | Gap | **恒久 N/A、実験対照として Partial** | `SIMPLE=1` は tool prompt も落とすため独立変数が汚れ、CLAUDE.md 不要の証拠にならない |
| M3 | Already | **Already (閉ループではない)** | `scripts/eval/eval-staleness.py` が saturated 判定を実装済。ただし退役・再生成へ繋がっていない |
| M4 | Partial | **Partial** | 撤退条件は `reversible-decisions.md`、railroading 回避は `skill-writing-guide.md:63-113`。委譲時の規律としては未 codify |
| M5 | Already (強化可能) | **Partial + 実バグ** | 下記参照 |
| M6 | Gap | **判定誤り。無測定で実施中** | 下記参照 |
| M7 | Already | Already (rehash) | Workflow tool 本体は deliberate non-adopt のまま |
| M8 | Partial | **未成立** | 下記参照 |
| M9 | Gap | **Reject** | 「injection 不能」は評価集合内の結果。被害半径を抑える層としての価値は変わらない |
| M10 | Gap | **Partial** | skill 単位 A/B (`skill-audit` 3-arm) はある。global harness を対象にした比較実験の規律が欠ける |
| M11 | N/A | N/A | dotfiles の作業領域外 |

### Codex が見つけた実バグ 3 件 (すべて実ファイルで確認済み)

**1. `completion-gate.py` — Ralph Loop の上限が到達不能**

`retries >= MAX_RETRIES` (=2) の safety valve が Ralph Loop 分岐より先に return する一方、
Ralph 側は同じ counter を `_set_retry_count(retries + 1)` で進めていた。
`MAX_RALPH_ITERATIONS=10` は dead config で、実効上限は 2 iteration。
15 日連続自走のための verification path として機能していなかった。

**2. `daily-health-check.sh` — 失敗が観測できない**

`claude -p "/check-health"` が非ゼロで終了しても `WARN` をログに書くだけで exit 0。
launchd から見て常に成功。memory の「daily-health-check は一度も成功していない」が
検出されないまま放置される構造だった。

**3. `tools/system-prompt-patcher/` — unhobbling を無測定で標準経路に入れている**

`patches/2.1.x/` に 5 パッチ。うち 4 つは `.replace.txt` が空 = Claude Code 公式 system prompt の削除
(code references / professional objectivity / planning without timelines / bash directory verification)。
`Taskfile.yml:70` で `task setup` の標準経路に入る。
M6 を「Gap (概念が存在しない)」と判定したのは誤りで、正しくは「評価なしで既に実施中」。

### Codex の中核反論 — 先行 absorb の過剰一般化

`2026-07-25-anthropic-context-engineering-claude5-absorb-analysis.md` は同じ「80% 削除」主張に対して
採用 0 で終了し、理由を「製品層 system prompt と個人 global CLAUDE.md は load path も寿命も違うので
削減率を移植してはいけない」とした。**この反論自体は正しい。**

しかしそこから ablation **手順**まで棄却したのは過剰一般化。
新世代モデルで各指示の限界寄与を知る方法は、制御された無効化比較しかない。

正しい翻訳:

- 削減率 (80%) は移植しない
- hard safety / permission / 不可逆操作の制約は ablate しない
- 物理削除しない。override で可逆に無効化する
- 新モデル・固定 task set・固定評価軸で baseline と比較する
- 必要と **2 回再現した**一文・一機構だけ戻す

既存 30 日ルールには「低頻度だが重大な safety hook を短期観測で消さない」正当性がある。
一方で **旧モデルでの 30 日利用実績を、新モデルで prompt scaffolding がまだ必要な証拠にするのは誤り**。
この 2 種を同じ削除規則で扱っていることが keep bias の根。

解は削除を default に反転することではなく、
**振る舞い prompt だけ default=unproven、機械的安全制約は default=keep に分離すること**。

## Phase 3-4: 採用 (6 件すべて実装済み)

| # | 内容 | ファイル | 規模 |
|---|------|---------|------|
| T1 | Ralph Loop 上限の到達不能を修正 + 回帰テスト 10 件 | `.config/claude/scripts/policy/completion-gate.py`, `.config/claude/scripts/tests/test_completion_gate_ralph_ceiling.py` | S |
| T2 | health check の失敗を exit code / status file / 通知に出す | `scripts/runtime/daily-health-check.sh` | S |
| T3 | 参照切れ 2 件を修正 (`dead-weight-scan.py` → 実配線の skill-tracker + 手動照合、AutoEvolve → 退役明記) | `references/harness-stability.md`, `references/managed-agents-scheduling.md` | S |
| T4 | モデル世代交代時の ablation 節を追加 (default 極性の反転・safety 分離・セル分割・測定軸・撤退条件) | `references/dead-weight-scan-protocol.md` | M |
| T5 | patcher が無測定であることを明記し ablation セルに接続 | `tools/system-prompt-patcher/README.md` | S |
| T6 | 委譲は task + guardrails + exit criteria で渡す規律を追加 | `templates/claude-md/rules.md` → `CLAUDE.md` | S |

T4 は新規 reference を作らず既存 `dead-weight-scan-protocol.md` を書き換えた
(CLAUDE.md core principle「指示の重複を作らない」— 同ファイルが既にトリガーに「モデルアップグレード後」を持っていたため)。

T5 は独立した測定機構を作らず、既存の `task restore-claude` / `task patch-claude` を反転レバーとして
T4 のセル 4 に接続した (ponytail: 機構は既にあり、欠けていたのは接続と可視化)。

## 不採用

- **M9 (injection 防御の前提反転)**: Codex 指摘により Reject。`prompt-injection-detector.py` は
  「モデル側防御が落ちても被害半径を抑える層」として維持する
- **M2 の恒久運用化**: `CLAUDE_CODE_SIMPLE=1` は隔離環境での極端な対照専用。通常運用の候補にしない
- **M8 の abstraction police 日次 routine**: T2 で health check の成功・失敗判定が直るまで新 routine を増やさない
  (Codex: 「入力データ・決定的 verifier・失敗通知・担当者がそろわない routine は、保守を自動化せずログを増やす」)
- **80% という削減率そのもの**: 先行 absorb の判断を維持

## Codex Review Gate — 3 巡 (BLOCK → BLOCK → BLOCK)

Codex は 3 回とも BLOCK を返した。指摘はすべて実ファイルで裏を取ってから修正している。
**2 巡目以降の指摘の過半は、記事由来の変更ではなく 1 巡目の修正自体が生んだ欠陥だった。**

### 1 巡目 — 4 件

1. **graduated mode の handback 消失** — Ralph 上限到達時に mode を問わず `decision: allow` だけ返していた。
   未完了 plan を残して止まる経路こそ handback が要る (`graduated-completion.md:103`)。
   `systemMessage` を併せて返すよう修正 + 回帰テスト追加
2. **`_find_incomplete_plan()` の例外が safety valve を fail-open にする** — valve より前に無条件で呼ぶよう
   変えたため、plan ディレクトリの `PermissionError` 等で gate 全体が落ちる。`OSError`/`UnicodeError` を
   捕捉して `incomplete=None` に倒し従来経路へ戻す + 回帰テスト追加
3. **`task install` は patcher を実行しない** — 実行するのは `task setup` (`Taskfile.yml:61`)。
   さらに **`task restore-claude` は動いていなかった**: `verify-patch.js` に `process.argv` の解析が無く
   `--restore` は黙って無視され、検証失敗時しか復元しない実質 NO-OP だった。
   argv 解析と `restoreOnly()` を実装し、README・protocol・index・log の `task install` 表記を訂正
4. **計測器の指定が未配線** — 初版で名指しした `learner/staleness-detector.py` と
   `learner/skill-usage-tracker.py` はどちらもどこにも配線されていない休眠スクリプト。
   実際に登録されているのは `policy/skill-tracker.py` (settings.json の `Skill` matcher)。
   **古い drift を直すつもりで新しい drift を作りかけた** — memory `feedback_dormant_artifact_edits.md` の再発。
   実配線を名指しし、hook/agent/reference には自動計測器が無いことを明記した

3 の `--restore` 未実装は、この repo 自身の core principle「暗黙フォールバック・モック・NO-OP 絶対禁止」違反。
T5 の「反転レバーは既にある」という前提が成立していなかったため、実装して初めて T5 が成立した。

### 2 巡目 — さらに 4 件

うち 2 件は修正自体が生んだ新しい欠陥。

5. **Stop hook の契約違反** — Ralph 上限で `{"decision": "allow", "reason": ...}` を返していた
   (元コードから引き継いだ形)。公式仕様では Stop hook の top-level `decision` に取りうる値は
   `"block"` のみで、停止を許可するときは `decision` を省略する。`"allow"` は PreToolUse の
   `permissionDecision` 系の値で、Stop には存在しない。
   **元は到達不能な分岐だったため無害だったが、T1 で到達可能にした瞬間に生きたバグになった。**
   `decision`/`reason` を落とし、graduated 時は `systemMessage` のみ返すよう修正
   (出典: <https://code.claude.com/docs/en/hooks>、claude-code-guide で裏取り)
6. **`MAX_RALPH_ITERATIONS=10` は直した後もランタイムに届かない** — Claude Code は Stop hook が
   8 回連続で block すると hook を上書きして停止する (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` で変更可)。
   上限 10 は依然として dead config。**default を 7 に下げ**、8 未満であることを test で固定した
7. **`restoreOnly()` の false-success** — `findBundlePath()` が「npm root -g 失敗」「package なし」
   「package はあるが bundle なし」の 3 つを等しく `null` に畳んでいたため、実際には復元できて
   いないのに exit 0 で成功に見えた (T2 で直したのと同じ silent failure)。
   `lookupBundle()` に理由を返させ、native installer (package-absent) だけ skip 0、他は exit 1 に分離
8. **「どこにも配線されていない」が言い過ぎ** — `staleness-detector.py` は `memory-eviction.py` から
   import され `/improve` 実行時 advisory の consumer を持つ (`improve-policy.md:489`)。
   hook 未登録なのは事実だが「未配線」ではない。**drift を直す過程で 2 回目の不正確な記述を出した。**
   consumer の有無と hook 登録の有無を書き分けた

### 3 巡目 — さらに 5 件

またしても過半が自分の修正由来。

9. **カウンタ共有の逆流** — Ralph で 3 回 block したあと plan が完了すると、共有 `retries` が
   `MAX_RETRIES=2` を超えたまま残る。次の Stop で safety valve が先に発火し、
   **テストゲートと harness review gate を丸ごと迂回する**。T1 の当初の修正 (上限を切り替えるだけ) では
   この向きの漏れが残っていた。`ralph-iterations` を独立ファイルに分離し、
   plan 完了時に reset するよう作り直した + 回帰テスト 2 件追加
10. **`restoreOnly()` が復元対象を検証していない** — PATH の `claude --version` を見ていたため、
    native installer と npm 版が共存する環境では復元した bundle を検証せず成功と出る。
    `node <bundlePath> --version` に変更
11. **Ralph 上限の説明が 3 箇所で実装と食い違う** — `agent-harness-contract.md` /
    `quality-gates.md` / `review-loop-patterns.md` はいずれも Ralph も `MAX_RETRIES=2` / 1 回きり
    と書いていた。**私の変更で初めて誤りになった記述**なので 3 箇所とも更新
12. 回帰テスト件数の記述が 4 件と 8 件で矛盾 → 実測 10 ケースに統一
13. 節見出しが「BLOCK → 4 件修正して PASS」と、再レビュー前に PASS を宣言していた → 実際の 3 巡に書き換え

### 4 巡目 — 未完了

3 巡目の修正後に投げた再レビューは 10 分間 no-progress で終了し、判定を得ていない。
skill の規定 (Codex 失敗時は理由を明記して進む) に従い**未取得のまま commit している**。
代わりに手動でカウンタ相互作用を追跡し、Ralph 分岐 (`completion-gate.py:1370-1415`) が
ralph カウンタしか触らず、retry カウンタの全変更点 (1419/1463/1491/1525) が Ralph の return より
後ろ = `incomplete` が偽のときしか到達しないことを確認した。**4 巡目の独立レビューは残タスク。**

## 検証

- `pytest .config/claude/scripts/tests/` — **318 passed** (T1 の回帰テスト 10 件を含む)
- T1 の回帰テストは修正前コードで 2 件失敗 (`KeyError: 'decision'`) を確認してから修正
- T2 は隔離 HOME で実走行し `EXIT=1` + status file 生成を確認
- `node --check` + `verify-patch.js --restore` を実走行 (native installer 環境で package-absent → skip 0)
- `bash -n` / bash 3.2 での空配列 + `set -u` 挙動を確認
- `task validate-configs` PASS / `task validate-symlinks` PASS

## 副次の観測 (未対応、要判断)

今回の scope 外なので触っていない。「隣接コードを勝手に直さない」に従い、判断はユーザーに残す。

- **`.config/claude/README.md:190,237` と `references/diagrams/architecture-overview.md:45`** —
  `skill-usage-tracker.py` が Stop/SessionEnd で動くと書いているが settings.json に登録がない。
  実配線は `PostToolUse: Skill` → `policy/skill-tracker.py`。ドキュメント 3 箇所の drift
- **`references/graduated-completion.md:47`** — handback を `additionalContext` と記載しているが
  実装は `systemMessage`。公式仕様ではこの 2 つは別物 (前者は Claude のコンテキストに注入、
  後者はユーザーにだけ表示される)。**どちらが意図なのか判断が要る** —
  handback を Claude に読ませたいなら実装が誤り、ユーザー向け報告なら doc が誤り
- `scripts/runtime/patrol-agent.sh:24` が参照する `cmux-notify.sh` は repo 内に実体なし
  (machine-local か 3 件目の drift か未確認)
- テストスイート実行が `references/negative-knowledge.md` に一時ディレクトリ名の garbage 行を追記する
  (`tmpgb2pdaxq` 等)。今回の commit からは除外したが、テスト分離の欠陥として残っている

## 教訓

- **1st-party の「削除しろ」は削減率でなく手順を読む。** 先行 absorb は削減率の移植を正しく拒否したが、
  方法論まで一緒に棄却して 6 日後に同じ主張を再検討することになった。
  記事を棄却するときは「主張のどの層を棄却したか」を分けて記録する
- **absorb は本体の採用より副産物のバグ検出で元が取れることがある。** 今回の最大の成果は
  記事由来の新規 instruction ではなく、記事の framing で照らして初めて見えた dead config 1 件と
  silent failure 1 件と無測定の標準経路 1 件
- **「Gap (存在しない)」判定は「既にやっているが測っていない」を見落とす。**
  M6 は corpus の grep で 0 件だったが、実際は `task setup` の標準経路で毎回実行されていた。
  概念名の不在を実装の不在と読み違えた
