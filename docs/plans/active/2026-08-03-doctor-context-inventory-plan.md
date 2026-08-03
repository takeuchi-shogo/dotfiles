---
date: 2026-08-03
status: active
source: https://note.com/o_ob/n/nd19cba8e11d7 (白井暁彦「CLAUDE.md と AGENTS.md を削ったら、AI コーディングがグンと賢くなった」)
analysis: docs/research/2026-08-03-shirai-claude-md-trim-absorb-analysis.md
scale: M
success_criteria: "task doctor:context が常時ロード散文の行数・skill description tax・条件ブロック数・未接続 producer 一覧を 1 画面で出し、初回スナップショットが docs/decommission-log.md に残っている"
---

# `doctor:context` — 常時ロード量の棚卸しを一枚にする

## Goal

「今このセッションに何が常時ロードされているか」を 1 コマンドで出す。
現状これを答えるには CLAUDE.md / rules / skill frontmatter / hook 配線を人が別々に数えるしかなく、
削減の議論が毎回「体感」から始まっている。

## Success Criteria

- `task doctor:context` が exit 0 で 4 区分 (常時ロード散文 / skill description tax / 条件ブロック / 未接続 producer) を出力する
- skill description tax は `settings.json` の `skillOverrides` で off / name-only にした分を除いた実効値になっている。
  検証: 任意の 1 skill を `off` にして再実行し、件数と文字数の両方が減る
- 未接続 producer 検出が `references/negative-knowledge.md` と同型のケースを拾える。
  検証: reader のいないダミー reference を置いて再実行し、一覧に出る
- 初回スナップショットが `docs/decommission-log.md` に日付つきで残っている

## Scope

触る:
- `Taskfile.yml` — `doctor:context` タスク追加
- `scripts/lifecycle/doctor-context.sh` (新規)
- `docs/decommission-log.md` — 初回スナップショット追記

触らない:
- `scripts/lifecycle/doctor.sh` — CLI のインストール状態診断で関心が違う。混ぜない
- `.config/claude/CLAUDE.md` および `templates/claude-md/` — 今回は測るだけで減らさない
- `settings.json` — 閾値による自動 block は入れない

## Constraints

- **行数を成果指標に格上げしない。** 出力はあくまで inventory であり、
  数字が減ったことを改善の証拠に使わない。根拠:
  `docs/research/2026-07-25-anthropic-context-engineering-claude5-absorb-analysis.md`
  の教訓「行数・件数を過剰制約の指標にしない」
- **skill 本文の行数は数えない。** 常時ロードされるのは frontmatter description であって本文ではない
- 未接続 producer 検出は誤検出を許容する advisory。CI や hook で block しない
- Claude Code 組み込みの `/doctor` は置き換えない。あちらは install / settings の診断で、
  実際に MCP 設定の drift を 1 件検出した実績がある (2026-07-25 absorb の T1)

## Unknowns

- **`<important if>` を実際の遅延ロードにできるか未検証。** Claude Code 側に path-scoped な
  ロード機構があるかを確認していない。先行コミット 282243c8 で `rules/*.md` の `paths:`
  frontmatter を「誰も読まない」として削除しており、少なくとも当時は機能していなかった。
  高影響 unknown: 機能するなら本プランの先に構造変更が来る。着手前に確認する
- 「常時ロードの概算トークン」をどう出すか。文字数ベースの近似で足りるか、
  実測 (`/context` 相当) が要るかを決めていない
- 未接続 producer の判定を grep ベースでやると、動的にパスを組み立てる writer を取りこぼす

## Validation

- `task doctor:context` を実行して 4 区分が出ることを目視
- Success Criteria の 2 つの検証手順 (skill を 1 件 off / ダミー reference を置く) を実行
- `task validate-configs`、`task validate-symlinks`
- `pytest .config/claude/scripts/tests -q`
- Codex Review Gate

## Steps

1. Unknowns の 1 件目 (path-scoped ロードの可否) を確認する。機能するなら本プランを見直す
2. `doctor-context.sh` を書く。4 区分のうち「常時ロード散文」「条件ブロック」から始める
3. skill description tax を足す。`skillOverrides` の実効値計算を含む
4. 未接続 producer 検出を足す
5. 初回スナップショットを `docs/decommission-log.md` に記録する

## Progress

- [ ] Step 1: path-scoped ロードの可否確認
- [ ] Step 2: 常時ロード散文 + 条件ブロック
- [ ] Step 3: skill description tax
- [ ] Step 4: 未接続 producer 検出
- [ ] Step 5: 初回スナップショット記録

## Surprises & Discoveries

- (着手時に追記)

## Decision Log

- **inventory は advisory に留め、閾値による自動 block を入れない。** 数字が減ったことを改善の
  証拠に使い始めると `docs/research/2026-07-25-anthropic-context-engineering-claude5-absorb-analysis.md`
  の教訓「行数・件数を過剰制約の指標にしない」を踏む。同型の失敗は
  `memory/feedback_skill_audit_conflict_metric.md` (CONFLICT 件数を成否指標にした) で既に 1 回起きている
- **Claude Code 組み込みの `/doctor` は置き換えず、context inventory だけ足す。** あちらは
  install / settings の診断で、実行しただけで MCP サーバ 1 つの起動失敗を検出した実績がある
  (2026-07-25 absorb の T1)。関心が違うので競合させない
- **`scripts/lifecycle/doctor.sh` に相乗りせず別スクリプトにする。** あちらは CLI のバージョンと
  インストール状態を見るもので、変更理由が別軸になる
- **skill 本文の行数は測らない。** 常時ロードされるのは frontmatter description であって本文ではない
  (2026-07-25 absorb で Codex が指摘した見落とし)。本文を測ると同じ過大評価を繰り返す

## 撤退条件

T1 の出力を 2 回見て、どちらも「知っていること」しか書かれていなかったら作らない側に倒す。
inventory は削減の判断材料になって初めて価値がある。数えるだけで何も動かないなら dead weight。

## Outcome

- (完了時に記入)

## 背景 — この absorb で判明した具体

記事の 3 手法 (M4 progressive disclosure / M10 行数を指標にしない / M11 `/doctor` で棚卸し) は
いずれも「まず現状を測れ」に収束するが、dotfiles には測る手段がない。実際に困った点:

- **`<important if>` は遅延ロードではない。** global CLAUDE.md の 122 行は毎セッション全文が
  コンテキストに入る。タグを解釈して除去・遅延ロードする処理は harness 内に存在しない。
  「必要時だけ読ませる構造」になっているのは参照先の `references/` 165 ファイルだけで、
  条件ブロック自体は常時ロード。この区別が可視化されていないため「progressive disclosure 済」と
  過大評価していた (Phase 2.5 で Codex が指摘)
- **`references/dead-weight-scan-protocol.md` の測定軸は行数を使っていない** (再指示回数 /
  誤った安全判断 / トークン) が、baseline と minimal を実測した比較ログが 1 件も残っていない
- **producer が接続されていない artifact を検出する手段がない。** 今回の absorb で
  `references/negative-knowledge.md` (reader ゼロの write-only store) が見つかったのは
  手作業の grep によるもので、mechanism では拾えなかった
