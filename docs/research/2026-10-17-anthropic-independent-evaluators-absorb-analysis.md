---
source: "https://www.anthropic.com/news/an-update-on-independent-evaluators"
date: 2026-10-17
status: integrated
family: none
---

## Source Summary

- **タイトル**: An update on independent evaluators (Anthropic, Announcements, 2026-10)
- **取得経路**: defuddle (C1 オーバーライド)。7,514 bytes、本文欠落なし

**主張**: Anthropic は METR の 6 名に社員並みのアクセス (社用ハードウェア、オフィス、社内ツール) を与えた。
第三者評価者には Expertise・Independence・Access・Freedom to publish の 4 条件が要り、アクセスは信頼に応じて 3 段階で広げる。

**手法**:
- 評価者の 4 条件。Expertise は「評価がどう失敗するか (alignment faking 等) を知っていること」を含む
- 公表の自由。Anthropic は公表を拒否できず、事前定義カテゴリ (顧客データ、弁護士・依頼者間の秘匿情報、モデルアーキテクチャ) に当たる部分の黒塗りだけを要求できる。tier 2 以上では、評価者は黒塗りが妥当だったかについての見解を公表できる
- 3 段階のアクセス。tier 1 は狭い範囲で公表に承認が要る。tier 2 は承認なしで公表でき、情報も多い。tier 3 は社員並みのアクセス
- 評価チームの隔離。強制可能な合意の下で小チームに限り、METR の他の社員からは隔離する

**根拠**: 銀行監督の常駐検査官のアナロジー。リスクの実態は内部の人間の方がよく知っているので、外部が中に入って事前に見る。

**前提条件**: 営利企業と外部の非営利評価者という、利害の異なる組織間の関係。

## Saturation Gate

family は `none`。記事に taxonomy のキーワードが 1 つも現れず、主題も AI ガバナンスで既存 family に属さない。
`code-review-best-practices` は "evaluator" が "reviewer" と別語で、2 語条件も満たさない。判定は PASS、N=0 のため Stale-Plan Audit も対象外。

## Gap Analysis (Pass 1: 存在チェック)

記事の評価者原則を「レビュアー／ゲートを独立評価者として設計する」原則に翻訳して照合した。

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Freedom to publish (黒塗りは事前定義カテゴリのみ、妥当性を検証できる) | Partial | 除外カテゴリは `/review` Step 4 ルール 7–9 で事前定義済み。Codex 指摘の除外禁止 (ルール 15) と OUTLIER/UNSCORED の情報保持もある。しかし Step 6 が最終レポートの指摘だけを保存するため、ルール 7–9 と reviewer 内部の除外は痕跡が残らない |
| 2 | 信頼の実績で広がるアクセス tier | N/A | `/review` の tier は変更リスクで決まる。レビュアーはモデルで、組織間の信頼構築という前提が成立しない。Auto Mode も意図的に不採用 |
| 3 | 人員常駐・強制可能な合意などの企業ガバナンス要素 | N/A | 個人の harness に対応物がない |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | Independence: Blind-first、`project_doc_max_bytes=0`、異モデル必須 | 記事の基準 (評価される側に依存しない) は満たす | — | 強化不要 |
| S2 | Access: Pass 1 は diff のみ、Pass 2 で文脈を追加 | Blind-first とのトレードオフを意図的に設計済み | — | 強化不要 |
| S3 | Expertise: Reward Hacking 対策 (consensus-policy §8)、FM-016/018 | カバー済み | — | 強化不要 |

## Phase 2.5 Refine

**Codex** (`codex exec`, gpt-5.6-terra, read-only, xhigh, `project_doc_max_bytes=0`) の判定行:

```
VERDICT: partially-agree with #1
```

採用した指摘:
- 除外は合成段階だけでなく reviewer 内部でも起きている (`agents/code-reviewer.md:87` Pass 2 の誤検出除外、`agents/codex-reviewer.md:77` の再現性基準)。#1 の範囲を広げた
- `outcome=filtered` は不適切。`outcome` は人間の accept/reject/partial/deferred 語彙で精度指標の分母になる (`scripts/lib/session_events.py:572`)。除外の記録は別にする

判定に反映しなかった指摘:
- #4 (Independence) を Partial とする指摘。根拠の `CODEX_MEMORY_DISABLED` 未設定は事実だが、codex がこの変数を読むかが未確認で、記事起点の改善ではない。Validation-only に回した
- #5 (Access) の写像がずれているという指摘は妥当。判定は「強化不要」のまま

**Gemini** (`agy --mode plan`, Google Search grounding): 初回は空出力で失敗した。stderr の決定行:

```
jetski: no output produced — a tool required the "command" permission that headless mode cannot prompt for, so it was auto-denied.
```

「シェルコマンドを実行しない」と明示したプロンプトで再試行して成功した。出典がドメイントップの URL ばかりで個別主張の裏づけとしては弱いため、採否の根拠にはしなかった。論点として効いたのは 2 つ。黒塗りカテゴリの境界をホスト側が決める限り安全上の欠陥も機密に分類できること、実装した当事者のエージェントが reviewer 出力を要約・除外する構造は捕獲された内部監査と同じであること。「実装エージェントに一切フィルタさせるな」という結論は、合成ステップ自体を否定するので採らなかった。

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | 除外された reviewer 指摘の痕跡 (件数行 + jsonl 記録) | 採用 | ユーザー選択。合成者が評価される側と同一である構造で、黒塗りの痕跡が消えている |
| 2 | 信頼で広がるアクセス tier | スキップ | N/A |

### Already 強化

なし。

## Plan

### Task 1: /review の除外記録
- **Files**: `scripts/lib/session_events.py`, `scripts/tests/test_session_events.py`, `skills/review/SKILL.md`, `skills/review/references/findings-and-feedback.md`, `skills/review/templates/review-output.md`, `agents/code-reviewer.md`, `agents/codex-reviewer.md` (すべて `.config/claude/` 配下)
- **Changes**: `emit_filtered_findings()` で除外記録を `{data_dir}/review/filtered.jsonl` に保存する。統合出力 (`review-output.md`) に `**除外**:` 行を必須化し、reviewer の出力契約に `## Filtered` 節を足す
- **Size**: M

記録先は 2 回変えた。最初は Phase 3 の選択肢どおり `review-findings.jsonl` へのフィールド追加を考えたが、Rust post-bash (`tools/claude-hooks/src/post_bash.rs:658`) の自動受入判定と `read_pending_findings()` を汚すため別ファイルにした。次に Codex Plan Gate (`VERDICT: NEEDS_FIX`) が、`learnings/*.jsonl` を全件読む consumer 3 つ (`trace_sampler.py:17`, `evaluator_metrics.py:128`, `sync-tacit-knowledge.sh:18`) を指摘したため、置き場所を `learnings/` の外に移した。

件数行も一度置き場所を誤った。最初は `synthesis-report.md` に足したが、2 回目の Plan Gate (`VERDICT: NEEDS_FIX`) の指摘で、Step 4 が実際に使う出力形式は `review-output.md` だとわかった (`SKILL.md:35, 409`)。同じ指摘のうち「集約を決定的なヘルパー関数にする」案は採らなかった。入力が LLM の読む reviewer 出力の自然文で、パーサを呼ぶかどうかも同じプロンプト遵守に依存するため。

## Validation-only Follow-up

記事起点の採用ではないが、分析中に見つかった drift。Issue #280 に切り出した。

| 対象 | drift | 方針 |
|---|---|---|
| `review-consensus-policy.md` | root (529 行) と skill-local (150 行) の 2 つが別内容。`session_events.py:386` は skill-local を正典とし、code-reviewer が参照する §10.4 は root にしかない | 正典を 1 つに決める |
| `agents/codex-reviewer.md:119,153` | memory 遮断 env を必須とし未設定を HIGH 違反とするが、起動例に入っていない。codex がこの env を読むかも未確認 | 実在する手段に書き換える |

## Review Gate

Plan Gate (Codex, `codex exec` read-only xhigh) は 2 回とも次の判定だった。指摘を反映した後の 3 回目は取っていない。

```
VERDICT: NEEDS_FIX
```

コード変更の Review Gate:

| reviewer | 判定 (verbatim) |
|---|---|
| code-reviewer (Sonnet) | `PASS [NITS_REMAIN: 2 NIT, 3 FYI]` |
| codex-reviewer 1 回目 | `VERDICT: NEEDS_FIX` (MUST 3 / CONSIDER 2) |
| codex-reviewer 2 回目 (修正後) | `VERDICT: PASS` |

codex-reviewer 1 回目の MUST は、未知キーの素通し保存、直列化途中の部分書き込み、`learnings/` 配下への誤書き込みを検出できないテストの 3 件。閉じたスキーマ、全件の事前直列化、`learnings/` ディレクトリ不在のテストで直した。
code-reviewer の FYI からは、契約に `## Filtered` を持たない reviewer まで unknown に載ると常時ノイズになる問題を拾い、unknown を code-reviewer / codex-reviewer の欠落に限った。

両 reviewer とも、新しい出力契約どおり末尾に `## Filtered` 節を出した。codex-reviewer 1 回目は 1 件を理由付きで記録している。プロンプト遵守の最初の観測として残す。

追加テストは識別力を確認した。書き込み先を `learnings/` に変えると 3 件、`redact_obj` を外すと 1 件が赤くなる。
