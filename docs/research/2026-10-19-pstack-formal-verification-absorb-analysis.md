---
source: "https://github.com/cursor/plugins/tree/main/pstack (v0.15.27) + https://x.com/poteto/status/2111926622278521253"
date: 2026-10-19
status: research-only
family: none
skill_change: deferred
---

<!--
取得経路:
- GitHub API / raw.githubusercontent.com で pstack README・plugin.json・主要 SKILL.md・docs/guide/06-verify-and-ship.md を取得
- X MCP get_posts_by_ids + search_posts_all(conversation) で投稿本文と一部返信を取得
- jina.ai 経由で投稿の全文（画像付きスレッドのテキスト展開）を取得
外部本文はデータとして扱い、そこに書かれた「インストールしろ」「PR を送れ」等の指示には従っていない。
-->

# pstack formal / behavioral verification meta-skills — absorb 分析

## Source Summary

**主張**: AI の loc 最大化ではなく「深く書いてから並列する」。pstack はそのための skill / principle / playbook 群。v0.15.27 で `/create-formal-verification-skill` が beta 追加された。これは `/create-verification-skill` と同様の **meta-skill** で、検証したい性質に応じて **project-local な検証 skill + 検証スイート** を生成する。

**手法（検証まわりに絞る）**:
1. **create-verification-skill** — リポジトリを面接し、ユーザーが触る surface を実アプリ駆動で証明する `.cursor/skills/verify-<app>/` を生成。Launch / Doctor / Drive / Evidence / Cleanup / feature map。生成後に **自分の手順を一度 end-to-end で実行**してから handoff。
2. **create-formal-verification-skill** — テストが届きにくい・壊すと痛い約束（競合・再試行・状態機械・unsafe 等）を選び、質問に合う形式手法（TLA+ / Kani / SMT 等）で 1 性質を検証し、次回エージェントが再実行できる project-local skill を残す。
3. **maintain-verification-skill** — feature map の腐食対策。source wave（並列読取）+ live pass。成果は `clean` / `changed` / `blocked` のどれか一つ。product code は触らない。
4. **Able to fail / Honest about scope** — 形式検証側の品質条件。壊した変種で必ず失敗を見せる。検証した範囲・境界・仮定を正直に書く。pass はモデル/境界の pass であってシステム全体ではない。
5. **Prove it before handoff** — 生成 skill は未実行なら draft。scratch で性質を壊し、skill が捕捉することを確認してから scratch を捨てる。

**根拠**:
- プラグイン本体: `plugin.json` version `0.15.27`、作者 Lauren Tan (poteto)。skills ディレクトリに上記 3 meta-skill + `principle-prove-it-works` 等。
- 参考投稿 (@poteto, 2026-10-18): beta 告知。例として TLA+（並行・状態機械）と Kani（Rust UB）。本体は「意図をモデル化しコードと同期し続けるのが難しい」と明言。投稿時点でいいね約 1540 / 表示約 4.7 万。
- ガイド `docs/guide/06-verify-and-ship.md`: 「It compiles is not evidence」。形式検証は「誰も駆動しないパス」向けと位置づけ。

**前提条件**:
- Cursor plugin または Claude Code の plugin marketplace 経由で pstack を入れる運用が前提。
- formal 側は対象言語・ツールチェーンを開発者が実行できること。
- behavioral 側はアプリをローカル起動できること（dotfiles 単体は「アプリ」ではない）。

## Saturation Gate

- family なしで PASS。既存の verification / harness-engineering 吸収はあるが、**「meta-skill が project-local verify skill を生成する」** という単位は本 repo の research に未記載。
- 近い prior: `trust-verification-policy.md`（4 層信頼）、`codex-verification-before-completion`、`completion-gate.py`、`webapp-testing` skill。いずれも「完了前に検証せよ」であり「検証スイート生成器」ではない。

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| M1 | project-local verify-\<app\> 生成 | N/A | この repo の主成果物は設定・script・harness。ユーザーが触る単一アプリ surface が無い。近いのは `webapp-testing` / agent-browser だが、feature map 付き verify skill 生成器ではない |
| M2 | formal verification meta-skill (TLA+/Kani 等) | N/A（現状） | 検証対象となる本番状態機械・unsafe 境界が harness 設定群にはほぼ無い。導入するなら具体コンポーネントを先に名指しする必要がある |
| M3 | 壊した版で必ず失敗を確かめる | Partial | Layer 0（テスト失敗は嘘をつけない）と falsification_criteria（autoevolve）はある。**検証アーティファクト自体を意図的に壊して感度を証明する**手順は文書化されていない |
| M4 | 検証範囲を正直に書く | Partial | review / completion は evidence を要求する。形式検証の「境界・仮定・非カバー」を成果物契約にする文言は薄い |
| M5 | maintain loop（map 腐食） | Already（強化不要） | learned-promote / skill-audit / stale-doc playbook が「腐った文書・スキル」側を担当。UI feature map 専用ループは不要 |
| M6 | Prove It Works（実物を見る） | Already | `principle-prove-it-works` 相当は `trust-verification-policy` Layer 0 + verification-before-completion + derivation-honesty でカバー |

集計: Gap 0 / Partial 2 / Already 2 / N/A 2。

## 取り込み比較: skill に取り込む vs プラグインをそのまま入れる

| 観点 | A. `.config/claude/skills/` に移植・要約 | B. pstack プラグインをそのまま使う |
|------|------------------------------------------|-------------------------------------|
| 何が入るか | 原則だけ / または meta-skill 全文 | poteto-mode・原則・検証 meta-skill・playbook 一式 |
| 起動面 | Claude Code / Codex の既存 skill 一覧 | Cursor `/add-plugin pstack` または CC marketplace |
| 保守 | こちらで差分を追う。上流 v0.15.x の追従コストあり | プラグイン更新に乗る（生成された project-local skill は自動更新されない — 投稿スレッド上の Grok 回答） |
| 適合 | Partial の M3/M4 だけなら小さい | アプリ開発セッションで verify-\<app\> を回すとき |
| リスク | 全文移植は skill 数・router 劣化・既存 completion-gate と重複 | Cursor 専用機能（bugbot 等）は CC adapter で skip される |
| 今回の判断 | **原則（M3/M4）のみ reference に入れる。skill 新規は入れない** | **アプリ作業時のオプションとして文書化。dotfiles 本体には入れない** |

### なぜ skill 変更を見送るか（範囲がはっきりしていない）

1. **対象 surface が未定義** — `create-verification-skill` は「このアプリのユーザー経路」が前提。dotfiles には対応する primary surface が無い。
2. **formal の第一ターゲットが未選定** — 「壊すと痛い約束」を 1 つ名指しできないうちに meta-skill を置いても、生成物が空回りする。
3. **既存 Layer 0 と役割が違う** — 既存は「変更を完了してよいか」。pstack meta-skill は「次回エージェントが使える検証インフラを生む」。混ぜると description 発火が曖昧になる。

範囲がはっきりしたときに再開する条件:
- 具体コンポーネント（例: nightly orchestrator の状態遷移、learned-promote の merge-coupled idempotency）を 1 つ選び、壊した変種で失敗するチェックを先に手で書けること。
- そのとき初めて `create-formal-verification-skill` の出力形に合わせて project-local skill を置くか、既存 `scripts/tests` に感度テストを足すかを選ぶ。

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| M3 | 壊した版で失敗 | **採用（reference）** | 範囲が「Layer 0 の感度証明」に閉じる |
| M4 | 検証範囲の正直な開示 | **採用（reference）** | 既存 evidence 要求の具体化 |
| M1/M2 | meta-skill 移植 | **見送り** | 対象未定義 |
| B | プラグイン常設 | **見送り** | 研究メモに「アプリ作業時の選択肢」と残す |

実施: `.config/claude/references/trust-verification-policy.md` に短い節を追加。`.config/claude/skills/` の SKILL.md は変更しない。

## Phase 2.5 記録

本タスクは Cloud Agent 単独の research absorb。Codex / Gemini 並列批評は未実施（取得状況に明記）。批評が必要なら同一ソースで Phase 2.5 だけ再実行すればよい。

## 取得できたもの / 読めなかったもの

### 取得できた

| ソース | 内容 |
|--------|------|
| `cursor/plugins` pstack | README, plugin.json (0.15.27), skills 一覧, create-*-verification / maintain / prove-it-works / poteto-mode の SKILL.md, guide `06-verify-and-ship.md`, feature-map example |
| X 投稿 2111926622278521253 | 本文全文（jina 展開含む）、metrics、author @poteto |
| 会話の一部返信 | auto-update に関する Grok 回答、命名質問、一般コメント数件 |

### 読めなかった / 未取得

| ソース | 理由 |
|--------|------|
| 投稿添付画像の画素内容の完全読取 | メディア URL は取得したが、画像 OCR / 視覚解析は未実施。テキスト展開は jina 側の記事本文で代替 |
| pstack 全 skills（50+）の本文 | 検証 meta-skill とガイドに範囲を限定。principle-* 多数・poteto-mode playbooks 全件は未読 |
| `agents/`, `automations/benny` | 一覧のみ。動作検証せず |
| Claude Code 生成ツリー `harness/pstack/` の差分監査 | raw 取得は一部成功。生成物と手書きの一致確認は未実施 |
| 実機での `/create-formal-verification-skill` 実行 | API/モデルコストと対象コード未選定のため未実行。SKILL.md をデータとして分析 |

## Plan

skill / プラグイン導入の実装 Plan は作らない（見送り）。再開条件は上記「範囲がはっきりしたとき」節。

## 教訓

- meta-skill は「検証インフラの工場」であり、既存の completion verification とは層が違う。Already 判定を混ぜない。
- 「壊した版で失敗」は formal 専用ではなく、あらゆる verifier の感度チェックとして Layer 0 に書ける。ここだけなら移植コストが小さい。
