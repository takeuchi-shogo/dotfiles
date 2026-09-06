---
source: "クラウドエージェントが未来である (sc30gsw / Zenn) https://zenn.dev/sc30gsw/articles/953334f11df507"
date: 2026-09-04
status: analyzed
family: cloud-agent-execution
family_n: 1
saturation_gate: PASS (新分野)
---

## Source Summary

**主張**: 開発の実行環境を手元の PC からクラウド上の専用 VM (Cursor Cloud Agents / Claude Code on the web) に移す。人間の操作は「起動」と「最小限の承認」に縮む。著者は意図的に 2 つだけローカルに残す — **計画** (数分おきに質問へ答える高頻度ループなので、1 回の問い合わせが数時間の待ちになるクラウドに置くと非効率) と **UI 微調整** (2px の余白調整は秒単位のループが要る)。

**手法**: (1) 専用 VM 隔離による許可待ちなし実行 (2) VM 内でテスト・アプリ起動まで完結 (3) 「止まるコストが大きい」前提の自律設計 (4) 検証証拠が PR に付き reviewer が checkout 不要 (5) 複数リポジトリを 1 環境に (6) worktree 不要・仕事の単位は PR (7) PC を閉じても継続・スマホから承認 (8) 並列でもローカル資源を食わない (9) 長時間実行向き (10) トークン効率 20-30% 改善 (11) 環境定義のコード化 (`.cursor/environment.json`) (12) computer use による UI テストの証拠添付 (13) Stacked PR で PR 量を捌く (14) 計画はローカル plan mode → コミット → `claude --cloud "Execute the plan in docs/..."` (15) UI 微調整はローカル (16) grill-me で計画を詰める (17) feedback-agent (アプリ内 feedback → cloud agent → PR)

**根拠**: 著者の実践 (8 割以上のタスクをクラウド実行)。Cursor 公式ブログの引用複数。Cursor 内マージ済み PR のクラウドエージェント由来比率が 2025-12 の 10% → 2026-07 末に 56%。定量データは全て Cursor 自社発表。

**前提条件**: Cursor / Claude Code on the web のクラウド実行を契約していること。**エージェントの実行環境に自分の統制 (ルール・権限・hook) が載っている**こと — 記事はこれを暗黙の前提にしている。この前提が本 dotfiles では成立しない (下記 #11)。

## Phase 1.5: Saturation Gate

既存 taxonomy 4 family (obsidian-second-brain / skill-graphs / harness-engineering / claude-code-tips) はいずれも閾値キーワード数に届かない。`docs/research/` を `cloud agent` / `クラウドエージェント` / `Claude Code on the web` / `code.claude.com` で grep しても実質ヒットなし (付随言及のみ)。

**判定: 新 family `cloud-agent-execution` の 1 件目、N=0 → PASS**。Step 7 (Stale-Plan Audit) は同 family の過去 absorb が 0 件のため対象外。

`multi-agent-orchestration` への分類も検討したが、当該 family は「複数エージェントの協調パターン」であり、本記事の主題は「実行がどこで起きるか (execution locus)」で軸が異なる。混ぜると将来の飽和判定が壊れるため分けた。

## Gap Analysis (Pass 1 + Pass 2)

Pass 1 は Sonnet Explore に委譲したが 24 分 idle のまま応答が無く、その間に Opus が直接 grep で判定した (agent はその後遅れて報告し、結論は概ね一致 + Cursor Cloud Agent 経路 1 件を追加)。

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | 専用 VM 隔離で許可待ちなし (YOLO) | N/A | `.config/claude/settings.json` の `permissions.disableBypassPermissionsMode: "disable"`、deny 88 件 (`Bash(rm -rf *)` 含む)。意図的に逆方向で、しかも設定自体がリモートに届かない (#11) |
| 2 | VM 内で検証まで完結 | Already | verification-before-completion + webapp-testing。クラウド固有の利得は検証そのものではなく #4 |
| 3 | 人間に聞かず進む設計 | N/A (現時点) | `rules/common/overconfidence-prevention.md` の "Default to Asking" はローカル同席前提。クラウド常用が無い今変える理由がない |
| 4 | 検証証拠が PR に付く | Partial | `commands/pull-request.md` の本文形式は `## Summary` + `## Test plan` (意図のチェックリスト)。実行結果を残す規約が無い。memory `feedback_browser_verify_ui_changes.md` は「実ブラウザで確認しろ」で止まり証拠の行き先を定めていない |
| 5 | 複数リポジトリを 1 環境に | N/A | `references/multi-agent-coordination-patterns.md:155` が「現状は該当なし」と既記。`docs/research/2026-07-27-dex-harness-not-enough` 他でも reject 済 |
| 6 | worktree は死んだ / 単位は PR | N/A | ここの worktree は symlink 実体を共有するハーネスの隔離と `worktrees/pr-*` レビュー文脈が用途。クラウド VM は代替にならない |
| 7 | PC を閉じても継続・スマホ承認 | Already | `remoteControlAtStartup: true` / `agentPushNotifEnabled: true`。実測で Remote Control 5 セッション + cloud 1 セッションが生存 |
| 8 | 並列でもローカル資源を食わない | N/A | cmux/herdr 並列で実害の記録なし |
| 9 | 長時間実行向き | Already | nightly launchd + background agents + `/dispatch` + `collect-result.sh` |
| 10 | トークン効率 20-30% | N/A | Cursor 自社主張、検証不能。ベンチ数値を単独の採用根拠にしない規約に該当 |
| 11 | 環境定義のコード化 | **Gap (最重要)** | 下記 |
| 12 | computer use での UI 検証 | N/A | Cursor 固有。証拠添付の論点は #4 に統合 |
| 13 | Stacked PR | Already (知識のみ) | memory `reference_github_stacked_prs.md` に仕様・制約 (cross-fork 不可、Desktop 非対応) まで記録済。repo 側の実装は無いが `docs/research/2026-05-24-google-eng-practices:198` で「個人 dotfiles で stack 分割は稀」と reject 済 |
| 14 | 計画はローカル → コミット → クラウド実行 | Already | `PLANS.md` の昇格トリガー「handoff・resume・将来参照」がクラウド実行を含む (Codex 指摘)。既定の `tmp/plans/` が `.gitignore:111` で除外される点は事実だが、昇格ルール自体は既にある |
| 15 | UI 微調整はローカル | Already | 同じ結論に既到達 |
| 16 | grill で計画を詰める | Already | `.config/claude/skills/grill-interview/SKILL.md` (origin: mattpocock/skills の grill-me)、`scripts/policy/plan-implement-bridge.py` と連携 |
| 17 | feedback-agent | N/A | 対象プロダクトが無い。`references/unattended-pipeline.md:149,162` は Slack/GitHub webhook を「将来」と明記した未実装の参照設計 |

### #11 の中身: ローカルの統制はリモートに付いてこない

| | ローカル (このマシン) | 別ホスト (クラウド / 他マシン) |
|---|---|---|
| hook コマンド | 126 個 (`~/.claude/settings.json`、実体 `.config/claude/settings.json`) | **2 個** (repo 追跡の `.claude/settings.json`、code-review-graph のみ) |
| permission | allow 71 / deny 88 / ask 8、`disableBypassPermissionsMode: "disable"` | **なし** |
| skills / agents / memory | user スコープに 100+ | repo 追跡分のみ |

そのままコピーしても移植できない。hook のうち 4 個が `/opt/homebrew/bin/node` を、1 個が `afplay /System/Library/Sounds/...` を直書きしており Linux VM では動かない。

クラウド実行の経路自体は既に 1 本ある: `.config/claude/skills/cursor/SKILL.md:56-64` の Cursor Cloud Agent (`agent -c`)。ただし同じ統制ギャップを引き継ぎ、`.cursor/environment.json` は存在しないため既定環境で走る。

## Phase 2.5: Codex 批評 (Gemini は IneligibleTierError で sunset、Codex 単独)

呼び出し: `codex exec --skip-git-repo-check -m gpt-5.6-terra --sandbox read-only --config model_reasoning_effort="xhigh" --config project_doc_max_bytes=0`、プロンプトはファイル化して stdin 経由。exit 0、所要 ~10 分、32,804 tokens。

**verdict (逐語)**:

> Do not adopt ADOPT-1–3 as three equal "S" items. The prerequisite is a portable governance mechanism.
>
> - **ADOPT-1 is mostly already covered.** `PLANS.md` already promotes plans for "handoff / resume / future reference." A cloud executor is plainly a handoff. (...) Given no established cloud workflow, doing it now is YAGNI.
> - **ADOPT-2 is directionally right but too broad and technically flawed.** A local "screenshot path" is not PR evidence: reviewers cannot access the cloud VM's or laptop's filesystem. The useful rule is: record actual commands and pass/fail results; for visual changes, attach/embed a screenshot or durable artifact link.
> - **ADOPT-3 is underpowered.** This is not merely a documentation boundary. (...) Treat this as a real security and reliability boundary.
> - The article's premise breaks here: a per-agent VM isolates a filesystem, not Git credentials, secrets, network access, package-install side effects, or pushes to shared remotes. "YOLO is safe" requires disposable credentials, least privilege, egress/secrets controls, and a portable policy baseline.
> - If only one thing is done: **build and test the minimal portable governance baseline**. Until then, adding tracked plans or richer PR evidence merely makes an under-governed cloud execution path easier to use.

Codex による Opus 判定の訂正 3 件:

1. **#14 を Gap → Already に降格**。「handoff」が既にクラウド実行を含む。
2. **#4 の Opus 案が技術的に誤り**。「screenshot のパスを PR に貼る」はレビュアーがそのファイルシステムを読めないため無意味。正しくは「実行コマンドと pass/fail を記録し、視覚的変更は画像そのものを添付する」。
3. **#11 を過小評価していた**。「ドキュメント化」ではなく機構の問題。順序は (a) security 上必須の統制とローカル専用の利便性を分類 (b) 前者を追跡対象・クロスプラットフォームな repo 側 hook/設定へ切り出す (c) 使い捨て Linux 環境でロードと enforcement を実証する preflight。

Validation-only の言い方も Codex が修正: `cowork-equivalents.md:36` は偽ではない。`--cloud` が CLI にあることと、このリポジトリがクラウド実行を支えられることは別問題。「CLI 上は利用可能だが、統制と環境契約が未検証のため dotfiles のサポート対象ワークフローではない」が正しい。

## Integration Decisions

ユーザー選択: **「事実の訂正だけ (S)」**。移植可能ベースライン (Codex の第一推奨、M/L) は、クラウド実行を本気で使う判断が出るまで着手しない。

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| T1 | `cowork-equivalents.md` の stale 記述訂正 + 統制境界の記録 | **採用 (S)** | 下記 |
| — | 移植可能ガバナンスベースライン + Linux preflight | 見送り (M/L) | Codex の第一推奨だが、クラウド実行の採用判断が先。着手すると「統制の薄い経路を使いやすくする」だけになる |
| — | PR 本文に Verification セクション | 見送り | Codex: PR-only レビューに依存するワークフローが無い段階では ceremony。加えて Opus の当初案 (パス貼り) は誤り |
| — | `PLANS.md` の昇格トリガー追記 | 見送り | Already。クラウド運用が無い今は YAGNI (Codex) |
| — | YOLO / bypass 採用 | 却下 | `disableBypassPermissionsMode: "disable"` と正面衝突。VM 隔離はファイルシステムしか守らない (Codex) |
| — | multi-repo / feedback-agent / stacked PR / token 効率 | 却下 | 順に needs なし・対象プロダクトなし・記録済かつ reject 済・検証不能なベンダー主張 |

### T1 (実施済み)

`docs/guides/2026-05-09-claude-cowork-equivalents.md`

- 表の行「Cowork Cloud Agents | Claude.ai web 側の機能、dotfiles からは利用しない」→「クラウド実行は Claude Code CLI からも使えるが、dotfiles のサポート対象ワークフローではない (§1.2)」
- §1.2 を新設: CLI v2.1.259 が `--cloud` / `--environment` / `--teleport` / `ultrareview` を持つ事実、既存の Cursor Cloud Agent 経路、ローカル vs リモートの統制比較表 (126 hooks vs 2、permission ルール全滅、macOS 直書き 5 箇所)、採用前に必要な 3 手順、VM 隔離が守らないもの (git 認証情報・シークレット・ネットワーク・共有リモートへの push)

## Validation-only Follow-up

| 対象 | drift | 訂正方針 |
|------|-------|---------|
| `docs/guides/2026-05-09-claude-cowork-equivalents.md:36` | 「Claude.ai web 側の機能」は surface の説明として stale。CLI v2.1.259 に `--cloud` / `--environment <ccpool_...>` / `--teleport` / `ultrareview` が実在 | T1 で訂正済 |
| `docs/playbooks/claude-code-routines-pr-review.md` (16.6K) | 前提に「Claude Code on the web が有効」を挙げるが、routine が実際に登録・稼働しているかは未確認。休眠 artifact の疑い | **未着手**。次に Routines を触るとき `/schedule list` 相当で稼働を確認する |
| `.config/claude/skills/cursor/SKILL.md:56-64` | Cursor Cloud Agent 経路が存在するが、統制が付いてこない点への注意書きが無い | **未着手** (T1 の §1.2 から参照はした) |

## 教訓

- **記事が暗黙に置いている前提を、自環境で検査する**。この記事の全メリットは「エージェントの実行環境に自分の統制が載っている」を前提にしている。dotfiles はハーネスの価値がまさにマシンローカルな設定にあるため、その前提が反転する。記事の魅力ではなく前提を突いたときに実像が出た。
- **「証拠を残す」は保存場所まで指定して初めて成立する**。Opus は「screenshot のパスを PR に」と書いたが、レビュアーはそのファイルシステムを読めない。証拠の要件は「誰が読めるか」まで含む。
- Pass 1 の Sonnet Explore が 24 分 idle で無応答 → Opus 直接 grep に切り替えて続行。後から届いた報告は結論が一致し、`skills/cursor/SKILL.md` の Cursor Cloud Agent 1 件を追加した。**委譲先が沈黙したら待たずに自分でやり、返ってきたら差分だけ取り込む**。
