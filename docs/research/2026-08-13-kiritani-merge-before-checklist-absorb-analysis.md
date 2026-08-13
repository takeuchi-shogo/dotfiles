---
title: "Coding Agent が All tests passed と言った後、Merge 前に見る5項目 (absorb 分析)"
date: 2026-08-13
source_url: https://zenn.dev/kiritani_r/articles/a16f25f3390246
source_author: kiritani_r
family: code-review-best-practices
saturation: PASS (warning) — N≈13、採用率高で非飽和
status: implemented
type: absorb-analysis
---

# Merge 前に見る5項目

## Source Summary

同じ Coding Agent に実装とテストを両方書かせると「要件を誤解 → 誤った実装 → その実装に合うテスト → All tests passed」が成立する。
`All tests passed` が保証するのは「実行したテストが全て成功した」だけで、要件の正しさ・変更範囲の妥当性・テスト観点の十分さ・影響範囲の網羅は含まれない。
だから merge 前は「テストだけでは保証できない場所」から見る。①変更範囲 ②要件との一致 ③テストの検出力 ④境界値と正しい失敗 ⑤変更漏れ。
加えて、agent には「直して」より先に「探して」と頼み、調査と変更を分離する。

ユーザー指定で Claude Code だけでなく Codex / Cursor も照合対象に含めた。

## Phase 2 判定（Phase 2.5 Codex 批評による修正後）

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | 変更範囲を最初に見る | Already だが弱い | `references/scope-governor.md` + review skill Step 1.1/1.2。依頼から想定変更を導く入力がない |
| 2 | 要件→実装→テストの三者照合 | Partial | Mandatory Review Dimensions に「仕様整合性」はあるが、spec file がない場合に元依頼を reviewer へ渡す規約がない |
| 3 | テストの検出力 | **Partial（配線切れ）** | `rules/common/testing.md:20-26` に実装者向けの識別力ルールはあるが reader ゼロ。CC-6 は「テストが追加されているか」の2行のみ。routing はテスト観点 reviewer を起動できていなかった（下記） |
| 4 | 境界値 + 正しく失敗するか | Partial | retry・サイレント失敗は `silent-failure-hunter` が見る。失敗時の原子性と再送冪等性が不足 |
| 5 | diff に出ていない場所 | Partial（当初 Already と誤判定） | Impact pre-scan は30行以上/export 変更中心で、設定キー・path・env rename を落とす |
| 6 | 調査と変更の分離 | Claude/Codex は Already | Claude reviewer は read-only、codex-review も reviewer を read-only とする。Cursor `verifier.md` は `readonly: false` で保証に数えない |
| 7 | PR 分割 | 既存が強すぎる | `pr-splitting-patterns.md` の300行を単一ユーザーの硬い分割条件にしない。同時に整合しなければ壊れる harness 変更は1つに保つ |
| 8 | Review Prompt テンプレート | Claude は Already / Cursor は Partial | 733行の Claude review skill を他2面へ移植しない |
| 9 | Merge 前チェックリスト | Already。新設不要 | `AGENTS.md` の Change Surface Matrix。実事故が2回起きたときだけ追加する |

### Codex が覆した判定

- #5 を Already → Partial（過大評価）
- #7 は「不足」ではなく「既存が強すぎる」
- Cursor に要件照合する `verifier.md` は**存在する**（Opus は `.cursor/agents/` の reviewer だけ読み verifier を読み飛ばした）。ただし `.cursor/skills/review/SKILL.md` は reviewer にしか委譲せず、verifier は起動されない。能力の存在であって実行経路の保証ではない
- Codex も `AGENTS.md` の一行だけではない。`codex-review/SKILL.md:25` が caller drift・retry・外部副作用・migration を risk-based に見る

### 記事側の漏れ（Codex 指摘）

- 「どのテストを、なぜ実行したか」。全テスト green でも対象外・skip・削除済みなら意味がない
- 要件が会話にしかなく reviewer が読めない。三者照合以前の入力欠損
- 観測不能な性質（性能・権限・rollback・外部サービス整合性）はテストと diff 読みだけでは証明できない。証明不能なら PASS の根拠に混ぜない

## 採用（P0 のみ実装、3ファイル）

記事の観点そのものより、記事の framing で露出した**配線切れ**が主収穫。

| ファイル | 変更 |
|---|---|
| `skills/review/references/reviewer-routing.md:72,74` | `subagent_type: pr-test-analyzer` → `test-analyzer`。名前空間なしでは解決できない旨を併記 |
| `skills/review/SKILL.md:308` | コンテンツベース検出表の `pr-test-analyzer` → `test-analyzer` |
| `references/review-checklists/cross-cutting.md` CC-6 | バグ修正時に regression test が修正前コードで落ちるかを問う項目を追加 |

`test-analyzer.md:11` は「正典: `/review` が呼ぶのはこのローカル版。プラグイン同梱の別実装は `pr-review-toolkit:pr-test-analyzer`（名前が異なる点に注意）」と**既に警告していた**が、呼ぶ側の routing は `pr-test-analyzer` のままだった。宣言と配線が逆を向いていた。

### Codex Review Gate

1回目 CONSIDER 1件: CC-6 に書いた「修正前 base で実際に確認」は read-only reviewer には実行不能で、黙って推論に退化する。あわせて `ask:` は Watch 扱いで verdict を変えないと指摘。
→ 実測条件を「用意済みの別 worktree、または base SHA に紐づく CI 実行結果・失敗ログを確認できる場合」に限定し、severity を `consider:` に変更。

2回目 verdict（verbatim）:
> 結論: 前回の2点は解消しています。blocking な残件はありません。

## 見送り（実装しない）

- **要件入力の必須化**（review skill の Review Input に「要件ソース / 受入条件 / 対象外」、欠落時は `SPEC UNVERIFIABLE` として checked 扱い禁止）— Codex が P0 と並ぶ実効性と評価したが、ユーザー判断で今回のスコープ外
- **Evidence Card 4項目の3面共通化**（要件ソース / 変更契約と `rg` 結果 / テスト識別力または N/A / 状態変更時の失敗保証または N/A）
- **Cursor 側の追随** — ユーザーは Cursor を Claude Code の代替としてメインで使う場面がある（トークン節約）ため実害はあるが、今回は実装しない
- Codex が名指しで削るべきとしたもの: 全変更への mutation test、冪等性チェックの一般化、review prompt の三重複製、300行での強制分割、新しい万能チェックリスト

## Validation-only Follow-up（採用件数に数えない）

| 対象 | 内容 |
|---|---|
| `validate-agents` (Taskfile) | agent 定義21件の存在は検証するが、**skill が参照する `subagent_type` の実在は検証していない**。今回の drift はここをすり抜けた。検証を足せば同種の再発を機械的に止められる |
| `rules/common/*.md` | `rules/common/testing.md` を名指しで読ませる経路は `init-project` のテンプレ生成一覧のみ。`rules/go.md` / `rules/typescript.md` は golang-reviewer / typescript-reviewer が読むのに、`common/` には受け皿がない。2026-07-31 absorb の G4 は採用済みに見えて実効性ゼロだった |
| review tier | 10行以下の light tier は reviewer 自体を省略するため、小さいバグ修正では CC-6 の新項目も走らない。記事が想定する「1行直してテスト1本追加」はこの閾値の下に落ちる |
| `.cursor/rules/*.mdc` | 10件中9件が 2026-03-18 が最終コミット。Claude 側 `rules/common/testing.md` の 2026-08-03 と5ヶ月の drift。`CURSOR.md:20` は「4原則は両方同期すること」と書くだけで強制する仕組みがなく、同期対象に testing rule は最初から入っていない |
| `silent-failure-hunter.md` | `validate-agents` が `invalid YAML frontmatter (e.g. unclosed quote)` を WARN。今回の変更とは無関係の既存不具合 |
| `docs/research/2026-06-20-review-ai-code-mari-absorb-analysis.md:48,92` | `agents/longevity-reviewer.md (200行超で自動起動)` と実在しない agent ファイルを Already 判定の根拠にしていた。実体は routing の `general-purpose` + 専用プロンプト。Already ハロシネーションの実例 |

## 教訓

**宣言と配線は別々に腐る。** `test-analyzer.md` は「正典はローカル版、プラグイン版とは名前が違う」と正しく警告していた。にもかかわらず呼ぶ側は壊れたままだった。注意書きを書いた時点で直した気になっている。2026-08-03 intent-cli absorb の「配線を直した」と「呼ばれる場所を直した」は別、と同型。

**論理名と実 subagent_type の混在は誤検出を生む。** `nil-path-reviewer` / `longevity-reviewer` を当初「存在しない agent」と判定したが、routing を読むと `general-purpose` + 専用プロンプトの設計だった。SKILL.md の表だけでは区別できない。
