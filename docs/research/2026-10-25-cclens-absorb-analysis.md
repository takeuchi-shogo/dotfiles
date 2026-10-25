---
title: "Claude Code の「無駄」を可視化するツール cclens absorb"
date: 2026-10-25
source:
  title: "Claude Code の「無駄」を可視化するツール cclens を作った"
  author: Alisue (lambdalisue)
  url: https://zenn.dev/lambdalisue/articles/introduce-cclens
  type: zenn-article
  fetched: WebFetch (全文取得成功)
  intro: "https://x.com/takeokunn/status/2113920047219695882"
status: research-only
family: none
adopted: 0
---

# cclens — 採否

## Source Summary

**主張**: Claude Code の設定効果は非決定的で検証しづらい。普段使いのトランスクリプトをローカル解析し、時間・トークン・労力の無駄を計測・可視化する。計測のために別タスクを走らせない。

**手法（記事本文）**:
- Homebrew / Nix / cargo で入れる CLI。データは送信しない
- `doctor` でグローバルとプロジェクトの健康診断。`waste` / `inventory` / `overhead` / `usage` / `failures` / `stuck` / `prompts` の View
- 中心モデルは **catalog × usage**: surface（設定の静的トークン重量）と event（ランタイム）を join し、未使用・高コスト低頻度を刈り込み候補にする
- `overhead` は毎セッションの常時オン床値を、設定由来とシステム由来に分解する
- `optimize` は findings を対話的な `claude` セッションへ渡す。プラグインでも `/cclens:doctor` 等を提供
- 解析は SQLite ストアへの増分 `analyze`。生トランスクリプトはコピーしない

**紹介ポスト** (@takeokunn): 「cclens本当に便利なので週1で実行するのオススメしてる」

## Phase 1.5

近い先行: `2026-05-04-claude-code-overhead-9patterns`（常時 tax）、`2026-05-09-skill-inventory-vs-usage`（inventory × usage の一回集計）、`2026-04-14-hermes-personal-analyst`（コスト tracking spike）、`skill-usage-weekly.sh` / `token-audit.py` / `dead-weight-scan.py` / `/skill-audit`。taxonomy 上の専用 family は未登録のため `family: none`。

## 既存 usage / コスト可視化との照合

| 記事の手法 | 既存 | 判定 |
|---|---|---|
| 計測のために別ランを走らせない（普段のログを読む） | transcript / skill-executions.jsonl を読む週次・一回限りレポート | Already（思想） |
| skill/agent の未使用一覧 | `skill-usage-weekly.sh`、`2026-05-09-skill-inventory-vs-usage.md`（DEAD / UNDER-USED）、`dead-weight-scan.py` | Already |
| 常時オンのコンテキスト量（静的） | `scripts/runtime/token-audit.py`（always-loaded / on-invoke 等） | Already |
| skill tax・剪定 | `/skill-audit`、overhead 9 patterns absorb の採用タスク | Already |
| catalog × usage の継続 CLI（静的重量 × ランタイム、増分 SQLite） | 一回限りの inventory×usage レポートと週次 skill 回数のみ。静的重量の join は無し | Gap → **Reject**（下記） |
| `overhead` のセッション床値（設定 vs システム分解） | token-audit はファイル推定。トランスクリプト由来の床値は無し | Gap → **Reject** |
| `failures` / `stuck` / `prompts` | 同等の View は無し | Gap → **Reject** |
| `optimize` で AI に直しを渡す | `/skill-audit` と手動剪定。専用 optimize セッションは無し | Reject（既存監査経路で足りる） |
| brew/nix/plugin として harness に組み込む | nix/home と Brewfile は CLI を厳選。hermes の月次コスト本実装は spike 止まり | Reject |

## Integration Decisions

**採用 0。harness / Brewfile / nix / plugin への組み込みはしない。**

理由:
1. 「週1で未使用を見る」需要は `skill-usage-weekly.sh` と inventory×usage 実績で既に満たしている。
2. catalog×usage の本格 CLI は価値があるが、コスト可視化は hermes spike（`aggregate-daily-cost.py` 未着）と経路が並ぶ。未完の計測スタックを増やさない。
3. 記事のローカル完結・増分解析は良い性質だが、個人 dotfiles にバイナリを足す判断は、既存の週次・audit で足りなくなってからでよい。

手動で試す場合の入口は記事の `brew install lambdalisue/cclens/cclens` または `nix run github:lambdalisue/cclens -- doctor`（repo には追加しない）。

## 取得できたもの / 読めなかったもの

| ソース | 結果 |
|---|---|
| Zenn 記事本文 | 全文取得・判定に使用 |
| X 紹介 (`takeokunn/2113920047219695882`) | 取得。「週1で実行」推奨のみ。手法の追加情報はなし |
| cclens リポジトリの `docs/specs/` | 未取得（記事本文の技術詳細節のみ使用） |
